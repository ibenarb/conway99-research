#!/usr/bin/env python3
"""Robust autonomous A/B/C scout runner for Conway_99 O3-BREADTH-1.

Design:
- 139 C4-free types, each solved A -> B -> C on one pinned physical core.
- Default 10 workers, 3600 s identical CaDiCaL limit per layer.
- Deterministically permuted type order.
- Crash-resumable per-type atomic JSON state.
- Temporary DIMACS: hash -> solve -> delete, except SAT/ERROR/anomaly freeze.
- 10-minute status reports with ETA, resources and solver counters when available.
- SAT is independently checked via Q^2 + Q = 12 I + 6 J and causes global stop.
- A/B/C soundness inconsistency causes hard stop.
- Disk/RAM floors pause new work; running jobs are not killed.
- No proof production: UNSAT is recorded as UNSAT_UNCERTIFIED.
"""
from __future__ import annotations

import argparse
import fcntl
import gc
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import traceback
from collections import Counter, defaultdict
from multiprocessing import Process
from pathlib import Path


LAYERS = ("A", "B", "C")
HARD_ABORT_REASONS = {"SAT_VERIFIED", "SAT_UNVERIFIED", "SOUNDNESS_VIOLATION"}
TERMINAL_OK = {"UNSAT_UNCERTIFIED", "TIMEOUT"}
HARD_STOP_STATUSES = {"SAT_VERIFIED", "SAT_UNVERIFIED", "SOUNDNESS_VIOLATION"}


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp.%d" % os.getpid())
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def load_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return default


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def job_id(tau, part):
    return "tau%02d_%s" % (tau, "-".join(map(str, part)))


def instance_seed(master_seed, tau, part, layer):
    raw = ("%d|%d|%s|%s" % (master_seed, tau, ",".join(map(str, part)), layer)).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:4], "big") & 0x7FFFFFFF


def write_dimacs(cnf, path):
    path = Path(path)
    with open(path, "w", newline="\n") as f:
        f.write("p cnf %d %d\n" % (cnf.n, len(cnf.cl)))
        for clause in cnf.cl:
            f.write(" ".join(map(str, clause)) + " 0\n")


def proc_status(pid):
    out = {"rss_kib": 0, "hwm_kib": 0, "cpu_seconds": 0.0}
    try:
        text = Path("/proc/%d/status" % pid).read_text()
        for line in text.splitlines():
            if line.startswith("VmRSS:"):
                out["rss_kib"] = int(line.split()[1])
            elif line.startswith("VmHWM:"):
                out["hwm_kib"] = int(line.split()[1])
        fields = Path("/proc/%d/stat" % pid).read_text().split()
        ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        out["cpu_seconds"] = (int(fields[13]) + int(fields[14])) / ticks
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
        pass
    return out


def mem_available_gib():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024.0 * 1024.0)
    except Exception:
        pass
    return math.nan


def disk_free_gib(path):
    u = shutil.disk_usage(path)
    return u.free / (1024.0 ** 3)


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True


def resource_pause_reason(cfg):
    reasons = []
    mem = mem_available_gib()
    disk = disk_free_gib(cfg["run_dir"])
    if mem < cfg["mem_floor_gib"]:
        reasons.append("MemAvailable %.2f < %.2f GiB" % (mem, cfg["mem_floor_gib"]))
    if disk < cfg["disk_floor_gib"]:
        reasons.append("disk %.2f < %.2f GiB" % (disk, cfg["disk_floor_gib"]))
    return "; ".join(reasons) if reasons else None


def wait_for_resources(cfg, run_dir, jid, tau, part, layer, cpu):
    while True:
        if stop_reason(run_dir):
            return False
        reason = resource_pause_reason(cfg)
        if not reason:
            return True
        update_marker(run_dir, jid, {
            "job_id": jid, "tau": tau, "cycle_type": list(part),
            "layer": layer, "phase": "PAUSED_RESOURCE", "cpu": cpu,
            "worker_pid": os.getpid(), "pause_reason": reason,
            "start_epoch": time.time(),
        })
        time.sleep(30.0)


def discover_physical_cpus():
    groups = defaultdict(list)
    for cpu_dir in sorted(Path("/sys/devices/system/cpu").glob("cpu[0-9]*")):
        cpu = int(cpu_dir.name[3:])
        try:
            core = (cpu_dir / "topology/core_id").read_text().strip()
            pkg = (cpu_dir / "topology/physical_package_id").read_text().strip()
            groups[(pkg, core)].append(cpu)
        except OSError:
            continue
    if groups:
        return [min(groups[key]) for key in sorted(groups, key=lambda x: (int(x[0]), int(x[1])))]
    n = os.cpu_count() or 1
    return list(range(0, n, 2)) or [0]


