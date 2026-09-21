"""Two isolated hypotheses: persistent family selection or cyclic apex trades."""
import bootstrap
from common import core
from search import key
import fast_moves
from itertools import combinations
from collections import Counter


def cycle_move(rows, triples, tips, direction=1):
    """Three disjoint existing triangles, cyclically permuted apex vertices."""
    if direction not in (-1, 1) or len(triples) != 3 or len(tips) != 3:
        return None
    if any(len(set(t)) != 3 or a not in t for t, a in zip(triples, tips)):
        return None
    if len(set(v for t in triples for v in t)) != 9:
        return None
    if any(not (rows[u] & (1 << v)) for t in triples for u, v in combinations(t, 2)):
        return None
    bases = [tuple(v for v in t if v != a) for t, a in zip(triples, tips)]
    deleted = tuple(sorted(core.edge(tips[i], v) for i in range(3) for v in bases[i]))
    added = tuple(sorted(core.edge(tips[(i+direction) % 3], v) for i in range(3) for v in bases[i]))
    if any(rows[u] & (1 << v) for u, v in added):
        return None
    move = deleted, added
    if not fast_moves.reference.lambda_preserved(rows, move):
        return None
    return move


def quota_parent(population, target, rng):
    family = rng.choice(sorted({p['family'] for p in population}))
    pool = [p for p in population if p['family'] == family]
    if rng.random() < 0.8:
        return min(rng.choices(pool, k=3), key=lambda p: key(p['scores'], target))
    return rng.choice(pool)


def quota_select(population, children, arm, target, rng, epoch, families):
    """At least one representative per family forever; use spare slots up to 4.

    Global elite two, protected representatives, quality to 12, random to 16.
    Quotas are lower bounds when enough distinct candidates exist, not clones.
    """
    if arm != 'lambda' or len(population) != 16:
        raise ValueError('Expected sixteen lambda candidates')
    unique = {}
    for p in population + children:
        unique.setdefault(p['class'], p)
    ordered = sorted(unique.values(), key=lambda p: (key(p['scores'], target), p['state']))
    chosen = ordered[:2]
    for count in range(1, 5):
        for family in sorted(families):
            if sum(p['family'] == family for p in chosen) >= count:
                continue
            options = [p for p in ordered if p['family'] == family and p not in chosen]
            if options:
                chosen.append(options[0])
    for p in ordered:
        if len(chosen) >= 12:
            break
        if p not in chosen:
            chosen.append(p)
    rest = [p for p in ordered if p not in chosen]
    chosen.extend(rng.sample(rest, 16-len(chosen)))
    if len(chosen) != 16 or set(p['family'] for p in chosen) != set(families):
        raise ValueError('Lost protected family or population size')
    return chosen


def cycle_moves(rows, rng=None, budget=None):
    """Enumerate directed compatibility 3-cycles of oriented triangles.

    Pair compatibility exactly checks each prospective new edge, but the
    final validator also checks unchanged edges incident to the support.
    """
    triangles = fast_moves.reference.triangles(rows)
    oriented = [(t, a, tuple(v for v in t if v != a)) for t in triangles for a in t]
    if rng:
        rng.shuffle(oriented)
    masks = [sum(1 << v for v in t) for t, _, _ in oriented]
    base_masks = [sum(1 << v for v in base) for _, _, base in oriented]
    outgoing = [set() for _ in oriented]
    incoming = [set() for _ in oriented]
    for i, (tri, tip, base) in enumerate(oriented):
        if budget:
            budget.check()
        without = [rows[v] & ~(1 << tip) for v in base]
        for j, (_, other_tip, _) in enumerate(oriented):
            if masks[i] & masks[j] or rows[other_tip] & base_masks[i]:
                continue
            other_row = rows[other_tip] & ~base_masks[j]
            if any(row & other_row for row in without):
                continue
            outgoing[i].add(j)
            incoming[j].add(i)
    seen = set()
    for i in range(len(oriented)):
        if budget:
            budget.check()
        for j in sorted(outgoing[i]):
            if j <= i:
                continue
            for k in sorted(outgoing[j] & incoming[i]):
                if k <= i or masks[j] & masks[k]:
                    continue
                indices = (i, j, k)
                move = cycle_move(rows, [oriented[v][0] for v in indices], [oriented[v][1] for v in indices])
                if move is not None and move not in seen:
                    seen.add(move)
                    yield move


class CycleSource(fast_moves.MoveSource):
    """Finite old catalogue plus general cycle3; each stream is state specific."""
    def __init__(self, rows, arm, rng, budget):
        if arm != 'lambda':
            raise ValueError('Lambda only')
        super().__init__(rows, arm, rng, budget)
        self.weights = {'apex': 72, 'rotation': 8, 'cycle3': 20}
        self.streams['cycle3'] = iter(cycle_moves(rows, rng, budget))
