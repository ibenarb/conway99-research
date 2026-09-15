# Dateiname: conway99_verifier.py
# Sprache: Python 3.10
# Abhängigkeiten: json, hashlib, sys
# Aufruf: python conway99_verifier.py <pfad_zur_json_datei>

import json
import hashlib
import sys

def graph6_to_adj(g6):
    if g6.startswith('~'):
        n = ((ord(g6[1])-63)<<18) | ((ord(g6[2])-63)<<12) | ((ord(g6[3])-63)<<6) | (ord(g6[4])-63)
        data_start = 5
    else:
        n = ord(g6[0]) - 63
        data_start = 1
    
    bits = []
    for char in g6[data_start:]:
        val = ord(char) - 63
        for i in range(5, -1, -1):
            bits.append((val >> i) & 1)
    
    adj = [[0]*n for _ in range(n)]
    idx = 0
    for i in range(n):
        for j in range(i+1, n):
            if idx < len(bits):
                adj[i][j] = adj[j][i] = bits[idx]
                idx += 1
    return adj

def verify_candidate(c):
    cid = c.get("candidate_id", "UNKNOWN")
    print(f"\n--- Prüfe Kandidat: {cid} ---")
    
    # 1. Schema & Pflichtfelder
    required = ["candidate_id", "family_id", "arm", "status", "graph6", "graph6_sha256", "scores", "hard_checks"]
    if not all(k in c for k in required):
        return "FAIL: Fehlende Pflichtfelder"
        
    # 2. Graph6 Dekodierung
    try:
        adj = graph6_to_adj(c["graph6"])
    except Exception as e:
        return f"FAIL: graph6 Dekodierung fehlgeschlagen: {e}"
        
    n = len(adj)
    
    # 3. Prüfsumme
    expected_sha = hashlib.sha256((c["graph6"] + '\n').encode('ascii')).hexdigest()
    if c["graph6_sha256"] != expected_sha:
        return f"FAIL: SHA256 Mismatch. Erwartet: {expected_sha}, Gefunden: {c['graph6_sha256']}"
        
    # 4. Harte Bedingungen
    checks = c["hard_checks"]
    
    # order_99
    if n != 99:
        return "FAIL: order_99 verletzt"
    if checks.get("order_99") is False:
        return "FAIL: hard_checks.order_99 ist false"
        
    # simple_undirected & Nulldiagonale
    for i in range(n):
        if adj[i][i] != 0:
            return "FAIL: Nulldiagonale verletzt"
        for j in range(i+1, n):
            if adj[i][j] != adj[j][i]:
                return "FAIL: Symmetrie verletzt"
    if checks.get("simple_undirected") is False:
        return "FAIL: hard_checks.simple_undirected ist false"
        
    # regular_14
    for i in range(n):
        if sum(adj[i]) != 14:
            return f"FAIL: Regularität verletzt bei Knoten {i} (Grad: {sum(adj[i])})"
    if checks.get("regular_14") is False:
        return "FAIL: hard_checks.regular_14 ist false"
        
    # 5. Scores Neuberechnung
    A2 = [[0]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if adj[i][k]:
                for j in range(k, n):
                    if adj[k][j]:
                        A2[i][j] += 1
                        if i != j: A2[j][i] = A2[i][j]
                        
    scores = c["scores"]
    calc_W, calc_L1, calc_F, calc_Linf, calc_lambda_bad = 0, 0, 0, 0, 0
    hist = {}
    
    for i in range(n):
        for j in range(i+1, n):
            r = A2[i][j] + adj[i][j] - 2
            hist[str(r)] = hist.get(str(r), 0) + 1
            if r != 0:
                calc_W += 1
                calc_L1 += abs(r)
                calc_F += r * r
                if abs(r) > calc_Linf: calc_Linf = abs(r)
            if adj[i][j] == 1 and A2[i][j] != 1:
                calc_lambda_bad += 1
                
    calc_Nmax = hist.get(str(calc_Linf), 0) if calc_Linf > 0 else (n*(n-1)//2)
    
    if scores.get("W") != calc_W: return f"FAIL: Score W Mismatch ({scores.get('W')} != {calc_W})"
    if scores.get("L1") != calc_L1: return f"FAIL: Score L1 Mismatch"
    if scores.get("F") != calc_F: return f"FAIL: Score F Mismatch"
    if scores.get("Linf") != calc_Linf: return f"FAIL: Score Linf Mismatch"
    if scores.get("Nmax") != calc_Nmax: return f"FAIL: Score Nmax Mismatch"
    if scores.get("lambda_bad_edges") != calc_lambda_bad: return f"FAIL: Score lambda_bad_edges Mismatch"
    
    # Histogramm Summe
    if sum(hist.values()) != 4851:
        return f"FAIL: Histogramm Summe ist {sum(hist.values())}, erwartet 4851"
        
    # 6. Arm-spezifische Checks
    arm = c["arm"]
    if arm == "omega":
        if "omega_frame" not in c or c["omega_frame"] is None:
            return "FAIL: omega_frame fehlt für omega arm"
        # Rahmenpermutation Länge prüfen
        if len(c["omega_frame"].get("canonical_to_graph6", [])) != 99:
            return "FAIL: canonical_to_graph6 hat nicht Länge 99"
            
    if checks.get("lambda_edge_condition") is True and calc_lambda_bad > 0:
        return "FAIL: lambda_edge_condition ist true, aber lambda_bad_edges > 0"

    return "PASS"

def main():
    if len(sys.argv) < 2:
        print("Usage: python conway99_verifier.py <candidates.json>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if data.get("schema_version") != "conway99-candidates-1.0":
        print("FAIL: Ungültige schema_version")
        sys.exit(1)
        
    for c in data.get("candidates", []):
        result = verify_candidate(c)
        print(f"Ergebnis: {result}")

if __name__ == "__main__":
    main()
