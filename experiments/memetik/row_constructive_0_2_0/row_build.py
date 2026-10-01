#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, random, time
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

OUTER=tuple((a,b) for a,b in combinations(range(14),2) if b-a!=7); PS=tuple(map(frozenset,OUTER)); N=84

def margins(u):
    a,b=OUTER[u]; return [1 if x in (a,b) or (x+7)%14 in (a,b) else 2 for x in range(14)]
def left(prefix,u): return sum(1<<v for v,r in enumerate(prefix) if (r>>u)&1)
def want(u,v,e): return 2-e-len(PS[u]&PS[v])
def digest(prefix):
    h=hashlib.sha256(); [h.update(r.to_bytes(11,'little')) for r in prefix]; return h.hexdigest()
def atomic(path,data):
    path=Path(path); t=path.with_suffix(path.suffix+'.tmp'); t.write_text(json.dumps(data,indent=2)); os.replace(t,path)

def check(prefix):
    for u,r in enumerate(prefix):
        if r.bit_count()!=12 or (r>>u)&1: raise ValueError('degree/diagonal')
        for v in range(u):
            if ((r>>v)&1)!=((prefix[v]>>u)&1): raise ValueError('symmetry')
            if (r&prefix[v]).bit_count()!=want(u,v,(r>>v)&1): raise ValueError('resolved pair')
        c=[0]*14
        for w in range(N):
            if (r>>w)&1:
                for a in OUTER[w]: c[a]+=1
        if c!=margins(u): raise ValueError('border margins')

def future_ok(prefix):
    d=len(prefix)
    for j in range(d,N):
        L=left(prefix,j)
        if L.bit_count()>12: return False
        c=[0]*14
        for v in range(d):
            if (L>>v)&1:
                for a in OUTER[v]: c[a]+=1
        if any(x>y for x,y in zip(c,margins(j))): return False
        for v in range(d):
            t=want(j,v,(prefix[v]>>j)&1); known=(L&prefix[v]&((1<<d)-1)).bit_count(); avail=(prefix[v]&~((1<<d)-1)&~(1<<j)).bit_count()
            if known>t or known+avail<t: return False
    return True

def subset(features,req,k,rng,limit,reverse=False):
    m=len(features); masks=[0]*len(req)
    for i,fs in enumerate(features):
        for c in fs: masks[c]|=1<<i
    nodes=0; cache=set()
    def rec(av,rr,need):
        nonlocal nodes; nodes+=1
        if nodes>limit: raise TimeoutError
        bad=0
        for c,x in enumerate(rr):
            if x==0: bad|=masks[c]
        av&=~bad
        if need<0 or av.bit_count()<need: return None
        for c,x in enumerate(rr):
            if x<0 or (av&masks[c]).bit_count()<x: return None
        if need==0: return 0 if all(x==0 for x in rr) else None
        key=(av,rr,need)
        if key in cache: return None
        cache.add(key)
        bc=min((c for c,x in enumerate(rr) if x>0),key=lambda c:((av&masks[c]).bit_count()-rr[c],(av&masks[c]).bit_count()))
        opts=[i for i in range(m) if (av>>i)&1 and bc in features[i]]
        if rng: rng.shuffle(opts)
        elif reverse: opts.reverse()
        for i in opts:
            nr=list(rr); ok=True
            for c in features[i]: nr[c]-=1; ok&=nr[c]>=0
            if ok:
                a=rec(av&~(1<<i),tuple(nr),need-1)
                if a is not None: return a|(1<<i)
        return None
    try: return rec((1<<m)-1,tuple(req),k),nodes,False
    except TimeoutError: return None,nodes,True

def row_solution(prefix,seed,limit,mode):
    u=len(prefix); L=left(prefix,u); k=12-L.bit_count(); req=margins(u)
    if k<0 or k>N-u-1: return None,'EXACT_INFEASIBLE'
    for w in range(u):
        if (L>>w)&1:
            for a in OUTER[w]: req[a]-=1
    if min(req)<0: return None,'EXACT_INFEASIBLE'
    for v in range(u): req.append(want(u,v,(L>>v)&1)-(L&prefix[v]).bit_count())
    if min(req)<0: return None,'EXACT_INFEASIBLE'
    cand=list(range(u+1,N)); feat=[]
    for w in cand:
        f=set(OUTER[w]); f.update(14+v for v in range(u) if (prefix[v]>>w)&1); feat.append(f)
    rng=None if mode!='random' else random.Random(seed)
    a,n,to=subset(feat,req,k,rng,limit,mode=='descending')
    if a is None: return None,'ROW_SEARCH_LIMIT' if to else 'EXACT_INFEASIBLE'
    r=L
    for i,w in enumerate(cand):
        if (a>>i)&1: r|=1<<w
    q=prefix+(r,); check(q)
    return (r,'FEASIBLE') if future_ok(q) else (None,'FORWARD_REJECT')

