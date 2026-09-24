"""Fixed endpoint criteria, complete receipts, and immutable V3 curve prefixes."""
import boot
from util import *
from prepare import verify
import statistics


def evaluate(run):
    plan = verify(run)
    v2, v3 = [], []
    cpu_total = 0
    cache = {}
    for job in plan['jobs']:
        d = run / job['directory']
        receipt = receipt_valid(d)
        result = read(d / 'result.json')
        if (receipt['status'] != 'COMPLETE'
                or result['endpoint_cpu_seconds'] != job['cumulative_budget_seconds']
                or receipt['budget_cpu_seconds'] > job['cumulative_budget_seconds']):
            raise RuntimeError('Incomplete/overrun task: ' + job['id'])
        sqlite_frozen(d / 'archive.sqlite')
        for c in [result['best'], *result['final_population'], *result['observed_best'].values(), *result['curves']]:
            if c['graph6'] not in cache:
                cache[c['graph6']] = checked(c['graph6'], 'lambda')[1]
            if cache[c['graph6']] != c['scores']:
                raise RuntimeError('Score mismatch')
        used = receipt['cpu_seconds'] - job['initial_actual_cpu']
        if not 0 <= used <= job['additional_cpu_seconds']:
            raise RuntimeError('Additional CPU overrun')
        cpu_total += used
        row = {'id': job['id'], 'best': result['best']['scores'], 'additional_cpu_seconds': used}
        if job['group'] == 'V2':
            row.update(start_W=job['frontier_W'], delta_W=result['best']['scores']['W'] - job['frontier_W'])
            v2.append(row)
        else:
            base = run / 'baseline' / job['id']
            old = read(base / 'result.json')
            original_receipt = read(base / 'receipt.json')
            original_task = read(base / 'task.json')
            if result['curves'][:len(old['curves'])] != old['curves']:
                raise RuntimeError('Historical curves changed')
            if any(result['milestones'][k] != v for k, v in old['milestones'].items()):
                raise RuntimeError('Historical milestones changed')
            if receipt['sessions'][:len(original_receipt['sessions'])] != original_receipt['sessions']:
                raise RuntimeError('Historical receipts changed')
            if any(c['family'] == 'HoG' or c['line'] != original_task['origin']
                   for c in [result['best'], *result['final_population'], *result['observed_best'].values()]):
                raise RuntimeError('Contaminated V3 lineage')
            row.update(origin=original_task['origin'], W_at_2h=old['best']['scores']['W'],
                       delta_W=result['best']['scores']['W'] - old['best']['scores']['W'])
            v3.append(row)
    aux = sum(e['cpu_seconds'] for e in read(run / 'auxiliary_ledger.json')['entries'])
    if cpu_total > 216000 or aux > 7200:
        raise RuntimeError('Campaign CPU overrun')
    positive2 = any(v['best']['W'] < 2102 for v in v2)
    positive3 = any(v['best']['W'] < 2150 for v in v3)
    report = {'status': 'DECISION_EVALUATED', 'jobs': 14, 'V2': v2, 'V3': v3,
              'V2_positive': positive2, 'V3_positive': positive3,
              'V2_median_W': statistics.median(v['best']['W'] for v in v2),
              'V3_median_W': statistics.median(v['best']['W'] for v in v3),
              'additional_search_cpu_hours': cpu_total / 3600,
              'aux_cpu_hours_before_this_evaluation': aux / 3600,
              'verified_distinct_graphs': len(cache),
              'decision': 'REVIEW_SIGNAL_BEFORE_ANY_FURTHER_RUN' if positive2 or positive3 else 'PAUSE_CURRENT_STRATEGY',
              'interpretation': 'Single hits are continuation signals, not family superiority; negative is no exhaustion proof.'}
    atomic(run / 'EVALUATION.json', report)
    return report
