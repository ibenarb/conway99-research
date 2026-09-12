"""Independent exact certificate/witness reconciliation; no external packages."""
from pathlib import Path
from itertools import permutations,product
from fractions import Fraction
from math import lcm
import json
BASE=Path(__file__).resolve().parents[2]
original=json.loads((BASE/'results/research_20260912/tau6_aggregate.json').read_text())['results']
certs=json.loads((BASE/'data/review_synthesis_20260912/tau6_farkas_18.json').read_text())
witnesses=json.loads((BASE/'data/review_synthesis_20260912/tau6_gram_44.json').read_text())
pairs=[(i,j) for i in range(6) for j in range(i,6)]
orbits={};lookup={}
for item in original:
    if item['status'].startswith('EXACT_NEGATIVE'):continue
    X=item['X'];G=[[6*(i==j)+6-5*X[i][j]-sum(X[i][k]*X[k][j] for k in range(6)) for j in range(6)] for i in range(6)]
    vectors={tuple(G[p[i]][p[j]] for i,j in pairs) for p in permutations(range(6))}
    index=item['atlas6_index'];orbits[index]=vectors
    for v in vectors:lookup.setdefault(v,set()).add(index)
assert len(orbits)==44
excluded=set();checked=[]
for cert in certs:
    y0=Fraction(cert['y0']);y=[Fraction(cert['y'].get(f'{i}{j}','0')) for i,j in pairs]
    scale=lcm(*(v.denominator for v in [y0]+y));c0=int(y0*scale);c=[int(v*scale) for v in y]
    # For any multiset of 27 binary columns, 27*c0+c.G <= 0.
    max_profile=max(c0+sum(a*r[i]*r[j] for a,(i,j) in zip(c,pairs)) for r in product((0,1),repeat=6))
    assert max_profile<=0
    found={}
    for index,vectors in orbits.items():
        best=max(27*c0+sum(a*b for a,b in zip(c,g)) for g in vectors)
        if best>0:found[index]=best
    assert found
    excluded.update(found)
    checked.append({'review_index':cert['atlas_index'],'integer_scale':scale,'max_profile_value':max_profile,'excluded_original_indices':found})
feasible=set();positive=[]
for position,item in enumerate(witnesses):
    if not item['binary_gram_feasible']:continue
    mult=item['profile_solution'];assert sum(mult.values())==27
    assert all(isinstance(n,int) and n>=0 and len(r)==6 and set(r)<=set('01') for r,n in mult.items())
    gram=tuple(sum(n*int(r[i])*int(r[j]) for r,n in mult.items()) for i,j in pairs)
    matches=lookup.get(gram,set());assert len(matches)==1
    index=next(iter(matches));assert index not in feasible
    feasible.add(index);positive.append({'review_list_position':position,'original_atlas6_index':index})
assert len(certs)==18 and len(excluded)==18 and len(feasible)==26
assert not feasible&excluded and feasible|excluded==set(orbits)
old={c['index'] for c in json.loads((BASE/'results/research_20260912/tau6_verified.json').read_text())['checks'] if c['status']=='EXACT_BOX_FARKAS_CERTIFICATE'}
result={'status':'PASS_EXACT_REVIEW_RECONCILIATION','gram_candidates':44,'certificate_count':18,'excluded':sorted(excluded),'gram_feasible':sorted(feasible),'old_four_exclusions':sorted(old),'old_four_in_review_exclusions':sorted(old&excluded),'remaining_after_union':sorted(feasible-old),'certificate_checks':checked,'witness_mapping':positive,'scope':'All relabelings checked to bridge incompatible atlas indices; necessary binary Gram model only.'}
(BASE/'results/review_synthesis_20260912/verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('certificate_checks','witness_mapping')},indent=2))
