import bootstrap
"""Actual subprocess GC-19/GC-15 regression suite. No wall-time experiment stops."""
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time

from census import audit_start, export, initialise, reconcile_crash, report
from runtime import BASE, answer, atomic, connect, get


def until(predicate):
    # Test harness polling; no worker deadline. A failure remains observable in logs.
    while True:
        result = predicate()
        if result:
            return result
        time.sleep(.05)


def launch(run, env=None):
    log = (run / ('test-' + str(time.time_ns()) + '.log')).open('w')
    proc = subprocess.Popen([sys.executable, str(BASE / 'census.py'), 'run', str(run)],
                            stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=env)
    return proc, log


def finish(proc, log):
    code = proc.wait()
    log.close()
    body = Path(log.name).read_text()
    assert code == 0, (code, body)
    samples = [json.loads(line.split(' ', 1)[1])['aggregate_cpu_s'] for line in body.splitlines()
               if line.startswith(('CENSUS_STATUS ', 'CENSUS_END '))]
    assert all(b + .05 >= a for a, b in zip(samples, samples[1:])), samples


def open_request(run):
    con = connect(run)
    row = con.execute("SELECT * FROM requests WHERE state='OPEN'").fetchone()
    con.close()
    return dict(row) if row else None


def done(run):
    con = connect(run)
    count = con.execute('SELECT COUNT(*) FROM results').fetchone()[0]
    con.close()
    return count


def query(run, sql):
    con = connect(run)
    rows = [dict(r) for r in con.execute(sql)]
    con.close()
    return rows


def final_state(path):
    with __import__('contextlib').suppress(FileNotFoundError, ValueError):
        state = json.loads(path.read_text())['state']
        return state if state != 'RUNNING' else None


FAKE_HELPER = """import json, os, sys, time
a = sys.argv; out = a[a.index('-OutputPath') + 1]; stop = a[a.index('-StopPath') + 1]
mode = os.environ.get('FAKE_MODE', 'good'); t0 = time.monotonic(); i = 0
while True:
    i += 1
    text = json.dumps({'pid': os.getpid(), 'stopwatch_s': time.monotonic() - t0, 'utc_s': time.time(),
                       'cpu_s': time.process_time(), 'source': 'operations_test fake'})
    if mode == 'corrupt' and i == 3:
        text = text.replace('.', ',', 1)  # e.g. a locale-formatted number
    open(out + '.tmp', 'w').write(text)
    os.replace(out + '.tmp', out)
    if os.path.exists(stop) and mode != 'ignore_stop':
        break
    time.sleep(2.5 if (mode == 'corrupt' and i == 3) else .3)
"""


def fake_bins(root):
    """Stand-ins for wslpath/powershell.exe: exercise the Windows clock branch on any Linux."""
    full, nops = root / 'fakebin', root / 'fakebin-no-powershell'
    for d in (full, nops):
        d.mkdir()
        (d / 'wslpath').write_text('#!/bin/sh\n[ "$1" = "-w" ] && echo "$2"\n')
        (d / 'wslpath').chmod(0o755)
    (full / 'powershell.exe').write_text('#!' + sys.executable + '\n' + FAKE_HELPER)
    (full / 'powershell.exe').chmod(0o755)
    return full, nops


def isolated_clock_environment(path, mode, inherited=None):
    """Only controlled executables may be resolved during a simulated clock test."""
    env = dict(os.environ if inherited is None else inherited)
    env.update(PATH=str(path.resolve()), FAKE_MODE=mode)
    return env


def clock_path_regression(root, full, nops):
    """Model WSL's installed PowerShell with a harmless inherited-PATH decoy."""
    outside = root / 'inherited-bin'
    outside.mkdir()
    marker = root / 'INHERITED_POWERSHELL_WAS_STARTED'
    decoy = outside / 'powershell.exe'
    decoy.write_text('#!' + sys.executable + '\nfrom pathlib import Path\n'
                     + 'Path(' + repr(str(marker)) + ').write_text("UNEXPECTED")\n')
    decoy.chmod(0o755)
    inherited = dict(os.environ, PATH=str(outside) + ':' + os.environ.get('PATH', ''))
    # The former prepending-only code finds an executable that should be absent.
    assert shutil.which('powershell.exe', path=str(nops) + ':' + inherited['PATH']) == str(decoy)
    for directory in (full, nops):
        env = isolated_clock_environment(directory, 'good', inherited)
        assert shutil.which('wslpath', path=env['PATH']) == str(directory / 'wslpath')
        expected = str(full / 'powershell.exe') if directory == full else None
        assert shutil.which('powershell.exe', path=env['PATH']) == expected
    return inherited, marker


