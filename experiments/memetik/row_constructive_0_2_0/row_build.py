#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, random, time
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

OUTER=tuple((a,b) for a,b in combinations(range(14),2) if b-a!=7)
PS=tuple(map(frozenset,OUTER)); N=84

def margins(u):
    a,b=OUTER[u]
    return [1 if x in (a,b) or (x+7)%14 in (a,b) else 2 for x in range(14)]

def left(prefix,u):
    return sum(1<<v for v,r in enumerate(prefix) if (r>>u)&1)

def want(u,v,e):
    return 2-e-len(PS[u]&PS[v])

def digest(prefix):
    h=hashlib.sha256()
    for r in prefix:
        h.update(r.to_bytes(11,'little'))
    return h.hexdigest()

def atomic(path,data):
    path=Path(path); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2))
    os.replace(tmp,path)

def check(prefix):
    for u,r in enumerate(prefix):
        if r.bit_count()!=12 or (r>>u)&1:
            raise ValueError('degree/diagonal')
        for v in range(u):
            if ((r>>v)&1)!=((prefix[v]>>u)&1):
                raise ValueError('symmetry')
            if (r&prefix[v]).bit_count()!=want(u,v,(r>>v)&1):
                raise ValueError('resolved pair')
        c=[0]*14
        for w in range(N):
            if (r>>w)&1:
                for a in OUTER[w]:
                    c[a]+=1
        if c!=margins(u):
            raise ValueError('border margins')

def future_ok(prefix):
    d=len(prefix)
    for j in range(d,N):
        L=left(prefix,j)
        if L.bit_count()>12:
            return False
        c=[0]*14
        for v in range(d):
            if (L>>v)&1:
                for a in OUTER[v]:
                    c[a]+=1
        if any(x>y for x,y in zip(c,margins(j))):
            return False
        for v in range(d):
            target=want(j,v,(prefix[v]>>j)&1)
            known=(L&prefix[v]&((1<<d)-1)).bit_count()
            avail=(prefix[v]&~((1<<d)-1)&~(1<<j)).bit_count()
            if known>target or known+avail<target:
                return False
    return True

def build_problem(prefix):
    u=len(prefix); L=left(prefix,u); k=12-L.bit_count(); req=margins(u)
    if k<0 or k>N-u-1:
        return None
    for w in range(u):
        if (L>>w)&1:
            for a in OUTER[w]:
                req[a]-=1
    if min(req)<0:
        return None
    for v in range(u):
        req.append(want(u,v,(L>>v)&1)-(L&prefix[v]).bit_count())
    if min(req)<0:
        return None
    cand=list(range(u+1,N)); feat=[]
    for w in cand:
        f=set(OUTER[w])
        f.update(14+v for v in range(u) if (prefix[v]>>w)&1)
        feat.append(f)
    return u,L,k,req,cand,feat

def enumerate_subsets(features,req,k,seed,mode,node_limit,raw_limit):
    m=len(features); masks=[0]*len(req)
    for i,fs in enumerate(features):
        for c in fs:
            masks[c]|=1<<i
    rng=random.Random(seed) if mode=='random' else None
    nodes=0; raw=[]; stop=None
    def rec(av,rr,need,chosen):
        nonlocal nodes,stop
        if stop:
            return
        nodes+=1
        if nodes>node_limit:
            stop='ROW_NODE_LIMIT'; return
        bad=0
        for c,x in enumerate(rr):
            if x==0:
                bad|=masks[c]
        av&=~bad
        if need<0 or av.bit_count()<need:
            return
        for c,x in enumerate(rr):
            if x<0 or (av&masks[c]).bit_count()<x:
                return
        if need==0:
            if all(x==0 for x in rr):
                raw.append(chosen)
                if len(raw)>=raw_limit:
                    stop='RAW_SOLUTION_LIMIT'
            return
        pos=[c for c,x in enumerate(rr) if x>0]
        if not pos:
            return
        bc=min(pos,key=lambda c:((av&masks[c]).bit_count()-rr[c],(av&masks[c]).bit_count()))
        opts=[i for i in range(m) if (av>>i)&1 and bc in features[i]]
        if rng:
            rng.shuffle(opts)
        elif mode=='descending':
            opts.reverse()
        excluded=0
        for i in opts:
            bit=1<<i
            nr=list(rr); ok=True
            for c in features[i]:
                nr[c]-=1
                if nr[c]<0:
                    ok=False; break
            if ok:
                rec(av&~excluded&~bit,tuple(nr),need-1,chosen|bit)
            excluded|=bit
            if stop:
                return
    rec((1<<m)-1,tuple(req),k,0)
    return raw,nodes,stop

