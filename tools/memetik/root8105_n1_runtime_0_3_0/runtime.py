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


def raw_atomic(path, value):
    path = Path(path)
    data = json.dumps(value, sort_keys=True, allow_nan=False).encode()
    envelope = json.dumps({"sha256": hashlib.sha256(data).hexdigest(),
                           "data": value}, sort_keys=True).encode()
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temp.open("xb") as stream:
        stream.write(envelope)
        stream.flush()
        os.fsync(stream.fileno())
    if os.environ.get('N1_TEST_WRITE_FAIL') == path.name and (path.parent / 'ALLOW_TEST_FAULTS').exists():
        raise OSError('injected failure before replace')
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def raw_read(path):
    envelope = json.loads(Path(path).read_text())
    data = json.dumps(envelope["data"], sort_keys=True, allow_nan=False).encode()
    if hashlib.sha256(data).hexdigest() != envelope["sha256"]:
        raise ValueError("damaged envelope: " + str(path))
    return envelope["data"]


def fault(root, stage):
    # Fault injection is inert unless both explicit test gates are present.
    if (root / "ALLOW_TEST_FAULTS").exists() and os.environ.get("N1_TEST_FAULT") == stage:
        os._exit(91)


def atomic(path, value):
    path = Path(path)
    if path.name != "state.json":
        return raw_atomic(path, value)
    history = path.parent / "states"
    history.mkdir(exist_ok=True)
    seq = value.get("_seq", 0) + 1
    target = history / f"{seq:012d}.json"
    if target.exists():
        raise ValueError("refuse overwriting a state generation")
    value["_seq"] = seq
    raw_atomic(target, value)
    fault(path.parent, "state_after_generation")
    raw_atomic(path, value)


def latest_state(root):
    paths = sorted((root / "states").glob("*.json"))
    if not paths:
        raise ValueError("missing state history")
    # Never silently fall back across a corrupt authoritative transaction.
    state = raw_read(paths[-1])
    if state["_seq"] != int(paths[-1].stem):
        raise ValueError("state sequence mismatch")
    return state


def read(path):
    path = Path(path)
    # Generations are authoritative; the convenience cache may lag a live write.
    if path.name == "state.json":
        return latest_state(path.parent)
    return raw_read(path)


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


def init(root, cnf, worker, checker, budget, binding=None):
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError("positive finite budget required")
    if binding is not None:
        import bind_n1
        import n1_check
        bind_n1.verify_regeneration(n1_check.load(binding), cnf)
    root.mkdir(exist_ok=False)
    (root / "supervisor.lock").touch(exist_ok=False)
    (root / "answers").mkdir()
    (root / "attempts").mkdir()
    with (root / "input.cnf").open("xb") as out, cnf.open("rb") as inp:
        for block in iter(lambda: inp.read(1048576), b""):
            out.write(block)
        out.flush()
        os.fsync(out.fileno())
    if binding is not None:
        with (root / "binding.json").open("xb") as stream:
            stream.write(binding.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
    m = {"run_id": uuid.uuid4().hex, "input_sha256": sha(root / "input.cnf"),
         "worker": str(worker.resolve()), "worker_sha256": sha(worker),
         "checker": str(checker.resolve()), "checker_sha256": sha(checker),
         "scope": "native_children_cpu_seconds", "original_budget": budget,
         "runtime_sha256": sha(__file__),
         "recovery_sha256": sha(Path(__file__).with_name("recovery.py")),
         "n1_check_sha256": sha(Path(__file__).with_name("n1_check.py")),
         "binder_sha256": sha(Path(__file__).with_name("bind_n1.py")),
         "binding_sha256": sha(root / "binding.json") if binding is not None else None,
         "production_approved": False}
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
    atomic(directory / (phase + "_intent.json"), {"attempt_id": directory.name, "phase": phase, "command": command})
    log = (directory / (phase + ".log")).open("xb")
    proc = subprocess.Popen(command, cwd=directory, stdin=subprocess.DEVNULL,
                            stdout=log, stderr=subprocess.STDOUT)
    s["child"] = identity(proc.pid)
    atomic(directory / (phase + "_identity.json"), s["child"])
    s["phase"] = phase
    s["live_cpu"] = 0.0
    atomic(root / "state.json", s)
    fault(root, phase + "_after_identity")
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
    fault(root, phase + "_after_wait4")
    end_cpu = usage.ru_utime + usage.ru_stime
    s["cpu_completed"] += end_cpu
    s["live_cpu"] = 0.0
    s["child"] = None
    receipt = {"attempt_id": directory.name, "input_sha256": sha(root / "input.cnf"), "phase": phase, "returncode": proc.returncode, "cpu_s": end_cpu,
               "peak_rss_kib": usage.ru_maxrss, "stop_sent": sent}
    outputs = [phase + ".log"]
    if phase == "search":
        outputs += [n for n in ("worker.json", "proof.partial", "model.txt") if (directory / n).exists()]
    receipt["files"] = {n: sha(directory / n) for n in outputs}
    atomic(directory / (phase + "_receipt.json"), receipt)
    fault(root, phase + "_after_receipt")
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
    from recovery import run as recovered_run
    return recovered_run(root, resume)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init", "run", "resume", "status", "reply", "recover"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--checker", type=Path)
    parser.add_argument("--budget", type=float)
    parser.add_argument("--request")
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--answer-id")
    parser.add_argument("--apply", action="store_true")
    a = parser.parse_args()
    root = a.root.resolve()
    if a.action == "init":
        init(root, a.cnf, a.worker, a.checker, a.budget, a.binding)
    elif a.action in ("run", "resume"):
        run(root, a.action == "resume")
    elif a.action == "recover":
        from recovery import recover
        print(json.dumps(recover(root, a.apply), indent=2))
    elif a.action == "reply":
        print(reply(root, a.request, a.seconds, a.answer_id))
    else:
        print(json.dumps(read(root / "state.json"), indent=2))


if __name__ == "__main__":
    main()
