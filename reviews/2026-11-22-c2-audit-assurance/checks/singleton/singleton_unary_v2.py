"""Independent preliminary singleton-root conditions, without orbit pruning.

This is NOT the full first-layer or second-layer singleton exclusion. It
enumerates all 924 balanced sign vectors of every physical catalogue chart,
both overall signs included, and checks only the stated unary conditions.
"""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import time
from cypari2 import Pari

BASE = Path(__file__).resolve().parent
P = Pari()
START = time.time()
rows = [list(map(int, line.split())) for line in (BASE / "layouts.tsv").read_text().splitlines()]
assert len(rows) == 3580
balanced = []
for positive in itertools.combinations(range(12), 6):
    mask = sum(1 << i for i in positive)
    balanced.append((mask, [1 if mask >> i & 1 else -1 for i in range(12)]))
assert len(balanced) == 924


def physical_graph(matching_p, matching_n):
    adjacency = [0] * 39

    def edge(a, b):
        assert a != b
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a

    edge(0, 1)
    edge(0, 2)
    edge(1, 2)
    for j in range(6):
        edge(0, 3 + 2 * j)
        edge(0, 4 + 2 * j)
        edge(3 + 2 * j, 4 + 2 * j)
    for i in range(12):
        edge(1, 15 + i)
        edge(2, 27 + i)
        edge(15 + i, 3 + i)
        edge(27 + i, 3 + (i ^ 1))
        edge(15 + i, 15 + matching_p[i])
        edge(27 + i, 27 + matching_p[i])
        edge(15 + i, 27 + matching_n[i])
        edge(27 + i, 15 + matching_n[i])
    return all((adjacency[i] & adjacency[j]).bit_count() <= 2 - ((adjacency[i] >> j) & 1)
               for i in range(39) for j in range(i))


def components(matching_p, matching_n):
    unseen = set(range(12))
    result = []
    while unseen:
        pending = [min(unseen)]
        component = set()
        while pending:
            v = pending.pop()
            if v in component:
                continue
            component.add(v)
            pending += [v ^ 1, matching_p[v], matching_n[v]]
        unseen -= component
        result.append(sorted(component))
    return result


def matrix(a):
    return P.matrix(len(a), len(a[0]), [x for row in a for x in row])


output = []
totals = Counter()
for cid, row in enumerate(rows):
    assert len(row) == 25 and row[0] in (7, 8, 9, 10, 11)
    matching_p, matching_n = row[1:13], row[13:25]
    for matching in (matching_p, matching_n):
        assert sorted(matching) == list(range(12))
        assert all(matching[i] != i and matching[matching[i]] == i for i in range(12))
    if not physical_graph(matching_p, matching_n):
        output.append({"chart": cid, "physical": False, "surviving_sign_masks": []})
        totals["nonphysical_charts"] += 1
        continue
    groups = components(matching_p, matching_n)
    component_of = {v: j for j, group in enumerate(groups) for v in group}
    h = [[5 * int(i == j) - int((i ^ 1) == j)
          - 2 * int(matching_p[i] == j) - 2 * int(matching_n[i] == j)
          for j in range(12)] for i in range(12)]
    assert all(sum(row) == 0 for row in h)
    inverse = matrix([[h[i][j] + int(component_of[i] == component_of[j])
                       for j in range(12)] for i in range(12)]) ** -1
    denominator = int(P.denominator(inverse))
    integer_inverse = [[int(denominator * inverse[i, j]) for j in range(12)]
                       for i in range(12)]
    counts = Counter()
    retained = []
    for mask, signs in balanced:
        same = sum(signs[i] == signs[matching_p[i]] for i in range(12))
        same += sum(signs[i] == signs[matching_n[i]] for i in range(12))
        assert same % 2 == 0
        same //= 2
        if same not in (0, 2):
            counts["same_sign_budget"] += 1
            continue
        if any(sum(signs[i] for i in group) != 0 for group in groups):
            counts["range"] += 1
            continue
        projected = sum(signs[i] * integer_inverse[i][j] * signs[j]
                        for i in range(12) for j in range(12))
        assert projected >= 0
        if projected > 2 * denominator:
            counts["root_schur"] += 1
            continue
        counts["retained"] += 1
        retained.append(mask)
    assert sum(counts.values()) == 924
    assert set(retained) == {4095 ^ mask for mask in retained}
    rec = {"chart": cid, "physical": True, "components": groups,
           "inverse_denominator": denominator, "counts": dict(counts),
           "surviving_sign_masks": retained}
    output.append(rec)
    totals.update(counts)
    if cid % 100 == 0:
        print(json.dumps({"through_chart": cid, "elapsed": time.time() - START}), flush=True)
assert totals["nonphysical_charts"] == 272
result = {"status": "PRELIMINARY_UNARY_ENUMERATION_COMPLETE",
          "full_singleton_search_complete": False, "charts": output,
          "totals": dict(totals), "elapsed": time.time() - START,
          "catalogue_sha256": hashlib.sha256((BASE / "layouts.tsv").read_bytes()).hexdigest(),
          "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with (BASE / "unary_result_v2.json").open("x") as file:
    json.dump(result, file, indent=4)
print(result["status"], flush=True)
