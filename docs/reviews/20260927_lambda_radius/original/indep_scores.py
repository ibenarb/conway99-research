"""Independent scoring of the three STARTS graphs with networkx only (no project code)."""
import json, hashlib, itertools, networkx as nx
starts = json.load(open('/home/claude/src/experiments/memetik/lambda_radius_1_0_0/STARTS.json'))
out = {}
for label, s in starts.items():
    G = nx.from_graph6_bytes(s['graph6'].encode())
    n = G.number_of_nodes(); degs = set(d for _, d in G.degree())
    A = {v: set(G[v]) for v in G}
    hist = {}
    lam_ok = True
    for u, v in itertools.combinations(G.nodes(), 2):
        c = len(A[u] & A[v]); a = 1 if v in A[u] else 0
        if a and c != 1: lam_ok = False
        r = c + a - 2
        hist[r] = hist.get(r, 0) + 1
    W = sum(k for r, k in hist.items() if r); L1 = sum(abs(r)*k for r, k in hist.items())
    F = sum(r*r*k for r, k in hist.items()); Linf = max(abs(r) for r in hist); Nmax = sum(k for r,k in hist.items() if abs(r)==Linf)
    # 4-cycles: Q = sum over pairs C(c_uv,2)
    Q = sum(len(A[u]&A[v])*(len(A[u]&A[v])-1)//2 for u,v in itertools.combinations(G.nodes(),2))//2  # each unoriented 4-cycle counted once (two diagonals)
    tri = sum(nx.triangles(G).values())//3
    out[label] = dict(n=n, degrees=sorted(degs), lambda1_every_edge=lam_ok, triangles=tri,
        hist={str(k):v for k,v in sorted(hist.items())},
        W=W, L1=L1, F=F, Linf=Linf, Nmax=Nmax, Q=Q, F_identity_4Q_minus_8316=4*(Q-2079),
        sum_nonedge_r=sum(r*k for r,k in hist.items()) ,
        state_sha=hashlib.sha256(s['graph6'].encode()).hexdigest(), state_claimed=s['state'],
        scores_claimed=s['scores'])
    out[label]['scores_match'] = all(out[label][k]==s['scores'][k] for k in ('W','L1','F','Linf','Nmax'))
    out[label]['state_match'] = out[label]['state_sha']==s['state']
json.dump(out, open('indep_scores.json','w'), indent=1)
for l,o in out.items():
    print(l, 'match', o['scores_match'], o['state_match'], 'W',o['W'],'L1',o['L1'],'F',o['F'],'Q',o['Q'],'4(Q-2079)=',o['F_identity_4Q_minus_8316'], 'sum r =',o['sum_nonedge_r'],'tri',o['triangles'],'lam',o['lambda1_every_edge'], 'hist',o['hist'])
