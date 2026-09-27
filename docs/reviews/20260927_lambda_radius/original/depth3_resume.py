"""Exact depth-3 recount for one arm with the frozen operator code, checkpointed.
Reproduces children count, absence of (W,L1) improvement and the number of distinct
labelled states first reached at exact depth 3. Distinct states are tracked by a
blake2b-128 digest of the packed 99-row state (collision probability negligible,
stated as an assumption). A deterministic sample of children is re-scored with an
independent pure-Python scorer. Checkpoint every 250 parents (pickle, atomic)."""
import sys, json, resource, random, itertools, pickle, os, hashlib
from collections import Counter
sys.path.insert(0, '/home/claude/src/experiments/memetik/lambda_radius_1_0_0')
import boot
from support import *
from enumeration import lower_layers
from kernel import catalogue, Scorer
label = sys.argv[1]
ck = f'ck_{label}.pkl'
starts = read(boot.HERE / 'STARTS.json'); g = Guard()
def cpu(): u=resource.getrusage(resource.RUSAGE_SELF); return u.ru_utime+u.ru_stime
def h(rows): return hashlib.blake2b(pack(rows), digest_size=16).digest()
def indep(rows):
    A=[set(core.vertices(r)) for r in rows]; W=L1=0
    for u,v in itertools.combinations(range(len(rows)),2):
        r=len(A[u]&A[v])+(1 if v in A[u] else 0)-2
        if r: W+=1; L1+=abs(r)
    return W,L1
t0=cpu()
states,n1,ev = lower_layers(starts[label], g)
base = key(Scorer(tuple(core.decode_g6(starts[label]['graph6']))).scores)
lower = {h(r) for r in states}
lowerWL = [(len(p), key(Scorer(r).scores)) for r,p in states.items()]
parents=sorted((r for r,p in states.items() if len(p)==2), key=pack)  # deterministic order
rng=random.Random(20260926); sample=set(rng.sample(range(1,450000),400))
if os.path.exists(ck):
    S=pickle.load(open(ck,'rb'))
    assert S['n_parents']==len(parents) and S['base']==base
    S['cpu_prev']=S.get('cpu_prev_total',0.0)
else:
    S=dict(next=0,children=0,improving=0,best=None,new3={},mism=0,sampled=0,cpu_prev=0.0,n_parents=len(parents),base=base)
def save():
    S['cpu_prev_total']=S['cpu_prev']+cpu()-t0
    tmp=ck+'.tmp'; pickle.dump(S,open(tmp,'wb')); os.replace(tmp,ck)
for n in range(S['next'], len(parents)):
    r=parents[n]; sc=Scorer(r)
    for _,mv in catalogue(r,False,g):
        child,s=sc.evaluate(mv); k=key(s); S['children']+=1
        if k<base: S['improving']+=1
        if S['best'] is None or k<S['best']: S['best']=k
        c=tuple(child); d=h(c)
        if d not in lower and d not in S['new3']: S['new3'][d]=k
        if S['children'] in sample:
            S['sampled']+=1
            if indep(c)!=k: S['mism']+=1
    S['next']=n+1
    if S['next']%250==0:
        save(); print(label,'parents',S['next'],'children',S['children'],'new3',len(S['new3']),flush=True)
save()
def hist(vals): return {str(k):v for k,v in sorted(Counter(vals).items())}
new3=S['new3']
res=dict(arm=label,base_WL1=list(base),parents=len(parents),children=S['children'],improving=S['improving'],
  best_child_WL1=list(S['best']),distinct_new_depth3=len(new3),
  expected=dict(children={'2076':526476,'2077':459185}[label],distinct_depth3={'2076':195508,'2077':169048}[label]),
  sampled_children_indep_checked=S['sampled'],score_mismatches=S['mism'],
  W_hist_by_depth={str(d):hist(k[0] for dd,k in lowerWL if dd==d) for d in (1,2)},
  W_hist_depth3=hist(k[0] for k in new3.values()),
  best5_WL1_by_depth={str(d):[[list(k),v] for k,v in sorted(Counter(k for dd,k in lowerWL if dd==d).items())[:5]] for d in (1,2)},
  best5_WL1_depth3=[[list(k),v] for k,v in sorted(Counter(new3.values()).items())[:5]],
  cpu_s_last_session=round(cpu()-t0,1), cpu_s_total_approx=round(S['cpu_prev_total'],1),
  note='distinct states counted via blake2b-128 digests; sample check uses an independent scorer')
res['match']= res['children']==res['expected']['children'] and res['distinct_new_depth3']==res['expected']['distinct_depth3'] and res['improving']==0
print(json.dumps(res),flush=True); json.dump(res,open(f'depth3_{label}.json','w'),indent=1)
