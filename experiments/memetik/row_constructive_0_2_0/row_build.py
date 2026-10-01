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

def forward_value_ok(prefix,u,L_u,k,j,e):
    Lj=left(prefix,j)
    if Lj.bit_count()+e>12:
        return False
    c=[0]*14
    for v in range(u):
        if (Lj>>v)&1:
            for a in OUTER[v]:
                c[a]+=1
    if e:
        for a in OUTER[u]:
            c[a]+=1
    if any(x>y for x,y in zip(c,margins(j))):
        return False
    for v in range(u):
        target=want(j,v,(prefix[v]>>j)&1)
        known=(Lj&prefix[v]&((1<<u)-1)).bit_count()
        if e and ((prefix[v]>>u)&1):
            known+=1
        avail=(prefix[v]&~((1<<(u+1))-1)&~(1<<j)).bit_count()
        if known>target or known+avail<target:
            return False
    target=want(j,u,e)
    known=(Lj&L_u).bit_count()
    avail=k-e
    return known<=target<=known+avail

def build_problem(prefix):
    u=len(prefix); L=left(prefix,u); k=12-L.bit_count(); req=margins(u)
    if k<0 or k>N-u-1:
        return None,'EXACT_INFEASIBLE'
    for w in range(u):
        if (L>>w)&1:
            for a in OUTER[w]:
                req[a]-=1
    if min(req)<0:
        return None,'EXACT_INFEASIBLE'
    for v in range(u):
        req.append(want(u,v,(L>>v)&1)-(L&prefix[v]).bit_count())
    if min(req)<0:
        return None,'EXACT_INFEASIBLE'
    forced=[]; forbidden=[]; free=[]
    for j in range(u+1,N):
        ok0=forward_value_ok(prefix,u,L,k,j,0)
        ok1=forward_value_ok(prefix,u,L,k,j,1)
        if not ok0 and not ok1:
            return None,'FORWARD_INFEASIBLE'
        if ok1 and not ok0:
            forced.append(j)
        elif ok0 and not ok1:
            forbidden.append(j)
        else:
            free.append(j)
    for w in forced:
        for a in OUTER[w]:
            req[a]-=1
        for v in range(u):
            if (prefix[v]>>w)&1:
                req[14+v]-=1
    kfree=k-len(forced)
    if kfree<0 or kfree>len(free) or min(req)<0:
        return None,'FORWARD_INFEASIBLE'
    feat=[]
    for w in free:
        f=set(OUTER[w])
        f.update(14+v for v in range(u) if (prefix[v]>>w)&1)
        feat.append(f)
    return (u,L,kfree,req,free,feat,forced,forbidden),'READY'

def enumerate_subsets(features,req,k,seed,mode,node_limit,solution_limit):
    m=len(features); masks=[0]*len(req)
    for i,fs in enumerate(features):
        for c in fs:
            masks[c]|=1<<i
    rng=random.Random(seed) if mode=='random' else None
    nodes=0; sols=[]; stop=None
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
                sols.append(chosen)
                if len(sols)>=solution_limit:
                    stop='SOLUTION_SCAN_LIMIT'
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
            bit=1<<i; nr=list(rr); ok=True
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
    return sols,nodes,stop

def scan_once(prefix,seed,cfg,mode,node_limit,solution_limit):
    prob,state=build_problem(prefix)
    if prob is None:
        return [],{'status':state,'nodes':0,'solutions':0,'post_rejects':0,'stop':None}
    u,L,k,req,free,feat,forced,forbidden=prob
    sols,nodes,stop=enumerate_subsets(feat,req,k,seed,mode,node_limit,solution_limit)
    accepted=[]; rejects=0; seen=set(); forced_bits=sum(1<<w for w in forced)
    for a in sols:
        r=L|forced_bits
        for i,w in enumerate(free):
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
        status='FEASIBLE_SET' if stop else 'FEASIBLE_EXHAUSTIVE'
    elif stop:
        status='LIMITED'
    elif sols:
        status='POST_FORWARD_EXHAUSTED'
    else:
        status='EXACT_INFEASIBLE'
    return accepted,{'status':status,'nodes':nodes,'solutions':len(sols),
                     'post_rejects':rejects,'stop':stop,
                     'forced':len(forced),'forbidden':len(forbidden),'free':len(free)}

