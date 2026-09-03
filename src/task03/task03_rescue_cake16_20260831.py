#!/usr/bin/env python3
import importlib.util
import signal
from pathlib import Path

SRC = Path("/home/rb/conway99_workspace/conway99_o3_lemma_1.0/task03_fullcert_1_1_salvage_v4_floor70_20260830.py")
TARGET = "LEAF_D1_100000000_100"
HEAP_MB = 16384
STACK_MB = 4096
MIN_MEM_GIB = 24.0

spec = importlib.util.spec_from_file_location("fullcert_v4_rescue", SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

signal.signal(signal.SIGINT, r.signal_handler)
signal.signal(signal.SIGTERM, r.signal_handler)


def fail(msg):
    print("RESCUE_ABORT", msg, flush=True)
    raise SystemExit(2)


def main():
    if r.RUNNER_PID.exists():
        try:
            pid = int(r.RUNNER_PID.read_text().strip())
            r.os.kill(pid, 0)
        except (ValueError, ProcessLookupError):
            pass
        else:
            fail(f"runner already active pid={pid}")

    state = r.read_json(r.STATE)
    if state.get("phase") not in ("STOPPED_RESUMABLE", "PARTIAL"):
        fail(f"unexpected phase={state.get('phase')}")

    rec = state["modular_jobs"][TARGET]
    if rec.get("state") != "ERROR" or rec.get("failure") != "CAKE_EXIT_1":
        fail(f"target state/failure={rec.get('state')}/{rec.get('failure')}")

    if not rec.get("attempts"):
        fail("target has no prior attempt")
    prior = rec["attempts"][-1]
    if (prior.get("solver") or {}).get("exitcode") != 20:
        fail("prior solver was not exit 20")
    if (prior.get("lrat_check") or {}).get("exitcode") != 0:
        fail("prior lrat-check was not exit 0")

    cnf = Path(rec["cnf"])
    outdir = r.proof_dir_for(TARGET, rec, "MODULAR")
    proof = outdir / "proof.lrat"
    proof_gz = outdir / "proof.lrat.gz"

    if not proof.exists():
        fail(f"raw proof missing: {proof}")
    if proof_gz.exists():
        fail(f"gzip already exists unexpectedly: {proof_gz}")

    expected_bytes = prior.get("raw_proof_bytes")
    expected_sha = prior.get("raw_proof_sha256")
    if proof.stat().st_size != expected_bytes:
        fail(f"raw size mismatch actual={proof.stat().st_size} expected={expected_bytes}")

    mem = r.mem_available_gib()
    free = r.disk_free_gib()
    print(f"RESCUE_PREFLIGHT target={TARGET} raw={proof.stat().st_size/(1024**3):.2f}GiB free={free:.1f}GiB mem={mem:.1f}GiB heap={HEAP_MB}MB stack={STACK_MB}MB", flush=True)
    if mem < MIN_MEM_GIB:
        fail(f"mem_available={mem:.1f}GiB below rescue minimum {MIN_MEM_GIB:.1f}GiB")
    if free < 100.0:
        fail(f"disk_free={free:.1f}GiB below rescue minimum 100GiB")

    started = r.time.time()

    cnf_before = r.sha256_file(cnf)
    if cnf_before != rec["cnf_sha256"]:
        fail("CNF hash mismatch")

    print("RESCUE_HASH raw proof...", flush=True)
    raw_sha = r.sha256_file(proof)
    if raw_sha != expected_sha:
        fail(f"raw proof hash mismatch actual={raw_sha} expected={expected_sha}")
    print(f"RESCUE_HASH_OK sha256={raw_sha}", flush=True)

    lrat_out = outdir / "rescue16_lrat_check.out"
    lrat_err = outdir / "rescue16_lrat_check.err"
    lrat_time = outdir / "rescue16_lrat_check.time"
    cake_out = outdir / "rescue16_cake_lpr.out"
    cake_err = outdir / "rescue16_cake_lpr.err"
    cake_time = outdir / "rescue16_cake_lpr.time"

    print("RESCUE_LRAT_START", flush=True)
    lrat = r.run_process(
        ["lrat-check", str(cnf), str(proof)],
        lrat_out, lrat_err, None,
        timefile=lrat_time,
        projected_extra_gib=0.0,
        global_disk_stop=False,
    )
    print(f"RESCUE_LRAT_DONE exit={lrat.get('exitcode')} wall={lrat.get('wall')}", flush=True)
    if lrat.get("timed_out") or lrat.get("stopped") or lrat.get("exitcode") != 0:
        fail(f"fresh lrat-check failed: {lrat}")

    cake_cmd = [
        str(r.CAKE_LPR),
        f"--CML_HEAP_SIZE={HEAP_MB}",
        f"--CML_STACK_SIZE={STACK_MB}",
        str(cnf),
        str(proof),
    ]
    print("RESCUE_CAKE_START " + " ".join(cake_cmd), flush=True)
    cake = r.run_process(
        cake_cmd,
        cake_out, cake_err, None,
        timefile=cake_time,
        projected_extra_gib=0.0,
        global_disk_stop=False,
    )
    print(f"RESCUE_CAKE_DONE exit={cake.get('exitcode')} wall={cake.get('wall')} time_v={cake.get('time_v')}", flush=True)
    if cake.get("timed_out") or cake.get("stopped") or cake.get("exitcode") != 0:
        if cake_err.exists():
            print("RESCUE_CAKE_STDERR:", cake_err.read_text(errors="replace")[-2000:], flush=True)
        fail(f"cake_lpr failed exit={cake.get('exitcode')}")

    print("RESCUE_POST_HASH_START", flush=True)
    cnf_after = r.sha256_file(cnf)
    raw_sha_after = r.sha256_file(proof)
    if cnf_after != cnf_before or cnf_after != rec["cnf_sha256"]:
        fail("CNF hash instability")
    if raw_sha_after != raw_sha:
        fail("proof hash instability")
    print("RESCUE_POST_HASH_OK", flush=True)

    print("RESCUE_GZIP_START", flush=True)
    raw_bytes = proof.stat().st_size
    compression = r.gzip_and_verify(proof, proof_gz, raw_sha)
    print(f"RESCUE_GZIP_DONE gzip_bytes={compression.get('gzip_bytes')} gzip_sha256={compression.get('gzip_sha256')}", flush=True)

    attempt = {
        "started_at": started,
        "ended_at": r.time.time(),
        "lane": "MODULAR",
        "salvage_existing_raw": True,
        "salvage_reason": "CAKEML_HEAP_EXHAUSTION_RETRY_16G",
        "salvage_prior_attempt_count": len(rec.get("attempts", [])),
        "solver": {
            "reused_existing_raw_proof": True,
            "prior_exitcode": 20,
            "prior_solver_wall": (prior.get("solver") or {}).get("wall"),
            "note": "Existing CaDiCaL UNSAT LRAT reused after exact size/hash match.",
        },
        "raw_proof_sha256": raw_sha,
        "raw_proof_bytes": raw_bytes,
        "cnf_sha256_before_checks": cnf_before,
        "cnf_sha256_after_checks": cnf_after,
        "raw_proof_sha256_after_checks": raw_sha_after,
        "lrat_check": lrat,
        "cake_lpr": {
            **cake,
            "cml_heap_mb": HEAP_MB,
            "cml_stack_mb": STACK_MB,
        },
        **compression,
        "proof_gz": str(proof_gz),
        "compression_ratio": compression["gzip_bytes"] / raw_bytes,
    }
    attempt["total_wall"] = attempt["ended_at"] - attempt["started_at"]

    proof.unlink()
    r.fsync_dir(proof.parent)

    r.terminal_update(state, state["modular_jobs"], TARGET, "CERTIFIED", attempt)
    state = r.read_json(r.STATE)
    state["stop_reason"] = None
    r.save_state(state, terminal=True)
    r.write_final_manifest(state)

    print(
        f"RESCUE_CERTIFIED target={TARGET} raw={raw_bytes/(1024**3):.2f}GiB "
        f"gz={compression['gzip_bytes']/(1024**3):.2f}GiB "
        f"free={r.disk_free_gib():.1f}GiB state={state['modular_jobs'][TARGET]['state']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