def parse_solver_stats(path):
    stats = {"conflicts": 0, "decisions": 0, "propagations": 0}
    try:
        lines = Path(path).read_text(errors="replace").splitlines()
    except OSError:
        return stats
    patterns = {
        key: re.compile(r"^c %s:\s*([0-9][0-9,]*)\b" % key, re.I)
        for key in stats
    }
    for line in lines:
        for key, pattern in patterns.items():
            match = pattern.match(line)
            if match:
                try:
                    stats[key] = int(match.group(1).replace(",", ""))
                except ValueError:
                    pass
    return stats


def parse_solver_result(path, returncode, wall, timeout):
    try:
        text = Path(path).read_text(errors="replace")
    except OSError:
        text = ""
    if re.search(r"^s\s+SATISFIABLE\b", text, flags=re.M):
        return "SAT"
    if re.search(r"^s\s+UNSATISFIABLE\b", text, flags=re.M):
        return "UNSAT_UNCERTIFIED"
    if returncode == 10:
        return "SAT"
    if returncode == 20:
        return "UNSAT_UNCERTIFIED"
    if wall >= max(1.0, timeout - 5.0):
        return "TIMEOUT"
    if re.search(r"\b(time|wall).*limit\b|\bUNKNOWN\b", text, flags=re.I):
        return "TIMEOUT"
    return "ERROR"