def main(out):
    results = []
    temp = tempfile.mkdtemp(prefix='root8105-ops-')
    print('TEST_ARTIFACTS ' + temp, flush=True)
    if True:
        root = Path(temp)
        run = root / 'open-budget'
        spec = initialise(run, 2, .01, True, 12, .04)
        proc, log = launch(run)
        req = until(lambda: open_request(run))
        before = done(run)
        # EOF + unanswered budget must not prevent completion and further scheduling.
        until(lambda: done(run) >= before + 2)
        assert proc.poll() is None
        assert open_request(run)['id'] == req['id']
        assert answer(run, spec['run_id'], req['id'], 'bad') == 'INVALID_INPUT_CONTINUING'
        assert answer(run, spec['run_id'], req['id'], '1') == 'EXTENDED'
        assert answer(run, spec['run_id'], req['id'], '1') == 'ALREADY_PROCESSED'
        con = connect(run)
        assert get(con, 'budget_cpu_s') == 1.01
        con.close()
        req2 = until(lambda: open_request(run))
        assert req2['id'] != req['id']
        assert answer(run, spec['run_id'], req2['id'], '0') == 'STOP_REQUESTED'
        finish(proc, log)
        con = connect(run)
        assert get(con, 'latest_state') == 'USER_BUDGET_ZERO'
        count_before = done(run)
        cpu_before = con.execute('SELECT SUM(cpu) FROM attempts').fetchone()[0]
        assert con.execute('SELECT COUNT(*) FROM attempts WHERE cpu_exact!=1').fetchone()[0] == 0
        assert con.execute("SELECT COUNT(*) FROM roots WHERE state='RUNNING'").fetchone()[0] == 0
        # Explicit resume is required after an intentional zero response.
        from runtime import put
        with con:
            put(con, 'stop_requested', False)
        con.close()
        proc, log = launch(run)
        finish(proc, log)
        assert done(run) == 12
        con = connect(run)
        assert con.execute('SELECT SUM(cpu) FROM attempts').fetchone()[0] > cpu_before
        assert con.execute('SELECT COUNT(DISTINCT root) FROM results').fetchone()[0] == 12
        assert con.execute("SELECT COUNT(*) FROM requests WHERE state='OPEN'").fetchone()[0] == 0
        assert count_before >= 2
        audit_start(con)
        con.close()
        results += ['EOF_and_no_answer_continue_scheduling', 'invalid_answer_continues',
                    'positive_extension_exactly_once', 'repeated_threshold_new_request',
                    'zero_graceful_checkpoint', 'resume_preserves_counts_and_cumulative_cpu',
                    'normal_completion_closes_request', 'live_CPU_never_regresses_beyond_tick_tolerance']
        export(run)
        assert len((run / 'census.jsonl').read_text().splitlines()) == 12
        # A signal checkpoint preserves the SAME open request over restart.
        run2 = root / 'signal'
        initialise(run2, 2, .01, True, 6, .03)
        proc, log = launch(run2)
        req = until(lambda: open_request(run2))
        proc.send_signal(signal.SIGTERM)
        finish(proc, log)
        assert open_request(run2)['id'] == req['id']
        proc, log = launch(run2)
        finish(proc, log)
        assert done(run2) == 6
        assert req['id'] in Path(log.name).read_text()  # K8: restarted controller re-announces it
        results.append('open_request_survives_signal_resume')
        results.append('open_request_reannounced_after_restart')
        # A single failing worker must not stop healthy roots.
        run3 = root / 'local-error'
        initialise(run3, 2, 3600, True, 4, .005, fail_root=1)
        proc, log = launch(run3)
        finish(proc, log)
        assert done(run3) == 3
        con = connect(run3)
        assert con.execute("SELECT COUNT(*) FROM roots WHERE state='ERROR'").fetchone()[0] == 1
        assert con.execute('SELECT COUNT(*) FROM attempts WHERE cpu_exact!=1').fetchone()[0] == 0
        results.append('worker_failure_isolated_and_wait4_accounted')
        # Artificial unclosed session must be rejected, not silently booked as zero.
        with con:
            con.execute("UPDATE sessions SET ended=NULL WHERE id=(SELECT id FROM sessions LIMIT 1)")
        try:
            audit_start(con)
        except ValueError as exc:
            assert 'UNCLOSED_SESSION' in str(exc)
        else:
            raise AssertionError('unclean restart accepted')
        con.close()
        results.append('unclean_session_requires_accounting_reconciliation')
        # K5: a torn/edited state (RUNNING root, closed attempt, missing result) must be rejected.
        run6 = root / 'torn'
        initialise(run6, 2, 3600, True, 3, .002)
        proc, log = launch(run6)
        finish(proc, log)
        con = connect(run6)
        with con:
            con.execute('DELETE FROM results WHERE root=3')
            con.execute("UPDATE roots SET state='RUNNING' WHERE id=3")
        try:
            audit_start(con)
        except ValueError as exc:
            assert 'ROOT_STATE_INCONSISTENT' in str(exc)
        else:
            raise AssertionError('RUNNING root without open attempt accepted')
        con.close()
        results.append('torn_running_root_rejected')
        # K6: controller killed immediately after a spawn; the worker must stop, not finish alone.
        run4 = root / 'pdeathsig'
        initialise(run4, 1, 3600, True, 3, .03)
        proc, log = launch(run4)
        while not query(run4, 'SELECT id FROM attempts WHERE ended IS NULL'):
            time.sleep(.001)
        proc.kill()
        proc.wait()
        log.close()
        first = query(run4, 'SELECT id,cpu FROM attempts WHERE ended IS NULL')[0]
        output = run4 / 'attempts' / (first['id'] + '.output.json')
        assert until(lambda: final_state(output)) == 'STOPPED_PARTIAL'
        results.append('orphaned_worker_stops_even_during_startup')
        # K4: crash reconciliation; dry run changes nothing, apply closes accounts as lower bounds.
        con = connect(run4)
        try:
            audit_start(con)
        except ValueError as exc:
            assert 'UNCLOSED_SESSION' in str(exc)
        else:
            raise AssertionError('crashed session accepted')
        con.close()
        plan = until(lambda: (lambda p: None if p['blocked'] else p)(reconcile_crash(run4)))
        assert 'applied' not in plan and len(plan['sessions']) == 1 and len(plan['attempts']) == 1
        assert query(run4, 'SELECT COUNT(*) AS n FROM sessions WHERE ended IS NULL')[0]['n'] == 1
        assert reconcile_crash(run4, apply=True)['applied']
        attempt = query(run4, "SELECT * FROM attempts WHERE id='%s'" % first['id'])[0]
        worker_cpu = json.loads(output.read_text())['worker_cpu_s']
        assert attempt['state'] == 'CRASH_LOWER_BOUND' and attempt['cpu_exact'] == 0
        assert attempt['cpu'] >= worker_cpu > 0
        assert query(run4, "SELECT state FROM sessions")[0]['state'] == 'CRASHED_RECONCILED'
        proc, log = launch(run4)
        finish(proc, log)
        assert done(run4) == 3
        con = connect(run4)
        audit_start(con)
        assert report(con)['cpu_is_lower_bound'] is True
        con.close()
        results.append('crash_reconciled_lower_bound_then_resumed')
        # K5: a worker stopped from outside must not end as a successful phase.
        run5 = root / 'external-stop'
        initialise(run5, 1, 3600, True, 2, .03)
        proc, log = launch(run5)
        victim = until(lambda: next((a for a in query(run5, 'SELECT id,pid FROM attempts WHERE ended IS NULL')
                                     if (run5 / 'attempts' / (a['id'] + '.output.json')).exists()), None))
        os.kill(victim['pid'], signal.SIGTERM)
        assert proc.wait() == 3
        log.close()
        con = connect(run5)
        assert get(con, 'latest_state') == 'PHASE_INCOMPLETE'
        con.close()
        proc, log = launch(run5)
        finish(proc, log)
        assert done(run5) == 2
        results.append('externally_stopped_worker_reports_phase_incomplete')
        # K1-K3: Windows clock helper faults never stop counting or leave a session open.
        full, nops = fake_bins(root)
        inherited, forbidden_marker = clock_path_regression(root, full, nops)
        for name, path, mode, check in [
                ('clock-good', full, 'good', lambda w, c: not w and c),
                ('clock-missing', nops, 'good', lambda w, c: 'unavailable' in str(w['host_clock'])),
                ('clock-corrupt', full, 'corrupt', lambda w, c: w['host_clock_read_errors'] >= 1),
                ('clock-hung', full, 'ignore_stop', lambda w, c: 'ignored stop' in str(w['host_clock']))]:
            run7 = root / name
            initialise(run7, 2, 3600, True, 6, .02, test_host_clock=True, host_stop_timeout_s=3)
            env = isolated_clock_environment(path, mode, inherited)
            proc, log = launch(run7, env)
            finish(proc, log)
            con = connect(run7)
            assert get(con, 'latest_state') == 'COMPLETE' and done(run7) == 6
            assert con.execute('SELECT COUNT(*) FROM sessions WHERE ended IS NULL').fetchone()[0] == 0
            warn = con.execute("SELECT value FROM meta WHERE key LIKE 'warnings_%'").fetchone()
            clock = con.execute("SELECT value FROM meta WHERE key LIKE 'host_clock_%'").fetchone()
            con.close()
            assert check(json.loads(warn[0]) if warn else None, clock), (name, warn, clock)
            results.append('host_clock_' + mode.replace('good', 'missing' if path == nops else 'ok')
                           + '_counting_continues')
        assert not forbidden_marker.exists(), 'clock test escaped its controlled executable path'
        results.append('clock_tests_isolated_from_inherited_powershell')
    atomic(out, {'status': 'PASS', 'actual_process_tests': results,
                 'scope': 'synthetic finite CPU workload; same controller, separate test model'})
    print(json.dumps({'status': 'PASS', 'tests': results}), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
