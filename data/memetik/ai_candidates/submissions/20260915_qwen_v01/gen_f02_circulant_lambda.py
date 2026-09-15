# generator_id: gen_f02_circulant_lambda
# Dateiname: gen_f02_circulant_lambda.py
# Sprache: Python 3.10
# Abhängigkeiten: None (Standardbibliothek: random, hashlib, json)
# Aufruf: python gen_f02_circulant_lambda.py

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

def main():
    best_S, best_bad = None, 1000
    for _ in range(100000):
        S = set(random.sample(range(1, 50), 7))
        bad = sum(1 for s in S if sum(1 for x in S if x != s and (s - x) % 99 in S) != 1)
        if bad < best_bad:
            best_bad, best_S = bad, sorted(list(S))
            if bad == 0: break
            
    adj = [[0]*99 for _ in range(99)]
    for i in range(99):
        for s in best_S:
            adj[i][(i + s) % 99] = adj[(i + s) % 99][i] = 1
            
    g6 = graph6_string(adj)
    sha = hashlib.sha256((g6 + '\n').encode('ascii')).hexdigest()
    print(json.dumps({"generators": best_S, "graph6": g6, "sha256": sha}, indent=2))

if __name__ == "__main__":
    main()
