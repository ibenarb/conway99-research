"""Necessary per-state filters, model F+LD+CAP-v1. NOT an exact child counter."""
import itertools

MODEL = 'F+LD+CAP-v1-per-state'


def label_forbidden(g, rows):
    forbidden = set()
    for row in rows.values():
        neighbors = [v for v in range(g.n) if row >> v & 1]
        for v, w in itertools.combinations(neighbors, 2):
            if g.sets[v] & g.sets[w]:
                forbidden.add((v, w))
    return forbidden


def check(g, rows, label_disjoint=True, capacity=True):
    g.verify(rows)
    forbidden = label_forbidden(g, rows) if label_disjoint else set()

    def term(v, w):
        if v == w:
            return 0, 0
        fixed = (rows[v] >> w & 1) if v in rows else ((rows[w] >> v & 1) if w in rows else None)
        banned = tuple(sorted((v, w))) in forbidden
        if fixed is not None:
            return fixed, fixed
        return 0, 0 if banned else 1

    for v, w in forbidden:
        if (v in rows and rows[v] >> w & 1) or (w in rows and rows[w] >> v & 1):
            return {'pass': False, 'reason': 'label_disjoint', 'pair': [v, w]}
    if not capacity:
        return {'pass': True, 'reason': None}
    for v in range(g.n):
        if v in rows:
            continue
        equations = [('degree', range(g.n), 2 * g.m - 2)]
        equations += [('border:' + str(c), vs, g.margins(v)[c]) for c, vs in enumerate(g.inc)]
        equations += [('pair:' + str(u), [w for w in range(g.n) if row >> w & 1],
                       2 - (row >> v & 1) - len(g.sets[u] & g.sets[v])) for u, row in rows.items()]
        for name, neighbors, target in equations:
            lo, hi = 0, 0
            for w in neighbors:
                x, y = term(v, w)
                lo, hi = lo + x, hi + y
            if not lo <= target <= hi:
                return {'pass': False, 'reason': 'capacity', 'row': v, 'equation': name,
                        'fixed_ones': lo, 'possible_ones': hi, 'target': target}
    return {'pass': True, 'reason': None}
