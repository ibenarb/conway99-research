"""Conway-99 graph operations; integer bitsets, exact scores and identities."""

from collections import Counter
from functools import lru_cache
from itertools import combinations
import hashlib
import json
import random
import time

VERSION = "0.2.0"
BASE_COMMIT = "15f6ce2550423ecfaf75847cfba824deecd563f3"
OUTER = tuple((a, b) for a, b in combinations(range(14), 2) if b - a != 7)
OUTER_INDEX = {p: i for i, p in enumerate(OUTER)}
INCIDENCE = tuple(sum(1 << (15 + i) for i, p in enumerate(OUTER) if a in p) for a in range(14))


class BudgetEnd(Exception):
    """The finite budget of one task is exhausted; the campaign continues."""


class Budget:
    def __init__(self, seconds=30.0, evaluations=256):
        self.started = time.process_time()
        self.deadline = self.started + seconds
        self.limit = evaluations
        self.evaluations = 0
        self.generated = 0

    def check(self):
        if time.process_time() >= self.deadline:
            raise BudgetEnd("CPU_BUDGET")
        if self.evaluations >= self.limit:
            raise BudgetEnd("EVALUATION_BUDGET")

    def evaluate(self):
        self.check()
        self.evaluations += 1

    def remaining(self):
        return max(0.001, self.deadline - time.process_time())


def vertices(bits):
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


def edge(a, b):
    return (min(a, b), max(a, b))


def from_edges(n, pairs):
    rows = [0] * n
    for a, b in pairs:
        if not 0 <= a < n or not 0 <= b < n or a == b:
            raise ValueError("Invalid edge")
        if rows[a] & (1 << b):
            raise ValueError("Repeated edge")
        rows[a] |= 1 << b
        rows[b] |= 1 << a
    return tuple(rows)


