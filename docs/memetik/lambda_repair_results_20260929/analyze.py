"""Reproduce comparison and Maple exports. Usage: audit-python analyze.py RUN120 RUN110 OUT."""
import collections
import hashlib
import json
import pathlib
import sys
import pynauty

run, old, out = map(pathlib.Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(run / 'program'))
from verify import decode, record
from audit import audit


def read(path):
    return json.loads(path.read_text())


def write(name, obj):
    (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def certificate(value):
    rows = decode(value['graph6'])
    return pynauty.certificate(pynauty.Graph(len(rows), adjacency_dict={i: list(row) for i, row in enumerate(rows)}))


a, b = read(run / 'RESULT.json'), read(old / 'RESULT.json')
m, previous = read(run / 'program/MANIFEST.json'), read(old / 'program/MANIFEST.json')
assert m['founders'] == previous['founders']
assert [{k: v for k, v in t.items() if k != 'cpu_limit_seconds'} for t in m['tasks']] == [{k: v for k, v in t.items() if k != 'cpu_limit_seconds'} for t in previous['tasks']]
tasks = {t['id']: t for t in m['tasks']}
roots = {g['id']: g for g in m['founders']}
assert set(a['done']) == set(tasks) and len(tasks) == 144
result = audit(run)
write('REPRODUCED_AUDIT.json', result)
unique = {v['state']: v for v in a['bests'].values()}
values = sorted(unique.values(), key=lambda v: (v['scores']['W'], v['scores']['L1'], v['state']))
for v in values:
    assert record(v['graph6']) == {k: v[k] for k in ('graph6', 'state', 'scores')}
pareto = [v for v in values if not any(u['scores']['W'] <= v['scores']['W'] and u['scores']['L1'] <= v['scores']['L1'] and (u['scores']['W'], u['scores']['L1']) != (v['scores']['W'], v['scores']['L1']) for u in values)]
new_classes = {certificate(v) for v in values}
old_classes = {certificate(v) for v in b['bests'].values()}
root_classes = {certificate(v) for v in roots.values()}
summary = {
    'status': 'PASS', 'same_founders_and_tasks_except_cpu_budget': True,
    'done_counts': dict(collections.Counter(a['done'].values())),
    'by_window': {str(s): dict(collections.Counter(v for k, v in a['done'].items() if '_s' + str(s) + '_' in k)) for s in (24, 40, 60)},
    'classes': len(new_classes), 'founder_classes': len(root_classes),
    'new_classes_vs_110': len(new_classes - old_classes),
    'new_classes_vs_founders': len(new_classes - root_classes),
    'status_changes': [{'task': k, 'old': b['done'][k], 'new': v} for k, v in a['done'].items() if v != b['done'][k]],
    'improvements': [{'task': k, 'before': roots[tasks[k]['founder']]['scores'], 'after': v['scores'], 'state': v['state']} for k, v in a['bests'].items() if v['scores'] != roots[tasks[k]['founder']]['scores']],
    'pareto': [{'state': v['state'], 'scores': v['scores']} for v in pareto],
    'campaign_cpu_hours': sum(a['cpu_seconds'].values()) / 3600,
    'export_ledger_cpu_hours': result['total_cpu_hours'],
    'host_wall_seconds': a['host_wall_seconds'],
    'scope': 'Local window results only; CP-SAT optimality is uncertified; timeouts remain unknown.'
}
write('SUMMARY.json', summary)
write('CANDIDATES_25.json', values)
for name, selected in [('Beste_Kandidaten_Maple.txt', pareto), ('Alle_25_Kandidaten_Maple.txt', values)]:
    lines = ['# Conway99 lambda repair 1.2.0; rows/columns 1..99; undirected adjacency matrices.', '# Best means Pareto-minimal in (W,L1); sorted lexicographically. Full export contains all 25 classes.' if len(selected) == 2 else '# All 25 classes, sorted by (W,L1,state).', '# L1 is the sum of absolute nonedge common-neighbor deviations from 2.']
    for i, v in enumerate(selected, 1):
        rows = decode(v['graph6'])
        matrix = '<' + ';'.join(','.join(str(int(j in rows[k])) for j in range(99)) for k in range(99)) + '>'
        parsed = [[int(x) for x in row.split(',')] for row in matrix[1:-1].split(';')]
        assert len(parsed) == 99 and all(len(row) == 99 and sum(row) == 14 for row in parsed)
        assert all(parsed[k][j] == int(j in rows[k]) for k in range(99) for j in range(99))
        lines += [f"# Candidate {i}; W={v['scores']['W']}; L1={v['scores']['L1']}; graph6 SHA256={v['state']}", f'A{i} := {matrix}:']
    (out / name).write_text('\n'.join(lines) + '\n')
print(json.dumps(summary, indent=2))
