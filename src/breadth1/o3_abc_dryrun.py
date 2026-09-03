#!/usr/bin/env python3
"""Final no-solver A/B/C dry-run for O3-BREADTH-1.

Includes an exhaustive solver-free CNF equivalence test for the new
Wallace/carry-save weighted-equality encoder on small cases.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MiniCNF:
    def __init__(self):
        self.cl = []
        self.n = 0
        self.names = []

    def var(self, name):
        self.n += 1
        self.names.append(name)
        return self.n

    def add(self, *lits):
        self.cl.append(list(lits))


def clause_satisfied(clause, assignment):
    return any(
        assignment[abs(lit)] == (lit > 0)
        for lit in clause
    )


def cnf_satisfied(cnf, bits):
    assignment = {
        index + 1: bool(bit)
        for index, bit in enumerate(bits)
    }
    return all(
        clause_satisfied(clause, assignment)
        for clause in cnf.cl
    )


def exhaustive_adder_selftest(abc):
    cases = [
        ((1, 1, 1), 2),
        ((1, 2, 3), 3),
        ((2, 3, 5), 5),
    ]
    checked_primary = 0

    for case_index, (weights, rhs) in enumerate(cases):
        cnf = MiniCNF()
        variables = [
            cnf.var("x%d" % i)
            for i in range(len(weights))
        ]
        abc.weighted_eq_wallace(
            cnf,
            list(zip(variables, weights)),
            rhs,
            "selftest_%d" % case_index,
        )

        primary_n = len(weights)
        aux_n = cnf.n - primary_n
        if aux_n > 14:
            raise AssertionError(
                "selftest unexpectedly large: %d aux vars" % aux_n
            )

        for primary_bits in itertools.product((0, 1), repeat=primary_n):
            expected = (
                sum(w * b for w, b in zip(weights, primary_bits))
                == rhs
            )
            exists = False

            for aux_bits in itertools.product((0, 1), repeat=aux_n):
                bits = primary_bits + aux_bits
                if cnf_satisfied(cnf, bits):
                    exists = True
                    break

            if exists != expected:
                raise AssertionError(
                    "Wallace CNF mismatch weights=%r rhs=%d primary=%r"
                    % (weights, rhs, primary_bits)
                )
            checked_primary += 1

    return checked_primary


def aggregate_pair_equations(core, comp):
    inside = set(comp)
    counter = Counter()
    rhs = 0
    for eq in core["pair_equations"]:
        i, j = eq["pair"]
        if i not in inside or j not in inside:
            continue
        rhs += eq["rhs"]
        for kind, key, weight in eq["terms"]:
            counter[(kind, tuple(key) if kind == "s" else int(key))] += weight
    return counter, rhs


def expected_m2_semantic(core, comp):
    inside = set(comp)
    candidate_set = set(map(tuple, core["candidate_edges"]))

    factor_to_pid = {}
    for item in core["products"]:
        a, b = map(tuple, item["factors"])
        key = (a, b) if a < b else (b, a)
        factor_to_pid[key] = item["id"]

    counter = Counter()
    vertices = list(comp)
    m = len(vertices)

    for ii in range(m):
        i = vertices[ii]
        for jj in range(ii + 1, m):
            j = vertices[jj]
            for k in range(core["n"]):
                if k in (i, j):
                    continue
                a = (i, k) if i < k else (k, i)
                b = (k, j) if k < j else (j, k)
                if a in candidate_set and b in candidate_set:
                    key = (a, b) if a < b else (b, a)
                    counter[("p", factor_to_pid[key])] += 1

    lset = set(map(tuple, core["L"]))
    for i in vertices:
        for j in vertices:
            if i >= j:
                continue
            edge = (i, j)
            if edge not in lset:
                counter[("s", edge)] += 9

    return counter, 3 * m * (m - 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generic-core", required=True)
    ap.add_argument("--abc-encode", required=True)
    ap.add_argument("--legacy-core", required=True)
    ap.add_argument("--legacy-encode", required=True)
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--summary", required=True)
    args = ap.parse_args()

    generic = load_module("generic_core", Path(args.generic_core))
    abc = load_module("abc_encode", Path(args.abc_encode))
    legacy_core = load_module("legacy_core", Path(args.legacy_core))
    legacy_encode = load_module("legacy_encode", Path(args.legacy_encode))

    adder_primary_checks = exhaustive_adder_selftest(abc)

    legacy_types = [p for p in legacy_core.all_types() if 4 not in p]
    assert len(legacy_types) == 103
    for part in legacy_types:
        core = legacy_core.make_core(part)
        old_cnf, old_sv = legacy_encode.cnf_from_core(
            core,
            lemma_triangle_eo=True,
        )
        a_cnf, a_sv, _ = abc.build_cnf(core, legacy_encode, "A")
        assert old_sv == a_sv
        assert old_cnf.n == a_cnf.n
        assert old_cnf.names == a_cnf.names
        assert old_cnf.cl == a_cnf.cl

    rows = []
    totals = Counter()
    by_tau = {}

    for tau in (6, 13, 20, 27):
        types = [p for p in generic.all_types(tau) if 4 not in p]
        by_tau[str(tau)] = Counter(types=len(types))

        for part in types:
            core = generic.make_core(tau, part)
            A, svA, metaA = abc.build_cnf(core, legacy_encode, "A")
            B, svB, metaB = abc.build_cnf(core, legacy_encode, "B")
            C, svC, metaC = abc.build_cnf(core, legacy_encode, "C")

            assert svA == svB == svC
            assert B.names[:A.n] == A.names
            assert C.names[:B.n] == B.names
            assert B.cl[:len(A.cl)] == A.cl
            assert C.cl[:len(B.cl)] == B.cl

            expected_eo = 30 * sum(m == 3 for m in part)
            assert metaA["eo_groups"] == expected_eo

            components = abc.cycle_components(core)
            cm_components = 0
            moment_equalities = 0

            for comp in components:
                if len(comp) < 5:
                    continue
                cm_components += 1

                aggregate, aggregate_rhs = aggregate_pair_equations(core, comp)
                expected, expected_rhs = expected_m2_semantic(core, comp)
                assert aggregate == expected
                assert aggregate_rhs == expected_rhs
                moment_equalities += 2

                assert all(
                    core["degree_targets"][str(v)] == 10
                    for v in comp
                )

            assert metaC["moment"]["components"] == cm_components
            assert metaC["moment"]["equalities"] == moment_equalities

            row = {
                "tau": tau,
                "cycle_type": ",".join(map(str, part)),
                "c3": sum(m == 3 for m in part),
                "cm_components": cm_components,
                "eo_groups": metaA["eo_groups"],
                "A_variables": A.n,
                "A_clauses": len(A.cl),
                "B_variables": B.n,
                "B_clauses": len(B.cl),
                "C_variables": C.n,
                "C_clauses": len(C.cl),
                "B_added_variables": B.n - A.n,
                "B_added_clauses": len(B.cl) - len(A.cl),
                "C_added_variables": C.n - B.n,
                "C_added_clauses": len(C.cl) - len(B.cl),
                "cm_constraints": metaB["cycle_local"]["constraints"],
                "moment_equalities": metaC["moment"]["equalities"],
            }
            rows.append(row)

            totals["types"] += 1
            totals["eo_groups"] += row["eo_groups"]
            totals["cm_constraints"] += row["cm_constraints"]
            totals["moment_equalities"] += row["moment_equalities"]
            totals["B_added_variables"] += row["B_added_variables"]
            totals["B_added_clauses"] += row["B_added_clauses"]
            totals["C_added_variables"] += row["C_added_variables"]
            totals["C_added_clauses"] += row["C_added_clauses"]

            for key in (
                "cm_constraints",
                "moment_equalities",
                "B_added_clauses",
                "C_added_clauses",
            ):
                by_tau[str(tau)][key] += row[key]

    assert totals["types"] == 139
    assert totals["eo_groups"] == 5280
    assert totals["cm_constraints"] == 13141

    tsv_path = Path(args.tsv)
    summary_path = Path(args.summary)
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with tsv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "format": "O3-BREADTH-1-ABC-DRYRUN-0.2",
        "scope": "CNF construction and symbolic redundancy audit; no SAT solver",
        "wallace_exhaustive_selftest": {
            "status": "PASS",
            "primary_assignments_checked": adder_primary_checks,
        },
        "tau6_baseline_A_exact": "PASS",
        "append_only_A_B_C": "PASS",
        "M2_symbolic_redundancy": "PASS",
        "M1_degree_sum_redundancy": "PASS",
        "totals": dict(totals),
        "by_tau": {k: dict(v) for k, v in by_tau.items()},
    }
    summary_path.write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print("O3_ABC_DRYRUN PASS")
    print(
        "WALLACE_EXHAUSTIVE_SELFTEST PASS primary_assignments=%d"
        % adder_primary_checks
    )
    print("TAU6_BASELINE_A_EXACT PASS types=103")
    print("APPEND_ONLY A<B<C PASS")
    print("M1_REDUNDANCY PASS")
    print("M2_SYMBOLIC_REDUNDANCY PASS")
    print("ALL_TYPES", totals["types"])
    print("EO_GROUPS", totals["eo_groups"])
    print("CM_CONSTRAINTS", totals["cm_constraints"])
    print("MOMENT_EQUALITIES", totals["moment_equalities"])
    print("B_ADDED_VARIABLES", totals["B_added_variables"])
    print("B_ADDED_CLAUSES", totals["B_added_clauses"])
    print("C_ADDED_VARIABLES", totals["C_added_variables"])
    print("C_ADDED_CLAUSES", totals["C_added_clauses"])

    for tau in ("6", "13", "20", "27"):
        item = by_tau[tau]
        print(
            "TAU",
            tau,
            "types",
            item["types"],
            "cm",
            item["cm_constraints"],
            "mom",
            item["moment_equalities"],
            "Bclauses",
            item["B_added_clauses"],
            "Cclauses",
            item["C_added_clauses"],
        )


if __name__ == "__main__":
    main()
