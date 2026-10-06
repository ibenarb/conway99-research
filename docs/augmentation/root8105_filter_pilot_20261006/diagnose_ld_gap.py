"""Post-pilot deterministic diagnostic; not part of the preregistered sample."""
import sys
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('package', type=Path)
parser.add_argument('output', type=Path)
args=parser.parse_args()
sys.path.insert(0, str(args.package.resolve()))
import json,time,resource
from plan import jobs
from kernel import Geo
import historical_core as core
from filters import check
import sat_control
from pysat.solvers import Glucose4
from runtime import atomic

started=time.process_time()
g=Geo(); root=min((r for r in jobs() if r['id']),key=lambda r:r['id']); parent=int(root['row'],16)
candidates=[]
for t in range(1,g.n):
    if not parent>>t&1 or g.sets[t]&g.sets[0]: continue
    for w in range(1,g.n):
        if w!=t and parent>>w&1 and g.sets[w]&g.sets[t]: candidates.append((t,w))
plan={'status':'POST_PILOT_DIAGNOSTIC','root':root['id'],'parent':root['row'],
      'selection':'smallest selected root ID, then smallest target and witness with e=1, label overlap 0 and shared label among root neighbors',
      'candidates':candidates,'stopping':'first F-SAT LD-rejected witness, or all candidates on this one root exhausted',
      'not_part_of_fixed_4608':True}
out=args.output;out.mkdir(exist_ok=False)
atomic(out/'plan.json',plan)
attempts=[];found=None
for t,w in candidates:
    cnf,variables=core.encode(core.Geometry(),{0:parent},t)
    fixed,free=core.projection(core.Geometry(),{0:parent},t,variables)
    lit=dict(free)[w]
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        satisfiable=solver.solve(assumptions=[lit])
        attempts.append({'target':t,'required_common_neighbor':w,'SAT':satisfiable})
        if not satisfiable: continue
        positives=set(v for v in solver.get_model() if v>0)
        row=fixed|sum(1<<v for v,l in free if l in positives)
    rows={0:parent,t:row};g.verify(rows)
    variants={n:check(g,rows,ld,cap) for n,ld,cap in [('F',False,False),('F_LD',True,False),('F_CAP',False,True),('F_LD_CAP',True,True)]}
    assert variants['F']['pass'] and not variants['F_LD']['pass']
    independent=sat_control.check(rows,7,True,False)
    assert independent['status']=='UNSAT_UNCERTIFIED'
    found={'root':root['id'],'type':root['type'],'parent':root['row'],'target':t,'row':hex(row),
           'target_label':g.labels[t],'required_common_neighbor':w,'common_neighbor_label':g.labels[w],
           'variants':variants,'independent':independent,
           'independent_CAP':sat_control.check(rows,7,False,True,variants['F_CAP']['row'])}
    break
atomic(out/'result.json',{'status':'VALID_F_LD_COUNTEREXAMPLE_FOUND' if found else 'NO_WITNESS_ON_THIS_ROOT',
      'attempts':attempts,'witness':found,'cpu_s':time.process_time()-started,
      'process_lifetime_cpu_s':time.process_time(),'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
      'scope':'post-pilot diagnostic, not added to the fixed sample or its rejection fractions'})
print(json.dumps(json.loads((out/'result.json').read_text()),indent=2))
