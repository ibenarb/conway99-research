"""Actual subprocess GC-19/GC-15 regression suite. No wall-time experiment stops."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

from census import audit_start, export, initialise
from runtime import BASE, answer, atomic, connect, get


def until(predicate):
    # Test harness polling; no worker deadline. A failure remains observable in logs.
    while True:
        result = predicate()
        if result:
            return result
        time.sleep(.05)


def launch(run):
    log = (run / ('test-' + str(time.time_ns()) + '.log')).open('w')
    proc = subprocess.Popen([sys.executable, str(BASE / 'census.py'), 'run', str(run)],
                            stdin=subprocess.DEVNULL, stdout=log, stderr=log)
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
        results.append('open_request_survives_signal_resume')
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
    atomic(out, {'status': 'PASS', 'actual_process_tests': results,
                 'scope': 'synthetic finite CPU workload; same controller, separate test model'})
    print(json.dumps({'status': 'PASS', 'tests': results}), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
