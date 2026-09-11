"""Crash-safe persistence, provenance, measured resource guards and status."""

from collections import deque
import fcntl
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import time

VERSION = "0.2.0"
SCHEMA = "conway99-memetic-checkpoint-v2"
DEFAULTS = {
    "version": VERSION,
    "master_seed": 2026091102,
    "objectives": ["L1", "L2", "Linf"],
    "workers": 3,
    "population_per_arm": 32,
    "family_target": 8,
    "hog_family_max": 4,
    "starter_attempts_per_method_arm": 16,
    "starter_walk_attempts_per_reference": 8,
    "startup_active_seconds": 2700,
    "pilot_active_seconds": 86400,
    "task_cpu_seconds": 30.0,
    "task_evaluations": 256,
    "descent_accepted_moves": 32,
    "descent_candidates_per_step": 8,
    "tabu_states": 8,
    "guided_choices": 8,
    "guided_probability": 0.8,
    "status_seconds": 600,
    "checkpoint_seconds": 30,
    "checkpoint_slots": 3,
    "archive_cells": 384,
    "archive_f_bin": 100,
    "worker_rss_limit_mib": 1100,
    "combined_rss_limit_mib": 3072,
    "host_pause_available_mib": 768,
    "host_stop_available_mib": 384,
    "free_disk_floor_gib": 10,
    "worker_watchdog_seconds": 600,
    "log_rotate_mib": 25,
    "log_keep": 4,
    "warmup_generations": 10,
    "stagnation_generations": 5
}


def canonical_json(data):
    # JSON object keys are strings after decoding. Normalize BEFORE sorting
    # so negative/multi-digit integer histogram keys have the same order on
    # both sides of a checkpoint round trip. Reject non-finite JSON numbers.
    normalized = json.loads(json.dumps(data, allow_nan=False))
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fsync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_bytes(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    fsync_directory(path.parent)


def atomic_json(path, data):
    atomic_bytes(path, json.dumps(data, sort_keys=True, indent=4).encode() + b"\n")


class RunLock:
    def __init__(self, directory):
        self.handle = (Path(directory) / "run.lock").open("a+")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.handle.close()
            raise RuntimeError("This run already has an active coordinator")
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(str(os.getpid()) + "\n")
        self.handle.flush()

    def close(self):
        self.handle.close()


class Checkpoints:
    def __init__(self, directory, slots=3):
        self.directory = Path(directory) / "checkpoints"
        self.directory.mkdir(exist_ok=True)
        self.slots = slots

    def save(self, state):
        state["checkpoint_sequence"] = state.get("checkpoint_sequence", 0) + 1
        state["schema"] = SCHEMA
        payload = canonical_json(state)
        wrapper = canonical_json({"sha256": digest(payload), "payload": state})
        if len(wrapper) > 50 * 1024 ** 2:
            raise RuntimeError("Checkpoint exceeds the documented bounded format")
        slot = state["checkpoint_sequence"] % self.slots
        compressed = gzip.compress(wrapper, compresslevel=3, mtime=0)
        atomic_bytes(self.directory / f"checkpoint.{slot}.json.gz", compressed)
        return {"sequence": state["checkpoint_sequence"], "bytes": len(compressed)}

    def load(self):
        valid, damaged = [], []
        files = list(self.directory.glob("checkpoint.*.json.gz"))
        for path in files:
            try:
                wrapper = json.loads(gzip.decompress(path.read_bytes()))
                state = wrapper["payload"]
                if wrapper["sha256"] != digest(canonical_json(state)) or state.get("schema") != SCHEMA:
                    raise ValueError("Digest/schema mismatch")
                valid.append(state)
            except (ValueError, KeyError, OSError, EOFError) as error:
                damaged.append({"file": path.name, "error": str(error)})
        if files and not valid:
            raise RuntimeError("All available checkpoints are invalid; no silent restart")
        state = max(valid, key=lambda s: s["checkpoint_sequence"]) if valid else None
        return state, damaged


class Journal:
    def __init__(self, directory, config):
        self.directory = Path(directory)
        self.maximum = config["log_rotate_mib"] * 1024 ** 2
        self.keep = config["log_keep"]

    def append(self, name, value):
        path = self.directory / f"{name}.jsonl"
        data = canonical_json(value) + b"\n"
        if path.exists() and path.stat().st_size + len(data) > self.maximum:
            for index in range(self.keep - 1, 0, -1):
                old = self.directory / f"{name}.{index}.jsonl"
                new = self.directory / f"{name}.{index + 1}.jsonl"
                if old.exists():
                    os.replace(old, new)
            os.replace(path, self.directory / f"{name}.1.jsonl")
        with path.open("ab") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())


