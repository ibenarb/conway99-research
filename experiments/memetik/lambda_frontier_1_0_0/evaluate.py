"""Fixed W threshold; no post hoc substitution by other norm records."""
import boot
from util import *
from prepare import verify
import statistics


def decision(count):
    return ('PAUSE_W_FRONTIER' if count == 0 else 'SINGLE_SIGNAL_REVIEW_ONLY'
            if count == 1 else 'REPEATED_SIGNAL_REVIEW_ONLY')


def evaluate(run):
    plan = verify(run)
    rows, cache, successful_classes, successful_states = [], {}, set(), set()
    cpu_total = 0
    for job in plan['jobs']:
        d = run / job['directory']
        receipt = receipt_valid(d)
        result = read(d / 'result.json')
        if (receipt['status'] != 'COMPLETE'
                or result['endpoint_cpu_seconds'] != job['cumulative_budget_seconds']
                or receipt['budget_cpu_seconds'] > job['cumulative_budget_seconds']):
            raise RuntimeError('Incomplete/overrun task: ' + job['id'])
        sqlite_frozen(d / 'archive.sqlite')
        candidates = [result['best'], *result['final_population'], *result['observed_best'].values()]
        for c in [*candidates, *result['curves']]:
            if c['graph6'] not in cache:
                cache[c['graph6']] = checked(c['graph6'], 'lambda')[1]
            if cache[c['graph6']] != c['scores']:
                raise RuntimeError('Score mismatch')
        if any(c['family'] != 'HoG' for c in candidates):
            raise RuntimeError('Unexpected ancestry')
        best = result['best']
        graph, _ = checked(best['graph6'], 'lambda')
        if core.canonical(graph) != best['class'] or sha(best['graph6'].encode()) != best['state']:
            raise RuntimeError('Best identity mismatch')
        success = best['scores']['W'] < 2096
        if success:
            successful_classes.add(best['class'])
            successful_states.add(best['state'])
        cpu_total += receipt['cpu_seconds']
        first = next((p['cpu'] for p in result['curves'] if p['scores']['W'] < 2096), None)
        rows.append({'id': job['id'], 'seed': job['seed'], 'start_W': job['frontier_W'],
                     'best': best['scores'], 'delta_W': best['scores']['W'] - job['frontier_W'],
                     'success': success, 'first_record_cpu_seconds': first,
                     'last_record_cpu_seconds': result['curves'][-1]['cpu'],
                     'class': best['class'], 'state': best['state'],
                     'cpu_seconds': receipt['cpu_seconds'],
                     'observed_norm_records': {k: c['scores'] for k, c in result['observed_best'].items()}})
    aux = sum(e['cpu_seconds'] for e in read(run / 'auxiliary_ledger.json')['entries'])
    if cpu_total > 115200 or aux > 3600:
        raise RuntimeError('Campaign CPU overrun')
    successes = sum(p['success'] for p in rows)
    report = {'status': 'FRONTIER_EVALUATED', 'jobs': rows, 'successful_jobs': successes,
              'successful_endpoint_classes': len(successful_classes),
              'successful_endpoint_states': len(successful_states), 'decision': decision(successes),
              'search_cpu_hours': cpu_total / 3600, 'aux_cpu_hours_before_this_evaluation': aux / 3600,
              'median_W_by_bank': {str(w): statistics.median(p['best']['W'] for p in rows if p['start_W'] == w)
                                   for w in (2096, 2101)},
              'verified_distinct_graphs': len(cache), 'automatic_extension': False,
              'interpretation': 'Repeated hits may converge to the same class; neither superiority nor exhaustion proof.'}
    atomic(run / 'EVALUATION.json', report)
    return report
