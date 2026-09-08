#!/usr/bin/env python3
"""Structural V3 fixed-K3 certification.

Uses a project-owned WLOG reduction on the two triangular 3-orbits T={12,13}:
* each T vertex has exactly two S-neighbours in each attachment group A0,A1,A2;
* the residual matching-preserving D8 action in each group reduces the ordered
  pair of 2-subsets to seven local types;
* S3 permutes the three attachment groups and S2 swaps the two T vertices;
* S18 on ordinary unattached vertices makes the pair of T-neighbourhoods
  canonical once its intersection size is known;
* the T-pair quotient equation fixes that intersection.

This leaves exactly 72 structural WLOG cases (62 with S_12,13=0 and 10 with
S_12,13=1). Each case is solved/certified independently; hard cases are
split dynamically on remaining primary variables. Progress is reported as
the exact fraction of all admissible labelled T-skeleton patterns whose WLOG
case has been completely certified.
"""
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, itertools, json, math, os, shutil, signal, time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import o3_fixed_triangle_parallel_certify_v2 as base

N=32
GROUPS=(tuple(range(0,4)),tuple(range(4,8)),tuple(range(8,12)))
T=(12,13)
ORD=tuple(range(14,32))
EXPECTED_ROOT_SHA256=base.EXPECTED_ROOT_SHA256

PAIRS=[(i,j) for i in range(N) for j in range(i+1,N)]
PAIR_INDEX={e:k for k,e in enumerate(PAIRS)}
def edge(i,j): return (i,j) if i<j else (j,i)
def svar(i,j): return PAIR_INDEX[edge(i,j)]+1
def lvar(i,j): return 497+PAIR_INDEX[edge(i,j)]

def sha_text(x):
    return hashlib.sha256(x.encode()).hexdigest()

def matching_group():
    M={frozenset((0,1)),frozenset((2,3))}
    H=[]
    for p in itertools.permutations(range(4)):
        img={frozenset((p[0],p[1])),frozenset((p[2],p[3]))}
        if img==M:H.append(p)
    return M,H

def pair_key(x):
    return (tuple(sorted(x[0])),tuple(sorted(x[1])))

def local_types():
    M,H=matching_group()
    subs=[frozenset(x) for x in itertools.combinations(range(4),2)]
    universe=[(A,B) for A in subs for B in subs]
    seen=set();orbs=[]
    for x in universe:
        if x in seen:continue
        orb=set()
        for p in H:
            orb.add((frozenset(p[i] for i in x[0]),frozenset(p[i] for i in x[1])))
        seen|=orb
        rep=min(orb,key=pair_key)
        orbs.append((rep,orb))
    orbs.sort(key=lambda z:pair_key(z[0]))
    if len(H)!=8 or len(orbs)!=7 or len(seen)!=36:
        raise RuntimeError('local orbit self-check failed')
    typ={}
    for k,(_,orb) in enumerate(orbs):
        for x in orb:
            if x in typ:raise RuntimeError('local orbit overlap')
            typ[x]=k
    swap={}
    for k,(rep,_) in enumerate(orbs):
        swap[k]=typ[(rep[1],rep[0])]
    expected={0:0,1:3,2:2,3:1,4:4,5:5,6:6}
    if swap!=expected:raise RuntimeError(f'unexpected T-swap map {swap}')
    inter={k:len(rep[0]&rep[1]) for k,(rep,_) in enumerate(orbs)}
    return universe,orbs,typ,swap,inter

def canon_types(ts,swap):
    a=tuple(sorted(ts))
    b=tuple(sorted(swap[t] for t in ts))
    return min(a,b)

def ord_pair_count(d,c):
    return math.comb(18,d)*math.comb(d,c)*math.comb(18-d,d-c)

