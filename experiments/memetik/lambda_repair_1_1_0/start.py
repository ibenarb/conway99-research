"""Fresh pilot 1.1.0. Existing runs and environments are never rewritten."""
import argparse
import fcntl
import os
from pathlib import Path
import shutil
import subprocess
import sys
from common import *


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    workspace = Path.home() / 'conway99_workspace'
    expected = workspace / 'venvs/lambda-repair-1.0.0/bin/python'
    if Path(sys.executable).absolute() != expected:
        raise RuntimeError('Use the existing dedicated solver Python: ' + str(expected))
    verify_package()
    environment()
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError('Python 3.12 is required')
    run = workspace / 'ryzen_lambda_repair_110_20260928'
    if run.exists():
        raise FileExistsError('Fresh run already exists. Inspect status; never rerun this starter.')
    if not args.prepare_only and (not os.environ.get('WSL_DISTRO_NAME') or not shutil.which('powershell.exe')):
        raise RuntimeError('Ryzen WSL and Windows PowerShell required')
    locks = []
    try:
        for name in ('ryzen_lambda_repair_100_20260927', 'ryzen_lambda_repair_100_20260927_recovery_101'):
            old = workspace / name
            if old.exists():
                if (old / 'session_active.json').exists() or read(old / 'ledger.json')['active']:
                    raise RuntimeError('An older repair run has an unresolved/active session: ' + name)
                handle = (old / 'controller.lock').open('rb')
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locks.append(handle)
        subprocess.run([sys.executable, str(HERE / 'run.py'), 'prepare', str(run)], check=True)
        state = read(run / 'ledger.json')
        state['used']['aux'] += 30
        state['cli_reservations'].append({'action': 'fresh_start_setup', 'cpu_seconds': 30})
        atomic(run / 'ledger.json', state)
        atomic(run / 'FRESH_START.json', {'version': '1.1.0', 'mode': 'NEW_EXPERIMENT',
                                         'inherited_task_results': False, 'inherited_cpu': False,
                                         'technical_predecessor': '1.0.0 stopped 2026-09-27',
                                         'manifest_sha256': digest(HERE / 'MANIFEST.json'),
                                         'policy_sha256': digest(HERE / 'BUDGET_POLICY.json')})
        if cpu() >= 29:
            raise RuntimeError('Setup CPU exceeded its reservation; preserve prepared run and diagnose')
        print('FRESH_REPAIR_PREPARED ' + str(run), flush=True)
        if not args.prepare_only:
            subprocess.run([sys.executable, str(run / 'program/run.py'), 'launch', str(run)], check=True)
    finally:
        for handle in locks:
            handle.close()


if __name__ == '__main__':
    main()
