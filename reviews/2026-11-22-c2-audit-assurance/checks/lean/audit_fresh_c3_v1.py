"""Post-run acceptance audit, separate from the C3 build/controller; no proof-source edits."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import tarfile

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
RAM = Path('/dev/shm/conway99_c3_assurance_20261122_v1')
REVISION = '9678dec98108003359cde7b404d57a6e09dd865c'
PERMITTED = {'propext', 'Quot.sound', 'Classical.choice'}
KERNELS = ['Lean paranoid', 'lean4lean', 'nanoda', 'con-leche', 'con-ron', 'Lean default']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def stream_hash(stream):
    result = hashlib.sha256()
    length = 0
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        result.update(block)
        length += len(block)
    return result.hexdigest(), length


def digest(path):
    with path.open('rb') as stream:
        return stream_hash(stream)[0]


def main():
    out = BASE / 'fresh_c3_acceptance_audit_v1.json'
    assert not out.exists(), 'Do not overwrite an acceptance record'
    controller = load(BASE / 'ram_lean_controller_result_v3.json')
    assert controller['status'] == 'ALL_FOUR_COMMAND_STAGES_PASSED_AUDIT_PENDING'
    assert [row['phase'] for row in controller['records']] == ['build', 'axioms', 'comparator', 'paranoid']
    assert all(row['exit_code'] == 0 for row in controller['records'])
    assert digest(BASE / 'run_ram_lean_phase_v3.py') == controller['source_sha256']
    pinned = [row for row in load(WORKSPACE / 'work/C3_Statuspruefung_20261122/source_manifest_v1.json')
              if row['path'].startswith('c3formal/')]
    assert len(pinned) == 28
    for row in pinned:
        local_name = row['path'][len('c3formal/'):]
        assert digest(BASE / 'c3formal' / local_name) == row['sha256']
        assert digest(RAM / local_name) == row['sha256']
    modules = sorted(row['path'][len('c3formal/'):-5].replace('/', '.')
                     for row in pinned if row['path'].endswith('.lean'))
    assert len(modules) == 24
    phases = {}
    for phase in ['build', 'axioms', 'comparator', 'paranoid']:
        report = load(BASE / f'ram_{phase}_result_v3.json')
        assert report['phase'] == phase and report['status'] == 'COMMANDS_PASSED'
        assert report['pinned_source_hashes_unchanged'] is True
        assert report['security_settings_changed'] is False
        assert all(row['exit_code'] == 0 for row in report['records'])
        phases[phase] = report
    build = phases['build']['records']
    assert len(build) == 25 and sorted(row['label'] for row in build[:-1]) == modules
    for row in build[:-1]:
        assert row['arguments'] == ['--no-cache', 'build', '+' + row['label']]
    assert build[-1]['arguments'] == ['--no-cache', 'build', 'C3formal', 'Challenge', 'Solution']
    check_source = (RAM / 'C3formal/Check.lean').read_text()
    required_axioms = re.findall(r'^#print axioms (\S+)', check_source, re.M)
    axioms_log = (BASE / 'ram_axioms_v3.stdout').read_text()
    axioms = re.findall(r"^'([^']+)' depends on axioms: \[([^\]]*)\]", axioms_log, re.M)
    assert len(axioms) == len(required_axioms) == 6
    assert {name for name, _ in axioms} == set(required_axioms)
    assert all(set(words.split(', ')) <= PERMITTED for _, words in axioms)
    assert 'C3.no_order3' in required_axioms
    config = load(RAM / 'comparator.json')
    assert len(config['theorem_names']) == 7 and len(set(config['theorem_names'])) == 7
    assert set(config['permitted_axioms']) == PERMITTED
    for phase, required in [('comparator', ['Lean default']), ('paranoid', KERNELS)]:
        record = phases[phase]['records']
        assert len(record) == 1
        expected_arguments = ['comparator'] + (['--paranoid'] if phase == 'paranoid' else [])
        assert record[0]['arguments'] == expected_arguments
        text = (BASE / f'ram_{phase}_v3.stdout').read_text()
        assert text.count('Your solution is okay!') == 1
        for kernel in required:
            assert text.count(kernel + ' kernel accepts the solution') == 1
        assert 'kernel rejected the solution' not in text
        assert 'Error while interacting with' not in text
        assert all(theorem in text for theorem in config['theorem_names'])
    archive_report = load(BASE / 'fresh_c3_build_archive_result_v1.json')
    assert archive_report['status'] == 'FRESH_BUILD_ARTIFACTS_PRESERVED_FULL_READBACK_PASS'
    archive_path = BASE / 'fresh_c3_build_artifacts_v1.tar.gz'
    assert digest(archive_path) == archive_report['archive_sha256']
    assert archive_path.stat().st_size == archive_report['archive_bytes']
    entries = archive_report['files']
    expected = {row['path']: row for row in entries}
    assert len(expected) == len(entries) > 0
    seen = set()
    with tarfile.open(archive_path, 'r:gz') as archive:
        for member in archive:
            assert member.isfile() and member.name in expected and member.name not in seen
            with archive.extractfile(member) as stream:
                actual, size = stream_hash(stream)
            assert actual == expected[member.name]['sha256']
            assert size == expected[member.name]['bytes']
            seen.add(member.name)
    assert seen == set(expected)
    assert sum(row['bytes'] for row in entries) == archive_report['uncompressed_bytes']
    for module in modules:
        assert 'lib/lean/' + module.replace('.', '/') + '.olean' in expected
    evidence = [f'ram_{phase}_{suffix}' for phase in phases
                for suffix in ['result_v3.json', 'v3.stdout', 'v3.stderr']]
    evidence += ['ram_lean_controller_result_v3.json', 'fresh_c3_build_archive_result_v1.json',
                 'fresh_c3_build_artifacts_v1.tar.gz', 'log_history_evidence_v1.json',
                 'LOG_HASH_HISTORY_NOTE_v1.txt', 'audit_fresh_c3_v1.py']
    report = {
        'status': 'FRESH_C3_BUILD_SIX_KERNELS_STATEMENT_MATCH_AND_ARCHIVE_PASS',
        'recorded_utc': datetime.now(timezone.utc).isoformat(), 'source_revision': REVISION,
        'pinned_files_verified': len(pinned), 'fresh_project_modules': len(modules),
        'theorems_compared': config['theorem_names'], 'paranoid_kernels_accepted': KERNELS,
        'axioms': {name: words.split(', ') for name, words in axioms},
        'archive_members_fully_reread': len(entries), 'archive_sha256': archive_report['archive_sha256'],
        'evidence_sha256': {name: digest(BASE / name) for name in evidence},
        'dependencies': 'Pinned official dependency caches used; all project proof modules rebuilt. This is not a rebuild of every Mathlib module.',
        'historical_logs': 'Five historical mismatches were already present at their first Git commits. The pre-commit cause remains unknown; neither sources nor original SHA256SUMS were changed.',
        'scope': 'Full C3 exclusion, including actions with fixed points. This is neither C2 completion nor graph nonexistence.',
        'security_settings_changed': False}
    with out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=4)
    print(json.dumps({k: v for k, v in report.items() if k != 'evidence_sha256'}))


if __name__ == '__main__':
    main()