def build_case_data():
    universe,orbs,typ,swap,inter=local_types()
    raw_weight=Counter(); raw_group=Counter()
    for s in (0,1):
        d=6-s
        for p0,p1,p2 in itertools.product(universe,repeat=3):
            a=len(p0[0]&p0[1])+len(p1[0]&p1[1])+len(p2[0]&p2[1])
            c=6-5*s-a
            if not (0<=c<=d):continue
            key=(s,canon_types((typ[p0],typ[p1],typ[p2]),swap))
            raw_group[key]+=1
            raw_weight[key]+=ord_pair_count(d,c)
    keys=sorted(raw_weight)
    if len(keys)!=72 or sum(k[0]==0 for k in keys)!=62 or sum(k[0]==1 for k in keys)!=10:
        raise RuntimeError('expected 72 structural cases = 62+10')
    total=sum(raw_weight.values())
    if total!=3544507983744:
        raise RuntimeError(f'unexpected raw T-skeleton total {total}')
    cases=[]
    for idx,key in enumerate(keys):
        s,types=key
        a=sum(inter[t] for t in types);d=6-s;c=6-5*s-a
        lits=[]; desc=[]
        for G,t in zip(GROUPS,types):
            A,B=orbs[t][0]
            A={G[i] for i in A};B={G[i] for i in B}
            for u in G:
                lits.append(svar(T[0],u) if u in A else -svar(T[0],u))
                lits.append(svar(T[1],u) if u in B else -svar(T[1],u))
            desc.append({'type':t,'N12':sorted(A),'N13':sorted(B),'intersection':len(A&B)})
        lits.append(svar(T[0],T[1]) if s else -svar(T[0],T[1]))
        A=set(ORD[:d])
        B=set(ORD[:c])|set(ORD[d:d+(d-c)])
        for u in ORD:
            lits.append(svar(T[0],u) if u in A else -svar(T[0],u))
            lits.append(svar(T[1],u) if u in B else -svar(T[1],u))
        for u in range(N):
            if u!=T[0]:lits.append(-lvar(T[0],u))
            if u!=T[1] and u!=T[0]:lits.append(-lvar(T[1],u))
        if len({abs(x) for x in lits})!=len(lits):
            raise RuntimeError(f'duplicate literals in case {key}')
        if any(-x in lits for x in lits):
            raise RuntimeError(f'conflicting literals in case {key}')
        if sum(1 for u in range(N) if u!=12 and svar(12,u) in lits)!=12:
            raise RuntimeError('T12 S-degree representative failure')
        if sum(1 for u in range(N) if u!=13 and svar(13,u) in lits)!=12:
            raise RuntimeError('T13 S-degree representative failure')
        common=sum(1 for u in range(N) if u not in T and svar(12,u) in lits and svar(13,u) in lits)
        if common!=6-5*s:
            raise RuntimeError(f'T-pair common-neighbour representative failure {key}: {common}')
        cid=f'k{idx:02d}_s{s}_t{"".join(map(str,types))}'
        cases.append({
            'id':cid,'s12_13':s,'local_types':list(types),
            'attached_common':a,'ordinary_common':c,
            'ordinary_degree_each':d,
            'local_description':desc,
            'ordinary_N12':sorted(A),'ordinary_N13':sorted(B),
            'raw_group_patterns':raw_group[key],
            'raw_weight':raw_weight[key],
            'lits':lits,
        })
    manifest_core={
        'format':'CONWAY99-FIXED-K3-STRUCTURAL-WLOG-1',
        'root_sha256':EXPECTED_ROOT_SHA256,
        'local_group_size':8,
        'local_type_count':7,
        'local_types':[{
            'id':k,
            'rep_N12':sorted(rep[0]),
            'rep_N13':sorted(rep[1]),
            'orbit_size':len(orb),
            'intersection':inter[k],
            'T_swap_type':swap[k],
        } for k,(rep,orb) in enumerate(orbs)],
        'case_count':len(cases),
        'case_count_s0':sum(c['s12_13']==0 for c in cases),
        'case_count_s1':sum(c['s12_13']==1 for c in cases),
        'raw_T_skeleton_total':total,
        'cases':cases,
    }
    payload=json.dumps(manifest_core,sort_keys=True,separators=(',',':'))
    manifest_core['self_hash_sha256']=sha_text(payload)
    return manifest_core

