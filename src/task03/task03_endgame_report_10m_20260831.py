#!/usr/bin/env python3
import collections
import math
import os
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

INTERVAL = 600
TOTAL_A = 656
DISK_GUARD_GIB = 75.0

RUN_DIR = Path("/home/rb/conway99_workspace/o3_qsat_runs/task03_fullcert_1.1_20260829")
STATE = RUN_DIR / "state.json"
RUN_LOG = RUN_DIR / "endgame_5plus3_20260831.log"
REPORT_LOG = RUN_DIR / "endgame_report_10m_20260831.log"

LONG_KEYS = {
    "LEAF_D1_001000000_001",
    "LEAF_D1_001100010_010",
    "LEAF_D1_010001100_001",
    "LEAF_D1_100000000_100",
    "LEAF_D1_100010001_010",
    "LEAF_D2_000000000_100_100",
    "LEAF_D3_000000000_010_001_100",
}

stop = False


def handle_stop(signum, frame):
    global stop
    stop = True


def load_state():
    import json
    with STATE.open() as f:
        return json.load(f)


def gib(n):
    return n / (1024 ** 3)


def disk_free():
    return gib(shutil.disk_usage("/home/rb").free)


def mem_available():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024 ** 2)
    return float("nan")


def parse_run_start():
    if not RUN_LOG.exists():
        return None
    pat = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) ENDGAME_5PLUS3_START")
    for line in RUN_LOG.read_text(errors="replace").splitlines():
        m = pat.match(line)
        if m:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            return dt.astimezone()
    return None


def active_processes():
    out = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,etimes=,args="],
        text=True, capture_output=True, check=False
    ).stdout
    cadical = []
    checkers = []
    for raw in out.splitlines():
        parts = raw.strip().split(None, 3)
        if len(parts) < 4:
            continue
        pid, ppid, elapsed, args = parts
        try:
            elapsed = int(elapsed)
        except ValueError:
            continue
        if args.startswith("cadical --lrat --no-binary"):
            cadical.append((int(pid), int(ppid), elapsed, args))
        elif args.startswith("lrat-check ") or " cake_lpr " in f" {args} " or args.startswith("cake_lpr "):
            checkers.append((int(pid), int(ppid), elapsed, args))
    return cadical, checkers


def leaf_for_args(args):
    for key in LONG_KEYS:
        short = key.removeprefix("LEAF_")
        if f"/{short}/" in args or f"/{short}.cnf" in args:
            return key
    return None


