"""Separate LZX recovery pass for 15 inactive, already byte-verified Lean files."""
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
    prior = json.loads((BASE / 'toolchain_storage_result_v1.json').read_text(encoding='utf-8'))
    assert prior['status'] == 'ALL_15_FILES_FULL_READBACK_BYTE_AND_MTIME_IDENTITY_PASS'
    assert json.loads((BASE / 'fresh_c3_acceptance_audit_v1.json').read_text(encoding='utf-8'))['status'] == 'FRESH_C3_BUILD_SIX_KERNELS_STATEMENT_MATCH_AND_ARCHIVE_PASS'
    rows = prior['records']
    assert len(rows) == 15 and len({r['file'] for r in rows}) == 15
    if mode == 'full':
        pilot = json.loads((BASE / 'toolchain_lzx_pilot_v5/result.json').read_text(encoding='utf-8'))
        assert pilot['status'] == 'INACTIVE_TOOLCHAIN_LZX_DOUBLE_READBACK_PASS' and pilot['saved_bytes'] > 0
    rows = rows[:1] if mode == 'pilot' else rows[1:]
    out = BASE / ('toolchain_lzx_' + mode + '_v5')
    out.mkdir(exist_ok=False)
    save(out / 'identity.json', dict(identity=identity(os.getpid()), source_sha256=sha(Path(__file__)), prior_receipt_sha256=sha(BASE / 'toolchain_storage_result_v1.json')), True)
    records = []
    for number, row in enumerate(rows):
        while True:
            resource = measure()
            ready = max(r['system_busy_cpu'] for r in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 12 and resource['disk_free_gib'] >= 2
            save(out / 'progress.json', dict(status='READY' if ready else 'WAIT_RESOURCE', completed=len(records), total=len(rows), resource=resource, next=row['file']))
            if ready:
                break
            time.sleep(10)
        path = (ROOT / row['file']).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
        before = dict(bytes=path.stat().st_size, mtime_ns=path.stat().st_mtime_ns, sha256=sha(path), allocated=allocated(path))
        assert all(before[k] == row['after'][k] for k in ['bytes', 'mtime_ns', 'sha256'])
        save(out / ('%02d.before.json' % number), dict(file=row['file'], before=before, resource=resource), True)
        with (out / ('%02d.stdout' % number)).open('xb') as stdout, (out / ('%02d.stderr' % number)).open('xb') as stderr:
            result = subprocess.run([str(COMPACT), '/C', '/F', '/EXE:LZX', '/Q', str(path)], stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        after = dict(bytes=path.stat().st_size, mtime_ns=path.stat().st_mtime_ns, sha256=sha(path), allocated=allocated(path))
        assert all(before[k] == after[k] for k in ['bytes', 'mtime_ns', 'sha256'])
        assert result.returncode == 0 and sha(path) == before['sha256']
        assert after['allocated'] <= before['allocated']
        rec = dict(file=row['file'], before=before, after=after, saved_bytes=before['allocated']-after['allocated'], complete_post_readbacks=2)
        save(out / ('%02d.result.json' % number), rec, True)
        records.append(rec)
    result = dict(status='INACTIVE_TOOLCHAIN_LZX_DOUBLE_READBACK_PASS', records=records, saved_bytes=sum(r['saved_bytes'] for r in records), no_deletions=True, no_research_started=True, research_thresholds_unchanged=True, corrective_storage_only=True, finished_utc=datetime.now(timezone.utc).isoformat())
    save(out / 'result.json', result, True)
    print(json.dumps({k:v for k,v in result.items() if k != 'records'}), flush=True)


if __name__ == '__main__':
    main()
