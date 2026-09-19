"""Controller lifecycle tests using disposable child processes, no C99 search."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from office_pilot import run_job, windows_free


def check():
    if not __debug__:
        raise RuntimeError('Assertions required')
    records = []
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
