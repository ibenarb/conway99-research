"""Finite lazy streams of validated product, Apex and rotation trades."""

from collections import defaultdict
from itertools import combinations, permutations
import random
import time

from core import OUTER, OUTER_INDEX, BudgetEnd, apply_move, edge, vertices


def triangles(rows):
    result = []
    for a, row in enumerate(rows):
        for b in vertices(row & ~((1 << (a + 1)) - 1)):
            for c in vertices(row & rows[b] & ~((1 << (b + 1)) - 1)):
                result.append((a, b, c))
    return result


def lambda_preserved(rows, move):
    child = apply_move(rows, move)
    touched = set(v for part in move for pair in part for v in pair)
    # Only edges incident with touched vertices can gain or lose triangles.
    # For all other edges, their two unchanged neighbor sets are unchanged.
    for a in touched:
        if child[a].bit_count() != rows[a].bit_count():
            return False
        for b in vertices(child[a]):
            if (child[a] & child[b]).bit_count() != 1:
                return False
    return True


def apex_moves(rows, rng=None, budget=None):
    ts = triangles(rows)
    if rng:
        rng.shuffle(ts)
    seen = set()
    counter = 0
    for first, second in combinations(ts, 2):
        counter += 1
        if budget and counter % 64 == 0:
            budget.check()
        if set(first) & set(second):
            continue
        for c in first:
            a, b = (v for v in first if v != c)
            for d in second:
                e, f = (v for v in second if v != d)
                added = tuple(sorted((edge(a, d), edge(b, d), edge(c, e), edge(c, f))))
                if any(rows[u] & (1 << v) for u, v in added):
                    continue
                deleted = tuple(sorted((edge(a, c), edge(b, c), edge(d, e), edge(d, f))))
                revised = {u: rows[u] for u in first + second}
                for u, v in deleted + added:
                    revised[u] ^= 1 << v
                    revised[v] ^= 1 << u
                if not all((revised[u] & revised[v]).bit_count() == 1 for u, v in added):
                    continue
                move = (deleted, added)
                if move not in seen and lambda_preserved(rows, move):
                    seen.add(move)
                    yield move


def rotation_moves(rows, rng=None, budget=None):
    ts = triangles(rows)
    by_vertex = defaultdict(list)
    for t in ts:
        for a in t:
            by_vertex[a].append(tuple(v for v in t if v != a))
    if rng:
        rng.shuffle(ts)
    seen = set()
    for tips in ts:
        if budget:
            budget.check()
        a, b, c = tips
        for base_a in by_vertex[a]:
            for base_b in by_vertex[b]:
                for base_c in by_vertex[c]:
                    bases = (base_a, base_b, base_c)
                    all_vertices = tips + sum(bases, ())
                    if len(set(all_vertices)) != 9:
                        continue
                    matched = True
                    for i, j in ((0, 1), (1, 2), (0, 2)):
                        if any(sum(bool(rows[u] & (1 << v)) for v in bases[j]) != 1 for u in bases[i]):
                            matched = False
                            break
                        if any(sum(bool(rows[v] & (1 << u)) for u in bases[i]) != 1 for v in bases[j]):
                            matched = False
                            break
                    if not matched:
                        continue
                    for direction in (1, -1):
                        deleted = tuple(sorted(edge(tips[i], v) for i in range(3) for v in bases[i]))
                        added = tuple(sorted(edge(tips[(i + direction) % 3], v) for i in range(3) for v in bases[i]))
                        if any(rows[u] & (1 << v) for u, v in added):
                            continue
                        move = (deleted, added)
                        if move not in seen and lambda_preserved(rows, move):
                            seen.add(move)
                            yield move


