"""Read-only recovery qualification for the frozen profile experiment."""
import hashlib
import json
import sqlite3
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(run):
    program = run / 'program'
    package = program / 'experiments/memetik/lambda_profile_1_0_0/PACKAGE.json'
    fingerprint = read(run / 'FINGERPRINT.json')
    assert digest(package) == fingerprint['package_sha256']
    for name, expected in read(package)['files'].items():
        assert digest(program / name) == expected, name
    ledger = read(run / 'ledger.json')
    assert not ledger['active'] and not (run / 'session_active.json').exists()
    result = read(run / 'RESULT.json')
    assert result['status'] == 'DIAGNOSIS_REQUIRED'
    assert result['error'] == "FileNotFoundError(2, 'No such file or directory')"
    assert result['cpu_seconds'] == ledger['used']
    assert result['host_wall_seconds'] == ledger['host_wall_seconds']
    log = (run / 'controller.log').read_text()
    assert 'self.disk_bytes = sum(p.stat().st_size' in log
    assert 'work.sqlite-journal' in log
    totals = {k: 0.0 for k in ledger['used']}
    cells = {}
    endpoints = {}
    for directory in sorted((run / 'jobs').iterdir()):
        receipt = read(directory / 'receipt.json')
        assert receipt['exit_code'] == 0
        for field, filename in [('task_sha256', 'task.json'), ('result_sha256', 'slice_result.json'), ('checkpoint_sha256', 'work.sqlite')]:
            if receipt[field] is not None:
                assert digest(directory / filename) == receipt[field], str(directory / filename)
        for session in receipt['sessions']:
            assert session['exit_code'] == 0 and 0 <= session['cpu_seconds'] <= session['allocation']
        assert abs(sum(s['cpu_seconds'] for s in receipt['sessions']) - receipt['cpu_seconds']) < 1e-7
        category = directory.name if directory.name in totals else 'aux'
        totals[category] += receipt['cpu_seconds']
        if not (directory / 'work.sqlite').exists():
            continue
        assert not list(directory.glob('work.sqlite-*'))
        db = sqlite3.connect((directory / 'work.sqlite').resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
        assert db.execute('PRAGMA integrity_check').fetchone() == ('ok',)
        metadata = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM meta')}
        task = read(directory / 'task.json')
        assert metadata['binding'] == hashlib.sha256(json.dumps(task, sort_keys=True).encode()).hexdigest()
        rows = [(i, json.loads(v)) for i, v in db.execute('SELECT idx,value FROM episodes ORDER BY idx')]
        progress = metadata['progress']
        assert [i for i, v in rows] == list(range(progress['next']))
        for i, v in rows:
            assert i == v['index'] and v['k'] == task['k'] and v['start_state'] == task['start']['state']
            seed = f"lambda-profile-v2|{task['start']['state']}|{task['k']}|{i}"
            assert v['seed'] == str(int.from_bytes(hashlib.sha256(seed.encode()).digest(), 'big'))
            assert v['state'] == hashlib.sha256(v['graph6'].encode()).hexdigest()
            if v['graph6'] in endpoints:
                assert endpoints[v['graph6']] == (v['scores'], v['class'])
            endpoints[v['graph6']] = (v['scores'], v['class'])
        if progress['episode'] is not None:
            assert progress['episode']['index'] == progress['next']
        cells[directory.name] = {'completed': len(rows), 'partial': progress['episode'] is not None,
                                'improved': sum(v['improved'] for i, v in rows)}
        db.close()
    totals['aux'] += sum(s['cpu_self'] + s['host_cpu'] for s in ledger['sessions'])
    totals['aux'] += sum(s['reserved_cpu'] for s in ledger['cli_reservations'])
    assert all(abs(totals[k] - ledger['used'][k]) < 0.001 for k in totals)
    assert len(cells) == 20
    return {'cells': cells, 'completed': sum(v['completed'] for v in cells.values()),
            'unique_endpoints': len(endpoints), 'cpu_seconds': totals,
            'host_wall_seconds': ledger['host_wall_seconds']}, endpoints


if __name__ == '__main__':
    import sys
    run = Path(sys.argv[1]).resolve()
    report, endpoints = audit(run)
    sys.path.insert(0, str(run / 'program/experiments/memetik/lambda_profile_1_0_0'))
    from support import checked, core
    for graph6, (scores, cls) in endpoints.items():
        rows, actual = checked(graph6, 'lambda')
        assert actual == scores and core.canonical(rows) == cls
    report['endpoint_score_class_recheck'] = 'PASS'
    print(json.dumps(report, indent=2))