def case_done(st,cid):
    leaves=[c for c in st['cubes'].values() if c['case_id']==cid and c['status']!='SPLIT']
    return bool(leaves) and all(c['status']=='CERTIFIED' for c in leaves)

def main():
    ap=argparse.ArgumentParser();home=Path.home()
    ap.add_argument('--root-cnf',default=str(home/'conway99_workspace/o3_reconciliation_runs/review_reconciled_20260907/fixed_triangle/fixed_triangle_o3_quotient.cnf'))
    ap.add_argument('--run-dir',default=str(home/'conway99_workspace/o3_reconciliation_runs/fixed_triangle_structural_v3_20260908'))
    ap.add_argument('--workers',type=int,default=21)
    ap.add_argument('--leaf-seconds',type=int,default=180)
    ap.add_argument('--proof-max-gib',type=float,default=1.0)
    ap.add_argument('--status-seconds',type=int,default=600)
    ap.add_argument('--disk-floor-gib',type=float,default=150)
    ap.add_argument('--admission-free-gib',type=float,default=400)
    ap.add_argument('--mem-floor-gib',type=float,default=4)
    ap.add_argument('--cert-backlog-max',type=int,default=8)
    ap.add_argument('--cert-backlog-gib',type=float,default=8.0)
    ap.add_argument('--preflight-only',action='store_true')
    ap.add_argument('--cadical',default=str(home/'.local/bin/cadical'))
    ap.add_argument('--lrat-check',default=str(home/'.local/bin/lrat-check'))
    ap.add_argument('--cake',default=str(home/'conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr'))
    a=ap.parse_args()
    if not 1<=a.workers<=21:raise SystemExit('workers must be 1..21')
    root=Path(a.root_cnf);run=Path(a.run_dir);jobs=run/'jobs';run.mkdir(parents=True,exist_ok=True);jobs.mkdir(exist_ok=True)
    for p in (root,Path(a.cadical),Path(a.lrat_check),Path(a.cake)):
        if not p.exists():raise SystemExit(f'missing: {p}')
    rh=base.sha(root)
    if rh!=EXPECTED_ROOT_SHA256:raise SystemExit(f'root hash mismatch: {rh}')
    manifest=build_case_data()
    mp=run/'structural_manifest.json'
    if mp.exists():
        old=json.loads(mp.read_text())
        if old.get('self_hash_sha256')!=manifest['self_hash_sha256']:
            raise SystemExit('structural manifest mismatch')
    else:
        base.save(mp,manifest)
    free=shutil.disk_usage(run).free/1024**3;mem=base.mem_available_gib();cpus=os.cpu_count() or 0
    print('=== FIXED-K3 STRUCTURAL CERTIFICATION V3 ===',flush=True)
    print(f'root_sha256={rh}',flush=True)
    print(f'structural_cases=72 (s=0:62, s=1:10) raw_T_skeletons={manifest["raw_T_skeleton_total"]}',flush=True)
    print(f'manifest_sha256={manifest["self_hash_sha256"]}',flush=True)
    print(f'cpus={cpus} workers={a.workers}+1 checker leaf_timeout={a.leaf_seconds}s proof_cap={a.proof_max_gib}GiB',flush=True)
    print(f'admission disk_free={free:.1f}GiB mem_available={mem if mem is not None else "unknown"}GiB',flush=True)
    if cpus and cpus<a.workers+3:raise SystemExit(f'need at least {a.workers+3} CPUs; found {cpus}')
    if free<a.admission_free_gib:raise SystemExit(f'admission refused: disk free {free:.1f}GiB')
    if mem is not None and mem<a.mem_floor_gib+8:raise SystemExit(f'admission refused: MemAvailable {mem:.1f}GiB')
    split_rank,root_fixed=base.split_order(root,992)
    print('STRUCTURAL_PREFLIGHT_PASS local_orbits=7 cases=72 raw_coverage_check=PASS',flush=True)
    if a.preflight_only:
        print('=== PREFLIGHT_PASS ===',flush=True);return

    statep=run/'state.json'
    case_by_id={c['id']:c for c in manifest['cases']}
    if statep.exists():
        st=json.loads(statep.read_text())
        if st.get('root_sha256')!=rh or st.get('manifest_sha256')!=manifest['self_hash_sha256']:
            raise SystemExit('resume state provenance mismatch')
        for c in st['cubes'].values():
            if c['status']=='ACTIVE':c['status']='PENDING'
            elif c['status']=='CERT_ACTIVE':c['status']='CERT_PENDING'
    else:
        cubes={}
        for c in manifest['cases']:
            cubes[c['id']]={
                'id':c['id'],'case_id':c['id'],'depth':0,'lits':c['lits'],
                'status':'PENDING','parent':None,
            }
        st={
            'format':'CONWAY99-FIXED-K3-STRUCTURAL-CERT-3',
            'root_sha256':rh,'manifest_sha256':manifest['self_hash_sha256'],
            'started_at':time.time(),'splits':0,'cubes':cubes,'parameters':vars(a),
        }
        base.save(statep,st)

    def persist():base.save(statep,st)
    def choose_split(c):
        used={abs(x) for x in c['lits']}
        for v in split_rank:
            if v not in used:return v
        raise RuntimeError(f'no split variable left for {c["id"]}')
    def split(c):
        v=choose_split(c);c['status']='SPLIT';c['split_var']=v
        for bit,lit in [('0',-v),('1',v)]:
            cid=c['id']+bit
            if cid not in st['cubes']:
                st['cubes'][cid]={
                    'id':cid,'case_id':c['case_id'],'depth':c['depth']+1,
                    'lits':c['lits']+[lit],'status':'PENDING','parent':c['id'],
                }
        st['splits']+=1
    def progress():
        done=[cid for cid in case_by_id if case_done(st,cid)]
        num=sum(case_by_id[cid]['raw_weight'] for cid in done)
        den=manifest['raw_T_skeleton_total']
        return done,Fraction(num,den)
    def backlog():
        q=[c for c in st['cubes'].values() if c['status'] in ('CERT_PENDING','CERT_ACTIVE')]
        b=0
        for c in q:
            p=jobs/c['id']/'proof.lrat'
            if p.exists():b+=p.stat().st_size
        return len(q),b/1024**3

    pool=cf.ThreadPoolExecutor(max_workers=a.workers)
    cpool=cf.ThreadPoolExecutor(max_workers=1)
    futs={};cfut=None;ccid=None;last=0;done_events=[]
    try:
        while True:
            if any(c['status']=='SAT' for c in st['cubes'].values()):
                st['status']='SAT_QUOTIENT_VERIFIED';persist()
                print('=== CAMPAIGN_COMPLETE_WITH_SAT_QUOTIENT ===',flush=True);break
            done,cv=progress()
            if len(done)==len(case_by_id):
                st['status']='UNSAT_CERTIFIED';st['ended_at']=time.time();persist()
                print('=== CAMPAIGN_PASS all 72 structural WLOG cases LRAT+Cake certified ===',flush=True);break
            free=shutil.disk_usage(run).free/1024**3;mem=base.mem_available_gib()
            if free<a.disk_floor_gib:raise RuntimeError('disk safety floor')
            if mem is not None and mem<a.mem_floor_gib:raise RuntimeError('memory safety floor')
            qn,qg=backlog();throttle=(qn>=a.cert_backlog_max or qg>=a.cert_backlog_gib)
            pend=sorted((c for c in st['cubes'].values() if c['status']=='PENDING'),
                        key=lambda c:(c['depth'], -case_by_id[c['case_id']]['raw_weight'], c['id']))
            while pend and len(futs)<a.workers and not throttle:
                c=pend.pop(0);c['status']='ACTIVE'
                f=pool.submit(base.solve_one,root,dict(c),jobs/c['id'],a.cadical,a.leaf_seconds,a.disk_floor_gib)
                futs[f]=c['id']
            for f in [x for x in futs if x.done()]:
                cid=futs.pop(f);c=st['cubes'][cid];r=f.result();c['last_solve']=r;k=r['kind']
                if k=='UNSAT':
                    if r['proof_bytes']>a.proof_max_gib*1024**3:
                        base.cleanup(jobs/cid);split(c)
                    else:c['status']='CERT_PENDING'
                elif k=='TIMEOUT':
                    base.cleanup(jobs/cid);split(c)
                elif k=='SAT':
                    c['status']='SAT';c['verify']=r.get('verify');st['sat_cube']=cid
                elif k=='RESOURCE':
                    c['status']='PENDING';persist();raise RuntimeError('resource stop')
                else:
                    c['status']='ERROR';persist();raise RuntimeError(f'{cid}: {k}')
            if cfut is None:
                q=sorted((c for c in st['cubes'].values() if c['status']=='CERT_PENDING'),
                         key=lambda c:(c['depth'],-case_by_id[c['case_id']]['raw_weight'],c['id']))
                if q:
                    c=q[0];c['status']='CERT_ACTIVE';ccid=c['id']
                    cfut=cpool.submit(base.certify,jobs[ccid],dict(c),a.lrat_check,a.cake)
            elif cfut.done():
                c=st['cubes'][ccid];caseid=c['case_id'];was_done=case_done(st,caseid)
                r=cfut.result();cfut=None
                if not r.get('ok'):
                    c['status']='ERROR';c['cert_error']=r;persist()
                    raise RuntimeError(f'certificate failure {ccid}: {r}')
                c['status']='CERTIFIED';c['certificate']=r
                if not was_done and case_done(st,caseid):
                    done_events.append((time.time(),case_by_id[caseid]['raw_weight']))
                ccid=None
            persist();now=time.time()
            if now-last>=a.status_seconds:
                done,cv=progress();cnt=Counter(c['status'] for c in st['cubes'].values())
                qn,qg=backlog();recent=[x for x in done_events if x[0]>=now-7200];eta='unknown'
                if len(recent)>=2:
                    dt=max(now-recent[0][0],1.0)
                    dw=sum(x[1] for x in recent)/manifest['raw_T_skeleton_total']
                    if dw>0:eta=f'{(1-float(cv))/(dw/dt)/3600:.2f}h(structural-weighted)'
                open_cases=len(case_by_id)-len(done)
                md=max(c['depth'] for c in st['cubes'].values() if c['status']!='SPLIT')
                print(
                    f'STATUS elapsed={(now-st["started_at"])/3600:.2f}h '
                    f'structural_coverage={float(cv*100):.4f}% classes={len(done)}/72 '
                    f'open_cases={open_cases} certified_leaves={cnt["CERTIFIED"]} '
                    f'active={cnt["ACTIVE"]} pending={cnt["PENDING"]} '
                    f'certq={qn} certq_gib={qg:.2f} throttle={throttle} '
                    f'splits={st["splits"]} max_extra_depth={md} '
                    f'disk_free={free:.1f}GiB mem_free={mem if mem is not None else "unknown"}GiB ETA={eta}',
                    flush=True)
                last=now
            time.sleep(1)
    except KeyboardInterrupt:
        base.stop_children(signal.SIGINT);time.sleep(2);base.stop_children(signal.SIGKILL)
        for c in st['cubes'].values():
            if c['status']=='ACTIVE':c['status']='PENDING'
            elif c['status']=='CERT_ACTIVE':c['status']='CERT_PENDING'
        st['status']='STOPPED_RESUMABLE';persist();print('STOPPED_RESUMABLE',flush=True)
    except Exception:
        base.stop_children(signal.SIGINT);time.sleep(2);base.stop_children(signal.SIGKILL)
        for c in st['cubes'].values():
            if c['status']=='ACTIVE':c['status']='PENDING'
            elif c['status']=='CERT_ACTIVE':c['status']='CERT_PENDING'
        st['status']='ERROR_RESUMABLE';persist()
        raise
    finally:
        pool.shutdown(wait=False,cancel_futures=True);cpool.shutdown(wait=False,cancel_futures=True)

if __name__=='__main__':main()