def signed_vectors(length, rng):
    """Support-4 or -6 vectors, modulo sign, without a quadratic pair table."""
    labels = list(range(14))
    rng.shuffle(labels)
    if length == 4:
        for subset in combinations(labels, 4):
            a, b, c, d = subset
            matchings = (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c)))
            for first, second in combinations(matchings, 2):
                pairs = first + second
                if all(edge(*p) in OUTER_INDEX for p in pairs):
                    yield tuple((OUTER_INDEX[edge(*p)], 1 if i < 2 else -1) for i, p in enumerate(pairs))
        return
    if length != 6:
        raise ValueError("Unsupported product support")
    # Simple six-cycles and two triangles with one shared frame vertex.
    for subset in combinations(labels, 6):
        for tail in permutations(subset[1:]):
            if tail[0] > tail[-1]:
                continue
            cyc = (subset[0],) + tail
            pairs = [edge(cyc[i], cyc[(i + 1) % 6]) for i in range(6)]
            if all(p in OUTER_INDEX for p in pairs):
                yield tuple((OUTER_INDEX[p], (-1) ** i) for i, p in enumerate(pairs))
    for subset in combinations(labels, 5):
        for a in subset:
            rest = [v for v in subset if v != a]
            for b, c in combinations(rest, 2):
                d, e = [v for v in rest if v not in (b, c)]
                if edge(b, c) > edge(d, e):
                    continue
                pairs = [edge(u, v) for u, v in ((a, b), (b, c), (c, a), (a, d), (d, e), (e, a))]
                if all(p in OUTER_INDEX for p in pairs):
                    yield tuple((OUTER_INDEX[p], (-1) ** i) for i, p in enumerate(pairs))


def restricted_vectors(signs, length):
    """Enumerate alternating closed edge trails with distinct support edges."""
    incident = defaultdict(list)
    for index, sign in signs.items():
        a, b = OUTER[index]
        incident[(a, sign)].append((index, b))
        incident[(b, sign)].append((index, a))
    seen = set()

    def visit(start, current, sign, path, used):
        if len(path) == length:
            if current == start:
                vector = tuple(sorted(path))
                if vector not in seen:
                    seen.add(vector)
                    yield vector
            return
        for index, other in incident[(current, sign)]:
            if index in used:
                continue
            # Distinct edges; repeated vertices permit the figure-eight family.
            yield from visit(start, other, -sign, path + ((index, sign),), used | {index})

    for start in range(14):
        yield from visit(start, start, 1, (), set())


def omega_moves(rows, family, rng=None, budget=None):
    rng = rng or random.Random(0)
    left, right = map(int, family.split("x"))
    seen = set()
    for counter, x in enumerate(signed_vectors(left, rng)):
        if budget and counter % 16 == 0:
            budget.check()
        used = {u for u, sign in x}
        signs = {}
        for v in range(84):
            if v in used:
                continue
            required = [(-1 if rows[u + 15] & (1 << (v + 15)) else 1) * sign for u, sign in x]
            if all(s == required[0] for s in required):
                signs[v] = required[0]
        if len(signs) < right:
            continue
        for y in restricted_vectors(signs, right):
            deleted, added = [], []
            for u, sx in x:
                for v, sy in y:
                    (added if sx * sy > 0 else deleted).append(edge(u + 15, v + 15))
            move = (tuple(sorted(deleted)), tuple(sorted(added)))
            if move not in seen:
                seen.add(move)
                yield move


class MoveSource:
    """Weighted finite family streams; an exhausted stream is removed.

    Within-family order is randomized by frame/triangle traversal, not claimed
    uniform over legal trades. Generation time is charged to the task budget.
    A budget stop is never reported as an exhaustive empty neighborhood.
    """
    def __init__(self, rows, arm, rng, budget):
        self.rows = rows
        self.rng = rng
        self.budget = budget
        self.weights = {"4x4": 70, "4x6": 20, "6x6": 10} if arm == "omega" else {"apex": 90, "rotation": 10}
        self.streams = {}
        for name in self.weights:
            if name == "apex":
                stream = apex_moves(rows, rng, budget)
            elif name == "rotation":
                stream = rotation_moves(rows, rng, budget)
            else:
                stream = omega_moves(rows, name, rng, budget)
            self.streams[name] = iter(stream)
        self.exhausted = []

    def next(self):
        while self.weights:
            self.budget.check()
            names = list(self.weights)
            name = self.rng.choices(names, [self.weights[k] for k in names])[0]
            try:
                move = next(self.streams[name])
                self.budget.generated += 1
                return name, move
            except StopIteration:
                del self.weights[name]
                self.exhausted.append(name)
        return None
