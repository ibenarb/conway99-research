from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
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


def save(path, obj):
    path.write_text(json.dumps(obj, indent=4, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    publication = load(OUT / 'git_publication_complete_v1.json')
    remote = load(OUT / 'remote_acceptance_v1.json')
    assert publication['status'] == 'BOTH_AUTHORIZED_REPOSITORIES_PUBLISHED_AND_REMOTE_HEADS_VERIFIED'
    assert remote['status'] == 'BOTH_REMOTE_HEADS_INDEPENDENTLY_RECONFIRMED'
    assert publication['private_full_singleton_cases'] == 3308 and publication['private_full_high_cases'] == 3156 and publication['private_full_low_cases'] == 92
    assert not live(load(OUT / 'git_publish_identity_v1.json')['identity'])
    resource = measure([])
    assert max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20
    assert resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 39
    for directory, branch, field in [('git-assurance', 'review/project/c2-assurance-20261122', 'private_commit'), ('git-research', 'main', 'public_commit')]:
        repo = ROOT / directory
        args = ['git', '-c', 'safe.directory=' + repo.as_posix(), '-C', str(repo)]
        assert subprocess.check_output(args + ['rev-parse', 'HEAD']).decode().strip() == publication[field]
        assert not subprocess.check_output(args + ['status', '--porcelain']).strip()
    accepted = load(OUT / 'final_s1_acceptance_v1.json')
    assert sha(BASE / 'singleton_v2/audit_complete_1900_v1.json') == accepted['singleton']['audit_sha256']
    old = load(DOSSIER / 'CHECKS_MANIFEST.json')
    old_rows = {row['path']: row for row in old['files']}
    p = load(BASE / 'progress.json')
    p['updated_utc'] = datetime.now(timezone.utc).isoformat()
    p['completion'] = dict(status='ALL_FIVE_ASSURANCE_CHECKS_AND_MATCHING_GIT_EVIDENCE_COMPLETE', counts=dict(singleton=3308, nonphysical=272, high=3156, low=92), final_s1_acceptance='publication_final_1930_v1/final_s1_acceptance_v1.json', scope='Completion within explicitly documented implementation, classification and historical-provenance dependencies.', remaining_research=[], final_publication_receipts_being_sealed=True)
    p['git'].update(private_commit=publication['private_commit'], public_commit=publication['public_commit'], remote_readback_verified_utc=remote['at_utc'], receipt='publication_final_1930_v1/remote_acceptance_v1.json')
    p['evidence_packaging'].update(current_local_audited=dict(singleton=3308, high=3156, low=92), full_job_payloads_in_git=dict(singleton=3308, high=3156, low=92), expanded_audit_receipts_in_git=True, remaining_payloads='None. All full job payloads, final audits and scope statements remotely verified. Final publication receipts sealed in this closing commit.')
    p['git_publication_progress'].update(status='BOTH_AUTHORIZED_REPOSITORIES_REMOTELY_VERIFIED_CLOSING_RECEIPTS', publication_pending=False, publisher_live=False)
    p['git_documentation_pending_after_active_publisher'] = False
    p['publication_receipts_to_include_with_next_snapshot'] = []
    p['running_evidence_audits'] = {}
    p['active_recovery_controller'] = None
    p['active_recovery_progress'] = None
    p['last_announced_verified_counts'] = dict(singleton=3308, high=3156, low=92)
    p['evidence_audit_admission'].update(status='ALL_FIVE_CHECKS_COMPLETE_AND_PUBLISHED', next='No additional research. Pause the authorized heartbeat after remote confirmation of the closing receipt commit.')
    for task in p['tasks']:
        task['next'] = 'Assurance and Git evidence complete within stated scope. No rerun absent changed source or finding; future manuscript integration is editorial.'
    for family in ['singleton', 'high', 'low']:
        p[family + '_snapshot']['note'] = 'All searches and independent evidence audits complete; full payloads remotely verified.'
    save(BASE / 'progress.json', p)
    shutil.copy2(BASE / 'progress.json', CHECKS / 'progress.json')
    shutil.copy2(BASE / 'progress.json', DOSSIER / 'progress.json')
    for source in sorted(OUT.iterdir()):
        if not source.is_file():
            continue
        destination = CHECKS / OUT.name / source.name
        assert not source.is_symlink()
        digest = sha(source)
        if destination.exists():
            assert sha(destination) == digest, destination
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        assert sha(destination) == digest
    rows = {}
    for path in sorted(CHECKS.rglob('*')):
        if path.is_file():
            assert not path.is_symlink()
            name = path.relative_to(CHECKS).as_posix()
            rows[name] = dict(path=name, bytes=path.stat().st_size, sha256=sha(path))
    assert set(old_rows).issubset(rows)
    changed = [name for name in old_rows if rows[name] != old_rows[name]]
    assert changed == ['progress.json'], changed
    ordered = [rows[row['path']] for row in old['files']] + [rows[name] for name in sorted(set(rows)-set(old_rows))]
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), count=len(ordered), total_bytes=sum(row['bytes'] for row in ordered), files=ordered)
    save(DOSSIER / 'CHECKS_MANIFEST.json', manifest)
    receipt = dict(status='FINAL_CLOSING_MANIFEST_FULL_READBACK_PASS', at_utc=datetime.now(timezone.utc).isoformat(), count=len(ordered), total_bytes=manifest['total_bytes'], manifest_sha256=sha(DOSSIER / 'CHECKS_MANIFEST.json'), previous_entries_verified_unchanged=len(old_rows)-1, previous_entries_updated=['progress.json'], counts=dict(singleton=3308, nonphysical=272, high=3156, low=92), all_final_audits_and_main_publication_receipts_preserved=True)
    save(DOSSIER / 'CHECKS_MANIFEST_READBACK.json', receipt)
    summary = dict(status='ALL_FIVE_ASSURANCE_CHECKS_COMPLETE_WITH_DOCUMENTED_SCOPE', at_utc=datetime.now(timezone.utc).isoformat(), frozen_c2=p['accepted_c2_revision'], frozen_c3=p['c3_revision'], final_s1_acceptance=accepted, verified_evidence_commit=publication['private_commit'], verified_public_status_commit=publication['public_commit'], final_manifest_readback=receipt, scope_limitations=[task['result'] for task in p['tasks']], remaining_research=[], automation='Pause after this closing receipt commit has been pushed and independently verified.', receipt_boundary='This closing commit contains all main publication receipts and uses Git content addressing for its own identity; its own post-push acknowledgement is retained locally, avoiding recursive self-referential manifests.')
    save(DOSSIER / 'FINAL_COMPLETION.json', summary)
    save(OUT / 'closing_manifest_readback_v1.json', dict(**receipt, resource=resource))
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
