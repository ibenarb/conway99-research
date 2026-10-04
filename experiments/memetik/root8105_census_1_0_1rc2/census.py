"""ROOT8105 P0/P1 controller. Linux/WSL; no time-triggered interruption."""
import argparse
import collections
import contextlib
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
                     digest, fingerprint, get, process_stat, put, read_host_clock,
                     require_local_filesystem, resources, schema)

STOP_SIGNAL = False


def on_signal(signum, frame):
    global STOP_SIGNAL
    STOP_SIGNAL = True


def initialise(run, workers, budget, test_mode=False, test_roots=5, test_cpu_s=0.015, fail_root=None,
               test_host_clock=False, host_stop_timeout_s=60):
    if test_host_clock and not test_mode:
        raise ValueError('test_host_clock is a test-model switch only')
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
              'fail_root': fail_root, 'test_host_clock': test_host_clock,
              'host_stop_timeout_s': host_stop_timeout_s, 'auxiliary_cpu_s': time.process_time(),
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
    if type(data.get('worker_cpu_s')) not in (int, float) or not math.isfinite(data['worker_cpu_s']) or data['worker_cpu_s'] < 0:
        raise ValueError('invalid worker CPU: expected finite nonnegative process total')
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


def audit_start(con, allow_crash=False):
    dbpath = Path(con.execute('PRAGMA database_list').fetchone()[2])
    manifest = json.loads((dbpath.parent / 'manifest.json').read_text())
    immutable = ('run_id', 'model', 'model_hash', 'root_hash', 'workers', 'original_budget_cpu_s',
                 'fingerprint', 'order', 'calibration', 'test_mode', 'test_cpu_s', 'fail_root', 'rules')
    immutable += ('test_host_clock', 'host_stop_timeout_s')
    if any(get(con, key) != manifest.get(key) for key in immutable):
        raise ValueError('run plan/manifest mismatch')
    if get(con, 'fingerprint') != fingerprint():
        raise ValueError('package fingerprint changed; historical run cannot change model/code')
    if not allow_crash and con.execute("SELECT COUNT(*) FROM sessions WHERE ended IS NULL").fetchone()[0]:
        raise ValueError('UNCLOSED_SESSION: crash recovery required; saved CPU is a lower bound. '
                         'Do not delete markers or report missing CPU as zero. Use inspect-crash.')
    if not allow_crash and con.execute("SELECT COUNT(*) FROM attempts WHERE ended IS NULL").fetchone()[0]:
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
        if attempt['root'] != row['root']:
            raise ValueError('result attempt belongs to another root')
    mismatch = con.execute("SELECT COUNT(*) FROM roots WHERE (state='DONE') != "
                           '(id IN (SELECT root FROM results))').fetchone()[0]
    if mismatch:
        raise ValueError('root completion mismatch')
    # K5: invariants a torn/edited database can violate while passing the checks above.
    states = dict(con.execute('SELECT state,COUNT(*) FROM roots GROUP BY state').fetchall())
    if set(states) - {'PENDING', 'RUNNING', 'DONE', 'ERROR'}:
        raise ValueError('ROOT_STATE_INCONSISTENT: unknown root state')
    orphaned = con.execute("SELECT id FROM roots WHERE state='RUNNING' AND "
                           "(SELECT COUNT(*) FROM attempts WHERE root=roots.id AND ended IS NULL)!=1").fetchall()
    if orphaned:
        raise ValueError('ROOT_STATE_INCONSISTENT NEW_RUN_REQUIRED: RUNNING root has no unique open '
                         'attempt. Preserve the entire stopped run; initialise a DIFFERENT run directory. '
                         'Do not reconcile or edit these inconsistent accounts.')
    if con.execute("SELECT COUNT(*) FROM attempts a LEFT JOIN roots r ON r.id=a.root "
                   "LEFT JOIN sessions s ON s.id=a.session WHERE r.id IS NULL OR s.id IS NULL OR "
                   "(a.ended IS NULL AND (r.state!='RUNNING' OR s.ended IS NOT NULL OR a.state!='RUNNING'))").fetchone()[0]:
        raise ValueError('ACCOUNT_STATE_INCONSISTENT NEW_RUN_REQUIRED: invalid attempt/root/session links')
    if con.execute("SELECT COUNT(*) FROM sessions WHERE ended IS NULL AND state!='RUNNING'").fetchone()[0]:
        raise ValueError('SESSION_STATE_INCONSISTENT NEW_RUN_REQUIRED: open non-running session')
    from kernel import MODEL, ROOT_SHA, load_roots
    roots = {r['id']: r for r in load_roots()}
    order = get(con, 'order')
    actual = list(con.execute('SELECT id,spec FROM roots'))
    if (len(order) != len(set(order)) or set(order) != {r['id'] for r in actual}
            or any(json.loads(r['spec']) != roots.get(r['id']) for r in actual)
            or not set(get(con, 'calibration')).issubset(order)):
        raise ValueError('ROOT_IDENTITY_MISMATCH: manifest order or immutable root data changed')
    model = 'OPERATIONS_TEST_NOT_CENSUS' if get(con, 'test_mode') else MODEL
    if get(con, 'root_hash') != ROOT_SHA or get(con, 'model') != model or get(con, 'model_hash') != digest({
            'model': model, 'historical_core_sha256': fingerprint()['files']['historical_core.py']}):
        raise ValueError('MODEL_IDENTITY_MISMATCH')
    cpu_values = [r[0] for r in con.execute('SELECT cpu FROM attempts UNION ALL SELECT cpu FROM sessions')]
    cpu_values.append(get(con, 'auxiliary_cpu_s', 0))
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in cpu_values):
        raise ValueError('ACCOUNT_CPU_INVALID: preserve accounts; finite nonnegative values required')
    if con.execute("SELECT COUNT(*) FROM roots WHERE state='ERROR' AND id NOT IN "
                   "(SELECT root FROM attempts WHERE state='ERROR')").fetchone()[0]:
        raise ValueError('ROOT_STATE_INCONSISTENT: ERROR root without ERROR attempt')
    if con.execute("SELECT COUNT(*) FROM sessions WHERE ended IS NOT NULL AND state='RUNNING'").fetchone()[0]:
        raise ValueError('SESSION_STATE_INCONSISTENT: ended session still RUNNING')
    last = con.execute('SELECT state FROM sessions WHERE ended IS NOT NULL ORDER BY ended DESC LIMIT 1').fetchone()
    if last and not con.execute('SELECT COUNT(*) FROM sessions WHERE ended IS NULL').fetchone()[0] and get(con, 'latest_state') != last['state']:
        raise ValueError('SESSION_STATE_INCONSISTENT: latest_state differs from last closed session')
    for row in con.execute("SELECT partial FROM roots WHERE state!='DONE'"):
        for t, value in json.loads(row['partial']).items():
            if str(int(t)) != t or not 1 <= int(t) <= 83 or type(value['width']) is not int or value['width'] < 0:
                raise ValueError('ROOT_STATE_INCONSISTENT: malformed partial counts')


