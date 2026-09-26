"""SQLite-free return audit. Does not replay the omitted radius computation."""
from pathlib import Path
import collections
import hashlib
import json
import sys
import zipfile
repo = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo / 'experiments/memetik/lambda_radius_1_0_0'))
import boot
from support import checked, core, witness, Guard
run, out = map(Path, sys.argv[1:])
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
folder = 'experiments/memetik/lambda_radius_1_0_0'
program = run / 'program'
package = load(program / folder / 'PACKAGE.json')
assert sha(program / folder / 'PACKAGE.json') == load(run / 'FINGERPRINT.json')['package_sha256']
with zipfile.ZipFile(repo / 'releases/memetik/lambda_radius_1_0_0.zip') as z:
    for name, expected in package['files'].items():
        assert sha(program / name) == expected, name
        assert (program / name).read_bytes() == z.read('lambda_radius_1_0_0/' + name), name
    assert (program / folder / 'PACKAGE.json').read_bytes() == z.read('lambda_radius_1_0_0/' + folder + '/PACKAGE.json')
starts = load(program / folder / 'STARTS.json')
for arm, item in starts.items():
    rows, scores = checked(item['graph6'], 'lambda')
    assert scores == item['scores'] and core.canonical(rows) == item['class']
    assert hashlib.sha256(item['graph6'].encode()).hexdigest() == item['state']
ledger, result = load(run / 'ledger.json'), load(run / 'RESULT.json')
assert load(run / 'status.json') == result
assert not ledger['active'] and not (run / 'session_active.json').exists()
assert result['status'] == 'FINISHED' and result['reason'] is None
jobs, used = {}, collections.defaultdict(float)
sessions, max_delta = 0, 0
for d in sorted((run / 'jobs').iterdir()):
    t, r, a = [load(d / n) for n in ('task.json', 'receipt.json', 'slice_result.json')]
    assert sha(d / 'task.json') == r['task_sha256'] and sha(d / 'slice_result.json') == r['result_sha256'], d
    assert r['exit_code'] == 0 and a['status'] == 'DONE', d
    assert abs(sum(s['cpu_seconds'] for s in r['sessions']) - r['cpu_seconds']) < 1e-6
    for s in r['sessions']:
        assert s['exit_code'] == 0 and 0 <= s['cpu_seconds'] <= s['allocation'], d
        assert s['cpu_seconds'] <= 1.02 * s['host_elapsed'] + 0.1, d
        sessions += 1
    used[t['arm'] if t.get('depth') == 4 else 'aux'] += r['cpu_seconds']
    max_delta = max(max_delta, abs(a['self_cpu'] - r['sessions'][-1]['cpu_seconds']))
    jobs[d.name] = t, r, a
assert all(not p.read_bytes() for p in (run / 'jobs').glob('*/worker.log'))
import xml.etree.ElementTree as ET
host_text = (run / 'host_stderr.log').read_text()
host_streams = collections.Counter()
if host_text:
    assert host_text.startswith('#< CLIXML')
    xml = ET.fromstring(host_text[host_text.index('<Objs'):])
    host_streams.update(x.attrib.get('S', 'UNCLASSIFIED') for x in xml)
    assert set(host_streams) == {'progress'}, dict(host_streams)
