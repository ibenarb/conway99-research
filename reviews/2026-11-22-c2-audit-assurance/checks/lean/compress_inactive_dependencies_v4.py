"""Separate storage pass for inactive, completed C3 dependency copies; .git excluded."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = (BASE / 'c3formal/.lake/packages').resolve()
sys.path.insert(0, str(BASE.parents[2] / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
from compress_closed_shell_v1 import allocated, COMPACT


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def admit():
    while True:
        resource = measure()
        if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35:
            return resource
        time.sleep(10)


def write(path, value, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=4)


def main():
    mode = sys.argv[1]
    assert mode in ('pilot', 'full')
    initial = admit()
    assert read(BASE / 'fresh_c3_acceptance_audit_v1.json')['status'] == 'FRESH_C3_BUILD_SIX_KERNELS_STATEMENT_MATCH_AND_ARCHIVE_PASS'
    assert sha(BASE / 'inactive_dependencies_inventory_v4.json') == '745c351c0250152f6649ad8a527102f6735423b2798fa530a0fccfd217cdb50b'
    rows = sorted(read(BASE / 'inactive_dependencies_inventory_v4.json'), key=lambda r: (-r['bytes'], r['path']))
    assert len(rows) == 2153 and len({r['path'] for r in rows}) == 2153
    if mode == 'full':
        pilot = read(BASE / 'dependency_storage_pilot_result_v4.json')
        assert pilot['status'] == 'ALL_SELECTED_FILES_FULL_READBACK_BYTE_AND_MTIME_IDENTITY_PASS'
        assert len(pilot['records']) == 2
        assert [r['file'] for r in pilot['records']] == [r['path'] for r in rows[:2]]
    selected = rows[:2] if mode == 'pilot' else rows[2:]
    prefix = 'dependency_storage_' + mode
    write(BASE / (prefix + '_identity_v4.json'), dict(identity=identity(os.getpid()),
          started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=sha(Path(__file__)),
          resource=initial, count=len(selected)), True)
    records = []
    for offset in range(0, len(selected), 16):
        resource = initial if offset == 0 else admit()
        batch = selected[offset:offset + 16]
        before = []
        paths = []
        for row in batch:
            path = (ROOT / row['path']).resolve()
            assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
            stat = path.stat()
            assert 16384 <= stat.st_size and stat.st_size == row['bytes'] and stat.st_mtime_ns == row['mtime_ns']
            paths.append(path)
            before.append(dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                               allocated=allocated(path), sha256=sha(path)))
        command = [str(COMPACT), '/C', '/EXE:XPRESS16K', '/Q', *map(str, paths)]
        assert len(subprocess.list2cmdline(command)) < 30000
        with (BASE / (prefix + f'_v4_{offset:04d}.stdout')).open('xb') as out, (BASE / (prefix + f'_v4_{offset:04d}.stderr')).open('xb') as err:
            completed = subprocess.run(command, stdout=out, stderr=err,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        assert completed.returncode == 0
        for path, original in zip(paths, before):
            stat = path.stat()
            after = dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                         allocated=allocated(path), sha256=sha(path))
            assert all(original[k] == after[k] for k in ('bytes', 'mtime_ns', 'sha256'))
            assert after['allocated'] <= original['allocated']
            records.append(dict(file=path.relative_to(ROOT).as_posix(), before=original,
                                after=after, full_readback=True, batch_offset=offset))
        write(BASE / (prefix + f'_batch_v4_{offset:04d}.json'),
              dict(resource=resource, exit_code=completed.returncode, files=len(paths)), True)
        write(BASE / (prefix + '_progress_v4.json'), dict(records=records,
              saved_bytes=sum(r['before']['allocated'] - r['after']['allocated'] for r in records)))
    result = dict(status='ALL_SELECTED_FILES_FULL_READBACK_BYTE_AND_MTIME_IDENTITY_PASS',
                  records=records, saved_bytes=sum(r['before']['allocated'] - r['after']['allocated'] for r in records),
                  paths_and_content_unchanged=True, no_deletions=True, disjoint_from_toolchain_passes=True,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    write(BASE / (prefix + '_result_v4.json'), result, True)
    print(json.dumps(dict(status=result['status'], files=len(records), saved_bytes=result['saved_bytes'])), flush=True)


if __name__ == '__main__':
    main()
