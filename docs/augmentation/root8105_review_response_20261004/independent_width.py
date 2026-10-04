import sys,itertools,json,time
from functools import lru_cache
sys.path.insert(0,'/tmp/root8105_review_received/root8105_claude_review_tools')
from width_dp import Geo,load_roots
G=Geo(7);roots=load_roots('/workspace/scratch/1636117723f4/conway99-research/experiments/memetik/root8105_pilot_1_0_1/roots.tsv',G)
for rid,t in [(1,G.labels.index((0,8))),(64,G.labels.index((0,8)))]:
 r=next(x['row'] for x in roots if x['id']==rid);Nu={v for v in range(G.n) if r>>v&1};e=int(t in Nu);k=2-e-len(G.sets[t]&G.sets[0]);deg=G.margins(t)
 forbidden={t}|({0} if not e else set())
 if e:forbidden|={v for v in Nu if len(G.sets[v]&G.sets[0])==1}
 forced={0} if e else set()
 allowed={G.labels[i]:int(i in Nu) for i in range(G.n) if i not in forbidden|forced}
 for i in forced:
  a,b=G.labels[i];deg[a]-=1;deg[b]-=1;k-=int(i in Nu)
 @lru_cache(None)
 def rec(ds,kk):
  if kk<0 or any(d<0 for d in ds):return 0
  if not any(ds):return int(kk==0)
  a=next(i for i,d in enumerate(ds) if d);need=ds[a];rest=[b for b in range(a+1,G.b) if ds[b] and (a,b) in allowed]
  total=0
  for nb in itertools.combinations(rest,need):
   dd=list(ds);dd[a]=0
   for b in nb:dd[b]-=1
   total+=rec(tuple(dd),kk-sum(allowed[(a,b)] for b in nb))
  return total
 t0=time.process_time();v=rec(tuple(deg),k)
 print(json.dumps({'root':rid,'target':G.labels[t],'width':v,'method':'Python arbitrary-integer vertex elimination, no numpy and no SAT','cache_states':rec.cache_info().currsize,'cpu_s':time.process_time()-t0}),flush=True)
