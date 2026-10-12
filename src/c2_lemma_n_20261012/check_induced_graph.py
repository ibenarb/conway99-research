"""Independently check common-neighbor bounds in the 39-vertex induced graph.
Input: pair_orbits.jsonl; output: JSON report. No matrix-product test is used.
"""
import itertools
import json
from pathlib import Path
import sys


def check(l,n):
    # 0 = root; 1..14 = anchors; 15..26 = W_a; 27..38 = W_b.
    adjacency=[set() for _ in range(39)]
    def edge(x,y):
        adjacency[x].add(y); adjacency[y].add(x)
    for c in range(14):
        edge(0,1+c)
        edge(1+c,1+(c^1))
    for x in range(12):
        edge(15+x,1); edge(15+x,3+x)
        edge(27+x,2); edge(27+x,3+(x^1))
        edge(15+x,15+l[x]); edge(27+x,27+l[x])
        edge(15+x,27+n[x])
    violations=[]
    for x,y in itertools.combinations(range(39),2):
        common=adjacency[x]&adjacency[y]
        bound=1 if y in adjacency[x] else 2
        if len(common)>bound:
            violations.append({'vertices':[x,y],'common_neighbors':sorted(common),'bound':bound})
    return violations


def main(source,destination):
    count=excluded=0
    for line in Path(source).read_text().splitlines():
        row=json.loads(line); bad=check(row['L'],row['N'])
        assert bool(bad)==(not row['passes_local_filter'])
        count+=1; excluded+=bool(bad)
    p=[x^1 for x in range(12)]
    l=[2,3,0,1]+p[4:]; n=[3,2,1,0]+p[4:]
    witness=check(l,n)
    assert any(r['vertices']==[15,28] and r['common_neighbors']==[3,17,30] for r in witness)
    report={'status':'PASS','pair_orbits_checked':count,'excluded':excluded,
            'surviving':count-excluded,'counterexample':{'L':l,'N':n,'violations':witness},
            'scope':'All pairwise common-neighbor upper bounds in the fully specified induced 39-vertex graph. Extension to 99 vertices remains open.'}
    Path(destination).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main(*sys.argv[1:])