def row_alternatives(prefix,seed,cfg,mode):
    node=cfg['node_limit_initial']; scan=cfg['solution_scan_initial']
    last=None; allrows=[]; seen=set()
    for round_no in range(cfg['adaptive_rounds']):
        rr,meta=scan_once(prefix,seed+round_no*32452843,cfg,mode,node,scan)
        for r in rr:
            if r not in seen:
                seen.add(r); allrows.append(r)
                if len(allrows)>=cfg['alternatives_per_node']:
                    meta['adaptive_round']=round_no
                    return allrows,meta
        last=meta
        if meta['status'] in ('EXACT_INFEASIBLE','FORWARD_INFEASIBLE','POST_FORWARD_EXHAUSTED','FEASIBLE_EXHAUSTIVE'):
            meta['adaptive_round']=round_no
            return allrows,meta
        node=min(cfg['node_limit_max'],node*cfg['adaptive_factor'])
        scan=min(cfg['solution_scan_max'],scan*cfg['adaptive_factor'])
    last=dict(last or {})
    last['status']='LIMIT_UNRESOLVED'
    last['adaptive_round']=cfg['adaptive_rounds']-1
    return allrows,last

def worker(cfg,wid,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    cp=out/f'checkpoint_{wid:02d}.json'
    base_mode='ascending' if wid==0 else 'descending' if wid==1 else 'random'
    seed=cfg['seed']+1000003*wid
    prefix=(); frames=[]; best=(); bt=0; counts={}; epoch=0; unresolved=0
    if cp.exists():
        saved=json.loads(cp.read_text())
        prefix=tuple(int(x,16) for x in saved.get('prefix',[]))
        best=tuple(int(x,16) for x in saved.get('best',[]))
        frames=saved.get('frames',[])
        bt=int(saved.get('backtracks',0))
        counts=saved.get('counts',{})
        epoch=int(saved.get('epoch',0))
        unresolved=int(saved.get('unresolved',0))
        check(prefix)
        if best:
            check(best)
    t0=time.time(); last=0; status='TIME_BUDGET'
    while time.time()-t0<cfg['wall_seconds']:
        d=len(prefix)
        if d==N:
            best=prefix; status='COMPLETE_SRG'; break
        if len(frames)<=d:
            mode=base_mode if epoch==0 else 'random'
            aa,meta=row_alternatives(prefix,seed+epoch*49979687+int(digest(prefix)[:16],16),cfg,mode)
            counts[meta['status']]=counts.get(meta['status'],0)+1
            unresolved+=int(meta['status']=='LIMIT_UNRESOLVED')
            frames.append({'alts':[hex(x) for x in aa],'next':0,'meta':meta})
        f=frames[d]
        if f['next']<len(f['alts']):
            r=int(f['alts'][f['next']],16); f['next']+=1
            prefix=prefix+(r,)
            if len(prefix)>len(best):
                best=prefix
        else:
            frames.pop()
            if prefix:
                prefix=prefix[:-1]; bt+=1
            else:
                epoch+=1; frames=[]
        if time.time()-last>=cfg['checkpoint_seconds']:
            atomic(cp,{'prefix':[hex(x) for x in prefix],'best':[hex(x) for x in best],
                       'frames':frames,'backtracks':bt,'counts':counts,
                       'epoch':epoch,'unresolved':unresolved})
            last=time.time()
    res={'worker':wid,'mode':base_mode,'status':status,'max_depth':len(best),
         'backtracks':bt,'epochs':epoch,'unresolved':unresolved,
         'counts':counts,'best_sha256':digest(best)}
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
    cfg={'alternatives_per_node':16,'node_limit_initial':250000,'node_limit_max':1000000,
         'solution_scan_initial':512,'solution_scan_max':4096,'adaptive_rounds':3,'adaptive_factor':4}
    root,meta=row_alternatives((),1234,cfg,'random')
    if len(root)<8 or len(set(root))!=len(root):
        raise SystemExit('enumeration regression failed')
    children=0
    for i,r in enumerate(root[:8]):
        aa,_=row_alternatives((r,),9000+i,cfg,'descending')
        children+=bool(aa)
    if children<6:
        raise SystemExit('forward-filter regression failed')
    limited_cfg=dict(cfg); limited_cfg.update({'node_limit_initial':1,'node_limit_max':1,
                                               'solution_scan_initial':1,'solution_scan_max':1,
                                               'adaptive_rounds':1})
    _,lm=row_alternatives((),1,limited_cfg,'random')
    if lm['status']!='LIMIT_UNRESOLVED':
        raise SystemExit('limit-semantics regression failed')
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
    p=dfs((),8,777)
    if p is None:
        raise SystemExit('constructive backtracking regression failed')
    check(p)
    print(json.dumps({'status':'PASS','depth':len(p),'root_alternatives':len(root),
                      'child_good':children,'dfs_nodes':visited,'sha256':digest(p)}))

def main():
    a=argparse.ArgumentParser(); s=a.add_subparsers(dest='cmd',required=True)
    s.add_parser('selftest')
    r=s.add_parser('run'); r.add_argument('config'); r.add_argument('outdir')
    z=a.parse_args()
    selftest() if z.cmd=='selftest' else run(z.config,z.outdir)

if __name__=='__main__':
    main()
