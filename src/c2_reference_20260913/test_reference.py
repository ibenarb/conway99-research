"""Independent finite SAT and graph controls for the reference encoder."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import tempfile

from c2_reference import CNF, Frame, add_matching, encode_base, reconstruct, verify_graph
from c2_reference import read_primary_model, sha256, write_json


def sat(clauses, assumptions=()):
    """Tiny independent DPLL, only for finite controls, not production search."""
    work = [tuple(c) for c in clauses] + [(x,) for x in assumptions]
    while True:
        if any(not c for c in work):
            return False
        if not work:
            return True
        unit = next((c[0] for c in work if len(c) == 1), None)
        if unit is None:
            x = work[0][0]
            return sat(work, (x,)) or sat(work, (-x,))
        work = [tuple(x for x in c if x != -unit) for c in work if unit not in c]


def truth(clauses, values):
    return all(any(values[abs(x)] == (x > 0) for x in clause) for clause in clauses)


def controls(output):
    counts = {"and_truth_assignments": 0, "ite_truth_assignments": 0,
              "weighted_projection_checks": 0, "rook_projection_checks": 0,
              "gate_clause_deletion_controls": 0}
    for kind in ("AND", "ITE"):
        c = CNF(retain=True)
        try:
            x, y, z = [c.variable() for _ in range(3)]
            result = c.conjunction(x, y) if kind == "AND" else c.select(x, y, z)
            for bits in itertools.product((False, True), repeat=c.variables):
                values = dict(enumerate(bits, 1))
                expected = (values[x] and values[y]) if kind == "AND" else (values[y] if values[x] else values[z])
                assert truth(c.saved, values) == (values[result] == expected)
                counts["and_truth_assignments" if kind == "AND" else "ite_truth_assignments"] += 1
            for omit in range(len(c.saved)):
                reduced = c.saved[:omit] + c.saved[omit+1:]
                assert any(truth(reduced, dict(enumerate(bits, 1))) and not truth(c.saved, dict(enumerate(bits, 1)))
                           for bits in itertools.product((False, True), repeat=c.variables))
                counts["gate_clause_deletion_controls"] += 1
        finally:
            c.close()
    for n in range(5):
        for weights in itertools.product((1, 2), repeat=n):
            for target in range(-1, sum(weights) + 3):
                c = CNF(retain=True)
                try:
                    vs = [c.variable() for _ in range(n)]
                    terms = [v for v, w in zip(vs, weights) for _ in range(w)] + [True, False]
                    c.exact(terms, target)
                    for bits in itertools.product((0, 1), repeat=n):
                        expected = sum(w*b for w, b in zip(weights, bits)) + 1 == target
                        assumptions = [v if b else -v for v, b in zip(vs, bits)]
                        assert sat(c.saved, assumptions) == expected, (weights, target, bits)
                        counts["weighted_projection_checks"] += 1
                finally:
                    c.close()
    rook_solution = None
    for matching in (False, True):
        c, f = CNF(retain=True), Frame(4)
        f.allocate(c)
        try:
            encode_base(c, f)
            if matching:
                before = c.variables, c.clauses
                add_matching(c, f)
                assert (c.variables, c.clauses) == before
            accepted = 0
            for bits in itertools.product((0, 1), repeat=len(f.map)):
                values = dict(enumerate(bits, 1))
                graph = reconstruct(f, values)
                expected = verify_graph(graph, 4)
                assert sat(c.saved, [v if b else -v for v, b in values.items()]) == expected
                counts["rook_projection_checks"] += 1
                accepted += int(expected)
                if expected:
                    rook_solution = graph
            assert accepted == 1
        finally:
            c.close()
    # A separate rook construction: positive graph check and a one-edge corruption.
    vertices = list(itertools.product(range(3), repeat=2))
    rook = [[int(a != b and (a[0] == b[0] or a[1] == b[1])) for b in vertices] for a in vertices]
    assert verify_graph(rook, 4)
    rook[0][1] = rook[1][0] = 1 - rook[0][1]
    assert not verify_graph(rook, 4)
    with tempfile.TemporaryDirectory() as temporary:
        p = Path(temporary) / "model.txt"
        p.write_text("s SATISFIABLE\nv 1 2 0\n")
        assert read_primary_model(p, 2) == {1: True, 2: True}
        for bad in ("v 1 0\n", "v 1 -1 2 0\n"):
            p.write_text(bad)
            try:
                read_primary_model(p, 2)
            except ValueError:
                pass
            else:
                raise AssertionError("Invalid model accepted")
    report = {"status": "C2_REFERENCE_CONTROLS_PASS", "version": "1.0.0", "counts": counts,
              "independent_DPLL": True, "independent_rook_and_negative_graph": True,
              "incomplete_and_contradictory_models_rejected": True,
              "reference_sha256": sha256(Path(__file__).with_name("c2_reference.py")),
              "test_sha256": sha256(__file__),
              "scope": "Finite controls plus written encoder induction; no Conway99 UNSAT proof."}
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, report)
    print(json.dumps(report))


def audit_generated(directory, output):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    variable_map = json.loads((directory / "variables.json").read_text())
    assert sha256(directory / "variables.json") == manifest["variables_sha256"]
    assert len(variable_map["primary_variables"]) == manifest["primary_variables"]
    assert [r[0] for r in variable_map["primary_variables"]] == list(range(1, manifest["primary_variables"] + 1))
    for name in ("baseline", "matching"):
        p = directory / (name + ".cnf")
        assert sha256(p) == manifest[name]["sha256"]
        assert p.stat().st_size == manifest[name]["bytes"]
        with p.open() as stream:
            head = stream.readline().split()
            assert head[:2] == ["p", "cnf"]
            nv, nc = map(int, head[2:])
            assert (nv, nc) == (manifest[name]["variables"], manifest[name]["clauses"])
            count = 0
            for line in stream:
                literals = list(map(int, line.split()))
                assert literals and literals[-1] == 0
                assert all(0 < abs(x) <= nv for x in literals[:-1])
                count += 1
            assert count == nc
    with (directory / "baseline.cnf").open("rb") as base, (directory / "matching.cnf").open("rb") as extra:
        base.readline()
        extra.readline()
        for line in base:
            assert extra.readline() == line
    report = {"status": "C2_DIMACS_AND_PREFIX_PASS", "k": manifest["k"],
              "baseline_sha256": manifest["baseline"]["sha256"],
              "matching_sha256": manifest["matching"]["sha256"],
              "scope": "DIMACS syntax, hashes and exact clause-prefix check; not a satisfiability result."}
    write_json(output, report)
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--audit-generated", type=Path)
    args = parser.parse_args()
    if args.audit_generated:
        audit_generated(args.audit_generated, args.out)
    else:
        controls(args.out)
