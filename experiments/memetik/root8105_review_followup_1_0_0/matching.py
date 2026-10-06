"""Exact general-graph perfect matchings with required and unavailable edges.

N_H(u) is NOT itself a perfect matching: its two border-paired vertices must
be removed first. L(c), on the other hand, is an entire perfect matching set.
No bipartite Hall assumption is used; subset recursion works on general graphs.
"""
import bootstrap
import itertools
from functools import lru_cache


def edge_key(u, v):
    return tuple(sorted((u, v)))


def neighborhoods(g, rows):
    out = []
    for u, mask in sorted(rows.items()):
        neighbors = [v for v in range(g.n) if mask >> v & 1]
        special = [v for v in neighbors if g.sets[u] & g.sets[v]]
        assert len(special) == 2
        residual = [v for v in neighbors if v not in special]
        out.append(('N:' + str(u), residual, special, neighbors))
    for c in range(g.b):
        out.append(('L:' + str(c), sorted(g.inc[c]), [], sorted(g.inc[c])))
    return out


def available_graph(g, vertices, rows, assignments=None, label_disjoint=False):
    assignments = assignments or {}
    allowed, forced = set(), set()
    for u, v in itertools.combinations(vertices, 2):
        k = (u, v) if u < v else (v, u)
        fixed = (rows[u] >> v & 1) if u in rows else ((rows[v] >> u & 1) if v in rows else assignments.get(k))
        permitted = not label_disjoint or not (g.sets[u] & g.sets[v])
        if fixed == 1:
            forced.add(k)
        if fixed != 0 and permitted:
            allowed.add(k)
    return allowed, forced


def prepare(vertices, allowed, forced):
    vertices = tuple(sorted(vertices))
    used = set()
    for u, v in forced:
        if (u, v) not in allowed or u in used or v in used:
            return None
        used.update((u, v))
    return tuple(v for v in vertices if v not in used)


def matchings(vertices, allowed, forced=frozenset()):
    rest = prepare(vertices, allowed, forced)
    if rest is None:
        return
    def rec(nodes):
        if not nodes:
            yield ()
            return
        u = nodes[0]
        for v in nodes[1:]:
            pair = edge_key(u, v)
            if pair in allowed:
                for tail in rec(tuple(x for x in nodes[1:] if x != v)):
                    yield (pair,) + tail
    for pairs in rec(rest):
        yield tuple(sorted(tuple(forced) + pairs))


def feasible(vertices, allowed, forced=frozenset()):
    rest = prepare(vertices, allowed, forced)
    if rest is None:
        return False
    @lru_cache(None)
    def rec(nodes):
        if not nodes:
            return True
        u = nodes[0]
        return any(edge_key(u, v) in allowed and rec(tuple(x for x in nodes[1:] if x != v))
                   for v in nodes[1:])
    return rec(rest)


def check(g, rows, assignments=None):
    assignments = assignments or {}
    for name, vertices, special, all_neighbors in neighborhoods(g, rows):
        for u in special:
            for v in all_neighbors:
                if u == v:
                    continue
                fixed = (rows[u] >> v & 1) if u in rows else ((rows[v] >> u & 1) if v in rows else assignments.get(edge_key(u, v)))
                if fixed == 1:
                    return {'pass': False, 'reason': 'border_paired_H_edge', 'set': name, 'pair': [u, v]}
        allowed, forced = available_graph(g, vertices, rows, assignments, name.startswith('N:'))
        if not feasible(vertices, allowed, forced):
            return {'pass': False, 'reason': 'no_perfect_matching', 'set': name,
                    'vertices': vertices, 'allowed': sorted(allowed), 'forced': sorted(forced)}
    return {'pass': True, 'reason': None}


def root_objects(g, root):
    import pynauty
    import historical_core as core
    rows = {0: root}
    _, vertices, special, neighbors = neighborhoods(g, rows)[0]
    allowed, forced = available_graph(g, vertices, rows, label_disjoint=True)
    raw = set(matchings(vertices, allowed, forced))
    generators, size1, size2, _, _ = pynauty.autgrp(core.Geometry(g.m).graph(rows))
    images = [[perm[g.b + v] - g.b for v in range(g.n)] for perm in generators]
    unseen = set(raw)
    classes = []
    while unseen:
        representative = min(unseen)
        orbit, queue = {representative}, [representative]
        while queue:
            item = queue.pop()
            for permutation in images:
                nxt = tuple(sorted(edge_key(permutation[u], permutation[v]) for u, v in item))
                if nxt not in raw:
                    raise ValueError('stabilizer action leaves admissible matching family')
                if nxt not in orbit:
                    orbit.add(nxt)
                    queue.append(nxt)
        unseen.difference_update(orbit)
        classes.append({'matching': representative, 'orbit_size': len(orbit)})
    assert sum(c['orbit_size'] for c in classes) == len(raw)
    return {'raw_count': len(raw), 'orbit_count': len(classes), 'classes': classes,
            'special_border_paired': special, 'residual_vertices': vertices,
            'stabilizer_order': round(size1 * 10 ** size2)}
