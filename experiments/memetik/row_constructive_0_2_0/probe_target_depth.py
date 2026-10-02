#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json

from diagnose_next import load_best
from probe_depth18 import verify, enum_rows
from row_build import N

def state_seed(rows, base_seed, target):
    h=hashlib.sha256()
    for u,r in sorted(rows.items()):
        h.update(bytes([u]))
        h.update(r.to_bytes(11,"little"))
    h.update(bytes([target]))
    return base_seed ^ int.from_bytes(h.digest()[:8],"little")

def search(rows, target_depth, base_seed, node_limit, solution_limit, memo, stats):
    verify(rows)
    stats["states_visited"]+=1
    if len(rows)>=target_depth:
        return "FOUND", []

    key=tuple(sorted(rows.items()))
    if key in memo:
        stats["memo_hits"]+=1
        return memo[key], None

    extensions=[]
    local_limit=False
    feasible_rows=[]

    for q in range(N):
        if q in rows:
            continue
        rr,nodes,stop=enum_rows(
            rows,q,state_seed(rows,base_seed,q),
            node_limit,solution_limit
        )
        stats["row_tests"]+=1
        stats["enum_nodes"]+=nodes
        if stop:
            local_limit=True
            stats["limit_events"]+=1
        if rr:
            feasible_rows.append({
                "full_row":16+q,
                "solutions":len(rr),
                "nodes":nodes,
                "stop":stop,
            })
            for r in rr:
                extensions.append((len(rr),nodes,q,r))

    stats["frontiers"].append({
        "built_count":len(rows),
        "feasible_row_count":len(feasible_rows),
        "feasible_rows":feasible_rows,
    })

    extensions.sort(key=lambda x:(x[0],x[1],x[2],x[3]))

    if not extensions:
        status="LIMIT" if local_limit else "DEAD"
        memo[key]=status
        return status,None

    any_limit=local_limit
    for _,_,q,r in extensions:
        child=dict(rows)
        child[q]=r
        verify(child)
        status,path=search(
            child,target_depth,base_seed,node_limit,solution_limit,memo,stats
        )
        if status=="FOUND":
            return "FOUND",[(q,r)]+path
        if status=="LIMIT":
            any_limit=True

    status="LIMIT" if any_limit else "DEAD"
    memo[key]=status
    return status,None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness")
    ap.add_argument("--base-depth",type=int,default=15)
    ap.add_argument("--target-depth",type=int,default=19)
    ap.add_argument("--seed",type=int,default=2026100216)
    ap.add_argument("--node-limit",type=int,default=128_000_000)
    ap.add_argument("--solution-limit",type=int,default=65_536)
    a=ap.parse_args()

    full=load_best(a.witness)
    if not 0<=a.base_depth<=len(full):
        raise ValueError("invalid base depth")
    if not a.base_depth<=a.target_depth<=N:
        raise ValueError("invalid target depth")

    rows={i:full[i] for i in range(a.base_depth)}
    verify(rows)
    stats={
        "states_visited":0,
        "memo_hits":0,
        "row_tests":0,
        "enum_nodes":0,
        "limit_events":0,
        "frontiers":[],
    }
    status,path=search(
        rows,a.target_depth,a.seed,a.node_limit,a.solution_limit,{},stats
    )

    out={
        "source":a.witness,
        "base_depth":a.base_depth,
        "target_depth":a.target_depth,
        "status":
            f"FOUND_DEPTH{a.target_depth}" if status=="FOUND"
            else "LIMIT_UNRESOLVED" if status=="LIMIT"
            else f"EXHAUSTIVE_NO_DEPTH{a.target_depth}",
        "stats":{
            k:v for k,v in stats.items() if k!="frontiers"
        },
    }

    if path is not None:
        out["added_rows"]=[
            {"full_row":16+q,"H_row_zero_based":q,"row_hex":hex(r)}
            for q,r in path
        ]
        final=dict(rows)
        for q,r in path:
            final[q]=r
        verify(final)
        out["built_count"]=len(final)
        out["built_full_rows"]=[16+q for q in sorted(final)]
    else:
        # Keep output compact but preserve every distinct frontier summary.
        seen=set()
        fs=[]
        for x in stats["frontiers"]:
            sig=(x["built_count"],tuple(
                (r["full_row"],r["solutions"],r["stop"])
                for r in x["feasible_rows"]
            ))
            if sig not in seen:
                seen.add(sig); fs.append(x)
        out["frontiers"]=fs

    print(json.dumps(out,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
