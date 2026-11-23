"""Transparent compression of selected inactive local toolchain files; byte identity required."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = (BASE / 'toolchain/lean-4.35.0-rc2-linux').resolve()
sys.path.insert(0, str(BASE.parents[2] / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
from compress_closed_shell_v1 import allocated, COMPACT

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

with (BASE / 'toolchain_storage_identity_v1.json').open('x') as stream:
    json.dump(dict(identity=identity(os.getpid()), started=time.time()), stream, indent=4)
files = sorted((p for p in ROOT.rglob('*') if p.is_file() and p.stat().st_size > 10000000),
               key=lambda p: -p.stat().st_size)
assert len(files) == 15
records = []
for index, path in enumerate(files):
    assert path.resolve().is_relative_to(ROOT) and not path.is_symlink()
    while True:
        resource = measure()
        if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35:
            break
        time.sleep(10)
    stat = path.stat()
    before = dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                  allocated=allocated(path), sha256=sha(path))
    command = [str(COMPACT), '/C', '/EXE:XPRESS16K', '/Q', str(path)]
    with (BASE / f'toolchain_storage_{index:02d}.stdout').open('xb') as out, (BASE / f'toolchain_storage_{index:02d}.stderr').open('xb') as err:
        result = subprocess.run(command, stdout=out, stderr=err,
                                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    stat = path.stat()
    after = dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                 allocated=allocated(path), sha256=sha(path))
    assert result.returncode == 0
    assert all(before[x] == after[x] for x in ['bytes', 'mtime_ns', 'sha256'])
    assert after['allocated'] <= before['allocated']
    records.append(dict(file=path.relative_to(ROOT).as_posix(), before=before, after=after,
                        full_readback=True, resource=resource, command=command))
    (BASE / 'toolchain_storage_progress_v1.json').write_text(json.dumps(dict(
        records=records, saved_bytes=sum(x['before']['allocated']-x['after']['allocated'] for x in records)), indent=4))
(BASE / 'toolchain_storage_result_v1.json').write_text(json.dumps(dict(
    status='ALL_15_FILES_FULL_READBACK_BYTE_AND_MTIME_IDENTITY_PASS', records=records,
    saved_bytes=sum(x['before']['allocated']-x['after']['allocated'] for x in records),
    no_deletions=True, logical_paths_unchanged=True, programs_unchanged=True), indent=4))
