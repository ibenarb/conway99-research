"""Version7: batched storage recovery with checked XPRESS16K fallback."""
from pathlib import Path
from datetime import datetime, timezone
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
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=4)


def main():
    mode = sys.argv[1]
    assert mode in ('pilot', 'full')
    plan_path = BASE / 'toolchain_lzx_plan_v6.json'
    assert sha(plan_path) == 'b66adf58571c5a9ce1c9d0a03350f0887b6182bfea7f0065437b3458f526919a'
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    for source in plan['sources']:
        assert sha(BASE / source['file']) == source['sha256']
    rows = plan['rows']
    assert len(rows) == 4525 and len({r['file'] for r in rows}) == 4525
    assert json.loads((BASE / 'toolchain_lzx_v6_allocation_incident_readback_v1.json').read_text(encoding='utf-8'))['status'] == 'ALL_146_TOUCHED_FILES_FULL_READBACK_PASS_ALLOCATION_GUARD_INCIDENT'
    if mode == 'full':
        pilot = json.loads((BASE / 'toolchain_lzx_pilot_v7/result.json').read_text(encoding='utf-8'))
        assert pilot['status'] == 'INACTIVE_TOOLCHAIN_LZX_FALLBACK_DOUBLE_READBACK_PASS' and pilot['fallbacks'] == 1
    rows = [r for r in rows if r['file'] == 'lib/lean/Lean/Elab/SyntheticMVars.olean.private'] if mode == 'pilot' else rows[146:]
    assert len(rows) == (1 if mode == 'pilot' else 4379)
    out = BASE / ('toolchain_lzx_' + mode + '_v7')
    out.mkdir(exist_ok=False)
    save(out / 'identity.json', dict(identity=identity(os.getpid()), source_sha256=sha(Path(__file__)), plan_sha256=sha(plan_path), started_utc=datetime.now(timezone.utc).isoformat()), True)
    records = []
    for offset in range(0, len(rows), 16):
        while True:
            resource = measure()
            ready = max(r['system_busy_cpu'] for r in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 12 and resource['disk_free_gib'] >= 2
            save(out / 'progress.json', dict(status='READY' if ready else 'WAIT_RESOURCE', completed=len(records), total=len(rows), saved_bytes=sum(r['saved_bytes'] for r in records), resource=resource))
            if ready:
                break
            time.sleep(10)
        selected = rows[offset:offset + 16]
        before = []
        paths = []
        for row in selected:
            path = (ROOT / row['file']).resolve()
            assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
            stat = path.stat()
            assert stat.st_size == row['bytes'] and 65536 <= stat.st_size < 10000000 and stat.st_mtime_ns == row['mtime_ns']
            assert sha(path) == row['sha256']
            paths.append(path)
            before.append(dict(bytes=stat.st_size, mtime_ns=stat.st_mtime_ns, sha256=row['sha256'], allocated=allocated(path)))
        save(out / ('%04d.before.json' % offset), dict(files=[p.relative_to(ROOT).as_posix() for p in paths], before=before, resource=resource), True)
        command = [str(COMPACT), '/C', '/F', '/EXE:LZX', '/Q', *map(str, paths)]
        assert len(subprocess.list2cmdline(command)) < 30000
        with (out / ('%04d.stdout' % offset)).open('xb') as stdout, (out / ('%04d.stderr' % offset)).open('xb') as stderr:
            done = subprocess.run(command, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        assert done.returncode == 0
        batch = []
        for path, original in zip(paths, before):
            stat = path.stat()
            assert stat.st_size == original['bytes'] and stat.st_mtime_ns == original['mtime_ns']
            assert sha(path) == original['sha256'] and sha(path) == original['sha256']
            after = allocated(path)
            fallback = after > original['allocated']
            lzx_allocated = after
            if fallback:
                label = '%04d_fallback_%02d' % (offset, len(batch))
                with (out / (label + '.stdout')).open('xb') as stdout, (out / (label + '.stderr')).open('xb') as stderr:
                    restored = subprocess.run([str(COMPACT), '/C', '/F', '/EXE:XPRESS16K', '/Q', str(path)], stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
                assert restored.returncode == 0
                assert sha(path) == original['sha256'] and sha(path) == original['sha256']
                assert path.stat().st_size == original['bytes'] and path.stat().st_mtime_ns == original['mtime_ns']
                after = allocated(path)
            assert after <= original['allocated']
            batch.append(dict(file=path.relative_to(ROOT).as_posix(), before=original, lzx_allocated=lzx_allocated, fallback_to_xpress16k=fallback, after_allocated=after, saved_bytes=original['allocated']-after, complete_readbacks_after=2))
        save(out / ('%04d.result.json' % offset), dict(records=batch, resource=resource), True)
        records.extend(batch)
    result = dict(status='INACTIVE_TOOLCHAIN_LZX_FALLBACK_DOUBLE_READBACK_PASS', records=records, fallbacks=sum(r['fallback_to_xpress16k'] for r in records), saved_bytes=sum(r['saved_bytes'] for r in records), no_deletions=True, no_research_started=True, research_thresholds_unchanged=True, corrective_storage_only=True, finished_utc=datetime.now(timezone.utc).isoformat())
    save(out / 'result.json', result, True)
    save(out / 'progress.json', dict(status=result['status'], completed=len(records), total=len(rows), saved_bytes=result['saved_bytes']))
    print(json.dumps({k:v for k,v in result.items() if k != 'records'}), flush=True)


if __name__ == '__main__':
    main()
