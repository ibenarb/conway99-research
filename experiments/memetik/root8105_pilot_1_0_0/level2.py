"""Measure x/u role exchange on the selected roots' complete two-star objects.

This benchmark never prunes the row search. Its sample is not closed under
rerooting; counts are equivalence classes within the selected subset only.
"""
import argparse
import json
from pathlib import Path

import pynauty
from core import Geometry, atomic


def matchings(items, g):
    if not items:
        yield []
        return
    u = items[0]
    for i, v in enumerate(items[1:], 1):
        if not (g.sets[u] & g.sets[v]):
            for rest in matchings(items[1:i] + items[i + 1:], g):
                yield [(u, v)] + rest


def graph(g, row, matching, swap):
    neighbors = [u for u in range(g.n) if (row >> u) & 1]
    position = {u: 16 + i for i, u in enumerate(neighbors)}
    adjacency = {u: set() for u in range(28)}
    def edge(u, v):
        adjacency[u].add(v)
        adjacency[v].add(u)
    for a in range(14):
        edge(0, 2 + a)
    for a in range(7):
        edge(2 + a, 2 + a + 7)
    for a in (0, 1):
        edge(1, 2 + a)
    for u in neighbors:
        edge(1, position[u])
        for a in g.labels[u]:
            edge(2 + a, position[u])
    for u, v in matching:
        edge(position[u], position[v])
    colors = [{0, 1}, set(range(2, 28))] if swap else [{0}, {1}, set(range(2, 28))]
    return pynauty.Graph(28, adjacency_dict={u: list(v) for u, v in adjacency.items()}, vertex_coloring=colors)


def benchmark(roots):
    g = Geometry()
    ordered, unordered = set(), set()
    count = 0
    per_root = []
    for root in roots:
        row = int(root['row'], 16)
        remaining = [u for u in range(g.n) if (row >> u) & 1 and not (g.sets[u] & g.sets[0])]
        local = 0
        for pairing in matchings(remaining, g):
            ordered.add(pynauty.certificate(graph(g, row, pairing, False)))
            unordered.add(pynauty.certificate(graph(g, row, pairing, True)))
            count += 1
            local += 1
        assert local == root['matchings']
        per_root.append({'root_id': root['id'], 'raw_local_matchings': local})
    return {'status': 'PASS', 'roots': len(roots), 'raw_two_star_objects': count,
            'distinct_ordered_roles_within_sample': len(ordered),
            'distinct_unordered_roles_within_sample': len(unordered),
            'search_pruning_enabled': False, 'scope': 'Selected subset only, not all 8105 roots',
            'per_root': per_root}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    a = p.parse_args()
    directory = Path(a.directory)
    result = benchmark(json.loads((directory / 'selected_roots.json').read_text()))
    atomic(directory / 'level2_benchmark.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'per_root'}))
