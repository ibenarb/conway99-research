"""Materialize a proposal only. This program never starts workers or changes runs."""
from pathlib import Path
import hashlib
import json
from analyse import load, key, sha

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/memetik/lambda_plan_codex_20260922'
DATA = ROOT / 'docs/memetik/lambda_results_20260922'
CODE_COMMIT = 'b659cb8743dd6036d91dafb466b2d12cb21a29b0'
RESULT_COMMIT = '84c46aac2b39d718c44daee2a7b994c29930e6c5'


def seed(identity):
    data = json.dumps([2026092201, identity], separators=(',', ':')).encode()
    return int.from_bytes(hashlib.sha256(data).digest()[:8], 'big')


def main():
    endpoints = load(DATA / 'ENDPOINTS.json.gz')
    receipts = load(DATA / 'RECEIPTS.json')
    audit = load(DATA / 'AUDIT.json.gz')
    descents = load(OUT / 'POSTRUN_DESCENTS.json')
    founders = load(ROOT / 'experiments/memetik/lambda_compare_0_2_0/founders.json')
    selected = []
    for i in range(12):
        variants = ('P', 'TC') if i % 2 == 0 else ('TC', 'P')
        for variant in variants:
            name = f'{variant}--lambda-W-{i:02d}'
            selected.append({'id': name, 'variant': variant, 'target': 'W',
                             'replicate': i, 'seed': endpoints[name]['seed'],
                             'mode': 'resume_full_state_from_verified_private_copy',
                             'old_endpoint_budget_seconds': 3600,
                             'old_actual_cpu_seconds': receipts[name]['cpu_seconds'],
                             'new_endpoint_budget_seconds': 14400,
                             'new_authorization_cpu_seconds': 10800,
                             'milestones_cumulative_cpu_seconds': [3600, 7200, 10800, 14400],
                             'old_receipt': receipts[name], 'no_migration': True})
    starts = {}
    records = []
    for target, count in [('W', 6), ('Linf', 4), ('L1', 2)]:
        source = audit['observed_records_all_targets'][target]
        origin = source['candidate']
        item = descents[target] if target in descents else origin
        text, scores = item['graph6'], item['scores']
        worst = max(founders, key=lambda f: (key(f['scores'], target), f['state']))
        assert key(scores, target) < min(key(f['scores'], target) for f in founders)
        starts[target] = {'graph6': text, 'scores': scores, 'state': sha(text.encode()),
                          'family': origin['family'], 'line': origin['line'],
                          'canonical_class': 'compute with pinned pynauty during preparation',
                          'source_observed_job': f"{source['variant']}--lambda-{source['active_target']}-{source['replicate']:02d}",
                          'postrun_source': 'POSTRUN_DESCENTS.json#' + target if target in descents else 'AUDIT.json.gz#observed_records_all_targets/L1/candidate',
                          'replace_original_founder_state': worst['state'],
                          'replace_original_founder_line': worst['line'],
                          'retained_founder_states_in_original_order': [f['state'] for f in founders if f['state'] != worst['state']]}
        for i in range(count):
            records.append({'id': f'RECORD-P--lambda-{target}-{i:02d}', 'variant': 'P',
                            'target': target, 'replicate': i,
                            'seed': seed(['lambda-record', target, i]),
                            'mode': 'fresh_population_15_original_plus_one_target_record',
                            'start_spec': target, 'worker_cpu_seconds': 7200,
                            'milestones_cpu_seconds': [600, 1800, 3600, 7200],
                            'no_migration': True, 'scope': 'record pursuit; not a paired treatment test'})
    diagnostic = [
        {'id': 'clock-single', 'jobs': 1, 'cpu_seconds_each': 180},
        {'id': 'clock-18-workers', 'jobs': 18, 'cpu_seconds_each': 180},
        {'id': 'controls-and-preparation', 'jobs': 1, 'cpu_seconds_each': 900},
        {'id': 'TC-restart-archive-diagnosis', 'jobs': 12, 'cpu_seconds_each': 240,
         'seeds': [seed(['lambda-TC-diagnosis', i]) for i in range(12)]}
    ]
    assert sum(d['jobs'] * d['cpu_seconds_each'] for d in diagnostic) == 7200
    assert len(selected) == 24 and sum(j['new_authorization_cpu_seconds'] for j in selected) == 72 * 3600
    assert len(records) == 12 and sum(j['worker_cpu_seconds'] for j in records) == 24 * 3600
    assert set(j['seed'] for j in records).isdisjoint(j['seed'] for j in selected)
    proposal = {'version': 'lambda-next-codex-proposal-1.0.0', 'authorized_to_launch': False,
                'source_code_commit': CODE_COMMIT, 'result_commit': RESULT_COMMIT,
                'source_run_read_only': '/home/rb/conway99_workspace/ryzen_lambda_compare_020_20260921',
                'new_run_parent': '/home/rb/conway99_workspace/lambda_next_codex_1_0_0',
                'workers_max_global': 18, 'population_P': 16,
                'closing_reserve_in_worker_budget_seconds': 5,
                'diagnostic': diagnostic, 'continuation_jobs': selected,
                'record_starts': starts, 'record_jobs': records,
                'budget_cpu_hours': {'diagnostic': 2, 'continuation': 72, 'record': 24,
                                     'infrastructure_and_host_probes': 2, 'total_ceiling': 100},
                'schedule': 'Diagnostics first; first 18 continuation jobs; remaining 6 continuations then 12 record jobs. Global pool <=18.',
                'automatic_extension': False,
                'milestone_method': 'Do not change frozen task config; derive 7200/10800 best from cumulative curves with validation completion <= mark.',
                'comparison_primary': 'paired active (W,L1), P versus TC at 14400 cumulative budget seconds',
                'historical_budget_not_reused': True,
                'candidate_rules': 'independent full lambda verification and zero-residual solution handling retained',
                'fallback_P_only_cpu_hours': {'diagnostic': 2, 'continuation': 36, 'record': 24, 'infrastructure': 2, 'total_ceiling': 64}}
    (OUT / 'PROPOSED_MANIFEST.json').write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + '\n')
    rows = ['category\tid\ttarget\tseed\tnew_cpu_seconds']
    rows += [f"continuation\t{j['id']}\t{j['target']}\t{j['seed']}\t{j['new_authorization_cpu_seconds']}" for j in selected]
    rows += [f"record\t{j['id']}\t{j['target']}\t{j['seed']}\t{j['worker_cpu_seconds']}" for j in records]
    (OUT / 'PROPOSED_JOBS.tsv').write_text('\n'.join(rows) + '\n')
    print(json.dumps({'status': 'PROPOSED_NOT_LAUNCHED', 'jobs': len(selected) + len(records),
                      'budget': proposal['budget_cpu_hours'],
                      'record_replacements': {t: s['replace_original_founder_line'] for t, s in starts.items()}}, indent=2))


if __name__ == '__main__':
    main()
