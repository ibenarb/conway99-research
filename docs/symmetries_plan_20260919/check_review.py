"""Small independent review checks; no SAT searches. Uses archived frame definitions."""
import sys
import json
from itertools import combinations, permutations, product
from pathlib import Path
source = Path('src/c2_matching_20260915')
if not source.exists():
    source = Path('c2_matching_20260915')
sys.path.insert(0, str(source.resolve()))
from c2_reference import CNF, Frame
from matching_orbits import canonical_matching, normalized

cnf = CNF()
f = Frame(14)
f.allocate(cnf)
parts_list = [(1,1,1,1,1,1),(1,1,1,1,2),(1,1,1,3),(1,1,2,2),(1,1,4),(1,2,3),(1,5),(2,2,2),(2,4),(3,3),(6,)]
rows = []
for parts in parts_list:
    matching = canonical_matching(parts)
    stabilizers = []
    for perm in permutations(range(6)):
        for flips in product(range(2), repeat=6):
            p = [2*perm[a//2]+((a%2)^flips[a//2]) for a in range(12)]
            if normalized((p[a],p[b]) for a,b in matching) == matching:
                stabilizers.append(p)
    identity = tuple(range(12))
    group = {identity}
    gens = []
    for p in stabilizers:
        if tuple(p) not in group:
            gens.append(p)
            group = {identity}
            pending = [identity]
            for current in pending:
                for g in gens:
                    image = tuple(g[current[i]] for i in range(12))
                    if image not in group:
                        group.add(image)
                        pending.append(image)
    label_lookup = {lab:i for i,lab in enumerate(f.labels)}
    parents = list(range(1723))
    def find(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x
    for p in gens:
        q = [0,1]+[a+2 for a in p]
        action = [label_lookup[tuple(sorted(q[a] for a in lab))] for lab in f.labels]
        for x,y in combinations(range(84),2):
            a,b = f.edge(x,y),f.edge(action[x],action[y])
            if a is not False:
                parents[find(a)] = find(b)
    rows.append({'parts':parts,'stabilizer':len(stabilizers),'primary_orbits':len({find(i) for i in range(1,1723)}),'generators':len(gens)})
clauses = set()
for x,y,z in combinations(range(84),3):
    if not any(set(f.labels[a]) & set(f.labels[b]) for a,b in [(x,y),(x,z),(y,z)]):
        continue
    edges = [f.edge(x,y),f.edge(x,z),f.edge(y,z)]
    if any(e is False for e in edges):
        continue
    clauses.add(tuple(sorted(set(edges))))
report = {'scope':'Stabilizers and primary orbits recomputed; triangle count recomputed. No UP or solver benchmark.', 'rows':rows,'triangle_clauses':len(clauses),'triangle_lengths':{str(k):sum(len(c)==k for c in clauses) for k in (1,2,3)},'worker_comparison_cpu_hours':(11+22)*20/60,'trace_D3':20*3**3+15*(-4)**3,'trace_D4':20*3**4+15*4**4}
cnf.close()
Path('docs/symmetries_plan_20260919/checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
