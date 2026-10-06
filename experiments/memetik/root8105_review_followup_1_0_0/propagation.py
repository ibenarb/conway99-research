"""Necessary zero/one deductions and exact matching feasibility, never a heuristic prune."""
import bootstrap
import itertools
from matching import edge_key, neighborhoods, available_graph, feasible


def propagate(g, rows, extra=None):
    g.verify(rows)
    assigned = dict(extra or {})
    changed = True
    reason = None

    def value(u, v):
        if u == v:
            return 0
        fixed = (rows[u] >> v & 1) if u in rows else ((rows[v] >> u & 1) if v in rows else None)
        other = assigned.get(edge_key(u, v))
        if fixed is not None and other is not None and fixed != other:
            raise ValueError('assigned bit contradicts built row')
        return fixed if fixed is not None else other

    def impose(u, v, val):
        nonlocal changed
        old = value(u, v)
        if old is not None:
            return old == val
        assigned[edge_key(u, v)] = val
        changed = True
        return True

    try:
        # Every neighbor set of a completed row supplies LD zeros.
        for mask in rows.values():
            vs = [v for v in range(g.n) if mask >> v & 1]
            for v, w in itertools.combinations(vs, 2):
                if g.sets[v] & g.sets[w] and not impose(v, w, 0):
                    return {'pass': False, 'reason': 'LD_fixed_edge', 'assigned': assigned}
        # Every degree, border and built-row pair equation is necessary.
        equations = []
        for v in range(g.n):
            if v in rows:
                continue
            equations.append((v, list(range(g.n)), 2 * g.m - 2, 'degree'))
            equations.extend((v, sorted(g.inc[c]), k, 'border:' + str(c))
                             for c, k in enumerate(g.margins(v)))
            for u, mask in sorted(rows.items()):
                equations.append((v, [w for w in range(g.n) if mask >> w & 1],
                    2 - (mask >> v & 1) - len(g.sets[u] & g.sets[v]), 'pair:' + str(u)))
        while changed:
            changed = False
            for v, neighbors, target, name in equations:
                vals = [(w, value(v, w)) for w in neighbors]
                ones = sum(x == 1 for _, x in vals)
                free = [w for w, x in vals if x is None]
                if not ones <= target <= ones + len(free):
                    return {'pass': False, 'reason': 'capacity', 'row': v,
                            'equation': name, 'assigned': assigned}
                if free and (target == ones or target == ones + len(free)):
                    bit = int(target > ones)
                    for w in free:
                        assert impose(v, w, bit)
            for name, vertices, special, all_neighbors in neighborhoods(g, rows):
                for u in special:
                    for v in all_neighbors:
                        if v != u and not impose(u, v, 0):
                            return {'pass': False, 'reason': 'border_paired_H_edge', 'assigned': assigned}
                allowed, forced = available_graph(g, vertices, rows, assigned, name.startswith('N:'))
                if not feasible(vertices, allowed, forced):
                    return {'pass': False, 'reason': 'no_perfect_matching', 'set': name, 'assigned': assigned}
                # Required endpoints cannot use another edge in their matching set.
                for u, v in forced:
                    for w in vertices:
                        if w not in (u, v):
                            if not impose(u, w, 0) or not impose(v, w, 0):
                                return {'pass': False, 'reason': 'matching_degree', 'assigned': assigned}
                # Degree-one deductions; exact feasibility above handles odd barriers.
                occupied = {x for pair in forced for x in pair}
                for u in vertices:
                    if u in occupied:
                        continue
                    options = [v for v in vertices if v != u and v not in occupied and edge_key(u, v) in allowed]
                    if len(options) == 1:
                        if not impose(u, options[0], 1):
                            return {'pass': False, 'reason': 'matching_singleton', 'assigned': assigned}
        return {'pass': True, 'reason': reason, 'assigned': assigned}
    except ValueError:
        return {'pass': False, 'reason': 'fixed_assignment_conflict', 'assigned': assigned}