expected_names = {'clock_probe', 'controls', 'prepare_2076', 'prepare_2077', 'merge_2076', 'merge_2077'}
coverage = {}
for depth in (3, 4):
    manifest = load(run / f'DEPTH{depth}_MANIFEST.json')
    assert len({x[0] for x in manifest}) == len(manifest)
    expected_names.update(x[0] for x in manifest)
    for arm in ('2076', '2077'):
        selected = sorted((x for x in manifest if x[1]['arm'] == arm), key=lambda x: x[1]['lo'])
        parent = ('prepare_' if depth == 3 else 'merge_') + arm
        filename = 'lower.sqlite' if depth == 3 else 'layers.sqlite'
        low, high, count = jobs[parent][2]['bounds']
        assert high - low + 1 == count
        cursor, children, parents = low, 0, 0
        for name, t, category in selected:
            assert t == jobs[name][0] and t['start'] == starts[arm]
            assert category == ('aux' if depth == 3 else arm)
            assert t['depth'] == depth and t['kind'] == 'expand'
            assert t['lo'] == cursor and t['hi'] >= t['lo']
            assert t['input_sha256'] == jobs[parent][1]['output_sha256'][filename]
            assert t['input'].endswith('/jobs/' + parent + '/' + filename)
            a = jobs[name][2]
            assert a['last'] == t['hi'] and a['parents'] == t['hi'] - t['lo'] + 1 and a['witness'] is None
            cursor = t['hi'] + 1
            parents += a['parents']
            children += a['children']
        assert cursor == high + 1 and parents == count
        coverage[f'depth{depth}_{arm}'] = dict(jobs=len(selected), parents=parents, children=children, contiguous_intervals=True)
        if depth == 3:
            gate = load(run / 'DEPTH3_VERIFIED.json')[arm]
            assert (parents, children) == ((5222, 526476) if arm == '2076' else (4768, 459185))
            assert gate['parents'] == parents and gate['children'] == children and gate['improving'] == 0
        else:
            final = result['arms'][arm]
            assert final['status'] == 'COMPLETE_NO_IMPROVEMENT_DEPTH4'
            assert final['parents_completed'] == parents and final['children_evaluated_in_completed_jobs'] == children
            assert final['jobs_total'] == final['jobs_completed'] == len(selected)
            assert final['start_state'] == starts[arm]['state'] and not final['witnesses']
assert set(jobs) == expected_names
for arm in ('2076', '2077'):
    sources = jobs['merge_' + arm][0]['sources']
    expected = {'prepare_' + arm} | {n for n, t, _ in load(run / 'DEPTH3_MANIFEST.json') if t['arm'] == arm}
    actual = set()
    for name, digest in sources:
        n = Path(name).parent.name
        actual.add(n)
        assert n in expected
        r = jobs[n][1]
        assert digest == (r['output_sha256']['lower.sqlite'] if n.startswith('prepare_') else r['checkpoint_sha256'])
    assert actual == expected and len(sources) == len(expected)
    assert abs(used[arm] - ledger['used'][arm]) < 1e-6 and used[arm] <= 72000
aux = used['aux'] + sum(x['reserved_cpu'] for x in ledger['cli_reservations'])
aux += sum(x['cpu_self'] + x['host_cpu'] for x in ledger['sessions'])
delta = ledger['used']['aux'] - aux
assert abs(delta) < 0.01 and ledger['used']['aux'] <= 7200
assert result['cpu_seconds'] == ledger['used']
assert result['host_wall_seconds'] == ledger['host_wall_seconds'] < 28800
assert abs(sum(x['host_wall'] for x in ledger['sessions']) - ledger['host_wall_seconds']) < 1e-6
control = jobs['controls'][2]
assert control['control_status'] == 'CONTROLS_PASS'
p = control['positive_depth4_witness']
assert json.loads(json.dumps(witness(starts['2079'], [x['move'] for x in p['steps']], Guard()))) == p
assert p['state'] == starts['2076']['state'] and len(p['steps']) == 4
summary = {'status': 'METADATA_SOURCE_ACCOUNTING_AND_CONTROL_REPLAY_PASS',
           'source_files_verified': len(package['files']), 'jobs_verified': len(jobs), 'worker_sessions': sessions,
           'coverage': coverage, 'cpu_hours': {k: v / 3600 for k, v in ledger['used'].items()},
           'total_accounted_cpu_hours': sum(ledger['used'].values()) / 3600,
           'wall_seconds': ledger['host_wall_seconds'], 'aux_sum_difference_seconds': delta,
           'max_self_vs_wait4_difference_seconds': max_delta,
           'start_scores_and_classes_verified': 3, 'positive_four_move_witness_replayed': True,
           'host_stderr_streams': dict(host_streams),
           'sqlite_files_in_return': len(list(run.rglob('*.sqlite*'))),
           'limits': ['SQLite databases omitted: actual hashes and contents not checked.',
                      'No independent replay of 36,281,544 depth-4 child evaluations.',
                      'Intervals checked against reported layer bounds, not against absent layer contents.',
                      'CPU receipts internally checked; host counters not independently remeasured.']}
assert summary['sqlite_files_in_return'] == 0
out.write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
