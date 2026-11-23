"""Independent exact checking of the referee's supplied genus and atlas certificates.

Does not import genus_lib or the original search. PARI is the common arithmetic
backend for isometry, automorphism and exhaustive short-vector enumeration.
This checks finite certificates; the theoretical mass formula is a separate
mathematical dependency. No floating-point LP decision is used.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import hashlib
import itertools
import json
import sys
import time

import numpy as np
from cypari2 import Pari

BASE = Path(__file__).resolve().parent
P = Pari()
P.allocatemem(1500000000, silent=True)
START = time.time()
SMOKE = "--smoke" in sys.argv
CLASSES = json.loads((BASE / "genus_classes.json").read_text())
CERTS = json.loads((BASE / "genus_farkas.json").read_text())
REFERENCE = json.loads((BASE / "genus_atlas.json").read_text())
CERT_BY_KEY = {(int(c["cls"]), int(c["vertex"])): c for c in CERTS}
assert len(CERT_BY_KEY) == len(CERTS) == 46


def pari_matrix(rows):
    return P.matrix(len(rows), len(rows[0]), [int(x) for row in rows for x in row])


def exact_integer_matrix(matrix):
    nr, nc = map(int, P.matsize(matrix))
    answer = []
    for i in range(nr):
        row = []
        for j in range(nc):
            assert P.denominator(matrix[i, j]) == 1
            row.append(int(matrix[i, j]))
        answer.append(row)
    return answer


def norm(vector, gram):
    return sum(int(vector[i]) * int(gram[i][j]) * int(vector[j])
               for i in range(15) for j in range(15))


def short_lines(gram, bound):
    result = P.qfminim(pari_matrix(gram), bound, None, 2)
    vectors = result[2]
    nr, nc = map(int, P.matsize(vectors))
    if nc == 0:
        assert int(result[0]) == 0
        return []
    assert nr == 15
    answer = [tuple(int(vectors[i, j]) for i in range(15)) for j in range(nc)]
    vector_set = set(answer)
    assert len(answer) == len(vector_set)
    assert all(0 < norm(v, gram) <= bound for v in answer)
    assert not any(tuple(-x for x in v) in vector_set for v in answer)
    assert int(result[0]) == 2 * len(answer)
    return answer


def quotient_map(gram2inverse):
    # Gauss-Jordan on bit rows; free coordinate order is pinned for the
    # supplied certificates, but kernel membership and rank are checked.
    rows = [sum((int(gram2inverse[i][j]) & 1) << i for i in range(15))
            for j in range(15)]
    pivots = []
    for column in range(15):
        found = next((i for i in range(len(pivots), 15)
                      if rows[i] & (1 << column)), None)
        if found is None:
            continue
        index = len(pivots)
        rows[index], rows[found] = rows[found], rows[index]
        for i in range(15):
            if i != index and rows[i] & (1 << column):
                rows[i] ^= rows[index]
        pivots.append(column)
    assert len(pivots) == 8
    kernel = []
    for free in range(15):
        if free in pivots:
            continue
        bits = 1 << free
        for index, pivot in enumerate(pivots):
            if rows[index] & (1 << free):
                bits |= 1 << pivot
        kernel.append(tuple((bits >> i) & 1 for i in range(15)))
    assert len(kernel) == 7
    assert all(sum(v[i] * gram2inverse[i][j] for i in range(15)) % 2 == 0
               for v in kernel for j in range(15))

    def project(vector):
        return tuple(sum(a * int(b) for a, b in zip(row, vector)) % 2
                     for row in kernel)
    return project


def find_frame(units, metric):
    adjacency = []
    for u in units:
        adjacency.append({j for j, v in enumerate(units)
                          if sum(u[a] * metric[a][b] * v[b]
                                 for a in range(15) for b in range(15)) == 0})

    def visit(selected, candidates):
        if len(selected) == 7:
            return selected
        if len(selected) + len(candidates) < 7:
            return None
        for j in sorted(candidates):
            result = visit(selected + [j],
                           {k for k in candidates if k > j} & adjacency[j])
            if result is not None:
                return result
        return None

    indices = visit([], set(range(len(units))))
    assert indices is not None
    return [list(units[j]) for j in indices]


def atlas_check(ci, gram, metric):
    project = quotient_map(metric)
    representatives = {}
    for vector in itertools.product((0, 1), repeat=15):
        representatives.setdefault(project(vector), vector)
        if len(representatives) == 128:
            break
    assert len(representatives) == 128
    quadratic = {key: norm(v, gram) % 4 for key, v in representatives.items()}

    def bilinear(k, l):
        u, v = representatives[k], representatives[l]
        return sum(u[i] * gram[i][j] * v[j]
                   for i in range(15) for j in range(15)) % 2

    # Complete generator checks prove q is well defined on the quotient.
    assert all(metric[i][i] % 2 == 0 for i in range(15))
    assert all(norm([metric[i][j] for i in range(15)], gram) % 4 == 0
               for j in range(15))
    edges = [k for k in representatives if quadratic[k] == 2]
    assert len(edges) == 28
    adjacent = {k: {l for l in edges if l != k and bilinear(k, l)} for k in edges}
    assert all(len(v) == 12 for v in adjacent.values())
    cliques = []

    def extend(chosen, candidates):
        if len(chosen) == 7:
            cliques.append(frozenset(chosen))
            return
        if len(chosen) + len(candidates) < 7:
            return
        for x in sorted(candidates):
            extend(chosen + [x], {y for y in candidates if y > x} & adjacent[x])

    extend([], set(edges))
    vertices = sorted(set(cliques), key=sorted)
    assert len(vertices) == 8
    ends = {edge: tuple(j for j, vertex in enumerate(vertices) if edge in vertex)
            for edge in edges}
    assert set(ends.values()) == set(itertools.combinations(range(8), 2))
    characteristic = [k for k in representatives
                      if all(bilinear(k, l) == quadratic[l] % 2 for l in representatives)]
    assert len(characteristic) == 1
    characteristic = characteristic[0]
    roots = [v for v in short_lines(gram, 2) if norm(v, gram) == 2]
    root_counts = [sum(j in ends[project(v)] for v in roots) for j in range(8)]
    dual_units = [v for v in short_lines(metric, 2) if norm(v, metric) == 2]
    frame = find_frame(dual_units, metric)
    norm5 = [v for v in short_lines(gram, 5) if norm(v, gram) == 5]
    labels = [project(v) for v in norm5]
    # Coordinate products are integral pairings between L and L*.
    max_v = max(abs(x) for v in norm5 for x in v)
    max_u = max(abs(x) for v in dual_units for x in v)
    assert 15 * max_v * max_u < 2 ** 62
    pairings = np.abs(np.array(norm5, dtype=np.int64) @
                      np.array(dual_units, dtype=np.int64).T)
    admissible = [i for i in range(len(norm5)) if int(pairings[i].max()) <= 1]
    geometries = []
    for vertex in range(8):
        required = [tuple(a ^ b for a, b in zip(characteristic, edge))
                    for edge in edges if vertex not in ends[edge]]
        assert len(set(required)) == 21
        assert all(quadratic[k] == 1 for k in required)
        buckets = [[i for i in admissible if labels[i] == k] for k in required]
        key = (ci, vertex)
        record = {"vertex": vertex, "root_lines": root_counts[vertex]}
        if any(not bucket for bucket in buckets):
            assert key not in CERT_BY_KEY
            record["status"] = "EMPTY_REQUIRED_CLASS"
        elif key in CERT_BY_KEY:
            cert = CERT_BY_KEY[key]
            y = [int(x) for x in cert["y"]]
            assert len(y) == 21 + len(dual_units)
            value = 2 * sum(y[:21]) + 14 * sum(y[21:])
            assert value > 0 and value == int(cert["value"])
            maximum = None
            for label_index, bucket in enumerate(buckets):
                for index in bucket:
                    dot = y[label_index] + sum(y[21 + u] for u in range(len(dual_units))
                                              if pairings[index, u])
                    assert dot <= 0
                    maximum = dot if maximum is None else max(maximum, dot)
            record.update(status="EXACT_FARKAS_EXCLUSION", rhs_value=value,
                          maximum_column_value=maximum)
        else:
            record["status"] = "RETAINED_NOT_EXCLUDED"
        reference_status = REFERENCE[ci]["geo"][vertex]["status"]
        expected = {"empty-domain": "EMPTY_REQUIRED_CLASS",
                    "lp-infeasible": "EXACT_FARKAS_EXCLUSION",
                    "lp-feasible": "RETAINED_NOT_EXCLUDED"}[reference_status]
        assert record["status"] == expected
        assert root_counts[vertex] == REFERENCE[ci]["geo"][vertex]["roots"]
        geometries.append(record)
    return {"class": ci, "dual_unit_lines": len(dual_units), "seven_unit_frame": frame,
            "norm5_lines": len(norm5), "admissible_lines": len(admissible),
            "geometries": geometries}


def main():
    assert len(CLASSES) == 31
    records = []
    checked_grams = []
    mass = Fraction(0)
    pair_count = 0
    for ci, supplied in enumerate(CLASSES):
        gram = supplied["gram"]
        assert len(gram) == 15 and all(len(row) == 15 for row in gram)
        assert all(gram[i][j] == gram[j][i] for i in range(15) for j in range(15))
        matrix = pari_matrix(gram)
        assert int(P.matdet(matrix)) == 256
        for order in range(1, 16):
            assert P.matdet(pari_matrix([r[:order] for r in gram[:order]])) > 0
        metric = exact_integer_matrix(2 * matrix ** -1)
        assert all(metric[i][i] % 2 == 0 for i in range(15))
        automorphisms = int(P.qfauto(matrix)[0])
        assert automorphisms == int(supplied["aut"])
        for previous in checked_grams:
            assert P.qfisom(previous, matrix) == 0
            pair_count += 1
        checked_grams.append(matrix)
        mass += Fraction(1, automorphisms)
        rec = atlas_check(ci, gram, metric)
        rec["automorphism_order"] = automorphisms
        records.append(rec)
        print(json.dumps({"class": ci, "automorphisms": automorphisms,
                          "pairwise_nonisometry_checks": pair_count,
                          "atlas_counts": dict(Counter(g["status"] for g in rec["geometries"])),
                          "elapsed": time.time() - START}), flush=True)
        if SMOKE:
            break
    counts = Counter(g["status"] for rec in records for g in rec["geometries"])
    if not SMOKE:
        assert pair_count == 465
        assert mass == Fraction(116980081, 898948399104000)
        assert mass == Fraction(3876193035, 2295) * Fraction(29713, 385648863215616000)
        assert counts == {"EMPTY_REQUIRED_CLASS": 122, "EXACT_FARKAS_EXCLUSION": 46,
                          "RETAINED_NOT_EXCLUDED": 80}
        survivors = [r for r in records if any(g["status"] == "RETAINED_NOT_EXCLUDED"
                                             for g in r["geometries"])]
        assert len(survivors) == 10
        assert all(all(g["status"] == "RETAINED_NOT_EXCLUDED" for g in r["geometries"])
                   for r in survivors)
        rootless = [r for r in survivors if all(g["root_lines"] == 0 for g in r["geometries"])]
        assert len(rootless) == 1
        assert all(all(g["root_lines"] > 0 for g in r["geometries"])
                   for r in survivors if r not in rootless)
    output = {"status": "SMOKE_PASS" if SMOKE else "FINITE_GENUS_CERTIFICATE_CHECKS_PASS",
              "scope": "Finite certificates only; genus membership and mass theorem remain mathematical dependencies.",
              "classes_checked": len(records), "nonisometry_pairs": pair_count,
              "mass": str(mass), "counts": dict(counts), "classes": records,
              "elapsed": time.time() - START,
              "inputs": {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest()
                         for name in ("genus_classes.json", "genus_farkas.json", "genus_atlas.json")},
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    target = BASE / ("smoke_result_v2.json" if SMOKE else "finite_result_v2.json")
    with target.open("x") as file:
        json.dump(output, file, indent=4)
    print(output["status"], flush=True)


if __name__ == "__main__":
    main()
