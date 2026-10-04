"""ROOT8105 P0/P1 controller. Linux/WSL; no time-triggered interruption."""
import argparse
import collections
import fcntl
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import resource
import signal
import subprocess
import sys
import time
import uuid

from runtime import (BASE, answer, atomic, budget_tick, canonical, close_requests, connect,
                     digest, fingerprint, get, process_stat, put, resources, schema)

STOP_SIGNAL = False


def on_signal(signum, frame):
    global STOP_SIGNAL
    STOP_SIGNAL = True


def initialise(run, workers, budget, test_mode=False, test_roots=5, test_cpu_s=0.015, fail_root=None):
    from kernel import MODEL, ROOT_SHA, load_roots
    roots = load_roots()
    groups = collections.defaultdict(list)
    for root in roots:
        groups[root['type']].append(root['id'])
    rng = random.Random(810520261004)
    calibration = []
    for typ in sorted(groups):
        values = groups[typ]
        chosen = rng.sample(values, min(22, len(values)))
        calibration.extend(chosen)
    rest = [r['id'] for r in roots if r['id'] not in calibration]
    rng.shuffle(rest)
    order = calibration + rest
    if test_mode:
        order = list(range(1, test_roots + 1))
        calibration = order[:min(3, len(order))]
    run.mkdir(parents=True, exist_ok=False)
    (run / 'attempts').mkdir()
    con = connect(run)
    schema(con)
    config = {'run_id': uuid.uuid4().hex, 'model': MODEL if not test_mode else 'OPERATIONS_TEST_NOT_CENSUS',
              'root_hash': ROOT_SHA, 'model_hash': digest({'model': MODEL if not test_mode else 'OPERATIONS_TEST_NOT_CENSUS', 'historical_core_sha256': fingerprint()['files']['historical_core.py']}), 'workers': workers, 'original_budget_cpu_s': budget,
              'budget_cpu_s': budget, 'fingerprint': fingerprint(), 'order': order,
              'calibration': calibration, 'test_mode': test_mode, 'test_cpu_s': test_cpu_s,
              'fail_root': fail_root, 'auxiliary_cpu_s': time.process_time(),
              'rules': ['GC-01', 'GC-02', 'GC-10', 'GC-11', 'GC-15', 'GC-18', 'GC-19', 'GC-20']}
    with con:
        for key, value in config.items():
            put(con, key, value)
        for root in roots:
            if root['id'] in set(order):
                con.execute('INSERT INTO roots(id,spec) VALUES (?,?)', (root['id'], canonical(root)))
    atomic(run / 'manifest.json', config)
    con.close()
    return config


def checked_payload(path, spec):
    data = json.loads(path.read_text())
    for key in ('attempt', 'model', 'code_hash', 'root_hash', 'model_hash', 'root_row_hash'):
        if data[key] != spec[key]:
            raise ValueError('worker identity mismatch: ' + key)
    if data['root'] != spec['root']['id']:
        raise ValueError('worker root mismatch')
    for t, value in data['counts'].items():
        if str(int(t)) != t or not 1 <= int(t) <= 83:
            raise ValueError('invalid target')
        if type(value['width']) is not int or value['width'] < 0:
            raise ValueError('invalid exact count')
        if not math.isfinite(value['cpu_s']) or value['cpu_s'] < 0:
            raise ValueError('invalid target CPU')
    for t, value in spec['partial'].items():
        if data['counts'].get(t) != value:
            raise ValueError('checkpoint changed on resume')
    return data


