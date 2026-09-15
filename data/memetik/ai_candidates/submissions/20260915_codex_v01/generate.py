import argparse
import hashlib
import itertools
import json
import platform
import random
import resource
import time

import networkx as nx
import numpy as np
from ortools.sat.python import cp_model


def frame():
    pairs = [(a, b) for a in range(14) for b in range(a + 1, 14)
             if b != (a + 7) % 14]
    p = np.zeros((14, 84), dtype=np.int64)
    for i, ab in enumerate(pairs):
        p[list(ab), i] = 1
    c = np.zeros((14, 14), dtype=np.int64)
    for a in range(14):
        c[a, (a + 7) % 14] = 1
    return pairs, p, c


def omega(kind, seed, seconds, objective):
    pairs, p, c = frame()
    rhs = 2 - (c + np.eye(14, dtype=np.int64)) @ p
    model = cp_model.CpModel()
    h = {}
    supports = [frozenset(a % 7 for a in ab) for ab in pairs]
    for i in range(84):
        for j in range(i + 1, 84):
            if kind == "free":
                h[i, j] = model.new_bool_var(f"h_{i}_{j}")
            elif supports[i] == supports[j]:
                h[i, j] = int(len(set(pairs[i]) & set(pairs[j])) == 1)
            elif supports[i].isdisjoint(supports[j]):
                h[i, j] = model.new_bool_var(f"h_{i}_{j}")
            else:
                h[i, j] = 0
    def entry(i, j):
        return 0 if i == j else h[min(i, j), max(i, j)]
    for j in range(84):
        model.add(sum(entry(i, j) for i in range(84)) == 12)
        for a in range(14):
            model.add(sum(entry(i, j) for i in range(84) if p[a, i])
                      == int(rhs[a, j]))
    if kind == "cover":
        blocks = sorted(set(supports), key=lambda s: tuple(sorted(s)))
        for i in range(84):
            for block in blocks:
                if supports[i].isdisjoint(block):
                    model.add(sum(entry(i, j) for j in range(84)
                                  if supports[j] == block) == 1)
    rng = random.Random(seed)
    variables = [v for v in h.values() if not isinstance(v, int)]
    if objective:
        model.minimize(sum(rng.randint(-100, 100) * v for v in variables))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.stop_after_first_solution = True
    if not objective:
        solver.parameters.randomize_search = True
        solver.parameters.random_branches_ratio = 0.1
        solver.parameters.linearization_level = 0
    status = solver.solve(model)
    info = {"solver_status": solver.status_name(status),
            "boolean_variables": len(variables),
            "branches": solver.num_branches, "conflicts": solver.num_conflicts}
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return None, info
    a = np.zeros((99, 99), dtype=np.int64)
    a[0, 1:15] = a[1:15, 0] = 1
    a[1:15, 1:15] = c
    a[1:15, 15:] = p
    a[15:, 1:15] = p.T
    for (i, j), var in h.items():
        value = var if isinstance(var, int) else solver.value(var)
        a[15 + i, 15 + j] = a[15 + j, 15 + i] = value
    return a, info


def triangle(seed, limit, general):
    rng = random.Random(seed)
    best = 0
    for attempt in range(1, limit + 1):
        pool = [(a, b) for a in range(33) for b in range(33)] if general else [
            (d, 2 * d % 33) for d in range(33)]
        rng.shuffle(pool)
        chosen = []
        for ab in pool:
            trial = chosen + [ab]
            if len({a for a, b in trial}) != len(trial):
                continue
            if len({b for a, b in trial}) != len(trial):
                continue
            if len({(b - a) % 33 for a, b in trial}) != len(trial):
                continue
            if any((trial[i][0] + trial[j][1] - trial[j][0] - trial[k][1]) % 33 == 0
                   for i, j, k in itertools.product(range(len(trial)), repeat=3)
                   if not i == j == k):
                continue
            chosen = trial
            if len(chosen) == 7:
                a = np.zeros((99, 99), dtype=np.int64)
                for u, v in chosen:
                    for x in range(33):
                        tri = [x, 33 + (x + u) % 33, 66 + (x + v) % 33]
                        for i, j in itertools.combinations(tri, 2):
                            a[i, j] = a[j, i] = 1
                return a, {"restarts": attempt, "offsets": chosen,
                           "general_offsets": general}
        best = max(best, len(chosen))
    return None, {"restarts": limit, "largest_partial": best}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["free", "cover", "ap", "offset"], required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--restarts", type=int, default=1000)
    parser.add_argument("--objective", action="store_true")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    wall, cpu = time.perf_counter(), time.process_time()
    if args.kind in ("free", "cover"):
        a, info = omega(args.kind, args.seed, args.seconds, args.objective)
    else:
        a, info = triangle(args.seed, args.restarts, args.kind == "offset")
    elapsed = time.perf_counter() - wall
    used = time.process_time() - cpu
    result = {"kind": args.kind, "seed": args.seed, "objective": args.objective, "details": info,
              "runtime": {"wall_seconds": elapsed, "cpu_seconds": used,
                          "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
                          "environment": f"{platform.system()} {platform.machine()}; Python {platform.python_version()}; one solver worker"}}
    if a is not None:
        data = nx.to_graph6_bytes(nx.from_numpy_array(a), header=False)
        result["graph6"] = data.decode("ascii").rstrip("\n")
        result["graph6_sha256"] = hashlib.sha256(data).hexdigest()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    print(json.dumps({k: v for k, v in result.items() if k != "graph6"}))


if __name__ == "__main__":
    main()
