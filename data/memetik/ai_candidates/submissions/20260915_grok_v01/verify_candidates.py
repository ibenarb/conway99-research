#!/usr/bin/env python3
"""Standalone verifier for the JSON block inside the Markdown submission."""
import json
import re
import sys
import hashlib
import networkx as nx
import numpy as np
from collections import Counter

def extract_json_block(md_text):
    m = re.search(r'```json\s*(\{.*?\})\s*```', md_text, re.DOTALL)
    if not m:
        raise ValueError("No JSON block found")
    return json.loads(m.group(1))

def decode_graph6(g6: str) -> nx.Graph:
    # Minimal decoder for standard graph6 (n<=62 or extended)
    # Production code should use a robust implementation or networkx.read_graph6
    # Here we assume networkx can handle it via temporary file or pure Python
    from io import StringIO
    # NetworkX 3.x supports
    return nx.from_graph6_bytes(g6.encode('ascii'))

def check_hard(G, arm, omega_frame=None):
    n = G.order()
    res = {
        "order_99": n == 99,
        "simple_undirected": nx.is_simple_path(G) is False and not any(u==v for u,v in G.edges()),  # rough
        "regular_14": nx.is_regular(G, 14),
        "lambda_edge_condition": None,
        "omega_frame_condition": None
    }
    # simple undirected more carefully
    A = nx.to_numpy_array(G, dtype=int)
    res["simple_undirected"] = (A == A.T).all() and (np.diag(A) == 0).all() and ((A == 0) | (A == 1)).all()
    if arm == "lambda":
        A2 = A @ A
        bad = 0
        for u, v in G.edges():
            if A2[u, v] != 1:
                bad += 1
        res["lambda_edge_condition"] = (bad == 0)
    elif arm == "omega":
        # Reconstruct frame from omega_frame permutation if given
        # Then check PH == 2J - (C+I)P and H 12-regular
        res["omega_frame_condition"] = None  # full implementation needs the permutation
        # Placeholder: user must supply complete check
    return res

def recompute_scores(G):
    # identical to helpers.full_scores
    A = nx.to_numpy_array(G, dtype=int)
    A2 = A @ A
    W = L1 = F = 0
    Linf = 0
    hist = Counter()
    lambda_bad = 0
    Nmax = 0
    for i in range(99):
        for j in range(i+1, 99):
            r = int(A2[i,j] + A[i,j] - 2)
            hist[str(r)] += 1
            if r != 0:
                W += 1
                L1 += abs(r)
                F += r*r
            ar = abs(r)
            if ar > Linf:
                Linf = ar
                Nmax = 1
            elif ar == Linf:
                Nmax += 1
            if A[i,j] and A2[i,j] != 1:
                lambda_bad += 1
    if Linf == 0:
        Nmax = 4851
    return {"W": W, "L1": L1, "F": F, "Linf": Linf, "Nmax": Nmax,
            "lambda_bad_edges": lambda_bad, "residual_histogram": dict(hist)}

def main(md_path):
    with open(md_path) as f:
        md = f.read()
    data = extract_json_block(md)
    assert data["schema_version"] == "conway99-candidates-1.0"
    ids = set()
    for c in data["candidates"]:
        cid = c["candidate_id"]
        if cid in ids:
            print(f"FAIL {cid}: duplicate id")
            continue
        ids.add(cid)
        status = "UNVERIFIED"
        reasons = []
        try:
            G = decode_graph6(c["graph6"])
            # checksum
            expected = c.get("graph6_sha256")
            if expected:
                got = hashlib.sha256((c["graph6"] + "\n").encode()).hexdigest()
                if got != expected:
                    reasons.append("SHA256 mismatch")
            hard = check_hard(G, c["arm"], c.get("omega_frame"))
            scores = recompute_scores(G)
            # compare reported vs recomputed
            for k in ["W","L1","F","Linf","Nmax","lambda_bad_edges"]:
                if c["scores"].get(k) is not None and c["scores"][k] != scores[k]:
                    reasons.append(f"score {k} mismatch")
            # hard checks
            required = ["order_99", "simple_undirected", "regular_14"]
            if c["arm"] == "lambda":
                required.append("lambda_edge_condition")
            elif c["arm"] == "omega":
                required.append("omega_frame_condition")
            for k in required:
                if hard.get(k) is not True:
                    reasons.append(f"hard {k} failed or null")
            if not reasons and all(hard.get(k) is True for k in required):
                status = "PASS"
            else:
                status = "FAIL" if reasons else "UNVERIFIED"
        except Exception as e:
            status = "FAIL"
            reasons.append(str(e))
        print(f"{status} {cid}: {'; '.join(reasons) if reasons else 'ok'}")
        # Isomorphie is separately reported as not_checked

if __name__ == "__main__":
    main(sys.argv[1])
