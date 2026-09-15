# helpers.py – minimale graph6 + Score-Funktionen
import networkx as nx
import numpy as np
import hashlib

def to_graph6(G):
    # (implementierung wie in gen_F01)
    pass

def sha256_graph6(g6: str) -> str:
    return hashlib.sha256((g6 + '\n').encode('ascii')).hexdigest()

def full_scores(G):
    """Berechnet W, L1, F, Linf, Nmax, lambda_bad_edges, residual_histogram."""
    A = nx.to_numpy_array(G, dtype=int)
    n = A.shape[0]
    A2 = A @ A
    W = L1 = F = 0
    Linf = 0
    hist = {}
    lambda_bad = 0
    Nmax = 0
    for i in range(n):
        for j in range(i+1, n):
            r = int(A2[i, j] + A[i, j] - 2)
            hist[str(r)] = hist.get(str(r), 0) + 1
            if r != 0:
                W += 1
                L1 += abs(r)
                F += r * r
            if abs(r) > Linf:
                Linf = abs(r)
                Nmax = 1
            elif abs(r) == Linf:
                Nmax += 1
            if A[i, j] == 1 and A2[i, j] != 1:
                lambda_bad += 1
    if Linf == 0:
        Nmax = 4851
    return {
        "W": W, "L1": L1, "F": F, "Linf": Linf, "Nmax": Nmax,
        "lambda_bad_edges": lambda_bad,
        "residual_histogram": hist
    }
