#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter

N = 33


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha(obj):
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def partitions(n, minimum=3):
    if n == 0:
        yield ()
        return
    for a in range(n, minimum - 1, -1):
        for rest in partitions(n - a, minimum):
            if not rest or a >= rest[0]:
                yield (a,) + rest


def all_types(tau):
    return list(partitions(N - tau))


def ledges(tau, part):
    out = []
    p = tau
    for length in part:
        out += [
            tuple(sorted((p + i, p + (i + 1) % length)))
            for i in range(length)
        ]
        p += length
    return sorted(out)


def features(part):
    counts = Counter(part)
    aut = 1
    for length, number in counts.items():
        aut *= (2 * length) ** number * math.factorial(number)
    return {
        "type": list(part),
        "c3": counts[3],
        "components": len(part),
        "largest": part[0],
        "different_lengths": len(counts),
        "log2_aut": math.log2(aut),
    }


def product_ids(candidates):
    candidate_set = set(candidates)
    products = set()
    for i in range(N):
        for j in range(i + 1, N):
            for k in range(N):
                if k in (i, j):
                    continue
                a = tuple(sorted((i, k)))
                b = tuple(sorted((k, j)))
                if a in candidate_set and b in candidate_set:
                    products.add((a, b) if a < b else (b, a))
    return sorted(products)


def make_core_from_structure(T, L, cycle_type):
    T = tuple(sorted(T))
    tset = set(T)
    if any(i < 0 or i >= N for i in T):
        raise ValueError("T vertex out of range")
    if len(tset) != len(T):
        raise ValueError("T contains duplicates")

    L = sorted(set(tuple(sorted(edge)) for edge in L))
    U = tuple(i for i in range(N) if i not in tset)
    uset = set(U)

    if sum(cycle_type) != len(U):
        raise ValueError("cycle partition does not match complement of T")
    if any(length < 3 for length in cycle_type):
        raise ValueError("cycle lengths must be >=3")
    if any(a == b or a not in uset or b not in uset for a, b in L):
        raise ValueError("L must be simple and supported on U")

    nbr = {i: set() for i in range(N)}
    for i, j in L:
        nbr[i].add(j)
        nbr[j].add(i)

    if any(len(nbr[i]) != 0 for i in T):
        raise ValueError("T vertices must have L-degree 0")
    if any(len(nbr[i]) != 2 for i in U):
        raise ValueError("L must be 2-regular on U")

    lset = set(L)
    candidates = [
        (i, j)
        for i in range(N)
        for j in range(i + 1, N)
        if (i, j) not in lset
    ]
    candidate_set = set(candidates)

    products = product_ids(candidates)
    product_id = {item: index for index, item in enumerate(products)}
    pair_equations = []

    for i in range(N):
        for j in range(i + 1, N):
            d = 2 * (i in tset) + 2 * (j in tset)
            cij = d + 1
            ell = (i, j) in lset
            terms = []

            for k in range(N):
                if k in (i, j):
                    continue
                a = tuple(sorted((i, k)))
                b = tuple(sorted((k, j)))
                if a in candidate_set and b in candidate_set:
                    z = (a, b) if a < b else (b, a)
                    terms.append(["p", product_id[z], 1])

            for k in nbr[j]:
                if k != i and tuple(sorted((i, k))) in candidate_set:
                    terms.append(["s", tuple(sorted((i, k))), 2])

            for k in nbr[i]:
                if k != j and tuple(sorted((k, j))) in candidate_set:
                    terms.append(["s", tuple(sorted((k, j))), 2])

            if not ell:
                terms.append(["s", (i, j), cij])

            rhs = 6 - 4 * len(nbr[i] & nbr[j]) - 2 * ell * cij
            pair_equations.append({
                "pair": [i, j],
                "rhs": rhs,
                "terms": terms,
            })

    core = {
        "format": "O3-QSAT-CORE-0.1",
        "n": N,
        "T": list(T),
        "U": list(U),
        "cycle_type": list(cycle_type),
        "L": L,
        "candidate_edges": candidates,
        "degree_targets": {
            str(i): (12 if i in tset else 10)
            for i in range(N)
        },
        "products": [
            {
                "id": index,
                "factors": [list(a), list(b)],
            }
            for index, (a, b) in enumerate(products)
        ],
        "pair_equations": pair_equations,
        "matrix": {
            "identity": "Q^2+Q=12I+6J",
            "Q": "2D_T+S+2L",
        },
    }
    core["sha256"] = sha(core)
    return core


def make_core(tau, part):
    if tau not in (6, 13, 20, 27):
        raise ValueError("tau must be one of 6,13,20,27")
    if sum(part) != N - tau or any(length < 3 for length in part):
        raise ValueError("cycle partition does not match 33-tau")
    T = tuple(range(tau))
    L = ledges(tau, part)
    return make_core_from_structure(T, L, part)


def validate_basic(core):
    tau = len(core["T"])
    u_size = N - tau
    assert len(core["U"]) == u_size
    assert sum(core["cycle_type"]) == u_size
    assert len(core["L"]) == u_size
    assert len(core["pair_equations"]) == N * (N - 1) // 2
    tset = set(core["T"])
    assert all(
        core["degree_targets"][str(i)] == (12 if i in tset else 10)
        for i in range(N)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tau", type=int)
    parser.add_argument("--type", nargs="*", type=int)
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.tau is None:
        counts = {}
        for tau in (6, 13, 20, 27):
            types = [part for part in all_types(tau) if 4 not in part]
            for part in types:
                validate_basic(make_core(tau, part))
            counts[tau] = len(types)
        assert counts == {6: 103, 13: 28, 20: 6, 27: 2}
        print("GENERIC_CORE_BASIC PASS", counts)
        return

    part = tuple(args.type or ())
    core = make_core(args.tau, part)
    validate_basic(core)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(canon(core) + "\n")
    print(core["sha256"])


if __name__ == "__main__":
    main()
