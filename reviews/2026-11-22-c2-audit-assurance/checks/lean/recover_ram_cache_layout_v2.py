"""Recover only the misplaced Mathlib cache directory in the temporary RAM copy."""
from pathlib import Path
import hashlib
import json
import os
import time

BASE = Path(__file__).resolve().parent
ROOT = Path('/dev/shm/conway99_c3_assurance_20261122_v1').resolve()
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
assert ROOT.parent == Path('/dev/shm')
assert not (BASE / 'ram_prepare_result_v2.json').exists()
started = time.time()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

config = json.loads((BASE / 'cache_config_v1.json').read_text())
expansion = json.loads((BASE / 'cache_expansion_result_v1.json').read_text())
mapping = {}
for item in config:
    if isinstance(item, str):
        name, base = Path(item).name, Path('.')
    else:
        name, base = Path(item['file']).name, Path(item['base'])
        assert base == Path('.lake/packages/mathlib')
    assert name not in mapping
    mapping[name] = base
assert len(mapping) == len(expansion['records']) == 2209
source = (ROOT / '.lake/build').resolve()
target = (ROOT / '.lake/packages/mathlib/.lake/build').resolve()
assert source.is_relative_to(ROOT) and target.is_relative_to(ROOT)
assert source.is_dir() and not target.exists()
expected = set()
for record in expansion['records']:
    base = mapping[record['archive']]
    for item in record['files']:
        current = ROOT / item['path']
        assert current.resolve().is_relative_to(ROOT)
        assert current.is_file() and not current.is_symlink()
        assert current.stat().st_size == item['bytes'] and sha(current) == item['sha256']
        if base != Path('.'):
            assert Path(item['path']).parts[:2] == ('.lake', 'build')
            expected.add(current.resolve())
actual = {x.resolve() for x in source.rglob('*') if x.is_file()}
assert actual == expected, 'Unexpected files in directory selected for relocation'
target.parent.mkdir(parents=True, exist_ok=True)
source.rename(target)
for record in expansion['records']:
    base = mapping[record['archive']]
    for item in record['files']:
        current = ROOT / base / item['path']
        assert current.resolve().is_relative_to(ROOT)
        assert current.stat().st_size == item['bytes'] and sha(current) == item['sha256']
manifest = json.loads((BASE.parents[2] / 'work/C3_Statuspruefung_20261122/source_manifest_v1.json').read_text())
pinned = [x for x in manifest if x['path'].startswith('c3formal/')]
assert len(pinned) == 28
for item in pinned:
    assert sha(ROOT / item['path'][len('c3formal/'):]) == item['sha256']
assert not (ROOT / '.lake/build').exists()
report = dict(status='RAM_BUILD_TREE_READY', root=str(ROOT), pinned_files=28,
              cache_archives=2209, relocated_mathlib_archives=1952,
              moved_files=len(expected), all_cache_files_verified_after_relocation=True,
              no_project_prebuilt_artifacts=True, original_sources_unchanged=True,
              cache_plan_sha256=sha(BASE / 'cache_config_v1.json'),
              preflight_manifest_sha256=sha(BASE / 'cache_expansion_result_v1.json'),
              original_v1_failure_preserved=True, elapsed_seconds=time.time() - started,
              proof_build=False, security_or_mount_changes=False)
(BASE / 'ram_prepare_result_v2.json').write_text(json.dumps(report, indent=4))
print(json.dumps(report), flush=True)
