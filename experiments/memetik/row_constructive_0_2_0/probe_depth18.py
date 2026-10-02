#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

from diagnose_next import load_best
from row_build import N, OUTER, margins, want, enumerate_subsets

def verify(rows):
    ids=sorted(rows)
    for u in ids:
        r=rows[u]
        if r.bit_count()!=12 or ((r>>u)&1):
            raise ValueError("degree/diagonal")
        c=[0]*14
        for w in range(N):
            if (r>>w)&1:
                for a in OUTER[w]:
                    c[a]+=1
        if c!=margins(u):
            raise ValueError("border margins")
    for i,u in enumerate(ids):
        for v in ids[:i]:
            e=(rows[u]>>v)&1
            if e!=((rows[v]>>u)&1):
                raise ValueError("symmetry")
            if (rows[u]&rows[v]).bit_count()!=want(u,v,e):
                raise ValueError("resolved pair")

def problem(rows,target):
    ids=sorted(rows)
    if target in rows:
        return None
    mask=sum(1<<v for v in ids)
    L=sum(1<<v for v in ids if (rows[v]>>target)&1)
    k=12-L.bit_count()
    if k<0:
        return None
    req=margins(target)
    for v in ids:
        if (L>>v)&1:
            for a in OUTER[v]:
                req[a]-=1
    if min(req)<0:
        return None
    for v in ids:
        e=(rows[v]>>target)&1
        known=(L&rows[v]&mask).bit_count()
        req.append(want(target,v,e)-known)
    if min(req)<0:
        return None
    cand=[w for w in range(N) if w not in rows and w!=target]
    if k>len(cand):
        return None
    feat=[]
    for w in cand:
        f=set(OUTER[w])
        for i,v in enumerate(ids):
            if (rows[v]>>w)&1:
                f.add(14+i)
        feat.append(f)
    return L,k,req,cand,feat

def enum_rows(rows,target,seed,node_limit,solution_limit):
    p=problem(rows,target)
    if p is None:
        return [],0,None
    L,k,req,cand,feat=p
    sols,nodes,stop=enumerate_subsets(
        feat,req,k,seed,"random",node_limit,solution_limit
    )
    out=[]
    for a in sols:
        r=L
        for i,w in enumerate(cand):
            if (a>>i)&1:
                r|=1<<w
        q=dict(rows); q[target]=r
        verify(q)
        out.append(r)
    return out,nodes,stop

def probe(path,seed,first_nodes,second_nodes,first_limit):
    full=load_best(path)
    if len(full)<17:
        raise ValueError("need depth-17 witness")
    rows0={i:full[i] for i in range(16)}
    verify(rows0)
    feasible=[]
    for t in range(N):
        if t in rows0:
            continue
        rr,nodes,stop=enum_rows(rows0,t,seed+t*1009,second_nodes,1)
        if rr:
            feasible.append(t)
        elif stop:
            return {"status":"LIMIT_FINDING_FIRST_ROWS","target":t,"stop":stop}
    trials=[]
    order=sorted(feasible,key=lambda x:(x==16,x))
    for t in order:
        first,fnodes,fstop=enum_rows(
            rows0,t,seed+1000003*t,first_nodes,first_limit
        )
        trial={"first_H_row":t,"first_full_row":16+t,
               "first_solutions_scanned":len(first),
               "first_nodes":fnodes,"first_stop":fstop}
        unresolved=0
        for idx,r in enumerate(first):
            rows1=dict(rows0); rows1[t]=r
            for q in range(N):
                if q in rows1:
                    continue
                rr,nodes,stop=enum_rows(
                    rows1,q,seed+2000003*t+104729*idx+q,second_nodes,1
                )
                if rr:
                    rows2=dict(rows1); rows2[q]=rr[0]; verify(rows2)
                    return {
                        "status":"FOUND_DEPTH18",
                        "source":str(path),
                        "first_feasible_full_rows":[16+x for x in feasible],
                        "first_choice_full_row":16+t,
                        "second_choice_full_row":16+q,
                        "first_candidate_index":idx,
                        "first_row_hex":hex(r),
                        "second_row_hex":hex(rr[0]),
                        "built_H_rows":sorted(rows2),
                        "trial":trial,
                    }
                if stop:
                    unresolved+=1
        trial["second_unresolved"]=unresolved
        trials.append(trial)
        if fstop or unresolved:
            return {
                "status":"LIMIT_UNRESOLVED",
                "source":str(path),
                "first_feasible_full_rows":[16+x for x in feasible],
                "trials":trials,
            }
    return {
        "status":"EXHAUSTIVE_NO_DEPTH18",
        "source":str(path),
        "first_feasible_full_rows":[16+x for x in feasible],
        "trials":trials,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness",nargs="+")
    ap.add_argument("--seed",type=int,default=2026100215)
    ap.add_argument("--first-nodes",type=int,default=128_000_000)
    ap.add_argument("--second-nodes",type=int,default=8_000_000)
    ap.add_argument("--first-limit",type=int,default=65_536)
    a=ap.parse_args()
    for i,p in enumerate(a.witness):
        print(json.dumps(probe(
            p,a.seed+i*10000019,a.first_nodes,a.second_nodes,a.first_limit
        ),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
