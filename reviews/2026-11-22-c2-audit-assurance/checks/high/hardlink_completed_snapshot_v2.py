"""Deduplicate only closed, audited, Git-committed high-job copies; preserve every path and byte."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
REPO = WORKSPACE / 'git-assurance'
DOSSIER = REPO / 'reviews/2026-11-22-c2-audit-assurance'
SOURCE = (BASE / 'jobs').resolve()
TARGET = (DOSSIER / 'checks/high/jobs').resolve()
EXPECTED_COMMIT = '4882302fa954984c95cc1595ab1be3dd1091f7c2'
sys.path.insert(0, str(WORKSPACE / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
from compress_closed_shell_v1 import allocated


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + str(REPO), '-C', str(REPO), *args])


def admit():
    while True:
        resource = measure()
        if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35:
            return resource
        time.sleep(10)


def main():
    resource = admit()
    controller = read(BASE / 'controller_identity.json')['identity']
    assert identity(controller['pid']) == controller
    assert git('rev-parse', 'HEAD').decode().strip() == EXPECTED_COMMIT
    manifest_path = 'reviews/2026-11-22-c2-audit-assurance/CHECKS_MANIFEST.json'
    committed = git('show', 'HEAD:' + manifest_path)
    assert committed == (DOSSIER / 'CHECKS_MANIFEST.json').read_bytes()
    manifest = {r['path']: r for r in json.loads(committed)['files']}
    inventory = read(BASE / 'additional_duplicate_inventory_v2.json')
    assert len(inventory) == 868
    audit = dict(status='IN_PROGRESS', started_utc=datetime.now(timezone.utc).isoformat(),
                 identity=identity(os.getpid()), source_sha256=digest(Path(__file__)),
                 git_commit=EXPECTED_COMMIT, manifest_sha256=hashlib.sha256(committed).hexdigest(),
                 resource_checks=[resource], files=[], samefile_already=0,
                 hardlinks_are_not_independent_backups=True)
    with (BASE / 'snapshot_hardlink_identity_v2.json').open('x', encoding='utf-8') as stream:
        json.dump(audit['identity'], stream, indent=4)
    journal = BASE / 'snapshot_hardlink_journal_v2.jsonl'
    with journal.open('x', encoding='utf-8', newline='\n') as stream:
        for index, row in enumerate(inventory):
            if index and index % 100 == 0:
                audit['resource_checks'].append(admit())
            relative = Path(row['path'])
            src = (SOURCE / relative).resolve()
            dst = (TARGET / relative).resolve()
            assert src.is_relative_to(SOURCE) and dst.is_relative_to(TARGET)
            assert src.is_file() and dst.is_file() and not src.is_symlink() and not dst.is_symlink()
            result = read(src.parent / 'result.json')
            assert result['status'] == 'SECOND_SOLVER_CLOSED' and result['open'] == 0
            assert relative.parts[0] not in read(BASE / 'full_progress.json')['active']
            expected = manifest['high/jobs/' + relative.as_posix()]
            assert src.stat().st_size == dst.stat().st_size == expected['bytes'] == row['bytes']
            assert digest(src) == digest(dst) == expected['sha256']
            if os.path.samefile(src, dst):
                audit['samefile_already'] += 1
                continue
            assert dst.stat().st_nlink == 1
            before = dict(allocated_bytes=allocated(dst), mtime_ns=dst.stat().st_mtime_ns)
            temp = dst.with_name(dst.name + '.verified-link-v2')
            assert not temp.exists()
            os.link(src, temp)
            assert os.path.samefile(src, temp) and digest(temp) == expected['sha256']
            os.replace(temp, dst)
            assert os.path.samefile(src, dst) and digest(dst) == digest(src) == expected['sha256']
            record = dict(path=relative.as_posix(), bytes=expected['bytes'], sha256=expected['sha256'],
                          previous_duplicate=before, source_and_target_readback=True,
                          source_path=str(src), target_path=str(dst))
            audit['files'].append(record)
            stream.write(json.dumps(record) + '\n')
            stream.flush()
    audit.update(status='ALL_868_CLOSED_COMMITTED_COPIES_FULL_READBACK_PASS',
                 finished_utc=datetime.now(timezone.utc).isoformat(),
                 reclaimed_allocated_bytes=sum(r['previous_duplicate']['allocated_bytes'] for r in audit['files']),
                 original_paths_preserved=True, original_file_contents_preserved=True)
    assert len(audit['files']) + audit['samefile_already'] == 868
    with (BASE / 'git_snapshot_hardlink_readback_v2.json').open('x', encoding='utf-8') as stream:
        json.dump(audit, stream, indent=4)
    print(json.dumps({k:v for k,v in audit.items() if k not in ('files','resource_checks')}), flush=True)


if __name__ == '__main__':
    main()
