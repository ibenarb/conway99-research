"""Independent direct validation of exported graph6, without CP-SAT or generator helpers."""
import collections
import hashlib
import itertools
import json
import pathlib

path = pathlib.Path('kandidat_42.g6')
raw = path.read_bytes()
s = raw.decode('ascii').rstrip('\n')
assert raw == (s+'\n').encode('ascii')
assert s[:4] == '~?@b' and len(s) == 813
values = [ord(c)-63 for c in s[4:]]
assert all(0<=v<64 for v in values)
bits = [(v>>b)&1 for v in values for b in range(5,-1,-1)]
adj = [set() for _ in range(99)]
k = 0
for j in range(1,99):
    for i in range(j):
        if bits[k]:
            adj[i].add(j)
            adj[j].add(i)
        k += 1
assert not any(bits[k:])
assert all(i not in adj[i] and len(adj[i])==14 for i in range(99))
assert all(i in adj[j] for i in range(99) for j in adj[i])
pairs = [p for p in itertools.combinations(range(14),2) if p[1] != p[0]+7]
assert adj[0] == set(range(1,15))
for a in range(14):
    expected = {0,1+(a+7)%14} | {15+j for j,p in enumerate(pairs) if a in p}
    assert adj[1+a] == expected
for j,pair in enumerate(pairs):
    assert adj[15+j] & set(range(15)) == {1+a for a in pair}
    hneighbors = {k-15 for k in adj[15+j] if k>=15}
    assert len(hneighbors) == 12
    for a in range(14):
        actual = sum(a in pairs[k] for k in hneighbors)
        expected = 2-int(a in pair)-int((a+7)%14 in pair)
        assert actual == expected
hist = collections.Counter()
bad = 0
for i in range(99):
    for j in range(i+1,99):
        common = len(adj[i]&adj[j])
        edge = j in adj[i]
        hist[common+int(edge)-2] += 1
        bad += int(edge and common!=1)
linf = max(map(abs,hist))
out = {'validation':'PASS','scope':'Graph6 bytes, simple99, regular14, full canonical frame, all1176 PH equations, all4851 pair scores',
       'sha256':hashlib.sha256(raw).hexdigest(),'graph6_bytes':len(raw),'arm':'omega',
       'W':sum(v for r,v in hist.items() if r), 'L1':sum(abs(r)*v for r,v in hist.items()),
       'F':sum(r*r*v for r,v in hist.items()), 'Linf':linf,
       'Nmax':sum(v for r,v in hist.items() if abs(r)==linf),'lambda_bad_edges':bad,
       'residual_histogram':dict(sorted(hist.items())), 'canonical_to_graph6':list(range(99)),
       'isomorphism_status':'not_checked', 'basin_novelty':'not_established'}
pathlib.Path('validation.json').write_text(json.dumps(out,indent=4)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='canonical_to_graph6'},indent=4))