def fmt_duration(seconds):
    if seconds is None or not math.isfinite(seconds):
        return "?"
    seconds = max(0, int(seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}d {h:02d}h {m:02d}m"
    return f"{h}h {m:02d}m"


def greedy_makespan(durations, slots=3):
    loads = [0.0] * slots
    for d in sorted(durations, reverse=True):
        i = min(range(slots), key=lambda j: loads[j])
        loads[i] += d
    return max(loads) if loads else 0.0


def report(prev=None):
    now = datetime.now().astimezone()
    state = load_state()
    jobs = state["modular_jobs"]
    counts = collections.Counter(rec.get("state") for rec in jobs.values())
    certified = counts.get("CERTIFIED", 0)
    remaining = TOTAL_A - certified

    long_states = {k: jobs[k].get("state") for k in sorted(LONG_KEYS)}
    long_done = sum(v == "CERTIFIED" for v in long_states.values())
    long_remaining = len(LONG_KEYS) - long_done
    regular_remaining = sum(
        rec.get("state") != "CERTIFIED"
        for k, rec in jobs.items()
        if k not in LONG_KEYS
    )

    free = disk_free()
    mem = mem_available()
    cadical, checkers = active_processes()
    active_long = {}
    active_regular = []
    for pid, ppid, elapsed, args in cadical:
        key = leaf_for_args(args)
        if key:
            active_long[key] = (pid, elapsed)
        else:
            active_regular.append((pid, elapsed, args))

    lower_durations = []
    for key, st in long_states.items():
        if st == "CERTIFIED":
            continue
        if key in active_long:
            lower_durations.append(max(0.0, 6 * 3600 - active_long[key][1]))
        elif st in ("CHECKING", "COMPRESSING"):
            lower_durations.append(0.0)
        else:
            lower_durations.append(6 * 3600)
    floor_seconds = greedy_makespan(lower_durations, 3)
    floor_time = now + timedelta(seconds=floor_seconds)

    run_start = parse_run_start()
    expected_lo = run_start + timedelta(hours=30) if run_start else None
    expected_hi = run_start + timedelta(hours=45) if run_start else None

    empirical = None
    if run_start and long_done:
        elapsed = max(1.0, (now - run_start).total_seconds())
        rate = long_done / elapsed
        empirical = long_remaining / rate if rate > 0 else None

    disk_line = "disk trend: first sample"
    if prev is not None:
        dt = time.time() - prev["t"]
        if dt > 0:
            rate_gib_h = (free - prev["free"]) / dt * 3600
            if rate_gib_h < -0.05:
                hours = (free - DISK_GUARD_GIB) / (-rate_gib_h) if free > DISK_GUARD_GIB else 0
                disk_line = f"disk: consuming {-rate_gib_h:.2f} GiB/h; ETA to {DISK_GUARD_GIB:.0f}GiB guard ~{fmt_duration(hours*3600)}"
            else:
                disk_line = f"disk: stable/increasing ({rate_gib_h:+.2f} GiB/h)"

    lines = [
        f"=== ENDGAME REPORT {now.isoformat(timespec='seconds')} ===",
        f"phase={state.get('phase')} pureA={certified}/{TOTAL_A} remaining={remaining} states={dict(sorted(counts.items()))}",
        f"remaining split: regular={regular_remaining} long={long_remaining}/7; long certified={long_done}/7",
        f"processes: cadical_real={len(cadical)} checker={len(checkers)}; free={free:.1f}GiB mem_available={mem:.1f}GiB stop_reason={state.get('stop_reason')}",
        disk_line,
        f"ETA hard floor from prior >6h/long solver history: not before ~{floor_time.strftime('%Y-%m-%d %H:%M')} (solver-only lower bound)",
    ]

    if expected_lo and expected_hi:
        lines.append(
            f"ETA planning window: {expected_lo.strftime('%Y-%m-%d %H:%M')} .. {expected_hi.strftime('%Y-%m-%d %H:%M')} "
            f"(30-45h from endgame start; expectation, NOT a bound)"
        )
    if empirical is not None:
        lines.append(f"ETA empirical long-cert throughput: ~{fmt_duration(empirical)} from now (very noisy until several long certs finish)")

    if active_long:
        lines.append("active long:")
        for key in sorted(active_long):
            pid, elapsed = active_long[key]
            short = key.removeprefix("LEAF_")
            proof = RUN_DIR / "cert" / "leaf" / short / "proof.lrat"
            size = gib(proof.stat().st_size) if proof.exists() else 0.0
            lines.append(f"  {short} pid={pid} elapsed={fmt_duration(elapsed)} proof={size:.2f}GiB state={jobs[key].get('state')}")
    else:
        lines.append("active long: none")

    text = "\n".join(lines) + "\n"
    print(text, end="", flush=True)
    with REPORT_LOG.open("a") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

    return {"t": time.time(), "free": free}


def main():
    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)
    prev = None
    while not stop:
        try:
            prev = report(prev)
        except Exception as exc:
            msg = f"REPORTER_ERROR {datetime.now().astimezone().isoformat(timespec='seconds')} {type(exc).__name__}: {exc}\n"
            print(msg, end="", flush=True)
            with REPORT_LOG.open("a") as f:
                f.write(msg)
        for _ in range(INTERVAL):
            if stop:
                break
            time.sleep(1)


if __name__ == "__main__":
    main()
