"""Freeze existing founders and windows. No solver and no graph search.

Run with tools/memetik/audit_python.py -- this_script FINAL_PROFILE_DIRECTORY.
Writes MANIFEST.json beside this script. Requires the audited final profile.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent', HERE.parent / 'lambda_profile_20260927/endpoints/reproduce.py')
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)
run = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(run / 'program/experiments/memetik/lambda_profile_1_0_0'))
from support import core


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def key(g):
    return g['scores']['W'], g['scores']['L1'], g['state']


def features(rows):
    defects = [0] * 99
    hist = [0] * 15
    for v in range(99):
        for u in range(v):
            if (rows[u] >> v) & 1:
                continue
            common = (rows[u] & rows[v]).bit_count()
            hist[common] += 1
            if common != 2:
                defects[u] += 1
                defects[v] += 1
    return defects, [42 * x for x in sorted(defects)] + hist


pools = {'2076': {}, '2077': {}}
roots = {}
for path in sorted((run / 'jobs').glob('*_k*/episodes.jsonl')):
    task = json.loads((path.parent / 'task.json').read_text())
    arm = task['arm']
    roots[arm] = task['start']
    values = [task['start']] + [json.loads(line) for line in path.read_text().splitlines()]
    for value in values:
        g = {k: value[k] for k in ('graph6', 'state', 'class', 'scores')}
        if g['scores']['W'] > task['start']['scores']['W'] + 100:
            continue
        old = pools[arm].get(g['class'])
        if old is None or key(g) < key(old):
            pools[arm][g['class']] = g

selected = []
used = set()
cache = {}
for arm in ('2076', '2077'):
    candidates = sorted((g for g in pools[arm].values() if g['class'] not in used), key=key)
    assert len(candidates) >= 12
    arm_selected = []
    for g in candidates:
        rows = independent.decode(g['graph6'])
        cache[g['state']] = (rows, features(rows))
    for index in range(12):
        remaining = [g for g in candidates if g['class'] not in used]
        if index < 6:
            g = remaining[0]
            selection = 'best_W_L1_state'
        else:
            def separation(g):
                f = cache[g['state']][1][1]
                return min(sum(abs(x-y) for x, y in zip(f, cache[h['state']][1][1])) for h in arm_selected)
            g = min(remaining, key=lambda g: (-separation(g), *key(g)))
            selection = 'maximin_invariant_feature_L1'
        rows = cache[g['state']][0]
        assert independent.score(rows) == g['scores']
        assert digest(g['graph6']) == g['state']
        assert core.canonical(tuple(rows)) == g['class']
        used.add(g['class'])
        arm_selected.append(g)
        selected.append({**g, 'id': f'{arm}_{index+1:02d}', 'origin': arm, 'selection': selection})
    assert any(g['state'] == roots[arm]['state'] for g in arm_selected)

tasks = []
for g in selected:
    rows, (defects, _) = cache[g['state']]
    seen = set()
    for size in (24, 40, 60):
        seed = f'lambda-repair-pilot-v2|{g["state"]}|{size}'
        for rule in ('defect', 'random'):
            # Hash rankings avoid dependence on random-library versions.
            def ranking(v, step):
                return digest(f'{seed}|{step}|{v}')
            initial = min(range(99), key=lambda v: ((-defects[v],) if rule == 'defect' else ()) + (ranking(v, 0), v))
            window = {initial}
            while len(window) < size:
                frontier = [v for v in range(99) if v not in window and any((rows[v] >> u) & 1 for u in window)]
                assert frontier
                v = min(frontier, key=lambda v: ((-defects[v],) if rule == 'defect' else ()) + (ranking(v, len(window)), v))
                window.add(v)
            vertices = sorted(window)
            assert tuple(vertices) not in seen
            seen.add(tuple(vertices))
            tasks.append({'id': f'{g["id"]}_s{size}_{rule}', 'founder': g['id'], 'size': size, 'rule': rule,
                          'seed_text': seed, 'vertices': vertices, 'cpu_limit_seconds': 3600})

assert len(selected) == len(used) == 24 and len(tasks) == 144
output = {'version': 2, 'status': 'PREPARED_NOT_EXECUTED',
          'source_archive_sha256': 'ccdb709a98ab0e5f32794807955026e1fe2819364de668f9eb3c37fe4854c2f3',
          'source_result': json.loads((run / 'RESULT.json').read_text()),
          'eligible_classes_by_origin': {a: len(p) for a, p in pools.items()},
          'selection_note': 'A then B, globally deduplicated; six best plus six maximin per origin. Features are descriptive, not basin distances.',
          'founders': selected, 'tasks': tasks,
          'aux_cpu_limit_seconds': 43200, 'total_cpu_limit_seconds': 561600,
          'active_host_wall_limit_seconds': 86400}
(HERE / 'MANIFEST.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': 'PASS', 'founders': len(selected), 'tasks': len(tasks),
                  'eligible_classes': output['eligible_classes_by_origin'],
                  'scores': {a: [g['scores']['W'] for g in selected if g['origin'] == a] for a in pools}}))