def proc_usage(pid):
    try:
        lines = Path(f"/proc/{pid}/status").read_text().splitlines()
        values = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in lines if ":" in line}
        stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {"rss_mib": int(values.get("VmRSS", "0 kB").split()[0]) / 1024,
                "cpu_seconds": (int(stat[11]) + int(stat[12])) / os.sysconf("SC_CLK_TCK")}
    except (FileNotFoundError, ProcessLookupError):
        return {"rss_mib": 0, "cpu_seconds": 0}


def resources(directory, pids, config):
    info = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, rest = line.split(":", 1)
        info[key] = int(rest.split()[0])
    usage = {str(pid): proc_usage(pid) for pid in pids}
    total_rss = sum(item["rss_mib"] for item in usage.values()) + proc_usage(os.getpid())["rss_mib"]
    free = {"linux_run_directory": shutil.disk_usage(directory).free / 1024 ** 3}
    if Path("/mnt/c").is_dir():
        free["windows_c"] = shutil.disk_usage("/mnt/c").free / 1024 ** 3
    available = info["MemAvailable"] / 1024
    hazards = []
    if available < config["host_stop_available_mib"]:
        hazards.append("HOST_RAM_DANGER")
    if total_rss > config["combined_rss_limit_mib"]:
        hazards.append("COMBINED_RAM_LIMIT")
    if any(v["rss_mib"] > config["worker_rss_limit_mib"] for v in usage.values()):
        hazards.append("WORKER_RAM_LIMIT")
    if min(free.values()) < config["free_disk_floor_gib"]:
        hazards.append("DISK_RESERVE")
    return {"available_mib": available, "combined_rss_mib": total_rss,
            "swap_used_mib": (info.get("SwapTotal", 0) - info.get("SwapFree", 0)) / 1024,
            "free_gib": free, "workers": usage, "hazards": hazards,
            "may_launch": available >= config["host_pause_available_mib"] and not hazards}


def fingerprint(repository, config):
    repository = Path(repository)
    files = list((repository / "src/memetic_v2").glob("*.py"))
    files += list((repository / "data/memetic_v2/reference").glob("*"))
    hashes = {str(p.relative_to(repository)): digest(p.read_bytes()) for p in sorted(files) if p.is_file()}
    installed = {}
    for name in ("ortools", "pynauty", "numpy"):
        try:
            installed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed[name] = None
    runtime_signature = digest(canonical_json({"packages": installed, "python": sys.version}))
    return {"version": VERSION, "files": hashes, "runtime_signature_sha256": runtime_signature, "packages": installed, "code_and_inputs_sha256": digest(canonical_json(hashes)),
            "config_sha256": digest(canonical_json(config)), "python": sys.version}


def format_seconds(value):
    if value is None:
        return "noch nicht belastbar"
    value = max(0, round(value))
    hours, rest = divmod(value, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours}h {minutes:02d}m {seconds:02d}s"


def make_status(state, config, resource_report, active_count):
    population = state.get("population", [])
    samples = state.get("recent_task_wall", [])
    jobs = state.get("jobs", [])
    finished = len(state.get("results", {}))
    remaining = max(0, len(jobs) - finished)
    eta = None
    measured = state.get("throughput_samples", [])
    if len(measured) >= 8:
        duration = measured[-1][0] - measured[0][0]
        done = measured[-1][1] - measured[0][1]
        if duration > 0 and done > 0:
            eta = duration * remaining / done
    pilot_left = max(0, config["pilot_active_seconds"] - state.get("pilot_active_seconds", 0))
    report = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "phase": state["phase"], "generation": state.get("generation", 0),
              "active_workers": active_count, "completed_tasks": state.get("completed_tasks", 0),
              "batch_done": finished, "batch_total": len(jobs),
              "batch_eta_seconds": eta, "eta_samples": len(measured),
              "pilot_active_seconds_remaining": pilot_left if state["phase"] == "PILOT" else None,
              "population": {arm: sum(p["arm"] == arm for p in population) for arm in ("omega", "lambda")},
              "best_F": {arm: min((p["F"] for p in state.get("archive", []) if p["arm"] == arm), default=None) for arm in ("omega", "lambda")},
              "resources": resource_report,
              "eta_scope": "Batch completion from measured coordinator throughput including checkpoints; no solution ETA"}
    return report


def print_status(report):
    print(f"[{report['utc']}] {report['phase']} Generation={report['generation']} "
          f"Aufgaben={report['batch_done']}/{report['batch_total']} Worker={report['active_workers']} "
          f"Population={report['population']} BestF={report['best_F']} "
          f"Batch-ETA={format_seconds(report['batch_eta_seconds'])} "
          f"Pilotrest={format_seconds(report['pilot_active_seconds_remaining'])} "
          f"RSS={report['resources']['combined_rss_mib']:.0f}MiB "
          f"RAM-frei={report['resources']['available_mib']:.0f}MiB", flush=True)
