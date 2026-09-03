#!/usr/bin/env python3
"""Conway-99 O3 Task-03 FULLCERT 1.1.

Peer-review-driven hybrid certification runner.

Core result (Stage 1): certify source_task03_triangle_eo.cnf UNSAT by
  * 488 direct root cube LRAT certificates, plus
  * for each of 24 hard roots: either a direct hard-root certificate or all
    terminal Triangle-EO leaf certificates.

Optional baseline lottery (C'): a direct certificate of the baseline CNF
without Triangle-EO would supersede the Stage-1 lemma-CNF result and remove
Lemma-B from the computational conclusion.

The runner is intentionally gated:
  prepare -> calibrate -> inspect calibration -> run
The full 12-core hybrid refuses to start unless calibration_gate.pass is true.

Maintenance commands run-a-only and run-a-only-pure resume the certified modular lane with all 12
solver slots while freezing HARD_RACE and BASELINE exactly as found in state.
"""

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0")
PKG_DIR = Path("/home/rb/conway99_workspace/conway99_o3_qsat_preflight_0.1.12")
CORE = Path("/home/rb/conway99_workspace/o3_qsat_runs/preflight_0.1.12_recovery_20260827/tasks/03-6-3-3-3-3-3-3-3/core.json")
CAKE_LPR = PKG_DIR / "dependencies/bin/cake_lpr"

RESCOUT_DIR = Path("/home/rb/conway99_workspace/o3_qsat_runs/task03_lemma_rescout_20260828")
RESCOUT_STATE = RESCOUT_DIR / "state.json"
RESCOUT_MANIFEST = RESCOUT_DIR / "manifest.json"
LEMMA_SOURCE = RESCOUT_DIR / "source_task03_triangle_eo.cnf"
RESCOUT_CUBES = RESCOUT_DIR / "cubes"

FRONTIER_DIR = Path("/home/rb/conway99_workspace/o3_qsat_runs/task03_triangle_overnight_20260829")
FRONTIER_STATE = FRONTIER_DIR / "state.json"

RUN_DIR = Path("/home/rb/conway99_workspace/o3_qsat_runs/task03_fullcert_1.1_20260829")
CERT_DIR = RUN_DIR / "cert"
RACE_DIR = RUN_DIR / "hard_root_race"
BASELINE_DIR = RUN_DIR / "baseline_lottery"
LOG_DIR = RUN_DIR / "logs"
STATE = RUN_DIR / "state.json"
STATUS = RUN_DIR / "status.json"
INDEX = RUN_DIR / "certificate_index.tsv"
MANIFEST = RUN_DIR / "certificate_manifest.json"
COVERAGE_INPUT = RUN_DIR / "coverage_input.json"
CALIBRATION = RUN_DIR / "calibration.json"
TOOLCHAIN = RUN_DIR / "toolchain.json"
BASELINE_CNF = RUN_DIR / "source_task03_baseline.cnf"
RUNNER_PID = RUN_DIR / "runner.pid"
DRIVER_LOG = RUN_DIR / "driver.log"
COVERAGE_CHECK_LOG = RUN_DIR / "coverage_check.out"
COVERAGE_CHECK_ERR = RUN_DIR / "coverage_check.err"
COVERAGE_CHECKER = PROJECT / "task03_coverage_check_1_1.py"

EXPECTED_ROOTS = 512
EXPECTED_DIRECT_ROOTS = 488
EXPECTED_HARD_ROOTS = 24
EXPECTED_LEAVES = 168
EXPECTED_VARS = 120349
EXPECTED_BASELINE_CLAUSES = 444474
EXPECTED_LEMMA_CLAUSES = 445314
PATTERNS = ("001", "010", "100")

PHYSICAL_CORES = 12
PURE_A_SOLVER_SLOTS = 8
INITIAL_MODULAR_SOLVERS = 8
HARD_RACE_SOLVERS = 2
BASELINE_SOLVERS = 1
LRAT_LIMIT = 4
GZIP_LIMIT = 2
CAKE_BUDGET_GIB = 28.0
CAKE_MIN_ESTIMATE_GIB = 4.0
CAKE_HEAVY_PROOF_MIB = 400.0
CAKE_HEAVY_ESTIMATE_GIB = 12.0
CAKE_CALIBRATION_BOOTSTRAP_GIB = 8.0
CAKE_MODEL_SAFETY = 1.15
# Runtime reservation cap: empirical large-proof validation on 2026-08-30
# saw 4.01 GiB max RSS for a ~21 GiB LRAT proof.  Keep the calibrated
# prediction in metadata, but reserve at most 8 GiB for one serial heavy Cake.
CAKE_RUNTIME_RESERVATION_CAP_GIB = 8.0
MEM_AVAILABLE_FLOOR_GIB = 12.0
# 2026-08-30 operator-approved final-phase disk floor: lowered from 70 GiB
# to 20 GiB, intentionally releasing 50 GiB while retaining a hard watcher
# every CHECK_INTERVAL seconds.
MIN_FREE_GIB = 70.0
CHECK_INTERVAL = 30.0
STATE_TICK = 60.0

MODULAR_SOLVER_TIMEOUT = 6 * 3600
HARD_ROOT_TIMEOUT = 12 * 3600
BASELINE_TIMEOUT = 7 * 24 * 3600
LRAT_CHECK_TIMEOUT = 3600
CAKE_CHECK_TIMEOUT = 6 * 3600
HARD_ROOT_PROOF_CAP_GIB = 40.0
BASELINE_PROOF_CAP_GIB = 60.0
GZIP_LEVEL = 3
CADICAL_OPTIONS = ["--lrat", "--no-binary"]
STOP_ON_GENERIC_JOB_ERROR = False

lock = threading.RLock()
stop_event = threading.Event()
baseline_success_event = threading.Event()
aux_stop_event = threading.Event()
children = {}
last_state_flush = 0.0
state_dirty = False
global_stop_reason = None


