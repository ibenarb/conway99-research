from pathlib import Path
from itertools import combinations, permutations, product
from collections import Counter
import json
import numpy as np

OUT = Path(__file__).resolve().parent
EDGES = [(u, v) for u in range(10) for v in range(u + 1, 10) if u // 2 != v // 2]
INDEX = {e: i for i, e in enumerate(EDGES)}
GCOL = [INDEX[tuple(sorted((u ^ 1, v ^ 1)))] for u, v in EDGES]
ORBITS = []
for b, c in combinations(range(5), 2):
    ORBITS.append((INDEX[(2 * b, 2 * c)], INDEX[(2 * b + 1, 2 * c + 1)]))
    ORBITS.append((INDEX[(2 * b, 2 * c + 1)], INDEX[(2 * b + 1, 2 * c)]))


def bitmask(edges):
    return sum(1 << e for e in edges)


def degree(edges):
    result = [0] * 10
    for edge in edges:
        u, v = EDGES[edge]
        result[u] += 1
        result[v] += 1
    return result


def cycles(edges):
    graph = [set() for _ in range(10)]
    for edge in edges:
        u, v = EDGES[edge]
        graph[u].add(v)
        graph[v].add(u)
    assert all(len(n) == 2 for n in graph)
    unseen = set(range(10))
    sizes = []
    while unseen:
        todo = [min(unseen)]
        comp = set()
        while todo:
            v = todo.pop()
            if v not in comp:
                comp.add(v)
                todo.extend(graph[v] - comp)
        unseen -= comp
        sizes.append(len(comp))
    return tuple(sorted(sizes))


def generate_h0():
    deg = [0] * 10
    chosen = []
    result = []
    def visit(index):
        if len(chosen) + 20 - index < 10:
            return
        if index == 20:
            if len(chosen) == 10 and deg == [2] * 10:
                result.append(tuple(sorted(chosen)))
            return
        for edge in ORBITS[index]:
            u, v = EDGES[edge]
            if deg[u] < 2 and deg[v] < 2 and len(chosen) < 10:
                deg[u] += 1
                deg[v] += 1
                chosen.append(edge)
                visit(index + 1)
                chosen.pop()
                deg[u] -= 1
                deg[v] -= 1
        visit(index + 1)
    visit(0)
    return result


def main():
    all_h0 = generate_h0()
    assert len(all_h0) == 22176
    group = np.array([[2 * p[u // 2] + ((u % 2) ^ bits[u // 2]) for u in range(10)]
                      for p in permutations(range(5)) for bits in product((0, 1), repeat=5)])
    edge_maps = np.array([[INDEX[tuple(sorted((int(p[u]), int(p[v]))))] for u, v in EDGES] for p in group])
    edge_bits = np.left_shift(np.uint64(1), edge_maps.astype(np.uint64))
    seen_h0 = set()
    h0_reps = []
    pair_reps = []
    first_pair = None
    for h0 in all_h0:
        mask0 = bitmask(h0)
        if mask0 in seen_h0:
            continue
        h0_reps.append(h0)
        images = edge_bits[:, h0].sum(axis=1, dtype=np.uint64)
        seen_h0.update(map(int, images))
        stabilizer = edge_bits[images == mask0]
        used = set(h0) | {GCOL[e] for e in h0}
        remaining = [o for o in ORBITS if o[0] not in used]
        assert len(remaining) == 10
        seen_h1 = set()
        for bits in product((0, 1), repeat=10):
            h1 = tuple(sorted(remaining[i][bits[i]] for i in range(10)))
            if degree(h1) != [2] * 10:
                continue
            if first_pair is None:
                first_pair = (h0, h1)
            mask1 = bitmask(h1)
            if mask1 in seen_h1:
                continue
            images1 = stabilizer[:, h1].sum(axis=1, dtype=np.uint64)
            seen_h1.update(map(int, images1))
            assert not (set(h0) & set(h1))
            assert not (set(h0) & {GCOL[e] for e in h1})
            invariant = sorted((cycles(h0), cycles(h1)))
            pair_reps.append({"h0": h0, "h1": h1, "cycle_pair_invariant": invariant})
    assert len(seen_h0) == 22176
    assert len(h0_reps) == 15
    assert len(pair_reps) == 78
    fixed_inv = sorted((cycles(first_pair[0]), cycles(first_pair[1])))
    distinct = next(p for p in pair_reps if p["cycle_pair_invariant"] != fixed_inv)
    # All four variable choices on both cyclic edge orbits between two blocks.
    parity_checks = 0
    for a0, a1, b0, b1 in product((0, 1), repeat=4):
        assert ((a0 == b0) + (a1 == b1)) % 2 == (a0 + a1 + b0 + b1) % 2
        parity_checks += 1
    output = {
        "h0_count": len(all_h0), "h0_orbits_B5": len(h0_reps), "ordered_pair_orbits_B5": len(pair_reps),
        "first_fixed_pair": {"h0": first_pair[0], "h1": first_pair[1], "cycle_pair_invariant": fixed_inv},
        "inequivalent_pair_witness": distinct, "edges": EDGES,
        "pair_representatives": pair_reps, "local_parity_identity_checks": parity_checks,
        "interpretation": "Different cycle-pair invariants persist under B5, exchange of h0/h1, and g-conjugation; they do not prove global SRG extendability."
    }
    (OUT / "boundary_audit.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k not in ("pair_representatives", "edges")}))


if __name__ == "__main__":
    main()
