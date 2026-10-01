"""Start one pinned recovery segment without changing the interrupted original."""
import argparse
import shutil
import subprocess
import sys
from common import *
from recovery import prepare_recovery


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    workspace = Path.home() / 'conway99_workspace'
    expected = workspace / 'venvs/lambda-repair-1.0.0/bin/python'
    if Path(sys.executable).absolute() != expected or sys.version_info[:2] != (3, 12):
        raise RuntimeError('Use existing Python 3.12: ' + str(expected))
    verify_package()
    environment()
    if not args.prepare_only and (not os.environ.get('WSL_DISTRO_NAME') or not shutil.which('powershell.exe')):
        raise RuntimeError('Ryzen WSL and Windows PowerShell required')
    plan = read(HERE / 'RECOVERY_PLAN.json')
    archive = Path('/mnt/c/Users/rb/Downloads') / plan['archive_name']
    run = prepare_recovery(workspace, archive)
    if not args.prepare_only:
        subprocess.run([sys.executable, str(run / 'program/run.py'), 'launch', str(run)], check=True)


if __name__ == '__main__':
    main()