def settle(con, item):
    """One transaction: exact wait4 receipt, root state, result. Safe to retry after a DB error."""
    status, usage = item['status'], item['usage']
    item['proc'].returncode = os.waitstatus_to_exitcode(status)
    item['log'].close()
    cpu = usage.ru_utime + usage.ru_stime
    aid, rid = item['spec']['attempt'], item['spec']['root']['id']
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
    return error


def start_host_clock(run, tag):
    paths = [str(BASE / 'host_clock.ps1'), str(run / ('host-clock-' + tag + '.json')), str(run / ('host-stop-' + tag))]
    win_paths = [subprocess.check_output(['wslpath', '-w', p], text=True, timeout=60).strip() for p in paths]
    log = (run / ('host-clock-' + tag + '.log')).open('w')
    try:
        proc = subprocess.Popen(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                                 '-File', win_paths[0], '-OutputPath', win_paths[1], '-StopPath', win_paths[2]],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=log)
    except BaseException:
        log.close()
        raise
    return proc, log


def stop_host_clock(proc, log, stop_path, timeout):
    """K3: bounded helper shutdown. On WSL, terminating the interop process may leave the Windows
    PowerShell process alive; it still exits at its next stop-file poll unless it is hung."""
    warnings = []
    with contextlib.suppress(OSError):
        stop_path.touch()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        warnings.append(f'host clock helper ignored stop for {timeout}s; terminated; Windows CPU is the last '
                        'reported value (lower bound)')
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    log.close()
    return warnings


