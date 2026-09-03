#!/usr/bin/env python3
import importlib.util
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0/task03_fullcert_1_1_endgame_notimeout_20260830.py")
REGULAR_SLOTS = 5
LONG_SLOTS = 3
TOTAL_A = 656

spec = importlib.util.spec_from_file_location("endgame_base", BASE)
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
r = e.r


def audit():
    actual = r.sha256_file(BASE)
    print(f"BASE={BASE}")
    print(f"BASE_SHA256={actual}")
    e.audit()
    print(f"SCHEDULER regular_slots={REGULAR_SLOTS} long_slots={LONG_SLOTS} total_slots={REGULAR_SLOTS + LONG_SLOTS}")
    ok = (
        len(e.SUPERSEDED_KEYS) == 12
        and len(e.LONG_KEYS) == 7
        and not (e.SUPERSEDED_KEYS & e.LONG_KEYS)
        and REGULAR_SLOTS + LONG_SLOTS == 8
    )
    print("SCHEDULER_AUDIT=" + ("PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit(2)


def finalize(state, done_event):
    done_event.set()
    state["ended_at"] = r.time.time()

    pure_count = sum(rec.get("state") == "CERTIFIED" for rec in state["modular_jobs"].values())
    pure_complete = pure_count == TOTAL_A

    if any(rec.get("state") == "SAT_VERIFIED" for rec in state["modular_jobs"].values()):
        state["phase"] = "SAT_VERIFIED"
    elif pure_complete:
        state["phase"] = "LEMMA_CNF_CERTIFIED"
    elif r.stop_event.is_set():
        state["phase"] = "STOPPED_RESUMABLE"
        if not state.get("stop_reason") and r.global_stop_reason:
            state["stop_reason"] = r.global_stop_reason
    else:
        state["phase"] = "PARTIAL"

    r.save_state(state, terminal=True)
    r.write_final_manifest(state)

    if pure_complete:
        check = r.run_coverage_checker()
        state["coverage_checker"] = check
        if check.get("exitcode") != 0:
            state["phase"] = "CERTIFIED_NEEDS_COVERAGE_REVIEW"
            state["stop_reason"] = "COVERAGE_CHECKER_FAILED"
        r.save_state(state, terminal=True)
        r.write_final_manifest(state)

    try:
        r.RUNNER_PID.unlink()
        r.fsync_dir(r.RUNNER_PID.parent)
    except FileNotFoundError:
        pass

    r.log(
        f"ENDGAME_5PLUS3_DONE phase={state['phase']} "
        f"pure_A={pure_count}/{TOTAL_A} free={r.disk_free_gib():.1f}GiB"
    )


def run():
    audit()

    state = r.read_json(r.STATE)
    r.reset_interrupted(state)

    gate = state.get("calibration_gate")
    if state.get("phase") not in ("CALIBRATION_COMPLETE", "STOPPED_RESUMABLE", "PARTIAL"):
        raise SystemExit(f"endgame run not allowed from phase={state.get('phase')}")
    if not gate or not gate.get("pass"):
        raise SystemExit("calibration gate not passed")

    r.stop_event.clear()
    r.baseline_success_event.clear()
    r.aux_stop_event.set()
    r.modular_solver_slots.set_limit(REGULAR_SLOTS + LONG_SLOTS)

    removed_count, removed_bytes = r.cleanup_incomplete_raw_proofs_aonly(state)

    eligible = {"PENDING", "TIMEOUT", "ERROR", "SKIPPED_SUPERSEDED"}
    pending = [k for k, rec in state["modular_jobs"].items() if rec.get("state") in eligible]
    expected = set(e.SUPERSEDED_KEYS) | set(e.LONG_KEYS)
    if len(pending) != 19 or set(pending) != expected:
        raise SystemExit(f"endgame pending-set mismatch count={len(pending)}")

    for key in pending:
        state["modular_jobs"][key]["state"] = "PENDING"
        state["modular_jobs"][key]["failure"] = None

    regular = sorted(
        e.SUPERSEDED_KEYS,
        key=lambda k: -(state["modular_jobs"][k].get("scout_conflicts") or 0),
    )
    long = sorted(
        e.LONG_KEYS,
        key=lambda k: -(state["modular_jobs"][k].get("scout_conflicts") or 0),
    )

    state["phase"] = "RUNNING"
    state["ended_at"] = None
    state["stop_reason"] = None
    r.atomic_text_fsync(r.RUNNER_PID, str(r.os.getpid()) + "\n")
    r.save_state(state, terminal=True)

    r.log(
        f"ENDGAME_5PLUS3_START regular={len(regular)} long={len(long)} "
        f"regular_slots={REGULAR_SLOTS} long_slots={LONG_SLOTS} "
        f"solver_timeout=None lrat_timeout=None cake_timeout=None "
        f"disk_floor={r.MIN_FREE_GIB:.1f}GiB "
        f"raw_reclaimed={removed_bytes/(1024**3):.1f}GiB files={removed_count} "
        f"free={r.disk_free_gib():.1f}GiB mem={r.mem_available_gib():.1f}GiB"
    )

    done_event = threading.Event()
    tick = threading.Thread(target=r.ticker, args=(state, done_event), daemon=True)
    tick.start()

    futures = []
    try:
        with ThreadPoolExecutor(max_workers=REGULAR_SLOTS) as regular_ex, \
             ThreadPoolExecutor(max_workers=LONG_SLOTS) as long_ex:
            futures.extend(regular_ex.submit(e.endgame_modular_worker, key, state) for key in regular)
            futures.extend(long_ex.submit(e.endgame_modular_worker, key, state) for key in long)

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    r.log(f"ENDGAME_FUTURE_EXCEPTION {type(exc).__name__}: {exc}")
                    r.request_stop("ENDGAME_FUTURE_EXCEPTION")
                if r.stop_event.is_set():
                    break
    finally:
        done_event.set()
        tick.join(timeout=5)
        finalize(state, done_event)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("audit", "run"))
    args = parser.parse_args()

    signal.signal(signal.SIGINT, r.signal_handler)
    signal.signal(signal.SIGTERM, r.signal_handler)

    audit() if args.command == "audit" else run()
