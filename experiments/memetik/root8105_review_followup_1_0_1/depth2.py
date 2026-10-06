"""Reviewer theorem at exactly two built H rows; exact restricted sampling."""
import bootstrap
from functools import lru_cache
from kernel import VertexSampler, constraints


def relation(g, root, target):
    e = (root >> target) & 1
    overlap = g.sets[0] & g.sets[target]
    return e, len(overlap)


def bad_common_neighbors(g, root, target):
    e, s = relation(g, root, target)
    neighbors = {v for v in range(g.n) if root >> v & 1 and v != target}
    if (e, s) == (1, 0):
        points = g.sets[0] | g.sets[target]
    elif (e, s) == (0, 1):
        c = next(iter(g.sets[0] & g.sets[target]))
        points = {c, (c + g.m) % g.b}
    else:
        return set()
    return {w for w in neighbors if g.sets[w] & points}


def predict(g, root, target, row):
    g.verify({0: root, target: row})
    e, s = relation(g, root, target)
    common = root & row
    assert common.bit_count() == 2 - e - s
    bad = bad_common_neighbors(g, root, target)
    rejects = any(common >> w & 1 for w in bad)
    ld = rejects and (e, s) == (1, 0)
    cap = rejects and (e, s) in ((1, 0), (0, 1))
    return {'F': True, 'F_LD': not ld, 'F_CAP': not cap, 'F_LD_CAP': not (ld or cap)}


class RestrictedSampler(VertexSampler):
    """Same exact ranking recursion, with additional required/forbidden bits.

    This samples the restricted set uniformly. It never samples and rejects
    from the unfiltered set. Class (0,1)/(1,0) has exactly one common neighbor,
    so banning every bad common neighbor implements the theorem in-generator.
    """
    def __init__(self, g, root, t, force=(), forbid=()):
        self.g, self.t = g, t
        forced, forbidden, flags, k = constraints(g, root, t)
        forced |= set(force)
        forbidden |= set(forbid)
        self.fixed = sum(1 << i for i in forced)
        self.allowed = {g.labels[i]: (i, int(i in flags)) for i in range(g.n)
                        if i not in forbidden | forced}
        margins = g.margins(t)
        for i in forced:
            for c in g.labels[i]:
                margins[c] -= 1
            k -= int(i in flags)
        self.initial = tuple(margins), k
        self.rec = lru_cache(None)(self._rec)
        self.total = 0 if forced & forbidden else self.rec(*self.initial)


def exact_split(g, root, target, historical_width):
    bad = sorted(bad_common_neighbors(g, root, target))
    good = RestrictedSampler(g, root, target, forbid=bad)
    good_width = good.total
    good.rec.cache_clear()
    pieces = []
    for w in bad:
        sampler = RestrictedSampler(g, root, target, force=[w])
        pieces.append({'common_neighbor': w, 'width': sampler.total})
        sampler.rec.cache_clear()
    rejected = sum(p['width'] for p in pieces)
    assert rejected + good_width == historical_width, (target, rejected, good_width, historical_width)
    return {'bad_common_neighbors': bad, 'bad_neighbor_conditional_widths': pieces,
            'historical_width': historical_width, 'accepted_width': good_width,
            'rejected_width': rejected, 'exact_partition_verified': True}
