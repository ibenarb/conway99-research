#!/usr/bin/env python3
from __future__ import annotations
import argparse, json

from diagnose_next import load_best
from probe_depth18 import verify, enum_rows
from row_build import N

def all_rows(rows,target,seed,node_limit,solution_limit):
    rr,nodes,stop=enum_rows(rows,target,seed,node_limit,solution_limit)
    return rr,{"nodes":nodes,"stop":stop,"count":len(rr)}

def probe(path,base_depth,seed,node_limit,solution_limit):
    full=load_best(path)
    if base_depth>len(full):
        raise ValueError("base depth exceeds witness")
    base={i:full[i] for i in range(base_depth)}
    verify(base)

    unresolved=[]
    depth17=[]
    depth18_states=0
    depth18_by_first={}
    tested_third=0

    for a in range(N):
        if a in base:
            continue
        first,meta1=all_rows(base,a,seed+a*1009,node_limit,solution_limit)
        if meta1["stop"]:
            unresolved.append({"stage":17,"row":16+a,**meta1})
        if not first:
            continue
        depth17.append({"full_row":16+a,"solutions":len(first),"meta":meta1})

        for ia,ra in enumerate(first):
            s17=dict(base); s17[a]=ra; verify(s17)
            key=str(16+a)
            depth18_by_first.setdefault(key,0)

            for b in range(N):
                if b in s17:
                    continue
                second,meta2=all_rows(
                    s17,b,seed+1000003*a+104729*ia+b,node_limit,solution_limit
                )
                if meta2["stop"]:
                    unresolved.append({
                        "stage":18,"first_full_row":16+a,
                        "first_index":ia,"row":16+b,**meta2
                    })
                if not second:
                    continue

                for ib,rb in enumerate(second):
                    s18=dict(s17); s18[b]=rb; verify(s18)
                    depth18_states+=1
                    depth18_by_first[key]+=1

                    sat_third=[]
                    limit_third=[]
                    for c in range(N):
                        if c in s18:
                            continue
                        third,nodes3,stop3=enum_rows(
                            s18,c,
                            seed+2000003*a+15485863*b+8191*ib+c,
                            node_limit,1
                        )
                        tested_third+=1
                        if third:
                            verify({**s18,c:third[0]})
                            return {
                                "status":"FOUND_DEPTH19",
                                "source":path,
                                "base_depth":base_depth,
                                "first_full_row":16+a,
                                "second_full_row":16+b,
                                "third_full_row":16+c,
                                "first_index":ia,
                                "second_index":ib,
                                "first_row_hex":hex(ra),
                                "second_row_hex":hex(rb),
                                "third_row_hex":hex(third[0]),
                                "depth17_summary":depth17,
                                "depth18_states_examined":depth18_states,
                                "tested_third_rows":tested_third,
                                "unresolved":unresolved,
                            }
                        if stop3:
                            limit_third.append({"row":16+c,"stop":stop3,"nodes":nodes3})
                    if limit_third:
                        unresolved.append({
                            "stage":19,"first_full_row":16+a,
                            "second_full_row":16+b,
                            "first_index":ia,"second_index":ib,
                            "limits":limit_third
                        })

    return {
        "status":"LIMIT_UNRESOLVED" if unresolved else "EXHAUSTIVE_NO_DEPTH19",
        "source":path,
        "base_depth":base_depth,
        "depth17_summary":depth17,
        "depth18_states_examined":depth18_states,
        "depth18_by_first":depth18_by_first,
        "tested_third_rows":tested_third,
        "unresolved":unresolved,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("witness")
    ap.add_argument("--base-depth",type=int,default=16)
    ap.add_argument("--seed",type=int,default=2026100216)
    ap.add_argument("--node-limit",type=int,default=128_000_000)
    ap.add_argument("--solution-limit",type=int,default=65_536)
    a=ap.parse_args()
    print(json.dumps(probe(
        a.witness,a.base_depth,a.seed,a.node_limit,a.solution_limit
    ),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
