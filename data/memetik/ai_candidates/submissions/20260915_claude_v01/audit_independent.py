import collections
import hashlib
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
PAIRS = [p for p in itertools.combinations(range(14),2) if p[1] != p[0]+7]
IDX = {p:i for i,p in enumerate(PAIRS)}

def decode(path):
    raw=path.read_bytes();s=raw.decode('ascii').rstrip('\n')
    assert raw==(s+'\n').encode() and s[:4]=='~?@b' and len(s)==813
    values=[ord(c)-63 for c in s[4:]]
    assert all(0<=v<64 for v in values)
    bits=[(v>>b)&1 for v in values for b in range(5,-1,-1)]
    adj=[set() for _ in range(99)];k=0
    for j in range(1,99):
        for i in range(j):
            if bits[k]:adj[i].add(j);adj[j].add(i)
            k+=1
    assert not any(bits[k:])
    return raw,adj

def validate(path,arm):
    raw,adj=decode(path)
    assert all(len(a)==14 for a in adj)
    if arm=='omega':
        assert adj[0]==set(range(1,15))
        for a in range(14):
            assert adj[a+1]=={0,1+(a+7)%14}|{15+j for j,p in enumerate(PAIRS) if a in p}
        for j,p in enumerate(PAIRS):
            assert adj[15+j]&set(range(15))=={a+1 for a in p}
            hn={k-15 for k in adj[15+j] if k>=15}
            assert len(hn)==12
            for a in range(14):
                assert sum(a in PAIRS[k] for k in hn)==2-int(a in p)-int((a+7)%14 in p)
    hist=collections.Counter();mu=collections.Counter();lam=collections.Counter()
    for i in range(99):
        for j in range(i+1,99):
            c=len(adj[i]&adj[j]);edge=j in adj[i]
            (lam if edge else mu)[c]+=1
            hist[c+int(edge)-2]+=1
    if arm=='lambda':assert lam=={1:693}
    pi=[0]+[1+(a+1)%14 for a in range(14)]+[15+IDX[tuple(sorted(((a+1)%14,(b+1)%14)))] for a,b in PAIRS]
    linf=max(map(abs,hist))
    return {'arm':arm,'status':'PASS','sha256':hashlib.sha256(raw).hexdigest(),
            'W':sum(v for r,v in hist.items() if r),'L1':sum(abs(r)*v for r,v in hist.items()),
            'F':sum(r*r*v for r,v in hist.items()),'Linf':linf,'Nmax':sum(v for r,v in hist.items() if abs(r)==linf),
            'lambda_bad_edges':sum(v for c,v in lam.items() if c!=1),
            'lambda_histogram':dict(sorted(lam.items())),'mu_histogram':dict(sorted(mu.items())),
            'z14_translation_invariant':all({pi[j] for j in adj[i]}==adj[pi[i]] for i in range(99))},adj

if __name__=='__main__':
    report={};graphs={};provided=json.loads((ROOT/'bewertung.json').read_text())
    for number,name,arm in [(1,'A','omega'),(2,'B','omega'),(3,'C','lambda')]:
        r,adj=validate(ROOT/f'kandidat_{number:02d}.g6',arm)
        for key in ['W','L1','F','Linf']:assert r[key]==provided[name][key]
        assert {str(k):v for k,v in r['mu_histogram'].items()}==provided[name]['mu_verteilung']
        if arm=='omega':
            h=json.loads((ROOT/f'cand_{name}.json').read_text())
            assert all(set(row)=={v-15 for v in adj[i+15] if v>=15} for i,row in enumerate(h))
        else:
            triples=json.loads((ROOT/'cand_C.json').read_text());inc=collections.Counter();edges=[]
            for t in triples:assert len(set(t))==3;inc.update(t);edges.extend(tuple(sorted(e)) for e in itertools.combinations(t,2))
            assert len(triples)==231 and set(inc.values())=={7} and len(set(edges))==693
            assert set(edges)=={(i,j) for i in range(99) for j in adj[i] if i<j}
        report[name]=r;graphs[name]=adj
    report['pairwise_nonisomorphic_by_invariants']=all(report[a]['mu_histogram']!=report[b]['mu_histogram'] for a,b in itertools.combinations('ABC',2))
    ea={(i,j) for i in range(15,99) for j in graphs['A'][i] if i<j}
    eb={(i,j) for i in range(15,99) for j in graphs['B'][i] if i<j}
    report['H_edge_symmetric_difference_A_B']=len(ea^eb)
    report['H_shared_edges_A_B']=len(ea&eb)
    assert len(ea^eb)==provided['hamming_A_B']
    print(json.dumps(report,indent=4))
