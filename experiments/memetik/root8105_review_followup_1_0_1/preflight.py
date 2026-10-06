import bootstrap
"""Accounted new-package validation. WSL host probe under three minutes of load."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from runtime import (BASE, atomic, budget_tick, close_requests, connect, fingerprint, get, put,
                     process_stat, require_local_filesystem, resources, read_host_clock)


def clock_load(run, con, already_cpu):
    from census import start_host_clock, stop_host_clock
    from clock_diagnostics import ClockDiagnostics
    if 'microsoft' not in Path('/proc/sys/kernel/osrelease').read_text().lower():
        return {'status': 'NOT_WSL', 'windows_cpu_s': 0, 'target_hardware_test': False}
    tag = 'preflight-load'
    host = log = None
    workers, samples = [], []
    path = run / ('host-clock-' + tag + '.json')
    stop_path = run / ('host-stop-' + tag)
    load_stop = run / 'load-stop'
    begun = time.monotonic()
    clocks = ClockDiagnostics(begun, time.time(), True)
    warnings = []
    try:
        host, log = start_host_clock(run, tag)
        code = "from pathlib import Path; import sys; p=Path(sys.argv[1]);\nwhile not p.exists(): sum(i*i for i in range(20000))"
        workers = [subprocess.Popen([sys.executable, '-c', code, str(load_stop)], stdin=subprocess.DEVNULL)
                   for _ in range(2)]
        # Finite diagnostic work, not a search timeout. CPU still uses GC-19.
        while time.monotonic() - begun < 180:
            fresh, error = read_host_clock(path)
            d = clocks.observe(time.monotonic(), time.time(), fresh, error)
            samples.append(d)
            atomic(run / 'preflight_clock_diagnostics.json', {'samples': samples})
            children = resource.getrusage(resource.RUSAGE_CHILDREN)
            active_cpu = sum((process_stat(p.pid) or {}).get('cpu_s', 0) for p in workers)
            budget_tick(con, run, already_cpu + time.process_time() + children.ru_utime + children.ru_stime
                        + active_cpu + (fresh['cpu_s'] if fresh else 0))
            print('CLOCK_LOAD ' + json.dumps(d), flush=True)
            if get(con, 'stop_requested', False):
                break
            time.sleep(5)
    except (OSError, subprocess.SubprocessError) as exc:
        warnings.append(repr(exc))
    finally:
        load_stop.touch()
        for proc in workers:
            proc.wait()
        if host:
            warnings.extend(stop_host_clock(host, log, stop_path, 60))
    final, error = read_host_clock(path)
    return {'status': 'PASS' if samples and samples[-1]['ok'] and not warnings else 'ETA_UNKNOWN',
            'windows_cpu_s': final['cpu_s'] if final else 0,
            'cpu_lower_bound': bool(host and (final is None or warnings)),
            'warnings': warnings, 'last_diagnostic': samples[-1] if samples else None,
            'samples': len(samples), 'target_hardware_test': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    con = connect(run)
    if get(con, 'fingerprint') != fingerprint() or get(con, 'preflight'):
        raise ValueError('fingerprint changed or preflight already recorded')
    require_local_filesystem(run)
    available = resources(run)
    if available['mem_available_bytes'] < 4 * 2 ** 30 or available['disk_free_bytes'] < 2 * 2 ** 30:
        raise ValueError('preflight needs >=4 GiB available RAM and >=2 GiB disk')
    expected = dict(line.strip().split('==') for line in (BASE / 'requirements.txt').read_text().splitlines() if line.strip())
    if any(importlib.metadata.version(n) != v for n, v in expected.items()):
        raise ValueError('dependency version mismatch')
    started_cpu = get(con, 'auxiliary_cpu_s', 0)
    # Persistent marker: after a crash, never silently treat missing preflight CPU as zero.
    marker = run / 'preflight_running.json'
    if marker.exists():
        raise ValueError('unfinished preflight; preserve run and create a new run')
    atomic(marker, {'pid': os.getpid(), 'started': time.time(), 'cpu_is_lower_bound': True})
    records, probe = [], {'windows_cpu_s': 0}
    failure = None
    try:
        for script in ('checks.py', 'pilot_tests.py', 'operations_test.py', 'recovery_test.py'):
            with (run / (script + '.log')).open('w') as log:
                proc = subprocess.Popen([sys.executable, str(BASE / script), str(run / (script + '.json'))],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                    env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
                while True:
                    pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
                    children = resource.getrusage(resource.RUSAGE_CHILDREN)
                    live = 0 if pid else (process_stat(proc.pid) or {}).get('cpu_s', 0)
                    budget_tick(con, run, started_cpu + time.process_time() + children.ru_utime + children.ru_stime + live)
                    if pid:
                        break
                    time.sleep(.25)
                proc.returncode = os.waitstatus_to_exitcode(status)
            records.append({'script': script, 'cpu_s_wait4': usage.ru_utime + usage.ru_stime,
                            'returncode': proc.returncode})
            if proc.returncode or get(con, 'stop_requested', False):
                raise RuntimeError('preflight failed or explicit stop at control boundary: ' + script)
            print('PREFLIGHT_CONTROL_PASS ' + script, flush=True)
        probe = clock_load(run, con, started_cpu)
        if get(con, 'stop_requested', False):
            raise RuntimeError('USER_BUDGET_ZERO')
    except BaseException as exc:
        failure = repr(exc)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    spent = time.process_time() + children.ru_utime + children.ru_stime + probe['windows_cpu_s']
    result = {'status': 'FAIL' if failure else 'PASS', 'error': failure, 'records': records,
              'cpu_s': spent, 'dependencies': expected, 'fingerprint': fingerprint(),
              'host_clock_probe': probe, 'resources': available, 'utc': time.time()}
    with con:
        put(con, 'auxiliary_cpu_s', started_cpu + spent)
        if probe.get('cpu_lower_bound'):
            put(con, 'cpu_lower_bound', True)
        if not failure:
            put(con, 'preflight', result)
    atomic(run / 'preflight.json', result)
    marker.unlink()
    if get(con, 'stop_requested', False):
        close_requests(con, 'CLOSED_USER_BUDGET_ZERO')
    con.close()
    print('PREFLIGHT_' + result['status'] + ' ' + json.dumps(result), flush=True)
    if failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
