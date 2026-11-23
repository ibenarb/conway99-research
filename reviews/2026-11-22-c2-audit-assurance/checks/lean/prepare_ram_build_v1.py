"""Prepare an isolated RAM build tree; preserve all durable sources and cache archives."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
SOURCE = BASE / 'c3formal'
ROOT = Path('/dev/shm/conway99_c3_assurance_20261122_v1')
BINARY = BASE / 'toolchain/lean-4.35.0-rc2-linux/bin'
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
started = time.time()

def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def write(name, data):
    (BASE / name).write_text(json.dumps(data, indent=4))

assert not ROOT.exists(), 'Existing RAM tree: refuse duplicate preparation'
expansion = json.loads((BASE / 'cache_expansion_result_v1.json').read_text())
assert expansion['status'] == 'ALL_ARCHIVES_EXPANDED_AND_HASHED_IN_RAM'
assert expansion['completed'] == 2209
assert shutil.disk_usage(ROOT.parent).free > expansion['expanded_bytes'] + 2 * 2**30
manifest = json.loads((WORKSPACE / 'work/C3_Statuspruefung_20261122/source_manifest_v1.json').read_text())
pinned = [x for x in manifest if x['path'].startswith('c3formal/')]
assert len(pinned) == 28
for item in pinned:
    assert sha(SOURCE / item['path'][len('c3formal/'):]) == item['sha256']
ROOT.mkdir()
try:
    copied = []
    for directory, directories, files in os.walk(SOURCE):
        relative = Path(directory).relative_to(SOURCE)
        if Path(directory).name == '.lake':
            directories[:] = [x for x in directories if x == 'packages']
            files = []
        destination = ROOT / relative
        destination.mkdir(parents=True, exist_ok=True)
        for name in files:
            if relative == Path('.') and name == 'CachePlan_v1.lean':
                continue
            original = Path(directory) / name
            target = destination / name
            assert not original.is_symlink(), str(original)
            shutil.copyfile(original, target)
            expected = sha(original)
            assert sha(target) == expected
            copied.append(dict(path=target.relative_to(ROOT).as_posix(),
                               bytes=target.stat().st_size, sha256=expected))
    assert not (ROOT / '.lake/build').exists()
    write('ram_source_copy_v1.json', dict(root=str(ROOT), files=copied, pinned_files=len(pinned)))
    for index, item in enumerate(expansion['records']):
        archive = BASE / 'mathlib_cache' / item['archive']
        assert sha(archive) == item['archive_sha256']
        result = subprocess.run([str(BINARY / 'leantar'), '--jobs', '1', '-C', str(ROOT), '-x', str(archive)],
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(dict(archive=item['archive'], exit_code=result.returncode, stderr=result.stderr))
        for record in item['files']:
            target = ROOT / record['path']
            assert target.resolve().is_relative_to(ROOT.resolve())
            assert target.is_file() and not target.is_symlink()
            assert target.stat().st_size == record['bytes'] and sha(target) == record['sha256']
        if (index + 1) % 100 == 0:
            write('ram_prepare_progress_v1.json', dict(status='PREPARING_RAM_TREE',
                  archives=index + 1, elapsed_seconds=time.time() - started, root=str(ROOT)))
    for item in pinned:
        assert sha(ROOT / item['path'][len('c3formal/'):]) == item['sha256']
    assert not (ROOT / '.lake/build').exists(), 'Project must have no prebuilt proof artifacts'
    report = dict(status='RAM_BUILD_TREE_READY', root=str(ROOT), pinned_files=len(pinned),
                  copied_files=len(copied), copied_bytes=sum(x['bytes'] for x in copied),
                  cache_archives=len(expansion['records']), cache_bytes=expansion['expanded_bytes'],
                  source_copy_manifest_sha256=sha(BASE / 'ram_source_copy_v1.json'),
                  cache_expansion_manifest_sha256=sha(BASE / 'cache_expansion_result_v1.json'),
                  elapsed_seconds=time.time() - started, proof_build=False,
                  originals_unchanged=True, no_security_or_mount_changes=True)
    write('ram_prepare_result_v1.json', report)
    print(json.dumps(report), flush=True)
except Exception as error:
    write('ram_prepare_error_v1.json', dict(status='PREPARATION_ERROR_NOT_PROOF_VERDICT',
          error=repr(error), root=str(ROOT), elapsed_seconds=time.time() - started))
    raise
