"""Bounded adaptations of the admitted Codex F02 and F04 generators.

Source: data/memetik/ai_candidates/submissions/20260915_codex_v01/generate.py
No NetworkX/Numpy dependency for graph construction. Mathematical constraints
and randomized order retained; every returned graph is independently checked.
"""
import itertools
import random

from common import core, cpu


def cover(seed, seconds):
    from ortools.sat.python import cp_model
    pairs = core.OUTER
    supports = [frozenset(a % 7 for a in ab) for ab in pairs]
    model = cp_model.CpModel()
    h = {}
    for i in range(84):
        for j in range(i + 1, 84):
            if supports[i] == supports[j]:
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
            model.add(sum(entry(i, j) for i in range(84) if a in pairs[i])
                      == 2 - int(a in pairs[j]) - int((a + 7) % 14 in pairs[j]))
    blocks = sorted(set(supports), key=lambda s: tuple(sorted(s)))
    for i in range(84):
        for block in blocks:
            if supports[i].isdisjoint(block):
                model.add(sum(entry(i, j) for j in range(84) if supports[j] == block) == 1)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.stop_after_first_solution = True
    solver.parameters.randomize_search = True
    solver.parameters.random_branches_ratio = 0.1
    solver.parameters.linearization_level = 0
    status = solver.solve(model)
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return None, {"solver_status": solver.status_name(status)}
    rows = [0] * 84
    for (i, j), var in h.items():
        value = var if isinstance(var, int) else solver.value(var)
        if value:
            rows[i] |= 1 << j
            rows[j] |= 1 << i
    return core.reconstruct(rows), {"solver_status": solver.status_name(status)}


def lift(seed, seconds, limit=1000):
    rng = random.Random(seed)
    deadline = cpu() + seconds
    best = 0
    for attempt in range(1, limit + 1):
        pool = [(a, b) for a in range(33) for b in range(33)]
        rng.shuffle(pool)
        chosen = []
        for ab in pool:
            if cpu() >= deadline:
                return None, {"status": "CPU_LIMIT", "restarts": attempt, "largest_partial": best}
            trial = chosen + [ab]
            if any(len(values) != len(trial) for values in
                   ({a for a, b in trial}, {b for a, b in trial}, {(b-a) % 33 for a, b in trial})):
                continue
            if any((trial[i][0]+trial[j][1]-trial[j][0]-trial[k][1]) % 33 == 0
                   for i, j, k in itertools.product(range(len(trial)), repeat=3) if not i == j == k):
                continue
            chosen = trial
            if len(chosen) == 7:
                edges = set()
                for u, v in chosen:
                    for x in range(33):
                        tri = [x, 33+(x+u) % 33, 66+(x+v) % 33]
                        edges.update(core.edge(i, j) for i, j in itertools.combinations(tri, 2))
                return core.from_edges(99, edges), {"restarts": attempt, "offsets": chosen}
        best = max(best, len(chosen))
    return None, {"status": "ATTEMPT_LIMIT", "largest_partial": best}


def structure(rows, family):
    """Test the fixed source template, not automorphism loss or all relabelings."""
    if family == "Z33_lift":
        return all(not ((rows[i] >> (33 * (i//33))) & ((1 << 33)-1))
                   and all(((rows[i] >> (33*b)) & ((1 << 33)-1)).bit_count() == 7
                           for b in range(3) if b != i//33) for i in range(99))
    if family == "F02":
        supports = [frozenset(a % 7 for a in ab) for ab in core.OUTER]
        for i in range(84):
            for j in range(i+1, 84):
                edge = bool(rows[i+15] & (1 << (j+15)))
                if supports[i] == supports[j]:
                    if edge != (len(set(core.OUTER[i]) & set(core.OUTER[j])) == 1):
                        return False
                elif not supports[i].isdisjoint(supports[j]) and edge:
                    return False
            for block in set(supports):
                if supports[i].isdisjoint(block):
                    if sum(bool(rows[i+15] & (1 << (j+15))) for j in range(84) if supports[j] == block) != 1:
                        return False
        return True
    return None
