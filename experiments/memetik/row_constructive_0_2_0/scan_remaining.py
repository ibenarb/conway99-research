#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from diagnose_next import load_best
from row_build import N, OUTER, margins, want, enumerate_subsets, digest, check

def exact_problem_for_row(prefix,j):
    built=range(len(prefix))
    L=sum(1<<v for v in built if (prefix[v]>>j)&1)
    k=12-L.bit_count()
    if k<0:
        return None
    req=margins(j)
    for v in built:
        if (L>>v)&1:
            for a in OUTER[v]:
                req[a]-=1
    if min(req)<0:
        return None
    for v in built:
        e=(prefix[v]>>j)&1
        known=(L&prefix[v]&((1<<len(prefix))-1)).bit_count()
        req.append(want(j,v,e)-known)
    if min(req)<0:
        return None
    candidates=[w for w in range(len(prefix),N) if w!=j]
    if k>len(candidates):
        return None
    feat=[]
    for w in candidates:
        f=set(OUTER[w])
        f.update(14+v for v in built if (prefix[v]>>w)&1)
        feat.append(f)
    return L,k,req,candidates,feat

def scan_one(prefix,j,seed,node_limit):
    prob=exact_problem_for_row(prefix,j)
    if prob is None:
        return {"row_H_zero_based":j,"full_row_one_based":16+j,"status":"TRIVIAL_UNSAT"}
    L,k,req,cand,feat=prob
    sols,nodes,stop=enumerate_subsets(feat,req,k,seed,"random",node_limit,1)
    if sols:
        a=sols[0]; r=L
        for i,w in enumerate(cand):
            if (a>>i)&1:
                r|=1<<w
        return {
            "row_H_zero_based":j,
            "full_row_one_based":16+j,
            "status":"SAT",
            "nodes":nodes,
            "left_degree":L.bit_count(),
            "future_ones_needed":k,
            "row_hex":hex(r),
        }
    return {
        "row_H_zero_based":j,
        "full_row_one_based":16+j,
        "status":"LIMIT" if stop else "UNSAT",
        "nodes":nodes,
        "left_degree":L.bit_count(),
        "future_ones_needed":k,
        "stop":stop,
    }

def scan(path,seed,node_limit):
    prefix=load_best(path)
    d=len(prefix)
    if d!=17:
        raise ValueError(f"expected depth 17, got {d}")
    rows=[]
    for j in range(d,N):
        rows.append(scan_one(prefix,j,seed+j*104729,node_limit))
    return {
        "file":str(path),
        "prefix_sha256":digest(prefix),
        "depth":d,
        "remaining_rows":N-d,
        "sat_count":sum(r["status"]=="SAT" for r in rows),
        "unsat_count":sum(r["status"] in ("UNSAT","TRIVIAL_UNSAT") for r in rows),
        "limit_count":sum(r["status"]=="LIMIT" for r in rows),
        "rows":rows,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness",nargs="+")
    ap.add_argument("--node-limit",type=int,default=8_000_000)
    ap.add_argument("--seed",type=int,default=2026100214)
    args=ap.parse_args()
    for i,p in enumerate(args.witness):
        print(json.dumps(scan(p,args.seed+i*1000003,args.node_limit),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
