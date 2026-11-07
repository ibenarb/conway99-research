"""Standalone exhaustive small-model batch check; Python3 and g++ on Linux.
Keep batch-engine.cpp and batch-verify.cpp next to this file. No production data
is needed. This regression check is not a global C2 exclusion certificate.
"""
from pathlib import Path
from itertools import combinations, product
import json
import os
import resource
import subprocess
import tempfile
P=Path(__file__).resolve().parent
G=[[2,0,1,1],[0,2,1,1],[1,1,2,0],[1,1,0,2]]
values=sorted(sum(1<<c for c in pair) for pair in combinations(range(4),2))
action=[1,0,2,3]
def image(x):
    return sum(1<<action[c] for c in range(4) if x>>c&1)
def limits():
    os.nice(15)
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(20,20))
def run(args):
    return subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=25,preexec_fn=limits)
def valid(rows,domains,boundary):
    return tuple(rows[:2])==boundary and all(x in domains[i] for i,x in enumerate(rows)) and all((rows[r]&rows[s]).bit_count()==G[r][s] for r in range(4) for s in range(4)) and all(sum(x>>c&1 for x in rows)==2 for c in range(4))
counts=dict(batches=0,sat_stops=0,unsat_batches=0,nonclosed_rejected=0)
with tempfile.TemporaryDirectory(prefix='c2-public-batch-') as temp:
    out=Path(temp)
    for name in ('batch-engine','batch-verify'):
        r=subprocess.run(['g++','-O3','-mpopcnt','-std=c++17',str(P/(name+'.cpp')),'-o',str(out/name)],capture_output=True,text=True,timeout=60)
        assert r.returncode==0,r.stderr
    ap=out/'action.txt';ap.write_text(' '.join(map(str,action)))
    bounds=[(3,12),(12,3),(3,12)]
    for bits in range(64):
        domain=[x for i,x in enumerate(values) if bits>>i&1]
        domains=[[3,12],[3,12],domain,domain]
        lines=['4 4','0 1 2 3']+[' '.join(map(str,row)) for row in G]*2
        for d in domains:lines.extend([str(len(d)),' '.join(map(str,d))])
        lines.extend(['3']+[f'{a} {b}' for a,b in bounds])
        model=out/f'model{bits}.txt';model.write_text('\n'.join(lines)+'\n')
        solutions=[(a,b) for a,b in product(domain,repeat=2) if valid([3,12,a,b],domains,bounds[0])]
        for order in ((0,1,2),(2,1,0)):
            folder=out/f'm{bits}_o{order[0]}';folder.mkdir()
            tasks=','.join(map(str,order))
            r=run([out/'batch-engine',model,tasks,folder,5,ap])
            if sorted(image(x) for x in domain)!=domain:
                assert r.returncode==1,r.stderr
                counts['nonclosed_rejected']+=1
                continue
            assert r.returncode==(10 if solutions else 20),r.stderr
            v=run([out/'batch-verify',model,tasks,folder,ap])
            assert (v.returncode==0)==(not solutions),v.stderr
            if solutions:
                report=json.loads((folder/f'boundary_{order[0]}.json').read_text())
                assert valid(report['rows'],domains,bounds[order[0]])
                assert not (folder/f'boundary_{order[1]}.proof').exists()
                counts['sat_stops']+=1
            else:
                assert v.stdout.count('s VERIFIED BOUNDARY UNSAT')==3
                counts['unsat_batches']+=1
            counts['batches']+=1
print(json.dumps(dict(status='PASS',ABA_and_reverse_order=True,**counts),indent=4))
