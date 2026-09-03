#!/usr/bin/env python3
import importlib.util
import signal
import threading
from collections import Counter
from pathlib import Path

SRC = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0/task03_fullcert_1_1_salvage_v4_floor70_20260830.py")
spec = importlib.util.spec_from_file_location("fullcert_v4", SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

TOTAL_A = 656
TOTAL_SLOTS = 8
LONG_SLOTS = 3
DISK_FLOOR_GIB = 75.0

initial = r.read_json(r.STATE)

def historically_timed_out(rec):
    if rec.get("state") == "TIMEOUT":
        return True
    for attempt in rec.get("attempts", []):
        if (attempt.get("solver") or {}).get("timed_out"):
            return True
    return False

LONG_KEYS = {k for k, rec in initial["modular_jobs"].items() if rec.get("state") != "CERTIFIED" and historically_timed_out(rec)}
SUPERSEDED_KEYS = {k for k, rec in initial["modular_jobs"].items() if rec.get("state") == "SKIPPED_SUPERSEDED"}
LONG_GATE = threading.Semaphore(LONG_SLOTS)

r.PURE_A_SOLVER_SLOTS = TOTAL_SLOTS
r.MIN_FREE_GIB = DISK_FLOOR_GIB
r.MODULAR_SOLVER_TIMEOUT = None
r.LRAT_CHECK_TIMEOUT = None
r.CAKE_CHECK_TIMEOUT = None


def acquire_long_slot():
    while not r.stop_event.is_set():
        if LONG_GATE.acquire(timeout=5):
            return True
    return False


def endgame_modular_worker(key, state):
    rec = state["modular_jobs"][key]
    held_long = False
    attempt = None
    try:
        if key in LONG_KEYS:
            held_long = acquire_long_slot()
            if not held_long:
                return
        if r.stop_event.is_set():
            return
        with r.lock:
            if rec["state"] != "PENDING":
                return
            rec["state"] = "RUNNING"
            r.mark_dirty()
        result, attempt = r.certify_pipeline(key, rec, "MODULAR", state, None)
        if result == "CERTIFIED":
            r.terminal_update(state, state["modular_jobs"], key, "CERTIFIED", attempt)
        elif result == "SAT_VERIFIED":
            r.terminal_update(state, state["modular_jobs"], key, "SAT_VERIFIED", attempt, "UNEXPECTED_SAT")
            r.request_stop(f"SAT_VERIFIED_{key}")
        elif result in ("STOPPED", "DISK_STOP"):
            with r.lock:
                rec["attempts"].append(attempt)
                rec["state"] = "PENDING"
                rec["failure"] = "STOPPED_RESUMABLE"
                r.mark_dirty()
                r.save_state(state, terminal=True)
        else:
            r.terminal_update(state, state["modular_jobs"], key, "ERROR", attempt, result)
            r.request_stop(f"ENDGAME_JOB_FAILURE_{key}_{result}")
    except Exception as exc:
        attempt = {"started_at": r.time.time(), "ended_at": r.time.time(), "exception": f"{type(exc).__name__}: {exc}"}
        r.terminal_update(state, state["modular_jobs"], key, "ERROR", attempt, attempt["exception"])
        r.request_stop(f"ENDGAME_EXCEPTION_{key}")
    finally:
        if held_long:
            LONG_GATE.release()


def audit():
    state = r.read_json(r.STATE)
    counts = Counter(rec.get("state") for rec in state["modular_jobs"].values())
    certified = counts.get("CERTIFIED", 0)
    remaining = TOTAL_A - certified
    active = [k for k, rec in state["modular_jobs"].items() if rec.get("state") in ("RUNNING", "CHECKING", "COMPRESSING")]
    print(f"SOURCE={SRC}")
    print(f"SOURCE_SHA256={r.sha256_file(SRC)}")
    print(f"PHASE={state.get("phase")} COUNTS={dict(sorted(counts.items()))} CERTIFIED={certified}/{TOTAL_A} REMAINING={remaining}")
    print(f"LONG_KEYS={len(LONG_KEYS)} {sorted(LONG_KEYS)}")
    print(f"SUPERSEDED_KEYS={len(SUPERSEDED_KEYS)} {sorted(SUPERSEDED_KEYS)}")
    print(f"ACTIVE_MODULAR={active}")
    print(f"CONFIG total_slots={TOTAL_SLOTS} long_slots={LONG_SLOTS} solver_timeout=None lrat_timeout=None cake_timeout=None disk_floor={DISK_FLOOR_GIB:.1f}GiB")
    print(f"RESOURCE free={r.disk_free_gib():.2f}GiB mem_available={r.mem_available_gib():.2f}GiB")
    ok = certified == 637 and remaining == 19 and len(LONG_KEYS) == 7 and len(SUPERSEDED_KEYS) == 12 and not active and state.get("phase") == "PARTIAL"
    print("AUDIT=" + ("PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit(2)


def run():
    audit()
    r.modular_worker = endgame_modular_worker
    signal.signal(signal.SIGINT, r.signal_handler)
    signal.signal(signal.SIGTERM, r.signal_handler)
    r.log(f"ENDGAME_NOTIMEOUT_CONFIG total_slots={TOTAL_SLOTS} long_slots={LONG_SLOTS} long_keys={len(LONG_KEYS)} superseded={len(SUPERSEDED_KEYS)} disk_floor={DISK_FLOOR_GIB:.1f}GiB solver_timeout=None lrat_timeout=None cake_timeout=None")
    r.run_a_only(True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("audit", "run"))
    args = ap.parse_args()
    audit() if args.command == "audit" else run()
