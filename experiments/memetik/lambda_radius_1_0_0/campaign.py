"""Two fixed radius questions; complete lower-layer gates precede depth four."""
import boot
from support import *
from controller import Controller
from enumeration import EXPECTED


def complete(results, jobs):
    return len(results) == len(jobs) and all(r['status'] == 'DONE' for r in results.values())


def chunks(arm, depth, source, bounds, start, size=128):
    lo, hi, count = bounds
    if not count:
        return []
    input_hash = digest(source)
    jobs = []
    for begin in range(lo, hi + 1, size):
        end = min(hi, begin + size - 1)
        task = {'kind': 'expand', 'arm': arm, 'depth': depth, 'start': start,
                'input': str(source), 'input_sha256': input_hash, 'lo': begin, 'hi': end}
        jobs.append((f'd{depth}_{arm}_{begin:08d}', task, 'aux' if depth == 3 else arm))
    return jobs


def interleave(groups):
    return [group[i] for i in range(max(map(len, groups), default=0)) for group in groups if i < len(group)]


def summarize(run, jobs, results, starts):
    out = {}
    for arm in ('2076', '2077'):
        selected = [j for j in jobs if j[2] == arm]
        values = [results[n] for n, _, _ in selected if n in results]
        witnesses = [v['witness'] for v in values if v['status'] == 'FOUND']
        if witnesses:
            status = 'VERIFIED_IMPROVEMENT_DEPTH4'
        elif len(values) == len(selected) and all(v['status'] == 'DONE' for v in values):
            status = 'COMPLETE_NO_IMPROVEMENT_DEPTH4'
        else:
            status = 'INCOMPLETE'
        out[arm] = {'status': status, 'start_state': starts[arm]['state'],
                    'jobs_total': len(selected), 'jobs_completed': len(values),
                    'parents_completed': sum(v['parents'] for v in values),
                    'children_evaluated_in_completed_jobs': sum(v['children'] for v in values),
                    'witnesses': witnesses}
    return out