def row_alternatives(prefix,seed,cfg,mode):
    prob=build_problem(prefix)
    if prob is None:
        return [],{'status':'EXACT_INFEASIBLE','nodes':0,'raw':0,'forward_rejects':0}
    u,L,k,req,cand,feat=prob
    raws,nodes,stop=enumerate_subsets(feat,req,k,seed,mode,cfg['node_limit'],cfg['raw_solution_limit'])
    accepted=[]; rejects=0; seen=set()
    for a in raws:
        r=L
        for i,w in enumerate(cand):
            if (a>>i)&1:
                r|=1<<w
        if r in seen:
            continue
        seen.add(r)
        q=prefix+(r,); check(q)
        if future_ok(q):
            accepted.append(r)
            if len(accepted)>=cfg['alternatives_per_node']:
                break
        else:
            rejects+=1
    if accepted:
        status='FEASIBLE_SET'
    elif stop:
        status=stop
    elif raws:
        status='FORWARD_EXHAUSTED'
    else:
        status='EXACT_INFEASIBLE'
    return accepted,{'status':status,'nodes':nodes,'raw':len(raws),'forward_rejects':rejects,'stop':stop}

def worker(cfg,wid,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    cp=out/f'checkpoint_{wid:02d}.json'
    mode='ascending' if wid==0 else 'descending' if wid==1 else 'random'
    seed=cfg['seed']+1000003*wid
    prefix=(); frames=[]; best=(); bt=0; counts={}
    if cp.exists():
        d=json.loads(cp.read_text())
        prefix=tuple(int(x,16) for x in d['prefix'])
        best=tuple(int(x,16) for x in d['best'])
        frames=d['frames']; bt=d['backtracks']; counts=d.get('counts',{})
        check(prefix)
    t0=time.time(); last=0; status='TIME_BUDGET'
    while time.time()-t0<cfg['wall_seconds']:
        d=len(prefix)
        if d==N:
            best=prefix; status='COMPLETE_SRG'; break
        if len(frames)<=d:
            aa,meta=row_alternatives(prefix,seed^int(digest(prefix)[:16],16),cfg,mode)
            counts[meta['status']]=counts.get(meta['status'],0)+1
            frames.append({'alts':[hex(x) for x in aa],'next':0,'meta':meta})
        f=frames[d]
        if f['next']<len(f['alts']):
            r=int(f['alts'][f['next']],16); f['next']+=1
            prefix=prefix+(r,)
            if len(prefix)>len(best):
                best=prefix
        else:
            frames.pop()
            if not prefix:
                status='ENUMERATED_SAMPLE_EXHAUSTED'; break
            prefix=prefix[:-1]; bt+=1
        if time.time()-last>=cfg['checkpoint_seconds']:
            atomic(cp,{'prefix':[hex(x) for x in prefix],'best':[hex(x) for x in best],
                       'frames':frames,'backtracks':bt,'counts':counts})
            last=time.time()
    res={'worker':wid,'mode':mode,'status':status,'max_depth':len(best),
         'backtracks':bt,'counts':counts,'best_sha256':digest(best)}
    atomic(out/f'result_{wid:02d}.json',res)
    return res

def run(cfgfile,out):
    cfg=json.loads(Path(cfgfile).read_text()); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    last=0
    with ProcessPoolExecutor(max_workers=cfg['workers']) as ex:
        fs=[ex.submit(worker,cfg,i,str(out)) for i in range(cfg['workers'])]
        while not all(f.done() for f in fs):
            if time.time()-last>=600:
                ds=[]
                for p in out.glob('checkpoint_*.json'):
                    try:
                        ds.append(len(json.loads(p.read_text())['best']))
                    except Exception:
                        pass
                done=sum(f.done() for f in fs)
                print(f"ROWBUILD best={max(ds,default=0)}/84 live={cfg['workers']-done} done={done}"[:79],flush=True)
                last=time.time()
            time.sleep(2)
        rr=[f.result() for f in fs]
    atomic(out/'SUMMARY.json',{'best_depth':max(x['max_depth'] for x in rr),'results':rr})

def selftest():
    cfg={'node_limit':250000,'raw_solution_limit':512,'alternatives_per_node':12}
    root,meta=row_alternatives((),1234,cfg,'random')
    if len(root)<2 or len(set(root))!=len(root):
        raise SystemExit('enumeration regression failed')
    good=bad=0
    for i,r in enumerate(root):
        child,_=row_alternatives((r,),9000+i,cfg,'random')
        good+=bool(child); bad+=not bool(child)
    if not good or not bad:
        raise SystemExit('backtracking regression failed')
    visited=0
    def dfs(prefix,target,salt):
        nonlocal visited
        visited+=1
        if len(prefix)>=target:
            return prefix
        aa,_=row_alternatives(prefix,salt^int(digest(prefix)[:16],16),cfg,'random')
        for i,r in enumerate(aa):
            got=dfs(prefix+(r,),target,salt+104729*(i+1))
            if got is not None:
                return got
        return None
    p=dfs((),6,777)
    if p is None:
        raise SystemExit('constructive backtracking regression failed')
    check(p)
    print(json.dumps({'status':'PASS','depth':len(p),'root_alternatives':len(root),
                      'child_good':good,'child_bad':bad,'dfs_nodes':visited,
                      'sha256':digest(p)}))

def main():
    a=argparse.ArgumentParser(); s=a.add_subparsers(dest='cmd',required=True)
    s.add_parser('selftest')
    r=s.add_parser('run'); r.add_argument('config'); r.add_argument('outdir')
    z=a.parse_args()
    selftest() if z.cmd=='selftest' else run(z.config,z.outdir)

if __name__=='__main__':
    main()
