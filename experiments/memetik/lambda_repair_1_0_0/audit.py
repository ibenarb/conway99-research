"""Read-only audit of all candidates, fixed edges, sources and wait4 accounting."""
import sys
from common import *
from verify import record, window_check, key


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
    for token in ledger['receipts']:
        receipt = read(run / 'receipts' / (token + '.json'))
        for label in ('best', 'result'):
            if receipt[label + '_sha256'] is not None:
                assert digest(run / 'receipts' / (token + '.' + label + '.json')) == receipt[label + '_sha256']
        totals[receipt['category']] += receipt['cpu_seconds']
        assert receipt['cpu_seconds'] <= receipt['allocation'] + 0.25
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
    return {'status': 'PASS', 'distinct_labelled_candidates': len(states), 'best_W': min((s['W'] for s in states.values()), default=None),
            'cpu_seconds': totals, 'total_cpu_hours': sum(totals.values()) / 3600,
            'host_wall_seconds': ledger['host_wall_seconds'],
            'scope': 'Full graph/score/fixed-edge and resource audit; no canonical classes or solver exclusion certificates.'}


if __name__ == '__main__':
    print(json.dumps(audit(sys.argv[1]), indent=2))
