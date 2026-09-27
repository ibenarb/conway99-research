"""Create a new pinned solver environment and frozen run; never change memetik."""
import argparse
import fcntl
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path.home() / 'conway99_workspace')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12) or platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('This wheel lock requires Ubuntu x86_64 / Python 3.12')
    if not args.prepare_only and (not os.environ.get('WSL_DISTRO_NAME') or not shutil.which('powershell.exe')):
        raise RuntimeError('Ryzen WSL / Windows host clock required before launch')
    package = json.loads((HERE / 'PACKAGE.json').read_text())
    for name, expected in package['files'].items():
        if sha(HERE / name) != expected:
            raise RuntimeError('Package hash mismatch: ' + name)
    root = args.workspace.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    run = root / 'ryzen_lambda_repair_100_20260927'
    if run.exists():
        raise FileExistsError('Run exists; use its documented status/resume commands, never rerun start.py')
    env = root / 'venvs' / 'lambda-repair-1.0.0'
    env.parent.mkdir(exist_ok=True)
    fingerprint = sha(HERE / 'requirements.lock')
    with (env.parent / 'lambda-repair-1.0.0.setup.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if env.exists():
            marker = env / 'REPAIR_ENV.json'
            if not marker.exists() or json.loads(marker.read_text())['requirements_sha256'] != fingerprint:
                raise RuntimeError('Unfinished/different dedicated environment. Preserve and diagnose; no overwrite.')
        else:
            venv.EnvBuilder(with_pip=True).create(env)
            python = env / 'bin/python'
            subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '--require-hashes',
                            '--only-binary=:all:', '-r', str(HERE / 'requirements.lock')], check=True,
                           env={**os.environ, 'PYTHONNOUSERSITE': '1'})
            (env / 'REPAIR_ENV.json').write_text(json.dumps({'requirements_sha256': fingerprint}) + '\n')
        python = env / 'bin/python'
        subprocess.run([str(python), '-m', 'pip', 'check'], check=True)
        own = resource.getrusage(resource.RUSAGE_SELF)
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        setup_cpu = own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime
        subprocess.run([str(python), str(HERE / 'run.py'), 'prepare', str(run)], check=True)
        from common import atomic, read
        ledger = read(run / 'ledger.json')
        ledger['used']['aux'] += setup_cpu
        ledger['cli_reservations'].append({'action': 'bootstrap_setup', 'cpu_seconds': setup_cpu})
        atomic(run / 'ledger.json', ledger)
    if args.prepare_only:
        print('Prepared only: ' + str(run))
    else:
        subprocess.run([str(python), str(run / 'program/run.py'), 'launch', str(run)], check=True)


if __name__ == '__main__':
    main()
