#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, time
from pathlib import Path

from row_build import (
    N, OUTER, left, margins, want, check, future_ok,
    enumerate_subsets, row_alternatives, digest,
)

def load_best(path):
    data=json.loads(Path(path).read_text())
    raw=data.get("best")
    if not raw:
        raise ValueError(f"{path}: missing best prefix")
    prefix=tuple(int(x,16) if isinstance(x,str) else int(x) for x in raw)
    check(prefix)
    return prefix

def core_problem(prefix):
    u=len(prefix)
    L=left(prefix,u)
    k=12-L.bit_count()
    req=margins(u)
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
    cand=list(range(u+1,N))
    feat=[]
    for w in cand:
        f=set(OUTER[w])
        f.update(14+v for v in range(u) if (prefix[v]>>w)&1)
        feat.append(f)
    return u,L,k,req,cand,feat

def core_exists(prefix, seed, limits):
    prob=core_problem(prefix)
    if prob is None:
        return {"status":"NO_EXACT","nodes":0}
    u,L,k,req,cand,feat=prob
    total=0
    for round_no,node_limit in enumerate(limits):
        sols,nodes,stop=enumerate_subsets(
            feat,req,k,seed+round_no*32452843,"random",node_limit,1
        )
        total+=nodes
        if sols:
            a=sols[0]
            r=L
            for i,w in enumerate(cand):
                if (a>>i)&1:
                    r|=1<<w
            q=prefix+(r,)
            check(q)
            return {
                "status":"YES_EXACT",
                "round":round_no,
                "nodes_last":nodes,
                "nodes_sum":total,
                "row_hex":hex(r),
                "forward_ok":future_ok(q),
            }
        if stop is None:
            return {
                "status":"NO_EXACT",
                "round":round_no,
                "nodes_last":nodes,
                "nodes_sum":total,
            }
    return {
        "status":"LIMIT_UNRESOLVED",
        "round":len(limits)-1,
        "nodes_sum":total,
    }

def forward_exists(prefix,seed):
    cfg={
        "alternatives_per_node":1,
        "solution_scan_initial":4096,
        "solution_scan_max":262144,
        "node_limit_initial":2000000,
        "node_limit_max":128000000,
        "adaptive_rounds":4,
        "adaptive_factor":4,
    }
    rows,meta=row_alternatives(prefix,seed,cfg,"random")
    result={"status":meta["status"],"meta":meta}
    if rows:
        q=prefix+(rows[0],)
        check(q)
        if not future_ok(q):
            raise RuntimeError("forward witness failed independent future_ok")
        result.update({"exists":True,"row_hex":hex(rows[0])})
    else:
        result["exists"]=False if meta["status"] in (
            "EXACT_INFEASIBLE","FORWARD_INFEASIBLE",
            "POST_FORWARD_EXHAUSTED","FEASIBLE_EXHAUSTIVE"
        ) else None
    return result

def diagnose(path,seed):
    prefix=load_best(path)
    if len(prefix)!=17:
        raise ValueError(f"{path}: expected depth 17, got {len(prefix)}")
    t0=time.time()
    core=core_exists(prefix,seed,[2_000_000,8_000_000,32_000_000,128_000_000])
    forward=forward_exists(prefix,seed+700000001)
    return {
        "file":str(path),
        "depth":len(prefix),
        "prefix_sha256":digest(prefix),
        "next_h_row_index_zero_based":len(prefix),
        "next_full_row_one_based":16+len(prefix),
        "core_without_future":core,
        "with_forward_checks":forward,
        "elapsed_s":time.time()-t0,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness",nargs="+")
    ap.add_argument("--seed",type=int,default=2026100213)
    args=ap.parse_args()
    for i,p in enumerate(args.witness):
        result=diagnose(p,args.seed+i*1000003)
        print(json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
