"""Cached static Omega supports; bit-parallel, state-specific compatibility.

Same finite product catalogue as escape-0.2.0, no symmetry quotient. The
H-dependent masks are recomputed for each state, never reused after a trade.
"""
from functools import lru_cache
import random
import sys

from common import core, load

# Historical operators import their companion as `core`.
# This process imports no other research package under that name.
sys.modules.setdefault("core", core)
reference = load("comparison_reference_operators", "experiments/memetik/escape_0_2/operators.py")
MASK = (1 << 84) - 1


@lru_cache(maxsize=2)
def catalogue(length):
    return tuple(tuple(v) for v in reference.signed_vectors(length, random.Random(0)))


def compatible(rows, x):
    plus = minus = MASK
    used = 0
    for u, sign in x:
        adjacent = rows[15 + u] >> 15
        positive = (MASK ^ adjacent) if sign > 0 else adjacent
        plus &= positive
        minus &= MASK ^ positive
        used |= 1 << u
    plus &= MASK ^ used
    minus &= MASK ^ used
    return {**{v: 1 for v in core.vertices(plus)},
            **{v: -1 for v in core.vertices(minus)}}


def omega_moves(rows, family, rng=None, budget=None):
    rng = rng or random.Random(0)
    left, right = map(int, family.split("x"))
    vectors = catalogue(left)
    order = list(range(len(vectors)))
    rng.shuffle(order)
    seen = set()
    for counter, index in enumerate(order):
        if budget and counter % 16 == 0:
            budget.check()
        x = vectors[index]
        signs = compatible(rows, x)
        if len(signs) < right:
            continue
        for y in reference.restricted_vectors(signs, right):
            deleted, added = [], []
            for u, sx in x:
                for v, sy in y:
                    (added if sx * sy > 0 else deleted).append(core.edge(u + 15, v + 15))
            move = tuple(sorted(deleted)), tuple(sorted(added))
            if move not in seen:
                seen.add(move)
                yield move


class MoveSource(reference.MoveSource):
    def __init__(self, rows, arm, rng, budget):
        super().__init__(rows, arm, rng, budget)
        if arm == "omega":
            self.streams = {name: iter(omega_moves(rows, name, rng, budget)) for name in self.weights}
