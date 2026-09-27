"""Controls, charged calibration and round-robin fixed-length profile."""
import boot
from support import *
from controller import Controller
from settings import *
from episodes import database
from collections import deque


def jobs_for(starts):
    return [(f'{a}_k{k:02d}', {'kind': 'profile', 'arm': a, 'k': k, 'n': N, 'start': starts[a]},
             f'{a}_k{k:02d}') for k in LENGTHS for a in ARMS]


def snapshot(c, name, task):
    directory = c.job(name, task)
    if not (directory / 'receipt.json').exists():
        return {'next': 0, 'episode': None, 'solution': False}
    c.done(directory)  # verifies task/result/checkpoint receipts, also for paused slices
    db = connect(directory / 'work.sqlite', True)
    p = meta(db, 'progress', {'next': 0, 'episode': None, 'solution': False})
    count = db.execute('SELECT count(*) FROM episodes').fetchone()[0]
    db.close()
    if count != p['next']:
        raise RuntimeError('EPISODE_COVERAGE_MISMATCH')
    return p


def execute_profile(c, jobs, goal, phase):
    c.phase = phase
    c.phase_started = c.host.last['host_seconds']
    c.phase_initial_done = 0
    c.profile_goal = goal
    c.profile_initial_episodes = sum(snapshot(c, n, t)['next'] for n, t, _ in jobs)
    pending = deque(jobs)
    results = {}
    while pending or c.active:
        c.monitor()
        for e, result in c.reap():
            task = read(e['directory'] / 'task.json')
            if not c.stopping:
                pending.append((e['name'], task, e['category']))
        for pid, entry in c.active.items():
            if c.stopping:
                if entry['sent'] is None:
                    os.kill(pid, signal.SIGTERM)
                    entry['sent'] = c.host.last['host_seconds']
                elif c.host.last['host_seconds'] - entry['sent'] > 10:
                    os.kill(pid, signal.SIGKILL)
        while pending and not c.stopping and len(c.active) < c.max_workers:
            name, task, category = pending.popleft()
            p = snapshot(c, name, task)
            if p['solution']:
                c.stopping = 'VERIFIED_SRG_SOLUTION'
                break
            if p['next'] >= goal:
                results[name] = {'status': 'DONE', 'completed': p['next']}
                continue
            cap = min(180, c.remaining(category) - 10)
            if cap < 6:
                results[name] = {'status': 'INCOMPLETE', 'completed': p['next'], 'reason': 'CELL_CPU_LIMIT'}
                continue
            if not c.spawn(name, c.run / 'jobs' / name, category, cap):
                raise RuntimeError('UNEXPECTED_RESERVATION_FAILURE')
        c.report(jobs, results)
        if c.stopping and not c.active:
            break
        if pending or c.active:
            time.sleep(0.1)
    c.report(jobs, results, True)
    return results


def summarize(c, jobs):
    cells = {}
    for name, task, category in jobs:
        d = c.run / 'jobs' / name
        if not (d / 'receipt.json').exists():
            cells[name] = {'status': 'INCOMPLETE', 'completed': 0}
            continue
        p = snapshot(c, name, task)
        db = connect(d / 'work.sqlite', True)
        values = [json.loads(row[0]) for row in db.execute('SELECT value FROM episodes ORDER BY idx')]
        db.close()
        if [v['index'] for v in values] != list(range(len(values))):
            raise RuntimeError('NONCONTIGUOUS_EPISODE_INDICES')
        n = len(values)
        improve = [v for v in values if v['improved']]
        counted_cpu = sum(v['episode_cpu_seconds'] for v in values)
        cpubudget = c.state['used'][category]
        if counted_cpu > cpubudget + 0.1:
            raise RuntimeError('EPISODE_CPU_EXCEEDS_WAIT4')
        cells[name] = {'status': 'COMPLETE' if n == task['n'] else 'INCOMPLETE', 'completed': n,
                      'target': task['n'], 'returned': sum(v['returned'] for v in values),
                      'isomorphic_return': sum(v['isomorphic_return'] for v in values),
                      'return_rate': sum(v['returned'] for v in values) / n if n else None,
                      'improvement_rate': len(improve) / n if n else None,
                      'cpu_per_completed_episode': cpubudget / n if n else None,
                      'cpu_per_improved_endpoint': cpubudget / len(improve) if improve else None,
                      'improved': len(improve), 'improving_classes': len({v['class'] for v in improve}),
                      'improving_blocks': sorted({v['block'] for v in improve}),
                      'global_W_records': sum(v['global_W_record'] for v in values),
                      'solution': any(v['solution'] for v in values),
                      'end_classes': len({v['class'] for v in values}),
                      'near_other_classes': len({v['class'] for v in values if v['class'] != task['start']['class']
                                                 and v['scores']['W'] <= task['start']['scores']['W'] + 2}),
                      'best_endpoint': min((v['scores'] for v in values), key=key, default=None),
                      'charged_cpu_seconds': cpubudget, 'measured_complete_phase_cpu_seconds': counted_cpu,
                      'measured_return_phase_cpu_seconds': sum(v['episode_cpu_seconds'] for v in values if v['returned']),
                      'other_cpu_including_checkpoint_startup_and_censoring': cpubudget - counted_cpu,
                      'censored_episode': p['episode'],
                      'zero_hit_upper95_iid': 1 - .05 ** (1 / n) if n and not improve else None}
        with (d / 'episodes.jsonl').open('w') as stream:
            for value in values:
                stream.write(json.dumps(value, separators=(',', ':')) + '\n')
    atomic(c.run / 'PROFILE.json', cells)
    return cells


