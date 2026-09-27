"""Sound binary propagation of necessary boundary conditions; no search."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent', HERE.parent / 'lambda_profile_20260927/endpoints/reproduce.py')
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)
manifest = json.loads((HERE / 'MANIFEST.json').read_text())
founders = {g['id']: independent.decode(g['graph6']) for g in manifest['founders']}
results = []
for task in manifest['tasks']:
    rows = founders[task['founder']]
    inside = task['vertices']
    mask = sum(1 << v for v in inside)
    outside = [v for v in range(99) if v not in inside]
    outer_mask = ((1 << 99) - 1) ^ mask
    pairs = [(u, v) for v in inside for u in inside if u < v]
    indices = {p: i for i, p in enumerate(pairs)}
    values = [None] * len(pairs)
    def variable(u, v):
        return indices[tuple(sorted((u, v)))]
    constraints = []
    for i, (u, v) in enumerate(pairs):
        if (rows[u] & rows[v] & outer_mask).bit_count() > 1:
            values[i] = 0
    for u in inside:
        constraints.append(([variable(u, v) for v in inside if v != u], (rows[u] & mask).bit_count()))
        for o in outside:
            if (rows[u] >> o) & 1:
                constraints.append(([variable(u, v) for v in inside if v != u and (rows[o] >> v) & 1],
                                    1 - (rows[u] & rows[o] & outer_mask).bit_count()))
    changed = True
    while changed:
        changed = False
        for variables, rhs in constraints:
            remaining = rhs - sum(values[i] for i in variables if values[i] is not None)
            free = [i for i in variables if values[i] is None]
            assert 0 <= remaining <= len(free)
            if free and remaining in (0, len(free)):
                for i in free:
                    values[i] = int(remaining != 0)
                changed = True
    assert all(value is None or value == ((rows[u] >> v) & 1) for (u, v), value in zip(pairs, values))
    results.append({'id': task['id'], 'size': task['size'], 'rule': task['rule'],
                    'variables': len(pairs), 'unfixed_after_necessary_propagation': values.count(None),
                    'proved_rigid_by_propagation': None not in values})
output = {'status': 'PASS', 'note': 'Necessary conditions only. Unfixed variables do not prove that any alternative feasible graph exists.', 'tasks': results}
(HERE / 'BOUNDARY_CHECK.json').write_text(json.dumps(output, indent=2) + '\n')
for size in (24, 40, 60):
    subset = [r for r in results if r['size'] == size]
    counts = sorted(r['unfixed_after_necessary_propagation'] for r in subset)
    print(json.dumps({'size': size, 'tasks': len(subset), 'rigid': sum(r['proved_rigid_by_propagation'] for r in subset),
                      'unfixed_min': min(counts), 'unfixed_median': (counts[23]+counts[24])/2, 'unfixed_max': max(counts)}))
