"""Recovery tests with real process exits and explicitly gated storage faults."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import runtime as r
import recovery as v
from test_runtime import wait_state, launch


UNSAT = "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--worker", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    out.mkdir(exist_ok=False)
    rows = []
    def record(name, **details):
        rows.append(dict(test=name, passed=True, **details))
        print(name, "PASS", flush=True)
    def new(name, text=UNSAT, checker=None, budget=60):
        cnf = out / (name + ".cnf")
        cnf.write_text(text)
        root = out / name
        r.init(root, cnf, a.worker, checker or a.checker, budget)
        (root / "ALLOW_TEST_FAULTS").touch()
        return root
    def crash(root, stage):
        env = dict(os.environ, N1_TEST_FAULT=stage)
        with (root / ("fault-" + stage + ".log")).open("wb") as log:
            p = subprocess.Popen([sys.executable, r.__file__, "run", str(root)],
                                 env=env, stdout=log, stderr=subprocess.STDOUT)
            assert p.wait() == 91
    def must_reject(call):
        try:
            call()
        except (ValueError, FileNotFoundError):
            return
        raise AssertionError("unsafe recovery accepted")
    def state_hashes(root):
        return {str(p.relative_to(root)): r.sha(p)
                for p in root.rglob("*") if p.is_file()}
    # Receipt committed, controller total not committed: reconstruct once.
    root = new("search_receipt")
    crash(root, "search_after_receipt")
    before = state_hashes(root)
    plan = v.recover(root)
    assert before == state_hashes(root)
    assert plan["proposed_status"] == "UNSAT_UNCERTIFIED"
    record("dry_run_read_only_after_real_supervisor_exit")
    v.recover(root, True)
    once = r.read(root / "state.json")["cpu_completed"]
    v.recover(root, True)
    assert r.read(root / "state.json")["cpu_completed"] == once
    old_source = next((root / "attempts").iterdir())
    old_proof = r.sha(old_source / "proof.partial")
    assert launch(root, True).wait() == 0
    s = r.read(root / "state.json")
    assert s["status"] == "UNSAT_CERTIFIED"
    assert len(list((root / "attempts").glob("*/search_receipt.json"))) == 1
    assert len(list((root / "attempts").glob("*/check_receipt.json"))) == 1
    assert r.sha(old_source / "proof.partial") == old_proof
    record("receipt_recovery_idempotent_then_checker_only_resume")
    for stage in ("check_after_receipt", "after_final"):
        p = new(stage)
        crash(p, stage)
        v.recover(p, True)
        assert r.read(p / "state.json")["status"] == "UNSAT_CERTIFIED"
        count = len(list((p / "attempts").iterdir()))
        assert launch(p, True).wait() == 0
        assert len(list((p / "attempts").iterdir())) == count
        record(stage + "_recovers_without_recomputing")
    # Real drat-trim runs first, wrapper delays its own completion after VERIFIED.
    wrapper = out / "delayed_checker.py"
    wrapper.write_text("#!" + sys.executable + "\n" +
        "import pathlib,subprocess,sys,time\n" +
        "p=subprocess.run([" + repr(str(a.checker)) + "]+sys.argv[1:],stdout=subprocess.PIPE)\n" +
        "sys.stdout.buffer.write(p.stdout); sys.stdout.flush()\n" +
        "pathlib.Path('VERIFIED_BUT_RUNNING').touch()\n" +
        "while not (pathlib.Path.cwd().parents[1]/'RELEASE_CHECKER').exists():\n" +
        "    sum(i*i for i in range(5000))\n" +
        "sys.exit(p.returncode)\n")
    wrapper.chmod(0o755)
    p = new("checker_stop", checker=wrapper, budget=0.01)
    proc = launch(p)
    s = wait_state(p, lambda x: x.get("phase") == "check" and x["request"], proc)
    while not list((p / "attempts").glob("*/VERIFIED_BUT_RUNNING")):
        assert proc.poll() is None
        time.sleep(0.02)
    assert r.read(p / "state.json")["status"] != "UNSAT_CERTIFIED"
    r.reply(p, s["request"]["id"], 0, "checkerzero")
    assert proc.wait() == 0
    s = r.read(p / "state.json")
    assert s["status"] == "UNSAT_UNCERTIFIED"
    source = next((p / "attempts").iterdir())
    proof_hash = r.sha(source / "proof.partial")
    (p / "RELEASE_CHECKER").touch()
    assert launch(p, True).wait() == 0
    assert r.read(p / "state.json")["status"] == "UNSAT_CERTIFIED"
    assert r.sha(source / "proof.partial") == proof_hash
    assert len(list((p / "attempts").glob("*/search_receipt.json"))) == 1
    record("zero_after_VERIFIED_waits_for_exit_and_resumes_checker_only")
    # Corrupted cache is not a corrupted authoritative transaction.
    p = new("cache")
    crash(p, "state_after_generation")
    (p / "state.json").write_bytes(b"torn cache")
    v.recover(p, True)
    assert any(f.read_bytes() == b"torn cache" for f in (p / "recovery").glob("*.state-before"))
    assert r.read(p / "state.json")["status"] == "STOPPED_UNRESOLVED"
    assert launch(p, True).wait() == 0
    record("generation_committed_cache_torn_recovered_and_preserved")
    p = new("write_failure")
    r.raw_atomic(p / "probe.json", {"old": True})
    old = state_hashes(p)
    os.environ["N1_TEST_WRITE_FAIL"] = "probe.json"
    try:
        try:
            r.raw_atomic(p / "probe.json", {"new": True})
            raise AssertionError("write fault not triggered")
        except OSError:
            pass
    finally:
        os.environ.pop("N1_TEST_WRITE_FAIL")
    assert all(r.sha(p / name) == digest for name, digest in old.items())
    assert r.read(p / "probe.json") == {"old": True}
    record("injected_pre_replace_failure_preserves_valid_state")
    p = new("bad_authoritative")
    latest = sorted((p / "states").glob("*.json"))[-1]
    latest.write_bytes(b"damaged authoritative generation")
    before = state_hashes(p)
    must_reject(lambda: v.recover(p, True))
    assert before == state_hashes(p)
    record("corrupt_authoritative_generation_refused_without_rollback")
    p = new("missing_end_cpu")
    crash(p, "search_after_wait4")
    v.recover(p, True)
    s = r.read(p / "state.json")
    assert s["status"] == "ACCOUNTING_INCOMPLETE"
    assert s["accounting_gaps"][0]["cpu_s"] is None
    assert launch(p, True).wait() != 0
    record("missing_wait4_receipt_never_zero_or_automatic_restart")
    # Real orphan test: only the known native child is asked to stop afterwards.
    clauses = []
    n, h = 22, 21
    for i in range(n):
        clauses.append([i*h+j+1 for j in range(h)])
    for j in range(h):
        for i in range(n):
            for k in range(i):
                clauses.append([-(i*h+j+1), -(k*h+j+1)])
    text = f"p cnf {n*h} {len(clauses)}\n"
    text += "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)
    p = new("live_orphan", text)
    crash(p, "search_after_identity")
    s = r.read(p / "state.json")
    assert v.alive(s["child"])
    before = state_hashes(p)
    must_reject(lambda: v.recover(p, True))
    assert before == state_hashes(p)
    d = p / "attempts" / s["active_attempt"]
    r.atomic(d / "STOP", {"explicit_test_cleanup": True})
    while v.alive(s["child"]):
        time.sleep(0.02)
    v.recover(p, True)
    assert not r.read(p / "state.json")["accounting_complete"]
    record("live_orphan_refused_then_cooperative_cleanup_gap_retained")
    # Budget and processed reply ids survive generation/cache fault recovery.
    p = new("transaction")
    s = r.read(p / "state.json")
    s["request"] = {"id": "testrequest", "generation": 1}
    r.atomic(p / "state.json", s)
    r.reply(p, "testrequest", 7, "once")
    script = ("import sys; from pathlib import Path; sys.path.insert(0," +
              repr(str(Path(r.__file__).parent)) + "); import runtime as r; p=Path(" +
              repr(str(p)) + "); r.service(p,r.read(p/'state.json'))")
    env = dict(os.environ, N1_TEST_FAULT="state_after_generation")
    assert subprocess.run([sys.executable, "-c", script], env=env).returncode == 91
    v.recover(p, True)
    s = r.read(p / "state.json")
    assert s["budget"] == 67 and s["replies"]["once"] == "ACCEPTED"
    r.service(p, s)
    assert r.read(p / "state.json")["budget"] == 67
    record("real_exit_after_reply_commit_no_duplicate_extension")
    report = {"complete": True, "tests": rows, "scope": "Linux cloud recovery controls",
              "N1_class_searches": 0, "production_approved": False}
    r.atomic(out / "TEST_RESULTS.json", report)
    print(json.dumps({"complete": True, "passed": len(rows)}), flush=True)


if __name__ == "__main__":
    main()
