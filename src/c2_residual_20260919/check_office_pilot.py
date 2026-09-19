"""Controller lifecycle tests using disposable child processes, no C99 search."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from office_pilot import classify_exit, run_job, windows_free


def check():
    if not __debug__:
        raise RuntimeError('Assertions required')
    records = []
    alarm_log = ('c setting time limit to 55 seconds real time (due to \'-t 55\')\n'
                 'c raising signal 14 (SIGALRM)\n')
    assert classify_exit(-14, alarm_log, 55.109039233997464, 50.75014,
                         solver_wall_limit=55) == 'WALL_TIME_LIMIT'
    assert classify_exit(-14, alarm_log, 20, 15, solver_wall_limit=55) == 'EXECUTION_ERROR'
    assert classify_exit(-14, alarm_log, 55.1, 50.7) == 'EXECUTION_ERROR'
    assert classify_exit(-15, alarm_log, 55.1, 50.7, solver_wall_limit=55) == 'EXECUTION_ERROR'
    assert classify_exit(-14, 'c raising signal 14 (SIGALRM)\n', 55.1, 50.7,
                         solver_wall_limit=55) == 'EXECUTION_ERROR'
    assert classify_exit(-14, alarm_log+'s UNSATISFIABLE\n', 55.1, 50.7,
                         solver_wall_limit=55) == 'EXECUTION_ERROR'
    records.append({'control': 'field_alarm_and_five_negative_controls', 'status': 'PASS'})
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        fixtures = [
            ('sat', 'print("s SATISFIABLE"); raise SystemExit(10)', 'SAT_UNVERIFIED'),
            ('unsat', 'print("s UNSATISFIABLE"); raise SystemExit(20)', 'UNSAT_UNCERTIFIED'),
            ('unknown', 'print("c UNKNOWN")', 'UNKNOWN'),
            ('bad_code', 'print("s UNSATISFIABLE"); raise SystemExit(10)', 'EXECUTION_ERROR'),
            ('silent', 'pass', 'EXECUTION_ERROR'),
        ]
        for name, program, expected in fixtures:
            result = run_job([sys.executable, '-c', program], root / (name + '.log'), lambda: None)
            assert result['status'] == expected, result
            assert result['cpu_seconds'] >= 0 and result['peak_rss_bytes'] > 0
            records.append({'control': name, 'status': result['status']})
        program = ('import os,signal,time; '
                   'print("c setting time limit to 1 seconds real time",flush=True); '
                   'time.sleep(1); '
                   'print("c raising signal 14 (SIGALRM)",flush=True); '
                   'os.kill(os.getpid(),signal.SIGALRM)')
        result = run_job([sys.executable, '-c', program], root / 'alarm.log', lambda: None,
                         solver_wall_limit=1)
        assert result['status'] == 'WALL_TIME_LIMIT' and result['returncode'] == -14
        records.append({'control': 'real_alarm_child', 'status': result['status']})
        sleeping = [sys.executable, '-c', 'import time; time.sleep(20)']
        result = run_job(sleeping, root / 'wall.log', lambda: None, wall_limit=0.1)
        assert result['status'] == 'STOPPED_WALL_LIMIT' and result['wall_seconds'] < 5
        records.append({'control': 'wall_timeout', 'status': result['status']})
        result = run_job(sleeping, root / 'guard.log', lambda: 'RAM_RESERVE')
        assert result['status'] == 'STOPPED_RAM_RESERVE' and result['wall_seconds'] < 5
        records.append({'control': 'guard_abort', 'status': result['status']})
        # The old log must never be overwritten, and no new child is started.
        try:
            run_job(sleeping, root / 'guard.log', lambda: None)
        except FileExistsError:
            records.append({'control': 'existing_log', 'status': 'REJECTED'})
        else:
            raise AssertionError('Existing log overwritten')
        program = 'import os; block=b"x"*(1024*1024); [os.write(1,block) for _ in range(32)]'
        result = run_job([sys.executable, '-c', program], root / 'large.log', lambda: None)
        assert result['status'] == 'EXECUTION_ERROR' and result['log_bytes'] <= 16 * 1024**2
        records.append({'control': 'hard_output_limit', 'status': 'BOUNDED'})
    # Host measurements fail closed: neither unavailable output nor insufficient
    # actual Windows reserve is silently replaced by virtual Linux free space.
    with patch('office_pilot.shutil.which', return_value='/mock/powershell.exe'):
        for stdout in (b'not a number', b'1000'):
            with patch('office_pilot.subprocess.run', return_value=subprocess.CompletedProcess([], 0, stdout, b'')):
                try:
                    windows_free()
                except RuntimeError:
                    records.append({'control': 'bad_or_low_host_free', 'status': 'REJECTED'})
                else:
                    raise AssertionError('Bad host measurement accepted')
        with patch('office_pilot.subprocess.run', side_effect=subprocess.TimeoutExpired('powershell', 8)):
            try:
                windows_free()
            except RuntimeError:
                records.append({'control': 'host_probe_timeout', 'status': 'REJECTED'})
            else:
                raise AssertionError('Host timeout accepted')
    return {'status': 'OFFICE_PILOT_CONTROLLER_CONTROLS_PASS', 'controls': records,
            'runner_sha256': hashlib.sha256(Path(__file__).with_name('office_pilot.py').read_bytes()).hexdigest(),
            'scope': 'Local disposable process tests; no Office execution and no real solver pilot.'}


if __name__ == '__main__':
    result = check()
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
