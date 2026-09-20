"""Only owned subprocesses, wait4 CPU receipts, locks and periodic host guards."""
import fcntl
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import resource
import subprocess
import sys
import time

from common import ROOT, atomic, cpu, sha
from progress import Progress
from resources import GIB, GROUP_LIMIT, RAM_RESERVE, memory, snapshot

HERE = Path(__file__).resolve().parent
THREAD_ENV = {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}


def read(path):
    return json.loads(Path(path).read_text())


def immutable(path, value):
    if path.exists():
        if read(path) != value:
            raise RuntimeError("Frozen input changed: " + str(path))
    else:
        atomic(path, value)


def fingerprint():
    paths = list(HERE.glob("*.py")) + [ROOT / "src/memetic_v2" / n for n in ("core.py", "verify.py")]
    paths += [ROOT / "experiments/memetik/escape_0_2/operators.py"]
    return {"files": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(paths)},
            "python": sys.version,
            "packages": {p: importlib.metadata.version(p) for p in ("pynauty", "ortools", "numpy")}}


def process(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {"cpu": (int(fields[11])+int(fields[12]))/os.sysconf("SC_CLK_TCK"),
                "start_ticks": fields[19], "rss": int(fields[21])*os.sysconf("SC_PAGE_SIZE")}
    except FileNotFoundError:
        return {"cpu": 0, "start_ticks": None, "rss": 0}


class Pool:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.lock = (self.directory / "controller.lock").open("a+")
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.stop = False
        self.active = {}
        self.started = time.monotonic()
        self.last_status = 0
        self.last_host = 0
        self.host = None
        self.cpu_this_session = 0
        self.last_reason = None
        signal.signal(signal.SIGTERM, self.request_stop)
        signal.signal(signal.SIGINT, self.request_stop)

    def request_stop(self, *args):
        self.stop = True

    def emergency_stop_owned(self):
        """Stop owned jobs on error; unresolved CPU receipts stay visibly dirty."""
        for pid in self.active:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        until = time.monotonic()+5
        while self.active and time.monotonic() < until:
            for pid in list(self.active):
                waited, status, usage = os.wait4(pid, os.WNOHANG)
                if waited:
                    entry = self.active.pop(pid)
                    entry["proc"].returncode = os.waitstatus_to_exitcode(status)
                    try:
                        atomic(entry["directory"] / "emergency_cpu_receipt.json",
                               {"cpu_seconds": entry["base"]+usage.ru_utime+usage.ru_stime,
                                "exit_code": entry["proc"].returncode,
                                "status": "DIAGNOSIS_REQUIRED"})
                    except OSError:
                        pass
            if self.active:
                time.sleep(0.1)

    def receipts(self):
        return [read(p) for p in (self.directory / "tasks").glob("*/receipt.json")]

    def check(self):
        now = time.monotonic()
        if now-self.last_host >= 15 or self.host is None:
            self.host = snapshot(self.directory)
            self.last_host = now
        usage = {pid: process(pid) for pid in self.active}
        hazards = list(self.host["hazards"])
        if memory()["MemAvailable"] < RAM_RESERVE:
            hazards.append("HOST_RAM_RESERVE")
        if sum(p["rss"] for p in usage.values()) + process(os.getpid())["rss"] > GROUP_LIMIT:
            hazards.append("GROUP_RAM_LIMIT")
        if any(p["rss"] > GIB for p in usage.values()):
            hazards.append("WORKER_RAM_LIMIT")
        if hazards:
            self.stop = True
            self.last_reason = hazards
        return usage

    def status(self, phase, pending, usage, force=False):
        now = time.monotonic()
        if force or now-self.last_status >= 600:
            receipts = self.receipts()
            charged = sum(r["cpu_seconds"] for r in receipts)
            active_cpu = sum(p["cpu"] for p in usage.values())
            elapsed = now-self.started
            rate = (self.cpu_this_session+active_cpu)/elapsed if elapsed else 0
            remaining = sum(max(0, t["worker_cpu_seconds"]-base) for t, base in pending)
            remaining += sum(max(0, t["task"]["worker_cpu_seconds"]-t["base"]-usage[pid]["cpu"])
                             for pid, t in self.active.items())
            report = {"phase": phase, "active_workers": len(self.active), "pending": len(pending),
                      "worker_cpu_seconds": charged+active_cpu, "session_wall_seconds": elapsed,
                      "cpu_budget_eta_seconds": remaining/rate if rate else None,
                      "eta_scope": "current queued phase CPU ceilings, not time to a solution",
                      "host": self.host, "stop_reason": self.last_reason,
                      "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            if phase == "confirmation":
                from search import key
                best, lengths, classes = {}, {}, {}
                for path in (self.directory / "tasks").glob("*/checkpoint.json"):
                    task = read(path.parent / "task.json")
                    state = read(path)["state"]
                    group = task["arm"]+"/"+task["target"]+"/"+task["variant"]
                    scores = state["best"]["scores"]
                    if group not in best or key(scores, task["target"]) < key(best[group], task["target"]):
                        best[group] = scores
                    classes[task["id"]] = len(state["class_hashes"])
                    for length, count in state["histogram"].get("perturb_length", {}).items():
                        lengths[length] = lengths.get(length, 0)+count
                report.update(best_by_group=best, endpoint_classes_per_run=classes,
                              actual_perturb_length_histogram=lengths)
            atomic(self.directory / "status.json", report)
            print(json.dumps({k: v for k, v in report.items() if k != "host"}), flush=True)
            self.last_status = now

    def run(self, tasks, workers, phase):
        immutable(self.directory / (phase + "_manifest.json"), tasks)
        timing_path = self.directory / (phase + "_timing.json")
        timing = read(timing_path) if timing_path.exists() else {"wall_seconds": 0.0, "clean": True}
        if not timing["clean"]:
            raise RuntimeError("Unclean phase timing; refuse a misleading throughput/resume: " + phase)
        pending = []
        for task in tasks:
            directory = self.directory / "tasks" / task["id"]
            directory.mkdir(parents=True, exist_ok=True)
            immutable(directory / "task.json", task)
            receipt = read(directory / "receipt.json") if (directory / "receipt.json").exists() else None
            if (directory / "active.json").exists():
                raise RuntimeError("Unclean controller stop: CPU receipt unresolved for " + task["id"])
            if receipt and receipt["exit_code"] != 0:
                raise RuntimeError("Failed task needs diagnosis: " + task["id"])
            if receipt and receipt["status"] not in ("PAUSED",):
                continue
            pending.append((task, receipt["cpu_seconds"] if receipt else 0))
        # Budget bounds include *all* tasks and repeated preparation processes.
        categories = {kind: sum(r["cpu_seconds"] for r in self.receipts()
                               if (r["kind"] == "generate") == (kind == "generate")
                               and r["kind"] != "compare") for kind in ("generate", "technical")}
        for task, base in pending:
            if task["kind"] != "compare":
                categories["generate" if task["kind"] == "generate" else "technical"] += max(0, task["worker_cpu_seconds"]-base)
        usage_self = resource.getrusage(resource.RUSAGE_SELF)
        infrastructure_cpu = usage_self.ru_utime+usage_self.ru_stime
        infrastructure_cpu += sum(read(p)["cpu_seconds"] for p in self.directory.glob("controller_cpu_*.json"))
        if categories["generate"] > 32*3600 or categories["technical"] + infrastructure_cpu > 16*3600:
            raise RuntimeError("Preparation CPU ceiling exceeded")
        progress = Progress(self.directory) if phase == "confirmation" else None
        wall_started = time.monotonic()
        atomic(timing_path, {"wall_seconds": timing["wall_seconds"], "clean": False})
        while pending or self.active:
            usage = self.check()
            if self.stop:
                for pid, entry in self.active.items():
                    if not entry.get("stop_sent"):
                        # Popen.terminate may internally poll/reap a child and
                        # lose wait4 usage. An unreaped owned PID cannot be reused.
                        os.kill(pid, signal.SIGTERM)
                        entry["stop_sent"] = True
            while pending and len(self.active) < workers and not self.stop:
                task, base = pending.pop(0)
                directory = self.directory / "tasks" / task["id"]
                log = (directory / "worker.log").open("ab")
                proc = subprocess.Popen([sys.executable, str(HERE / "worker.py"), str(directory)],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, **THREAD_ENV})
                log.close()
                atomic(directory / "active.json", {"pid": proc.pid, "base_cpu_seconds": base,
                                                    "start_ticks": process(proc.pid)["start_ticks"]})
                self.active[proc.pid] = {"proc": proc, "task": task, "base": base, "directory": directory}
            for pid in list(self.active):
                # Do not call Popen.poll/wait: only wait4 may reap the child.
                waited, status, rusage = os.wait4(pid, os.WNOHANG)
                if not waited:
                    continue
                entry = self.active.pop(pid)
                code = os.waitstatus_to_exitcode(status)
                entry["proc"].returncode = code
                actual = rusage.ru_utime+rusage.ru_stime
                self.cpu_this_session += actual
                output = entry["directory"] / "result.json"
                result = read(output) if output.exists() and code == 0 else {"status": "FAILED"}
                receipt = {"id": entry["task"]["id"], "kind": entry["task"]["kind"],
                           "cpu_seconds": entry["base"]+actual, "session_cpu_seconds": actual,
                           "exit_code": code, "status": result["status"],
                           "task_sha256": sha((entry["directory"] / "task.json").read_bytes()),
                           "result_sha256": sha(output.read_bytes()) if output.exists() else None}
                atomic(entry["directory"] / "receipt.json", receipt)
                (entry["directory"] / "active.json").unlink()
                if code != 0:
                    self.stop = True
                    self.last_reason = ["WORKER_FAILED", entry["task"]["id"]]
            usage = {pid: process(pid) for pid in self.active}
            self.status(phase, pending, usage)
            if progress:
                progress.poll()
            if self.stop and not self.active:
                self.status(phase, pending, usage, force=True)
                atomic(timing_path, {"wall_seconds": timing["wall_seconds"]+time.monotonic()-wall_started, "clean": True})
                raise RuntimeError("PAUSED: " + str(self.last_reason or "requested"))
            if pending or self.active:
                time.sleep(0.25)
        if progress:
            progress.poll(force=True)
        self.status(phase, [], {}, force=True)
        wall = timing["wall_seconds"]+time.monotonic()-wall_started
        atomic(timing_path, {"wall_seconds": wall, "clean": True})
        return {"wall_seconds_this_session": wall,
                "results": [read(self.directory / "tasks" / t["id"] / "result.json") for t in tasks],
                "cpu_seconds": sum(read(self.directory / "tasks" / t["id"] / "receipt.json")["cpu_seconds"] for t in tasks)}
