"""Bounded continuous weighted-profile check of the 26 verified Gram survivors."""
from pathlib import Path
import sys,json
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src/research_20260912'))
from tau6_aggregate import build
items=json.loads((BASE/'results/research_20260912/tau6_aggregate.json').read_text())['results']
indices=json.loads((BASE/'results/review_synthesis_20260912/verification.json').read_text())['gram_feasible']
out=[]
for index in indices:
    A,b,u,_,_=build(np.array(items[index]['X'],dtype=np.int64))
    sol=linprog(np.zeros(len(u)),A_eq=A,b_eq=b,bounds=list(zip(np.zeros(len(u)),u)),method='highs',options={'time_limit':10})
    record={'index':index,'status':int(sol.status),'message':sol.message}
    if sol.status==0:
        z=[Fraction(float(v)).limit_denominator(1000000) for v in sol.x]
        totals=[Fraction(0) for _ in b]
        for col,value in enumerate(z):
            assert 0<=value<=int(u[col])
            if value:
                for q in range(A.indptr[col],A.indptr[col+1]):
                    totals[int(A.indices[q])]+=int(A.data[q])*value
        record['rational_reconstruction_verified']=(totals==[Fraction(int(v)) for v in b])
        if record['rational_reconstruction_verified']:
            record['exact_rational_witness']={str(i):str(v) for i,v in enumerate(z) if v}
        record['variables']=len(z)
        record['all_integral']=all(v.denominator==1 for v in z)
    out.append(record)
result={'scope':'Continuous weighted aggregate relaxation; rational witness provided only when exact replay succeeds; otherwise numerical feasibility only. No general integer-feasibility claim. 10-second solver cap per type.','results':out}
(BASE/'results/review_synthesis_20260912/remaining_lp.json').write_text(json.dumps(result,indent=2)+'\n')
from collections import Counter
print(dict(Counter(v['status'] for v in out)))
