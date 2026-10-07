"""Cloud prototype: one immutable CNF, durable replies, native child accounting.
Not an N1 production runner. No target-hardware approval.
"""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
import uuid


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def atomic(path, value):
    path = Path(path)
    data = json.dumps(value, sort_keys=True, allow_nan=False).encode()
    envelope = json.dumps({"sha256": hashlib.sha256(data).hexdigest(),
                           "data": value}, sort_keys=True).encode()
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temp.open("xb") as stream:
        stream.write(envelope)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read(path):
    envelope = json.loads(Path(path).read_text())
    data = json.dumps(envelope["data"], sort_keys=True, allow_nan=False).encode()
    if hashlib.sha256(data).hexdigest() != envelope["sha256"]:
        raise ValueError("damaged envelope: " + str(path))
    return envelope["data"]


def identity(pid):
    namespace = os.readlink("/proc/self/ns/pid")
    candidates = [Path("/proc") / str(pid)]
    candidates += [d for d in Path("/proc").iterdir() if d.name.isdigit()]
    for directory in candidates:
        try:
            if os.readlink(directory / "ns/pid") != namespace:
                continue
            status = (directory / "status").read_text().splitlines()
            ids = next(x.split()[1:] for x in status if x.startswith("NSpid:"))
            if int(ids[-1]) != pid:
                continue
            fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
            return {"pid": pid, "proc_pid": int(directory.name),
                    "birth": fields[19], "namespace": namespace,
                    "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    raise ValueError("cannot identify process in mounted proc namespace")


def live_cpu(ident):
    fields = Path(f"/proc/{ident['proc_pid']}/stat").read_text().rsplit(")", 1)[1].split()
    if fields[19] != ident["birth"]:
        raise ValueError("process identity changed")
    return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")


def init(root, cnf, worker, checker, budget):
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError("positive finite budget required")
    root.mkdir(exist_ok=False)
    (root / "answers").mkdir()
    (root / "attempts").mkdir()
    with (root / "input.cnf").open("xb") as out, cnf.open("rb") as inp:
        for block in iter(lambda: inp.read(1048576), b""):
            out.write(block)
        out.flush()
        os.fsync(out.fileno())
    m = {"run_id": uuid.uuid4().hex, "input_sha256": sha(root / "input.cnf"),
         "worker": str(worker.resolve()), "worker_sha256": sha(worker),
         "checker": str(checker.resolve()), "checker_sha256": sha(checker),
         "scope": "native_children_cpu_seconds", "original_budget": budget,
         "runtime_sha256": sha(__file__), "production_approved": False}
    atomic(root / "manifest.json", m)
    atomic(root / "state.json", {
        "run_id": m["run_id"], "status": "READY", "budget": budget,
        "cpu_completed": 0.0, "live_cpu": 0.0, "accounting_complete": True,
        "generation": 0, "request": None, "replies": {}, "attempts": [],
        "stop": False, "phase": None, "child": None, "supervisor": None})


def reply(root, request_id, seconds, answer_id=None):
    if seconds < 0:
        raise ValueError("nonnegative integer required")
    s = read(root / "state.json")
    answer_id = answer_id or uuid.uuid4().hex
    if not answer_id.isalnum():
        raise ValueError("alphanumeric answer id required")
    value = {"run_id": s["run_id"], "request_id": request_id,
             "seconds": seconds, "answer_id": answer_id}
    path = root / "answers" / (answer_id + ".json")
    if path.exists():
        if read(path) != value:
            raise ValueError("answer id reused with different content")
    else:
        # Serialize competing CLI writers as well as repeated delivery.
        with (root / "reply.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if path.exists() and read(path) != value:
                raise ValueError("answer id conflict")
            if not path.exists():
                atomic(path, value)
    return answer_id


def service(root, s):
    for path in sorted((root / "answers").glob("*.json")):
        if path.stem in s["replies"]:
            continue
        try:
            a = read(path)
            valid = (a["answer_id"] == path.stem and a["run_id"] == s["run_id"]
                     and s["request"] is not None
                     and a["request_id"] == s["request"]["id"]
                     and type(a["seconds"]) is int and a["seconds"] >= 0)
        except (ValueError, KeyError, TypeError):
            valid = False
        s["replies"][path.stem] = "ACCEPTED" if valid else "REJECTED"
        if valid:
            if a["seconds"] == 0:
                s["stop"] = True
            else:
                s["budget"] += a["seconds"]
            s["request"] = None
        # Reply id and its effect commit together; retries cannot add twice.
        atomic(root / "state.json", s)
    consumed = s["cpu_completed"] + s["live_cpu"]
    if not s["stop"] and consumed >= s["budget"] and s["request"] is None:
        s["generation"] += 1
        s["request"] = {"id": uuid.uuid4().hex, "generation": s["generation"],
                        "scope": "native_children_cpu_seconds",
                        "budget": s["budget"], "consumed_at_request": consumed,
                        "message": "time limit reached. ETA unknown. Extend [seconds] ?"}
    s["status"] = ("STOP_REQUESTED" if s["stop"] else
                   "RUNNING_AWAITING_TIME_EXTENSION" if s["request"] else "RUNNING")
    s["updated_utc"] = time.time()
    s["supervisor_cpu_this_session"] = time.process_time()
    atomic(root / "state.json", s)


def child(root, s, directory, command, phase):
    log = (directory / (phase + ".log")).open("xb")
    proc = subprocess.Popen(command, cwd=directory, stdin=subprocess.DEVNULL,
                            stdout=log, stderr=subprocess.STDOUT)
    s["child"] = identity(proc.pid)
    s["phase"] = phase
    s["live_cpu"] = 0.0
    atomic(root / "state.json", s)
    sent = False
    last_sync = 0.0
    while True:
        pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
        if pid:
            proc.returncode = os.waitstatus_to_exitcode(status)
            break
        s["live_cpu"] = live_cpu(s["child"])
        service(root, s)
        if s["stop"] and not sent:
            # PID is still our unreaped child; no unrelated process can reuse it.
            if phase == "search":
                atomic(directory / "STOP", {"requested_utc": time.time()})
            else:
                proc.send_signal(signal.SIGTERM)
            sent = True
        if time.monotonic() - last_sync >= 1:
            proof = directory / "proof.partial"
            if proof.exists():
                fd = os.open(proof, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            last_sync = time.monotonic()
        time.sleep(0.05)
    log.flush()
    os.fsync(log.fileno())
    log.close()
    end_cpu = usage.ru_utime + usage.ru_stime
    s["cpu_completed"] += end_cpu
    s["live_cpu"] = 0.0
    s["child"] = None
    receipt = {"phase": phase, "returncode": proc.returncode, "cpu_s": end_cpu,
               "peak_rss_kib": usage.ru_maxrss, "stop_sent": sent}
    atomic(directory / (phase + "_receipt.json"), receipt)
    atomic(root / "state.json", s)
    return receipt


def cnf_model_ok(cnf, model):
    values = [int(x) for x in model.read_text().split()]
    if not values or values[-1] != 0:
        return False
    literals = values[:-1]
    assignment = {abs(x): x > 0 for x in literals}
    if 0 in literals or len(assignment) != len(literals):
        return False
    clause, count, nvars, expected = [], 0, None, None
    for line in cnf.read_text().splitlines():
        words = line.split()
        if not words or words[0] == "c":
            continue
        if words[0] == "p":
            if nvars is not None or len(words) != 4 or words[1] != "cnf":
                return False
            nvars, expected = map(int, words[2:])
            continue
        for lit in map(int, words):
            if lit:
                clause.append(lit)
            else:
                if not any(assignment.get(abs(x)) == (x > 0) for x in clause):
                    return False
                clause = []
                count += 1
    return (nvars is not None and not clause and count == expected and
            set(assignment) == set(range(1, nvars + 1)))


def verify_attempt(directory, item):
    r = read(directory / "final.json")
    if sha(directory / "final.json") != item["receipt_sha256"]:
        raise ValueError("receipt changed")
    if not all(sha(directory / n) == h for n, h in r["files"].items()):
        raise ValueError("attempt artifact changed")
    return r


def run(root, resume=False):
    lock = (root / "supervisor.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    m, s = read(root / "manifest.json"), read(root / "state.json")
    if resource.getrlimit(resource.RLIMIT_CPU) != (-1, -1):
        raise ValueError("finite inherited CPU limit")
    for p, h in [(root / "input.cnf", m["input_sha256"]),
                 (Path(m["worker"]), m["worker_sha256"]),
                 (Path(m["checker"]), m["checker_sha256"]),
                 (Path(__file__), m["runtime_sha256"])]:
        if sha(p) != h:
            raise ValueError("input/tool identity mismatch")
    for item in s["attempts"]:
        verify_attempt(root / "attempts" / item["id"], item)
    if s["status"] in ("SAT_CNF_VERIFIED", "UNSAT_CERTIFIED"):
        return s
    if s["status"] not in ("READY", "STOPPED_UNRESOLVED"):
        raise ValueError("unclosed session: read-only recovery required; no automatic restart")
    if s["status"] == "STOPPED_UNRESOLVED" and not resume:
        raise ValueError("explicit resume required")
    if not s["accounting_complete"]:
        raise ValueError("incomplete accounting")
    s["stop"] = False
    s["request"] = None
    s["supervisor"] = identity(os.getpid())
    s["status"] = "RUNNING"
    aid = uuid.uuid4().hex
    directory = root / "attempts" / aid
    directory.mkdir()
    s["active_attempt"] = aid
    atomic(root / "state.json", s)
    started = time.process_time()
    search = child(root, s, directory, [m["worker"], str(root / "input.cnf")], "search")
    result = "STOPPED_UNRESOLVED"
    raw = directory / "worker.json"
    if raw.exists():
        worker = json.loads(raw.read_text())
        code = worker["result"]
        if search["returncode"] != code:
            raise ValueError("worker/exit disagreement")
        if code == 10:
            if not cnf_model_ok(root / "input.cnf", directory / "model.txt"):
                raise ValueError("invalid SAT model")
            result = "SAT_CNF_VERIFIED"
        elif code == 20 and not s["stop"]:
            check = child(root, s, directory, [m["checker"], str(root / "input.cnf"),
                          str(directory / "proof.partial"), "-O"], "check")
            lines = (directory / "check.log").read_text().replace("\r", "\n").splitlines()
            valid = (check["returncode"] == 0 and "s VERIFIED" in lines and
                     not any(x in lines for x in
                             ("s NOT VERIFIED", "s TIMEOUT", "s DERIVATION")))
            result = "UNSAT_CERTIFIED" if valid else "UNSAT_UNCERTIFIED"
        elif code == 20:
            result = "UNSAT_UNCERTIFIED"
        elif code != 0:
            raise ValueError("unexpected solver code")
    else:
        result = "CRASHED_UNRESOLVED"
    final = {"status": result, "attempt_id": aid, "input_sha256": m["input_sha256"],
             "cpu_completed": s["cpu_completed"], "accounting_complete": True,
             "supervisor_session_cpu_s": time.process_time() - started,
             "files": {p.name: sha(p) for p in directory.iterdir() if p.is_file()}}
    atomic(directory / "final.json", final)
    item = {"id": aid, "receipt_sha256": sha(directory / "final.json")}
    verify_attempt(directory, item)
    s["attempts"].append(item)
    s["status"] = result
    s["request"] = None
    s["active_attempt"] = None
    atomic(root / "state.json", s)
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "run", "resume", "status", "reply"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--checker", type=Path)
    parser.add_argument("--budget", type=float)
    parser.add_argument("--request")
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--answer-id")
    a = parser.parse_args()
    root = a.root.resolve()
    if a.action == "init":
        init(root, a.cnf, a.worker, a.checker, a.budget)
    elif a.action in ("run", "resume"):
        run(root, a.action == "resume")
    elif a.action == "reply":
        print(reply(root, a.request, a.seconds, a.answer_id))
    else:
        print(json.dumps(read(root / "state.json"), indent=2))


if __name__ == "__main__":
    main()
