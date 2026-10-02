#!/usr/bin/env python3
from __future__ import annotations
import argparse, json

from diagnose_next import load_best
from probe_depth18 import verify, enum_rows
from row_build import N

def parse_addition(s):
    a,b=s.split(":",1)
    full=int(a)
    if not 16<=full<=99:
        raise ValueError("full row must be 16..99")
    return full-16,int(b,16)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness")
    ap.add_argument("--base-depth",type=int,default=16)
    ap.add_argument("--add",action="append",default=[])
    ap.add_argument("--node-limit",type=int,default=8_000_000)
    ap.add_argument("--seed",type=int,default=2026100216)
    a=ap.parse_args()

    full=load_best(a.witness)
    if a.base_depth>len(full):
        raise ValueError("base depth exceeds witness")
    rows={i:full[i] for i in range(a.base_depth)}
    for spec in a.add:
        u,r=parse_addition(spec)
        if u in rows:
            raise ValueError(f"duplicate built row {u+16}")
        rows[u]=r
    verify(rows)

    out=[]
    for q in range(N):
        if q in rows:
            continue
        rr,nodes,stop=enum_rows(rows,q,a.seed+q*104729,a.node_limit,1)
        out.append({
            "full_row_one_based":16+q,
            "status":"SAT" if rr else ("LIMIT" if stop else "UNSAT"),
            "nodes":nodes,
            "stop":stop,
            "row_hex":hex(rr[0]) if rr else None,
        })

    sat=[x for x in out if x["status"]=="SAT"]
    unsat=[x for x in out if x["status"]=="UNSAT"]
    limited=[x for x in out if x["status"]=="LIMIT"]
    print(json.dumps({
        "source":a.witness,
        "base_depth":a.base_depth,
        "built_full_rows":[16+x for x in sorted(rows)],
        "built_count":len(rows),
        "sat_count":len(sat),
        "unsat_count":len(unsat),
        "limit_count":len(limited),
        "sat_rows":[x["full_row_one_based"] for x in sat],
        "rows":out,
    },sort_keys=True))

if __name__=="__main__":
    main()
