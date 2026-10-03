"""Independent full adjacency-matrix validation, no SAT/row-check reuse."""
from itertools import combinations


def verify_complete(g, rows):
    if set(rows) != set(range(g.n)):
        raise ValueError('not every H row is present')
    n = 1 + g.b + g.n
    adjacency = [[0] * n for _ in range(n)]
    def edge(u, v):
        adjacency[u][v] = adjacency[v][u] = 1
    for a in range(g.b):
        edge(0, 1 + a)
    for a in range(g.m):
        edge(1 + a, 1 + a + g.m)
    for u, pair in enumerate(g.labels):
        if rows[u] < 0 or rows[u] >> g.n:
            raise ValueError('H row out of bounds')
        for a in pair:
            edge(1 + a, 1 + g.b + u)
        for v in range(g.n):
            adjacency[1 + g.b + u][1 + g.b + v] = (rows[u] >> v) & 1
    for u in range(n):
        if adjacency[u][u] or sum(adjacency[u]) != 2 * g.m:
            raise ValueError('full graph diagonal or degree')
    for u, v in combinations(range(n), 2):
        if adjacency[u][v] != adjacency[v][u]:
            raise ValueError('full graph not symmetric')
        common = sum(adjacency[u][w] * adjacency[v][w] for w in range(n))
        if common != (1 if adjacency[u][v] else 2):
            raise ValueError('full graph common-neighbor count')
    return {'status': 'SRG_FOUND_VERIFIED', 'm': g.m,
            'parameters': [n, 2 * g.m, 1, 2], 'pairs_checked': n * (n - 1) // 2,
            'adjacency_lists': [[v for v in range(n) if adjacency[u][v]] for u in range(n)]}
