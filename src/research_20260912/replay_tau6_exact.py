"""Replay 116 exclusions with Python standard library only; no optimizer."""
from pathlib import Path
from itertools import combinations, permutations
from fractions import Fraction
import json
BASE=Path(__file__).resolve().parents[2]
source=json.loads((BASE/'results/research_20260912/tau6_aggregate.json').read_text())['results']
certs={r['index']:r for r in json.loads((BASE/'results/research_20260912/tau6_verified.json').read_text())['checks'] if r['status']=='EXACT_BOX_FARKAS_CERTIFICATE'}
def determinant(a):
    a=[[Fraction(v) for v in row] for row in a]; d=Fraction(1)
    for j in range(len(a)):
        pivot=next((i for i in range(j,len(a)) if a[i][j]),None)
        if pivot is None:return 0
        if pivot!=j:a[j],a[pivot]=a[pivot],a[j];d=-d
        v=a[j][j];d*=v
        for i in range(j+1,len(a)):
            f=a[i][j]/v
            for k in range(j+1,len(a)):a[i][k]-=f*a[j][k]
    return d
pairs=list(combinations(range(6),2)); positions={e:i for i,e in enumerate(pairs)}
covered=set(); exclusions=[]
for item in source:
    X=item['X']; edges=[(i,j) for i,j in pairs if X[i][j]]
    assert len(X)==6 and all(X[i][j]==X[j][i] and X[i][j] in (0,1) and (i!=j or X[i][j]==0) for i in range(6) for j in range(6))
    orbit={sum(1<<positions[tuple(sorted((p[i],p[j])))] for i,j in edges) for p in permutations(range(6))}
    assert not orbit&covered;covered|=orbit
    G=[[6*(i==j)+6-sum(X[i][k]*X[k][j] for k in range(6))-5*X[i][j] for j in range(6)] for i in range(6)]
    status=item['status']; index=item['atlas6_index']
    if status=='EXACT_NEGATIVE_GRAM_ENTRY':
        assert min(map(min,G))<0;exclusions.append(index)
    elif status=='EXACT_NEGATIVE_PRINCIPAL_MINOR':
        indices=item['witness']['indices']
        assert determinant([[G[i][j] for j in indices] for i in indices])==item['witness']['determinant']<0
        exclusions.append(index)
    elif index in certs:
        profiles=[]
        for mask in range(64):
            r=[(mask>>j)&1 for j in range(6)]
            t=[6-3*r[j]-sum(r[i]*X[i][j] for i in range(6)) for j in range(6)]
            if all(0<=v<=14-sum(r) for v in t):profiles.append((r,t))
        m=len(profiles); gram=[(i,j) for i in range(6) for j in range(i,6)]
        b=[27]+[G[i][j] for i,j in gram]+[0]*(8*m)
        w=certs[index]['dual_integers']; assert len(w)==len(b)
        products=[]; bounds=[]
        for i,(r,t) in enumerate(profiles):
            products.append(w[0]+sum(r[a]*r[c]*w[1+q] for q,(a,c) in enumerate(gram))-(10-sum(r))*w[22+8*i]-2*w[23+8*i]-sum(t[q]*w[24+8*i+q] for q in range(6)))
            bounds.append(27)
        for kind,threshold,upper,weight in ((0,5,135,1),(1,4,27,2)):
            for i in range(m):
                for j in range(i,m):
                    if sum(a*b for a,b in zip(profiles[i][0],profiles[j][0]))>threshold:continue
                    value=0
                    for left,right in ((i,j),(j,i)):
                        value+=w[22+8*left+kind]+weight*sum(profiles[right][0][q]*w[24+8*left+q] for q in range(6))
                    products.append(value);bounds.append(upper)
        lhs=sum(a*v for a,v in zip(b,w)); rhs=sum(u*max(0,v) for u,v in zip(bounds,products))
        assert lhs==certs[index]['lhs'] and rhs==certs[index]['box_upper'] and lhs>rhs
        exclusions.append(index)
assert covered==set(range(32768)) and len(exclusions)==116
output={'status':'PASS_STDLIB_EXACT_116_EXCLUSIONS','classes':156,'labelled_covered':32768,'excluded':116,'remaining':40,'four_dual_classes':sorted(certs),'scope':'Necessary weighted quotient profile model; not full tau6 exclusion.'}
(BASE/'results/research_20260912/tau6_exact_replay.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output))