def campaign(run, host=None, test=False):
    c = Controller(run, host, test)
    starts = read(boot.HERE / 'STARTS.json')
    outcome = {'status': 'INCOMPLETE', 'phase': 'controls'}
    try:
        # Independent host/CPU sanity check uses measured wait4 time.
        clock_jobs = [('clock_probe', {'kind': 'spin', 'seconds': 1}, 'aux')]
        r = c.execute(clock_jobs, 'CLOCK', allocation=10)
        if not complete(r, clock_jobs):
            return outcome
        receipt = read(run / 'jobs/clock_probe/receipt.json')
        for row in receipt['sessions']:
            if row['cpu_seconds'] > row['host_elapsed'] * 1.02 + 0.1:
                raise RuntimeError('CPU exceeds independent host wall interval')
        jobs = [('controls', {'kind': 'controls'}, 'aux')]
        r = c.execute(jobs, 'CONTROLS', allocation=600)
        if not complete(r, jobs):
            return outcome
        print('RADIUS_CONTROLS_PASS', flush=True)
        jobs = [(f'prepare_{arm}', {'kind': 'prepare', 'arm': arm, 'start': starts[arm]}, 'aux') for arm in ('2076', '2077')]
        lower = c.execute(jobs, 'LOWER_LAYERS', allocation=300)
        if not complete(lower, jobs):
            return outcome
        groups = []
        for arm in ('2076', '2077'):
            d = run / 'jobs' / ('prepare_' + arm)
            source = d / 'lower.sqlite'
            if digest(source) != lower['prepare_' + arm]['lower_sha256']:
                raise RuntimeError('Lower-layer input hash mismatch')
            groups.append(chunks(arm, 3, source, lower['prepare_' + arm]['bounds'], starts[arm]))
        jobs3 = interleave(groups)
        atomic(run / 'DEPTH3_MANIFEST.json', jobs3)
        outcome['phase'] = 'depth3'
        r3 = c.execute(jobs3, 'DEPTH3', early_found=True, allocation=90)
        if not complete(r3, jobs3):
            found = [v for v in r3.values() if v['status'] == 'FOUND']
            if found:
                outcome.update(status='LOWER_DEPTH_COUNTEREXAMPLE', witnesses=found)
            return outcome
        gate = {}
        merges = []
        for arm in ('2076', '2077'):
            selected = [j for j in jobs3 if j[1]['arm'] == arm]
            parents = sum(r3[n]['parents'] for n, _, _ in selected)
            children = sum(r3[n]['children'] for n, _, _ in selected)
            if (parents, children) != EXPECTED[arm][1:]:
                raise RuntimeError('Depth-3 coverage/census mismatch')
            sources = [(str(run / 'jobs' / ('prepare_' + arm) / 'lower.sqlite'), lower['prepare_' + arm]['lower_sha256'])]
            sources += [(str(run / 'jobs' / n / 'work.sqlite'), digest(run / 'jobs' / n / 'work.sqlite')) for n, _, _ in selected]
            gate[arm] = {'parents': parents, 'children': children, 'improving': 0, 'status': 'COMPLETE_NO_IMPROVEMENT_DEPTH3'}
            merges.append(('merge_' + arm, {'kind': 'merge', 'arm': arm, 'sources': sources}, 'aux'))
        atomic(run / 'DEPTH3_VERIFIED.json', gate)
        print('RADIUS_DEPTH3_VERIFIED ' + json.dumps(gate), flush=True)
        merged = c.execute(merges, 'MERGE_AND_CALIBRATE', allocation=300)
        if not complete(merged, merges):
            return outcome
        groups = []
        for arm in ('2076', '2077'):
            counts = merged['merge_' + arm]['counts']
            if [counts[str(i)] if str(i) in counts else counts[i] for i in (0, 1, 2)] != [1, *EXPECTED[arm][:2]]:
                raise RuntimeError('Merged lower layers mismatch')
            groups.append(chunks(arm, 4, run / 'jobs' / ('merge_' + arm) / 'layers.sqlite',
                                 merged['merge_' + arm]['bounds'], starts[arm]))
        jobs4 = interleave(groups)
        atomic(run / 'DEPTH4_MANIFEST.json', jobs4)
        estimate = {}
        for arm in ('2076', '2077'):
            selected = [n for n, t, _ in jobs3 if t['arm'] == arm]
            cpu = sum(read(run / 'jobs' / n / 'receipt.json')['cpu_seconds'] for n in selected)
            n3 = merged['merge_' + arm]['bounds'][2]
            estimate[arm] = {'unique_depth3_states': n3, 'measured_depth3_cpu_seconds': cpu,
                             'rough_depth4_cpu_hours': cpu / EXPECTED[arm][1] * n3 / 3600,
                             'limit_cpu_hours': 20, 'note': 'projection; depth4 omits state inserts, overhead differs'}
        atomic(run / 'CALIBRATION.json', estimate)
        print('RADIUS_READY_DEPTH4 ' + json.dumps(estimate), flush=True)
        outcome['phase'] = 'depth4'
        r4 = c.execute(jobs4, 'DEPTH4', early_found=True, allocation=90)
        outcome['arms'] = summarize(run, jobs4, r4, starts)
        # A negative claim requires exact coverage of the entire L3 layer.
        for arm, row in outcome['arms'].items():
            if row['status'] == 'COMPLETE_NO_IMPROVEMENT_DEPTH4':
                if row['parents_completed'] != merged['merge_' + arm]['bounds'][2]:
                    raise RuntimeError('Negative claim lacks complete depth-3 coverage')
        outcome['status'] = 'FINISHED' if all(x['status'] != 'INCOMPLETE' for x in outcome['arms'].values()) else 'INCOMPLETE'
        return outcome
    except BaseException as error:
        outcome.update(status='DIAGNOSIS_REQUIRED', error=repr(error))
        raise
    finally:
        c.close()
        if c.stopping and c.stopping.startswith('WORKER_FAILED'):
            outcome['status'] = 'DIAGNOSIS_REQUIRED'
        outcome['reason'] = c.stopping
        outcome['cpu_seconds'] = c.state['used']
        outcome['host_wall_seconds'] = c.state['host_wall_seconds']
        if any(c.state['used'][k] > v for k, v in __import__('controller').LIMITS.items()):
            outcome['status'] = 'DIAGNOSIS_REQUIRED'
            outcome['error'] = 'CPU budget overrun'
        atomic(run / 'RESULT.json', outcome)
        atomic(run / 'status.json', outcome)
        print('RADIUS_RESULT ' + json.dumps(outcome), flush=True)
