#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import random
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def upair(a, b):
    return (a, b) if a < b else (b, a)


def evaluate_pair_equation(core, equation, selected):
    products = {}
    for item in core["products"]:
        a, b = map(tuple, item["factors"])
        products[item["id"]] = int(a in selected and b in selected)

    total = 0
    for kind, key, weight in equation["terms"]:
        if kind == "p":
            total += weight * products[key]
        else:
            total += weight * int(tuple(key) in selected)
    return total


def direct_normalized_rhs(core, i, j):
    tset = set(core["T"])
    lset = set(map(tuple, core["L"]))
    nbr = {v: set() for v in range(core["n"])}
    for a, b in lset:
        nbr[a].add(b)
        nbr[b].add(a)
    ell = int(upair(i, j) in lset)
    cij = 2 * int(i in tset) + 2 * int(j in tset) + 1
    return 6 - 4 * len(nbr[i] & nbr[j]) - 2 * ell * cij


def q_matrix(core, selected):
    n = core["n"]
    tset = set(core["T"])
    lset = set(map(tuple, core["L"]))
    q = [[0] * n for _ in range(n)]
    for i in tset:
        q[i][i] = 2
    for a, b in lset:
        q[a][b] = q[b][a] = 2
    for a, b in selected:
        q[a][b] = q[b][a] = 1
    return q


def fixed_terms(core, i, j):
    tset = set(core["T"])
    lset = set(map(tuple, core["L"]))
    nbr = {v: set() for v in range(core["n"])}
    for a, b in lset:
        nbr[a].add(b)
        nbr[b].add(a)
    ell = int(upair(i, j) in lset)
    cij = 2 * int(i in tset) + 2 * int(j in tset) + 1
    return 4 * len(nbr[i] & nbr[j]) + 2 * ell * cij


def e2e_random_algebra(core, seed, rounds=12):
    rng = random.Random(seed)
    candidates = list(map(tuple, core["candidate_edges"]))
    total = 0
    for _ in range(rounds):
        selected = {edge for edge in candidates if rng.randrange(2)}
        q = q_matrix(core, selected)
        for equation in core["pair_equations"]:
            i, j = equation["pair"]
            direct = sum(q[i][k] * q[k][j] for k in range(core["n"])) + q[i][j]
            normalized = evaluate_pair_equation(core, equation, selected)
            if normalized != direct - fixed_terms(core, i, j):
                raise AssertionError(("LHS", core["T"], core["cycle_type"], [i, j]))
            expected_rhs = direct_normalized_rhs(core, i, j)
            if equation["rhs"] != expected_rhs:
                raise AssertionError(("RHS", core["T"], core["cycle_type"], [i, j]))
            total += 1
    return total


def semantic_signature(core, inverse=None):
    if inverse is None:
        inverse = {i: i for i in range(core["n"])}

    def mv(v):
        return inverse[v]

    def me(edge):
        return upair(mv(edge[0]), mv(edge[1]))

    product_factors = {}
    for item in core["products"]:
        a, b = map(tuple, item["factors"])
        aa, bb = me(a), me(b)
        product_factors[item["id"]] = tuple(sorted((aa, bb)))

    equations = []
    for equation in core["pair_equations"]:
        pair = me(tuple(equation["pair"]))
        terms = []
        for kind, key, weight in equation["terms"]:
            if kind == "s":
                terms.append(("s", me(tuple(key)), weight))
            else:
                terms.append(("p", product_factors[key], weight))
        equations.append((pair, equation["rhs"], tuple(sorted(terms, key=repr))))

    return {
        "T": tuple(sorted(mv(v) for v in core["T"])),
        "U": tuple(sorted(mv(v) for v in core["U"])),
        "L": tuple(sorted(me(tuple(edge)) for edge in core["L"])),
        "degree_targets": tuple(sorted(
            (mv(int(vertex)), target)
            for vertex, target in core["degree_targets"].items()
        )),
        "candidate_edges": tuple(sorted(
            me(tuple(edge)) for edge in core["candidate_edges"]
        )),
        "equations": tuple(sorted(equations, key=repr)),
    }


def relabelling_test(new, tau, part, seed):
    rng = random.Random(seed)
    base = new.make_core(tau, part)
    perm_list = list(range(new.N))
    rng.shuffle(perm_list)
    perm = {i: perm_list[i] for i in range(new.N)}
    inverse = {perm[i]: i for i in range(new.N)}

    T2 = {perm[i] for i in base["T"]}
    L2 = {upair(perm[a], perm[b]) for a, b in map(tuple, base["L"])}
    moved = new.make_core_from_structure(T2, L2, tuple(part))

    if semantic_signature(base) != semantic_signature(moved, inverse):
        raise AssertionError(("RELABEL", tau, part))

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-core", required=True)
    parser.add_argument("--legacy-core", required=True)
    args = parser.parse_args()

    new = load_module("o3_generic_core", Path(args.new_core))
    legacy = load_module("legacy_o3_core", Path(args.legacy_core))

    legacy_types = [part for part in legacy.all_types() if 4 not in part]
    assert len(legacy_types) == 103

    mismatches = []
    for part in legacy_types:
        old_core = legacy.make_core(part)
        new_core = new.make_core(6, part)
        if old_core != new_core:
            mismatches.append((
                part,
                old_core.get("sha256"),
                new_core.get("sha256"),
            ))

    if mismatches:
        print("TAU6_EXACT_REGRESSION FAIL", len(mismatches))
        print("FIRST_MISMATCH", mismatches[0])
        raise SystemExit(1)

    counts = {}
    hashes = set()
    total = 0
    for tau in (6, 13, 20, 27):
        types = [part for part in new.all_types(tau) if 4 not in part]
        counts[tau] = len(types)
        for part in types:
            core = new.make_core(tau, part)
            new.validate_basic(core)
            total += 1
            hashes.add(core["sha256"])

    assert counts == {6: 103, 13: 28, 20: 6, 27: 2}
    assert total == 139
    assert len(hashes) == 139

    representatives = {
        6: (27,),
        13: (20,),
        20: (13,),
        27: (6,),
    }
    e2e_pairs = {}
    relabel = {}
    for index, tau in enumerate((6, 13, 20, 27)):
        part = representatives[tau]
        core = new.make_core(tau, part)
        e2e_pairs[tau] = e2e_random_algebra(
            core,
            seed=0xC0990000 + tau,
            rounds=12,
        )
        relabel[tau] = relabelling_test(
            new,
            tau,
            part,
            seed=0xB1EAD000 + tau,
        )

    print("TAU6_EXACT_REGRESSION PASS types=103")
    print("ALL_TAU_BASIC PASS counts=%s total=%d unique_hashes=%d" % (
        counts,
        total,
        len(hashes),
    ))
    print("ALL_TAU_E2E_ALGEBRA PASS pairs=%s" % e2e_pairs)
    print("RELABEL_WLOG PASS tau=%s" % sorted(relabel))


if __name__ == "__main__":
    main()
