"""Re-run frozen lower_layers (depth 0..2) for both arms + positive control, with timing."""
import sys, time, json, resource
sys.path.insert(0, '/home/claude/src/experiments/memetik/lambda_radius_1_0_0')
import boot
from support import *
from enumeration import lower_layers
from kernel import catalogue, Scorer
starts = read(boot.HERE / 'STARTS.json')
g = Guard()
res = {}
def cpu(): u=resource.getrusage(resource.RUSAGE_SELF); return u.ru_utime+u.ru_stime
for label in ('2076','2077'):
    t=cpu()
    states, n1, ev = lower_layers(starts[label], g)
    n2 = sum(len(p)==2 for p in states.values())
    root = tuple(core.decode_g6(starts[label]['graph6']))
    n0 = sum(len(p)==0 for p in states.values())
    # move type census at root
    kinds = {}
    for name, mv in catalogue(root, False, g):
        kinds[name]=kinds.get(name,0)+1
    # best (W,L1) in layers 1 and 2
    base = Scorer(root).scores
    best = min(key(Scorer(r).scores) for r in states)
    res[label] = dict(n0=n0, n1=n1, n2=n2, evaluations=ev, root_moves=kinds, base=(base['W'],base['L1']), best_in_L0_2=best, cpu_s=round(cpu()-t,2))
    print(label, res[label], flush=True)
# positive control: W2079 -> W2076 in four moves via meet in the middle of depth-2 layers
t=cpu()
a,_,_ = lower_layers(starts['2079'], g)
b,_,_ = lower_layers(starts['2076'], g)
overlap = a.keys() & b.keys()
dists = sorted(len(a[r])+len(b[r]) for r in overlap)
res['control'] = dict(overlap=len(overlap), min_total_len=dists[0] if dists else None, n_min=dists.count(dists[0]) if dists else 0, cpu_s=round(cpu()-t,2))
print('control', res['control'])
json.dump(res, open('layers12.json','w'), indent=1)
