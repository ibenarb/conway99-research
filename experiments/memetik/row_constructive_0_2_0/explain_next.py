#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from diagnose_next import load_best, core_problem
from row_build import enumerate_subsets, OUTER, digest

def labels_for(u):
    return [f"border[{a}]" for a in range(14)] + [f"pair_with_Hrow[{v}]" for v in range(u)]

def projected(features, req, active, k):
    pos={c:i for i,c in enumerate(active)}
    card=len(active)
    pf=[]
    for fs in features:
        g={pos[c] for c in fs if c in pos}
        g.add(card)
        pf.append(g)
    pr=[req[c] for c in active]+[k]
    return pf,pr

def solve_active(features, req, k, active, node_limit=2_000_000):
    pf,pr=projected(features,req,active,k)
    sols,nodes,stop=enumerate_subsets(
        pf,pr,k,123456789,"ascending",node_limit,1
    )
    if sols:
        return "SAT",nodes
    if stop is None:
        return "UNSAT",nodes
    return "LIMIT",nodes

def small_core(features,req,k,nc):
    for size in (1,2,3):
        for active in combinations(range(nc),size):
            status,nodes=solve_active(features,req,k,active)
            if status=="UNSAT":
                return list(active),nodes
    return None,None

def irreducible_core(features,req,k,nc):
    active=list(range(nc))
    full_status,full_nodes=solve_active(features,req,k,active,20_000_000)
    if full_status!="UNSAT":
        return None,{"full_status":full_status,"full_nodes":full_nodes}
    changed=True
    tests=0
    limited=0
    while changed:
        changed=False
        for c in active[:]:
            trial=[x for x in active if x!=c]
            status,nodes=solve_active(features,req,k,trial,5_000_000)
            tests+=1
            if status=="UNSAT":
                active=trial
                changed=True
            elif status=="LIMIT":
                limited+=1
    return active,{"full_status":"UNSAT","full_nodes":full_nodes,"shrink_tests":tests,"limited_tests":limited}

def regression():
    # A zero-only projected constraint must not make an otherwise possible
    # cardinality choice UNSAT. This caught the 0.1 explainer bug.
    features=[set(),set(),set()]
    req=[0]
    status,_=solve_active(features,req,2,[0],1000)
    if status!="SAT":
        raise SystemExit("projection-cardinality regression failed")

def explain(path):
    prefix=load_best(path)
    prob=core_problem(prefix)
    if prob is None:
        return {"file":str(path),"depth":len(prefix),"status":"TRIVIAL_INFEASIBLE"}
    u,L,k,req,cand,features=prob
    labels=labels_for(u)
    availability=[sum(c in fs for fs in features) for c in range(len(req))]
    base={
        "file":str(path),
        "depth":len(prefix),
        "prefix_sha256":digest(prefix),
        "next_H_row_zero_based":u,
        "next_full_row_one_based":16+u,
        "left_degree":L.bit_count(),
        "future_ones_needed":k,
        "candidate_columns":len(cand),
        "border_residuals":req[:14],
        "pair_residuals":req[14:],
        "constraint_availability":[
            {"constraint":labels[i],"required":req[i],"available":availability[i]}
            for i in range(len(req))
        ],
    }
    core,nodes=small_core(features,req,k,len(req))
    if core is not None:
        base["certificate"]={
            "type":f"UNSAT_CORE_SIZE_{len(core)}",
            "constraints":[
                {"index":i,"name":labels[i],"required":req[i],"available":availability[i]}
                for i in core
            ],
            "nodes":nodes,
        }
        return base
    core,meta=irreducible_core(features,req,k,len(req))
    base["shrink_meta"]=meta
    if core is not None:
        base["certificate"]={
            "type":"DELETION_IRREDUCIBLE_CORE",
            "size":len(core),
            "constraints":[
                {"index":i,"name":labels[i],"required":req[i],"available":availability[i]}
                for i in core
            ],
        }
    return base

def main():
    regression()
    ap=argparse.ArgumentParser()
    ap.add_argument("witness",nargs="+")
    args=ap.parse_args()
    for p in args.witness:
        print(json.dumps(explain(p),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
