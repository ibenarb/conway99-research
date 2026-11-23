"""Principal-minor oracle, ambient positive controls, and 58 published local fixtures."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, product
from math import isqrt
import hashlib
import json
import random
import subprocess
import time
import own_local
from singleton_setup_v1 import determinant

BASE = Path(__file__).resolve().parent
def oracle(a):
    rank=0
    det=F(1)
    for size in range(1,len(a)+1):
        for indices in combinations(range(len(a)),size):
            value=determinant([[a[i][j] for j in indices] for i in indices])
            if value<0:
                return False,None,None
            if value>0:
                rank,det=size,value
    return True,rank,det

def square(x):
    return x>=0 and x.denominator==1 and isqrt(x.numerator)**2==x.numerator

def main():
    started=time.time()
    rng=random.Random(2026112201)
    cases=[]
    for a,b,c in product(range(-3,4),repeat=3):
        cases.append(('G',[[a,b],[b,c]],None))
    cases.append(('G',[],None))
    for n in range(1,7):
        for trial in range(30):
            a=[[0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i,n):
                    a[i][j]=a[j][i]=rng.randrange(-5,6)
            cases.append(('G',a,None))
        for dim in range(1,7):
            for trial in range(6):
                v=[[rng.randrange(-3,4) for _ in range(dim)] for _ in range(n)]
                a=[[sum(x*y for x,y in zip(v[i],v[j])) for j in range(n)] for i in range(n)]
                cases.append(('G',a,True))
    for sr in (10,11,12,13,14,15):
        for n in range(5):
            for k in (1,2):
                for trial in range(15):
                    dim=max(1,15-sr)
                    v=[[rng.randrange(-2,3) for _ in range(dim)] for _ in range(n+k)]
                    a=[[sum(x*y for x,y in zip(v[i],v[j])) for j in range(n+k)] for i in range(n+k)]
                    cases.append(('S',a,(n,sr,k)))
                    b=[row[:] for row in a]
                    b[-1][-1]-=rng.randrange(1,5)
                    cases.append(('S',b,(n,sr,k)))
    commands=[]
    for kind,a,data in cases:
        if kind=='G':
            commands.append(f'G {len(a)}')
        else:
            n,sr,k=data
            commands.append(f'S {n} {sr} 1 {k}')
        commands.append(' '.join(str(x) for row in a for x in row))
    fixture_source=BASE.parents[1]/'C2_Mxym_20261122/proof_review_v1/unsigned_packet_v2/singleton-simplex-packet/unsigned15/h1fixtures.tsv'
    fixture_dir=BASE/'fixtures_v1'
    fixture_dir.mkdir(exist_ok=True)
    fixture_meta=[]
    for index,line in enumerate(fixture_source.read_text().splitlines()):
        numbers=list(map(int,line.split()))
        cid,root=numbers[:2]
        C=own_local.Chart(cid,0)
        groups=[[i for i in range(12) if C.comp[i]==c] for c in range(C.ncomp)]
        basis=[i for group in groups for i in group[:-1]]
        dh=determinant([[C.HA[i][j] for j in basis] for i in basis])
        df=determinant([row[:11] for row in C.FA[:11]])
        name=f'fixtures_v1/{index}.txt'
        with (BASE/name).open('w') as out:
            def emit(row):
                out.write(' '.join(map(str,row))+'\n')
            emit([cid,len(basis),dh,df,1,4]);emit([root]);emit(C.P);emit(C.N);emit(C.A)
            for matrix in (C.Hinv,C.Finv,C.FA):
                for row in matrix:
                    emit(row)
            for yi,aa,bb in [numbers[i:i+3] for i in range(2,14,3)]:
                y=own_local.OUTER[yi]
                j,k,t=y
                mask=(1<<own_local.ax(j,0))|(1<<own_local.ax(k,t))
                twin=(1<<own_local.ax(j,1))|(1<<own_local.ax(k,1-t))
                a=[(aa>>i)&1 for i in range(12)]
                b=[(bb>>i)&1 for i in range(12)]
                for i in range(12):
                    if a[i]:
                        mask|=1<<own_local.pos(i);twin|=1<<own_local.neg(i)
                    if b[i]:
                        mask|=1<<own_local.neg(i);twin|=1<<own_local.pos(i)
                key=[a[i]+b[i] for i in range(12)]
                f=[-C.zdot(i,y)-4*(a[i]-b[i]) for i in range(12)]
                u=[1-abs(C.zdot(i,y))-2*key[i] for i in range(12)]
                emit([yi,mask,twin]+key+f+u)
        commands.append('F '+name+' '+' '.join(map(str,numbers[14:])))
        fixture_meta.append(dict(chart=cid,root=root))
    text='\n'.join(commands)+'\n'
    (BASE/'controls_v1.in').write_text(text)
    command=['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec','./singleton_probe_v1_checked']
    result=subprocess.run(command,input=text,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (BASE/'controls_v1.stdout').write_text(result.stdout)
    (BASE/'controls_v1.stderr').write_text(result.stderr)
    assert result.returncode==0 and 'runtime error:' not in result.stderr
    rows=result.stdout.splitlines()
    assert len(rows)==len(cases)+len(fixture_meta)
    positive=negative=0
    for index,((kind,a,data),row) in enumerate(zip(cases,rows)):
        okay,rank,det=oracle(a)
        if kind=='G':
            actual,arank,adet=row.split()
            assert bool(int(actual))==okay,(index,a,row)
            if okay:
                assert int(arank)==rank
                # Two nonsingular principal bases differ by a rational square.
                ratio=F(adet)/det
                assert isqrt(ratio.numerator)**2==ratio.numerator and isqrt(ratio.denominator)**2==ratio.denominator
            expected=okay
            if data is not None:
                assert expected==data
        else:
            n,sr,k=data
            base=[r[:n] for r in a[:n]]
            bp,br,bd=oracle(base)
            expected=okay and bp and sr+rank<=15
            if expected and sr+rank==15:
                expected=square(det)
            assert bool(int(row))==expected,(index,a,data,row,expected)
        positive+=bool(expected)
        negative+=not bool(expected)
    for meta,row in zip(fixture_meta,rows[len(cases):]):
        cap,tcap,hd,fd,hr,fr,r7=map(int,row.split())
        assert cap==tcap==hd==fd==1 and hr<=15 and fr<=15 and r7<=13,(meta,row)
    summary=dict(status='SINGLETON_CORE_CONTROLS_PASS',cases=len(cases),positive=positive,
                 negative=negative,local_positive_fixtures=len(fixture_meta),
                 elapsed_seconds=time.time()-started,
                 fixture_source_sha256=hashlib.sha256(fixture_source.read_bytes()).hexdigest(),
                 hashes={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
                         for name in ['singleton_exact_v1.cpp','singleton_exact_v1_checked','singleton_probe_v1.cpp',
                                      'singleton_probe_v1_checked','validate_singleton_v1.py','controls_v1.in','controls_v1.stdout']})
    (BASE/'controls_result_v1.json').write_text(json.dumps(summary,indent=4))
    print(json.dumps(summary),flush=True)
if __name__=='__main__':
    main()
