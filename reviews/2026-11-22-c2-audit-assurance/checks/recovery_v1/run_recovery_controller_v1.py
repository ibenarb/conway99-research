"""Versioned continuation; preserves completed evidence and adopts two live jobs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

REC = Path(__file__).resolve().parent
BASE = REC.parent
sys.path.insert(0, str(REC))
from resource_observer_v1 import measure, live
from c2_serial_admission_core_20261118_v1 import identity


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value, exclusive=False):
    if exclusive:
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=4)
        return
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes((json.dumps(value, indent=4) + '\n').encode('utf-8'))
    temporary.replace(path)


def admissible(resource, active_count, warmups, family_count, family_limit):
    return (active_count < 20 and active_count + 1 <= resource['c2_worker_budget']
            and family_count < family_limit
            and max(r['system_busy_cpu'] for r in resource['intervals']) + warmups + 1 <= 20
            and resource['ram_free_gib'] >= 10 + 2 * (warmups + 1)
            and resource['disk_free_gib'] >= 35.4 + 0.1 * warmups)


def valid_result(family, job, folder, expected):
    result_path = folder / 'result.json'
    if not result_path.exists():
        return False, 'MISSING_RESULT_NOT_EXCLUSION'
    result = read(result_path)
    if result.get('status') != expected:
        return False, result.get('status', 'INVALID_RESULT_NOT_EXCLUSION')
    if family == 'high':
        assert result['job'] == job and result['open'] == 0 and result['stars'] == result['closed']
    elif family == 'low':
        assert result['chart'] == job['chart'] and result['packet_parity'] == job['packet_parity']
        assert result['stars'] == job['stars'] and result['open'] == 0 and result['stars'] == result['closed']
        assert result['viable_planes'] == result['closed_planes']
    else:
        assert result['chart'] == job['chart'] and result['roots_completed'] == result['roots_planned']
        assert result['exit_code'] == 0
    hashes = result.get('hashes', result.get('evidence_hashes', result.get('output_hashes', {})))
    assert hashes
    for name, digest in hashes.items():
        assert sha(folder / name) == digest, (family, job['id'], name)
    return True, result['status']


def controls():
    sample = dict(c2_worker_budget=18, intervals=[dict(system_busy_cpu=3), dict(system_busy_cpu=4)],
                  ram_free_gib=32, disk_free_gib=40)
    assert admissible(sample, 10, 0, 0, 4), 'No fixed total-worker ceiling of ten'
    assert not admissible(dict(sample, c2_worker_budget=10), 10, 0, 0, 4)
    assert not admissible(dict(sample, intervals=[dict(system_busy_cpu=20)]), 0, 0, 0, 4)
    assert not admissible(dict(sample, ram_free_gib=11), 0, 0, 0, 4)
    assert not admissible(dict(sample, disk_free_gib=35.39), 0, 0, 0, 4)
    assert not admissible(sample, 0, 0, 4, 4)
    assert not admissible(dict(sample, intervals=[dict(system_busy_cpu=18)]), 5, 2, 0, 4)
    plan = read(REC / 'recovery_plan_v1.json')
    for family, spec in plan['families'].items():
        parts = [set(spec['completed']), {j['id'] for j in spec['pending']},
                 {r['job']['id'] for r in spec['adopted']}]
        assert len(set.union(*parts)) == sum(map(len, parts)) == spec['total']
    for path, digest in plan['frozen_files'].items():
        assert sha(BASE / path) == digest, path
    save(REC / 'controller_controls_v1.json',
         dict(status='DISJOINT_COVERAGE_RESOURCE_AND_SOURCE_CONTROLS_PASS',
              controller_sha256=sha(Path(__file__)), plan_sha256=sha(REC / 'recovery_plan_v1.json'),
              resource_sha256=sha(REC / 'resource_observer_v1.py'),
              resource_boundary_tests=7, mathematical_search_unchanged=True), True)
    print('DISJOINT_COVERAGE_RESOURCE_AND_SOURCE_CONTROLS_PASS')


def main():
    checked = read(REC / 'controller_controls_v1.json')
    assert checked['status'] == 'DISJOINT_COVERAGE_RESOURCE_AND_SOURCE_CONTROLS_PASS'
    assert sha(Path(__file__)) == checked['controller_sha256']
    assert sha(REC / 'recovery_plan_v1.json') == checked['plan_sha256']
    assert sha(REC / 'resource_observer_v1.py') == checked['resource_sha256']
    plan = read(REC / 'recovery_plan_v1.json')
    assert all(not live(r) for r in plan['old_controller_identities'].values())
    own = identity(os.getpid())
    save(REC / 'controller_identity_v1.json', dict(identity=own, started_utc=datetime.now(timezone.utc).isoformat(),
         source_sha256=checked['controller_sha256'], plan_sha256=checked['plan_sha256']), True)
    pending = {k: list(v['pending']) for k, v in plan['families'].items()}
    closed = {k: set(v['completed']) for k, v in plan['families'].items()}
    failures, attempts, active = [], {}, {}
    logs = REC / 'driver_logs'
    logs.mkdir(exist_ok=False)
    for family, spec in plan['families'].items():
        for row in spec['adopted']:
            assert live(row['identity'])
            active[(family, row['job']['id'])] = dict(job=row['job'], identity=row['identity'],
                                                    process=None, started=0, adopted=True)
    rotation = 0
    while any(pending.values()) or active:
        for key, item in list(active.items()):
            family, jid = key
            process = item['process']
            if (process is None and live(item['identity'])) or (process is not None and process.poll() is None):
                continue
            if process is not None:
                item['out'].close()
                item['err'].close()
            spec = plan['families'][family]
            folder = BASE / spec['folder'] / 'jobs' / jid
            try:
                good, status = valid_result(family, item['job'], folder, spec['success_status'])
                if process is not None and process.returncode != 0:
                    good = False
                    status = 'NONZERO_DRIVER_EXIT_NOT_EXCLUSION'
            except Exception as exc:
                good, status = False, 'INTEGRITY_ERROR_NOT_EXCLUSION:' + repr(exc)
            if good:
                closed[family].add(jid)
            elif not folder.exists() and process is not None:
                error = item['stderr_path'].read_text(encoding='utf-8', errors='replace')
                resource_refusal = ('AssertionError' in error and
                                    ('system_busy_cpu' in error or 'ram_free_gib' in error or 'disk_free_gib' in error))
                if resource_refusal:
                    pending[family].append(item['job'])
                else:
                    failures.append(dict(family=family, id=jid, status=status, exit_code=process.returncode))
            else:
                failures.append(dict(family=family, id=jid, status=status,
                                     exit_code=process.returncode if process is not None else None))
            save(logs / (family + '__' + jid + '__' + str(item.get('attempt', 0)) + '.receipt.json'),
                 dict(family=family, id=jid, success=good, status=status, adopted=item['adopted'],
                      at_utc=datetime.now(timezone.utc).isoformat()), True)
            del active[key]
        roots = [x['identity'] for x in active.values() if x.get('identity')]
        try:
            resource = measure(roots)
        except Exception as exc:
            save(REC / 'resource_error_latest.json', dict(at_utc=datetime.now(timezone.utc).isoformat(),
                                                        error=repr(exc), no_new_starts=True))
            time.sleep(10)
            continue
        warmups = sum(time.monotonic() - x['started'] < 15 for x in active.values() if not x['adopted'])
        families = ['high', 'low', 'singleton']
        for step in range(3):
            family = families[(rotation + step) % 3]
            spec = plan['families'][family]
            count = sum(k[0] == family for k in active)
            if not pending[family] or not admissible(resource, len(active), warmups, count,
                                                    plan['max_workers_by_family'][family]):
                continue
            for path, digest in plan['frozen_files'].items():
                assert sha(BASE / path) == digest, ('BOUND_SOURCE_CHANGED', path)
            job = pending[family].pop(0)
            jid = job['id']
            directory = BASE / spec['folder'] / 'jobs' / jid
            if directory.exists():
                failures.append(dict(family=family, id=jid, status='EXISTING_DIRECTORY_NOT_OVERWRITTEN'))
                continue
            key = (family, jid)
            assert key not in active and jid not in closed[family]
            attempts[key] = attempts.get(key, 0) + 1
            tag = family + '__' + jid + '__' + str(attempts[key])
            out_path, err_path = logs / (tag + '.stdout'), logs / (tag + '.stderr')
            out, err = out_path.open('xb'), err_path.open('xb')
            args = [sys.executable, '-B', str(BASE / spec['folder'] / spec['driver'])]
            args += ([jid] if family == 'high' else [str(job['chart']), str(job['own_parity'])]
                     if family == 'low' else [str(job['chart'])])
            process = subprocess.Popen(args, cwd=BASE / spec['folder'], stdout=out, stderr=err,
                                       creationflags=subprocess.CREATE_NO_WINDOW,
                                       env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
            try:
                birth = identity(process.pid)
            except (OSError, AssertionError):
                birth = None
            item = dict(job=job, process=process, identity=birth, started=time.monotonic(),
                        adopted=False, out=out, err=err, stderr_path=err_path, attempt=attempts[key])
            active[key] = item
            save(logs / (tag + '.launch.json'), dict(job=job, family=family, identity=birth,
                 pid=process.pid, args=args, resource=resource, controller_identity=own), True)
            rotation = (families.index(family) + 1) % 3
            break
        status = dict(status='RUNNING' if any(pending.values()) or active else 'FINISHED_RECONCILIATION_REQUIRED',
                      updated_utc=datetime.now(timezone.utc).isoformat(), resource=resource, failures=failures,
                      families={k: dict(total=v['total'], closed=len(closed[k]), pending=len(pending[k]),
                                        active={jid: dict(identity=item['identity'], adopted=item['adopted'])
                                                for (fam, jid), item in active.items() if fam == k})
                                for k, v in plan['families'].items()},
                      full_independent_evidence_audit_required=True, old_sources_unchanged=True)
        save(REC / 'progress.json', status)
        if any(pending.values()) or active:
            time.sleep(3)
    save(REC / 'finished.json', status, True)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--controls':
        controls()
    else:
        main()
