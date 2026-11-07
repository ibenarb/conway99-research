"""Screen coupled boundary stabilisers; no search pruning or production changes."""
from pathlib import Path
from collections import Counter
from itertools import combinations
import gzip,hashlib,json,sys
P=Path(__file__).resolve().parent
R=P.parent/'C2_L62_Direkt_20261103'
sys.path.insert(0,str(R))
from base_audit import specification
records={r['id']:r for r in json.loads((R/'representatives.json').read_text())['records']}
result=[]
for case in [20,77,78]:
    folder=P.parent/'C2_Rest55_20261104'/f'case_{case:04d}'
    file=folder/'boundary_states.json.gz'
    with gzip.open(file,'rt') as stream:package=json.load(stream)
    record=records[case]
    pairs,w,perm,d,g,k,_=specification(record)
    d,g,k=d.tolist(),g.tolist(),k.tolist()
    for x,y in [(0,1),(2,3)]:
        q=list(range(12));q[x],q[y]=q[y],q[x]
        assert all(d[r]==d[q[r]] for r in range(12))
        assert all(g[r][s]==g[q[r]][q[s]] and k[r][s]==k[q[r]][q[s]] for r in range(12) for s in range(12))
    group=package['group'];bounds=package['representatives']
    group_set={tuple(p) for p in group}
    assert len(group_set)==len(group) and tuple(range(12)) in group_set
    assert all(tuple(p[q[i]] for i in range(12)) in group_set for p in group for q in group)
    assert all(set(p[2:4])=={2,3} for p in group)
    column_actions=set()
    masks=sorted({x for pair in bounds for x in pair})
    images=[]
    for p in group:
        assert sorted(p)==list(range(12)) and set(p[:2])=={0,1}
        assert all(p[i^1]==(p[i]^1) and p[record['M'][i]]==record['M'][p[i]] and p[record['E'][i]]==record['E'][p[i]] for i in range(12))
        assert all(d[r][c]==d[p[r]][p[c]] for r in range(12) for c in range(12))
        assert all(g[r][s]==g[p[r]][p[s]] and k[r][s]==k[p[r]][p[s]] for r in range(12) for s in range(12))
        columns=[pairs.index(tuple(sorted((p[a],p[b])))) for a,b in pairs]
        assert all(columns[perm[c]]==perm[columns[c]] for c in range(60))
        column_actions.add(tuple(columns))
        table=[]
        for byte in range(8):
            table.append([sum(1<<columns[byte*8+b] for b in range(8) if byte*8+b<60 and v>>b&1) for v in range(256)])
        images.append({x:sum(table[b][x>>(8*b)&255] for b in range(8)) for x in masks})
    assert len(column_actions)==len(group)
    histogram=Counter();enhanced=[]
    for index,(a,b) in enumerate(bounds):
        assert a!=b
        eligible=[i for i,image in enumerate(images) if (image[a]==a and image[b]==b) or (image[a]==b and image[b]==a)]
        order=2*len(eligible)
        assert order>=4
        histogram[order]+=1
        if order>4:enhanced.append(dict(boundary=index,order=order,coupled_elements=eligible))
    result.append(dict(case=case,boundaries=len(bounds),coupled_group_order=len(group),
                       extended_boundary_stabiliser_orders=dict(sorted(histogram.items())),
                       stronger_than_S2=len(enhanced),fraction=len(enhanced)/len(bounds),
                       examples=enhanced[:12],source_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
answer=dict(status='SCREEN_COMPLETE',results=result,
            scope='Existing coupled vertex-automorphism group augmented by validated pure row swaps (0 1),(2 3). Boundary stabiliser only; no additional pruning or speed claim. Does not enumerate every possible row/column action.')
(P/'COUPLED_STABILISER_SCREEN.json').write_text(json.dumps(answer,indent=4)+'\n')
print(json.dumps(answer,indent=4))
