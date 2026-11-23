"""Preserve fresh RAM build artifacts with complete archive readback; never declares a theorem."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import tarfile
import time

BASE = Path(__file__).resolve().parent
ROOT = Path('/dev/shm/conway99_c3_assurance_20261122_v1')
BUILD = ROOT / '.lake/build'
ARCHIVE = BASE / 'fresh_c3_build_artifacts_v1.tar.gz'
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
controller = json.loads((BASE / 'ram_lean_controller_result_v3.json').read_text())
assert BUILD.is_dir()
assert not ARCHIVE.exists()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

files = []
for path in sorted(BUILD.rglob('*')):
    if path.is_file():
        assert not path.is_symlink() and path.resolve().is_relative_to(BUILD.resolve())
        files.append(dict(path=path.relative_to(BUILD).as_posix(),
                          bytes=path.stat().st_size, sha256=sha(path)))
assert files
amount = sum(x['bytes'] for x in files)
assert shutil.disk_usage(BASE).free - amount > 35 * 2**30, 'Insufficient archive margin'
with tarfile.open(ARCHIVE, 'w:gz', compresslevel=6) as archive:
    for item in files:
        archive.add(BUILD / item['path'], arcname=item['path'], recursive=False)
expected = {x['path']: x for x in files}
seen = set()
with tarfile.open(ARCHIVE, 'r:gz') as archive:
    for member in archive:
        assert member.isfile() and member.name in expected and member.name not in seen
        h = hashlib.sha256()
        stream = archive.extractfile(member)
        total = 0
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            total += len(block)
            h.update(block)
        assert total == expected[member.name]['bytes']
        assert h.hexdigest() == expected[member.name]['sha256']
        seen.add(member.name)
assert seen == set(expected)
for item in files:
    assert sha(BUILD / item['path']) == item['sha256'], 'Artifact changed during archive'
report = dict(status='FRESH_BUILD_ARTIFACTS_PRESERVED_FULL_READBACK_PASS',
              controller_status=controller['status'], files=files,
              uncompressed_bytes=amount, archive_bytes=ARCHIVE.stat().st_size,
              archive_sha256=sha(ARCHIVE), no_ram_files_deleted=True,
              theorem_verdict=False, recorded_at=time.time())
(BASE / 'fresh_c3_build_archive_result_v1.json').write_text(json.dumps(report, indent=4))
print(json.dumps({k: v for k, v in report.items() if k != 'files'}), flush=True)
