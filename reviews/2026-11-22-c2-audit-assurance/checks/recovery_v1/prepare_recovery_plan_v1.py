"""Freeze an integrity-checked, disjoint continuation plan; never launch work."""
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

REC = Path(__file__).resolve().parent
BASE = REC.parent
sys.path.insert(0, str(REC))
from resource_observer_v1 import measure, live


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    frozen, changes = {}, []
    for family, folder, original, target in [
            ('low', 'low_v2', 'run_one_low_v1.py', 'run_one_low_recovery_v2.py'),
            ('singleton', 'singleton_v2', 'run_one_singleton_v2.py', 'run_one_singleton_recovery_v3.py')]:
        src, dst = BASE / folder / original, BASE / folder / target
        text = src.read_text(encoding='utf-8')
        needle = 'from c2_shared_measurement_20261118_v1 import measure'
        replacement = "sys.path.insert(0, str(BASE.parent / 'recovery_v1'))\nfrom resource_observer_v1 import measure"
        if family == 'low':
            added = "    report['execution_driver_sha256'] = sha(Path(__file__))\n"
        else:
            added = "        record['execution_driver_sha256'] = sha(Path(__file__))\n"
        assert dst.read_text(encoding='utf-8').replace(added, '').replace(replacement, needle) == text
        changes.append(dict(family=family, original=src.relative_to(BASE).as_posix(),
                            original_sha256=sha(src), new=dst.relative_to(BASE).as_posix(),
                            new_sha256=sha(dst), search_logic_identical=True,
                            only_changes=['resource import without historical-process dependency',
                                          'execution driver hash in result']))
    families = {}
    specs = [('high', 'high_v1', 'SECOND_SOLVER_CLOSED', 'jobs_manifest.json'),
             ('low', 'low_v2', 'SECOND_LOW_SOLVER_CLOSED', 'jobs_manifest.json'),
             ('singleton', 'singleton_v2', 'SECOND_SINGLETON_SOLVER_CLOSED', 'jobs_manifest_v1.json')]
    for family, folder, ok, manifest in specs:
        directory = BASE / folder
        data = read(directory / manifest)
        frozen[(directory / manifest).relative_to(BASE).as_posix()] = sha(directory / manifest)
        jobs = ([dict(id=str(cid), chart=cid) for cid in data['search_charts']]
                if family == 'singleton' else data['jobs'])
        assert len(jobs) == {'high': 3156, 'low': 92, 'singleton': 3308}[family]
        assert len({job['id'] for job in jobs}) == len(jobs)
        completed, pending, adopted, integrity = [], [], [], []
        for job in jobs:
            path = directory / 'jobs' / job['id']
            if not path.exists():
                pending.append(job)
                continue
            if not (path / 'result.json').exists():
                assert family == 'low' and job['id'] in ['333.0', '333.1']
                expected = read(path / 'identity.json')['identity']
                assert live(expected)
                adopted.append(dict(job=job, identity=expected))
                continue
            result = read(path / 'result.json')
            assert result['status'] == ok, (family, job['id'], result.get('status'))
            hashes = result.get('hashes', result.get('evidence_hashes', result.get('output_hashes', {})))
            assert hashes
            for name, digest in hashes.items():
                assert sha(path / name) == digest, (family, job['id'], name)
            if family == 'high':
                assert result['job'] == job and result['open'] == 0 and result['closed'] == result['stars']
                for name, archive in result['input_archives'].items():
                    assert sha(path / (name + '.gz')) == archive['compressed_sha256']
            elif family == 'low':
                assert result['chart'] == job['chart'] and result['packet_parity'] == job['packet_parity']
                assert result['stars'] == job['stars'] and result['open'] == 0
                assert result['closed'] == result['stars'] and result['closed_planes'] == result['viable_planes']
            else:
                assert result['chart'] == job['chart'] and result['roots_completed'] == result['roots_planned']
                assert result['exit_code'] == 0
                archive = result.get('lossless_input_archive')
                if archive:
                    assert archive['full_readback'] and sha(path / archive['file']) == archive['archive_sha256']
                else:
                    assert job['chart'] in [0, 183, 3377] and 'setup.txt' in hashes
            for name, digest in result.get('source_hashes', {}).items():
                key = (directory / name).relative_to(BASE).as_posix()
                if key not in frozen:
                    frozen[key] = sha(directory / name)
                assert frozen[key] == digest, (family, name)
            completed.append(job['id'])
            integrity.append(dict(id=job['id'], result_sha256=sha(path / 'result.json'),
                                  recorded_evidence_hashes_match=True))
        drivers = dict(high='run_one_high_v1.py', low='run_one_low_recovery_v2.py',
                       singleton='run_one_singleton_recovery_v3.py')
        additional = dict(high=['orbits_result.json', 'star_counts_own.json'],
                          low=['gram_controls_result.json', 'pair_controls_result.json', 'star_counts_own.json'],
                          singleton=['controls_result_v1.json', 'singleton_setup_v1.py',
                                     'singleton_exact_v1.cpp', 'singleton_exact_v1_checked'])
        for name in [drivers[family]] + additional[family]:
            frozen[(directory / name).relative_to(BASE).as_posix()] = sha(directory / name)
        families[family] = dict(folder=folder, success_status=ok, total=len(jobs), completed=completed,
                                pending=pending, adopted=adopted, integrity=integrity, driver=drivers[family])
    frozen['recovery_v1/resource_observer_v1.py'] = sha(REC / 'resource_observer_v1.py')
    plan = dict(status='INTEGRITY_RECONCILED_FOR_CONTINUATION_NOT_NEW_MATHEMATICAL_AUDIT',
                created_utc=datetime.now(timezone.utc).isoformat(), families=families,
                frozen_files=frozen, driver_changes=changes,
                old_controller_identities=read(BASE / 'heartbeat_control_0125.json')['identities'],
                resource_observation=measure(), max_workers_by_family=dict(high=10, low=4, singleton=6),
                max_workers_total=20)
    with (REC / 'recovery_plan_v1.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(plan, stream, indent=4)
    print(json.dumps({k: dict(completed=len(v['completed']), adopted=len(v['adopted']), pending=len(v['pending']))
                      for k, v in families.items()}))


if __name__ == '__main__':
    main()
