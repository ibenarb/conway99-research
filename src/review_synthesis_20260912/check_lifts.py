"""Independent finite end-to-end controls and nonexact-quotient counterexamples."""
from pathlib import Path
from itertools import product
import sys,json
import numpy as np
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'src/research_20260912'))
from f3_lift import phase_u

def test(R):
    m=len(R);k=int(R[0].sum());I=np.eye(m,dtype=np.int64);B=(R+I)%3
    edges=[(i,j) for i in range(m) for j in range(i+1,m) if R[i,j]]
    exact=np.array_equal(R@R+R-(k-2)*I,6*np.ones((m,m),dtype=np.int64))
    checked=srg_count=boxed_count=false=0;example=None
    for phases in product(range(3),repeat=len(edges)):
        Z=np.zeros_like(R);A=np.zeros((3*m,3*m),dtype=np.int64)
        for i in range(m):
            if R[i,i]==2:A[3*i:3*i+3,3*i:3*i+3]=np.ones((3,3),dtype=np.int64)-np.eye(3,dtype=np.int64)
        for (i,j),z in zip(edges,phases):
            Z[i,j]=z;Z[j,i]=-z
            for a in range(3):
                for b in range(3):
                    ok=((b-a)%3==(-z)%3) if R[i,j]==1 else ((b-a)%3!=z)
                    A[3*i+a,3*j+b]=A[3*j+b,3*i+a]=int(ok)
        U=phase_u(R,Z)
        boxed=not np.any((B@Z+Z@B-Z)%3) and not np.any((B@U+U@B-U-B-I-2+Z@Z)%3)
        srg=bool(np.all(A.sum(axis=1)==k) and np.array_equal(A@A+A-(k-2)*np.eye(3*m,dtype=np.int64),2*np.ones_like(A)))
        checked+=1;srg_count+=srg;boxed_count+=boxed
        if boxed and not srg:
            false+=1
            if example is None:example={'R':R.tolist(),'Z':Z.tolist(),'A':A.tolist(),'quotient_residual':(R@R+R-(k-2)*I-6).tolist()}
        if exact:assert boxed==srg
    return {'assignments':checked,'exact':exact,'srg':srg_count,'boxed':boxed_count,'false_positives':false,'example':example}
controls=[]
for R in (np.ones((3,3),dtype=np.int64)+np.eye(3,dtype=np.int64),2*(np.ones((3,3),dtype=np.int64)-np.eye(3,dtype=np.int64))):
    r=test(R);assert r['assignments']==27 and r['srg']==r['boxed']==9
    controls.append(r)
R=np.array([[0,2,2,1],[2,0,2,1],[2,2,0,1],[1,1,1,2]],dtype=np.int64)
r=test(R);assert not r['exact'] and r['false_positives']>0
out={'status':'PASS_END_TO_END_AND_COUNTEREXAMPLE','rook_controls':controls,'nonexact_quotient':r,'scope':'Two exhaustive 27-phase positive controls and all 729 phases of the specified nonexact quotient; no BvLS reproduction.'}
(BASE/'results/review_synthesis_20260912/lifts.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in r.items() if k!='example'})