def audit_start(con):
    dbpath = Path(con.execute('PRAGMA database_list').fetchone()[2])
    manifest = json.loads((dbpath.parent / 'manifest.json').read_text())
    immutable = ('run_id', 'model', 'model_hash', 'root_hash', 'workers', 'original_budget_cpu_s',
                 'fingerprint', 'order', 'calibration', 'test_mode', 'test_cpu_s', 'fail_root', 'rules')
    if any(get(con, key) != manifest[key] for key in immutable):
        raise ValueError('run plan/manifest mismatch')
    if get(con, 'fingerprint') != fingerprint():
        raise ValueError('package fingerprint changed; historical run cannot change model/code')
    if con.execute("SELECT COUNT(*) FROM sessions WHERE ended IS NULL").fetchone()[0]:
        raise ValueError('UNCLOSED_SESSION: crash recovery required; saved CPU is a lower bound. '
                         'Do not delete markers or report missing CPU as zero. Use inspect-crash.')
    if con.execute("SELECT COUNT(*) FROM attempts WHERE ended IS NULL").fetchone()[0]:
        raise ValueError('UNCLOSED_ATTEMPT')
    if con.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
        raise ValueError('SQLite integrity failure')
    for row in con.execute('SELECT * FROM results'):
        data = json.loads(row['payload'])
        if digest(data) != row['digest'] or len(data['counts']) != 83:
            raise ValueError('result digest/completeness mismatch')
        attempt = con.execute('SELECT * FROM attempts WHERE id=?', (row['attempt'],)).fetchone()
        if not attempt or not attempt['cpu_exact'] or attempt['state'] != 'COMPLETE':
            raise ValueError('result lacks exact attempt receipt')
    mismatch = con.execute("SELECT COUNT(*) FROM roots WHERE (state='DONE') != "
                           '(id IN (SELECT root FROM results))').fetchone()[0]
    if mismatch:
        raise ValueError('root completion mismatch')


def eta_estimate(con, selected, elapsed, session, clock_ok):
    # Separate strata; rough measured estimate, no confidence bound or tree extrapolation.
    rows = con.execute("SELECT roots.spec,attempts.cpu FROM results JOIN roots ON roots.id=results.root "
                       'JOIN attempts ON attempts.id=results.attempt').fetchall()
    samples = collections.defaultdict(list)
    for row in rows:
        samples[json.loads(row['spec'])['type']].append(row['cpu'])
    pending = con.execute("SELECT id,spec,partial FROM roots WHERE state NOT IN ('DONE','ERROR')").fetchall()
    todo = [r for r in pending if r['id'] in selected]
    if not todo:
        return 0.0
    types = {json.loads(r['spec'])['type'] for r in todo}
    if not clock_ok or elapsed < 60 or any(len(samples[t]) < 3 for t in types):
        return None
    means = {t: sum(v) / len(v) for t, v in samples.items()}
    remaining = sum(means[json.loads(r['spec'])['type']] * (1 - len(json.loads(r['partial'])) / 83)
                    for r in todo)
    used = con.execute('SELECT COALESCE(SUM(cpu),0) FROM attempts WHERE session=?', (session,)).fetchone()[0]
    rate = min(get(con, 'workers'), used / elapsed)
    return remaining / rate if rate > 0 else None


