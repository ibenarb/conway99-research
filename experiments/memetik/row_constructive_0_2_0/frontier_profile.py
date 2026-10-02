#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from diagnose_next import load_best
from scan_remaining import scan_one
from row_build import N, digest, check

def profile(path,seed,node_limit):
    full=load_best(path)
    if len(full)<1:
        raise ValueError("empty witness")
    depths=[]
    for d in range(len(full)+1):
        prefix=full[:d]
        check(prefix)
        rows=[]
        for j in range(d,N):
            rows.append(scan_one(prefix,j,seed+d*1000003+j*104729,node_limit))
        sat=[r for r in rows if r["status"]=="SAT"]
        unsat=[r for r in rows if r["status"] in ("UNSAT","TRIVIAL_UNSAT")]
        limited=[r for r in rows if r["status"]=="LIMIT"]
        depths.append({
            "depth":d,
            "prefix_sha256":digest(prefix),
            "remaining_rows":N-d,
            "sat_count":len(sat),
            "unsat_count":len(unsat),
            "limit_count":len(limited),
            "sat_rows_full_one_based":[r["full_row_one_based"] for r in sat],
            "min_sat_nodes":min((r.get("nodes",10**18) for r in sat),default=None),
            "max_sat_nodes":max((r.get("nodes",0) for r in sat),default=None),
        })
    return {
        "file":str(path),
        "witness_depth":len(full),
        "witness_sha256":digest(full),
        "node_limit":node_limit,
        "depths":depths,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness",nargs="+")
    ap.add_argument("--node-limit",type=int,default=8_000_000)
    ap.add_argument("--seed",type=int,default=2026100215)
    args=ap.parse_args()
    for i,p in enumerate(args.witness):
        print(json.dumps(profile(p,args.seed+i*10000019,args.node_limit),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