def decode_g6(text):
    text = text.strip().removeprefix(">>graph6<<")
    values = [ord(c) - 63 for c in text]
    if not values or any(not 0 <= v <= 63 for v in values):
        raise ValueError("Invalid graph6")
    if values[0] < 63:
        n, offset = values[0], 1
    elif len(values) >= 4 and values[1] < 63:
        n = (values[1] << 12) + (values[2] << 6) + values[3]
        offset = 4
    else:
        raise ValueError("Unsupported graph6 order")
    count = n * (n - 1) // 2
    if len(values) != offset + (count + 5) // 6:
        raise ValueError("Invalid graph6 length")
    rows = [0] * n
    position = 0
    for j in range(1, n):
        for i in range(j):
            if values[offset + position // 6] & (1 << (5 - position % 6)):
                rows[i] |= 1 << j
                rows[j] |= 1 << i
            position += 1
    if count % 6 and values[-1] & ((1 << (6 - count % 6)) - 1):
        raise ValueError("Nonzero graph6 padding")
    return tuple(rows)


def encode_g6(rows):
    n = len(rows)
    prefix = chr(n + 63) if n < 63 else "~" + "".join(chr(((n >> shift) & 63) + 63) for shift in (12, 6, 0))
    output, value, used = [], 0, 0
    for j in range(1, n):
        for i in range(j):
            value = (value << 1) | ((rows[i] >> j) & 1)
            used += 1
            if used == 6:
                output.append(chr(value + 63))
                value, used = 0, 0
    if used:
        output.append(chr((value << (6 - used)) + 63))
    return prefix + "".join(output)


def score(rows):
    total = 0
    for i, row in enumerate(rows):
        for j in range(i):
            residual = (row & rows[j]).bit_count() + ((row >> j) & 1) - 2
            total += residual * residual
    return total


def metrics(rows):
    histogram = Counter()
    defects = [0] * len(rows)
    lambda_bad, triangles6, c4sum = 0, 0, 0
    for i, row in enumerate(rows):
        for j in range(i):
            common = (row & rows[j]).bit_count()
            adjacent = (row >> j) & 1
            r = common + adjacent - 2
            histogram[r] += 1
            if r:
                defects[i] += 1
                defects[j] += 1
            lambda_bad += int(bool(adjacent and common != 1))
            triangles6 += adjacent * common
            c4sum += common * (common - 1) // 2
    return {"F": sum(r * r * n for r, n in histogram.items()),
            "W": sum(n for r, n in histogram.items() if r),
            "L1": sum(abs(r) * n for r, n in histogram.items()),
            "Linf": max(map(abs, histogram), default=0),
            "Nmax": sum(n for r, n in histogram.items() if abs(r) == max(map(abs, histogram), default=0)),
            "lambda_bad": lambda_bad, "triangles": triangles6 // 3,
            "C4": c4sum // 2, "residual_histogram": dict(sorted(histogram.items())),
            "defect_degrees": sorted(defects), "max_defect_degree": max(defects, default=0)}


def validate(rows, arm=None, degree=14):
    n = len(rows)
    if n != 99 or any(type(r) is not int or r < 0 or r >> n for r in rows):
        raise ValueError("Expected 99 integer adjacency rows")
    for i, row in enumerate(rows):
        if row & (1 << i) or row.bit_count() != degree:
            raise ValueError("Diagonal or degree violation")
        for j in vertices(row):
            if not rows[j] & (1 << i):
                raise ValueError("Asymmetric adjacency")
    if arm == "lambda":
        if any((rows[i] & rows[j]).bit_count() != 1 for i in range(n) for j in vertices(rows[i]) if i < j):
            raise ValueError("Lambda condition violated")
    elif arm == "omega":
        expected = reconstruct(tuple(row >> 15 for row in rows[15:]))
        if expected != tuple(rows):
            raise ValueError("Noncanonical Omega frame")
        for u, pair in enumerate(OUTER):
            for label in range(14):
                target = 1 if label in pair or (label + 7) % 14 in pair else 2
                if (rows[u + 15] & INCIDENCE[label]).bit_count() != target:
                    raise ValueError("P-margin violation")
    elif arm is not None:
        raise ValueError("Unknown arm")
    return True


def reconstruct(hrows):
    if len(hrows) != 84:
        raise ValueError("Expected 84 outer rows")
    rows = [((1 << 15) - 2)] + [0] * 98
    for a in range(14):
        rows[1 + a] = 1 | (1 << (1 + (a + 7) % 14)) | INCIDENCE[a]
    for i, (a, b) in enumerate(OUTER):
        rows[15 + i] = (hrows[i] << 15) | (1 << (a + 1)) | (1 << (b + 1))
    return tuple(rows)


def apply_move(rows, move):
    deleted, added = move
    updated = list(rows)
    if set(deleted) & set(added) or len(set(deleted + added)) != len(deleted + added):
        raise ValueError("Malformed trade")
    for sign, pairs in ((0, deleted), (1, added)):
        for a, b in pairs:
            if a >= b or bool(updated[a] & (1 << b)) == bool(sign):
                raise ValueError("Trade not applicable")
            updated[a] ^= 1 << b
            updated[b] ^= 1 << a
    return tuple(updated)


def distance(first, second):
    return sum((a ^ b).bit_count() for a, b in zip(first, second)) // 2


def relabel(rows, old_to_new):
    n = len(rows)
    if sorted(old_to_new) != list(range(n)):
        raise ValueError("Invalid permutation")
    result = [0] * n
    for old, row in enumerate(rows):
        result[old_to_new[old]] = sum(1 << old_to_new[j] for j in vertices(row))
    return tuple(result)


def frame_permutation(base):
    if sorted(base) != list(range(14)) or any(base[(a + 7) % 14] != (base[a] + 7) % 14 for a in range(14)):
        raise ValueError("Not a frame automorphism")
    return [0] + [a + 1 for a in base] + [15 + OUTER_INDEX[edge(base[a], base[b])] for a, b in OUTER]


def random_frame(rng):
    pairs = list(range(7))
    rng.shuffle(pairs)
    first = [p + 7 * rng.randrange(2) for p in pairs]
    return frame_permutation(first + [(p + 7) % 14 for p in first])


@lru_cache(maxsize=512)
def canonical(rows, rooted=False):
    import pynauty
    coloring = [{0}, set(range(1, 15)), set(range(15, 99))] if rooted else []
    graph = pynauty.Graph(len(rows), adjacency_dict={i: list(vertices(row)) for i, row in enumerate(rows)}, vertex_coloring=coloring)
    certificate = pynauty.certificate(graph)
    return hashlib.sha256(certificate).hexdigest()


def describe(rows, arm, family, seed, origin):
    validate(rows, arm)
    data = metrics(rows)
    data.update({"g6": encode_g6(rows), "arm": arm, "family": family,
                 "seed": seed, "origin": origin, "canonical": canonical(rows),
                 "rooted_canonical": canonical(rows, True) if arm == "omega" else None})
    return data


def descriptor_distance(first, second):
    a, b = first["defect_degrees"], second["defect_degrees"]
    ha, hb = first["residual_histogram"], second["residual_histogram"]
    keys = set(map(str, ha)) | set(map(str, hb))
    return sum(abs(x - y) for x, y in zip(a, b)) + sum(abs(ha.get(k, ha.get(int(k), 0)) - hb.get(k, hb.get(int(k), 0))) for k in keys)


def derive_seed(master, identity):
    text = json.dumps([master, identity], separators=(",", ":"))
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def align(first, second, arm, rng, budget):
    best, best_distance = second, distance(first, second)
    if arm == "omega":
        for _ in range(64):
            budget.check()
            candidate = relabel(second, random_frame(rng))
            d = distance(first, candidate)
            if d < best_distance:
                best, best_distance = candidate, d
    else:
        # Finite heuristic alignment; no claim of minimum graph-edit distance.
        for _ in range(256):
            budget.check()
            a, b = rng.sample(range(99), 2)
            perm = list(range(99))
            perm[a], perm[b] = b, a
            candidate = relabel(best, perm)
            d = distance(first, candidate)
            if d < best_distance:
                best, best_distance = candidate, d
    return best


def objective_key(data, objective):
    if objective == "L1":
        return (data["L1"],)
    if objective == "L2":
        return (data["F"],)
    if objective == "Linf":
        return (data["Linf"], data["Nmax"], data["L1"])
    raise ValueError("Unknown objective: " + str(objective))
