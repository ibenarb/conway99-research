"""New isolated environment; verify package and exercise real parallel control path."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from runtime import (BASE, atomic, budget_tick, connect, fingerprint, get, put, resources, process_stat,
                     require_local_filesystem)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    con = connect(run)
    if get(con, 'fingerprint') != fingerprint():
        raise ValueError('code fingerprint mismatch')
    if get(con, 'preflight'):
        raise ValueError('preflight already recorded; do not double account')
    fstype = require_local_filesystem(run)  # K7: refuse 9p/drvfs/network/FUSE before any work
    available = resources(run)
    print('PREFLIGHT_RESOURCES ' + json.dumps(available), flush=True)
    if available['mem_available_bytes'] < 4 * 2 ** 30 or available['disk_free_bytes'] < 2 * 2 ** 30:
        raise ValueError('need >=4 GiB available RAM and >=2 GiB disk for preflight')
    expected = dict(line.strip().split('==') for line in (BASE / 'requirements.txt').read_text().splitlines() if line.strip())
    if any(importlib.metadata.version(name) != version for name, version in expected.items()):
        raise ValueError('dependency versions differ from tested requirements')
    child_cpu = 0
    records = []
    for script, report, extra in [('validate.py', 'preflight_math.json', ['--quick']),
                                   ('operations_test.py', 'preflight_operations.json', []),
                                   ('recovery_test.py', 'preflight_recovery.json', [])]:
        log = (run / (script + '.log')).open('w')
        proc = subprocess.Popen([sys.executable, str(BASE / script), str(run / report), *extra],
                                stdout=log, stderr=log, stdin=subprocess.DEVNULL,
                                env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'))
        while True:
            pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
            stat = process_stat(proc.pid) if not pid else None
            used = get(con, 'auxiliary_cpu_s', 0) + child_cpu + time.process_time()
            used += (usage.ru_utime + usage.ru_stime) if pid else (stat['cpu_s'] if stat else 0)
            budget_tick(con, run, used)
            if pid:
                break
            time.sleep(.25)
        proc.returncode = os.waitstatus_to_exitcode(status)
        log.close()
        cpu = usage.ru_utime + usage.ru_stime
        child_cpu += cpu
        records.append({'script': script, 'cpu_s_wait4': cpu, 'returncode': proc.returncode})
        if proc.returncode or get(con, 'stop_requested', False):
            children = resource.getrusage(resource.RUSAGE_CHILDREN)
            spent = children.ru_utime + children.ru_stime + time.process_time()
            atomic(run / 'preflight_failed.json', {'records': records, 'cpu_s': spent})
            with con:
                put(con, 'auxiliary_cpu_s', get(con, 'auxiliary_cpu_s', 0) + spent)
            raise RuntimeError(script + ' failed or was explicitly stopped at its atomic control boundary; preserved log ' + str(run / (script + '.log')))
    # K7: exercise the real Windows clock path once. Non-blocking: failures mean ETA unknown.
    is_wsl = 'microsoft' in Path('/proc/sys/kernel/osrelease').read_text().lower()
    if is_wsl:
        from census import host_clock_probe
        probe = host_clock_probe(run)
        if probe['status'] != 'PASS':
            print('PREFLIGHT_WARNING host clock ' + json.dumps(probe), flush=True)
    else:
        probe = {'status': 'NOT_WSL', 'windows_cpu_s': 0}
    children = resource.getrusage(resource.RUSAGE_CHILDREN)  # scripts, wslpath, interop helper
    result = {'status': 'PASS', 'resources': available, 'filesystem': fstype, 'host_clock_probe': probe,
              'records': records,
              'python': sys.version, 'dependencies': {n: importlib.metadata.version(n)
                  for n in ('numpy', 'pynauty', 'python-sat')}, 'fingerprint': fingerprint(),
              'cpu_s': children.ru_utime + children.ru_stime + time.process_time() + probe['windows_cpu_s'],
              'timestamp': time.time()}
    with con:
        put(con, 'auxiliary_cpu_s', get(con, 'auxiliary_cpu_s', 0) + result['cpu_s'])
        put(con, 'preflight', result)
    atomic(run / 'preflight.json', result)
    print('PREFLIGHT_PASS ' + json.dumps(result), flush=True)
    con.close()


if __name__ == '__main__':
    main()
