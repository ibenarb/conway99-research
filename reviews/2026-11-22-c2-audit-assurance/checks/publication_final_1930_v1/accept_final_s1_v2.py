from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(BASE / 'recovery_v1'))
from resource_observer_v1 import measure, live


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    audit_id = load(BASE / 'singleton_v2/audit_identity_1900.json')
    assert not live(audit_id['identity']), 'Final auditor still running'
    controller = load(BASE / 'recovery_v1/controller_identity_v1.json')
    assert not live(controller['identity'])
    resource = measure([])
    assert max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20
    assert resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 39
    assert sha(BASE / 'recovery_v1/finished.json') == '06c6c6990ecf1808ef4aa528195c25d2576650fd12d4815441951208911f8fb5'
    assert json.loads((BASE / 'recovery_v1/finished.json').read_text()) == json.loads((BASE / 'recovery_v1/progress.json').read_text())
    assert sha(BASE / 'recovery_v1/progress.json') == 'ef55a00938bfe48627829744a536493896cd179fccf7e16838c72145eed172e4'
    plan_path = BASE / 'recovery_v1/recovery_plan_v1.json'
    assert sha(plan_path) == 'e3a6386b0c60d9e5c37f539563a31af6317f14e23bd78e92f39ec1aeb5e89fdc'
    plan = load(plan_path)
    assert len(plan['frozen_files']) == 32
    assert all(sha(BASE / name) == digest for name, digest in plan['frozen_files'].items())
    assert sha(BASE / 'recovery_v1/run_recovery_controller_v1.py') == 'c8685119a431f2ef9889a04fc76d52fb0bde185bcf08e91db94c459dbdaf2a9c'
    singleton = BASE / 'singleton_v2'
    report_path = singleton / 'audit_complete_1900_v1.json'
    report = load(report_path)
    previous = load(singleton / 'audit_snapshot_1744_v1.json')
    assert sha(singleton / 'audit_snapshot_1744_v1.json') == '848e84b913711e2f271be62d51256e68d8de173a3bdbd79f89a1a15fe3a402e1'
    assert report['status'] == 'SINGLETON_EVIDENCE_SNAPSHOT_PASS'
    assert report['full_S1_coverage'] is True
    assert report['frozen_original'] == 'd73a176f942b1fd67bac3b60c07d181487d84b66'
    assert report['total_charts'] == 3580 and report['search_required'] == report['audited_closed'] == 3308
    assert report['nonphysical_independently_checked'] == 272 and report['remaining'] == 0 and report['remaining_charts'] == []
    assert report['source_hashes'] == previous['source_hashes']
    assert report['unary_input_sha256'] == previous['unary_input_sha256']
    assert report['auditor_sha256'] == audit_id['auditor_sha256'] == sha(singleton / 'audit_singleton_evidence_v1.py') == '82ffe266b631aac9b1d39b6009e85a9349fe1cc3b4285f8d9ac9ef4726c32347'
    assert all(sha(singleton / name) == digest for name, digest in report['source_hashes'].items())
    manifest = load(singleton / 'jobs_manifest_v1.json')
    physical, nonphysical = set(manifest['search_charts']), set(manifest['nonphysical'])
    assert len(physical) == 3308 and len(nonphysical) == 272 and not physical & nonphysical
    assert physical | nonphysical == set(range(3580))
    rows = {row['chart']: row for row in report['checked']}
    assert len(rows) == len(report['checked']) == 3308 and set(rows) == physical
    old_rows = {row['chart']: row for row in previous['checked']}
    assert len(old_rows) == 2738 and all(rows[key] == row for key, row in old_rows.items())
    p = plan['families']['singleton']
    planned = set(map(int, p['completed'])) | {int(row['id']) for row in p['pending']} | {int(row['id']) for row in p['adopted']}
    assert planned == physical
    assert {int(path.name) for path in (singleton / 'jobs').iterdir()} == physical
    for chart, row in rows.items():
        result_path = singleton / 'jobs' / str(chart) / 'result.json'
        assert sha(result_path) == row['result_sha256']
        result = load(result_path)
        assert result['status'] == 'SECOND_SINGLETON_SOLVER_CLOSED' and result['chart'] == chart
        assert result['exit_code'] == 0 and result['roots_completed'] == result['roots_planned'] == row['orbit_representatives']
        assert result['setup']['raw_root_signs'] == row['raw_roots']
        assert result['setup']['attachments'] == row['attachments']
        assert row['full_input_readback'] is True and row['natural_exhaustion'] is True
        assert ' open 0 ' in result['final_line']
    totals = {key: sum(row[key] for row in rows.values()) for key in ['raw_roots', 'orbit_representatives', 'attachments', 'first_survivors', 'second_layer_calls']}
    assert totals['raw_roots'] == manifest['raw_root_signs']
    assert totals['first_survivors'] == totals['second_layer_calls'] == 0
    assert rows[183]['first_survivors'] == rows[3377]['first_survivors'] == 0
    assert (singleton / 'audit_1900_stderr.log').stat().st_size == 0
    log_end = json.loads((singleton / 'audit_1900_stdout.log').read_text().splitlines()[-1])
    assert all(log_end[key] == report[key] for key in ['status', 'full_S1_coverage', 'audited_closed', 'remaining', 'elapsed_seconds'])
    high_path = BASE / 'high_v1/audit_complete_1820_v2.json'
    assert sha(high_path) == '1f94173e7eabb8135d2849b626f0490273350abac864e5adf698b2558e895391'
    high = load(high_path)
    result = dict(at_utc=datetime.now(timezone.utc).isoformat(), status='FULL_S1_COVERAGE_AND_FINAL_REPORT_INDEPENDENTLY_ACCEPTED', source_sha256=sha(Path(__file__)), resource=resource, auditor_exited=True, stderr_empty=True, final_stdout_matches_report=True, frozen32files_unchanged=True, singleton=dict(audited=3308, nonphysical=272, total_charts=3580, full_S1_complete=True, audit_sha256=sha(report_path), old2738rows_and_bindings_retained=True, all3308planned_results_rebound=True, totals=totals, scope=report['scope']), high=dict(audited=3156, full_S2_complete=True, prior_acceptance_retained='recovery_v1/audit_acceptance_1831_v1.json'), low=dict(audited=92, prior_complete_audit_retained=True), no_second_layer_survivor_ledger_reproduction_claim=True, no_formal_search_correctness_or_third_solver_claim=True)
    with (OUT / 'final_s1_acceptance_v1.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=4)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
