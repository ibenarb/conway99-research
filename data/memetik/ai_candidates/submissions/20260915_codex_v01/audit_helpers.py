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

