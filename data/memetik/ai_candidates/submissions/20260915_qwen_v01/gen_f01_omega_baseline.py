# generator_id: gen_f01_omega_baseline
# Dateiname: gen_f01_omega_baseline.py
# Sprache: Python 3.10
# Abhängigkeiten: None (Standardbibliothek: random, hashlib, json)
# Aufruf: python gen_f01_omega_baseline.py

import random
import hashlib
import json

def graph6_string(adj):
    n = len(adj)
    if n <= 62:
        header = chr(n + 63)
    else:
        header = '~' + chr((n >> 18) + 63) + chr(((n >> 12) & 63) + 63) + chr(((n >> 6) & 63) + 63) + chr((n & 63) + 63)
    bits = []
    for i in range(n):
        for j in range(i + 1, n):
            bits.append(adj[i][j])
    chars = []
    for i in range(0, len(bits), 6):
        chunk = bits[i:i+6]
        val = sum(bit << (5 - idx) for idx, bit in enumerate(chunk))
        val = val << (6 - len(chunk))
        chars.append(chr(val + 63))
    return header + "".join(chars)

def main():
    pairs = []
    for i in range(14):
        for j in range(i+1, 14):
            if (j - i) % 14 != 7:
                pairs.append((i, j))
    
    adj = [[0]*99 for _ in range(99)]
    for i in range(14):
        adj[0][i+1] = adj[i+1][0] = 1
    for i in range(7):
        u, v = i + 1, (i + 7) % 14 + 1
        adj[u][v] = adj[v][u] = 1
    for k_idx, (u, v) in enumerate(pairs):
        outer = 15 + k_idx
        adj[u+1][outer] = adj[outer][u+1] = 1
        adj[v+1][outer] = adj[outer][v+1] = 1
        
    stubs = [i for i in range(84) for _ in range(12)]
    for _ in range(100):
        random.shuffle(stubs)
        valid = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i+1]
            if u == v or adj[15+u][15+v] == 1:
                valid = False
                break
            adj[15+u][15+v] = adj[15+v][15+u] = 1
        if valid:
            break
            
    g6 = graph6_string(adj)
    sha = hashlib.sha256((g6 + '\n').encode('ascii')).hexdigest()
    print(json.dumps({"graph6": g6, "sha256": sha}, indent=2))

if __name__ == "__main__":
    main()