def parse_model(path):
    model = set()
    saw = False
    try:
        lines = Path(path).read_text(errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        if not line.startswith("v"):
            continue
        saw = True
        for token in line[1:].split():
            try:
                lit = int(token)
            except ValueError:
                continue
            if lit > 0:
                model.add(lit)
    return model if saw else None


def verify_sat(core, sv, positive_vars):
    if positive_vars is None:
        return False, {"error": "model missing"}
    n = core["n"]
    tset = set(core["T"])
    lset = {tuple(edge) for edge in core["L"]}
    q = [[0] * n for _ in range(n)]
    for i in tset:
        q[i][i] = 2
    for a, b in lset:
        q[a][b] = q[b][a] = 2
    selected = []
    for edge, var in sv.items():
        if var in positive_vars:
            a, b = edge
            q[a][b] = q[b][a] = 1
            selected.append([a, b])
    failures = []
    for i in range(n):
        for j in range(n):
            lhs = sum(q[i][k] * q[k][j] for k in range(n)) + q[i][j]
            rhs = 18 if i == j else 6
            if lhs != rhs:
                failures.append([i, j, lhs, rhs])
                if len(failures) >= 20:
                    break
        if len(failures) >= 20:
            break
    return not failures, {
        "selected_S_edges": selected,
        "Q": q,
        "failures": failures,
        "equation": "Q^2 + Q = 12 I + 6 J",
    }


def freeze_instance(run_dir, jid, layer, cnf_path, log_path, payload):
    dst = Path(run_dir) / "frozen" / ("%s_%s" % (jid, layer))
    dst.mkdir(parents=True, exist_ok=True)
    if Path(cnf_path).exists():
        os.replace(cnf_path, dst / "instance.cnf")
    if Path(log_path).exists():
        shutil.copy2(log_path, dst / "solver.log")
    atomic_json(dst / "result.json", payload)
    return str(dst)


def running_marker_path(run_dir, jid):
    return Path(run_dir) / "running" / ("%s.json" % jid)


def update_marker(run_dir, jid, data):
    data = dict(data)
    data["updated_at"] = now_iso()
    atomic_json(running_marker_path(run_dir, jid), data)


def stop_reason(run_dir):
    p = Path(run_dir) / "STOP.json"
    return load_json(p, None)


def set_stop(run_dir, reason, details=None):
    p = Path(run_dir) / "STOP.json"
    if p.exists():
        return
    atomic_json(p, {
        "reason": reason,
        "details": details or {},
        "time": now_iso(),
    })


def abort_other_solvers_for_hard_stop(run_dir, stop):
    """Terminate solver process groups other than the worker that raised the stop."""
    reason = (stop or {}).get("reason")
    if reason not in HARD_ABORT_REASONS:
        return []
    origin = ((stop or {}).get("details") or {}).get("job_id")
    killed = []
    for p in (Path(run_dir) / "running").glob("*.json"):
        try:
            marker = json.loads(p.read_text())
        except Exception:
            continue
        if marker.get("job_id") == origin:
            continue
        pid = int(marker.get("solver_pid") or 0)
        if not pid:
            continue
        try:
            os.killpg(pid, signal.SIGTERM)
            killed.append({
                "job_id": marker.get("job_id"),
                "layer": marker.get("layer"),
                "solver_pid": pid,
            })
        except ProcessLookupError:
            pass
    if killed:
        atomic_json(
            Path(run_dir) / "recovery" / ("hard_abort_%d.json" % int(time.time())),
            {
                "time": now_iso(),
                "reason": reason,
                "origin_job_id": origin,
                "terminated": killed,
            },
        )
    return killed


def worker_run(cfg, tau, part, cpu):
    run_dir = Path(cfg["run_dir"])
    jid = job_id(tau, part)
    type_path = run_dir / "types" / ("%s.json" % jid)
    marker = running_marker_path(run_dir, jid)
    try:
        os.sched_setaffinity(0, {cpu})
    except (AttributeError, OSError):
        pass

    generic = load_module("generic_core_worker_%d" % os.getpid(), cfg["generic_core"])
    abc = load_module("abc_encode_worker_%d" % os.getpid(), cfg["abc_encode"])
    legacy = load_module("legacy_encode_worker_%d" % os.getpid(), cfg["legacy_encode"])
    core = generic.make_core(tau, tuple(part))
    state = load_json(type_path, {
        "job_id": jid,
        "tau": tau,
        "cycle_type": list(part),
        "instances": [],
        "complete": False,
        "created_at": now_iso(),
    })
    done_layers = {x["layer"] for x in state.get("instances", [])}

    try:
        for layer in LAYERS:
            if layer in done_layers:
                continue
            if stop_reason(run_dir):
                break
            if not wait_for_resources(cfg, run_dir, jid, tau, part, layer, cpu):
                break
            start = time.time()
            cnf_path = run_dir / "tmp" / ("%s_%s.cnf" % (jid, layer))
            log_path = run_dir / "logs" / ("%s_%s.log" % (jid, layer))
            cnf_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            update_marker(run_dir, jid, {
                "job_id": jid, "tau": tau, "cycle_type": list(part),
                "layer": layer, "phase": "ENCODING", "cpu": cpu,
                "worker_pid": os.getpid(), "start_epoch": start,
                "log_path": str(log_path), "cnf_path": str(cnf_path),
            })

            cnf, sv, meta = abc.build_cnf(core, legacy, layer)
            write_dimacs(cnf, cnf_path)
            cnf_sha = sha256_file(cnf_path)
            variables = cnf.n
            clauses = len(cnf.cl)
            del cnf
            gc.collect()

            if stop_reason(run_dir):
                try:
                    cnf_path.unlink()
                except FileNotFoundError:
                    pass
                break
            if not wait_for_resources(cfg, run_dir, jid, tau, part, layer, cpu):
                try:
                    cnf_path.unlink()
                except FileNotFoundError:
                    pass
                break

            seed = instance_seed(cfg["master_seed"], tau, part, layer)
            command = [
                cfg["solver"],
                "-t", str(cfg["timeout"]),
                "--seed=%d" % seed,
                "--stats",
                str(cnf_path),
            ]
            update_marker(run_dir, jid, {
                "job_id": jid, "tau": tau, "cycle_type": list(part),
                "layer": layer, "phase": "SOLVING", "cpu": cpu,
                "worker_pid": os.getpid(), "start_epoch": start,
                "log_path": str(log_path), "cnf_path": str(cnf_path),
                "cnf_sha256": cnf_sha, "variables": variables, "clauses": clauses,
                "command": command,
            })

            child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
            solve_start = time.time()
            with open(log_path, "w") as log:
                proc = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                update_marker(run_dir, jid, {
                    "job_id": jid, "tau": tau, "cycle_type": list(part),
                    "layer": layer, "phase": "SOLVING", "cpu": cpu,
                    "worker_pid": os.getpid(), "solver_pid": proc.pid,
                    "start_epoch": start, "solve_start_epoch": solve_start,
                    "log_path": str(log_path), "cnf_path": str(cnf_path),
                    "cnf_sha256": cnf_sha, "variables": variables, "clauses": clauses,
                    "command": command,
                })
                watchdog = cfg["timeout"] + cfg["watchdog_slack"]
                solver_peak_rss_kib = 0
                while proc.poll() is None and time.time() - solve_start < watchdog:
                    solver_peak_rss_kib = max(
                        solver_peak_rss_kib,
                        proc_status(proc.pid).get("hwm_kib", 0),
                    )
                    time.sleep(1.0)
                solver_peak_rss_kib = max(
                    solver_peak_rss_kib,
                    proc_status(proc.pid).get("hwm_kib", 0),
                )
                watchdog_hit = proc.poll() is None
                if watchdog_hit:
                    try:
                        os.killpg(proc.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        proc.wait()
                rc = proc.returncode

            solve_wall = time.time() - solve_start
            child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
            stats = parse_solver_stats(log_path)
            raw_status = "TIMEOUT" if watchdog_hit else parse_solver_result(
                log_path, rc, solve_wall, cfg["timeout"]
            )
            result = {
                "job_id": jid, "tau": tau, "cycle_type": list(part), "layer": layer,
                "status": raw_status, "started_at": time.strftime(
                    "%Y-%m-%dT%H:%M:%S%z", time.localtime(start)
                ),
                "finished_at": now_iso(), "wall_seconds": time.time() - start,
                "solve_wall_seconds": solve_wall, "returncode": rc,
                "cpu": cpu, "seed": seed, "cnf_sha256": cnf_sha,
                "variables": variables, "clauses": clauses,
                "conflicts": stats["conflicts"], "decisions": stats["decisions"],
                "propagations": stats["propagations"],
                "child_cpu_seconds": max(
                    0.0,
                    (child_after.ru_utime + child_after.ru_stime)
                    - (child_before.ru_utime + child_before.ru_stime),
                ),
                "solver_peak_rss_kib": solver_peak_rss_kib,
                "worker_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "child_peak_rss_kib": child_after.ru_maxrss,
                "encoder_meta": meta,
                "solver_log": str(log_path),
            }

            freeze = False
            if raw_status == "SAT":
                positive = parse_model(log_path)
                verified, verification = verify_sat(core, sv, positive)
                result["sat_verification"] = verification
                previous_unsat = [
                    x["layer"] for x in state.get("instances", [])
                    if x.get("status") == "UNSAT_UNCERTIFIED"
                ]
                if not verified:
                    result["status"] = "SAT_UNVERIFIED"
                    freeze = True
                    set_stop(run_dir, "SAT_UNVERIFIED", {
                        "job_id": jid, "layer": layer,
                    })
                elif previous_unsat:
                    result["status"] = "SOUNDNESS_VIOLATION"
                    result["previous_unsat_layers"] = previous_unsat
                    freeze = True
                    set_stop(run_dir, "SOUNDNESS_VIOLATION", {
                        "job_id": jid, "layer": layer,
                        "previous_unsat_layers": previous_unsat,
                    })
                else:
                    result["status"] = "SAT_VERIFIED"
                    freeze = True
                    set_stop(run_dir, "SAT_VERIFIED", {
                        "job_id": jid, "layer": layer,
                    })
            elif raw_status == "ERROR":
                freeze = True

            if freeze:
                result["frozen_dir"] = freeze_instance(
                    run_dir, jid, layer, cnf_path, log_path, result
                )
                atomic_json(Path(result["frozen_dir"]) / "result.json", result)
            else:
                try:
                    cnf_path.unlink()
                except FileNotFoundError:
                    pass

            state.setdefault("instances", []).append(result)
            state["updated_at"] = now_iso()
            state["complete"] = len({x["layer"] for x in state["instances"]}) == 3
            atomic_json(type_path, state)

            if (
                result["status"] in HARD_STOP_STATUSES
                or result["status"] == "ERROR"
                or stop_reason(run_dir)
            ):
                break

        state = load_json(type_path, state)
        state["complete"] = len({x["layer"] for x in state.get("instances", [])}) == 3
        state["updated_at"] = now_iso()
        atomic_json(type_path, state)
    except BaseException as exc:
        error = {
            "time": now_iso(),
            "job_id": jid,
            "tau": tau,
            "cycle_type": list(part),
            "error": repr(exc),
            "traceback": traceback.format_exc(),
        }
        atomic_json(run_dir / "errors" / ("%s.json" % jid), error)
        set_stop(run_dir, "WORKER_CRASH", error)
        raise
    finally:
        try:
            marker.unlink()
        except FileNotFoundError:
            pass


def build_types(generic):
    out = []
    for tau in (6, 13, 20, 27):
        for part in generic.all_types(tau):
            if 4 not in part:
                out.append((tau, tuple(part)))
    if len(out) != 139:
        raise RuntimeError("expected 139 types, got %d" % len(out))
    return out


def make_manifest(cfg, generic, cpus):
    types = build_types(generic)
    def order_key(item):
        tau, part = item
        raw = ("%d|%d|%s" % (
            cfg["master_seed"], tau, ",".join(map(str, part))
        )).encode()
        return hashlib.sha256(raw).digest()
    types = sorted(types, key=order_key)
    if cfg["max_types"] > 0:
        types = types[:cfg["max_types"]]
    manifest = {
        "schema": 1,
        "created_at": now_iso(),
        "master_seed": cfg["master_seed"],
        "timeout": cfg["timeout"],
        "workers": cfg["workers"],
        "report_seconds": cfg["report_seconds"],
        "disk_floor_gib": cfg["disk_floor_gib"],
        "mem_floor_gib": cfg["mem_floor_gib"],
        "reserve_physical_cores": cfg["reserve_cores"],
        "physical_cpu_representatives": cpus,
        "worker_cpus": cpus[:cfg["workers"]],
        "layers": list(LAYERS),
        "types": [
            {"ordinal": i, "tau": tau, "cycle_type": list(part), "job_id": job_id(tau, part)}
            for i, (tau, part) in enumerate(types)
        ],
        "instances": len(types) * 3,
        "paths": {
            "runner": cfg["runner"], "solver": cfg["solver"],
            "generic_core": cfg["generic_core"], "abc_encode": cfg["abc_encode"],
            "legacy_encode": cfg["legacy_encode"],
        },
        "sha256": {
            key: sha256_file(cfg[key])
            for key in ("runner", "solver", "generic_core", "abc_encode", "legacy_encode")
        },
    }
    return manifest


def load_type_states(run_dir):
    states = {}
    for p in (Path(run_dir) / "types").glob("*.json"):
        try:
            s = json.loads(p.read_text())
            states[s["job_id"]] = s
        except Exception:
            continue
    return states


def all_instance_results(states):
    return [x for s in states.values() for x in s.get("instances", [])]


def read_markers(run_dir):
    out = []
    for p in (Path(run_dir) / "running").glob("*.json"):
        try:
            out.append(json.loads(p.read_text()))
        except Exception:
            pass
    return out


def format_hms(seconds):
    if not math.isfinite(seconds):
        return "n/a"
    seconds = max(0, int(seconds))
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def report(run_dir, manifest, started_epoch, active_count, paused_reason=None):
    states = load_type_states(run_dir)
    results = all_instance_results(states)
    markers = read_markers(run_dir)
    total = manifest["instances"]
    done = len(results)
    running = len(markers)
    open_count = max(0, total - done - running)
    counts = Counter(x.get("status", "?") for x in results)
    by_layer_tau = defaultdict(Counter)
    for x in results:
        by_layer_tau[(x["layer"], x["tau"])][x["status"]] += 1

    conflicts = sum(int(x.get("conflicts", 0) or 0) for x in results)
    decisions = sum(int(x.get("decisions", 0) or 0) for x in results)
    propagations = sum(int(x.get("propagations", 0) or 0) for x in results)
    cpu_seconds = sum(float(x.get("child_cpu_seconds", 0.0) or 0.0) for x in results)
    peak_kib = max([
        max(
            int(x.get("solver_peak_rss_kib", 0) or 0),
            int(x.get("worker_peak_rss_kib", 0) or 0),
            int(x.get("child_peak_rss_kib", 0) or 0),
        )
        for x in results
    ] + [0])

    now = time.time()
    running_rows = []
    for m in markers:
        pid = int(m.get("solver_pid") or m.get("worker_pid") or 0)
        ps = proc_status(pid) if pid else {"cpu_seconds": 0, "hwm_kib": 0}
        cpu_seconds += ps["cpu_seconds"]
        peak_kib = max(peak_kib, ps["hwm_kib"])
        live = parse_solver_stats(m.get("log_path", ""))
        conflicts += live["conflicts"]
        decisions += live["decisions"]
        propagations += live["propagations"]
        running_rows.append((
            now - float(m.get("start_epoch", now)),
            "%s/%s/%s" % (m.get("job_id"), m.get("layer"), m.get("phase")),
        ))

    wall = now - started_epoch
    rate_h = done / wall * 3600.0 if wall > 0 else 0.0
    eta = (total - done) / rate_h * 3600.0 if rate_h > 0 else math.inf

    remaining_budget = 0.0
    result_keys = {(x["job_id"], x["layer"]) for x in results}
    marker_map = {(m.get("job_id"), m.get("layer")): m for m in markers}
    for item in manifest["types"]:
        jid = item["job_id"]
        for layer in LAYERS:
            if (jid, layer) in result_keys:
                continue
            m = marker_map.get((jid, layer))
            if m and m.get("phase") == "SOLVING":
                elapsed = now - float(m.get("solve_start_epoch", now))
                remaining_budget += max(0.0, manifest["timeout"] - elapsed)
            else:
                remaining_budget += manifest["timeout"]
    pess = remaining_budget / max(1, manifest["workers"])

    disk = disk_free_gib(run_dir)
    mem = mem_available_gib()
    stop = stop_reason(run_dir)
    phase = "STOPPED" if stop else ("PAUSED" if paused_reason else "RUNNING")
    if done == total and not stop:
        phase = "COMPLETE"

    last_error = None
    error_files = sorted((Path(run_dir) / "errors").glob("*.json"), key=lambda p: p.stat().st_mtime)
    if error_files:
        e = load_json(error_files[-1], {})
        last_error = "%s: %s" % (e.get("job_id", "?"), e.get("error", "?"))
    elif counts.get("ERROR"):
        errs = [x for x in results if x.get("status") == "ERROR"]
        if errs:
            last_error = "%s/%s rc=%s" % (
                errs[-1].get("job_id"), errs[-1].get("layer"), errs[-1].get("returncode")
            )

    lines = [
        "[%s] PHASE=%s done=%d running=%d open=%d active_types=%d" % (
            now_iso(), phase, done, running, open_count, active_count
        ),
        "STATUS %s" % dict(sorted(counts.items())),
    ]
    layer_bits = []
    for layer in LAYERS:
        for tau in (6, 13, 20, 27):
            c = by_layer_tau.get((layer, tau), {})
            if c:
                layer_bits.append("%s/tau%d=%s" % (layer, tau, dict(c)))
    lines.append("BY_LAYER_TAU " + (" | ".join(layer_bits) if layer_bits else "none"))
    lines.append(
        "SOLVER conflicts=%d decisions=%d propagations=%d cpu=%s campaign_wall=%s peak_rss=%.2fGiB" % (
            conflicts, decisions, propagations, format_hms(cpu_seconds),
            format_hms(wall), peak_kib / (1024.0 ** 2)
        )
    )
    lines.append(
        "RESOURCES mem_available=%.2fGiB disk_free=%.2fGiB rate=%.2f inst/h ETA=%s pessimistic=%s" % (
            mem, disk, rate_h, format_hms(eta), format_hms(pess)
        )
    )
    for elapsed, label in sorted(running_rows, reverse=True)[:3]:
        lines.append("LONG_RUNNING %s elapsed=%s" % (label, format_hms(elapsed)))
    lines.append("LAST_ERROR %s" % (last_error or "none"))
    if paused_reason:
        lines.append("PAUSE_REASON %s" % paused_reason)
    if stop:
        lines.append("STOP_REASON %s" % stop)
    print("\n" + "\n".join(lines), flush=True)
    with open(Path(run_dir) / "reports.log", "a") as report_log:
        report_log.write("\n".join(lines) + "\n\n")

    snapshot = {
        "time": now_iso(), "phase": phase, "done": done, "running": running,
        "open": open_count, "status_counts": dict(counts), "conflicts": conflicts,
        "decisions": decisions, "propagations": propagations,
        "solver_cpu_seconds": cpu_seconds, "campaign_wall_seconds": wall,
        "peak_rss_kib": peak_kib, "mem_available_gib": mem,
        "disk_free_gib": disk, "rate_instances_per_hour": rate_h,
        "eta_seconds": None if not math.isfinite(eta) else eta,
        "pessimistic_seconds": pess, "last_error": last_error,
        "paused_reason": paused_reason, "stop": stop,
    }
    atomic_json(Path(run_dir) / "status.json", snapshot)


def reconcile_stale_markers(run_dir):
    run_dir = Path(run_dir)
    live = []
    stale = []
    for marker_path in sorted((run_dir / "running").glob("*.json")):
        marker = load_json(marker_path, {})
        solver_pid = marker.get("solver_pid")
        worker_pid = marker.get("worker_pid")
        if pid_alive(solver_pid) or pid_alive(worker_pid):
            live.append({
                "marker": str(marker_path),
                "job_id": marker.get("job_id"),
                "layer": marker.get("layer"),
                "worker_pid": worker_pid,
                "solver_pid": solver_pid,
            })
            continue
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        label = "%s_%s_%s" % (
            marker.get("job_id", marker_path.stem),
            marker.get("layer", "unknown"),
            stamp,
        )
        dst = run_dir / "recovery" / label
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(marker_path, dst / "marker.json")
        for key, name in (("cnf_path", "instance.cnf"), ("log_path", "solver.log")):
            src = marker.get(key)
            if src and Path(src).exists():
                shutil.move(str(src), dst / name)
        marker_path.unlink()
        stale.append(str(dst))
    if live:
        raise RuntimeError(
            "live process(es) from a prior runner detected; refusing duplicate resume: %s"
            % live
        )
    return stale


def validate_environment(cfg, manifest):
    problems = []
    for key in ("generic_core", "abc_encode", "legacy_encode"):
        if not Path(cfg[key]).is_file():
            problems.append("%s missing: %s" % (key, cfg[key]))
    if not Path(cfg["solver"]).is_file() or not os.access(cfg["solver"], os.X_OK):
        problems.append("solver missing/not executable: %s" % cfg["solver"])
    if len(manifest["physical_cpu_representatives"]) < cfg["workers"] + cfg["reserve_cores"]:
        problems.append(
            "need >= %d physical cores, detected %d"
            % (cfg["workers"] + cfg["reserve_cores"], len(manifest["physical_cpu_representatives"]))
        )
    if disk_free_gib(cfg["run_dir"]) < cfg["disk_floor_gib"]:
        problems.append("disk below floor at startup")
    if mem_available_gib() < cfg["mem_floor_gib"]:
        problems.append("MemAvailable below floor at startup")
    if problems:
        raise RuntimeError("; ".join(problems))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("plan", "run"), default="plan")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--solver", default=str(Path.home() / ".local/bin/cadical"))
    ap.add_argument("--generic-core", default="src/breadth1/o3_generic_core.py")
    ap.add_argument("--abc-encode", default="src/breadth1/o3_abc_encode.py")
    ap.add_argument(
        "--legacy-encode",
        default="/home/rb/conway99_workspace/conway99_freezes/"
                "O3_TASK03_FULLCERT_1.1_20260902/SOURCE/context/qsat/encode.py",
    )
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--watchdog-slack", type=int, default=120)
    ap.add_argument("--report-seconds", type=int, default=600)
    ap.add_argument("--disk-floor-gib", type=float, default=120.0)
    ap.add_argument("--mem-floor-gib", type=float, default=8.0)
    ap.add_argument("--reserve-cores", type=int, default=2)
    ap.add_argument("--master-seed", type=int, default=20260903)
    ap.add_argument("--max-types", type=int, default=0)
    args = ap.parse_args()

    root = Path.cwd()
    cfg = vars(args).copy()
    cfg["runner"] = str(Path(__file__).resolve())
    for key in ("run_dir", "solver", "generic_core", "abc_encode", "legacy_encode"):
        p = Path(cfg[key]).expanduser()
        if key != "run_dir" and not p.is_absolute():
            p = root / p
        cfg[key] = str(p.resolve())
    run_dir = Path(cfg["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("types", "running", "logs", "tmp", "frozen", "errors", "recovery"):
        (run_dir / sub).mkdir(exist_ok=True)

    lock_file = open(run_dir / "runner.lock", "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("another runner holds %s" % (run_dir / "runner.lock"))

    generic = load_module("generic_core_main", cfg["generic_core"])
    cpus = discover_physical_cpus()
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        expected = make_manifest(cfg, generic, cpus)
        keys = (
            "master_seed", "timeout", "workers", "layers", "types", "instances",
            "worker_cpus", "paths", "sha256",
        )
        for key in keys:
            if manifest.get(key) != expected.get(key):
                raise RuntimeError("manifest mismatch on resume: %s" % key)
    else:
        manifest = make_manifest(cfg, generic, cpus)
        atomic_json(manifest_path, manifest)

    validate_environment(cfg, manifest)
    print("O3_ABC_SCOUT_PREFLIGHT PASS", flush=True)
    print("TYPES=%d INSTANCES=%d WORKERS=%d TIMEOUT=%ds" % (
        len(manifest["types"]), manifest["instances"], cfg["workers"], cfg["timeout"]
    ), flush=True)
    print("WORKER_CPUS=%s RESERVED_PHYSICAL_CORES=%d" % (
        manifest["worker_cpus"], cfg["reserve_cores"]
    ), flush=True)
    print("MEM_AVAILABLE=%.2fGiB DISK_FREE=%.2fGiB" % (
        mem_available_gib(), disk_free_gib(run_dir)
    ), flush=True)
    batches = math.ceil(len(manifest["types"]) / max(1, cfg["workers"]))
    scientific_hours = batches * len(LAYERS) * cfg["timeout"] / 3600.0
    watchdog_hours = batches * len(LAYERS) * (
        cfg["timeout"] + cfg["watchdog_slack"]
    ) / 3600.0
    print("SCIENTIFIC_LIMIT_UPPER_BOUND=%.2fh" % scientific_hours, flush=True)
    print("WATCHDOG_CEILING_EXCL_ENCODING=%.2fh" % watchdog_hours, flush=True)

    if cfg["mode"] == "plan":
        print("PLAN_ONLY: no CNF encoded and no solver started.", flush=True)
        return

    recovered = reconcile_stale_markers(run_dir)
    if recovered:
        print("RECOVERED_STALE_ARTIFACTS=%d" % len(recovered), flush=True)

    if stop_reason(run_dir):
        raise SystemExit("STOP.json exists; refusing to resume automatically: %s" % stop_reason(run_dir))

    started_epoch = time.time()
    active = {}
    interrupted = {"value": False}
    hard_abort_handled = False

    def handle_signal(signum, frame):
        interrupted["value"] = True
        set_stop(run_dir, "USER_INTERRUPT", {"signal": signum})

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    last_report = 0.0
    while True:
        for pid, item in list(active.items()):
            proc = item["proc"]
            if not proc.is_alive():
                proc.join()
                if proc.exitcode != 0 and not stop_reason(run_dir):
                    set_stop(run_dir, "WORKER_CRASH", {
                        "pid": pid, "job_id": item["job_id"], "exitcode": proc.exitcode,
                    })
                del active[pid]

        states = load_type_states(run_dir)
        results = all_instance_results(states)
        errors = sum(1 for x in results if x.get("status") == "ERROR")
        if results and errors / len(results) > 0.05 and not stop_reason(run_dir):
            set_stop(run_dir, "ERROR_RATE_GT_5_PERCENT", {
                "errors": errors, "completed_instances": len(results),
            })

        stop = stop_reason(run_dir)
        if (
            stop
            and stop.get("reason") in HARD_ABORT_REASONS
            and not hard_abort_handled
        ):
            killed = abort_other_solvers_for_hard_stop(run_dir, stop)
            print(
                "HARD_STOP_ABORT reason=%s other_solvers=%d"
                % (stop.get("reason"), len(killed)),
                flush=True,
            )
            hard_abort_handled = True
        paused_reason = resource_pause_reason(cfg)

        if not stop and not paused_reason:
            active_jids = {x["job_id"] for x in active.values()}
            for item in manifest["types"]:
                if len(active) >= cfg["workers"]:
                    break
                jid = item["job_id"]
                state = states.get(jid)
                if state and state.get("complete"):
                    continue
                if jid in active_jids:
                    continue
                used_cpus = {x["cpu"] for x in active.values()}
                free_cpus = [
                    c for c in manifest["worker_cpus"]
                    if c not in used_cpus
                ]
                if not free_cpus:
                    break
                cpu = free_cpus[0]
                proc = Process(
                    target=worker_run,
                    args=(cfg, item["tau"], tuple(item["cycle_type"]), cpu),
                    name=jid,
                )
                proc.start()
                active[proc.pid] = {"proc": proc, "job_id": jid, "cpu": cpu}
                active_jids.add(jid)

        now = time.time()
        if now - last_report >= cfg["report_seconds"] or last_report == 0:
            report(run_dir, manifest, started_epoch, len(active), paused_reason)
            last_report = now

        states = load_type_states(run_dir)
        complete_types = sum(1 for s in states.values() if s.get("complete"))
        if complete_types == len(manifest["types"]) and not active:
            report(run_dir, manifest, started_epoch, 0, None)
            print("O3_ABC_SCOUT COMPLETE", flush=True)
            break
        if stop_reason(run_dir) and not active:
            report(run_dir, manifest, started_epoch, 0, paused_reason)
            print("O3_ABC_SCOUT STOPPED", flush=True)
            break
        if interrupted["value"] and not active:
            break
        time.sleep(2.0)


if __name__ == "__main__":
    main()
