#!/usr/bin/env python3
"""F02: Random Cayley graph on Z/99Z seeking λ=1."""
import argparse
import networkx as nx
import numpy as np
import hashlib
import sys

N = 99
DEG = 14

def cayley(S):
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for x in range(N):
        for s in S:
            G.add_edge(x, (x + s) % N)
    return G

def check_lambda1(G):
    A = nx.to_numpy_array(G, dtype=int)
    A2 = A @ A
    for u, v in G.edges():
        if A2[u, v] != 1:
            return False
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--max_tries', type=int, default=100000)
    p.add_argument('--out', default='-')
    args = p.parse_args()
    rng = np.random.default_rng(args.seed)
    positives = list(range(1, (N//2)+1))
    for t in range(args.max_tries):
        chosen = rng.choice(positives, size=DEG//2, replace=False)
        S = set(chosen) | set((-c) % N for c in chosen)
        if len(S) != DEG:
            continue
        G = cayley(S)
        if nx.is_regular(G, DEG) and check_lambda1(G):
            # graph6 (reuse simple encoder from F01 or nx.write_graph6 if available)
            # For brevity assume a working to_graph6; in practice implement as above
            print("FOUND", file=sys.stderr)
            # ... emit graph6 + sha
            sys.exit(0)
    print("FAILED", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    main()
