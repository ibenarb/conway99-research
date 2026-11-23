from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
OUT = Path(__file__).resolve().parent
CHECKS = ROOT / 'git-assurance/reviews/2026-11-22-c2-audit-assurance/checks'
sys.path.insert(0, str(BASE / 'recovery_v1'))
from resource_observer_v1 import measure, live


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    released = json.loads((BASE / 'R_offload_20261123_v1/case77_relocation_complete.json').read_text())
    assert released['bytes_preserved'] and released['released_bytes'] == 32139272868
    assert not (ROOT / 'review/C2_Fall77_Abschluss_20261107_Vollstaendig.zip').exists()
    controller = json.loads((BASE / 'recovery_v1/controller_identity_v1.json').read_text())
    assert not live(controller['identity'])
    assert sha(BASE / 'recovery_v1/finished.json') == '06c6c6990ecf1808ef4aa528195c25d2576650fd12d4815441951208911f8fb5'
    assert json.loads((BASE / 'recovery_v1/finished.json').read_text()) == json.loads((BASE / 'recovery_v1/progress.json').read_text())
    assert sha(BASE / 'recovery_v1/progress.json') == 'ef55a00938bfe48627829744a536493896cd179fccf7e16838c72145eed172e4'
    accepted = json.loads((OUT / 'final_s1_acceptance_v1.json').read_text())
    assert accepted['status'] == 'FULL_S1_COVERAGE_AND_FINAL_REPORT_INDEPENDENTLY_ACCEPTED'
    assert accepted['singleton']['audited'] == 3308 and accepted['singleton']['full_S1_complete']
    resource = measure([])
    assert max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20
    assert resource['ram_free_gib'] >= 10
    groups = [
        ('high_v1', 'high', 'audit_complete_1820_v2.json', 'passed', 'id'),
        ('singleton_v2', 'singleton_v2', 'audit_complete_1900_v1.json', 'checked', 'chart')
    ]
    items = []
    snapshots = []
    for source_folder, destination_folder, audit_name, row_key, id_key in groups:
        source = BASE / source_folder
        destination = CHECKS / destination_folder
        audit = json.loads((source / audit_name).read_text())
        assert audit['status'] in ('COMPLETE_S2_LEDGER_AND_READBACK_PASS', 'SINGLETON_EVIDENCE_SNAPSHOT_PASS')
        assert not audit.get('failures', [])
        if source_folder == 'singleton_v2':
            assert audit['full_S1_coverage'] and audit['audited_closed'] == 3308 and audit['remaining'] == 0
            assert sha(source / audit_name) == accepted['singleton']['audit_sha256']
        snapshots.append(dict(source_folder=source_folder, cases=len(audit[row_key]), audit=audit_name, sha256=sha(source / audit_name)))
        items.append((source / audit_name, destination / audit_name))
        for row in audit[row_key]:
            identifier = str(row[id_key])
            job_source = source / 'jobs' / identifier
            assert sha(job_source / 'result.json') == row['result_sha256']
            for path in sorted(job_source.rglob('*')):
                if path.is_file():
                    assert not path.is_symlink()
                    assert path.stat().st_size < 100 * 1024 ** 2, 'Git single-file limit'
                    items.append((path, destination / 'jobs' / identifier / path.relative_to(job_source)))
    assert len({str(dst) for _, dst in items}) == len(items)
    new_bytes = sum(src.stat().st_size for src, dst in items if not dst.exists())
    assert shutil.disk_usage(ROOT).free >= 39 * 1024 ** 3 + 2 * new_bytes
    added, checked = [], []
    for source, destination in items:
        before = source.stat()
        digest = sha(source)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(destination.name + '.staging_1930')
            assert not temporary.exists()
            shutil.copy2(source, temporary)
            assert sha(temporary) == digest and temporary.stat().st_size == before.st_size
            temporary.rename(destination)
            added.append(dict(path=destination.relative_to(CHECKS).as_posix(), bytes=before.st_size, sha256=digest))
        assert sha(destination) == digest
        after = source.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        checked.append(destination.relative_to(CHECKS).as_posix())
    result = dict(at_utc=datetime.now(timezone.utc).isoformat(), status='AUDITED_SNAPSHOT_PAYLOADS_COPIED_AND_FULL_READBACK_PASS', source_sha256=sha(Path(__file__)), resource=resource, snapshots=snapshots, all_selected_files_checked=len(checked), new_files=len(added), new_bytes=new_bytes, added=added, no_new_search_or_mathematical_predicate_claim=True, copies_not_hardlinks=True)
    target = OUT / 'payload_staging_complete_1930_v1.json'
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=4)
    print(json.dumps({k: result[k] for k in ('status', 'snapshots', 'all_selected_files_checked', 'new_files', 'new_bytes')}), flush=True)


if __name__ == '__main__':
    main()
