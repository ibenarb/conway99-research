#!/usr/bin/env python3
"""Independent O3-BREADTH-1 cycle-local checker, peer-review revision.

No historical qsat module is imported.

Checks:
- quotient template against direct integer matrix multiplication for all tau;
- positive control srg(9,4,1,2);
- C5..C8 enumeration;
- explicit ablation of the inner-consistency lemma;
- moment identity and safe d_w <= min(m,12) cap;
- small-m distance-class assertions;
- coefficient mutations and negative controls.

This is a validation tool, not a global UNSAT certificate.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from functools import lru_cache
from pathlib import Path

N = 33
TAUS = (6, 13, 20, 27)
WEAK_COUNTS = {5: 6, 6: 66, 7: 478, 8: 14615}
LOCAL_COUNTS = {5: 6, 6: 66, 7: 408, 8: 6717}
MOMENT_COUNTS = {5: 6, 6: 34, 7: 309, 8: 5754}
MUTATED_MIXED_COUNTS = {5: 21, 6: 239, 7: 3930, 8: 116423}


def upair(a, b):
    return (a, b) if a < b else (b, a)


def cycle_edges(vertices):
    m = len(vertices)
    return {upair(vertices[i], vertices[(i + 1) % m]) for i in range(m)}


class CycleModel:
    def __init__(self, m):
        if m < 5:
            raise ValueError("CycleModel requires m >= 5")
        self.m = m
        self.chords = []
        self.idx = [[-1] * m for _ in range(m)]

        for i in range(m):
            for j in range(i + 1, m):
                d = min(j - i, m - (j - i))
                if d != 1:
                    k = len(self.chords)
                    self.chords.append((i, j))
                    self.idx[i][j] = self.idx[j][i] = k

        self.pairs = []
        self.distance_histogram = Counter()
        for i in range(m):
            for j in range(i + 1, m):
                d = min(j - i, m - (j - i))
                self.distance_histogram[1 if d == 1 else 2 if d == 2 else 3] += 1
                fixed = 2 if d == 1 else 4 if d == 2 else 0
                xidx = self.idx[i][j]

                products = []
                for k in range(m):
                    if k in (i, j):
                        continue
                    a = self.idx[i][k]
                    b = self.idx[k][j]
                    if a >= 0 and b >= 0:
                        products.append((a, b))

                mixed = []
                for a, b in (
                    (i, j - 1),
                    (i, j + 1),
                    (i - 1, j),
                    (i + 1, j),
                ):
                    a %= m
                    b %= m
                    if a != b and self.idx[a][b] >= 0:
                        mixed.append(self.idx[a][b])

                self.pairs.append(
                    (i, j, d, fixed, xidx, tuple(products), tuple(mixed))
                )

        expected_far = m * (m - 1) // 2 - 2 * m
        assert self.distance_histogram[1] == m
        assert self.distance_histogram[2] == m
        assert self.distance_histogram[3] == expected_far
        if m == 5:
            assert expected_far == 0
        if m == 6:
            assert expected_far == 3

        self.amo = []
        for i in range(m):
            triple = []
            for a, b in (
                (i, i + 2),
                (i, i + 3),
                (i - 1, i + 2),
            ):
                a %= m
                b %= m
                k = self.idx[a][b]
                if k < 0:
                    raise AssertionError("distance-2 AMO term is not a chord")
                triple.append(k)
            self.amo.append(tuple(triple))

    @staticmethod
    def bit(mask, k):
        return 0 if k < 0 else (mask >> k) & 1

    def components_for_pair(self, mask, spec):
        i, j, d, fixed, xidx, products, mixed = spec
        x = self.bit(mask, xidx)
        internal_common = sum(
            self.bit(mask, p) * self.bit(mask, q)
            for p, q in products
        )
        mixed_count = sum(self.bit(mask, k) for k in mixed)
        return i, j, d, fixed, x, internal_common, mixed_count

    def weak_pair_remainder(self, mask, spec):
        _, _, _, fixed, x, _, mixed_count = self.components_for_pair(mask, spec)
        return 6 - fixed - x - 2 * mixed_count

    def local_pair_remainder(self, mask, spec, mixed_coefficient=2):
        _, _, _, fixed, x, internal_common, mixed_count = self.components_for_pair(
            mask,
            spec,
        )
        return (
            6
            - fixed
            - x
            - internal_common
            - mixed_coefficient * mixed_count
        )

    def weak_feasible(self, mask):
        return all(
            self.weak_pair_remainder(mask, spec) >= 0
            for spec in self.pairs
        )

    def local_feasible(self, mask, mixed_coefficient=2):
        return all(
            self.local_pair_remainder(mask, spec, mixed_coefficient) >= 0
            for spec in self.pairs
        )

    def chosen_edges(self, mask):
        return [
            edge
            for k, edge in enumerate(self.chords)
            if self.bit(mask, k)
        ]

    def chord_degrees(self, mask):
        deg = [0] * self.m
        for k, (a, b) in enumerate(self.chords):
            if self.bit(mask, k):
                deg[a] += 1
                deg[b] += 1
        return deg

    def moment_targets(self, mask):
        e = mask.bit_count()
        deg = self.chord_degrees(mask)
        first = 10 * self.m - 2 * e
        second = (
            3 * self.m * (self.m - 3)
            - 9 * e
            - sum(d * (d - 1) // 2 for d in deg)
        )
        return first, second

    def direct_second_moment(self, mask):
        return sum(
            self.local_pair_remainder(mask, spec)
            for spec in self.pairs
        )


@lru_cache(maxsize=None)
def moment_possible(noutside, cap, first, second):
    if first < 0 or second < 0:
        return False
    states = {(0, 0)}
    for _ in range(noutside):
        nxt = set()
        for s1, s2 in states:
            for d in range(cap + 1):
                a = s1 + d
                b = s2 + d * (d - 1) // 2
                if a <= first and b <= second:
                    nxt.add((a, b))
        states = nxt
        if not states:
            return False
    return (first, second) in states


def enumerate_cycle(m):
    model = CycleModel(m)
    weak = 0
    local = 0
    moment = 0
    mutated_mixed = 0
    edge_hist = Counter()
    moment_hist = Counter()
    c6_counterexample = None

    for mask in range(1 << len(model.chords)):
        if model.weak_feasible(mask):
            weak += 1

        if model.local_feasible(mask, mixed_coefficient=1):
            mutated_mixed += 1

        if not model.local_feasible(mask):
            continue

        local += 1
        e = mask.bit_count()
        edge_hist[e] += 1

        for triple in model.amo:
            if sum(model.bit(mask, k) for k in triple) > 1:
                raise AssertionError(
                    f"distance-2 AMO failed m={m} mask={mask}"
                )

        if m == 5 and e > 1:
            raise AssertionError("C5 at-most-one chord failed")

        if m == 6 and e >= 2 and c6_counterexample is None:
            c6_counterexample = model.chosen_edges(mask)

        first, second = model.moment_targets(mask)
        if second != model.direct_second_moment(mask):
            raise AssertionError(
                f"moment identity failed m={m} mask={mask}"
            )

        if moment_possible(
            N - m,
            min(m, 12),
            first,
            second,
        ):
            moment += 1
            moment_hist[e] += 1

    expected = {
        "weak": WEAK_COUNTS[m],
        "local": LOCAL_COUNTS[m],
        "moment": MOMENT_COUNTS[m],
        "mutated_mixed": MUTATED_MIXED_COUNTS[m],
    }
    actual = {
        "weak": weak,
        "local": local,
        "moment": moment,
        "mutated_mixed": mutated_mixed,
    }
    if actual != expected:
        raise AssertionError(
            f"C{m} regression mismatch actual={actual} expected={expected}"
        )

    out = {
        "m": m,
        "chords": len(model.chords),
        "total_assignments": 1 << len(model.chords),
        "weak_without_inner_consistency": weak,
        "local_with_inner_consistency": local,
        "moment_feasible": moment,
        "mutated_mixed_coefficient_1": mutated_mixed,
        "local_edge_histogram": dict(sorted(edge_hist.items())),
        "moment_edge_histogram": dict(sorted(moment_hist.items())),
        "distance_classes": dict(sorted(model.distance_histogram.items())),
    }

    if m == 6:
        if c6_counterexample is None:
            raise AssertionError(
                "false C6 at-most-one lemma was not rejected"
            )
        out["false_c6_at_most_one_rejected"] = True
        out["c6_counterexample_edges"] = c6_counterexample

    return out


def single_cycle_structure(tau):
    T = set(range(tau))
    U = tuple(range(tau, N))
    L = cycle_edges(U)
    nbr = [set() for _ in range(N)]
    for a, b in L:
        nbr[a].add(b)
        nbr[b].add(a)
    return T, L, nbr


def q_matrix(T, L, S):
    q = [[0] * N for _ in range(N)]
    for i in T:
        q[i][i] = 2
    for a, b in L:
        q[a][b] = q[b][a] = 2
    for a, b in S:
        q[a][b] = q[b][a] = 1
    return q


def sind(S, a, b):
    return 0 if a == b else int(upair(a, b) in S)


def template(T, L, nbr, S, i, j, l2coef=4):
    di = 2 * int(i in T)
    dj = 2 * int(j in T)
    cs = sum(
        sind(S, i, k) * sind(S, k, j)
        for k in range(N)
        if k not in (i, j)
    )
    mixed = (
        sum(sind(S, i, k) for k in nbr[j])
        + sum(sind(S, k, j) for k in nbr[i])
    )
    l2 = len(nbr[i] & nbr[j])
    sij = sind(S, i, j)
    lij = int(upair(i, j) in L)
    return (
        cs
        + 2 * mixed
        + l2coef * l2
        + (di + dj + 1) * sij
        + 2 * (di + dj + 1) * lij
    )


def run_template_test():
    rng = random.Random(0xC099B1)
    total = 0
    per_tau = {}

    for tau in TAUS:
        T, L, nbr = single_cycle_structure(tau)
        candidates = [
            (i, j)
            for i in range(N)
            for j in range(i + 1, N)
            if (i, j) not in L
        ]
        count = 0
        for _ in range(8):
            S = {e for e in candidates if rng.randrange(2)}
            q = q_matrix(T, L, S)
            for i in range(N):
                for j in range(i + 1, N):
                    direct = (
                        sum(q[i][k] * q[k][j] for k in range(N))
                        + q[i][j]
                    )
                    got = template(T, L, nbr, S, i, j)
                    if direct != got:
                        raise AssertionError(
                            f"template mismatch tau={tau} pair={(i, j)}"
                        )
                    total += 1
                    count += 1
        per_tau[str(tau)] = count

    T, L, nbr = single_cycle_structure(27)
    q = q_matrix(T, L, set())
    witness = None
    for i in range(N):
        for j in range(i + 1, N):
            direct = (
                sum(q[i][k] * q[k][j] for k in range(N))
                + q[i][j]
            )
            if direct != template(
                T,
                L,
                nbr,
                set(),
                i,
                j,
                l2coef=3,
            ):
                witness = [i, j]
                break
        if witness:
            break

    if witness is None:
        raise AssertionError(
            "mutated L2 coefficient was not detected"
        )

    return {
        "status": "PASS",
        "pairs_checked": total,
        "per_tau": per_tau,
        "negative_control": "PASS",
        "negative_witness_pair": witness,
    }


def positive_control_rook9():
    n = 3
    q = [
        [2 if i == j else 1 for j in range(n)]
        for i in range(n)
    ]
    for i in range(n):
        if sum(q[i]) != 4:
            raise AssertionError("rook9 row sum failed")
        for j in range(n):
            got = sum(q[i][k] * q[k][j] for k in range(n)) + q[i][j]
            expected = 8 if i == j else 6
            if got != expected:
                raise AssertionError(
                    f"rook9 positive control failed pair={(i, j)}"
                )
    return {
        "status": "PASS",
        "quotient": "Q=I+J",
        "identity": "Q^2+Q=2I+6J",
    }


def moment_cap_regression():
    checks = {}
    for m in (13, 27):
        noutside = N - m
        cap12 = moment_possible(noutside, min(m, 12), 12, 66)
        cap10 = moment_possible(noutside, 10, 12, 66)
        if not cap12 or cap10:
            raise AssertionError(
                f"moment cap regression failed m={m}"
            )
        checks[str(m)] = {
            "outside": noutside,
            "cap12_accepts_degree12_signature": cap12,
            "wrong_cap10_rejects_signature": not cap10,
        }
    return checks


def chordless_c5_check():
    model = CycleModel(5)
    first, second = model.moment_targets(0)
    if (first, second) != (50, 30):
        raise AssertionError("chordless C5 moments changed")
    all_le2 = moment_possible(28, 2, first, second)
    unrestricted = moment_possible(28, 5, first, second)
    if all_le2 or not unrestricted:
        raise AssertionError(
            "chordless C5 hypothesis check failed"
        )
    return {
        "sum_d": first,
        "sum_choose_d_2": second,
        "all_d_at_most_2_possible": all_le2,
        "some_d_at_least_3": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("O3_cycle_local_results.json"),
    )
    args = ap.parse_args()

    template_result = run_template_test()
    positive = positive_control_rook9()
    cap_tests = moment_cap_regression()
    cycles = [enumerate_cycle(m) for m in range(5, 9)]

    result = {
        "format": "O3-BREADTH-1-CYCLE-LOCAL-CHECK-0.3",
        "scope": (
            "necessary local quotient conditions; "
            "not a global certificate"
        ),
        "template": template_result,
        "positive_control_rook9": positive,
        "moment_cap_regression": cap_tests,
        "cycles": cycles,
        "chordless_c5": chordless_c5_check(),
    }

    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("O3_CYCLE_LOCAL_CHECK PASS")
    print(
        "TEMPLATE",
        f"pairs={template_result['pairs_checked']}",
        f"negative_control={template_result['negative_control']}",
    )
    print("POSITIVE_CONTROL_ROOK9 PASS")
    print("MOMENT_CAP m13=PASS m27=PASS")

    for item in cycles:
        print(
            f"C{item['m']}",
            f"total={item['total_assignments']}",
            f"weak={item['weak_without_inner_consistency']}",
            f"local={item['local_with_inner_consistency']}",
            f"moment={item['moment_feasible']}",
            f"mut1={item['mutated_mixed_coefficient_1']}",
        )

    c5 = result["chordless_c5"]
    print(
        "C5_CHORDLESS",
        f"sum_d={c5['sum_d']}",
        f"sum_choose_d_2={c5['sum_choose_d_2']}",
        f"some_d_ge_3={c5['some_d_at_least_3']}",
    )
    print(f"RESULT {args.out}")


if __name__ == "__main__":
    main()
