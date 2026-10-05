"""Historical F, depth one only. Exact int64 edge DP; Python-int unranking.
Derived from Claude's width_dp.py (2026-10-04). No new SRG filters here.
"""
import hashlib
import itertools
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

MODEL = 'F-historical-core-1.0.1-depth1'
ROOT_SHA = 'c525d03be144a7493c3239340c6263dcb8a29b5521e5d3b152ce43afe90cac41'


class Geo:
    def __init__(self, m=7):
        self.m, self.b = m, 2 * m
        self.labels = list(p for p in itertools.combinations(range(self.b), 2) if p[1] - p[0] != m)
        self.n = len(self.labels)
        self.sets = list(map(frozenset, self.labels))
        self.index = {p: i for i, p in enumerate(self.labels)}
        self.inc = [{i for i, p in enumerate(self.labels) if a in p} for a in range(self.b)]

    def margins(self, t):
        a, b = self.labels[t]
        special = {a, b, (a + self.m) % self.b, (b + self.m) % self.b}
        return [1 if a in special else 2 for a in range(self.b)]

    def verify(self, rows):
        for u, r in rows.items():
            if not 0 <= u < self.n or r < 0 or r >> self.n or r >> u & 1:
                raise ValueError('row identity/bounds/diagonal')
            if [sum(r >> v & 1 for v in vs) for vs in self.inc] != self.margins(u):
                raise ValueError('border margins')
            for v, s in rows.items():
                if v < u:
                    e = r >> v & 1
                    if e != (s >> u & 1):
                        raise ValueError('symmetry')
                    if (r & s).bit_count() != 2 - e - len(self.sets[u] & self.sets[v]):
                        raise ValueError('common neighbors')


def overflow_bound(g):
    return sum(math.comb(g.n, k) for k in range(2 * g.m - 1))


def constraints(g, root, t):
    if not 0 < t < g.n:
        raise ValueError('depth-one target must differ from root 0')
    neighbors = {v for v in range(g.n) if root >> v & 1}
    e = int(t in neighbors)
    k = 2 - e - len(g.sets[t] & g.sets[0])
    forced = {0} if e else set()
    forbidden = {t} | (set() if e else {0})
    if e:
        forbidden |= {v for v in neighbors if len(g.sets[v] & g.sets[0]) == 1}
    return forced, forbidden, neighbors - {t}, k


def count(g, t, forced=(), forbidden=(), flagged=(), k=0):
    # Every cell counts subsets of at most degree labels, including eliminated axes.
    if overflow_bound(g) > np.iinfo(np.int64).max:
        raise ValueError('int64 bound not proved for this geometry; use arbitrary integers')
    forced, forbidden, flagged = set(forced), set(forbidden) | {t}, set(flagged)
    use = [i for i in range(g.n) if i not in forbidden]
    if k < 0 or not forced <= set(use):
        return 0
    margins = g.margins(t)
    last = {c: i for i in use for c in g.labels[i]}
    if len(last) != g.b:
        return 0
    axes = list(range(g.b))
    a = np.zeros(tuple(d + 1 for d in margins) + (k + 1,), dtype=np.int64)
    a[(0,) * a.ndim] = 1
    for i in use:
        x, y = g.labels[i]
        px, py = axes.index(x), axes.index(y)
        src, dst = [slice(None)] * a.ndim, [slice(None)] * a.ndim
        src[px], dst[px] = slice(0, margins[x]), slice(1, margins[x] + 1)
        src[py], dst[py] = slice(0, margins[y]), slice(1, margins[y] + 1)
        if i in flagged:
            src[-1], dst[-1] = slice(0, k), slice(1, k + 1)
        shifted = np.zeros_like(a)
        shifted[tuple(dst)] = a[tuple(src)]
        a = shifted if i in forced else a + shifted
        for c in (x, y):
            if last[c] == i:
                p = axes.index(c)
                a = np.take(a, margins[c], axis=p)
                axes.pop(p)
    return int(a[k])


def width(g, root, t):
    return count(g, t, *constraints(g, root, t))


def load_roots(path=None):
    path = Path(path) if path else Path(__file__).with_name('roots.tsv')
    if hashlib.sha256(path.read_bytes()).hexdigest() != ROOT_SHA:
        raise ValueError('roots.tsv SHA256 mismatch')
    g, roots = Geo(), []
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        fields = line.split('\t')
        labels = [tuple(map(int, v.split('-'))) for v in fields[3:]]
        if len(labels) != 12 or len(set(labels)) != 12:
            raise ValueError('duplicate/incomplete root')
        row = sum(1 << g.index[p] for p in labels)
        g.verify({0: row})
        typ = sum(bool(g.sets[v] & {7, 8}) for v in range(g.n)
                  if row >> v & 1 and g.sets[v] & g.sets[0])
        roots.append({'id': int(fields[0]), 'stab': int(fields[1]), 'orbit': int(fields[2]),
                      'row': hex(row), 'type': typ})
    if [r['id'] for r in roots] != list(range(1, 8106)):
        raise ValueError('root ids')
    if sum(r['orbit'] for r in roots) != 56011010 or any(r['orbit'] * r['stab'] != 7680 for r in roots):
        raise ValueError('orbit/stabilizer audit')
    return roots


class VertexSampler:
    """Independent arbitrary-int vertex recursion; rank -> row is a bijection.

    Uniformity follows from rng.randrange(total) and exact unranking; no float weights.
    This depth-one sampler is not a general-depth or m11 performance promise.
    """
    def __init__(self, g, root, t):
        self.g, self.t = g, t
        forced, forbidden, flags, k = constraints(g, root, t)
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

    def choices(self, ds, k):
        a = next(i for i, d in enumerate(ds) if d)
        rest = [b for b in range(a + 1, self.g.b) if ds[b] and (a, b) in self.allowed]
        for nb in itertools.combinations(rest, ds[a]):
            dd, kk, mask = list(ds), k, 0
            dd[a] = 0
            for b in nb:
                dd[b] -= 1
                i, flag = self.allowed[(a, b)]
                kk -= flag
                mask |= 1 << i
            yield tuple(dd), kk, mask

    def _rec(self, ds, k):
        if k < 0 or any(d < 0 for d in ds):
            return 0
        if not any(ds):
            return int(k == 0)
        return sum(self.rec(dd, kk) for dd, kk, _ in self.choices(ds, k))

    def unrank(self, rank):
        if not 0 <= rank < self.total:
            raise ValueError('rank out of range')
        ds, k = self.initial
        row = self.fixed
        while any(ds):
            for dd, kk, mask in self.choices(ds, k):
                weight = self.rec(dd, kk)
                if rank < weight:
                    ds, k, row = dd, kk, row | mask
                    break
                rank -= weight
            else:
                raise AssertionError('unrank exhausted')
        return row

    def sample(self, rng):
        if not self.total:
            raise ValueError('empty projection')
        return self.unrank(rng.randrange(self.total))


def deterministic_target(rows, widths):
    """State-based rule R-min-all-v1, for later work only; includes zero widths."""
    eligible = [t for t in widths if t not in rows]
    return min(eligible, key=lambda t: (widths[t], t)) if eligible else None
