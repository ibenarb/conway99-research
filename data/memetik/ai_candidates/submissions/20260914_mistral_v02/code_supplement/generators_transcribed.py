"""Transcription of supplied executable statements; prose/comments omitted.
No algorithmic correction. Functions are called by audit_execution.py.
"""
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from itertools import combinations


def generate_omega_conway():
    C = np.zeros((14, 14), dtype=int)
    for a in range(14):
        C[a][(a + 7) % 14] = 1
    all_pairs = list(combinations(range(14), 2))
    C_pairs = set(((a, (a + 7) % 14) for a in range(7)))
    V2_pairs = [p for p in all_pairs if p not in C_pairs]
    assert len(V2_pairs) == 84
    P = np.zeros((14, 84), dtype=int)
    for i, (x, y) in enumerate(V2_pairs):
        P[x][i] = 1
        P[y][i] = 1
    H = np.zeros((84, 84), dtype=int)
    for i in range(84):
        for j in range(i + 1, 84):
            set_i = set(V2_pairs[i])
            set_j = set(V2_pairs[j])
            intersection = set_i & set_j
            union = set_i | set_j
            if len(intersection) != 1:
                continue
            c_pairs_in_union = 0
            for (a, b) in C_pairs:
                if a in union and b in union:
                    c_pairs_in_union += 1
            if c_pairs_in_union == 1:
                H[i][j] = 1
                H[j][i] = 1
    A = np.zeros((99, 99), dtype=int)
    A[0, 1:15] = 1
    A[1:15, 0] = 1
    A[1:15, 1:15] = C
    A[1:15, 15:] = P
    A[15:, 1:15] = P.T
    A[15:, 15:] = H
    row_sums = A.sum(axis=1)
    assert np.all(row_sums == 14), f"Zeilensummen: {row_sums}"
    import networkx as nx
    G = nx.from_numpy_array(A)
    graph6 = nx.generate_graph6(G, header=False)
    return graph6, A


def generate_tridecomp():
    n = 99
    triangles = []
    for i in range(0, n, 3):
        triangles.append((i, i+1, i+2))
    A = np.zeros((n, n), dtype=int)
    for tri in triangles:
        a, b, c = tri
        A[a][b] = A[b][a] = 1
        A[a][c] = A[c][a] = 1
        A[b][c] = A[c][b] = 1
    for u in range(n):
        neighbors = set(np.where(A[u] == 1)[0])
        candidates = [v for v in range(n) if v != u and A[u][v] == 0]
        np.random.shuffle(candidates)
        added = 0
        for v in candidates:
            if added >= 12:
                break
            common_neighbors = 0
            for w in neighbors:
                if A[v][w] == 1:
                    common_neighbors += 1
            if common_neighbors == 1:
                A[u][v] = A[v][u] = 1
                neighbors.add(v)
                added += 1
    row_sums = A.sum(axis=1)
    assert np.all(row_sums == 14), f"Zeilensummen: {row_sums}"
    import networkx as nx
    G = nx.from_numpy_array(A)
    graph6 = nx.generate_graph6(G, header=False)
    return graph6, A


import random
from collections import defaultdict


def generate_randfill(seed=42):
    random.seed(seed)
    n = 99
    target_degree = 14
    A = np.zeros((n, n), dtype=int)
    degrees = np.zeros(n, dtype=int)
    adjacency = defaultdict(set)

    def can_add_edge(u, v):
        if u == v or A[u][v] == 1:
            return False
        if degrees[u] >= target_degree or degrees[v] >= target_degree:
            return False
        common = adjacency[u] & adjacency[v]
        if len(common) != 0:
            return False
        for w in adjacency[u]:
            if v in adjacency[w]:
                return False
        for w in adjacency[v]:
            if u in adjacency[w]:
                return False
        return True

    edges_to_add = [(u, v) for u in range(n) for v in range(u + 1, n)]
    random.shuffle(edges_to_add)
    for u, v in edges_to_add:
        if can_add_edge(u, v):
            A[u][v] = A[v][u] = 1
            degrees[u] += 1
            degrees[v] += 1
            adjacency[u].add(v)
            adjacency[v].add(u)
    if not np.all(degrees == target_degree):
        for u in range(n):
            if degrees[u] < target_degree:
                for v in range(n):
                    if u != v and A[u][v] == 0 and can_add_edge(u, v):
                        A[u][v] = A[v][u] = 1
                        degrees[u] += 1
                        degrees[v] += 1
                        adjacency[u].add(v)
                        adjacency[v].add(u)
                        if degrees[u] == target_degree:
                            break
    row_sums = A.sum(axis=1)
    assert np.all(row_sums == 14), f"Zeilensummen: {row_sums}"
    import networkx as nx
    G = nx.from_numpy_array(A)
    graph6 = nx.generate_graph6(G, header=False)
    return graph6, A


def compute_metrics(A):
    n = A.shape[0]
    A2 = A @ A
    W = 0
    L1 = 0
    F = 0
    Linf = 0
    for i in range(n):
        for j in range(i + 1, n):
            r_ij = A2[i][j] + A[i][j] - 2
            if r_ij != 0:
                W += 1
                L1 += abs(r_ij)
                F += r_ij ** 2
                Linf = max(Linf, abs(r_ij))
    return W, L1, F, Linf
