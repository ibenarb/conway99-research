"""Read-only audit of all candidates, fixed edges, sources and wait4 accounting."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "experiments/memetik/lambda_repair_1_0_0"))
from common import *
from verify import record, window_check, key
from recovery_policy import historical_overrun


def audit(run):
    run = Path(run)
    fingerprint = read(run / 'FINGERPRINT.json')
    assert digest(run / 'program/PACKAGE.json') == fingerprint['package_sha256']
    for name, expected in read(run / 'program/PACKAGE.json')['files'].items():
        assert digest(run / 'program' / name) == expected
    manifest = read(run / 'program/MANIFEST.json')
    roots = {g['id']: g for g in manifest['founders']}
    tasks = {t['id']: t for t in manifest['tasks']}
    ledger = read(run / 'ledger.json')
    assert not ledger['active'] and not (run / 'session_active.json').exists()
    totals = {name: 0.0 for name in ledger['used']}
    historical_deviations = []
    assert len(ledger['receipts']) == len(set(ledger['receipts']))
    for token in ledger['receipts']:
        receipt = read(run / 'receipts' / (token + '.json'))
        for label in ('best', 'result'):
            if receipt[label + '_sha256'] is not None:
                assert digest(run / 'receipts' / (token + '.' + label + '.json')) == receipt[label + '_sha256']
        totals[receipt['category']] += receipt['cpu_seconds']
        if receipt['cpu_seconds'] > receipt['allocation'] + 0.25:
            assert historical_overrun(run, token, receipt), 'Unrecognized CPU overrun'
            historical_deviations.append({'receipt': token, 'excess_seconds': receipt['cpu_seconds'] - receipt['allocation'], 'sha256': digest(run / 'receipts' / (token + '.json'))})
        if receipt['best_sha256'] is not None and receipt['category'] != 'aux':
            saved = read(run / 'receipts' / (token + '.best.json'))
            task = tasks[receipt['category']]
            assert record(saved['graph6'])['state'] == saved['state']
            assert window_check(saved['graph6'], roots[task['founder']]['graph6'], task['vertices']) == saved['scores']
            assert key(saved['scores']) <= key(roots[task['founder']]['scores'])
    totals['aux'] += sum(s['controller_cpu_seconds'] + s['host_helper_cpu_seconds'] + s['finalization_cpu_reserved'] for s in ledger['sessions'])
    totals['aux'] += sum(x['cpu_seconds'] for x in ledger['cli_reservations'])
    assert all(abs(totals[k] - ledger['used'][k]) < 1e-6 for k in totals)
    assert abs(sum(s['host_wall_seconds'] for s in ledger['sessions']) - ledger['host_wall_seconds']) < 1e-6
    assert totals['aux'] <= 43200.25 and sum(totals.values()) <= 561600.25
    assert all(totals[t] <= tasks[t]['cpu_limit_seconds'] + 0.25 for t in tasks)
    states = {}
    for path in sorted((run / 'jobs').glob('*/*.json')):
        if path.name != 'best.json' and not path.name.startswith('candidate_'):
            continue
        task = tasks[path.parent.name]
        founder = roots[task['founder']]
        value = read(path)
        actual = record(value['graph6'])
        assert actual['state'] == value['state'] and actual['scores'] == value['scores']
        assert window_check(value['graph6'], founder['graph6'], task['vertices']) == value['scores']
        assert key(value['scores']) <= key(founder['scores'])
        states[value['state']] = value['scores']
    for path in (run / 'jobs').glob('*/task.json'):
        assert read(path) == tasks[path.parent.name]
    return {'status': 'PASS_WITH_DOCUMENTED_HISTORICAL_DEVIATION' if historical_deviations else 'PASS', 'historical_cpu_deviations': historical_deviations, 'distinct_labelled_candidates': len(states), 'best_W': min((s['W'] for s in states.values()), default=None),
            'cpu_seconds': totals, 'total_cpu_hours': sum(totals.values()) / 3600,
            'host_wall_seconds': ledger['host_wall_seconds'],
            'scope': 'Full graph/score/fixed-edge and resource audit; no canonical classes or solver exclusion certificates.'}


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1]), indent=2))
