from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = BASE.parents[1]
DOSSIER = ROOT / 'git-assurance/reviews/2026-11-22-c2-audit-assurance'
CHECKS = DOSSIER / 'checks'
sys.path.insert(0, str(BASE / 'recovery_v1'))
from resource_observer_v1 import measure, live


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=4, ensure_ascii=False) + '\n', encoding='utf-8')


def copy_verified(source, destination):
    before = source.stat()
    digest = sha(source)
    if destination.exists():
        assert sha(destination) == digest, destination
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    assert sha(destination) == digest and destination.stat().st_size == before.st_size
    after = source.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)


def main():
    staging = load(OUT / 'payload_staging_complete_1930_v1.json')
    assert staging['status'] == 'AUDITED_SNAPSHOT_PAYLOADS_COPIED_AND_FULL_READBACK_PASS'
    accepted = load(OUT / 'final_s1_acceptance_v1.json')
    assert accepted['singleton']['audited'] == 3308 and accepted['singleton']['full_S1_complete'] and accepted['high']['audited'] == 3156 and accepted['high']['full_S2_complete']
    controller = load(BASE / 'recovery_v1/controller_identity_v1.json')
    assert not live(controller['identity'])
    assert sha(BASE / 'recovery_v1/finished.json') == '06c6c6990ecf1808ef4aa528195c25d2576650fd12d4815441951208911f8fb5'
    resource = measure([])
    assert max(row['system_busy_cpu'] for row in resource['intervals']) + 1 <= 20
    assert resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 39
    save(OUT / 'manifest_admission_v1.json', resource)
    old_manifest = load(DOSSIER / 'CHECKS_MANIFEST.json')
    old_rows = {row['path']: row for row in old_manifest['files']}
    assert len(old_rows) == len(old_manifest['files']) == 44737
    p = load(BASE / 'progress.json')
    p['updated_utc'] = datetime.now(timezone.utc).isoformat()
    p['running_evidence_audits'] = {}
    p.pop('pending_accepted_audit', None)
    p.pop('pending_audit_acceptance', None)
    p['active_evidence_admission'].update(status='COMPLETED_FINAL_S1_ACCEPTED', live=False, next='Finite waiter and final auditor completed; no restart.')
    p['evidence_audit_admission'].update(status='ALL_FIVE_CHECKS_ACCEPTED_FINAL_PUBLICATION_PENDING', next='Publish complete S1 payloads, final acceptance and completion scope; verify both remote refs.')
    p['latest_resource'] = resource
    p['latest_control_record'] = 'publication_final_1930_v1/final_s1_acceptance_v1.json'
    p['latest_integrity_record'] = p['latest_control_record']
    p['evidence_packaging'].update(current_local_audited=dict(singleton=3308, high=3156, low=92), expanded_audit_receipts_in_git=False, remaining_payloads='All3308singleton/3156high/92low complete payloads assembled and fully read back locally; final S1 publication pending. Previous2738/3156/92 remains remote-confirmed.')
    p['git_publication_progress'] = dict(status='PREPARED_ALL_FIVE_CHECKS_FINAL_PUBLICATION_PENDING', publication_pending=True, publisher_live=False, directory='publication_final_1930_v1', completion_receipt='publication_final_1930_v1/git_publication_complete_v1.json', matching_payload_counts=dict(singleton=3308, high=3156, low=92))
    p['active_recovery_controller'] = None
    p['recovery_terminal_receipt'] = 'recovery_v1/finished.json'
    p['publication_receipts_to_include_with_next_snapshot'] = ['publication_final_1930_v1/git_publication_complete_v1.json']
    p['git_documentation_pending_after_active_publisher'] = True
    for task in p['tasks']:
        if task['id'] == 'S1':
            task['status'] = 'FULL_SINGLETON_SEARCH_AND_COVERAGE_AUDIT_COMPLETE'
            task['result'] = 'All3580charts reconciled:3308physical searches naturally exhaust and272nonphysical cases independently reconstructed. Exact unary roots and full stabilizer orbits, input/output byte readbacks, source/result bindings and complete ROOT/FINAL transcripts pass. All cases close under stronger exact first-layer conditions, including original second-layer cases183/3377. No reproduction of the original second-layer survivor ledger is claimed. Attachment completeness and search predicate validity retain separately documented implementation/review dependencies.'
            task['next'] = 'Publish final full payloads and acceptance; no research rerun absent changed source or finding.'
            task['latest_evidence_audit'] = 'singleton_v2/audit_complete_1900_v1.json; full3308/3308physical plus272nonphysical, zero remaining; independently accepted in publication_final_1930_v1/final_s1_acceptance_v1.json.'
            task['totals'] = accepted['singleton']['totals']
        if task['id'] == 'S2':
            assert task['status'] == 'FULL_SECOND_HIGH_SOLVER_AND_COVERAGE_AUDIT_COMPLETE'
    cp = load(BASE / 'recovery_v1/progress.json')
    assert not cp['failures']
    for family in ('high', 'low', 'singleton'):
        row = cp['families'][family]
        p[family + '_snapshot'] = dict(raw_closed=row['closed'], active=len(row['active']), pending_not_started=row['pending'], at_utc=cp['updated_utc'], note='All research naturally ended and all3308singleton/3156high/92low independently accepted within disclosed scopes; final Git publication pending.')
    temporary = BASE / 'progress_1930.tmp'
    assert not temporary.exists()
    save(temporary, p)
    temporary.replace(BASE / 'progress.json')
    for target in (CHECKS / 'progress.json', DOSSIER / 'progress.json'):
        shutil.copy2(BASE / 'progress.json', target)
        assert sha(target) == sha(BASE / 'progress.json')
    for directory in ['publication_1833_v1', 'final_s1_admission_1900_v1']:
        for source in sorted((BASE / directory).iterdir()):
            if source.is_file():
                copy_verified(source, CHECKS / directory / source.name)
    for family, package in [('singleton_v2', 'singleton_v2')]:
        for name in ['audit_identity_1900.json', 'audit_1900_stdout.log', 'audit_1900_stderr.log']:
            copy_verified(BASE / family / name, CHECKS / package / name)
    for name in ['control_1842_v1.json', 'control_1857_v1.json', 'finished.json']:
        copy_verified(BASE / 'recovery_v1' / name, CHECKS / 'recovery_v1' / name)
    for source in sorted(OUT.iterdir()):
        if source.is_file():
            copy_verified(source, CHECKS / OUT.name / source.name)
    stamp = datetime.now().strftime('%H:%M')
    totals = accepted['singleton']['totals']
    paragraph = f"23 November, {stamp} CET: all five supplementary assurance checks are complete within their documented scopes. Final S1 coverage is 3,580 charts: all 3,308 physical searches naturally exhaust, and all 272 nonphysical cases are independently reconstructed. The final separate auditor reconstructs {totals['raw_roots']:,} exact admissible root signs and {totals['orbit_representatives']:,} orbit representatives, checks input/output bytes and complete ROOT/FINAL transcripts, and the final acceptance rebinds every result to its planned chart and frozen sources. There are no remaining or open searches and no audit failures. Every case closes under the stronger exact first-layer conditions, including original second-layer cases 183 and 3377; no independent reproduction of the original second-layer survivor ledger or empirical validation of an unused branch is claimed. Attachment completeness and search predicate validity retain their separately documented implementation/review dependencies. S2 covers all 3,156 high-rank jobs and S3 all 92 low-rank chart/parities. S4 combines the completed finite certificate checks with the disclosed Conway-Sloane classification and mass argument; its shared PARI backend remains disclosed. S5 is a fresh build of the pinned C3 project using pinned Mathlib cache, not a full Mathlib rebuild; the five historical log-hash mismatches predate their first commits, and their pre-commit cause remains unknown. These checks add assurance to the C2 involution exclusion, not a graph nonexistence proof, journal acceptance, or formal verification of the entire computation. Full evidence and acceptance are preserved in the private review repository; this public status is published only after its matching private commit has been pushed and verified."
    for path in [ROOT / 'git-research/docs/c2/AUDIT_AND_ASSURANCE_2026-11-22.md', DOSSIER / 'STATUS_AND_PLAN.md']:
        text = path.read_bytes().decode('utf-8')
        lines = text.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith('| ID |'):
                assert '18:33 CET' in line
                lines[index] = line.replace('18:33 CET', stamp + ' CET')
            elif line.startswith('| S1 |'):
                assert '2,738' in line and '570' in line
                columns = line.split('|')
                assert len(columns) == 5
                columns[3] = ' Completed: all 3,308 physical searches naturally exhausted plus 272 independently reconstructed nonphysical cases, covering all 3,580 charts. Exact unary roots, full stabilizer orbits, source/result bindings, complete input/output readbacks and exhaustive transcripts pass, with no open or remaining case. Stronger first-layer conditions close every case, including original second-layer cases 183/3377. The original second-layer survivor ledger is not independently reproduced. Attachment completeness and search predicate validity retain separately documented implementation/review dependencies. Full payloads and final acceptance are retained privately. '
                lines[index] = '|'.join(columns)
            elif line.startswith('| S2 |'):
                assert '3,156' in line and 'Completed' in line
        assert paragraph not in text
        path.write_bytes((''.join(lines).rstrip() + '\r\n\r\n' + paragraph + '\r\n').encode('utf-8'))
    files = sorted(path for path in CHECKS.rglob('*') if path.is_file())
    rows = {}
    for path in files:
        assert not path.is_symlink()
        relative = path.relative_to(CHECKS).as_posix()
        rows[relative] = dict(path=relative, bytes=path.stat().st_size, sha256=sha(path))
    assert set(old_rows).issubset(rows)
    changed = [name for name in old_rows if old_rows[name] != rows[name]]
    assert changed == ['progress.json'], changed
    ordered = [rows[row['path']] for row in old_manifest['files']]
    ordered += [rows[name] for name in sorted(set(rows) - set(old_rows))]
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), files=ordered, count=len(ordered), total_bytes=sum(row['bytes'] for row in ordered))
    save(DOSSIER / 'CHECKS_MANIFEST.json', manifest)
    assert len(set(row['path'] for row in ordered)) == len(files)
    assert {row['path'] for row in ordered} == {path.relative_to(CHECKS).as_posix() for path in files}
    receipt = dict(status='EXACT_FILESET_AND_FULL_SHA256_READBACK_PASS', created_utc=datetime.now(timezone.utc).isoformat(), files=len(files), bytes=manifest['total_bytes'], manifest_sha256=sha(DOSSIER / 'CHECKS_MANIFEST.json'), previous_entries_verified_unchanged=len(old_rows)-1, previous_entries_updated=['progress.json'], full_snapshot_counts=dict(singleton=3308, high=3156, low=92), does_not_claim_remote_publication=True)
    save(OUT / 'manifest_readback_v1.json', receipt)
    save(DOSSIER / 'CHECKS_MANIFEST_READBACK.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
