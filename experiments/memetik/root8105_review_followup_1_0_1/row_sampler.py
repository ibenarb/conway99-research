"""Exact count/unrank of a necessary local row proposal at arbitrary depth.

The proposal enforces target margins, symmetry, pair equations with all built
rows and zero-star consequences. It does NOT claim the count of the historical
full-star projection. A SAT membership gate checks that projection separately.
Inverse-probability weighting includes rejected proposals. No survivor-biased
resampling and no truncated SAT enumeration masquerading as uniform sampling.
"""
import bootstrap
import itertools
from functools import lru_cache
from matching import edge_key


class RowProposal:
    def __init__(self, g, rows, target, assigned=None, cache_size=200000):
        self.g, self.target = g, target
        g.verify(rows)
        forced, forbidden = set(), {target}
        for u, mask in rows.items():
            (forced if mask >> target & 1 else forbidden).add(u)
        for (u, v), bit in (assigned or {}).items():
            if target in (u, v):
                (forced if bit else forbidden).add(v if u == target else u)
        for u, mask in rows.items():
            ns = [v for v in range(g.n) if mask >> v & 1]
            for v in ns:
                if g.sets[u] & g.sets[v]:
                    # Completed-star equation for adjacent overlapping labels is zero.
                    if v == target:
                        forbidden.update(ns)
                    elif target in ns:
                        forbidden.add(v)
        self.built = sorted(rows)
        ks = [2 - (rows[u] >> target & 1) - len(g.sets[u] & g.sets[target]) for u in self.built]
        ds = g.margins(target)
        for v in forced:
            for c in g.labels[v]:
                ds[c] -= 1
            for j, u in enumerate(self.built):
                ks[j] -= rows[u] >> v & 1
        self.allowed = {g.labels[v]: (v, tuple(j for j, u in enumerate(self.built) if rows[u] >> v & 1))
                        for v in range(g.n) if v not in forced | forbidden}
        self.fixed = sum(1 << v for v in forced)
        self.initial = tuple(ds), tuple(ks)
        self.rec = lru_cache(cache_size)(self._rec)
        self.total = 0 if forced & forbidden else self.rec(*self.initial)

    def choices(self, ds, ks):
        a = next(i for i, d in enumerate(ds) if d)
        rest = [b for b in range(a + 1, self.g.b) if ds[b] and (a, b) in self.allowed]
        for ns in itertools.combinations(rest, ds[a]):
            dd, kk, mask = list(ds), list(ks), 0
            dd[a] = 0
            for b in ns:
                dd[b] -= 1
                v, flags = self.allowed[(a, b)]
                mask |= 1 << v
                for j in flags:
                    kk[j] -= 1
            yield tuple(dd), tuple(kk), mask

    def _rec(self, ds, ks):
        if any(d < 0 for d in ds) or any(k < 0 for k in ks):
            return 0
        edges = sum(ds) // 2
        if any(k > edges for k in ks):
            return 0
        if not any(ds):
            return int(not any(ks))
        return sum(self.rec(dd, kk) for dd, kk, _ in self.choices(ds, ks))

    def unrank(self, rank):
        if not 0 <= rank < self.total:
            raise ValueError('proposal rank outside exact range')
        ds, ks = self.initial
        row = self.fixed
        while any(ds):
            for dd, kk, mask in self.choices(ds, ks):
                weight = self.rec(dd, kk)
                if rank < weight:
                    ds, ks, row = dd, kk, row | mask
                    break
                rank -= weight
            else:
                raise AssertionError('proposal unranking exhausted')
        return row
