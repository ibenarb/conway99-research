"""Standalone small-model oracle and replay tests; no production data needed.
Run in Linux with Python3 and g++: python3 public_smoke.py
Sources cached-engine.cpp and cached-verify.cpp must be beside this file.
This is a bounded regression check, not a C2 exclusion proof.
"""
from pathlib import Path
from itertools import combinations,product
import json,subprocess,tempfile,resource,os
P=Path(__file__).resolve().parent

def limits():
    os.nice(15)
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(20,20))

def run(args):
    return subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=25,preexec_fn=limits)

def image(x,p):
    return sum(1<<p[c] for c in range(4) if x>>c&1)

G=[[2,0,1,1],[0,2,1,1],[1,1,2,0],[1,1,0,2]]
values=sorted(sum(1<<c for c in pair) for pair in combinations(range(4),2))
counts=dict(accepted_models=0,sat=0,unsat=0,nonclosed_rejected=0)
with tempfile.TemporaryDirectory(prefix='c2-controls-') as temp:
    out=Path(temp)
    for name in ('engine','verify'):
        r=subprocess.run(['g++','-O3','-mpopcnt','-std=c++17',str(P/('cached-'+name+'.cpp')),'-o',str(out/name)],capture_output=True,text=True,timeout=60)
        assert r.returncode==0,r.stderr
    for bits in range(64):
        domain=[x for i,x in enumerate(values) if bits>>i&1]
        solutions=[]
        for a,b in product(domain,repeat=2):
            rows=[3,12,a,b]
            if all((rows[r]&rows[s]).bit_count()==G[r][s] for r in range(4) for s in range(4)) and all(sum(x>>c&1 for x in rows)==2 for c in range(4)):
                solutions.append(rows)
        text=['4 4','0 1 2 3']+[' '.join(map(str,row)) for row in G]*2
        for d in ([3],[12],domain,domain):text.extend([str(len(d)),' '.join(map(str,d))])
        text.extend(['1','3 12']);model=out/'model.txt';model.write_text('\n'.join(text)+'\n')
        for p in ([0,1,2,3],[1,0,2,3],[1,0,3,2]):
            action=out/'action.txt';action.write_text(' '.join(map(str,p))+'\n')
            proof=out/'proof';report=out/'result.json'
            r=run([out/'engine',model,0,proof,5,report,action])
            closed=sorted(image(x,p) for x in domain)==domain
            if not closed:
                assert r.returncode==1,r.stderr;counts['nonclosed_rejected']+=1;continue
            assert r.returncode==(10 if solutions else 20),r.stderr
            data=json.loads(report.read_text())
            if solutions:
                assert data['rows'] in solutions
                a,b=data['rows'][2:]
                assert (a,b)==min((a,b),(b,a),(image(a,p),image(b,p)),(image(b,p),image(a,p)))
                counts['sat']+=1
            else:counts['unsat']+=1
            v=run([out/'verify',model,0,proof,action]);assert (v.returncode==0)==(not solutions),v.stderr
            counts['accepted_models']+=1
print(json.dumps(dict(status='PASS',**counts),indent=4))
