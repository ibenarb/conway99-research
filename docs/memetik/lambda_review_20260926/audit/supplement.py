"""Read-only audit of the fixed flat package; no new search."""
import collections
import hashlib
import json
from pathlib import Path
import sys
import pynauty

root = Path(sys.argv[1])
records = {}
occurrences = 0
mismatches = []

def certificate(g6):
    v = [ord(c) - 63 for c in g6]
    n = (v[1] << 12) + (v[2] << 6) + v[3]
    bits = [(x >> k) & 1 for x in v[4:] for k in range(5, -1, -1)]
    adj = {i: [] for i in range(n)}
    t = 0
    for j in range(n):
        for i in range(j):
            if bits[t]:
                adj[i].append(j)
                adj[j].append(i)
            t += 1
    g = pynauty.Graph(n, adjacency_dict=adj)
    return hashlib.sha256(pynauty.certificate(g)).hexdigest(), adj, g

def visit(obj, source):
    global occurrences
    if isinstance(obj, dict):
        if 'graph6' in obj and 'scores' in obj:
            g6 = obj['graph6']
            if g6 not in records:
                c, adj, g = certificate(g6)
                records[g6] = dict(scores=obj['scores'], state=hashlib.sha256(g6.encode()).hexdigest(), iso=c, sources=[])
            records[g6]['sources'].append(source)
            if 'class' in obj:
                occurrences += 1
                if obj['class'] != records[g6]['iso']:
                    mismatches.append(dict(source=source, state=records[g6]['state'], declared=obj['class'], actual=records[g6]['iso']))
        for x in obj.values():
            visit(x, source)
    elif isinstance(obj, list):
        for x in obj:
            visit(x, source)

for p in sorted(root.glob('*__result.json')) + sorted(root.glob('*__task.json')):
    visit(json.loads(p.read_text()), p.name)
points = sorted({(x['scores']['W'], x['scores']['F']) for x in records.values()})
front = []
fmin = float('inf')
for w, f in points:
    if f < fmin:
        front.append((w, f))
        fmin = f
pareto = [dict(W=w, F=f, graphs=[{k: x[k] for k in ('state', 'iso', 'scores')} for x in records.values() if (x['scores']['W'], x['scores']['F']) == (w, f)]) for w, f in front]
curves = []
for p in sorted(root.glob('O*__result.json')):
    r = json.loads(p.read_text())
    for x in r['curves']:
        curves.append(dict(job=p.name, cpu=x['cpu'], **records[x['graph6']]))
early = {x['iso'] for x in curves if x['cpu'] <= 14400}
late = [dict(job=x['job'], cpu=x['cpu'], scores=x['scores'], iso=x['iso'], new_vs_early_best_curves=x['iso'] not in early) for x in curves if x['cpu'] > 14400]
structures = {}
for w in (2076, 2077):
    wanted = {2076: '8169eba8e1f2bf78eb655d99b94844a1eb5056df828e8c610a3778d537a7d0fe', 2077: '136bad89e063ba84bbc4201cfa5be21db6d511852602ad861a4d2c0e0ef8e49c'}[w]
    g6 = next(g for g, x in records.items() if x['state'] == wanted)
    c, adj, g = certificate(g6)
    neighbors = {i: set(v) for i, v in adj.items()}
    h = collections.Counter()
    loads = [0] * 99
    for u in range(99):
        for v in range(u + 1, 99):
            if v not in neighbors[u]:
                r = len(neighbors[u] & neighbors[v]) - 2
                h[r] += 1
                loads[u] += abs(r)
                loads[v] += abs(r)
    _, mantissa, exponent, _, orbits = pynauty.autgrp(g)
    structures[w] = dict(state=records[g6]['state'], residual_histogram=dict(sorted(h.items())), automorphism_order=mantissa * 10 ** exponent, vertex_orbits=orbits, vertex_L1_min=min(loads), vertex_L1_max=max(loads), vertex_L1_sum=sum(loads))
manifest = json.loads((root / 'MANIFEST.json').read_text())
result = dict(unique_labelled_graphs=len(records), distinct_classes=len({x['iso'] for x in records.values()}), full_class_fields_checked=occurrences, class_mismatches=mismatches, pareto_W_F=pareto, late_best_curve_events=late, structures=structures, manifest_entries=len(manifest), previous_check_result_in_manifest='05_CHECK_RESULT.json' in manifest)
Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'pareto_W_F'}, indent=2))
print('PARETO_POINTS', front)