def host_clock_probe(run, seconds=12, timeout=30):
    """Preflight smoke test of the real Windows helper path (K7). Non-blocking for counting."""
    tag = 'preflight-' + uuid.uuid4().hex[:8]
    out, stop = run / ('host-clock-' + tag + '.json'), run / ('host-stop-' + tag)
    try:
        proc, log = start_host_clock(run, tag)
    except Exception as exc:
        return {'status': 'UNAVAILABLE', 'error': repr(exc)[:200], 'windows_cpu_s': 0}
    start, reads, problems, first, last = time.monotonic(), 0, [], None, None
    while time.monotonic() - start < seconds:
        data, problem = read_host_clock(out)
        reads += 1
        if problem:
            problems.append(problem)
        if data:
            first = first or (data, time.monotonic())
            last = (data, time.monotonic())
        time.sleep(.25)
    warnings = stop_host_clock(proc, log, stop, timeout)
    final, _ = read_host_clock(out)
    result = {'reads': reads, 'read_errors': len(problems), 'first_error': problems[0] if problems else None,
              'stop_warnings': warnings, 'windows_cpu_s': (final or (last or ({'cpu_s': 0},))[0])['cpu_s']}
    if first and last and last[1] > first[1]:
        result['host_delta_s'] = last[0]['stopwatch_s'] - first[0]['stopwatch_s']
        result['guest_delta_s'] = last[1] - first[1]
    result['status'] = 'PASS' if last and not problems and not warnings else 'DEGRADED'
    return result


def eta_estimate(con, selected, elapsed, session, clock_ok, live=None):
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
    live = live or {}
    per_root = [means[json.loads(r['spec'])['type']] *
                (1 - max(len(json.loads(r['partial'])), live.get(r['id'], 0)) / 83) for r in todo]
    used = con.execute('SELECT COALESCE(SUM(cpu),0) FROM attempts WHERE session=?', (session,)).fetchone()[0]
    rate = min(get(con, 'workers'), used / elapsed)
    # One root runs in one single-threaded worker: the longest remaining root bounds the tail.
    return max(sum(per_root) / rate, max(per_root)) if rate > 0 else None


