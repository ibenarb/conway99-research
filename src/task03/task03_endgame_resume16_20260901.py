#!/usr/bin/env python3
import importlib.util
import os
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SRC = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0/task03_fullcert_1_1_salvage_v4_floor70_20260830.py")
WORK = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0")
REAL_CAKE = Path("/home/rb/conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr")
CAKE_WRAPPER = WORK / "cake_lpr_16g_wrapper_20260901.sh"

TOTAL_A = 656
SLOTS = 3
HEAP_MB = 16384
STACK_MB = 4096
DISK_FLOOR_GIB = 75.0

EXPECTED_OPEN = {
    "LEAF_D1_001000000_001",
    "LEAF_D1_001100010_010",
    "LEAF_D1_010001100_001",
    "LEAF_D1_100010001_010",
}

spec = importlib.util.spec_from_file_location("fullcert_v4_resume16", SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

r.MIN_FREE_GIB = DISK_FLOOR_GIB
r.MODULAR_SOLVER_TIMEOUT = None
r.LRAT_CHECK_TIMEOUT = None
r.CAKE_CHECK_TIMEOUT = None
r.PURE_A_SOLVER_SLOTS = SLOTS


def ensure_cake_wrapper():
    text = "#!/bin/sh\n" + f'exec "{REAL_CAKE}" --CML_HEAP_SIZE={HEAP_MB} --CML_STACK_SIZE={STACK_MB} "$@"\n'
    if not CAKE_WRAPPER.exists() or CAKE_WRAPPER.read_text() != text:
        CAKE_WRAPPER.write_text(text)
        os.chmod(CAKE_WRAPPER, 0o755)
    r.CAKE_LPR = CAKE_WRAPPER


def live_runner_pid():
    if not r.RUNNER_PID.exists():
        return None
    try:
        pid = int(r.RUNNER_PID.read_text().strip())
        os.kill(pid, 0)
        return pid
    except (ValueError, ProcessLookupError):
        return None


def audit():
    ensure_cake_wrapper()
    pid = live_runner_pid()
    if pid:
        raise SystemExit(f"AUDIT_FAIL live runner pid={pid}")

    state = r.read_json(r.STATE)
    open_keys = {k for k, rec in state["modular_jobs"].items() if rec.get("state") != "CERTIFIED"}
    cert = sum(rec.get("state") == "CERTIFIED" for rec in state["modular_jobs"].values())
    errors = {k: state["modular_jobs"][k].get("failure") for k in open_keys if state["modular_jobs"][k].get("state") == "ERROR"}

    print(f"SOURCE={SRC}")
    print(f"SOURCE_SHA256={r.sha256_file(SRC)}")
    print(f"PHASE={state.get('phase')} CERTIFIED={cert}/{TOTAL_A} OPEN={len(open_keys)}")
    print(f"OPEN_KEYS={sorted(open_keys)}")
    print(f"ERRORS={errors}")
    print(f"CAKE_WRAPPER={CAKE_WRAPPER}")
    print(f"CAKE_WRAPPER_SHA256={r.sha256_file(CAKE_WRAPPER)}")
    print(f"CONFIG slots={SLOTS} solver_timeout=None lrat_timeout=None cake_timeout=None disk_floor={DISK_FLOOR_GIB:.1f}GiB heap={HEAP_MB}MB stack={STACK_MB}MB")
    print(f"RESOURCE free={r.disk_free_gib():.1f}GiB mem_available={r.mem_available_gib():.1f}GiB")
    ok = (
        state.get("phase") in ("STOPPED_RESUMABLE", "PARTIAL")
        and cert == 652
        and open_keys == EXPECTED_OPEN
        and state.get("stop_reason") in (None, "")
    )
    print("RESUME_AUDIT=" + ("PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit(2)


def worker(key, state):
    rec = state["modular_jobs"][key]
    attempt = None
    try:
        if r.stop_event.is_set():
            return
        with r.lock:
            if rec["state"] != "PENDING":
                return
            rec["state"] = "RUNNING"
            rec["failure"] = None
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
            r.request_stop(f"RESUME16_JOB_FAILURE_{key}_{result}")
    except Exception as exc:
        attempt = {"started_at": r.time.time(), "ended_at": r.time.time(), "exception": f"{type(exc).__name__}: {exc}"}
        r.terminal_update(state, state["modular_jobs"], key, "ERROR", attempt, attempt["exception"])
        r.request_stop(f"RESUME16_EXCEPTION_{key}")


def finalize(state, done_event):
    done_event.set()
    state["ended_at"] = r.time.time()
    cert = sum(rec.get("state") == "CERTIFIED" for rec in state["modular_jobs"].values())

    if any(rec.get("state") == "SAT_VERIFIED" for rec in state["modular_jobs"].values()):
        state["phase"] = "SAT_VERIFIED"
    elif cert == TOTAL_A:
        state["phase"] = "LEMMA_CNF_CERTIFIED"
    elif r.stop_event.is_set():
        state["phase"] = "STOPPED_RESUMABLE"
        if not state.get("stop_reason") and r.global_stop_reason:
            state["stop_reason"] = r.global_stop_reason
    else:
        state["phase"] = "PARTIAL"

    r.save_state(state, terminal=True)
    r.write_final_manifest(state)

    if cert == TOTAL_A:
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

    r.log(f"ENDGAME_RESUME16_DONE phase={state['phase']} certified={cert}/{TOTAL_A} free={r.disk_free_gib():.1f}GiB")


def run():
    audit()
    ensure_cake_wrapper()
    state = r.read_json(r.STATE)
    r.reset_interrupted(state)

    gate = state.get("calibration_gate")
    if not gate or not gate.get("pass"):
        raise SystemExit("calibration gate not passed")

    r.stop_event.clear()
    r.baseline_success_event.clear()
    r.aux_stop_event.set()
    r.modular_solver_slots.set_limit(SLOTS)

    removed_count, removed_bytes = r.cleanup_incomplete_raw_proofs_aonly(state)

    open_keys = [k for k, rec in state["modular_jobs"].items() if rec.get("state") != "CERTIFIED"]
    if set(open_keys) != EXPECTED_OPEN:
        raise SystemExit(f"resume open-set mismatch: {sorted(open_keys)}")

    for key in open_keys:
        state["modular_jobs"][key]["state"] = "PENDING"
        state["modular_jobs"][key]["failure"] = None

    open_keys.sort(key=lambda k: -(state["modular_jobs"][k].get("scout_conflicts") or 0))

    state["phase"] = "RUNNING"
    state["ended_at"] = None
    state["stop_reason"] = None
    r.atomic_text_fsync(r.RUNNER_PID, str(os.getpid()) + "\n")
    r.save_state(state, terminal=True)

    r.log(
        f"ENDGAME_RESUME16_START pending={len(open_keys)} slots={SLOTS} "
        f"solver_timeout=None lrat_timeout=None cake_timeout=None "
        f"cake_heap={HEAP_MB}MB cake_stack={STACK_MB}MB "
        f"disk_floor={DISK_FLOOR_GIB:.1f}GiB "
        f"raw_reclaimed={removed_bytes/(1024**3):.1f}GiB files={removed_count} "
        f"free={r.disk_free_gib():.1f}GiB mem={r.mem_available_gib():.1f}GiB"
    )

    done_event = threading.Event()
    tick = threading.Thread(target=r.ticker, args=(state, done_event), daemon=True)
    tick.start()

    futures = []
    try:
        with ThreadPoolExecutor(max_workers=SLOTS) as ex:
            futures = [ex.submit(worker, key, state) for key in open_keys]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    r.log(f"RESUME16_FUTURE_EXCEPTION {type(exc).__name__}: {exc}")
                    r.request_stop("RESUME16_FUTURE_EXCEPTION")
                if r.stop_event.is_set():
                    break
    finally:
        done_event.set()
        tick.join(timeout=5)
        finalize(state, done_event)


if __name__ == "__main__":
    import argparse

    signal.signal(signal.SIGINT, r.signal_handler)
    signal.signal(signal.SIGTERM, r.signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("audit", "run"))
    args = parser.parse_args()

    audit() if args.command == "audit" else run()
