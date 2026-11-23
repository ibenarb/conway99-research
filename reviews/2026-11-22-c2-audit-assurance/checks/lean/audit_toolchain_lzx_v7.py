"""Separate full-byte acceptance of the 4525-file inactive toolchain pass."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'toolchain/lean-4.35.0-rc2-linux'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    plan_path = BASE / 'toolchain_lzx_plan_v6.json'
    assert sha(plan_path) == 'b66adf58571c5a9ce1c9d0a03350f0887b6182bfea7f0065437b3458f526919a'
    plan = read(plan_path)
    for source in plan['sources']:
        assert sha(BASE / source['file']) == source['sha256']
    source_path = BASE / 'recompress_inactive_toolchain_lzx_v7.py'
    assert sha(source_path) == '0a283f33899c07f578502c7493befce4bba1d75f6bee1a04500b0361095fb4f6'
    result_path = BASE / 'toolchain_lzx_full_v7/result.json'
    result = read(result_path)
    assert result['status'] == 'INACTIVE_TOOLCHAIN_LZX_FALLBACK_DOUBLE_READBACK_PASS'
    assert result['no_deletions'] and result['research_thresholds_unchanged']
    rows = plan['rows']
    assert len(rows) == len({r['file'] for r in rows}) == 4525
    records = {r['file']: r for r in result['records']}
    assert len(records) == len(result['records']) == 4379
    assert set(records) == {r['file'] for r in rows[146:]}
    incident = read(BASE / 'toolchain_lzx_v6_allocation_incident_readback_v1.json')
    assert incident['status'] == 'ALL_146_TOUCHED_FILES_FULL_READBACK_PASS_ALLOCATION_GUARD_INCIDENT'
    recovered = read(BASE / 'toolchain_lzx_v6_recovery_v1/result.json')
    assert recovered['status'] == 'ORIGINAL_ALLOCATION_AND_FULL_BYTE_IDENTITY_RESTORED'
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCompressedFileSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetCompressedFileSizeW.restype = wintypes.DWORD
    checked = []
    for row in rows:
        path = (ROOT / row['file']).resolve()
        assert path.is_relative_to(ROOT.resolve()) and path.is_file()
        stat = path.stat()
        assert stat.st_size == row['bytes'] and stat.st_mtime_ns == row['mtime_ns']
        assert sha(path) == row['sha256']
        high = wintypes.DWORD()
        ctypes.set_last_error(0)
        low = kernel.GetCompressedFileSizeW(str(path), ctypes.byref(high))
        assert low != 0xFFFFFFFF or not ctypes.get_last_error()
        allocated = int(low) + (int(high.value) << 32)
        assert allocated <= row['allocated']
        if row['file'] in records:
            record = records[row['file']]
            assert record['before']['sha256'] == row['sha256']
            assert record['before']['bytes'] == row['bytes']
            assert record['before']['mtime_ns'] == row['mtime_ns']
            assert allocated == record['after_allocated']
            assert record['saved_bytes'] == record['before']['allocated'] - allocated
            assert record['complete_readbacks_after'] == 2
        checked.append(dict(file=row['file'], sha256=row['sha256'], bytes=stat.st_size,
                            mtime_ns=stat.st_mtime_ns, allocated=allocated,
                            saved_bytes=row['allocated']-allocated))
    assert sum(r['saved_bytes'] for r in result['records']) == result['saved_bytes']
    assert sum(r['fallback_to_xpress16k'] for r in result['records']) == result['fallbacks']
    output = dict(status='ALL_4525_INACTIVE_FILES_SEPARATE_FULL_READBACK_PASS',
                  finished_utc=datetime.now(timezone.utc).isoformat(), files=len(checked),
                  source_sha256=sha(Path(__file__)), plan_sha256=sha(plan_path),
                  v7_result_sha256=sha(result_path), v7_files=4379,
                  earlier_touched_files=146, v7_fallbacks=result['fallbacks'],
                  v7_saved_bytes=result['saved_bytes'],
                  all_4525_saved_bytes=sum(r['saved_bytes'] for r in checked),
                  mathematical_search_status_unchanged=True, records=checked)
    with (BASE / 'toolchain_lzx_acceptance_v7.json').open('x', encoding='utf-8') as stream:
        json.dump(output, stream, indent=4)
        stream.write('\n')
    print(json.dumps({k:v for k,v in output.items() if k != 'records'}), flush=True)


if __name__ == '__main__':
    main()