def run_campaign(run, phase, retry_errors=False, min_memory_gib=2, min_disk_gib=1, interval=1):
    run = run.resolve()
    require_local_filesystem(run)
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
    controller_stat = process_stat(os.getpid())
    identity = controller_stat['identity']
    mono_start, utc_start = time.monotonic(), time.time()
    with con:
        con.execute('INSERT INTO sessions(id,started,state,boot,pid,identity) VALUES (?,?,?,?,?,?)',
                    (session, utc_start, 'RUNNING', boot, os.getpid(), identity))
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    active, last_log, stop_reason = {}, -1e30, None
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               PYTHONNOUSERSITE='1')
    host = host_log = None
    host_path = run / ('host-clock-' + session + '.json')
    host_stop = run / ('host-stop-' + session)
    is_wsl = 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()
    test_mode = get(con, 'test_mode')
    host_wanted = (is_wsl and not test_mode) or (test_mode and get(con, 'test_host_clock', False))
    host_warnings, host_read_errors, live_warnings, unsettled = [], 0, 0, []
    latest_host = None
    host_anchor = None
    fatal = None
    reaped_worker_cpu = 0.0
    helper_cpu_s = 0.0
    end_state = None
    announced = False
    try:
        if host_wanted:
            try:
                host, host_log = start_host_clock(run, session)
            except Exception as exc:  # K1: clock helper failure never blocks counting
                host_warnings.append('host clock unavailable: ' + repr(exc)[:200])
                print('HOST_CLOCK_UNAVAILABLE ' + canonical({'error': repr(exc)[:200]}), flush=True)
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
                        'fail_root': get(con, 'fail_root'), 'controller_pid': os.getpid(),
                        'controller_proc_pid': controller_stat['proc_pid'], 'controller_identity': identity}
                spec_path = run / 'attempts' / (aid + '.input.json')
                output = run / 'attempts' / (aid + '.output.json')
                log = (run / 'attempts' / (aid + '.log')).open('w')
                atomic(spec_path, spec)
                proc = subprocess.Popen([sys.executable, str(BASE / 'worker.py'), str(spec_path), str(output)],
                                        env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log)
                try:
                    stat = process_stat(proc.pid)
                    with con:
                        con.execute('INSERT INTO attempts(id,root,session,pid,identity,started,state,output) '
                                    'VALUES (?,?,?,?,?,?,?,?)',
                                    (aid, rid, session, proc.pid, stat['identity'] if stat else None,
                                     time.time(), 'RUNNING', str(output.relative_to(run))))
                        con.execute("UPDATE roots SET state='RUNNING' WHERE id=?", (rid,))
                except BaseException:
                    # Unregistered worker: stop and reap it; its CPU then appears as helper CPU.
                    with contextlib.suppress(ProcessLookupError):
                        proc.kill()
                    proc.wait()
                    log.close()
                    raise
                active[proc.pid] = {'proc': proc, 'spec': spec, 'output': output, 'log': log,
                                    'sent_stop': False}
            for pid, item in list(active.items()):
                if stop_reason and not item['sent_stop']:
                    os.kill(pid, signal.SIGTERM)
                    item['sent_stop'] = True
                done, status, usage = os.wait4(pid, os.WNOHANG)
                aid, rid = item['spec']['attempt'], item['spec']['root']['id']
                if not done:
                    try:
                        if item['output'].exists():
                            checkpoint = checked_payload(item['output'], item['spec'])
                            item['live_targets'] = len(checkpoint['counts'])
                            process = checkpoint['process']
                            stat = process_stat(pid, proc_pid=process['proc_pid'], identity=process['identity'])
                        else:
                            stat = process_stat(pid)
                    except Exception as exc:  # live value only; the wait4 receipt stays authoritative
                        stat = None
                        live_warnings += 1
                        if live_warnings <= 3:
                            print('LIVE_CPU_SKIPPED ' + canonical({'attempt': aid, 'error': repr(exc)[:200]}),
                                  flush=True)
                    if stat:
                        with con:
                            con.execute('UPDATE attempts SET cpu=? WHERE id=?', (stat['cpu_s'], aid))
                    continue
                del active[pid]
                reaped_worker_cpu += usage.ru_utime + usage.ru_stime
                item.update(status=status, usage=usage)
                unsettled.append(item)
                error = settle(con, item)
                unsettled.remove(item)
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
            if host_wanted:
                clock_ok = False
                fresh, problem = read_host_clock(host_path)
                if problem:
                    host_read_errors += 1
                    if host_read_errors in (1, 10, 100, 1000):
                        print('HOST_CLOCK_READ_ERROR ' + canonical({'count': host_read_errors, 'error': problem}),
                              flush=True)
                if fresh:
                    latest_host = fresh
                    if host_anchor is None:
                        host_anchor = (fresh['stopwatch_s'], elapsed)
                    host_delta = fresh['stopwatch_s'] - host_anchor[0]
                    guest_delta = elapsed - host_anchor[1]
                    clock_ok = (host_delta >= 30 and abs(host_delta - guest_delta) <= max(5, host_delta * .02)
                                and abs(time.time() - fresh['utc_s']) < 15)
                clock_source = 'Windows Stopwatch vs WSL monotonic; tolerance 2%, freshness 15s'
            live = {i['spec']['root']['id']: i.get('live_targets', 0) for i in active.values()}
            eta = eta_estimate(con, selected, elapsed, session, clock_ok, live)
            eta_text = 'unknown' if eta is None else f'{int(eta // 3600):02d}:{int(eta % 3600 // 60):02d}'
            awaiting = budget_tick(con, run, total_cpu, eta_text, announce=not announced)
            announced = True
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
            try:
                _, status, usage = os.wait4(pid, 0)
            except ChildProcessError:
                continue
            del active[pid]
            reaped_worker_cpu += usage.ru_utime + usage.ru_stime
            item.update(status=status, usage=usage)
            unsettled.append(item)
        for item in list(unsettled):
            try:  # worker partials are kept exactly as in a regular checkpoint stop
                settle(con, item)
                unsettled.remove(item)
            except Exception as again:
                print('UNSETTLED_ATTEMPT ' + canonical({'attempt': item['spec']['attempt'],
                                                       'error': repr(again)[:200]}), flush=True)
        active.clear()
    finally:
        if host:
            host_warnings += stop_host_clock(host, host_log, host_stop, get(con, 'host_stop_timeout_s', 60))
            final_host, _ = read_host_clock(host_path)
            latest_host = final_host or latest_host
        states = dict(con.execute('SELECT id,state FROM roots').fetchall())
        left = sum(states.get(r) not in ('DONE', 'ERROR') for r in selected_list)
        phase_errors = sum(states.get(r) == 'ERROR' for r in selected_list)
        done_count = con.execute('SELECT COUNT(*) FROM results').fetchone()[0]
        if fatal:
            end_state = 'CONTROLLER_ERROR'
        elif stop_reason:
            end_state = stop_reason
        elif done_count == len(get(con, 'order')):
            end_state = 'COMPLETE'
        elif left:  # e.g. a worker stopped from outside: never report this as calibration/census success
            end_state = 'PHASE_INCOMPLETE'
        elif phase == 'census':
            end_state = 'COMPLETE_WITH_ERRORS'
        else:
            end_state = 'CALIBRATION_COMPLETE_WITH_ERRORS' if phase_errors else 'CALIBRATION_COMPLETE'
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
            if host_warnings or host_read_errors or live_warnings:
                put(con, 'warnings_' + session, {'host_clock': host_warnings, 'host_clock_read_errors':
                                                 host_read_errors, 'live_cpu_skipped': live_warnings})
        if end_state in ('COMPLETE', 'COMPLETE_WITH_ERRORS', 'USER_BUDGET_ZERO'):
            close_requests(con, 'CLOSED_' + end_state)
        atomic(run / 'status.json', report(con) | {'state': end_state, 'utc': time.time(),
                                                   'snapshot_not_live_query': True})
        print('CENSUS_END ' + canonical(report(con) | {'state': end_state}), flush=True)
        con.close()
        lock.close()
    if fatal:
        raise fatal
    return end_state


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
            'cpu_is_lower_bound': bool(get(con, 'cpu_lower_bound', False)),
            'cpu_scope': 'Linux workers wait4 + measured supervisor lifetime + non-worker child CPU + Windows clock '
                         'process CPU + recorded preflight; task times are descriptive, never added twice'}


