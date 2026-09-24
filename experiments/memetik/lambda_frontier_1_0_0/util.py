"""Integrity, accounting and owned-process primitives."""
import boot
from common import atomic, sha, checked, core
from archive import file_sha
from runtime import process, THREAD_ENV
from pathlib import Path
import fcntl
import importlib.metadata
import json
import os
import resource
import signal
import sqlite3
import subprocess
import sys
import time

GIB = 1024 ** 3
AUX_LIMITS = {"clocks": 540, "controls": 1260, "harvest": 0, "infrastructure": 1800}
ABORT = False

def abort_requested():
    return ABORT

def child_cpu():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime

def read(path):
    return json.loads(Path(path).read_text())

def own_cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime

def env():
    return {"python": sys.version, "pynauty": importlib.metadata.version("pynauty")}

def lock(path, create=True):
    stream = Path(path).open("a+" if create else "r")
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        stream.close()
        raise
    return stream

def checked_item(graph6, origin):
    rows, scores = checked(graph6, "lambda")
    return {"graph6": graph6, "scores": scores, "state": sha(graph6.encode()),
            "class": core.canonical(rows), "family": "HoG",
            "line": origin, "parent": None}

def receipt_valid(d, allow_failed=False):
    r = read(d / "receipt.json")
    for name, field in (("task.json", "task_sha256"), ("result.json", "result_sha256"),
                        ("checkpoint.json", "checkpoint_sha256"), ("archive.sqlite", "archive_sha256")):
        if r[field] != file_sha(d / name):
            raise RuntimeError("Receipt hash mismatch: " + str(d / name))
    if abs(sum(s["cpu_seconds"] for s in r["sessions"]) - r["cpu_seconds"]) > 1e-6:
        raise RuntimeError("CPU session sum mismatch")
    if r["budget_cpu_seconds"] < r["cpu_seconds"] or r["closed_reserve_cpu_seconds"] < 0:
        raise RuntimeError("Invalid reserve accounting")
    if not allow_failed and (r["exit_code"] or r["status"] not in ("COMPLETE", "PAUSED", "SOLUTION")):
        raise RuntimeError("Failed or unresolved job: " + str(d))
    task_hash = file_sha(d / "task.json")
    c = read(d / "checkpoint.json")
    if c["sha256"] != sha(json.dumps(c["state"], sort_keys=True).encode()) or c["state"]["task_sha256"] != task_hash:
        raise RuntimeError("Changed or corrupt checkpoint")
    return r

def sqlite_frozen(path):
    for suffix in ("-wal", "-journal"):
        p = Path(str(path) + suffix)
        if p.exists() and p.stat().st_size:
            raise RuntimeError("Uncheckpointed SQLite file: " + str(p))
    db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise RuntimeError("SQLite integrity failure")
    finally:
        db.close()

def make_receipt(d, previous, base, ceiling, code, usage, host_start=None, host_end=None):
    actual = usage.ru_utime + usage.ru_stime
    result = read(d / "result.json") if code == 0 and (d / "result.json").exists() else {"status": "FAILED"}
    task = read(d / "task.json")
    sessions = previous.get("sessions", []) + [{
        "cpu_seconds": actual, "budget": ceiling, "exit_code": code,
        "status": result["status"], "host_start": host_start, "host_end": host_end,
        "maxrss_kib": usage.ru_maxrss}]
    r = {"id": task["id"], "kind": task["kind"], "cpu_seconds": previous.get("cpu_seconds", 0) + actual,
         "budget_cpu_seconds": base + actual, "closed_reserve_cpu_seconds": base - previous.get("cpu_seconds", 0),
         "session_cpu_seconds": actual, "sessions": sessions, "exit_code": code, "status": result["status"]}
    for name, field in (("task.json", "task_sha256"), ("result.json", "result_sha256"),
                        ("checkpoint.json", "checkpoint_sha256"), ("archive.sqlite", "archive_sha256")):
        r[field] = file_sha(d / name) if (d / name).exists() else None
    atomic(d / "receipt.json", r)
    return r

class AuxiliaryLedger:
    def __init__(self, run):
        self.path = Path(run) / "auxiliary_ledger.json"
        if not self.path.exists():
            atomic(self.path, {"limits": AUX_LIMITS, "entries": [], "active": None})

    def used(self, category):
        return sum(e["cpu_seconds"] for e in read(self.path)["entries"] if e["category"] == category)

    def remaining(self, category):
        return AUX_LIMITS[category] - self.used(category)

    def begin(self, category, label, maximum):
        value = read(self.path)
        if value["active"] is not None:
            raise RuntimeError("Unresolved auxiliary CPU; diagnosis required")
        if self.remaining(category) < maximum:
            raise RuntimeError("Auxiliary allowance exhausted: " + category)
        value["active"] = {"category": category, "label": label, "maximum": maximum,
                           "pid": os.getpid(), "start_ticks": process(os.getpid())["start_ticks"]}
        atomic(self.path, value)

    def finish(self, seconds, status, extra=None):
        value = read(self.path)
        item = value["active"]
        if item is None:
            raise RuntimeError("No auxiliary transaction")
        value["entries"].append({**item, "cpu_seconds": seconds, "status": status, "details": extra})
        value["active"] = None
        atomic(self.path, value)
        if seconds > item["maximum"] + 0.01 or self.remaining(item["category"]) < 0:
            raise RuntimeError("Auxiliary CPU overrun; no silent budget transfer")

    def charge_infrastructure(self, seconds, label, host_seconds=0):
        value = read(self.path)
        value["entries"].append({"category": "infrastructure", "label": label,
                                "cpu_seconds": seconds + host_seconds,
                                "linux_self_cpu": seconds, "windows_helper_cpu": host_seconds,
                                "status": "ACCOUNTED"})
        atomic(self.path, value)
        if self.remaining("infrastructure") < 0:
            raise RuntimeError("Infrastructure CPU allowance exhausted")

def timed_child(command, stdout_path, ceiling):
    """Only wait4 reaps; failed sessions retain their measured CPU."""
    with Path(stdout_path).open("ab") as log:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, **THREAD_ENV})
    sent = False
    while True:
        pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
        if pid:
            break
        if ABORT and not sent:
            os.kill(proc.pid, signal.SIGTERM)
            sent = True
        time.sleep(0.1)
    proc.returncode = os.waitstatus_to_exitcode(status)
    return proc.returncode, usage

def hashes(root, names):
    return {name: file_sha(root / name) for name in names}