def nowstr():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    line = f"{nowstr()} {message}"
    print(line, flush=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with DRIVER_LOG.open("a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def sha256_file(path, block=8 * 1024 * 1024):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(block), b""):
            h.update(data)
    return h.hexdigest()


def fsync_dir(path):
    fd = os.open(str(Path(path)), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_text_fsync(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    with tmp.open("w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fsync_dir(path.parent)


def atomic_json_fsync(path, obj):
    atomic_text_fsync(path, json.dumps(obj, sort_keys=True, indent=2) + "\n")


def read_json(path):
    return json.loads(Path(path).read_text())


def disk_free_gib(path=RUN_DIR):
    Path(path).mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(path).free / (1024 ** 3)


def mem_available_gib():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024 ** 2)
    except OSError:
        pass
    return 0.0


def mem_total_gib():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) / (1024 ** 2)
    except OSError:
        pass
    return 0.0


def parse_dimacs_header(path):
    with Path(path).open() as f:
        for line in f:
            if line.startswith("p cnf "):
                m = re.fullmatch(r"p cnf (\d+) (\d+)\s*", line)
                if not m:
                    raise RuntimeError(f"bad DIMACS header in {path}")
                return int(m.group(1)), int(m.group(2))
    raise RuntimeError(f"missing DIMACS header in {path}")


def parse_time_v(path):
    out = {}
    try:
        text = Path(path).read_text(errors="replace")
    except FileNotFoundError:
        return out
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    if m:
        out["max_rss_kib"] = int(m.group(1))
    m = re.search(r"Elapsed \(wall clock\) time .*?:\s*([^\n]+)", text)
    if m:
        out["elapsed_text"] = m.group(1).strip()
    m = re.search(r"Exit status:\s*(-?\d+)", text)
    if m:
        out["time_exit_status"] = int(m.group(1))
    return out


def grab(text, pattern, cast=int):
    m = re.search(pattern, text, re.M)
    return cast(m.group(1)) if m else None


def cadical_stats(path):
    try:
        text = Path(path).read_text(errors="replace")
    except FileNotFoundError:
        return {}
    return {
        "conflicts": grab(text, r"^c conflicts:\s+(\d+)"),
        "decisions": grab(text, r"^c decisions:\s+(\d+)"),
        "propagations": grab(text, r"^c propagations:\s+(\d+)"),
        "restarts": grab(text, r"^c restarts:\s+(\d+)"),
        "real_s": grab(text, r"^c total real time since initialization:\s+([0-9.]+)", float),
        "max_rss_MB": grab(text, r"^c maximum resident set size of process:\s+([0-9.]+)", float),
    }


def recursive_conflicts(record):
    for name in ("scout_attempts", "attempts"):
        seq = record.get(name) or []
        for attempt in reversed(seq):
            stats = attempt.get("stats") or {}
            if stats.get("conflicts") is not None:
                return int(stats["conflicts"])
            if stats and attempt.get("exitcode") == 20 and not attempt.get("timed_out", False):
                return 0
            for sub in ("solver", "result"):
                s = attempt.get(sub) or {}
                stats = s.get("stats") or {}
                if stats.get("conflicts") is not None:
                    return int(stats["conflicts"])
                if stats and s.get("exitcode") == 20 and not s.get("timed_out", False):
                    return 0
    return None


def recursive_wall(record):
    for name in ("scout_attempts", "attempts"):
        seq = record.get(name) or []
        for attempt in reversed(seq):
            if attempt.get("wall") is not None:
                return float(attempt["wall"])
            for sub in ("solver", "result"):
                s = attempt.get(sub) or {}
                if s.get("wall") is not None:
                    return float(s["wall"])
    return None


def parse_witness_literals(path):
    vals = {}
    for line in Path(path).read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line[0] in "cs":
            continue
        toks = line[1:].split() if line.startswith("v") else line.split()
        for token in toks:
            try:
                lit = int(token)
            except ValueError:
                continue
            if lit:
                vals[abs(lit)] = lit > 0
    return vals


def verify_cnf_witness(cnf, witness):
    vals = parse_witness_literals(witness)
    if not vals:
        return False, "no model literals"
    clauses = 0
    with Path(cnf).open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c") or line.startswith("p"):
                continue
            clauses += 1
            lits = [int(x) for x in line.split() if x != "0"]
            if not any(vals.get(abs(lit)) == (lit > 0) for lit in lits):
                return False, f"unsatisfied-or-unassigned clause {clauses}"
    return True, f"verified {clauses} clauses"


def verify_sat_strong(cnf, witness):
    cnf_ok, cnf_message = verify_cnf_witness(cnf, witness)
    result = {
        "cnf_witness_ok": cnf_ok,
        "cnf_witness_message": cnf_message,
        "model_projection_ok": False,
        "model_projection_message": None,
    }
    if not cnf_ok:
        return False, result
    try:
        if str(PKG_DIR) not in sys.path:
            sys.path.insert(0, str(PKG_DIR))
        from qsat.encode import cnf_from_core
        from qsat.sat_model import primary_edge_map, project_primary_model
        from qsat.verify import verify

        core = read_json(CORE)
        _, edge_vars = cnf_from_core(core)
        selected = project_primary_model(Path(witness).read_text(), primary_edge_map(core, edge_vars))
        verify(core, selected)
        result["model_projection_ok"] = True
        result["model_projection_message"] = "qsat project_primary_model + verify PASS"
        result["selected_edges"] = selected
        return True, result
    except Exception as exc:
        result["model_projection_message"] = f"{type(exc).__name__}: {exc}"
        return False, result


def gzip_and_verify(src, dst, raw_sha):
    tmp = Path(str(dst) + ".tmp")
    with Path(src).open("rb") as fi, gzip.open(tmp, "wb", compresslevel=GZIP_LEVEL) as fo:
        shutil.copyfileobj(fi, fo, length=8 * 1024 * 1024)
    os.replace(tmp, dst)
    fsync_dir(Path(dst).parent)

    h = hashlib.sha256()
    with gzip.open(dst, "rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    decompressed_sha = h.hexdigest()
    if decompressed_sha != raw_sha:
        raise RuntimeError(f"gzip round-trip hash mismatch {decompressed_sha} != {raw_sha}")
    return {
        "gzip_sha256": sha256_file(dst),
        "gzip_bytes": Path(dst).stat().st_size,
        "decompressed_sha256": decompressed_sha,
    }


def tool_version(binary):
    binary = str(binary)
    for args in (["--version"], ["-h"], ["--help"]):
        try:
            p = subprocess.run([binary] + args, capture_output=True, text=True, timeout=20)
            text = ((p.stdout or "") + "\n" + (p.stderr or "")).strip()
            if text:
                return text[:4000]
        except Exception:
            pass
    return "VERSION_UNAVAILABLE"


def collect_toolchain():
    cadical = shutil.which("cadical")
    lrat = shutil.which("lrat-check")
    if not cadical or not lrat or not CAKE_LPR.exists():
        raise RuntimeError("required tool missing: cadical/lrat-check/cake_lpr")
    tools = {}
    for name, path in (("cadical", Path(cadical)), ("lrat-check", Path(lrat)), ("cake_lpr", CAKE_LPR)):
        tools[name] = {
            "path": str(path.resolve()),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "version_output": tool_version(path),
        }
    if "2.2.1" not in tools["cadical"]["version_output"]:
        raise RuntimeError("CaDiCaL 2.2.1 required for the frozen LRAT toolchain; got: " + tools["cadical"]["version_output"][:200])
    return tools


def generate_baseline_cnf():
    if str(PKG_DIR) not in sys.path:
        sys.path.insert(0, str(PKG_DIR))
    from qsat.encode import write_cnf

    core = read_json(CORE)
    tmp = Path(str(BASELINE_CNF) + ".tmp")
    if tmp.exists():
        tmp.unlink()
    write_cnf(core, tmp)
    nv, nc = parse_dimacs_header(tmp)
    if nv != EXPECTED_VARS or nc != EXPECTED_BASELINE_CLAUSES:
        raise RuntimeError(f"baseline header mismatch vars={nv} clauses={nc}")
    os.replace(tmp, BASELINE_CNF)
    fsync_dir(BASELINE_CNF.parent)
    return {
        "path": str(BASELINE_CNF),
        "sha256": sha256_file(BASELINE_CNF),
        "variables": nv,
        "clauses": nc,
        "bytes": BASELINE_CNF.stat().st_size,
    }


def terminate_process_group(proc, grace=30):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return proc.poll()
    try:
        return proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return proc.wait()


def run_process(cmd, stdout_path, stderr_path, timeout, timefile=None,
                watch_file=None, file_cap_gib=None, projected_extra_gib=0.0,
                global_disk_stop=True, local_stop_event=None):
    started = time.time()
    timed_out = False
    stopped = False
    disk_stop = False
    file_cap_stop = False
    stdout_path = Path(stdout_path)
    stderr_path = Path(stderr_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    run_cmd = list(cmd)
    if timefile is not None:
        run_cmd = ["/usr/bin/time", "-v", "-o", str(timefile)] + run_cmd

    if disk_free_gib() - projected_extra_gib < MIN_FREE_GIB:
        return {
            "started": started,
            "ended": time.time(),
            "wall": 0.0,
            "exitcode": None,
            "timed_out": False,
            "stopped": False,
            "disk_stop": True,
            "file_cap_stop": False,
            "command": run_cmd,
            "prestart_resource_reject": True,
        }

    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        proc = subprocess.Popen(run_cmd, stdout=out, stderr=err, start_new_session=True)
        with lock:
            children[proc.pid] = proc
        last_watch = 0.0
        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    break
                now = time.time()
                if stop_event.is_set() or (local_stop_event is not None and local_stop_event.is_set()):
                    stopped = True
                    rc = terminate_process_group(proc)
                    break
                if timeout is not None and now - started >= timeout:
                    timed_out = True
                    rc = terminate_process_group(proc)
                    break
                if now - last_watch >= CHECK_INTERVAL:
                    last_watch = now
                    free = disk_free_gib()
                    if free < MIN_FREE_GIB:
                        disk_stop = True
                        rc = terminate_process_group(proc)
                        if global_disk_stop:
                            request_stop(f"DISK_FLOOR_{free:.1f}GIB")
                        break
                    if watch_file is not None and file_cap_gib is not None:
                        p = Path(watch_file)
                        if p.exists() and p.stat().st_size > file_cap_gib * (1024 ** 3):
                            file_cap_stop = True
                            rc = terminate_process_group(proc)
                            break
                time.sleep(1)
        finally:
            with lock:
                children.pop(proc.pid, None)

    rec = {
        "started": started,
        "ended": time.time(),
        "wall": time.time() - started,
        "exitcode": rc,
        "timed_out": timed_out,
        "stopped": stopped,
        "disk_stop": disk_stop,
        "file_cap_stop": file_cap_stop,
        "command": run_cmd,
    }
    if timefile is not None:
        rec["time_v"] = parse_time_v(timefile)
    return rec


def request_stop(reason):
    global state_dirty, global_stop_reason
    with lock:
        stop_event.set()
        state_dirty = True
        if global_stop_reason is None:
            global_stop_reason = reason
        procs = list(children.values())
    for proc in procs:
        terminate_process_group(proc, grace=10)


def signal_handler(signum, frame):
    request_stop(f"SIGNAL_{signum}")


class AdjustableLimiter:
    def __init__(self, limit):
        self.limit = int(limit)
        self.in_use = 0
        self.cond = threading.Condition()

    def set_limit(self, limit):
        with self.cond:
            self.limit = int(limit)
            self.cond.notify_all()

    def acquire(self):
        with self.cond:
            while self.in_use >= self.limit:
                if stop_event.is_set():
                    return False
                self.cond.wait(timeout=2)
            self.in_use += 1
            return True

    def release(self):
        with self.cond:
            self.in_use -= 1
            self.cond.notify_all()

    def snapshot(self):
        with self.cond:
            return {"limit": self.limit, "in_use": self.in_use}


class CakeAdmission:
    def __init__(self, budget_gib):
        self.budget = float(budget_gib)
        self.reserved = 0.0
        self.heavy_in_use = False
        self.cond = threading.Condition()

    def acquire(self, estimate_gib, heavy):
        need = max(CAKE_MIN_ESTIMATE_GIB, float(estimate_gib))
        total = mem_total_gib()
        if need > self.budget or (total > 0 and MEM_AVAILABLE_FLOOR_GIB + need > total):
            request_stop(
                "CAKE_ADMISSION_IMPOSSIBLE_"
                f"need={need:.2f}GiB_budget={self.budget:.2f}GiB_total={total:.2f}GiB"
            )
            return None
        with self.cond:
            while True:
                if stop_event.is_set():
                    return None
                mem_ok = mem_available_gib() >= MEM_AVAILABLE_FLOOR_GIB + need
                budget_ok = self.reserved + need <= self.budget
                heavy_ok = (not heavy) or (not self.heavy_in_use)
                if mem_ok and budget_ok and heavy_ok:
                    self.reserved += need
                    if heavy:
                        self.heavy_in_use = True
                    return need
                self.cond.wait(timeout=5)

    def release(self, reserved_gib, heavy):
        with self.cond:
            self.reserved = max(0.0, self.reserved - float(reserved_gib))
            if heavy:
                self.heavy_in_use = False
            self.cond.notify_all()

    def snapshot(self):
        with self.cond:
            return {
                "budget_gib": self.budget,
                "reserved_gib": self.reserved,
                "heavy_in_use": self.heavy_in_use,
            }


cpu_slots = AdjustableLimiter(PHYSICAL_CORES)
modular_solver_slots = AdjustableLimiter(INITIAL_MODULAR_SOLVERS)
hard_race_slots = AdjustableLimiter(HARD_RACE_SOLVERS)
baseline_slots = AdjustableLimiter(BASELINE_SOLVERS)
lrat_slots = AdjustableLimiter(LRAT_LIMIT)
gzip_slots = AdjustableLimiter(GZIP_LIMIT)
cake_admission = CakeAdmission(CAKE_BUDGET_GIB)


def branch_tree_checks(rescout, frontier):
    roots = sorted(rescout["cubes"])
    direct = sorted(k for k, r in rescout["cubes"].items() if r["state"] == "UNSAT_UNCERTIFIED")
    hard = sorted(k for k, r in rescout["cubes"].items() if r["state"] == "TIMEOUT")
    if roots != [format(i, "09b") for i in range(512)]:
        raise RuntimeError("root 9-bit partition incomplete")
    if len(direct) != EXPECTED_DIRECT_ROOTS or len(hard) != EXPECTED_HARD_ROOTS:
        raise RuntimeError(f"unexpected rescout partition direct={len(direct)} hard={len(hard)}")
    if sorted(frontier["root_timeout_parents"]) != hard:
        raise RuntimeError("frontier hard-root set differs from rescout TIMEOUT set")

    jobs = frontier["jobs"]
    children_by_parent = defaultdict(list)
    d1_by_root = defaultdict(list)
    for key, record in jobs.items():
        if record.get("parent_job"):
            children_by_parent[record["parent_job"]].append((key, record))
        if record["depth"] == 1:
            d1_by_root[record["root_parent"]].append((key, record))

    split_groups = set()
    for root in hard:
        kids = d1_by_root[root]
        if sorted(r["pattern"] for _, r in kids) != list(PATTERNS):
            raise RuntimeError(f"bad first-level branching root={root}")
        groups = {tuple(r["split_vars"]) for _, r in kids}
        if len(groups) != 1:
            raise RuntimeError(f"inconsistent first split vars root={root}")
        split_groups |= groups

    for key, record in jobs.items():
        if record["state"] == "TIMEOUT":
            kids = children_by_parent.get(key, [])
            if sorted(r["pattern"] for _, r in kids) != list(PATTERNS):
                raise RuntimeError(f"TIMEOUT node lacks exact EO children key={key}")
            groups = {tuple(r["split_vars"]) for _, r in kids}
            if len(groups) != 1:
                raise RuntimeError(f"inconsistent child split vars key={key}")
            split_groups |= groups

    parent_keys = set(children_by_parent)
    leaves = sorted((k, r) for k, r in jobs.items() if k not in parent_keys)
    if len(leaves) != EXPECTED_LEAVES:
        raise RuntimeError(f"expected {EXPECTED_LEAVES} leaves, got {len(leaves)}")
    if any(r["state"] != "UNSAT_UNCERTIFIED" for _, r in leaves):
        raise RuntimeError("non-UNSAT frontier leaf")
    return {
        "roots": roots,
        "direct": direct,
        "hard": hard,
        "leaves": leaves,
        "split_groups": sorted(split_groups),
        "internal_timeouts": sum(r["state"] == "TIMEOUT" for r in jobs.values()),
    }


def verify_eo_clauses(split_groups):
    required = {}
    for group in split_groups:
        x, y, z = group
        required[group] = {
            tuple(sorted((x, y, z))),
            tuple(sorted((-x, -y))),
            tuple(sorted((-x, -z))),
            tuple(sorted((-y, -z))),
        }
    wanted = set().union(*required.values()) if required else set()
    seen = set()
    with LEMMA_SOURCE.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c") or line.startswith("p"):
                continue
            lits = tuple(sorted(int(x) for x in line.split() if x != "0"))
            if lits in wanted:
                seen.add(lits)
    missing = {str(g): sorted(cs - seen) for g, cs in required.items() if cs - seen}
    if missing:
        raise RuntimeError(f"lemma source missing EO clauses: {missing}")
    return {
        "groups_checked": len(split_groups),
        "clauses_per_group": 4,
        "all_present": True,
    }


def make_modular_specs(rescout, tree):
    jobs = {}
    for bits in tree["direct"]:
        rec = rescout["cubes"][bits]
        jobs["ROOT_" + bits] = {
            "lane": "MODULAR",
            "kind": "ROOT",
            "root": bits,
            "frontier_key": None,
            "cnf": str(RESCOUT_CUBES / f"cube_{bits}.cnf"),
            "cnf_sha256": rec["cnf_sha256"],
            "scout_conflicts": recursive_conflicts(rec),
            "scout_wall": recursive_wall(rec),
        }
    for key, rec in tree["leaves"]:
        jobs["LEAF_" + key] = {
            "lane": "MODULAR",
            "kind": "LEAF",
            "root": rec["root_parent"],
            "frontier_key": key,
            "cnf": rec["cnf"],
            "cnf_sha256": rec["cnf_sha256"],
            "scout_conflicts": recursive_conflicts(rec),
            "scout_wall": recursive_wall(rec),
        }
    if len(jobs) != EXPECTED_DIRECT_ROOTS + EXPECTED_LEAVES:
        raise RuntimeError(f"unexpected modular job count {len(jobs)}")
    return jobs


def make_race_specs(rescout, tree):
    jobs = {}
    leaf_conflict_sum = defaultdict(int)
    for _, rec in tree["leaves"]:
        c = recursive_conflicts(rec)
        if c is not None:
            leaf_conflict_sum[rec["root_parent"]] += c
    for bits in tree["hard"]:
        rec = rescout["cubes"][bits]
        jobs[bits] = {
            "lane": "HARD_RACE",
            "kind": "HARD_ROOT",
            "root": bits,
            "cnf": str(RESCOUT_CUBES / f"cube_{bits}.cnf"),
            "cnf_sha256": rec["cnf_sha256"],
            "leaf_conflict_sum": leaf_conflict_sum.get(bits, 0),
        }
    return jobs


def verify_specs_hashes(specs, workers=8):
    def check(item):
        key, spec = item
        p = Path(spec["cnf"])
        if not p.exists():
            return key, False, "missing"
        actual = sha256_file(p)
        return key, actual == spec["cnf_sha256"], actual

    bad = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for key, ok, detail in ex.map(check, specs.items()):
            if not ok:
                bad.append((key, detail))
    if bad:
        raise RuntimeError(f"CNF hash mismatch: {bad[:5]}")


def choose_calibration_sentinels(modular_jobs):
    leaves = sorted(
        ((k, r) for k, r in modular_jobs.items() if r["kind"] == "LEAF" and r.get("scout_conflicts") is not None),
        key=lambda kv: kv[1]["scout_conflicts"],
    )
    roots = sorted(
        ((k, r) for k, r in modular_jobs.items() if r["kind"] == "ROOT" and r.get("scout_conflicts") is not None),
        key=lambda kv: kv[1]["scout_conflicts"],
    )
    if len(leaves) != EXPECTED_LEAVES or len(roots) != EXPECTED_DIRECT_ROOTS:
        raise RuntimeError(f"missing scout conflicts leaves={len(leaves)} roots={len(roots)}")

    def qpick(items, q):
        idx = int(round(q * (len(items) - 1)))
        return items[idx]

    picks = [
        ("LEAF_P10",) + qpick(leaves, 0.10),
        ("LEAF_P50",) + qpick(leaves, 0.50),
        ("LEAF_P90",) + qpick(leaves, 0.90),
        ("ROOT_P50",) + qpick(roots, 0.50),
        ("ROOT_MAX",) + roots[-1],
    ]
    return [
        {
            "label": label,
            "job_key": key,
            "kind": spec["kind"],
            "scout_conflicts": spec["scout_conflicts"],
            "scout_wall": spec.get("scout_wall"),
        }
        for label, key, spec in picks
    ]


def prepare():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CERT_DIR.mkdir(exist_ok=True)
    RACE_DIR.mkdir(exist_ok=True)
    BASELINE_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    if not COVERAGE_CHECKER.exists():
        raise SystemExit(f"coverage checker missing: {COVERAGE_CHECKER}")

    tools = collect_toolchain()
    atomic_json_fsync(TOOLCHAIN, tools)

    rescout_sha = sha256_file(RESCOUT_STATE)
    frontier_sha = sha256_file(FRONTIER_STATE)
    lemma_sha = sha256_file(LEMMA_SOURCE)
    core_sha = sha256_file(CORE)
    rescout = read_json(RESCOUT_STATE)
    frontier = read_json(FRONTIER_STATE)
    tree = branch_tree_checks(rescout, frontier)
    eo = verify_eo_clauses(tree["split_groups"])

    nv, nc = parse_dimacs_header(LEMMA_SOURCE)
    if nv != EXPECTED_VARS or nc != EXPECTED_LEMMA_CLAUSES:
        raise SystemExit(f"lemma source header mismatch vars={nv} clauses={nc}")

    modular_specs = make_modular_specs(rescout, tree)
    race_specs = make_race_specs(rescout, tree)
    verify_specs_hashes(modular_specs, workers=8)
    verify_specs_hashes(race_specs, workers=8)
    baseline = generate_baseline_cnf()

    coverage_input = {
        "format": "O3-QSAT-TASK03-COVERAGE-INPUT-1.1",
        "lemma_source": str(LEMMA_SOURCE),
        "lemma_source_sha256": lemma_sha,
        "rescout_state": str(RESCOUT_STATE),
        "rescout_state_sha256": rescout_sha,
        "frontier_state": str(FRONTIER_STATE),
        "frontier_state_sha256": frontier_sha,
        "core": str(CORE),
        "core_sha256": core_sha,
        "root_partition_complete": tree["roots"] == [format(i, "09b") for i in range(512)],
        "direct_roots": tree["direct"],
        "hard_roots": tree["hard"],
        "internal_timeouts": tree["internal_timeouts"],
        "leaf_keys": [k for k, _ in tree["leaves"]],
        "eo": eo,
    }
    atomic_json_fsync(COVERAGE_INPUT, coverage_input)

    sentinels = choose_calibration_sentinels(modular_specs)

    if STATE.exists():
        state = read_json(STATE)
        expected = {
            "source_cnf_sha256": lemma_sha,
            "rescout_state_sha256": rescout_sha,
            "frontier_state_sha256": frontier_sha,
            "core_sha256": core_sha,
        }
        bad = {k: (state.get(k), v) for k, v in expected.items() if state.get(k) != v}
        if bad:
            raise SystemExit(f"existing state provenance mismatch: {bad}")
        if sorted(state["modular_jobs"]) != sorted(modular_specs):
            raise SystemExit("existing modular job keys differ")
        if sorted(state["race_jobs"]) != sorted(race_specs):
            raise SystemExit("existing race job keys differ")
        log(f"PREPARE_EXISTS phase={state['phase']} modular={len(modular_specs)} race={len(race_specs)}")
        return

    modular_jobs = {}
    for key, spec in modular_specs.items():
        rec = dict(spec)
        rec.update({"state": "PENDING", "attempts": [], "failure": None})
        modular_jobs[key] = rec
    race_jobs = {}
    for key, spec in race_specs.items():
        rec = dict(spec)
        rec.update({"state": "PENDING", "attempts": [], "failure": None})
        race_jobs[key] = rec

    state = {
        "format": "O3-QSAT-TASK03-FULLCERT-1.1",
        "prepared_at": time.time(),
        "started_at": None,
        "ended_at": None,
        "phase": "PREPARED",
        "stop_reason": None,
        "source_cnf": str(LEMMA_SOURCE),
        "source_cnf_sha256": lemma_sha,
        "rescout_state_sha256": rescout_sha,
        "frontier_state_sha256": frontier_sha,
        "core_sha256": core_sha,
        "coverage_input_sha256": sha256_file(COVERAGE_INPUT),
        "toolchain_sha256": sha256_file(TOOLCHAIN),
        "baseline": baseline,
        "calibration_sentinels": sentinels,
        "calibration_gate": None,
        "scheduler": {
            "physical_cores": PHYSICAL_CORES,
            "initial_modular_solvers": INITIAL_MODULAR_SOLVERS,
            "hard_race_solvers": HARD_RACE_SOLVERS,
            "baseline_solvers": BASELINE_SOLVERS,
            "lrat_limit": LRAT_LIMIT,
            "cake_budget_gib": CAKE_BUDGET_GIB,
            "gzip_limit": GZIP_LIMIT,
        },
        "modular_jobs": modular_jobs,
        "race_jobs": race_jobs,
        "baseline_job": {
            "state": "PENDING",
            "attempts": [],
            "failure": None,
            "cnf": str(BASELINE_CNF),
            "cnf_sha256": baseline["sha256"],
        },
    }
    save_state(state, terminal=True)
    log(
        "PREPARE_OK modular=656 roots=488 leaves=168 hard_race=24 "
        f"EO_groups={eo['groups_checked']} sentinels=" +
        ",".join(f"{s['label']}:{s['job_key']}:{s['scout_conflicts']}" for s in sentinels)
    )


def mark_dirty():
    global state_dirty
    state_dirty = True


def save_state(state, terminal=False):
    global last_state_flush, state_dirty
    with lock:
        now = time.time()
        if not terminal and not state_dirty and now - last_state_flush < STATE_TICK:
            return
        atomic_json_fsync(STATE, state)
        write_status_file(state)
        if terminal:
            write_index(state)
        last_state_flush = now
        state_dirty = False


def write_status_file(state):
    mod = Counter(r["state"] for r in state["modular_jobs"].values())
    race = Counter(r["state"] for r in state["race_jobs"].values())
    payload = {
        "phase": state["phase"],
        "stop_reason": state.get("stop_reason"),
        "modular": dict(sorted(mod.items())),
        "race": dict(sorted(race.items())),
        "baseline": state["baseline_job"]["state"],
        "calibration_gate": state.get("calibration_gate"),
        "disk_free_gib": disk_free_gib(),
        "mem_available_gib": mem_available_gib(),
        "cpu_slots": cpu_slots.snapshot(),
        "modular_solver_slots": modular_solver_slots.snapshot(),
        "hard_race_slots": hard_race_slots.snapshot(),
        "lrat_slots": lrat_slots.snapshot(),
        "cake": cake_admission.snapshot(),
        "gzip_slots": gzip_slots.snapshot(),
    }
    atomic_json_fsync(STATUS, payload)


def write_index(state):
    rows = []
    for lane_name, jobs in (("MODULAR", state["modular_jobs"]), ("HARD_RACE", state["race_jobs"])):
        for key, rec in sorted(jobs.items()):
            last = rec["attempts"][-1] if rec.get("attempts") else {}
            rows.append({
                "lane": lane_name,
                "key": key,
                "kind": rec.get("kind"),
                "root": rec.get("root"),
                "state": rec["state"],
                "scout_conflicts": rec.get("scout_conflicts", rec.get("leaf_conflict_sum", "")),
                "raw_proof_bytes": last.get("raw_proof_bytes", ""),
                "gzip_bytes": last.get("gzip_bytes", ""),
                "solver_wall": (last.get("solver") or {}).get("wall", ""),
                "cake_rss_kib": ((last.get("cake_lpr") or {}).get("time_v") or {}).get("max_rss_kib", ""),
                "failure": rec.get("failure") or "",
            })
    with INDEX.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
        f.flush()
        os.fsync(f.fileno())
    fsync_dir(INDEX.parent)


def reset_interrupted(state):
    changed = False
    for jobs in (state["modular_jobs"], state["race_jobs"]):
        for rec in jobs.values():
            if rec["state"] in ("RUNNING", "CHECKING", "COMPRESSING"):
                rec["state"] = "PENDING"
                rec["failure"] = "RESET_FROM_INTERRUPTED_STATE"
                changed = True
            if rec["state"] == "CERTIFIED" and rec.get("attempts"):
                a = rec["attempts"][-1]
                gz = Path(a.get("proof_gz", ""))
                if not gz.exists() or sha256_file(gz) != a.get("gzip_sha256"):
                    rec["state"] = "PENDING"
                    rec["failure"] = "CERT_ARTIFACT_MISSING_OR_HASH_MISMATCH_ON_RESUME"
                    changed = True
    b = state["baseline_job"]
    if b["state"] in ("RUNNING", "CHECKING", "COMPRESSING"):
        b["state"] = "PENDING"
        b["failure"] = "RESET_FROM_INTERRUPTED_STATE"
        changed = True
    if changed:
        mark_dirty()
        save_state(state, terminal=True)


def proof_dir_for(key, rec, lane):
    if lane == "MODULAR":
        group = "root" if rec["kind"] == "ROOT" else "leaf"
        name = rec["root"] if rec["kind"] == "ROOT" else rec["frontier_key"]
        return CERT_DIR / group / name
    if lane == "HARD_RACE":
        return RACE_DIR / rec["root"]
    return BASELINE_DIR


def calibration_model(state):
    gate = state.get("calibration_gate") or {}
    return gate.get("model") or {}


def estimate_proof_bytes(state, conflicts):
    model = calibration_model(state)
    if conflicts is None or not model:
        return int(600 * 1024 ** 2)
    intercept = float(model.get("proof_intercept_bytes", 111.6 * 1024 ** 2))
    slope = float(model.get("proof_slope_bytes_per_conflict", 390.0))
    return max(64 * 1024 ** 2, int(intercept + slope * float(conflicts)))


def certified_calibration_cake_samples(state):
    samples = []
    sentinel_keys = {s["job_key"] for s in state.get("calibration_sentinels", [])}
    for key in sentinel_keys:
        rec = state["modular_jobs"].get(key)
        if not rec or rec.get("state") != "CERTIFIED" or not rec.get("attempts"):
            continue
        a = rec["attempts"][-1]
        raw = a.get("raw_proof_bytes")
        rss_kib = ((a.get("cake_lpr") or {}).get("time_v") or {}).get("max_rss_kib")
        if raw and rss_kib:
            samples.append((raw / (1024 ** 3), rss_kib / (1024 ** 2)))
    return samples


def provisional_calibration_cake_gib(state, proof_bytes):
    proof_gib = proof_bytes / (1024 ** 3)
    samples = certified_calibration_cake_samples(state)
    if len(samples) < 2:
        return CAKE_CALIBRATION_BOOTSTRAP_GIB
    xs = [x for x, _ in samples]
    ys = [y for _, y in samples]
    intercept, slope = fit_linear(xs, ys)
    intercept = max(0.0, intercept)
    slope = max(0.0, slope)
    base = [max(CAKE_MIN_ESTIMATE_GIB, intercept + slope * x) for x in xs]
    envelope = max((y / p for y, p in zip(ys, base)), default=1.0)
    safety = CAKE_MODEL_SAFETY * max(1.0, envelope)
    return max(CAKE_MIN_ESTIMATE_GIB, safety * (intercept + slope * proof_gib))


def estimate_cake_gib(state, proof_bytes):
    model = calibration_model(state)
    proof_gib = proof_bytes / (1024 ** 3)
    if model and "cake_rss_intercept_gib" in model:
        intercept = float(model.get("cake_rss_intercept_gib", 0.0))
        slope = float(model.get("cake_rss_gib_per_proof_gib", 0.0))
        return max(CAKE_MIN_ESTIMATE_GIB, intercept + slope * proof_gib)
    if state.get("phase") == "CALIBRATING":
        return provisional_calibration_cake_gib(state, proof_bytes)
    beta = float(model.get("cake_rss_gib_per_proof_gib", 10.0))
    return max(CAKE_MIN_ESTIMATE_GIB, beta * proof_gib)


def acquire_process_slot(lane, phase):
    if phase == "solver":
        lane_limiter = modular_solver_slots if lane == "MODULAR" else hard_race_slots if lane == "HARD_RACE" else baseline_slots
    elif phase == "lrat":
        lane_limiter = lrat_slots
    else:
        lane_limiter = None
    if lane_limiter is not None and not lane_limiter.acquire():
        return False
    if not cpu_slots.acquire():
        if lane_limiter is not None:
            lane_limiter.release()
        return False
    return True


def release_process_slot(lane, phase):
    cpu_slots.release()
    if phase == "solver":
        if lane == "MODULAR":
            modular_solver_slots.release()
        elif lane == "HARD_RACE":
            hard_race_slots.release()
        else:
            baseline_slots.release()
    elif phase == "lrat":
        lrat_slots.release()


def certify_pipeline(key, rec, lane, state, solver_timeout, proof_cap_gib=None):
    attempt = {"started_at": time.time(), "lane": lane}
    cnf = Path(rec["cnf"])
    if sha256_file(cnf) != rec["cnf_sha256"]:
        raise RuntimeError("CNF_HASH_MISMATCH_BEFORE_SOLVER")

    outdir = proof_dir_for(key, rec, lane)
    outdir.mkdir(parents=True, exist_ok=True)
    proof = outdir / "proof.lrat"
    proof_gz = outdir / "proof.lrat.gz"
    witness = outdir / "witness.out"
    solver_out = outdir / "solver.out"
    solver_err = outdir / "solver.err"
    solver_time = outdir / "solver.time"
    lrat_out = outdir / "lrat_check.out"
    lrat_err = outdir / "lrat_check.err"
    lrat_time = outdir / "lrat_check.time"
    cake_out = outdir / "cake_lpr.out"
    cake_err = outdir / "cake_lpr.err"
    cake_time = outdir / "cake_lpr.time"

    for p in (proof, witness, solver_out, solver_err, solver_time, lrat_out, lrat_err, lrat_time, cake_out, cake_err, cake_time):
        try:
            p.unlink()
        except FileNotFoundError:
            pass

    predicted = estimate_proof_bytes(state, rec.get("scout_conflicts"))
    predicted_gib = predicted / (1024 ** 3)
    local_stop = aux_stop_event if lane in ("HARD_RACE", "BASELINE") else None

    if not acquire_process_slot(lane, "solver"):
        return "STOPPED", attempt
    try:
        solver = run_process(
            ["cadical"] + CADICAL_OPTIONS + ["-w", str(witness), str(cnf), str(proof)],
            solver_out,
            solver_err,
            solver_timeout,
            timefile=solver_time,
            watch_file=proof,
            file_cap_gib=proof_cap_gib,
            projected_extra_gib=min(predicted_gib * 1.5, proof_cap_gib or predicted_gib * 1.5),
            global_disk_stop=True,
            local_stop_event=local_stop,
        )
    finally:
        release_process_slot(lane, "solver")
    solver["stats"] = cadical_stats(solver_out)
    attempt["solver"] = solver

    if solver.get("file_cap_stop"):
        attempt["incomplete_proof_bytes"] = proof.stat().st_size if proof.exists() else 0
        return "PROOF_CAP", attempt
    if solver.get("disk_stop"):
        return "DISK_STOP", attempt
    if solver.get("timed_out"):
        attempt["incomplete_proof_bytes"] = proof.stat().st_size if proof.exists() else 0
        return "TIMEOUT", attempt
    if solver.get("stopped"):
        return "STOPPED", attempt

    if solver["exitcode"] == 10:
        sat_ok, sat_detail = verify_sat_strong(cnf, witness)
        attempt["sat_verification"] = sat_detail
        attempt["witness_sha256"] = sha256_file(witness) if witness.exists() else None
        attempt["cnf_frozen_sha256"] = sha256_file(cnf)
        if sat_ok:
            frozen = outdir / "SAT_ARTIFACTS_FROZEN.json"
            atomic_json_fsync(frozen, {
                "key": key,
                "lane": lane,
                "cnf": str(cnf),
                "cnf_sha256": sha256_file(cnf),
                "witness": str(witness),
                "witness_sha256": attempt["witness_sha256"],
                "verification": sat_detail,
            })
            return "SAT_VERIFIED", attempt
        return "SAT_INVALID", attempt

    if solver["exitcode"] != 20 or not proof.exists():
        return f"SOLVER_EXIT_{solver['exitcode']}", attempt

    raw_sha = sha256_file(proof)
    raw_bytes = proof.stat().st_size
    cnf_before = sha256_file(cnf)
    attempt["raw_proof_sha256"] = raw_sha
    attempt["raw_proof_bytes"] = raw_bytes
    attempt["cnf_sha256_before_checks"] = cnf_before

    if not acquire_process_slot(lane, "lrat"):
        return "STOPPED", attempt
    try:
        lrat = run_process(
            ["lrat-check", str(cnf), str(proof)],
            lrat_out,
            lrat_err,
            LRAT_CHECK_TIMEOUT,
            timefile=lrat_time,
            projected_extra_gib=0.0,
            local_stop_event=local_stop,
        )
    finally:
        release_process_slot(lane, "lrat")
    attempt["lrat_check"] = lrat
    if lrat.get("timed_out"):
        return "LRAT_TIMEOUT", attempt
    if lrat.get("stopped") or lrat.get("disk_stop"):
        return "STOPPED", attempt
    if lrat["exitcode"] != 0:
        return f"LRAT_EXIT_{lrat['exitcode']}", attempt

    cake_est = estimate_cake_gib(state, raw_bytes)
    heavy = raw_bytes > CAKE_HEAVY_PROOF_MIB * 1024 ** 2 or cake_est > CAKE_HEAVY_ESTIMATE_GIB
    cake_runtime_est = min(cake_est, CAKE_RUNTIME_RESERVATION_CAP_GIB)
    reserved = cake_admission.acquire(cake_runtime_est, heavy)
    if reserved is None:
        return "STOPPED", attempt
    if not cpu_slots.acquire():
        cake_admission.release(reserved, heavy)
        return "STOPPED", attempt
    try:
        cake = run_process(
            [str(CAKE_LPR), str(cnf), str(proof)],
            cake_out,
            cake_err,
            CAKE_CHECK_TIMEOUT,
            timefile=cake_time,
            projected_extra_gib=0.0,
            local_stop_event=local_stop,
        )
    finally:
        cpu_slots.release()
        cake_admission.release(reserved, heavy)
    cake["admission_model_estimate_gib"] = cake_est
    cake["admission_runtime_estimate_gib"] = cake_runtime_est
    cake["admission_reserved_gib"] = reserved
    cake["heavy_lane"] = heavy
    attempt["cake_lpr"] = cake
    if cake.get("timed_out"):
        return "CAKE_TIMEOUT", attempt
    if cake.get("stopped") or cake.get("disk_stop"):
        return "STOPPED", attempt
    if cake["exitcode"] != 0:
        return f"CAKE_EXIT_{cake['exitcode']}", attempt

    cnf_after = sha256_file(cnf)
    proof_after = sha256_file(proof)
    attempt["cnf_sha256_after_checks"] = cnf_after
    attempt["raw_proof_sha256_after_checks"] = proof_after
    if cnf_before != cnf_after or cnf_before != rec["cnf_sha256"]:
        return "CNF_HASH_INSTABILITY", attempt
    if raw_sha != proof_after:
        return "PROOF_HASH_INSTABILITY", attempt

    if not gzip_slots.acquire():
        return "STOPPED", attempt
    try:
        compression = gzip_and_verify(proof, proof_gz, raw_sha)
    finally:
        gzip_slots.release()
    attempt.update(compression)
    attempt["proof_gz"] = str(proof_gz)
    attempt["compression_ratio"] = compression["gzip_bytes"] / raw_bytes if raw_bytes else None
    proof.unlink()
    fsync_dir(proof.parent)
    attempt["ended_at"] = time.time()
    attempt["total_wall"] = attempt["ended_at"] - attempt["started_at"]
    return "CERTIFIED", attempt


def terminal_update(state, collection, key, result, attempt, failure=None):
    with lock:
        rec = collection[key]
        rec["attempts"].append(attempt)
        rec["state"] = result
        rec["failure"] = failure
        mark_dirty()
        save_state(state, terminal=True)


def modular_worker(key, state):
    rec = state["modular_jobs"][key]
    if stop_event.is_set():
        return
    if rec["kind"] == "LEAF":
        race = state["race_jobs"].get(rec["root"])
        if race and race["state"] == "CERTIFIED":
            with lock:
                rec["state"] = "SKIPPED_SUPERSEDED"
                rec["failure"] = None
                mark_dirty()
                save_state(state, terminal=True)
            return
    with lock:
        if rec["state"] != "PENDING":
            return
        rec["state"] = "RUNNING"
        mark_dirty()
    try:
        result, attempt = certify_pipeline(key, rec, "MODULAR", state, MODULAR_SOLVER_TIMEOUT)
        if result == "CERTIFIED":
            terminal_update(state, state["modular_jobs"], key, "CERTIFIED", attempt)
        elif result == "SAT_VERIFIED":
            terminal_update(state, state["modular_jobs"], key, "SAT_VERIFIED", attempt, "UNEXPECTED_SAT")
            request_stop(f"SAT_VERIFIED_{key}")
        elif result in ("LRAT_TIMEOUT", "CAKE_TIMEOUT") or result.startswith("LRAT_EXIT_") or result.startswith("CAKE_EXIT_") or result.endswith("HASH_INSTABILITY"):
            terminal_update(state, state["modular_jobs"], key, "ERROR", attempt, result)
            request_stop(f"CHECKER_OR_HASH_FAILURE_{key}_{result}")
        elif result == "STOPPED":
            with lock:
                rec["state"] = "PENDING"
                rec["failure"] = "STOPPED_RESUMABLE"
                mark_dirty()
                save_state(state, terminal=True)
        else:
            terminal_update(state, state["modular_jobs"], key, "ERROR" if result != "TIMEOUT" else "TIMEOUT", attempt, result)
            if STOP_ON_GENERIC_JOB_ERROR and result != "TIMEOUT":
                request_stop(f"JOB_ERROR_{key}_{result}")
    except Exception as exc:
        attempt = {"started_at": time.time(), "ended_at": time.time(), "exception": f"{type(exc).__name__}: {exc}"}
        terminal_update(state, state["modular_jobs"], key, "ERROR", attempt, attempt["exception"])
        if STOP_ON_GENERIC_JOB_ERROR:
            request_stop(f"EXCEPTION_{key}")


def hard_race_worker(root, state):
    rec = state["race_jobs"][root]
    if stop_event.is_set() or aux_stop_event.is_set():
        return
    with lock:
        if rec["state"] != "PENDING":
            return
        rec["state"] = "RUNNING"
        mark_dirty()
    try:
        result, attempt = certify_pipeline(root, rec, "HARD_RACE", state, HARD_ROOT_TIMEOUT, HARD_ROOT_PROOF_CAP_GIB)
        if result == "CERTIFIED":
            terminal_update(state, state["race_jobs"], root, "CERTIFIED", attempt)
            with lock:
                for key, leaf in state["modular_jobs"].items():
                    if leaf["kind"] == "LEAF" and leaf["root"] == root and leaf["state"] == "PENDING":
                        leaf["state"] = "SKIPPED_SUPERSEDED"
                mark_dirty()
                save_state(state, terminal=True)
        elif result == "SAT_VERIFIED":
            terminal_update(state, state["race_jobs"], root, "SAT_VERIFIED", attempt, "UNEXPECTED_SAT")
            request_stop(f"SAT_VERIFIED_HARD_ROOT_{root}")
        elif result in ("LRAT_TIMEOUT", "CAKE_TIMEOUT") or result.startswith("LRAT_EXIT_") or result.startswith("CAKE_EXIT_") or result.endswith("HASH_INSTABILITY"):
            terminal_update(state, state["race_jobs"], root, "ERROR", attempt, result)
            request_stop(f"CHECKER_OR_HASH_FAILURE_HARD_{root}_{result}")
        elif result == "STOPPED":
            with lock:
                rec["state"] = "PENDING"
                rec["failure"] = "STOPPED_RESUMABLE"
                mark_dirty()
                save_state(state, terminal=True)
        else:
            terminal_update(state, state["race_jobs"], root, "TIMEOUT" if result in ("TIMEOUT", "PROOF_CAP") else "ERROR", attempt, result)
    except Exception as exc:
        attempt = {"started_at": time.time(), "ended_at": time.time(), "exception": f"{type(exc).__name__}: {exc}"}
        terminal_update(state, state["race_jobs"], root, "ERROR", attempt, attempt["exception"])


def baseline_worker(state):
    rec = state["baseline_job"]
    if stop_event.is_set() or aux_stop_event.is_set():
        return
    with lock:
        if rec["state"] != "PENDING":
            return
        rec["state"] = "RUNNING"
        mark_dirty()
    pseudo = {
        "kind": "BASELINE",
        "root": None,
        "cnf": rec["cnf"],
        "cnf_sha256": rec["cnf_sha256"],
        "scout_conflicts": None,
    }
    try:
        result, attempt = certify_pipeline("BASELINE", pseudo, "BASELINE", state, BASELINE_TIMEOUT, BASELINE_PROOF_CAP_GIB)
        with lock:
            rec["attempts"].append(attempt)
            if result == "CERTIFIED":
                rec["state"] = "CERTIFIED"
                rec["failure"] = None
                baseline_success_event.set()
                state["stop_reason"] = "BASELINE_CERTIFIED_STRONGER_RESULT"
                mark_dirty()
                save_state(state, terminal=True)
                request_stop("BASELINE_CERTIFIED_STRONGER_RESULT")
            elif result == "SAT_VERIFIED":
                rec["state"] = "SAT_VERIFIED"
                rec["failure"] = "BASELINE_SAT_VERIFIED"
                mark_dirty()
                save_state(state, terminal=True)
                request_stop("BASELINE_SAT_VERIFIED")
            elif result == "STOPPED":
                rec["state"] = "PENDING"
                rec["failure"] = "STOPPED_RESUMABLE"
                mark_dirty()
                save_state(state, terminal=True)
            else:
                rec["state"] = "TIMEOUT" if result in ("TIMEOUT", "PROOF_CAP") else "ERROR"
                rec["failure"] = result
                mark_dirty()
                save_state(state, terminal=True)
    except Exception as exc:
        with lock:
            rec["attempts"].append({"started_at": time.time(), "ended_at": time.time(), "exception": f"{type(exc).__name__}: {exc}"})
            rec["state"] = "ERROR"
            rec["failure"] = f"{type(exc).__name__}: {exc}"
            mark_dirty()
            save_state(state, terminal=True)


def fit_linear(xs, ys):
    if len(xs) < 2 or len(xs) != len(ys):
        raise RuntimeError("insufficient calibration points")
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom <= 0:
        return my, 0.0
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    intercept = my - slope * mx
    return intercept, slope


def build_calibration_gate(state):
    rows = []
    for sent in state["calibration_sentinels"]:
        rec = state["modular_jobs"][sent["job_key"]]
        if rec["state"] != "CERTIFIED" or not rec["attempts"]:
            raise RuntimeError(f"sentinel not certified: {sent['job_key']} state={rec['state']}")
        a = rec["attempts"][-1]
        cake_rss = ((a.get("cake_lpr") or {}).get("time_v") or {}).get("max_rss_kib")
        solver_wall = (a.get("solver") or {}).get("wall")
        rows.append({
            "label": sent["label"],
            "job_key": sent["job_key"],
            "scout_conflicts": rec.get("scout_conflicts"),
            "scout_wall": rec.get("scout_wall"),
            "cert_solver_wall": solver_wall,
            "raw_proof_bytes": a.get("raw_proof_bytes"),
            "cake_rss_kib": cake_rss,
        })

    xs = [float(r["scout_conflicts"]) for r in rows]
    ys = [float(r["raw_proof_bytes"]) for r in rows]
    intercept, slope = fit_linear(xs, ys)

    solve_multipliers = []
    cake_xs = []
    cake_ys = []
    for r in rows:
        if r["cake_rss_kib"] and r["raw_proof_bytes"]:
            cake_xs.append(r["raw_proof_bytes"] / (1024 ** 3))
            cake_ys.append(r["cake_rss_kib"] / (1024 ** 2))
        if r["scout_wall"] and r["cert_solver_wall"] and r["scout_wall"] > 0:
            solve_multipliers.append(r["cert_solver_wall"] / r["scout_wall"])

    if len(cake_xs) < 2:
        raise RuntimeError("insufficient cake_lpr calibration points")
    cake_intercept, cake_slope = fit_linear(cake_xs, cake_ys)
    cake_intercept = max(0.0, cake_intercept)
    cake_slope = max(0.0, cake_slope)
    cake_base = [
        max(CAKE_MIN_ESTIMATE_GIB, cake_intercept + cake_slope * x)
        for x in cake_xs
    ]
    cake_envelope = max((y / p for y, p in zip(cake_ys, cake_base)), default=1.0)
    cake_safety = CAKE_MODEL_SAFETY * max(1.0, cake_envelope)
    cake_intercept *= cake_safety
    cake_slope *= cake_safety

    median_leaf_conf = statistics.median(
        r["scout_conflicts"] for r in state["modular_jobs"].values()
        if r["kind"] == "LEAF" and r.get("scout_conflicts") is not None
    )
    median_proof = max(64 * 1024 ** 2, intercept + slope * median_leaf_conf)
    median_cake = max(
        CAKE_MIN_ESTIMATE_GIB,
        cake_intercept + cake_slope * (median_proof / (1024 ** 3)),
    )
    total_gib = mem_total_gib()
    allows_two_median = (
        2 * median_cake <= CAKE_BUDGET_GIB
        and total_gib > 0
        and 2 * median_cake + MEM_AVAILABLE_FLOOR_GIB <= total_gib
    )

    model = {
        "proof_intercept_bytes": intercept,
        "proof_slope_bytes_per_conflict": slope,
        "cake_rss_intercept_gib": cake_intercept,
        "cake_rss_gib_per_proof_gib": cake_slope,
        "cake_model_safety_factor": cake_safety,
        "mem_total_gib": total_gib,
        "solver_multiplier_median": statistics.median(solve_multipliers) if solve_multipliers else None,
        "solver_multiplier_min": min(solve_multipliers) if solve_multipliers else None,
        "solver_multiplier_max": max(solve_multipliers) if solve_multipliers else None,
        "median_leaf_conflicts": median_leaf_conf,
        "median_predicted_proof_bytes": median_proof,
        "median_predicted_cake_gib": median_cake,
    }
    gate = {
        "pass": bool(allows_two_median),
        "reason": "PASS" if allows_two_median else "RAM_MODEL_ALLOWS_FEWER_THAN_TWO_MEDIAN_CAKE_CHECKS",
        "created_at": time.time(),
        "samples": rows,
        "model": model,
    }
    return gate


def calibrate():
    stop_event.clear()
    state = read_json(STATE)
    reset_interrupted(state)

    if RUNNER_PID.exists():
        try:
            old_pid = int(RUNNER_PID.read_text().strip())
            os.kill(old_pid, 0)
        except (ValueError, ProcessLookupError):
            try:
                RUNNER_PID.unlink()
                fsync_dir(RUNNER_PID.parent)
            except FileNotFoundError:
                pass
        else:
            raise SystemExit(f"runner already active pid={old_pid}")

    if state["phase"] == "CALIBRATING":
        state["phase"] = "CALIBRATION_INCOMPLETE"
        state["stop_reason"] = "RESUME_STALE_CALIBRATION"
        save_state(state, terminal=True)

    if state["phase"] not in ("PREPARED", "CALIBRATION_INCOMPLETE", "CALIBRATION_REVIEW_REQUIRED", "CALIBRATION_COMPLETE"):
        raise SystemExit(f"calibrate not allowed from phase={state['phase']}")

    atomic_text_fsync(RUNNER_PID, str(os.getpid()) + "\n")
    try:
        state["phase"] = "CALIBRATING"
        state["stop_reason"] = None
        save_state(state, terminal=True)
        log("CALIBRATION_START serial=5")

        for sentinel in state["calibration_sentinels"]:
            if stop_event.is_set():
                break
            key = sentinel["job_key"]
            rec = state["modular_jobs"][key]
            if rec["state"] == "CERTIFIED":
                log(f"CALIBRATION_SKIP already_certified {sentinel['label']} {key}")
                continue
            if rec["state"] not in ("PENDING", "ERROR", "TIMEOUT"):
                raise RuntimeError(f"bad sentinel state {key} {rec['state']}")
            rec["state"] = "PENDING"
            rec["failure"] = None
            modular_worker(key, state)
            log(f"CALIBRATION_SENTINEL {sentinel['label']} {key} state={rec['state']}")
            if rec["state"] != "CERTIFIED":
                state["phase"] = "CALIBRATION_INCOMPLETE"
                state["stop_reason"] = f"SENTINEL_{key}_{rec['state']}"
                save_state(state, terminal=True)
                return

        if stop_event.is_set():
            state["phase"] = "CALIBRATION_INCOMPLETE"
            state["stop_reason"] = global_stop_reason or "CALIBRATION_STOPPED"
            save_state(state, terminal=True)
            return

        gate = build_calibration_gate(state)
        state["calibration_gate"] = gate
        state["phase"] = "CALIBRATION_COMPLETE" if gate["pass"] else "CALIBRATION_REVIEW_REQUIRED"
        state["stop_reason"] = None if gate["pass"] else gate["reason"]
        atomic_json_fsync(CALIBRATION, gate)
        save_state(state, terminal=True)
        log(
            f"CALIBRATION_DONE pass={gate['pass']} median_proof={gate['model']['median_predicted_proof_bytes']/(1024**2):.1f}MiB "
            f"median_cake={gate['model']['median_predicted_cake_gib']:.1f}GiB "
            f"cake_intercept={gate['model']['cake_rss_intercept_gib']:.2f}GiB "
            f"cake_slope={gate['model']['cake_rss_gib_per_proof_gib']:.3f}GiB/GiB"
        )
    finally:
        try:
            if RUNNER_PID.exists() and RUNNER_PID.read_text().strip() == str(os.getpid()):
                RUNNER_PID.unlink()
                fsync_dir(RUNNER_PID.parent)
        except FileNotFoundError:
            pass


def hard_root_covered(state, root):
    if state["race_jobs"][root]["state"] == "CERTIFIED":
        return True
    leaves = [r for r in state["modular_jobs"].values() if r["kind"] == "LEAF" and r["root"] == root]
    return bool(leaves) and all(r["state"] == "CERTIFIED" for r in leaves)


def lemma_coverage_complete(state):
    direct_ok = all(r["state"] == "CERTIFIED" for r in state["modular_jobs"].values() if r["kind"] == "ROOT")
    hard_ok = all(hard_root_covered(state, root) for root in state["race_jobs"])
    return direct_ok and hard_ok


def write_final_manifest(state):
    certificates = {}
    for key, rec in sorted(state["modular_jobs"].items()):
        if rec["state"] != "CERTIFIED" or not rec["attempts"]:
            continue
        a = rec["attempts"][-1]
        certificates[key] = {
            "lane": "MODULAR",
            "kind": rec["kind"],
            "root": rec["root"],
            "frontier_key": rec.get("frontier_key"),
            "cnf": rec["cnf"],
            "cnf_sha256": rec["cnf_sha256"],
            "raw_proof_sha256": a["raw_proof_sha256"],
            "raw_proof_bytes": a["raw_proof_bytes"],
            "proof_gz": a["proof_gz"],
            "gzip_sha256": a["gzip_sha256"],
            "gzip_bytes": a["gzip_bytes"],
            "lrat_exit": a["lrat_check"]["exitcode"],
            "cake_exit": a["cake_lpr"]["exitcode"],
        }
    hard_certificates = {}
    for root, rec in sorted(state["race_jobs"].items()):
        if rec["state"] != "CERTIFIED" or not rec["attempts"]:
            continue
        a = rec["attempts"][-1]
        hard_certificates[root] = {
            "lane": "HARD_RACE",
            "root": root,
            "cnf": rec["cnf"],
            "cnf_sha256": rec["cnf_sha256"],
            "raw_proof_sha256": a["raw_proof_sha256"],
            "raw_proof_bytes": a["raw_proof_bytes"],
            "proof_gz": a["proof_gz"],
            "gzip_sha256": a["gzip_sha256"],
            "gzip_bytes": a["gzip_bytes"],
            "lrat_exit": a["lrat_check"]["exitcode"],
            "cake_exit": a["cake_lpr"]["exitcode"],
        }
    baseline = None
    if state["baseline_job"]["state"] == "CERTIFIED" and state["baseline_job"]["attempts"]:
        a = state["baseline_job"]["attempts"][-1]
        baseline = {
            "cnf": state["baseline_job"]["cnf"],
            "cnf_sha256": state["baseline_job"]["cnf_sha256"],
            "raw_proof_sha256": a["raw_proof_sha256"],
            "proof_gz": a["proof_gz"],
            "gzip_sha256": a["gzip_sha256"],
            "lrat_exit": a["lrat_check"]["exitcode"],
            "cake_exit": a["cake_lpr"]["exitcode"],
        }
    manifest = {
        "format": "O3-QSAT-TASK03-FULLCERT-MANIFEST-1.1",
        "created_at": time.time(),
        "phase": state["phase"],
        "stage1_claim": "source_task03_triangle_eo.cnf is UNSAT",
        "stage2_claim_label": "machine-verified modulo documented Lemma-B transfer",
        "source_cnf": state["source_cnf"],
        "source_cnf_sha256": state["source_cnf_sha256"],
        "rescout_state_sha256": state["rescout_state_sha256"],
        "frontier_state_sha256": state["frontier_state_sha256"],
        "core_sha256": state["core_sha256"],
        "coverage_input": str(COVERAGE_INPUT),
        "coverage_input_sha256": sha256_file(COVERAGE_INPUT),
        "toolchain": read_json(TOOLCHAIN),
        "calibration": state.get("calibration_gate"),
        "lemma_coverage_complete": lemma_coverage_complete(state),
        "baseline_certified": baseline is not None,
        "modular_certificates": certificates,
        "hard_root_certificates": hard_certificates,
        "baseline_certificate": baseline,
        "scope": {
            "symmetry_case": "type (6,3^7) at tau=6",
            "full_fpf_exclusion_requires_remaining_types": True,
            "tau6_focus_condition": "documented a1=18 conditionality; later tau in {13,20,27}",
            "no_claim_about_asymmetric_graphs_or_total_existence": True,
        },
    }
    atomic_json_fsync(MANIFEST, manifest)
    return manifest


def run_coverage_checker():
    if not COVERAGE_CHECKER.exists():
        return {"exitcode": None, "error": "checker_missing"}
    with COVERAGE_CHECK_LOG.open("wb") as out, COVERAGE_CHECK_ERR.open("wb") as err:
        p = subprocess.run(
            [sys.executable, str(COVERAGE_CHECKER), "--manifest", str(MANIFEST)],
            stdout=out,
            stderr=err,
        )
    return {
        "exitcode": p.returncode,
        "stdout_sha256": sha256_file(COVERAGE_CHECK_LOG),
        "stderr_sha256": sha256_file(COVERAGE_CHECK_ERR),
    }


def ticker(state, done_event):
    while not done_event.wait(STATE_TICK):
        try:
            mark_dirty()
            save_state(state, terminal=False)
        except Exception as exc:
            log(f"TICKER_ERROR {type(exc).__name__}: {exc}")


def run_full():
    state = read_json(STATE)
    reset_interrupted(state)
    gate = state.get("calibration_gate")
    if state["phase"] not in ("CALIBRATION_COMPLETE", "STOPPED_RESUMABLE", "PARTIAL"):
        raise SystemExit(f"run requires CALIBRATION_COMPLETE/STOPPED_RESUMABLE/PARTIAL, got {state['phase']}")
    if not gate or not gate.get("pass"):
        raise SystemExit("calibration gate not passed; do not run full hybrid")

    stop_event.clear()
    baseline_success_event.clear()
    aux_stop_event.clear()
    state["phase"] = "RUNNING"
    state["started_at"] = state.get("started_at") or time.time()
    state["ended_at"] = None
    state["stop_reason"] = None
    atomic_text_fsync(RUNNER_PID, str(os.getpid()) + "\n")
    save_state(state, terminal=True)

    modular_pending = [
        k for k, r in state["modular_jobs"].items()
        if r["state"] in ("PENDING", "TIMEOUT", "ERROR")
    ]
    for k in modular_pending:
        if state["modular_jobs"][k]["state"] != "PENDING":
            state["modular_jobs"][k]["state"] = "PENDING"
    modular_pending.sort(
        key=lambda k: (
            0 if state["modular_jobs"][k]["kind"] == "ROOT" else 1,
            -(state["modular_jobs"][k].get("scout_conflicts") or 0),
        )
    )
    race_pending = [r for r, rec in state["race_jobs"].items() if rec["state"] in ("PENDING", "TIMEOUT", "ERROR")]
    for r in race_pending:
        state["race_jobs"][r]["state"] = "PENDING"
    race_pending.sort(key=lambda r: state["race_jobs"][r].get("leaf_conflict_sum", 0))
    if state["baseline_job"]["state"] in ("TIMEOUT", "ERROR"):
        state["baseline_job"]["state"] = "PENDING"

    done_event = threading.Event()
    tick = threading.Thread(target=ticker, args=(state, done_event), daemon=True)
    tick.start()

    log(
        f"FULL_RUN_START modular_pending={len(modular_pending)} race_pending={len(race_pending)} "
        f"baseline={state['baseline_job']['state']} free={disk_free_gib():.1f}GiB mem={mem_available_gib():.1f}GiB"
    )

    # Separate orchestration executors keep all three lanes live. OS-process
    # concurrency is still globally bounded to 12 by cpu_slots.
    futures = []
    try:
        with ThreadPoolExecutor(max_workers=12) as modular_ex, \
             ThreadPoolExecutor(max_workers=2) as race_ex, \
             ThreadPoolExecutor(max_workers=1) as baseline_ex:
            for key in modular_pending:
                futures.append(modular_ex.submit(modular_worker, key, state))
            for root in race_pending:
                futures.append(race_ex.submit(hard_race_worker, root, state))
            if state["baseline_job"]["state"] == "PENDING":
                futures.append(baseline_ex.submit(baseline_worker, state))

            races_left = len(race_pending)
            baseline_left = state["baseline_job"]["state"] == "PENDING"
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    log(f"FUTURE_EXCEPTION {type(exc).__name__}: {exc}")
                races_now = sum(rec["state"] in ("PENDING", "RUNNING") for rec in state["race_jobs"].values())
                if races_left and races_now == 0:
                    races_left = 0
                    modular_solver_slots.set_limit(10 if baseline_left else 11)
                    log(f"REALLOCATE hard-race finished modular_solver_limit={modular_solver_slots.snapshot()['limit']}")
                baseline_now = state["baseline_job"]["state"] in ("PENDING", "RUNNING")
                if baseline_left and not baseline_now:
                    baseline_left = False
                    modular_solver_slots.set_limit(10 if races_left else 11)
                    log(f"REALLOCATE baseline lane finished modular_solver_limit={modular_solver_slots.snapshot()['limit']}")
                if lemma_coverage_complete(state) and not aux_stop_event.is_set():
                    aux_stop_event.set()
                    modular_solver_slots.set_limit(12)
                    log("AUX_CANCEL lemma coverage complete; stopping remaining hard-root races and baseline lottery")
                if stop_event.is_set():
                    break
    finally:
        done_event.set()
        tick.join(timeout=5)
        state["ended_at"] = time.time()
        if state["baseline_job"]["state"] == "CERTIFIED":
            state["phase"] = "BASELINE_CERTIFIED"
        elif any(r["state"] == "SAT_VERIFIED" for r in state["modular_jobs"].values()) or any(r["state"] == "SAT_VERIFIED" for r in state["race_jobs"].values()) or state["baseline_job"]["state"] == "SAT_VERIFIED":
            state["phase"] = "SAT_VERIFIED"
        elif lemma_coverage_complete(state):
            state["phase"] = "LEMMA_CNF_CERTIFIED"
        elif stop_event.is_set():
            state["phase"] = "STOPPED_RESUMABLE"
            if not state.get("stop_reason") and global_stop_reason:
                state["stop_reason"] = global_stop_reason
        else:
            state["phase"] = "PARTIAL"
        save_state(state, terminal=True)
        manifest = write_final_manifest(state)
        if manifest["lemma_coverage_complete"] or manifest["baseline_certified"]:
            check = run_coverage_checker()
            state["coverage_checker"] = check
            if check.get("exitcode") != 0 and not manifest["baseline_certified"]:
                state["phase"] = "CERTIFIED_NEEDS_COVERAGE_REVIEW"
                state["stop_reason"] = "COVERAGE_CHECKER_FAILED"
            save_state(state, terminal=True)
            write_final_manifest(state)
        try:
            RUNNER_PID.unlink()
            fsync_dir(RUNNER_PID.parent)
        except FileNotFoundError:
            pass
        log(f"FULL_RUN_DONE phase={state['phase']} lemma_coverage={lemma_coverage_complete(state)} baseline={state['baseline_job']['state']}")




def salvage_existing_raw_proofs():
    """Certify already-existing raw modular LRAT proofs without rerunning CaDiCaL.

    This command is intentionally separate from run-a-only.  It is only allowed
    while no runner is active and the campaign is stopped/partial.  Every raw
    proof is treated as untrusted input: the CNF hash is rechecked; lrat-check
    and cake_lpr are rerun; CNF/proof hashes are checked before/after; gzip is
    round-trip verified; only then is a fresh synthetic attempt appended and
    the job marked CERTIFIED.  Failed/non-proof raw files are left untouched so
    that the caller can inspect them before a later cleanup/resume.
    """
    global global_stop_reason
    if RUNNER_PID.exists():
        try:
            pid = int(RUNNER_PID.read_text().strip())
            os.kill(pid, 0)
        except (ValueError, ProcessLookupError):
            pass
        else:
            raise SystemExit(f"runner already active pid={pid}")

    stop_event.clear()
    global_stop_reason = None
    state = read_json(STATE)
    reset_interrupted(state)
    if state["phase"] not in ("CALIBRATION_COMPLETE", "STOPPED_RESUMABLE", "PARTIAL"):
        raise SystemExit(f"salvage-existing not allowed from phase={state['phase']}")

    candidates = []
    for key, rec in sorted(state["modular_jobs"].items()):
        if rec["state"] == "CERTIFIED":
            continue
        proof = proof_dir_for(key, rec, "MODULAR") / "proof.lrat"
        if proof.exists() and proof.stat().st_size > 0:
            candidates.append((key, rec, proof))

    report = {
        "schema": "conway99-task03-fullcert-1.1-salvage-existing-v1",
        "created_at": time.time(),
        "runtime_cake_reservation_cap_gib": CAKE_RUNTIME_RESERVATION_CAP_GIB,
        "candidates": [],
    }
    log(f"SALVAGE_START candidates={len(candidates)} free={disk_free_gib():.1f}GiB mem={mem_available_gib():.1f}GiB")

    for ordinal, (key, rec, proof) in enumerate(candidates, 1):
        outdir = proof.parent
        cnf = Path(rec["cnf"])
        proof_gz = outdir / "proof.lrat.gz"
        lrat_out = outdir / "salvage_lrat_check.out"
        lrat_err = outdir / "salvage_lrat_check.err"
        lrat_time = outdir / "salvage_lrat_check.time"
        cake_out = outdir / "salvage_cake_lpr.out"
        cake_err = outdir / "salvage_cake_lpr.err"
        cake_time = outdir / "salvage_cake_lpr.time"
        started = time.time()
        item = {"key": key, "proof": str(proof), "started_at": started}
        report["candidates"].append(item)
        try:
            cnf_sha_before = sha256_file(cnf)
            if cnf_sha_before != rec["cnf_sha256"]:
                item.update({"result": "CNF_HASH_MISMATCH", "cnf_sha256": cnf_sha_before})
                log(f"SALVAGE_REJECT {ordinal}/{len(candidates)} key={key} reason=CNF_HASH_MISMATCH")
                continue
            raw_sha = sha256_file(proof)
            raw_bytes = proof.stat().st_size
            item.update({"raw_proof_sha256": raw_sha, "raw_proof_bytes": raw_bytes})
            log(f"SALVAGE_CHECK {ordinal}/{len(candidates)} key={key} raw={raw_bytes/(1024**3):.2f}GiB")

            lrat = run_process(
                ["lrat-check", str(cnf), str(proof)],
                lrat_out, lrat_err, LRAT_CHECK_TIMEOUT,
                timefile=lrat_time, projected_extra_gib=0.0,
                global_disk_stop=False,
            )
            item["lrat_exit"] = lrat.get("exitcode")
            item["lrat_time_v"] = lrat.get("time_v")
            if lrat.get("timed_out") or lrat.get("stopped") or lrat.get("exitcode") != 0:
                item["result"] = "LRAT_REJECT"
                log(f"SALVAGE_REJECT {ordinal}/{len(candidates)} key={key} reason=LRAT exit={lrat.get('exitcode')}")
                continue

            if mem_available_gib() < MEM_AVAILABLE_FLOOR_GIB + CAKE_RUNTIME_RESERVATION_CAP_GIB:
                item["result"] = "CAKE_MEMORY_NOT_AVAILABLE"
                log(f"SALVAGE_STOP key={key} reason=CAKE_MEMORY_NOT_AVAILABLE mem={mem_available_gib():.1f}GiB")
                break

            cake = run_process(
                [str(CAKE_LPR), str(cnf), str(proof)],
                cake_out, cake_err, CAKE_CHECK_TIMEOUT,
                timefile=cake_time, projected_extra_gib=0.0,
                global_disk_stop=False,
            )
            item["cake_exit"] = cake.get("exitcode")
            item["cake_time_v"] = cake.get("time_v")
            if cake.get("timed_out") or cake.get("stopped") or cake.get("exitcode") != 0:
                item["result"] = "CAKE_REJECT"
                log(f"SALVAGE_REJECT {ordinal}/{len(candidates)} key={key} reason=CAKE exit={cake.get('exitcode')}")
                continue

            cnf_sha_after = sha256_file(cnf)
            raw_sha_after = sha256_file(proof)
            if cnf_sha_after != rec["cnf_sha256"] or cnf_sha_after != cnf_sha_before:
                item["result"] = "CNF_HASH_INSTABILITY"
                log(f"SALVAGE_REJECT {ordinal}/{len(candidates)} key={key} reason=CNF_HASH_INSTABILITY")
                continue
            if raw_sha_after != raw_sha:
                item["result"] = "PROOF_HASH_INSTABILITY"
                log(f"SALVAGE_REJECT {ordinal}/{len(candidates)} key={key} reason=PROOF_HASH_INSTABILITY")
                continue

            compression = gzip_and_verify(proof, proof_gz, raw_sha)
            attempt = {
                "started_at": started,
                "ended_at": time.time(),
                "lane": "MODULAR",
                "salvage_existing_raw": True,
                "salvage_prior_attempt_count": len(rec.get("attempts", [])),
                "solver": {
                    "reused_existing_raw_proof": True,
                    "exitcode": None,
                    "note": "Raw proof salvaged independently of interrupted solver metadata; proof validity established by both checkers.",
                },
                "raw_proof_sha256": raw_sha,
                "raw_proof_bytes": raw_bytes,
                "cnf_sha256_before_checks": cnf_sha_before,
                "cnf_sha256_after_checks": cnf_sha_after,
                "raw_proof_sha256_after_checks": raw_sha_after,
                "lrat_check": lrat,
                "cake_lpr": cake,
                **compression,
                "proof_gz": str(proof_gz),
                "compression_ratio": compression["gzip_bytes"] / raw_bytes if raw_bytes else None,
            }
            attempt["total_wall"] = attempt["ended_at"] - attempt["started_at"]
            proof.unlink()
            fsync_dir(proof.parent)
            terminal_update(state, state["modular_jobs"], key, "CERTIFIED", attempt)
            item.update({
                "result": "CERTIFIED",
                "gzip_sha256": compression["gzip_sha256"],
                "gzip_bytes": compression["gzip_bytes"],
                "ended_at": attempt["ended_at"],
            })
            log(
                f"SALVAGE_CERTIFIED {ordinal}/{len(candidates)} key={key} "
                f"raw={raw_bytes/(1024**3):.2f}GiB gz={compression['gzip_bytes']/(1024**3):.2f}GiB "
                f"cake_rss={((cake.get('time_v') or {}).get('max_rss_kib') or 0)/1024**2:.2f}GiB"
            )
        except Exception as exc:
            item.update({"result": "EXCEPTION", "exception": f"{type(exc).__name__}: {exc}"})
            log(f"SALVAGE_EXCEPTION key={key} {type(exc).__name__}: {exc}")
        finally:
            atomic_json_fsync(RUN_DIR / "salvage_existing_report.json", report)

    report["ended_at"] = time.time()
    report["summary"] = dict(Counter(x.get("result", "UNKNOWN") for x in report["candidates"]))
    atomic_json_fsync(RUN_DIR / "salvage_existing_report.json", report)
    state = read_json(STATE)
    save_state(state, terminal=True)
    log(f"SALVAGE_DONE summary={report['summary']} free={disk_free_gib():.1f}GiB")


def cleanup_incomplete_raw_proofs_aonly(state):
    """Remove only raw LRAT files from non-certified jobs before A-only resume.

    Certified gzip artifacts and all metadata are preserved.  These raw files
    are incomplete products of interrupted/failed attempts and would otherwise
    consume disk indefinitely, especially in the frozen auxiliary lanes.
    """
    removed = 0
    removed_bytes = 0
    paths = []
    for key, rec in state["modular_jobs"].items():
        if rec["state"] != "CERTIFIED":
            paths.append(proof_dir_for(key, rec, "MODULAR") / "proof.lrat")
    for root, rec in state["race_jobs"].items():
        if rec["state"] != "CERTIFIED":
            paths.append(proof_dir_for(root, rec, "HARD_RACE") / "proof.lrat")
    if state["baseline_job"]["state"] != "CERTIFIED":
        paths.append(BASELINE_DIR / "proof.lrat")
    touched = set()
    for p in paths:
        try:
            size = p.stat().st_size
        except FileNotFoundError:
            continue
        p.unlink()
        removed += 1
        removed_bytes += size
        touched.add(p.parent)
    for parent in touched:
        fsync_dir(parent)
    return removed, removed_bytes


def run_a_only(include_superseded=False):
    """Resume Stage-1 certification with all 12 solver slots assigned to A.

    HARD_RACE and BASELINE are frozen exactly as found in state.json.  Existing
    certified hard-root results remain usable for coverage; unfinished auxiliary
    work is neither reset to PENDING nor submitted.  Hard roots not already
    certified are completed solely through their modular leaf certificates.
    """
    state = read_json(STATE)
    reset_interrupted(state)
    gate = state.get("calibration_gate")
    if state["phase"] not in ("CALIBRATION_COMPLETE", "STOPPED_RESUMABLE", "PARTIAL"):
        raise SystemExit(f"run-a-only requires CALIBRATION_COMPLETE/STOPPED_RESUMABLE/PARTIAL, got {state['phase']}")
    if not gate or not gate.get("pass"):
        raise SystemExit("calibration gate not passed; do not run A-only resume")

    stop_event.clear()
    baseline_success_event.clear()
    aux_stop_event.set()
    a_solver_slots = PURE_A_SOLVER_SLOTS if include_superseded else PHYSICAL_CORES
    modular_solver_slots.set_limit(a_solver_slots)

    removed_count, removed_bytes = cleanup_incomplete_raw_proofs_aonly(state)

    state["phase"] = "RUNNING"
    state["started_at"] = state.get("started_at") or time.time()
    state["ended_at"] = None
    state["stop_reason"] = None
    atomic_text_fsync(RUNNER_PID, str(os.getpid()) + "\n")
    save_state(state, terminal=True)

    eligible_states = ("PENDING", "TIMEOUT", "ERROR", "SKIPPED_SUPERSEDED") if include_superseded else ("PENDING", "TIMEOUT", "ERROR")
    modular_pending = [
        k for k, r in state["modular_jobs"].items()
        if r["state"] in eligible_states
    ]
    for k in modular_pending:
        if state["modular_jobs"][k]["state"] != "PENDING":
            state["modular_jobs"][k]["state"] = "PENDING"
    modular_pending.sort(
        key=lambda k: (
            0 if state["modular_jobs"][k]["kind"] == "ROOT" else 1,
            -(state["modular_jobs"][k].get("scout_conflicts") or 0),
        )
    )
    save_state(state, terminal=True)

    frozen_race = Counter(rec["state"] for rec in state["race_jobs"].values())
    frozen_baseline = state["baseline_job"]["state"]

    done_event = threading.Event()
    tick = threading.Thread(target=ticker, args=(state, done_event), daemon=True)
    tick.start()

    log(
        f"{'A_ONLY_PURE_RUN_START' if include_superseded else 'A_ONLY_RUN_START'} modular_pending={len(modular_pending)} "
        f"race_frozen={dict(sorted(frozen_race.items()))} baseline_frozen={frozen_baseline} "
        f"solver_slots={a_solver_slots} raw_reclaimed={removed_bytes / (1024 ** 3):.1f}GiB files={removed_count} "
        f"free={disk_free_gib():.1f}GiB mem={mem_available_gib():.1f}GiB"
    )

    futures = []
    try:
        with ThreadPoolExecutor(max_workers=a_solver_slots) as modular_ex:
            for key in modular_pending:
                futures.append(modular_ex.submit(modular_worker, key, state))
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    log(f"FUTURE_EXCEPTION {type(exc).__name__}: {exc}")
                if stop_event.is_set():
                    break
    finally:
        done_event.set()
        tick.join(timeout=5)
        state["ended_at"] = time.time()
        if state["baseline_job"]["state"] == "CERTIFIED":
            state["phase"] = "BASELINE_CERTIFIED"
        elif any(r["state"] == "SAT_VERIFIED" for r in state["modular_jobs"].values()) or any(r["state"] == "SAT_VERIFIED" for r in state["race_jobs"].values()) or state["baseline_job"]["state"] == "SAT_VERIFIED":
            state["phase"] = "SAT_VERIFIED"
        elif lemma_coverage_complete(state):
            state["phase"] = "LEMMA_CNF_CERTIFIED"
        elif stop_event.is_set():
            state["phase"] = "STOPPED_RESUMABLE"
            if not state.get("stop_reason") and global_stop_reason:
                state["stop_reason"] = global_stop_reason
        else:
            state["phase"] = "PARTIAL"
        save_state(state, terminal=True)
        manifest = write_final_manifest(state)
        if manifest["lemma_coverage_complete"] or manifest["baseline_certified"]:
            check = run_coverage_checker()
            state["coverage_checker"] = check
            if check.get("exitcode") != 0 and not manifest["baseline_certified"]:
                state["phase"] = "CERTIFIED_NEEDS_COVERAGE_REVIEW"
                state["stop_reason"] = "COVERAGE_CHECKER_FAILED"
            save_state(state, terminal=True)
            write_final_manifest(state)
        try:
            RUNNER_PID.unlink()
            fsync_dir(RUNNER_PID.parent)
        except FileNotFoundError:
            pass
        log(
            f"{'A_ONLY_PURE_RUN_DONE' if include_superseded else 'A_ONLY_RUN_DONE'} phase={state['phase']} "
            f"lemma_coverage={lemma_coverage_complete(state)} "
            f"race_frozen={dict(sorted(Counter(rec['state'] for rec in state['race_jobs'].values()).items()))} "
            f"baseline={state['baseline_job']['state']}"
        )

def status():
    if not STATE.exists():
        print("NO_STATE")
        return
    state = read_json(STATE)
    mod = Counter(r["state"] for r in state["modular_jobs"].values())
    race = Counter(r["state"] for r in state["race_jobs"].values())
    gate = state.get("calibration_gate") or {}
    pid = RUNNER_PID.read_text().strip() if RUNNER_PID.exists() else None
    print(
        "phase=%s gate=%s modular=%s race=%s baseline=%s coverage=%s free=%.2fGiB mem=%.2fGiB pid=%s" % (
            state["phase"],
            gate.get("pass"),
            dict(sorted(mod.items())),
            dict(sorted(race.items())),
            state["baseline_job"]["state"],
            lemma_coverage_complete(state),
            disk_free_gib(),
            mem_available_gib(),
            pid,
        )
    )
    if gate.get("model"):
        model = gate["model"]
        print(
            "calibration median_proof=%.1fMiB median_cake=%.1fGiB proof_slope=%.1fB/conf solver_mult=%s" % (
                model["median_predicted_proof_bytes"] / (1024 ** 2),
                model["median_predicted_cake_gib"],
                model["proof_slope_bytes_per_conflict"],
                "%.2f" % model["solver_multiplier_median"] if model.get("solver_multiplier_median") is not None else "NA",
            )
        )


def stop():
    if not RUNNER_PID.exists():
        print("NO_RUNNING_PID")
        return
    pid = int(RUNNER_PID.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"STOP_SIGNAL_SENT pid={pid}")
    except ProcessLookupError:
        print(f"PID_NOT_RUNNING pid={pid}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("prepare", "calibrate", "run", "run-a-only", "run-a-only-pure", "salvage-existing", "status", "stop"))
    args = ap.parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if args.command == "prepare":
        prepare()
    elif args.command == "calibrate":
        calibrate()
    elif args.command == "run":
        run_full()
    elif args.command == "run-a-only":
        run_a_only(False)
    elif args.command == "run-a-only-pure":
        run_a_only(True)
    elif args.command == "salvage-existing":
        salvage_existing_raw_proofs()
    elif args.command == "status":
        status()
    else:
        stop()


if __name__ == "__main__":
    main()
