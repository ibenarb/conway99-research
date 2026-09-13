#!/usr/bin/env python3
"""Independently verify every stored negative principal minor in a V4 audit.

Reconstructs the target Gram matrix using explicit combinatorial formulas,
not the matrix-multiplication builder. Recomputes determinants with a separate
row-pivoting elimination. Also checks a deterministic sample by rational
Gaussian elimination and exercises a deliberately corrupted certificate.
No external packages, SAT solvers, or project writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import o3_v4_preflight as core


def combinatorial_gram(case: Any, neighbors: Any) -> list[list[int]]:
    bits, s = case["attached_T_bits"], case["s"]
    adjacency = [set(ns) for ns in neighbors]
    m = [[0] * 14 for _ in range(14)]
    for i in range(12):
        x, y = bits[i]
        m[i][i] = 12 - x - y
        for j in range(i + 1, 12):
            common = len(adjacency[i] & adjacency[j])
            target = 3 if i // 4 == j // 4 else 6
            value = target - int(j in adjacency[i]) - common - x * bits[j][0] - y * bits[j][1]
            m[i][j] = m[j][i] = value
        for b in range(2):
            value = 6 - 3 * bits[i][b] - s * bits[i][1 - b] - sum(bits[v][b] for v in neighbors[i])
            m[i][12 + b] = m[12 + b][i] = value
    m[12][12] = m[13][13] = 6 - s
    m[12][13] = m[13][12] = 6 - 5 * s - sum(x * y for x, y in bits)
    return m


def determinant_integer(matrix: list[list[int]]) -> int:
    """Row-pivoting fraction-free Gaussian elimination; no symmetric updates."""
    a, previous, sign = [row[:] for row in matrix], 1, 1
    n = len(a)
    if n == 0:
        return 1
    for k in range(n - 1):
        row = next((i for i in range(k, n) if a[i][k]), None)
        if row is None:
            return 0
        if row != k:
            a[k], a[row] = a[row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                value = pivot * a[i][j] - a[i][k] * a[k][j]
                core.require(value % previous == 0, "Verifier exact division failed")
                a[i][j] = value // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def determinant_rational(matrix: list[list[int]]) -> int:
    a = [[Fraction(x) for x in row] for row in matrix]
    result = Fraction(1)
    for k in range(len(a)):
        row = next((i for i in range(k, len(a)) if a[i][k]), None)
        if row is None:
            return 0
        if row != k:
            a[k], a[row] = a[row], a[k]
            result = -result
        pivot = a[k][k]
        result *= pivot
        for i in range(k + 1, len(a)):
            factor = a[i][k] / pivot
            for j in range(k + 1, len(a)):
                a[i][j] -= factor * a[k][j]
    core.require(result.denominator == 1, "Nonintegral rational determinant")
    return result.numerator


def validate(matrix: Any, witness: Any, rational: bool = False) -> None:
    indices = witness["indices"]
    core.require(len(set(indices)) == len(indices) and all(0 <= i < 14 for i in indices),
                 "Invalid principal minor indices")
    principal = [[matrix[i][j] for j in indices] for i in indices]
    determinant = determinant_integer(principal)
    core.require(determinant == witness["determinant"] and determinant < 0,
                 "Negative principal minor verification failed")
    if rational:
        core.require(determinant_rational(principal) == determinant, "Rational check failed")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="NEW JSON file")
    ap.add_argument("--status-seconds", type=float, default=600.0)
    args = ap.parse_args()
    core.require(args.status_seconds > 0, "status-seconds must be positive")
    core.require(not args.out.exists(), "Output already exists")
    meta = json.loads((args.audit / "metadata.json").read_text())
    core.require(meta["status"] == "COMPLETE" and meta["exact_PSD"], "Completed PSD audit required")
    rng = random.Random(20260908)
    controls = 0
    for n in range(1, 9):
        for _ in range(10):
            a = [[rng.randrange(-4, 7) for _ in range(n)] for _ in range(n)]
            core.require(determinant_integer(a) == determinant_rational(a), "Determinant control failed")
            controls += 1
    types, lookup = core.local_types()
    case_map = {c["id"]: c for c in core.build_cases(types, lookup)}
    files = sorted(args.audit.glob("k*.json"))
    total = sum(sum(r[6] is not None for r in json.loads(p.read_text())["orbits"]) for p in files)
    start, last_status = time.monotonic(), time.monotonic()
    checked = rational_checks = matrix_checks = 0
    corrupted_rejected = False
    counts = {}
    for file in files:
        data = json.loads(file.read_text())
        case = case_map[data["summary"]["id"]]
        count = 0
        for record in data["orbits"]:
            code, witness = record[0], record[6]
            if witness is None:
                continue
            neighbors = core.neighbors_for(core.TRIPLES[code])
            matrix = combinatorial_gram(case, neighbors)
            # Two differently constructed matrices, checked for every certificate.
            core.require(matrix == core.make_gram(case, neighbors)[1], "Gram constructors disagree")
            matrix_checks += 1
            rational = count < 2 or checked % 1000 == 0
            validate(matrix, witness, rational)
            rational_checks += rational
            if not corrupted_rejected:
                wrong = {"indices": witness["indices"], "determinant": witness["determinant"] - 1}
                try:
                    validate(matrix, wrong)
                except RuntimeError:
                    corrupted_rejected = True
                core.require(corrupted_rejected, "Corrupted witness was accepted")
            checked += 1
            count += 1
            now = time.monotonic()
            if now - last_status >= args.status_seconds:
                eta = (now - start) * (total - checked) / max(checked, 1)
                print(f"VERIFY_STATUS checked={checked}/{total} elapsed_s={now-start:.1f} ETA_s~{eta:.1f}", flush=True)
                last_status = now
        counts[case["id"]] = count
    core.require(checked == total and corrupted_rejected, "Verifier coverage failed")
    result = {
        "status": "PASS", "negative_principal_minors_checked": checked,
        "independent_Gram_reconstructions": matrix_checks, "rational_determinant_checks": rational_checks,
        "synthetic_determinant_controls": controls, "corrupted_witness_rejected": corrupted_rejected,
        "case_counts": counts, "wall_seconds": round(time.monotonic() - start, 3),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "audit_source_sha256": meta["source_sha256"],
        "scope": "Exact independent arithmetic witness verification, not LRAT/Cake or a verified proof assistant",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting results.
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print("MINOR_VERIFICATION_PASS " + json.dumps({k: v for k, v in result.items() if k != "case_counts"}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
