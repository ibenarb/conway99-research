"""Small N1 controls only; no 99-vertex class search."""
import argparse
import copy
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import bind_n1 as b
import n1_check as d
import runtime as r
import recovery as recovery


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--worker", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    out.mkdir(exist_ok=False)
    rows = []
    def record(name, **detail):
        rows.append(dict(test=name, passed=True, **detail))
        print(name, "PASS", flush=True)
    def reject(fn):
        try:
            fn()
        except (ValueError, KeyError, TypeError):
            return
        raise AssertionError("invalid data accepted")
    def launch(root, action="run", env=None):
        log = (root / ("supervisor-" + action + ".log")).open("ab")
        p = subprocess.Popen([sys.executable, r.__file__, action, str(root)],
                             stdout=log, stderr=subprocess.STDOUT, env=env)
        log.close()
        return p
    # Derive the 3x3 rook control through actual graph/border adjacency,
    # independently of encoder labels_for/fixed_edges/decode/check.
    vertices = list(itertools.product(range(3), repeat=2))
    adjacent = lambda x, y: x != y and (x[0] == y[0] or x[1] == y[1])
    border = [(0,1),(1,0),(0,2),(2,0)]
    outside = [v for v in vertices if v != (0,0) and not adjacent(v,(0,0))]
    mapping = {tuple(i for i,w in enumerate(border) if adjacent(v,w)): v for v in outside}
    labels = [(i,j) for i in range(4) for j in range(i+1,4) if j-i != 2]
    h = [mapping[p] for p in labels]
    matrix = [[int(adjacent(u,v)) for v in h] for u in h]
    spec = {"kind":"control","root_id":"3x3-rook","class_id":0,
            "m":2,"anchor":0,"rows":{"0":[v for v in range(4) if matrix[0][v]]},
            "matching":[]}
    prepared = out / "prepared"
    binding = b.prepare(spec, prepared)
    assert b.verify_regeneration(binding, prepared / "input.cnf")["status"] == "EXACT_N1_BINDING_VERIFIED"
    record("exact_CNF_regeneration_and_mapping_binding")
    root = out / "bound_run"
    r.init(root, prepared / "input.cnf", a.worker, a.checker, 60, prepared / "binding.json")
    assert launch(root).wait() == 0
    state = r.read(root / "state.json")
    assert state["status"] == "SAT_N1_VERIFIED"
    attempt = root / "attempts" / state["attempts"][0]["id"]
    evidence = r.read(attempt / "N1_WITNESS.json")
    assert evidence["matrix"] == matrix and not evidence["check"]["SRG_claim"]
    record("native_solver_CNF_and_independent_N1_witness")
    count = len(list((root / "attempts").iterdir()))
    recovery.recover(root, True)
    assert launch(root, "resume").wait() == 0
    assert len(list((root / "attempts").iterdir())) == count
    record("recovery_revalidates_N1_without_new_search")
    # No encoder import in direct validation, even under python -O.
    script = ("import sys; from pathlib import Path; sys.path.insert(0," +
              repr(str(Path(d.__file__).parent)) +
              "); import n1_check as d; b=d.load(" + repr(str(prepared / "binding.json")) +
              "); d.decode_and_check(b,Path(" + repr(str(prepared / "input.cnf")) +
              "),Path(" + repr(str(attempt / "model.txt")) +
              "));\nif 'pysat' in sys.modules or 'n1_pinned_encoder' in sys.modules:\n    raise RuntimeError('encoder imported')")
    assert subprocess.run([sys.executable, "-O", "-c", script]).returncode == 0
    record("independent_checker_without_encoder_or_PySAT_import")
    # Exhaust all free edge settings and check against independently derived rook matrix.
    free = binding["edge_map"]
    accepted = []
    for bits in itertools.product((0,1), repeat=len(free)):
        candidate = copy.deepcopy(matrix)
        for (u,v,lit), bit in zip(free,bits):
            candidate[u][v] = candidate[v][u] = bit
        try:
            d.check_matrix(spec, candidate)
            valid = True
        except ValueError:
            valid = False
        assert valid == (candidate == matrix)
        accepted.append(valid)
    assert len(accepted) == 4 and sum(accepted) == 1
    record("four_edge_settings_exactly_one_valid", cases=4)
    for label, mutation in (
        ("diagonal", lambda x: x[0].__setitem__(0,1)),
        ("asymmetry", lambda x: x[0].__setitem__(1,1-x[0][1])),
        ("boolean_bit", lambda x: x[0].__setitem__(0,False)),
    ):
        changed = copy.deepcopy(matrix)
        mutation(changed)
        reject(lambda: d.check_matrix(spec,changed))
    record("damaged_matrix_structure_rejected")
    wrong = copy.deepcopy(binding)
    wrong["edge_map"][0][2] = wrong["edge_map"][1][2]
    reject(lambda: b.verify_regeneration(wrong,prepared/"input.cnf"))
    wrong = copy.deepcopy(binding)
    wrong["spec"]["rows"]["0"].append(wrong["spec"]["rows"]["0"][0])
    reject(lambda: b.verify_regeneration(wrong,prepared/"input.cnf"))
    wrong = copy.deepcopy(binding)
    wrong["spec"]["matching"] = [[1,2],[1,2]]
    reject(lambda: b.verify_regeneration(wrong,prepared/"input.cnf"))
    record("wrong_mapping_duplicate_rows_and_matching_rejected")
    # Self-consistent replacement hashes do not bypass exact CNF regeneration.
    changed_cnf = out / "changed.cnf"
    text = (prepared / "input.cnf").read_text().splitlines()
    text[-1] = "0"
    changed_cnf.write_text("\n".join(text)+"\n")
    wrong = copy.deepcopy(binding)
    wrong["cnf_sha256"] = d.digest(changed_cnf)
    reject(lambda: b.verify_regeneration(wrong,changed_cnf))
    record("modified_CNF_with_updated_hash_rejected_by_regeneration")
    changed_model = out / "missing.model"
    vals = (attempt / "model.txt").read_text().split()
    changed_model.write_text(" ".join(vals[1:])+"\n")
    reject(lambda: d.decode_and_check(binding,prepared/"input.cnf",changed_model))
    record("incomplete_SAT_assignment_rejected")
    binding_bytes = (root/"binding.json").read_bytes()
    (root/"binding.json").write_bytes(binding_bytes+b" ")
    reject(lambda: recovery.recover(root, True))
    (root/"binding.json").write_bytes(binding_bytes)
    record("binding_change_detected_before_resume")
    # Crash after search receipt precedes decoded witness persistence.
    crashroot = out/"crash_bound"
    r.init(crashroot,prepared/"input.cnf",a.worker,a.checker,60,prepared/"binding.json")
    (crashroot/"ALLOW_TEST_FAULTS").touch()
    env=dict(os.environ,N1_TEST_FAULT="search_after_receipt")
    assert launch(crashroot,env=env).wait()==91
    assert not list((crashroot/"attempts").glob("*/N1_WITNESS.json"))
    plan=recovery.recover(crashroot,True)
    assert plan["proposed_status"]=="SAT_N1_VERIFIED"
    witness=next(iter(plan["inventory"]["n1_evidence"].values()))
    assert witness["matrix"]==matrix
    assert launch(crashroot,"resume").wait()==0
    assert len(list((crashroot/"attempts").iterdir()))==1
    record("crash_recovery_reconstructs_and_saves_independent_N1_evidence")
    report={"complete":True,"tests":rows,"scope":"m=2 rook controls only",
            "N1_99_class_searches":0,"production_approved":False,
            "unchecked_99_catalog_identity":True}
    r.atomic(out/"TEST_RESULTS.json",report)
    print(json.dumps({"passed":len(rows),"complete":True}),flush=True)


if __name__=="__main__":
    main()