def idle_ticks():
    values = [int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]]
    return sum(values), values[3] + values[4]


def campaign(run, host=None, test=False):
    run = Path(run)
    c = Controller(run, host, test)
    starts = read(boot.HERE / 'STARTS.json')
    jobs = jobs_for(starts)
    outcome = {'status': 'INCOMPLETE'}
    try:
        atomic(run / 'TASKS.json', jobs)
        before = idle_ticks()
        clockjobs = [('clock_probe', {'kind': 'spin', 'seconds': 1}, 'aux')]
        clock = c.execute(clockjobs, 'CLOCK', allocation=10)
        if len(clock) != 1 or c.stopping:
            return
        r = read(run / 'jobs/clock_probe/receipt.json')
        if any(s['cpu_seconds'] > s['host_elapsed'] * 1.02 + .1 for s in r['sessions']):
            raise RuntimeError('CLOCK_CPU_SANITY_FAILURE')
        after = idle_ticks()
        if not test:
            total = after[0] - before[0]
            idle = after[1] - before[1]
            free = int(12 * idle / total) if total > 0 else 0
            c.max_workers = min(c.max_workers, free)
            if c.max_workers < 1:
                c.stopping = 'NO_IDLE_CPU_CAPACITY'
                return
        atomic(run / 'CAPACITY.json', {'workers': c.max_workers, 'idle_before': before, 'idle_after': after,
                                      'note': 'conservative launch estimate, workers use nice 10'})
        controls = c.execute([('controls', {'kind': 'controls'}, 'aux')], 'CONTROLS', allocation=600)
        if len(controls) != 1 or c.stopping:
            return
        print('PROFILE_CONTROLS_PASS', flush=True)
        calibration_jobs = [j for j in jobs if j[1]['k'] in (8, 32)]
        calibration = execute_profile(c, calibration_jobs, min(10, N), 'CALIBRATION')
        if c.stopping:
            return
        rates = {n: c.state['used'][n] / r['completed'] for n, r in calibration.items() if r['completed']}
        atomic(run / 'CALIBRATION.json', {'cpu_seconds_per_episode_including_worker_overhead': rates,
                                        'note': 'first 10 observations retained; per-cell limit stays 3600 s'})
        execute_profile(c, jobs, N, 'PROFILE')
        outcome['cells'] = summarize(c, jobs)
        if any(x.get('solution') for x in outcome['cells'].values()):
            outcome['status'] = 'VERIFIED_SRG_SOLUTION'
        elif not c.stopping and all(x['status'] == 'COMPLETE' for x in outcome['cells'].values()):
            outcome['status'] = 'COMPLETE'
    except BaseException as error:
        outcome.update(status='DIAGNOSIS_REQUIRED', error=repr(error))
        raise
    finally:
        c.close()
        if c.stopping and c.stopping.startswith('WORKER_FAILED'):
            outcome['status'] = 'DIAGNOSIS_REQUIRED'
        outcome.update(reason=c.stopping, cpu_seconds=c.state['used'], host_wall_seconds=c.state['host_wall_seconds'])
        if any(c.state['used'][k] > v for k, v in LIMITS.items()):
            outcome.update(status='DIAGNOSIS_REQUIRED', error='CPU_BUDGET_OVERRUN')
        atomic(run / 'RESULT.json', outcome)
        atomic(run / 'status.json', outcome)
        print('PROFILE_RESULT ' + json.dumps({k: v for k, v in outcome.items() if k != 'cells'}), flush=True)