def alts(prefix,seed,cfg,mode):
    out=[]; seen=set(); states=[]
    for i in range(cfg['attempts_per_node']):
        r,s=row_solution(prefix,seed+104729*i,cfg['node_limit'],mode); states.append(s)
        if r is not None and r not in seen: seen.add(r); out.append(r)
        if len(out)>=cfg['alternatives_per_node'] or s=='EXACT_INFEASIBLE': break
    return out,states

def worker(cfg,wid,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True); cp=out/f'checkpoint_{wid:02d}.json'
    mode='ascending' if wid==0 else 'descending' if wid==1 else 'random'; seed=cfg['seed']+1000003*wid
    prefix=(); frames=[]; best=(); bt=0; exact=limited=0
    if cp.exists():
        d=json.loads(cp.read_text()); prefix=tuple(int(x,16) for x in d['prefix']); best=tuple(int(x,16) for x in d['best']); frames=d['frames']; bt=d['backtracks']; check(prefix)
    t0=time.time(); last=0; status='TIME_BUDGET'
    while time.time()-t0<cfg['wall_seconds']:
        d=len(prefix)
        if d==N: best=prefix; status='COMPLETE_SRG'; break
        if len(frames)<=d:
            aa,ss=alts(prefix,seed^int(digest(prefix)[:16],16),cfg,mode)
            if not aa: exact+=('EXACT_INFEASIBLE' in ss); limited+=('ROW_SEARCH_LIMIT' in ss)
            frames.append({'alts':[hex(x) for x in aa],'next':0})
        f=frames[d]
        if f['next']<len(f['alts']):
            r=int(f['alts'][f['next']],16); f['next']+=1; prefix=prefix+(r,)
            if len(prefix)>len(best): best=prefix
        else:
            frames.pop()
            if not prefix: status='TREE_SAMPLE_EXHAUSTED'; break
            prefix=prefix[:-1]; bt+=1
        now=time.time()
        if now-last>=cfg['checkpoint_seconds']:
            atomic(cp,{'prefix':[hex(x) for x in prefix],'best':[hex(x) for x in best],'frames':frames,'backtracks':bt}); last=now
    res={'worker':wid,'mode':mode,'status':status,'max_depth':len(best),'backtracks':bt,'exact_dead':exact,'limited_dead':limited,'best_sha256':digest(best)}
    atomic(out/f'result_{wid:02d}.json',res); return res

def run(cfgfile,out):
    cfg=json.loads(Path(cfgfile).read_text()); out=Path(out); out.mkdir(parents=True,exist_ok=True); last=0
    with ProcessPoolExecutor(max_workers=cfg['workers']) as ex:
        fs=[ex.submit(worker,cfg,i,str(out)) for i in range(cfg['workers'])]
        while not all(f.done() for f in fs):
            if time.time()-last>=600:
                ds=[]
                for p in out.glob('checkpoint_*.json'):
                    try: ds.append(len(json.loads(p.read_text())['best']))
                    except: pass
                done=sum(f.done() for f in fs); print(f"ROWBUILD best={max(ds,default=0)}/84 live={cfg['workers']-done} done={done}"[:79],flush=True); last=time.time()
            time.sleep(2)
        rr=[f.result() for f in fs]
    atomic(out/'SUMMARY.json',{'best_depth':max(x['max_depth'] for x in rr),'results':rr})

def selftest():
    p=()
    for u in range(6):
        aa,ss=alts(p,1000+u*1000,{'attempts_per_node':64,'alternatives_per_node':1,'node_limit':250000},'random')
        if not aa: raise SystemExit((u,ss[-1] if ss else None))
        p=p+(aa[0],); check(p)
    print(json.dumps({'status':'PASS','depth':len(p),'sha256':digest(p)}))

def main():
    a=argparse.ArgumentParser(); s=a.add_subparsers(dest='cmd',required=True); s.add_parser('selftest'); r=s.add_parser('run'); r.add_argument('config'); r.add_argument('outdir'); z=a.parse_args(); selftest() if z.cmd=='selftest' else run(z.config,z.outdir)
if __name__=='__main__': main()
