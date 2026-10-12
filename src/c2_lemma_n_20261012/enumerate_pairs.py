"""Exact ordered (L,N) orbit census under Aut(P), plus necessary local filter.
No SAT solver. Independent orbit enumeration and Burnside counts agree.
Run: python enumerate_pairs.py OUTPUT_DIRECTORY
"""
import collections
import itertools
import json
import math
from pathlib import Path
import sys
import time


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for i, b in enumerate(vertices[1:], 1):
        for rest in matchings(vertices[1:i] + vertices[i+1:]):
            yield ((a,b),) + rest


def parts(n, low=1):
    if n == 0:
        yield ()
    for k in range(low,n+1):
        for rest in parts(n-k,k):
            yield (k,) + rest


def representative(partition):
    p = [-1]*12
    start = 0
    for size in partition:
        for i in range(size):
            a,b = 2*(start+i)+1, 2*(start+(i+1)%size)
            p[a],p[b] = b,a
        start += size
    return tuple(p)


def transform(p,g):
    result = [0]*12
    for i in range(12):
        result[g[i]] = g[p[i]]
    return tuple(result)


def fixed_matchings(g):
    # An invariant matching either pairs equal-length cycles (l alignments),
    # or pairs an even cycle internally by its half-turn (one choice).
    unseen=set(range(12)); cycles=collections.Counter()
    while unseen:
        x=next(iter(unseen)); count=0
        while x in unseen:
            unseen.remove(x); count+=1; x=g[x]
        cycles[count]+=1
    result=1
    for length,a in cycles.items():
        total=0
        for k in range(a//2+1):
            if length%2 and 2*k!=a:
                continue
            total += math.factorial(a)//(math.factorial(a-2*k)*2**k*math.factorial(k))*length**k
        result*=total
    return result


def violations(l,n):
    return tuple(x for x in range(12) if l[n[x]] == (x^1) and n[l[x]] == (x^1))


def main(destination):
    start=time.monotonic(); out=Path(destination); out.mkdir(parents=True,exist_ok=True)
    all_m=[]
    for edges in matchings(tuple(range(12))):
        p=[0]*12
        for a,b in edges: p[a],p[b]=b,a
        all_m.append(tuple(p))
    assert len(set(all_m))==10395
    group=[]
    for perm in itertools.permutations(range(6)):
        for flips in itertools.product(range(2),repeat=6):
            group.append(tuple(2*perm[x//2]+((x%2)^flips[x//2]) for x in range(12)))
    assert len(set(group))==46080
    fixed={g:fixed_matchings(g) for g in group}
    rows=[]; records=[]; labelled_total=0; valid_labelled_total=0
    for partition in parts(6):
        l=representative(partition)
        stabilizer=[g for g in group if all(g[l[x]]==l[g[x]] for x in range(12))]
        seen=set(); count=valid=0; row_weight=valid_weight=0
        for n in all_m:
            if n in seen: continue
            orbit={transform(n,g) for g in stabilizer}
            assert not (orbit & seen)
            seen.update(orbit); count+=1; row_weight+=len(orbit)
            canonical=min(orbit)
            bad=violations(l,canonical)
            # Check invariance on every element, not only representative.
            assert all(bool(violations(l,v))==bool(bad) for v in orbit)
            aut=len(stabilizer)//len(orbit)
            assert aut*len(orbit)==len(stabilizer)
            weight=46080//aut
            labelled_total+=weight
            if not bad:
                valid+=1; valid_weight+=len(orbit); valid_labelled_total+=weight
            records.append({'partition':partition,'d_plus':partition.count(1),
                'd_minus':sum(canonical[x]==(x^1) for x in range(12))//2,
                'L':l,'N':canonical,'automorphisms':aut,'pair_orbit_size':weight,
                'passes_local_filter':not bool(bad),'violating_vertices':bad})
        burnside=sum(fixed[g] for g in stabilizer)//len(stabilizer)
        assert sum(fixed[g] for g in stabilizer)%len(stabilizer)==0
        assert count==burnside and row_weight==10395 and len(seen)==10395
        row={'partition':partition,'d_plus':partition.count(1),'stabilizer_L':len(stabilizer),
             'orbits':count,'burnside':burnside,'locally_excluded':count-valid,
             'surviving':valid,'labelled_N_surviving':valid_weight}
        rows.append(row); print(json.dumps(row),flush=True)
    assert labelled_total==10395**2
    # Independent full-group Burnside calculation of ordered pair orbits.
    global_burnside=sum(v*v for v in fixed.values())//46080
    assert sum(v*v for v in fixed.values())%46080==0
    assert global_burnside==len(records)
    by_degree=[]
    for d in (0,1,2,3,4,6):
        rr=[r for r in rows if r['d_plus']==d]
        by_degree.append({'d_plus':d,**{k:sum(r[k] for r in rr) for k in ('orbits','locally_excluded','surviving')}})
    summary={'status':'PASS','group_order':46080,'matchings':10395,'ordered_pair_orbits':len(records),
        'global_burnside':global_burnside,'labelled_pairs':labelled_total,
        'labelled_pairs_surviving':valid_labelled_total,'by_partition':rows,'by_degree':by_degree,
        'LOW_orbits':sum(r['orbits'] for r in rows if r['d_plus']<=2),
        'LOW_surviving':sum(r['surviving'] for r in rows if r['d_plus']<=2),
        'seconds':time.monotonic()-start,
        'scope':'Necessary local filter only; surviving pairs are not asserted globally feasible.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'pair_orbits.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main(sys.argv[1])
