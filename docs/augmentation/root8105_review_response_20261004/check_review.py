import sys,json,time,math,statistics,random
from pathlib import Path
sys.path.insert(0,'/tmp/root8105_review_received/root8105_claude_review_tools')
from width_dp import Geo,load_roots,width_fast,width_exact
from crosscheck_sat import import_pilot,sat_rows,random_root
base=Path('/tmp/root8105_review_received/root8105_claude_review_tools')
pilot='/workspace/scratch/1636117723f4/conway99-research/experiments/memetik/root8105_pilot_1_0_1'
pc=import_pilot(pilot);g=Geo(7);roots=load_roots(pilot+'/roots.tsv',g)
original=[json.loads(x) for x in (base/'results/widths128.jsonl').read_text().splitlines()]
byid={r['id']:r for r in original};summary=json.loads((base/'results/widths128_summary.json').read_text())
assert len(original)==128 and all(len(r['w'])==83 for r in original)
for r in summary['per_root']:
    w=byid[r['id']]['w'];assert r['min']==min(w) and r['max']==max(w) and r['ord']==w[0]
from collections import Counter
pop=Counter()
for r in roots:
    Nu=[i for i in range(g.n) if r['row']>>i&1]
    iso=[i for i in Nu if len(g.sets[i]&g.sets[0])==1]
    assert len(iso)==2
    pop[sum(bool(g.sets[i]&{7,8}) for i in iso)]+=1
print(json.dumps({'population_types':dict(pop),'max_partial_dp_count_upper_bound':sum(math.comb(84,k) for k in range(13)),'fits_int64':sum(math.comb(84,k) for k in range(13))<2**63}),flush=True)
for rid in [1,64,751,3675]:
    root=next(r for r in roots if r['id']==rid);t0=time.process_time()
    w=[width_fast(g,root['row'],t) for t in range(1,g.n)]
    assert w==byid[rid]['w']
    print(json.dumps({'test':'all_83_widths','root':rid,'match':True,'min':min(w),'cpu_s':time.process_time()-t0}),flush=True)
G=pc.Geometry(7);r=roots[0]['row'];t1=G.index[(0,8)]
for x in [json.loads(x) for x in (base/'results/probe_level2_root1.jsonl').read_text().splitlines()]:
    S={0:r,t1:int(x['row'],16)};G.verify(S)
    w=width_exact(g,S,G.index[(1,7)]);assert w==x['min']
    print(json.dumps({'test':'probe_min_recount','sample':x['sample'],'width':w}),flush=True)
# New small-state checks; no time cutoff, every reported match is exhaustive.
rng=random.Random(810520261004)
for m in [4,5,6,7]:
    gg=Geo(m);GG=pc.Geometry(m)
    if m==7:S={0:r,t1:int(json.loads((base/'results/probe_level2_root1.jsonl').read_text().splitlines()[0])['row'],16)}
    else:S={0:random_root(gg,rng)}
    while len(S)<3:
        found=False
        for t in [v for v in range(gg.n) if v not in S and any(rs>>v&1 for rs in S.values())]:
            cnf,var=pc.encode(GG,S,t)
            from pysat.solvers import Glucose4
            with Glucose4(bootstrap_with=cnf.clauses) as sol:
                if not sol.solve():continue
                pos=set(x for x in sol.get_model() if x>0);fixed,free=pc.projection(GG,S,t,var)
                S[t]=fixed|sum(1<<v for v,l in free if l in pos);GG.verify(S);found=True;break
        assert found
    cand=[t for t in range(gg.n) if t not in S and any(rs>>t&1 for rs in S.values())]
    for t in cand[:2]:
        t0=time.process_time();w=width_exact(gg,S,t);children,done=sat_rows(pc,GG,S,t)
        assert done and len(children)==w
        for row in children:GG.verify({**S,t:row})
        print(json.dumps({'test':'new_depth3_exact_vs_sat','m':m,'target':t,'width':w,'match':True,'cpu_s':time.process_time()-t0,'rows':{str(s):hex(rs) for s,rs in S.items()}}),flush=True)
print(json.dumps({'status':'PASS'}),flush=True)
