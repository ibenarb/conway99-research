"""Small real-process acceptance tests; never launches an N1 class."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
import runtime as r


def wait_state(root, predicate, proc):
    announced = time.monotonic()
    while True:
        s = r.read(root / "state.json")
        if predicate(s):
            return s
        if proc.poll() is not None:
            raise AssertionError(("supervisor ended", proc.returncode, s))
        if time.monotonic() - announced >= 30:
            print("Still waiting; no automatic time abort:", s["status"], flush=True)
            announced = time.monotonic()
        time.sleep(0.03)


def launch(root, resume=False):
    log = (root / ("supervisor-" + str(time.time_ns()) + ".log")).open("wb")
    p = subprocess.Popen([sys.executable, r.__file__,
                          "resume" if resume else "run", str(root)],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    log.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--worker", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    out.mkdir(exist_ok=False)
    results = []
    def record(name, **details):
        results.append({"test": name, "passed": True, **details})
        print(name, "PASS", flush=True)
    def new(name, text, budget=60):
        cnf = out / (name + ".cnf")
        cnf.write_text(text)
        root = out / name
        r.init(root, cnf, a.worker, a.checker, budget)
        return root
    sat = new("sat", "p cnf 3 2\n1 0\n-1 2 0\n")
    p = launch(sat)
    assert p.wait() == 0
    s = r.read(sat / "state.json")
    assert s["status"] == "SAT_CNF_VERIFIED"
    record("SAT_full_model_including_unused_variable", cpu=s["cpu_completed"])
    old = len(s["attempts"])
    assert launch(sat, True).wait() == 0
    assert len(r.read(sat / "state.json")["attempts"]) == old
    record("completed_result_reused_without_new_search")
    unsat = new("unsat", "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n")
    assert launch(unsat).wait() == 0
    u = r.read(unsat / "state.json")
    assert u["status"] == "UNSAT_CERTIFIED"
    d = unsat / "attempts" / u["attempts"][0]["id"]
    final = r.verify_attempt(d, u["attempts"][0])
    search, check = r.read(d / "search_receipt.json"), r.read(d / "check_receipt.json")
    assert abs(u["cpu_completed"] - search["cpu_s"] - check["cpu_s"]) < 1e-12
    record("real_CaDiCaL_DRAT_external_check_and_disjoint_wait4", cpu=u["cpu_completed"])
    bad = out / "bad.drat"
    bad.write_text("0\n")
    forged = subprocess.run([str(a.checker), str(sat / "input.cnf"), str(bad), "-O"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert b"s VERIFIED" not in forged.stdout
    (out / "forged.log").write_bytes(forged.stdout)
    record("forged_proof_rejected_by_real_checker")
    model = out / "bad.model"
    model.write_text("-1 -2 3 0\n")
    assert not r.cnf_model_ok(sat / "input.cnf", model)
    record("damaged_SAT_model_rejected")
    # Pigeonhole is a synthetic control CNF, not a ROOT8105 search.
    pigeons, holes = 22, 21
    clauses = []
    var = lambda p, h: p * holes + h + 1
    for p0 in range(pigeons):
        clauses.append([var(p0, h) for h in range(holes)])
    for h in range(holes):
        for p0 in range(pigeons):
            for p1 in range(p0):
                clauses.append([-var(p0, h), -var(p1, h)])
    text = f"p cnf {pigeons * holes} {len(clauses)}\n"
    text += "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)
    root = new("stop_resume", text, 0.01)
    p = launch(root)
    s = wait_state(root, lambda x: x["request"] is not None, p)
    ident, cpu, req = s["child"], s["live_cpu"], s["request"]["id"]
    s = wait_state(root, lambda x: x["live_cpu"] > cpu + 0.12, p)
    assert s["child"] == ident and s["budget"] == 0.01
    record("EOF_and_no_reply_continue_same_real_solver")
    competitor = launch(root)
    assert competitor.wait() != 0 and p.poll() is None
    record("second_supervisor_rejected_without_disturbing_child")
    r.reply(root, "stale", 7, "stale")
    wait_state(root, lambda x: "stale" in x["replies"], p)
    assert r.read(root / "state.json")["budget"] == 0.01
    record("stale_reply_no_budget_effect")
    r.reply(root, req, 1, "extend")
    r.reply(root, req, 1, "extend")
    s = wait_state(root, lambda x: "extend" in x["replies"], p)
    assert s["budget"] == 1.01 and s["child"] == ident
    record("duplicate_extension_exactly_once")
    # Simulate lost acknowledgement by redelivering the same saved response.
    r.reply(root, req, 1, "extend")
    s = wait_state(root, lambda x: x["request"] is not None, p)
    assert s["budget"] == 1.01
    r.reply(root, s["request"]["id"], 0, "stop")
    assert p.wait() == 0
    s = r.read(root / "state.json")
    assert s["status"] == "STOPPED_UNRESOLVED" and s["accounting_complete"]
    old_cpu = s["cpu_completed"]
    old_id = s["attempts"][0]["id"]
    old_dir = root / "attempts" / old_id
    old_hashes = {f.name: r.sha(f) for f in old_dir.iterdir()}
    record("repeated_budget_then_cooperative_zero_with_wait4", cpu=old_cpu)
    p = launch(root, True)
    s = wait_state(root, lambda x: x["request"] is not None, p)
    assert s["active_attempt"] != old_id and s["cpu_completed"] == old_cpu
    r.reply(root, s["request"]["id"], 0, "stopresume")
    assert p.wait() == 0
    s = r.read(root / "state.json")
    assert len(s["attempts"]) == 2 and s["cpu_completed"] > old_cpu
    assert old_hashes == {f.name: r.sha(f) for f in old_dir.iterdir()}
    record("new_attempt_preserves_partial_proof_and_cumulative_CPU")
    r.atomic(root / "state.json", {**s, "status": "RUNNING", "child": ident})
    assert launch(root, True).wait() != 0
    record("unclosed_session_refuses_automatic_restart")
    r.atomic(root / "state.json", s)
    proof = d / "proof.partial"
    original = proof.read_bytes()
    proof.write_bytes(original + b"x")
    assert launch(unsat, True).wait() != 0
    proof.write_bytes(original)
    record("sealed_artifact_corruption_detected")
    # Pre-existing stop must be honored during a large import, before solve().
    import_dir = out / "import_stop"
    import_dir.mkdir()
    import_cnf = out / "import.cnf"
    import_cnf.write_text("p cnf 1 200000\n" + "1 0\n" * 200000)
    (import_dir / "STOP").write_text("requested")
    imported = subprocess.run([str(a.worker), str(import_cnf)], cwd=import_dir,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (import_dir / "worker.log").write_bytes(imported.stdout)
    assert imported.returncode == 0
    assert json.loads((import_dir / "worker.json").read_text())["stop_seen"]
    record("zero_during_import_preserves_partial_file")
    # Invalid replies and damaged envelopes are rejected without mutation.
    before = r.sha(root / "state.json")
    try:
        r.reply(root, "invalid", -1)
        raise AssertionError("negative reply accepted")
    except ValueError:
        pass
    assert r.sha(root / "state.json") == before
    record("negative_reply_no_mutation")
    damaged = out / "damaged.json"
    r.atomic(damaged, {"x": 1})
    envelope = json.loads(damaged.read_text())
    envelope["data"]["x"] = 2
    damaged.write_text(json.dumps(envelope))
    try:
        r.read(damaged)
        raise AssertionError("damaged checkpoint accepted")
    except ValueError:
        pass
    record("damaged_checkpoint_rejected")
    report = {"complete": True, "scope": "Linux cloud synthetic controls only",
              "tests": results, "N1_class_searches": 0,
              "worker_sha256": r.sha(a.worker), "checker_sha256": r.sha(a.checker),
              "limitations": ["No Windows/WSL test", "No N1 decoded witness integration",
                             "No crash/power-loss end-accounting recovery",
                             "No production release"]}
    r.atomic(out / "TEST_RESULTS.json", report)
    print(json.dumps({"passed": len(results), "complete": True}), flush=True)


if __name__ == "__main__":
    main()
