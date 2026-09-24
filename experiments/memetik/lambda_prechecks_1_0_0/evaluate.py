"""Paired descriptive screening, same-origin V3 outcomes, no automatic inference."""
import boot
from util import *
from prepare import verify
from search import key
import statistics


def evaluate(run):
    plan = verify(run)
    results, cpu_total = {}, 0.0
    for job in plan['jobs']:
        d = run / job['directory']
        receipt = receipt_valid(d)
        result = read(d / 'result.json')
        if (receipt['status'] != 'COMPLETE'
                or result['endpoint_cpu_seconds'] != job['cumulative_budget_seconds']
                or receipt['budget_cpu_seconds'] > job['cumulative_budget_seconds']):
            raise RuntimeError('Incomplete or overrun task: ' + job['id'])
        sqlite_frozen(d / 'archive.sqlite')
        for candidate in [result['best'], *result['final_population'], *result['observed_best'].values()]:
            if checked(candidate['graph6'], 'lambda')[1] != candidate['scores']:
                raise RuntimeError('Score mismatch')
            if job['group'] == 'V3' and (candidate['family'] == 'HoG' or candidate['line'] != job['origin']):
                raise RuntimeError('Contaminated V3 lineage')
        for point in result['curves']:
            if checked(point['graph6'], 'lambda')[1] != point['scores']:
                raise RuntimeError('Curve score mismatch')
        results[job['id']] = result
        cpu_total += receipt['cpu_seconds']
    pairs = []
    for i in range(8):
        a, b = results[f'V1-{i:02d}-P'], results[f'V1-{i:02d}-PCesc']
        row = {'seed_index': i, 'P': a['best']['scores'], 'PCesc': b['best']['scores'],
               'delta_W_PCesc_minus_P': b['best']['scores']['W'] - a['best']['scores']['W'],
               'delta_L1_PCesc_minus_P': b['best']['scores']['L1'] - a['best']['scores']['L1'],
               'winner': 'PCesc' if key(b['best']['scores'], 'W') < key(a['best']['scores'], 'W') else
                         'P' if key(a['best']['scores'], 'W') < key(b['best']['scores'], 'W') else 'tie'}
        for arm, result in [('P', a), ('PCesc', b)]:
            row[arm + '_episodes_per_allocated_cpu_hour'] = result['episodes']
            row[arm + '_metrics'] = result['experiment_metrics']
            row[arm + '_isomorphic_return_histogram'] = result['histogram'].get('isomorphic_return', {})
        pairs.append(row)
    isolated = []
    for job in plan['jobs']:
        if job['group'] != 'V3':
            continue
        result = results[job['id']]
        isolated.append({'id': job['id'], 'origin': job['origin'], 'best': result['best']['scores'],
                         'initial_best': result['curves'][0]['scores'],
                         'positive_signal_W_below_2200': result['best']['scores']['W'] < 2200,
                         'curve_points': len(result['curves']), 'episodes': result['episodes'],
                         'archive_classes': result['archive_classes'],
                         'endpoint_classes': result['endpoint_classes']})
    ledger = read(run / 'auxiliary_ledger.json')
    aux = sum(e['cpu_seconds'] for e in ledger['entries'])
    if cpu_total > 32 * 3600 or aux > 7200:
        raise RuntimeError('Campaign CPU overrun')
    report = {'status': 'PRECHECKS_EVALUATED', 'jobs': 24,
              'search_cpu_hours': cpu_total / 3600, 'aux_cpu_hours_before_this_evaluation': aux / 3600,
              'V1_pairs': pairs, 'V1_median_delta_W': statistics.median(p['delta_W_PCesc_minus_P'] for p in pairs),
              'V1_wins': {arm: sum(p['winner'] == arm for p in pairs) for arm in ('P', 'PCesc', 'tie')},
              'V3': isolated,
              'interpretation': 'Exploratory screen; no universal operator rejection, basin exhaustion or existence inference.'}
    atomic(run / 'EVALUATION.json', report)
    return report