def run_campaign(run, phase, retry_errors=False, min_memory_gib=2, min_disk_gib=1, interval=1):
    run = run.resolve()
    lock = (run / 'controller.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    con = connect(run)
    audit_start(con)
    if get(con, 'stop_requested', False):
        raise ValueError('Run was explicitly stopped by answer 0. Use resume-after-stop to reopen intentionally.')
    if not get(con, 'test_mode') and not get(con, 'preflight', {}).get('status') == 'PASS':
        raise ValueError('PREFLIGHT_REQUIRED: run preflight.py before calibration/census')
    if not get(con, 'test_mode'):
        expected = get(con, 'preflight')['dependencies']
        if any(importlib.metadata.version(name) != version for name, version in expected.items()):
            raise ValueError('runtime dependency versions changed since preflight')
    workers = get(con, 'workers')
    selected_list = get(con, 'calibration') if phase == 'calibrate' else get(con, 'order')
    selected = set(selected_list)
    if retry_errors:
        with con:
            con.execute("UPDATE roots SET state='PENDING' WHERE state='ERROR'")
    pending = {r['id'] for r in con.execute("SELECT id FROM roots WHERE state='PENDING'")}
    queue = collections.deque(r for r in selected_list if r in pending)
    session = uuid.uuid4().hex
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    identity = process_stat(os.getpid())['identity']
    mono_start, utc_start = time.monotonic(), time.time()
    with con:
        con.execute('INSERT INTO sessions(id,started,state,boot,pid,identity) VALUES (?,?,?,?,?,?)',
                    (session, utc_start, 'RUNNING', boot, os.getpid(), identity))
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    active, last_log, stop_reason = {}, -1e30, None
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               PYTHONNOUSERSITE='1')
    host = None
    host_path = run / ('host-clock-' + session + '.json')
    host_stop = run / ('host-stop-' + session)
    is_wsl = 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()
    if is_wsl and not get(con, 'test_mode'):
        paths = [str(BASE / 'host_clock.ps1'), str(host_path), str(host_stop)]
        win_paths = [subprocess.check_output(['wslpath', '-w', p], text=True).strip() for p in paths]
        host_log = (run / ('host-clock-' + session + '.log')).open('w')
        host = subprocess.Popen(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy',
                                 'Bypass', '-File', win_paths[0], '-OutputPath', win_paths[1],
                                 '-StopPath', win_paths[2]], stdout=host_log, stderr=host_log)
    latest_host = None
    host_anchor = None
    fatal = None
    reaped_worker_cpu = 0.0
    helper_cpu_s = 0.0
    try:
        while queue or active:
            now = time.monotonic()
            res = resources(run)
            if res['mem_available_bytes'] < min_memory_gib * 2 ** 30:
                stop_reason = 'RESOURCE_MEMORY'
            if res['disk_free_bytes'] < min_disk_gib * 2 ** 30:
                stop_reason = 'RESOURCE_DISK'
            if STOP_SIGNAL:
                stop_reason = 'USER_SIGNAL_CHECKPOINT'
            if get(con, 'stop_requested', False):
                stop_reason = 'USER_BUDGET_ZERO'
            while queue and len(active) < workers and stop_reason is None:
                rid = queue.popleft()
                row = con.execute('SELECT * FROM roots WHERE id=?', (rid,)).fetchone()
                aid = uuid.uuid4().hex
                spec = {'root': json.loads(row['spec']), 'partial': json.loads(row['partial']),
                        'attempt': aid, 'code_hash': get(con, 'fingerprint')['code_hash'],
                        'root_hash': get(con, 'root_hash'), 'model': get(con, 'model'), 'model_hash': get(con, 'model_hash'),
                        'root_row_hash': digest(json.loads(row['spec'])['row']),
                        'test_mode': get(con, 'test_mode'), 'test_cpu_s': get(con, 'test_cpu_s'),
                        'fail_root': get(con, 'fail_root')}
                spec_path = run / 'attempts' / (aid + '.input.json')
                output = run / 'attempts' / (aid + '.output.json')
                log = (run / 'attempts' / (aid + '.log')).open('w')
                atomic(spec_path, spec)
                proc = subprocess.Popen([sys.executable, str(BASE / 'worker.py'), str(spec_path), str(output)],
                                        env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log)
                stat = process_stat(proc.pid)
                with con:
                    con.execute('INSERT INTO attempts(id,root,session,pid,identity,started,state,output) '
                                'VALUES (?,?,?,?,?,?,?,?)',
                                (aid, rid, session, proc.pid, stat['identity'] if stat else None,
                                 time.time(), 'RUNNING', str(output.relative_to(run))))
                    con.execute("UPDATE roots SET state='RUNNING' WHERE id=?", (rid,))
                active[proc.pid] = {'proc': proc, 'spec': spec, 'output': output, 'log': log,
                                    'sent_stop': False}
            for pid, item in list(active.items()):
                if stop_reason and not item['sent_stop']:
                    os.kill(pid, signal.SIGTERM)
                    item['sent_stop'] = True
                done, status, usage = os.wait4(pid, os.WNOHANG)
                aid, rid = item['spec']['attempt'], item['spec']['root']['id']
                if not done:
                    if item['output'].exists():
                        checkpoint = checked_payload(item['output'], item['spec'])
                        process = checkpoint['process']
                        stat = process_stat(pid, proc_pid=process['proc_pid'], identity=process['identity'])
                    else:
                        stat = process_stat(pid)
                    if stat:
                        with con:
                            con.execute('UPDATE attempts SET cpu=? WHERE id=?', (stat['cpu_s'], aid))
                    continue
                item['proc'].returncode = os.waitstatus_to_exitcode(status)
                item['log'].close()
                cpu = usage.ru_utime + usage.ru_stime
                reaped_worker_cpu += cpu
                error = None
                try:
                    data = checked_payload(item['output'], item['spec'])
                    if data['state'] == 'COMPLETE' and (len(data['counts']) != 83 or item['proc'].returncode != 0):
                        raise ValueError('worker completion/exit mismatch')
                    state = data['state']
                    if state not in ('COMPLETE', 'STOPPED_PARTIAL', 'ERROR'):
                        raise ValueError('missing worker final receipt')
                    error = data.get('error')
                except Exception as exc:
                    data = {'counts': item['spec']['partial']}
                    state, error = 'ERROR', repr(exc)
                with con:
                    con.execute('UPDATE attempts SET ended=?,cpu=?,cpu_exact=1,state=?,error=? WHERE id=?',
                                (time.time(), cpu, state, error, aid))
                    con.execute('UPDATE roots SET state=?,partial=? WHERE id=?',
                                ('DONE' if state == 'COMPLETE' else ('ERROR' if state == 'ERROR' else 'PENDING'),
                                 canonical(data['counts']), rid))
                    if state == 'COMPLETE':
                        con.execute('INSERT INTO results VALUES (?,?,?,?)', (rid, aid, canonical(data), digest(data)))
                del active[pid]
                if error:
                    print('WORKER_ERROR ' + canonical({'root': rid, 'attempt': aid, 'error': error}), flush=True)
            child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            helper_cpu_s = max(0, child_usage.ru_utime + child_usage.ru_stime - reaped_worker_cpu)
            own_cpu = time.process_time() + helper_cpu_s + (latest_host['cpu_s'] if latest_host else 0)
            with con:
                con.execute('UPDATE sessions SET cpu=? WHERE id=?', (own_cpu, session))
            total_cpu = con.execute('SELECT COALESCE(SUM(cpu),0) FROM attempts').fetchone()[0]
            total_cpu += con.execute('SELECT COALESCE(SUM(cpu),0) FROM sessions').fetchone()[0]
            total_cpu += get(con, 'auxiliary_cpu_s', 0)
            elapsed = now - mono_start
            clock_ok = abs((time.time() - utc_start) - elapsed) <= max(2, elapsed * .01)
            clock_source = 'Linux monotonic vs UTC'
            if is_wsl and not get(con, 'test_mode'):
                clock_ok = False
                if host_path.exists():
                    latest_host = json.loads(host_path.read_text(encoding='utf-8-sig'))
                    if host_anchor is None:
                        host_anchor = (latest_host['stopwatch_s'], elapsed)
                    host_delta = latest_host['stopwatch_s'] - host_anchor[0]
                    guest_delta = elapsed - host_anchor[1]
                    clock_ok = (host_delta >= 30 and abs(host_delta - guest_delta) <= max(5, host_delta * .02)
                                and abs(time.time() - latest_host['utc_s']) < 15)
                clock_source = 'Windows Stopwatch vs WSL monotonic; tolerance 2%, freshness 15s'
            eta = eta_estimate(con, selected, elapsed, session, clock_ok)
            eta_text = 'unknown' if eta is None else f'{int(eta // 3600):02d}:{int(eta % 3600 // 60):02d}'
            awaiting = budget_tick(con, run, total_cpu, eta_text)
            counts = dict(con.execute('SELECT state,COUNT(*) FROM roots GROUP BY state').fetchall())
            snapshot = {'run_id': get(con, 'run_id'), 'session': session, 'phase': phase,
                        'utc': time.time(), 'pid': os.getpid(), 'boot_id': boot,
                        'state': stop_reason or ('RUNNING_AWAITING_TIME_EXTENSION' if awaiting else 'RUNNING'),
                        'roots': counts, 'active_workers': len(active), 'queued_in_phase': len(queue),
                        'aggregate_cpu_s': total_cpu, 'budget_cpu_s': get(con, 'budget_cpu_s'),
                        'cpu_overrun_s': max(0, total_cpu - get(con, 'budget_cpu_s')),
                        'eta_seconds': eta, 'eta_kind': 'measured stratified rough estimate, not a bound',
                        'clock_ok': clock_ok, 'clock_source': clock_source, 'host_clock': latest_host,
                        'resources': res, 'snapshot_not_live_query': True}
            atomic(run / 'status.json', snapshot)
            if now - last_log >= 600 or stop_reason:
                print('CENSUS_STATUS ' + canonical(snapshot), flush=True)
                last_log = now
            if stop_reason and not active:
                break
            if queue or active:
                time.sleep(interval)
    except BaseException as exc:
        fatal = exc
        # Save a sound checkpoint after current target; never terminate unrelated processes.
        for pid in active:
            with __import__('contextlib').suppress(ProcessLookupError):
                os.kill(pid, signal.SIGTERM)
        for pid, item in list(active.items()):
            _, status, usage = os.wait4(pid, 0)
            item['proc'].returncode = os.waitstatus_to_exitcode(status)
            item['log'].close()
            reaped_worker_cpu += usage.ru_utime + usage.ru_stime
            with con:
                con.execute("UPDATE attempts SET ended=?,cpu=?,cpu_exact=1,state='ERROR',error=? WHERE id=?",
                            (time.time(), usage.ru_utime + usage.ru_stime, 'controller failure; output retained',
                             item['spec']['attempt']))
                con.execute("UPDATE roots SET state='PENDING' WHERE id=?", (item['spec']['root']['id'],))
        active.clear()
    finally:
        if host:
            host_stop.touch()
            # Finite helper shutdown; budget does not control this wait.
            host.wait()
            host_log.close()
            if host_path.exists():
                latest_host = json.loads(host_path.read_text(encoding='utf-8-sig'))
        errors = con.execute("SELECT COUNT(*) FROM roots WHERE state='ERROR'").fetchone()[0]
        done_count = con.execute('SELECT COUNT(*) FROM results').fetchone()[0]
        end_state = ('CONTROLLER_ERROR' if fatal else stop_reason) or (
            'COMPLETE' if done_count == len(get(con, 'order')) else (
                'COMPLETE_WITH_ERRORS' if errors else 'CALIBRATION_COMPLETE'))
        child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        helper_cpu_s = max(0, child_usage.ru_utime + child_usage.ru_stime - reaped_worker_cpu)
        session_cpu = time.process_time() + helper_cpu_s + (latest_host['cpu_s'] if latest_host else 0)
        with con:
            con.execute('UPDATE sessions SET ended=?,cpu=?,state=? WHERE id=?',
                        (time.time(), session_cpu, end_state, session))
            put(con, 'helper_cpu_' + session, {'Linux_children_excluding_workers': helper_cpu_s,
                'Windows_clock_process': latest_host['cpu_s'] if latest_host else 0})
            put(con, 'latest_state', end_state)
            if latest_host:
                put(con, 'host_clock_' + session, latest_host)
        if end_state in ('COMPLETE', 'COMPLETE_WITH_ERRORS', 'USER_BUDGET_ZERO'):
            close_requests(con, 'CLOSED_' + end_state)
        atomic(run / 'status.json', report(con) | {'state': end_state, 'utc': time.time(),
                                                   'snapshot_not_live_query': True})
        print('CENSUS_END ' + canonical(report(con) | {'state': end_state}), flush=True)
        con.close()
        lock.close()
    if fatal:
        raise fatal


