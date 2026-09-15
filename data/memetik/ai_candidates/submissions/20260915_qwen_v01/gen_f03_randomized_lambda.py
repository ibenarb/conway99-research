# generator_id: gen_f03_randomized_lambda
# Dateiname: gen_f03_randomized_lambda.py
# Sprache: Python 3.10
# Abhängigkeiten: None (Standardbibliothek: random, hashlib, json)
# Aufruf: python gen_f03_randomized_lambda.py

import random
import hashlib
import json

def graph6_string(adj):
    n = len(adj)
    if n <= 62: header = chr(n + 63)
    else: header = '~' + chr((n >> 18) + 63) + chr(((n >> 12) & 63) + 63) + chr(((n >> 6) & 63) + 63) + chr((n & 63) + 63)
    bits = [adj[i][j] for i in range(n) for j in range(i + 1, n)]
    chars = []
    for i in range(0, len(bits), 6):
        chunk = bits[i:i+6]
        val = sum(bit << (5 - idx) for idx, bit in enumerate(chunk))
        chars.append(chr((val << (6 - len(chunk))) + 63))
    return header + "".join(chars)

def get_lambda_bad(adj):
    n = len(adj)
    bad = 0
    for i in range(n):
        for j in range(i+1, n):
            if adj[i][j] == 1:
                if sum(1 for k in range(n) if adj[i][k] and adj[j][k]) != 1:
                    bad += 1
    return bad

def main():
    n, degree = 99, 14
    stubs = [i for i in range(n) for _ in range(degree)]
    for _ in range(100):
        random.shuffle(stubs)
        adj = [[0]*n for _ in range(n)]
        valid = all((u:=stubs[i], v:=stubs[i+1], u!=v, not adj[u][v], adj[u].__setitem__(v, 1), adj[v].__setitem__(u, 1), True)[-1] for i in range(0, len(stubs), 2))
        if valid: break

    best_adj = [row[:] for row in adj]
    best_bad = get_lambda_bad(adj)
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if adj[i][j]]
    
    for _ in range(2000):
        i1, i2 = random.sample(range(len(edges)), 2)
        a, b = edges[i1]
        c, d = edges[i2]
        if len({a,b,c,d}) < 4 or adj[a][c] or adj[b][d]: continue
        
        adj[a][b] = adj[b][a] = adj[c][d] = adj[d][c] = 0
        adj[a][c] = adj[c][a] = adj[b][d] = adj[d][b] = 1
        edges[i1], edges[i2] = (a, c), (b, d)
        
        new_bad = get_lambda_bad(adj)
        if new_bad < best_bad:
            best_bad, best_adj = new_bad, [row[:] for row in adj]
            if best_bad == 0: break
        elif random.random() >= 0.05:
            adj[a][c] = adj[c][a] = adj[b][d] = adj[d][b] = 0
            adj[a][b] = adj[b][a] = adj[c][d] = adj[d][c] = 1
            edges[i1], edges[i2] = (a, b), (c, d)
            
    g6 = graph6_string(best_adj)
    sha = hashlib.sha256((g6 + '\n').encode('ascii')).hexdigest()
    print(json.dumps({"graph6": g6, "sha256": sha}, indent=2))

if __name__ == "__main__":
    main()
