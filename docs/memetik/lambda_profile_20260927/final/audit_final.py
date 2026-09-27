"""Read-only final audit. Arguments: recovered run, original run. Uses isolated audit Python."""
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
    assert result['status'] == 'INCOMPLETE'
    assert result['cpu_seconds'] == ledger['used']
    assert result['host_wall_seconds'] == ledger['host_wall_seconds']
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
    run, old = [Path(p).resolve() for p in sys.argv[1:3]]
    report, endpoints = audit(run)
    repo = Path(__file__).resolve().parents[4]
    assert digest(run / 'recovery/MANIFEST.json') == digest(repo / 'experiments/memetik/lambda_profile_recovery_1_0_1/MANIFEST.json')
    assert read(run / 'FINGERPRINT.json') == read(old / 'FINGERPRINT.json')
    for name, expected in read(run / 'recovery/MANIFEST.json').items():
        assert digest(run / 'recovery' / name) == expected
    assert digest(run / 'recovery/MANIFEST.json') == read(run / 'RECOVERY.json')['recovery_manifest_sha256']
    sys.path.insert(0, str(run / 'program/experiments/memetik/lambda_profile_1_0_0'))
    from support import checked, core
    from episodes import seed_for
    for graph6, (scores, cls) in endpoints.items():
        rows, actual = checked(graph6, 'lambda')
        assert actual == scores and core.canonical(rows) == cls
    profile = read(run / 'PROFILE.json')
    assert profile == read(run / 'RESULT.json')['cells']
    allclasses = set()
    near = {}
    intermediate = 0
    preserved = 0
    totals = {'n': 0, 'returned': 0, 'improved': 0}
    table = []
    for name in sorted(profile):
        d = run / 'jobs' / name
        db = sqlite3.connect((d / 'work.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
        records = db.execute('SELECT idx,value FROM episodes ORDER BY idx').fetchall()
        values = [json.loads(v) for i,v in records]
        olddb = sqlite3.connect((old / 'jobs' / name / 'work.sqlite').as_uri() + '?mode=ro&immutable=1', uri=True)
        previous = olddb.execute('SELECT idx,value FROM episodes ORDER BY idx').fetchall()
        assert records[:len(previous)] == previous
        preserved += len(previous)
        olddb.close()
        assert [json.loads(line) for line in (d / 'episodes.jsonl').read_text().splitlines()] == values
        task = read(d / 'task.json')
        assert task == read(old / 'jobs' / name / 'task.json')
        s = profile[name]
        assert s['completed'] == len(values)
        assert s['returned'] == sum(v['returned'] for v in values)
        assert s['improved'] == sum(v['improved'] for v in values)
        assert s['end_classes'] == len({v['class'] for v in values})
        assert s['best_endpoint'] == min((v['scores'] for v in values), key=lambda x:(x['W'],x['L1']))
        assert s['charged_cpu_seconds'] == read(run / 'ledger.json')['used'][name]
        for v in values:
            assert v['returned'] == (v['graph6'] == task['start']['graph6'])
            assert v['isomorphic_return'] == (v['class'] == task['start']['class'])
            assert v['improved'] == ((v['scores']['W'],v['scores']['L1']) < (task['start']['scores']['W'],task['start']['scores']['L1']))
            assert v['global_W_record'] == (v['scores']['W'] < 2076)
            assert v['actual_k'] == task['k'] and v['stop'] == 'LOCAL_MIN_EXACT_AP'
            assert len(v['path']) == v['actual_k'] + v['descent_length']
            assert v['intermediate_better'] == [i+1 for i,p in enumerate(v['path']) if (p['scores']['W'],p['scores']['L1']) < (task['start']['scores']['W'],task['start']['scores']['L1'])]
            allclasses.add(v['class'])
            intermediate += len(v['intermediate_better'])
            if not v['isomorphic_return'] and v['scores']['W'] <= task['start']['scores']['W']+2:
                near.setdefault(v['class'],{'scores':v['scores'],'state':v['state'],'graph6':v['graph6'],'observations':[]})['observations'].append([name,v['index']])
        for field in totals:
            totals[field] += len(values) if field=='n' else s[field]
        table.append({'cell':name,'n':len(values),'returned':s['returned'],'return_percent':100*s['returned']/len(values),
                      'classes':s['end_classes'],'cpu_per_episode':s['cpu_per_completed_episode']})
        db.close()
    report.update(endpoint_score_class_recheck='PASS', original_episodes_byte_preserved=preserved,
                  unique_classes=len(allclasses), totals=totals, table=table, near_other_classes=near,
                  intermediate_improvements=intermediate,
                  total_cpu_hours=sum(report['cpu_seconds'].values())/3600,
                  search_cpu_hours=sum(v for k,v in report['cpu_seconds'].items() if k!='aux')/3600)
    print(json.dumps(report, indent=2))
