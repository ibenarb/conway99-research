"""Exact integer scoring and complete state-specific lambda catalogues."""
import bootstrap
from common import core
import fast_moves
from strategy import cycle_moves
from collections import Counter, defaultdict
from itertools import combinations

FIELDS = ('W', 'L1', 'F', 'Linf', 'Nmax')


def compact(histogram):
    maximum = max((abs(r) for r, n in histogram.items() if n), default=0)
    return {'W': sum(n for r, n in histogram.items() if r),
            'L1': sum(abs(r)*n for r, n in histogram.items()),
            'F': sum(r*r*n for r, n in histogram.items()), 'Linf': maximum,
            'Nmax': sum(n for r, n in histogram.items() if abs(r) == maximum)}


class Scorer:
    def __init__(self, rows):
        self.rows = rows
        self.residuals = {(i,j): (rows[i] & rows[j]).bit_count()+((rows[i] >> j) & 1)-2
                          for i in range(len(rows)) for j in range(i)}
        self.histogram = Counter(self.residuals.values())
        self.scores = compact(self.histogram)

    def evaluate(self, move):
        child = core.apply_move(self.rows, move)
        touched = {v for edges in move for edge in edges for v in edge}
        histogram = self.histogram.copy()
        for i in touched:
            for j in range(len(child)):
                if i == j or (j in touched and j > i):
                    continue
                pair = (max(i,j), min(i,j))
                histogram[self.residuals[pair]] -= 1
                histogram[(child[i] & child[j]).bit_count()+((child[i] >> j) & 1)-2] += 1
        return child, compact(histogram)


def pivot_candidates(rows):
    by_point = defaultdict(list)
    for triple in fast_moves.reference.triangles(rows):
        for point in triple:
            by_point[point].append(tuple(v for v in triple if v != point))
    for point, pairs in sorted(by_point.items()):
        for (x,y), (u,v) in combinations(pairs,2):
            for a,b in ((x,y),(y,x)):
                yield point, a, b, u, v


def pivots(rows, guard):
    for i, (p,x,y,u,v) in enumerate(pivot_candidates(rows)):
        if i % 64 == 0:
            guard.check()
        if rows[x] & (1 << u) or rows[y] & (1 << v):
            continue
        if (rows[x] & rows[u]).bit_count() == 1 and (rows[y] & rows[v]).bit_count() == 1:
            yield (tuple(sorted((core.edge(x,y),core.edge(u,v)))),
                   tuple(sorted((core.edge(x,u),core.edge(y,v)))))


def apex_exact(rows, guard):
    """Reviewer M4, exact integer common-neighbor table; final tests independent."""
    ts = fast_moves.reference.triangles(rows)
    cn = [[(a & b).bit_count() for b in rows] for a in rows]
    masks = {t: sum(1 << v for v in t) for t in ts}
    seen = set()
    for count, (left,right) in enumerate(combinations(ts,2)):
        if count % 64 == 0:
            guard.check()
        if masks[left] & masks[right]:
            continue
        for c in left:
            a,b = (v for v in left if v != c)
            for d in right:
                e,f = (v for v in right if v != d)
                if rows[d] & ((1 << a)|(1 << b)) or rows[c] & ((1 << e)|(1 << f)):
                    continue
                cd = (rows[c] >> d) & 1
                ae,af = (rows[a] >> e) & 1, (rows[a] >> f) & 1
                be,bf = (rows[b] >> e) & 1, (rows[b] >> f) & 1
                if (cn[a][d],cn[b][d],cn[c][e],cn[c][f]) != (cd+ae+af,cd+be+bf,ae+be+cd,af+bf+cd):
                    continue
                move = (tuple(sorted(core.edge(u,v) for u,v in ((a,c),(b,c),(d,e),(d,f)))),
                        tuple(sorted(core.edge(u,v) for u,v in ((a,d),(b,d),(c,e),(c,f)))))
                if move not in seen:
                    seen.add(move)
                    yield move


def catalogue(rows, include_cycles, guard):
    seen = set()
    sources = [('apex',apex_exact(rows,guard)),('pivot',pivots(rows,guard))]
    if include_cycles:
        sources.append(('cycle3',cycle_moves(rows,None,guard)))
    for name, stream in sources:
        for move in stream:
            guard.check()
            if move not in seen:
                seen.add(move)
                yield name,move
