"""Count cycle3 moves (3-cycle of apex rotations, excluded from the radius catalogue) at both roots,
and check whether any of them improves (W,L1) at depth 1."""
import sys, json
sys.path.insert(0,'/home/claude/src/experiments/memetik/lambda_radius_1_0_0')
import boot
from support import read, core, Guard, key
from kernel import catalogue, Scorer
starts=read(boot.HERE/'STARTS.json'); g=Guard(); out={}
for label in ('2076','2077'):
    rows=tuple(core.decode_g6(starts[label]['graph6'])); sc=Scorer(rows); base=key(sc.scores)
    cnt={}; best=None; impr=0; ap=set()
    for name,mv in catalogue(rows,True,g):
        cnt[name]=cnt.get(name,0)+1
        if name!='cycle3': continue
        child,s=sc.evaluate(mv); k=key(s)
        if k<base: impr+=1
        if best is None or k<best: best=k
    out[label]=dict(catalogue_with_cycle3=cnt, cycle3_depth1_improving=impr, best_cycle3_child=best, base=base)
    print(label,out[label])
json.dump(out,open('cycle3_census.json','w'),indent=1)