def _process_exited(proc_pid, identity):
    try:
        fields = Path(f'/proc/{proc_pid}/stat').read_text().rsplit(')', 1)[1].split()
    except (FileNotFoundError, ProcessLookupError):
        return True
    return fields[19] != identity or fields[0] in ('Z', 'X')


def reconcile_crash(run, apply=False):
    """K4/GC-15: close accounts of a crashed session without deleting anything.

    Dry run unless apply=True. Open attempts are closed as CRASH_LOWER_BOUND (cpu_exact=0) with
    max(last live /proc value, worker self-reported process_time); their roots return to PENDING with
    the last DB checkpoint. Salvaged worker outputs are stored separately and are NOT merged.
    The whole run is flagged cpu_lower_bound. Refuses while a controller or worker may still run."""
    cpu_start = time.process_time()
    run = run.resolve()
    require_local_filesystem(run)
    lock = (run / 'controller.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise ValueError('controller lock held: a controller is still running; nothing to reconcile')
    con = None
    try:
        with contextlib.closing(connect(run, readonly=True)) as inspected:
            audit_start(inspected, allow_crash=True)
        con = connect(run, readonly=not apply)
        if apply:
            con.execute('BEGIN IMMEDIATE')
        audit_start(con, allow_crash=True)
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        sessions = [dict(r) for r in con.execute('SELECT * FROM sessions WHERE ended IS NULL')]
        attempts = [dict(r) for r in con.execute('SELECT * FROM attempts WHERE ended IS NULL')]
        boots = {r['id']: r['boot'] for r in con.execute('SELECT id,boot FROM sessions')}
        plan = {'run_id': get(con, 'run_id'), 'boot_now': boot, 'sessions': [], 'attempts': [], 'blocked': []}
        for a in attempts:
            entry = {'attempt': a['id'], 'root': a['root'], 'session': a['session'], 'db_live_cpu_s': a['cpu']}
            evidence, proc_pid, identity = None, a['pid'], a['identity']
            try:
                spec = json.loads((run / 'attempts' / (a['id'] + '.input.json')).read_text())
                expected = {'attempt': a['id'], 'root': json.loads(con.execute(
                    'SELECT spec FROM roots WHERE id=?', (a['root'],)).fetchone()[0]),
                    'model': get(con, 'model'), 'code_hash': get(con, 'fingerprint')['code_hash'],
                    'root_hash': get(con, 'root_hash'), 'model_hash': get(con, 'model_hash')}
                if any(spec.get(k) != v for k, v in expected.items()) or spec.get('root_row_hash') != digest(expected['root']['row']):
                    raise ValueError('attempt input identity mismatch')
                data = checked_payload(run / a['output'], spec)
                proc_pid, identity = data['process']['proc_pid'], data['process']['identity']
                evidence = {'state': data['state'], 'targets': len(data['counts']), 'worker_cpu_s': data['worker_cpu_s'],
                            'payload': data}
            except Exception as exc:
                entry['output_unusable'] = repr(exc)[:200]
            if boots.get(a['session']) == boot:
                if identity is None or not _process_exited(proc_pid, identity):
                    plan['blocked'].append({'attempt': a['id'], 'reason': 'worker may still run in this boot'})
            entry['cpu_lower_bound_s'] = max(a['cpu'] or 0, (evidence or {}).get('worker_cpu_s', 0) or 0)
            entry['salvaged'] = {k: v for k, v in (evidence or {}).items() if k != 'payload'}
            entry['_payload'] = (evidence or {}).get('payload')
            plan['attempts'].append(entry)
        for sess in sessions:
            last_seen = sess['started']
            with contextlib.suppress(Exception):
                snap = json.loads((run / 'status.json').read_text())
                if snap.get('session') == sess['id']:
                    last_seen = max(last_seen, snap['utc'])
            host_last, _ = read_host_clock(run / ('host-clock-' + sess['id'] + '.json'))
            plan['sessions'].append({'session': sess['id'], 'boot_at_start': sess['boot'], 'started': sess['started'],
                                     'last_seen_utc': last_seen, 'supervisor_cpu_lower_bound_s': sess['cpu'],
                                     'host_clock_last': host_last})
        public = dict(plan, attempts=[{k: v for k, v in e.items() if k != '_payload'} for e in plan['attempts']])
        if apply and plan['blocked']:
            raise ValueError('RECONCILE_BLOCKED ' + canonical(plan['blocked']))
        if apply and (sessions or attempts):
            now = time.time()
            with con:
                for e in plan['attempts']:
                    con.execute("UPDATE attempts SET ended=?,cpu=?,cpu_exact=0,state='CRASH_LOWER_BOUND',error=? "
                                'WHERE id=? AND ended IS NULL',
                                (now, e['cpu_lower_bound_s'], 'reconciled after crash; CPU is a lower bound', e['attempt']))
                    con.execute("UPDATE roots SET state='PENDING' WHERE id=? AND state='RUNNING'", (e['root'],))
                    if e['_payload']:
                        put(con, 'salvage_' + e['attempt'], e['_payload'])
                for e in plan['sessions']:
                    con.execute("UPDATE sessions SET ended=?,state='CRASHED_RECONCILED' WHERE id=? AND ended IS NULL",
                                (e['last_seen_utc'], e['session']))
                    put(con, 'crash_reconciliation_' + e['session'], dict(e, reconciled_utc=now, attempts=[
                        {k: v for k, v in a.items() if k != '_payload'} for a in plan['attempts']
                        if a['session'] == e['session']]))
                    with contextlib.suppress(OSError):  # ask an orphaned Windows clock helper to exit
                        (run / ('host-stop-' + e['session'])).touch()
                put(con, 'cpu_lower_bound', True)
                put(con, 'latest_state', 'CRASHED_RECONCILED')
                put(con, 'auxiliary_cpu_s', get(con, 'auxiliary_cpu_s', 0) + time.process_time() - cpu_start)
            public['applied'] = True
        return public

    finally:
        if con is not None:
            con.close()
        lock.close()


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
    recon = sub.add_parser('reconcile-crash')
    recon.add_argument('run', type=Path)
    recon.add_argument('--apply', action='store_true')
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
        end_state = run_campaign(args.run, args.phase, args.retry_errors)
        export(args.run)
        if end_state == 'PHASE_INCOMPLETE':
            print('PHASE_INCOMPLETE: unfinished roots remain; run again to continue.', file=sys.stderr, flush=True)
            sys.exit(3)
    elif args.command == 'reconcile-crash':
        print(canonical(reconcile_crash(args.run, args.apply)))
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
