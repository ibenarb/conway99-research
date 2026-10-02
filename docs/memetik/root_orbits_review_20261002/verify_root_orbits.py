#!/usr/bin/env python3
from __future__ import annotations
import itertools, json
from collections import defaultdict
from itertools import combinations

MATCH={i:(i+7 if i<7 else i-7) for i in range(14)}
OUTER=tuple((a,b) for a,b in combinations(range(14),2) if MATCH[a]!=b)
assert len(OUTER)==84
U=(0,1)
CANDIDATE_EDGES=tuple(e for e in OUTER if e!=U)
SPECIAL={0,1,MATCH[0],MATCH[1]}
TARGET=tuple(1 if i in SPECIAL else 2 for i in range(14))

def coefficient_count(edges):
    dp={(0,)*14:1}
    for a,b in edges:
        nd=dict(dp)
        for state,n in dp.items():
            if state[a]<TARGET[a] and state[b]<TARGET[b]:
                s=list(state); s[a]+=1; s[b]+=1; s=tuple(s)
                nd[s]=nd.get(s,0)+n
        dp=nd
    return dp.get(TARGET,0)

def make_perm(sigma,flips):
    p=[None]*14
    for i in range(7):
        for side in (0,1):
            p[i+7*side]=sigma[i]+7*(side^flips[i])
    return tuple(p)

def stabilizer_elements():
    out=[]; rest=range(2,7)
    for swap in (False,True):
        for pr in itertools.permutations(rest):
            sigma=list(range(7))
            sigma[0],sigma[1]=(1,0) if swap else (0,1)
            for i,j in zip(rest,pr): sigma[i]=j
            for bits in range(32):
                flips=[0,0]+[(bits>>(i-2))&1 for i in range(2,7)]
                out.append(make_perm(sigma,flips))
    assert len(out)==7680 and len(set(out))==7680
    return out

def signed_cycle_key(p):
    sigma=[]; flips=[]
    for i in range(7):
        image=p[i]; sigma.append(image%7); flips.append(int(image>=7))
    special_swap=int(sigma[0]==1)
    seen=set(); positive=[]; negative=[]
    for i in range(2,7):
        if i in seen: continue
        j=i; parity=0; length=0
        while j not in seen:
            seen.add(j); length+=1; parity^=flips[j]; j=sigma[j]
        (negative if parity else positive).append(length)
    return special_swap,tuple(sorted(positive)),tuple(sorted(negative))

def edge_orbit_contributions(p):
    edge_set=set(CANDIDATE_EDGES); seen=set(); out=[]
    for e in CANDIDATE_EDGES:
        if e in seen: continue
        cyc=[]; cur=e
        while cur not in seen:
            seen.add(cur); cyc.append(cur)
            cur=tuple(sorted((p[cur[0]],p[cur[1]])))
            assert cur in edge_set
        c=[0]*14
        for a,b in cyc: c[a]+=1; c[b]+=1
        out.append(tuple(c))
    return out

def fixed_valid_rows(p):
    dp={(0,)*14:1}
    for c in edge_orbit_contributions(p):
        nd=dict(dp)
        for state,n in dp.items():
            s=[]; ok=True
            for i,x in enumerate(c):
                y=state[i]+x
                if y>TARGET[i]: ok=False; break
                s.append(y)
            if ok:
                s=tuple(s); nd[s]=nd.get(s,0)+n
        dp=nd
    return dp.get(TARGET,0)

def main():
    wrong=coefficient_count(OUTER)
    valid=coefficient_count(CANDIDATE_EDGES)
    stab=stabilizer_elements()
    classes=defaultdict(list)
    for p in stab: classes[signed_cycle_key(p)].append(p)
    assert len(classes)==72
    rows=[]; total=0
    for key,group in sorted(classes.items(),key=lambda kv:repr(kv[0])):
        fixed=fixed_valid_rows(group[0]); mult=len(group); total+=fixed*mult
        rows.append({"special_swap":key[0],
                     "positive_signed_cycle_lengths":list(key[1]),
                     "negative_signed_cycle_lengths":list(key[2]),
                     "class_multiplicity":mult,
                     "fixed_valid_rows":fixed})
    group_order=(2**7)*5040
    stabilizer_order=group_order//84
    assert wrong==58_311_050
    assert valid==56_011_010
    assert stabilizer_order==7680
    assert sum(r["class_multiplicity"] for r in rows)==7680
    assert total==62_246_400
    assert total//7680==8105 and total%7680==0
    print(json.dumps({"outer_vertices":84,
      "full_border_group_order":group_order,
      "H_root_stabilizer_order":stabilizer_order,
      "stabilizer_conjugacy_classes":len(rows),
      "count_if_diagonal_is_wrongly_allowed":wrong,
      "valid_first_rows_diagonal_excluded":valid,
      "burnside_fixed_sum":total,
      "first_row_orbits":total//stabilizer_order,
      "classes":rows},indent=2,sort_keys=True))

if __name__=="__main__": main()
