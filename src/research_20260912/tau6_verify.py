"""Independent coverage and integer-witness checks; exact Farkas certificates if found."""
from fractions import Fraction
from functools import reduce
from itertools import combinations, permutations
from math import lcm, gcd
from pathlib import Path
import json
import numpy as np
import networkx as nx
from scipy.optimize import linprog
from tau6_aggregate import build

BASE=Path(__file__).resolve().parents[2]
source=json.loads((BASE/'results/research_20260912/tau6_aggregate.json').read_text())
pairs=list(combinations(range(6),2))
index={e:i for i,e in enumerate(pairs)}
perms=list(permutations(range(6)))
covered=set()
for item in source['results']:
    X=np.array(item['X'],dtype=np.int64)
    edges=[(i,j) for i,j in pairs if X[i,j]]
    orbit=set()
    for p in perms:
        orbit.add(sum(1<<index[tuple(sorted((p[i],p[j])))] for i,j in edges))
    assert not covered & orbit
    covered.update(orbit)
assert covered==set(range(1<<15))
checks=[]
for item in source['results']:
    X=np.array(item['X'],dtype=np.int64)
    if item['status']=='EXACT_AGGREGATE_FEASIBLE':
        A,b,u,columns,profiles=build(X)
        assert [list(v) for v in columns]==item['columns']
        z=np.array(item['witness'],dtype=np.int64)
        assert np.array_equal(A.toarray().astype(np.int64)@z,b.astype(np.int64))
        assert np.all(z>=0) and np.all(z<=u)
        counts = {mask: int(z[i]) for i, mask in enumerate(item['profile_masks'])}
        bits = {mask: [(mask >> q) & 1 for q in range(6)] for mask in counts}
        expected = 6*np.eye(6,dtype=np.int64)+6-X@X-5*X
        assert sum(counts.values()) == 27
        assert all(sum(counts[m]*bits[m][i]*bits[m][j] for m in counts) == expected[i,j] for i in range(6) for j in range(6))
        ds = {m: 0 for m in counts}
        dl = {m: 0 for m in counts}
        cross = {m: [0]*6 for m in counts}
        for value, (kind, i, j) in zip(z, columns):
            if kind == 'n':
                continue
            m, q = item['profile_masks'][i], item['profile_masks'][j]
            assert sum(a*b for a,b in zip(bits[m],bits[q])) <= (4 if kind == 'l' else 5)
            for left,right in ((m,q),(q,m)):
                (dl if kind == 'l' else ds)[left] += int(value)
                for coordinate in range(6):
                    cross[left][coordinate] += int(value)*(2 if kind == 'l' else 1)*bits[right][coordinate]
        for m in counts:
            r = bits[m]
            assert ds[m] == (10-sum(r))*counts[m]
            assert dl[m] == 2*counts[m]
            assert all(cross[m][j] == (6-3*r[j]-sum(r[i]*int(X[i,j]) for i in range(6)))*counts[m] for j in range(6))
        checks.append({'index':item['atlas6_index'],'status':'EXACT_INTEGER_WITNESS_REPLAY_AND_DIRECT_SEMANTICS'})
    elif item['status']=='SOLVER_INFEASIBLE_UNCERTIFIED':
        A,b,u,_,_=build(X)
        lp=linprog(np.zeros(len(u)),A_eq=A,b_eq=b,bounds=(0,None),method='highs')
        record={'index':item['atlas6_index'],'primal_LP_status':int(lp.status),'status':'NO_EXACT_EXCLUSION'}
        if lp.status==2:
            dual=linprog(-b,A_ub=A.T,b_ub=np.zeros(len(u)),bounds=[(-1,1)]*len(b),method='highs')
            if dual.x is not None:
                dense=A.toarray().astype(np.int64)
                for scale in (1,2,3,6,12,24,120,1000,10000,100000,1000000):
                    w=[int(round(float(v)*scale)) for v in dual.x]
                    products=[sum(int(dense[i,j])*w[i] for i in range(len(w))) for j in range(len(u))]
                    lhs=sum(int(b[i])*w[i] for i in range(len(w)))
                    bound=sum(int(u[j])*max(0,products[j]) for j in range(len(u)))
                    if lhs>bound:
                        record.update(status='EXACT_BOX_FARKAS_CERTIFICATE',dual_integers=w,lhs=lhs,box_upper=bound,gap=lhs-bound)
                        break
        checks.append(record)
output={'status':'PASS_EXHAUSTIVE_X_COVERAGE_AND_EXACT_WITNESSES','labelled_X_covered':len(covered),
        'isomorphism_classes':156,'checks':checks,
        'scope':'Exact dual checks concern the necessary aggregate relaxation, not a full graph/lift.'}
(BASE/'results/research_20260912/tau6_verified.json').write_text(json.dumps(output,indent=4)+'\n')
print(json.dumps({**output,'checks':[{k:v for k,v in r.items() if k!='dual_integers'} for r in checks]},indent=4))
