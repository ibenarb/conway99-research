"""Read-only audit of all candidates, fixed edges, sources and wait4 accounting."""
import sys
from common import *
from verify import record, key
from validation import validate_best


def premature_tasks(done, tasks, totals, minimum):
    return [t for t, status in done.items() if status == 'CPU_LIMIT_UNKNOWN' and tasks[t]['cpu_limit_seconds'] - totals[t] >= minimum]


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
    policy = read(run / 'program/BUDGET_POLICY.json')
    totals = {name: 0.0 for name in ledger['used']}
    deviations = []
    assert len(ledger['receipts']) == len(set(ledger['receipts']))
    for token in ledger['receipts']:
        receipt = read(run / 'receipts' / (token + '.json'))
        assert not receipt.get('integrity_error'), 'Quarantined invalid result'
        for label in ('best', 'result'):
            if receipt[label + '_sha256'] is not None:
                assert digest(run / 'receipts' / (token + '.' + label + '.json')) == receipt[label + '_sha256']
        totals[receipt['category']] += receipt['cpu_seconds']
        assert receipt['cpu_seconds'] >= 0
        if receipt['cpu_seconds'] > receipt['soft_target_cpu_seconds'] + 0.25:
            deviations.append({'receipt': token, 'category': receipt['category'], 'cpu_seconds': receipt['cpu_seconds'], 'soft_target_cpu_seconds': receipt['soft_target_cpu_seconds'], 'allocation': receipt['allocation']})
        if receipt['cpu_seconds'] > receipt['allocation'] + policy['receipt_measurement_tolerance_seconds']:
            assert token in ledger.get('local_hard_overruns', []), 'Unrecorded hard overrun'
        if receipt['category'] != 'aux' and receipt['best_sha256'] is not None:
            saved = read(run / 'receipts' / (token + '.best.json'))
            t = tasks[receipt['category']]
            validate_best(saved, roots[t['founder']], t)
    totals['aux'] += sum(s['controller_cpu_seconds'] + s['host_helper_cpu_seconds'] + s['finalization_cpu_reserved'] for s in ledger['sessions'])
    totals['aux'] += sum(x['cpu_seconds'] for x in ledger['cli_reservations'])
    assert all(abs(totals[k] - ledger['used'][k]) < 1e-6 for k in totals)
    assert abs(sum(s['host_wall_seconds'] for s in ledger['sessions']) - ledger['host_wall_seconds']) < 1e-6
    assert totals['aux'] <= policy['aux_cpu_limit_seconds'] + 0.001
    assert sum(totals.values()) <= policy['total_cpu_limit_seconds'] + 0.001
    for t in tasks:
        if totals[t] > tasks[t]['cpu_limit_seconds'] + policy['task_shutdown_grace_cpu_seconds'] + policy['task_measurement_tolerance_seconds']:
            assert ledger['done'].get(t) == 'LOCAL_HARD_LIMIT_UNKNOWN'
    premature = premature_tasks(ledger['done'], tasks, totals, policy['minimum_search_attempt_seconds'])
    assert not premature, 'PREMATURE_TASK_COMPLETION: ' + ', '.join(premature)
    states = {}
    for path in sorted((run / 'jobs').glob('*/*.json')):
        if path.name != 'best.json' and not path.name.startswith('candidate_'):
            continue
        task = tasks[path.parent.name]
        founder = roots[task['founder']]
        value = read(path)
        validate_best(value, founder, task)
        states[value['state']] = value['scores']
    # Secondary lambda incumbents from packing experiments remain a separate pool.
    for path in (run / 'jobs').glob('*/lambda_best.json'):
        value = read(path); actual = record(value['graph6'])
        assert actual['state'] == value['state']
        assert all(actual['scores'][k] == value['scores'][k] for k in ('W', 'L1'))
    for path in (run / 'jobs').glob('*/catalog_archive.json'):
        for value in read(path):
            actual = record(value['graph6'])
            assert actual['state'] == value['state'] and actual['scores'] == value['scores']
    for path in (run / 'jobs').glob('*/task.json'):
        assert read(path) == tasks[path.parent.name]
    result = {'status': 'PASS_WITH_RECORDED_LOCAL_DEVIATIONS' if deviations else 'PASS', 'soft_target_deviations': deviations, 'local_hard_overruns': ledger.get('local_hard_overruns', []), 'distinct_labelled_candidates': len(states), 'best_W': min((s['W'] for s in states.values() if 'W' in s), default=None), 'best_packing_edges': max((s['edges'] for s in states.values() if 'edges' in s), default=None),
            'cpu_seconds': totals, 'total_cpu_hours': sum(totals.values()) / 3600,
            'host_wall_seconds': ledger['host_wall_seconds'],
            'scope': 'Full graph/score/fixed-edge and resource audit; no canonical classes or solver exclusion certificates.'}

    from recovery import summary
    return summary(run, result)


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1]), indent=2))
