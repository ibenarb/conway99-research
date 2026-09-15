#!/usr/bin/env python3
"""F01: Greedy triangle decomposition aiming at 14-regular λ=1 graph on 99 verts."""
import argparse
import networkx as nx
import numpy as np
import hashlib
import sys

N = 99
DEG = 14

def is_lambda1(G):
    A = nx.to_numpy_array(G, dtype=int)
    A2 = A @ A
    for u, v in G.edges():
        if A2[u, v] != 1:
            return False
    return True

def greedy_triangles(seed, max_tries):
    rng = np.random.default_rng(seed)
    for trial in range(max_tries):
        G = nx.Graph()
        G.add_nodes_from(range(N))
        degrees = np.zeros(N, dtype=int)
        # random order of potential triangles
        candidates = [(i, j, k) for i in range(N) for j in range(i+1, N) for k in range(j+1, N)]
        rng.shuffle(candidates)
        for i, j, k in candidates:
            if degrees[i] >= DEG or degrees[j] >= DEG or degrees[k] >= DEG:
                continue
            if G.has_edge(i, j) or G.has_edge(i, k) or G.has_edge(j, k):
                continue
            # add triangle
            G.add_edges_from([(i, j), (i, k), (j, k)])
            degrees[i] += 2
            degrees[j] += 2
            degrees[k] += 2
            if degrees.min() == DEG and degrees.max() == DEG:
                if is_lambda1(G) and nx.is_regular(G, DEG):
                    return G
        # if stuck, continue to next trial
    return None

def graph_to_graph6(G):
    # NetworkX does not ship graph6 writer for arbitrary labels; implement minimal
    # Standard graph6 (no header)
    n = G.order()
    # bit string of upper triangle
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if G.has_edge(i, j) else 0)
    # pad to multiple of 6
    while len(bits) % 6:
        bits.append(0)
    data = []
    for t in range(0, len(bits), 6):
        val = 0
        for b in bits[t:t+6]:
            val = (val << 1) | b
        data.append(val + 63)
    # length encoding
    if n < 63:
        header = bytes([n + 63])
    else:
        # simplified; for n=99 use 3-byte
        header = bytes([126, (n >> 12) + 63, ((n >> 6) & 63) + 63, (n & 63) + 63])
    return (header + bytes(data)).decode('ascii')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--max_tries', type=int, default=1000)
    p.add_argument('--out', type=str, default='-')
    args = p.parse_args()
    G = greedy_triangles(args.seed, args.max_tries)
    if G is None:
        print("FAILED", file=sys.stderr)
        sys.exit(1)
    g6 = graph_to_graph6(G)
    if args.out == '-':
        print(g6)
    else:
        with open(args.out, 'w') as f:
            f.write(g6 + '\n')
    # SHA256 of g6 + LF
    h = hashlib.sha256((g6 + '\n').encode('ascii')).hexdigest()
    print(f"# SHA256: {h}", file=sys.stderr)

if __name__ == '__main__':
    main()