def report(con):
    roots = dict(con.execute('SELECT state,COUNT(*) FROM roots GROUP BY state').fetchall())
    worker_cpu = con.execute('SELECT COALESCE(SUM(cpu),0) FROM attempts').fetchone()[0]
    supervisor_cpu = con.execute('SELECT COALESCE(SUM(cpu),0) FROM sessions').fetchone()[0]
    auxiliary_cpu = get(con, 'auxiliary_cpu_s', 0)
    return {'run_id': get(con, 'run_id'), 'roots': roots, 'model': get(con, 'model'),
            'worker_cpu_s': worker_cpu, 'supervisor_cpu_s': supervisor_cpu,
            'auxiliary_cpu_s': auxiliary_cpu, 'aggregate_cpu_s': worker_cpu + supervisor_cpu + auxiliary_cpu,
            'budget_cpu_s': get(con, 'budget_cpu_s'),
            'open_attempts': con.execute('SELECT COUNT(*) FROM attempts WHERE ended IS NULL').fetchone()[0],
            'cpu_scope': 'Linux workers wait4 + measured supervisor lifetime + non-worker child CPU + Windows clock '
                         'process CPU + recorded preflight; task times are descriptive, never added twice'}


def export(run):
    cpu_start = time.process_time()
    con = connect(run)
    target = run / 'census.jsonl'
    tmp = target.with_suffix('.jsonl.tmp')
    total_min, completed = 0, 0
    with tmp.open('w') as stream:
        for record in con.execute('SELECT roots.spec,results.payload,results.digest FROM results '
                                  'JOIN roots ON roots.id=results.root ORDER BY roots.id'):
            root, data = json.loads(record['spec']), json.loads(record['payload'])
            if digest(data) != record['digest']:
                raise ValueError('result hash mismatch')
            widths = [data['counts'][str(t)]['width'] for t in range(1, 84)]
            minimum = min(widths)
            total_min += minimum
            completed += 1
            stream.write(canonical(root | {'widths_t1_to_t83': widths, 'min': minimum,
                                          'argmin': [t for t in range(1, 84) if widths[t - 1] == minimum],
                                          'model': data['model'], 'code_hash': data['code_hash'],
                                          'root_hash': data['root_hash'], 'model_hash': data['model_hash'],
                                          'root_row_hash': data['root_row_hash'], 'certified': False}) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, target)
    with con:
        put(con, 'auxiliary_cpu_s', get(con, 'auxiliary_cpu_s', 0) + time.process_time() - cpu_start)
    atomic(run / 'summary.json', report(con) | {'completed_roots': completed, 'exact_counts': completed * 83,
          'sum_min_width_completed_roots': total_min, 'full_census': completed == 8105 and not get(con, 'test_mode'),
          'not_a_full_tree_size': True})
    con.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('run', type=Path)
    init.add_argument('--workers', type=int, default=11)
    init.add_argument('--budget-cpu-seconds', type=float, default=48 * 3600)
    launch = sub.add_parser('run')
    launch.add_argument('run', type=Path)
    launch.add_argument('--phase', choices=['calibrate', 'census'], default='census')
    launch.add_argument('--retry-errors', action='store_true')
    for name in ('status', 'export', 'inspect-crash', 'resume-after-stop'):
        sub.add_parser(name).add_argument('run', type=Path)
    reply = sub.add_parser('answer')
    reply.add_argument('run', type=Path)
    reply.add_argument('run_id')
    reply.add_argument('request_id')
    reply.add_argument('seconds')
    args = parser.parse_args()
    if args.command == 'init':
        if not 1 <= args.workers <= 11 or args.budget_cpu_seconds <= 0:
            parser.error('workers must be 1..11 and aggregate CPU threshold positive')
        print(canonical(initialise(args.run, args.workers, args.budget_cpu_seconds)))
    elif args.command == 'run':
        run_campaign(args.run, args.phase, args.retry_errors)
        export(args.run)
    elif args.command == 'answer':
        print(answer(args.run, args.run_id, args.request_id, args.seconds))
    elif args.command == 'export':
        export(args.run)
    else:
        con = connect(args.run)
        if args.command == 'resume-after-stop':
            audit_start(con)
            with con:
                put(con, 'stop_requested', False)
                put(con, 'explicit_resume_utc', time.time())
        if args.command == 'inspect-crash':
            print(canonical({'sessions': [dict(r) for r in con.execute('SELECT * FROM sessions WHERE ended IS NULL')],
                             'attempts': [dict(r) for r in con.execute('SELECT * FROM attempts WHERE ended IS NULL')],
                             'warning': 'CPU lower bounds only. Preserve all files; reconcile before resume.'}))
        else:
            print(canonical(report(con)))
        con.close()


if __name__ == '__main__':
    main()
