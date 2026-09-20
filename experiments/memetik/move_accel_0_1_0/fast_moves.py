"""Order-preserving accelerators for the frozen 0.4.1 finite move streams.

No change to families, RNG draws, deduplication, or admissibility predicates.
Checks for necessary conditions precede Python object construction.
"""
import random
from itertools import combinations
from collections import defaultdict

from common import core
import moves as baseline

reference = baseline.reference
MASK = baseline.MASK


def omega_moves(rows, family, rng=None, budget=None):
    rng = rng or random.Random(0)
    left, right = map(int, family.split('x'))
    vectors = baseline.catalogue(left)
    order = list(range(len(vectors)))
    rng.shuffle(order)  # Keep exactly the baseline random permutation/draws.
    adjacent = tuple(row >> 15 for row in rows[15:])
    absent = tuple(MASK ^ row for row in adjacent)
    seen = set()
    half = right // 2
    for counter, index in enumerate(order):
        if budget and counter % 16 == 0:
            budget.check()
        x = vectors[index]
        plus = minus = MASK
        used = 0
        for u, sign in x:
            plus &= absent[u] if sign > 0 else adjacent[u]
            minus &= adjacent[u] if sign > 0 else absent[u]
            used |= 1 << u
            # An alternating closed even trail needs right/2 of EACH sign.
            if plus.bit_count() < half or minus.bit_count() < half:
                break
        else:
            plus &= MASK ^ used
            minus &= MASK ^ used
            if plus.bit_count() < half or minus.bit_count() < half:
                continue
            signs = {**{v: 1 for v in core.vertices(plus)},
                     **{v: -1 for v in core.vertices(minus)}}
            for y in reference.restricted_vectors(signs, right):
                deleted, added = [], []
                for u, sx in x:
                    for v, sy in y:
                        pair = (u+15, v+15) if u < v else (v+15, u+15)
                        (added if sx*sy > 0 else deleted).append(pair)
                move = tuple(sorted(deleted)), tuple(sorted(added))
                if move not in seen:
                    seen.add(move)
                    yield move


def apex_moves(rows, rng=None, budget=None):
    ts = reference.triangles(rows)
    if rng:
        rng.shuffle(ts)
    bits = tuple(1 << v for v in range(len(rows)))
    masks = {t: sum(bits[v] for v in t) for t in ts}
    seen = set()
    for counter, (first, second) in enumerate(combinations(ts, 2), 1):
        if budget and counter % 64 == 0:
            budget.check()
        if masks[first] & masks[second]:
            continue
        for c in first:
            a, b = (v for v in first if v != c)
            ab = bits[a] | bits[b]
            for d in second:
                ef = masks[second] ^ bits[d]
                if rows[d] & ab or rows[c] & ef:
                    continue
                e, f = (v for v in second if v != d)
                revised = {a: rows[a] ^ bits[c] ^ bits[d],
                           b: rows[b] ^ bits[c] ^ bits[d],
                           c: rows[c] ^ ab ^ ef,
                           d: rows[d] ^ ef ^ ab,
                           e: rows[e] ^ bits[d] ^ bits[c],
                           f: rows[f] ^ bits[d] ^ bits[c]}
                if any((revised[u] & revised[v]).bit_count() != 1
                       for u, v in ((a, d), (b, d), (c, e), (c, f))):
                    continue
                edge = core.edge
                added = tuple(sorted((edge(a, d), edge(b, d), edge(c, e), edge(c, f))))
                deleted = tuple(sorted((edge(a, c), edge(b, c), edge(d, e), edge(d, f))))
                move = deleted, added
                if move not in seen and reference.lambda_preserved(rows, move):
                    seen.add(move)
                    yield move


def rotation_moves(rows, rng=None, budget=None):
    ts = reference.triangles(rows)
    by_vertex = defaultdict(list)
    for t in ts:
        for a in t:
            by_vertex[a].append(tuple(v for v in t if v != a))
    if rng:
        rng.shuffle(ts)
    masks = {pair: sum(1 << v for v in pair) for pairs in by_vertex.values() for pair in pairs}
    matches = {}

    def matched(a, b):
        k = (a, b) if a < b else (b, a)
        if k not in matches:
            matches[k] = (all((rows[u] & masks[b]).bit_count() == 1 for u in a)
                          and all((rows[v] & masks[a]).bit_count() == 1 for v in b))
        return matches[k]

    seen = set()
    for tips in ts:
        if budget:
            budget.check()
        a, b, c = tips
        tip_mask = sum(1 << v for v in tips)
        for base_a in by_vertex[a]:
            ma = masks[base_a]
            if ma & tip_mask:
                continue
            for base_b in by_vertex[b]:
                mb = masks[base_b]
                if mb & (tip_mask | ma) or not matched(base_a, base_b):
                    continue
                for base_c in by_vertex[c]:
                    mc = masks[base_c]
                    if mc & (tip_mask | ma | mb):
                        continue
                    if not matched(base_b, base_c) or not matched(base_a, base_c):
                        continue
                    bases = (base_a, base_b, base_c)
                    for direction in (1, -1):
                        deleted = tuple(sorted(core.edge(tips[i], v) for i in range(3) for v in bases[i]))
                        added = tuple(sorted(core.edge(tips[(i+direction) % 3], v) for i in range(3) for v in bases[i]))
                        if any(rows[u] & (1 << v) for u, v in added):
                            continue
                        move = deleted, added
                        if move not in seen and reference.lambda_preserved(rows, move):
                            seen.add(move)
                            yield move


class MoveSource(reference.MoveSource):
    def __init__(self, rows, arm, rng, budget):
        super().__init__(rows, arm, rng, budget)
        self.streams = {name: iter(omega_moves(rows, name, rng, budget)) if arm == 'omega'
                        else iter((apex_moves if name == 'apex' else rotation_moves)(rows, rng, budget))
                        for name in self.weights}
