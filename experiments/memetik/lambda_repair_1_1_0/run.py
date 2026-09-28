"""Frozen campaign launch, resume, status, pause, verification and export."""
import argparse
import fcntl
import shutil
import signal
import subprocess
import sys
import tarfile
from common import *


def frozen(run):
    return run / 'program' / 'run.py'


def lock(run):
    stream = (run / 'controller.lock').open('a+')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return stream


def prepare(run):
    fingerprint = verify_package()
    dependencies = environment()
    if run.exists():
        raise FileExistsError('Existing run is never overwritten')
    run.mkdir(parents=True)
    files = list(read(HERE / 'PACKAGE.json')['files']) + ['PACKAGE.json']
    for name in files:
        destination = run / 'program' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, destination)
    manifest = read(HERE / 'MANIFEST.json')
    atomic(run / 'FINGERPRINT.json', {'package_sha256': fingerprint, 'dependencies': dependencies,
                                     'python': sys.version, 'interpreter': sys.executable,
                                     'manifest_sha256': digest(HERE / 'MANIFEST.json')})
    atomic(run / 'ledger.json', {'used': {'aux': 30, **{t['id']: 0 for t in manifest['tasks']}},
                                'done': {}, 'active': {}, 'receipts': [], 'sessions': [], 'next_attempt': 1,
                                'host_wall_seconds': 0, 'cli_reservations': [{'action': 'prepare', 'cpu_seconds': 30}]})
    if cpu() > 29:
        raise RuntimeError('Preparation exceeded reserved CPU; diagnose, do not launch')
    print('REPAIR_PREPARED ' + str(run), flush=True)


def verify_run(run):
    expected = read(run / 'FINGERPRINT.json')
    if expected['package_sha256'] != verify_package() or expected['dependencies'] != environment():
        raise RuntimeError('Frozen package/environment mismatch')
    if expected['python'] != sys.version or expected['interpreter'] != sys.executable:
        raise RuntimeError('Frozen Python interpreter changed')
    ledger = read(run / 'ledger.json')
    if ledger['active'] or (run / 'session_active.json').exists():
        raise RuntimeError('Unresolved session. No automatic reuse of unreceipted CPU')
    if (run / 'HOST_START_FAILED.json').exists():
        raise RuntimeError('Host clock failed: diagnosis required')
    return ledger


def reserve(run, action, amount=10):
    ledger = read(run / 'ledger.json')
    if ledger['used']['aux'] + amount > 43100 or cpu() >= amount - 1:
        raise RuntimeError('Insufficient auxiliary allowance')
    ledger['used']['aux'] += amount
    ledger['cli_reservations'].append({'action': action, 'cpu_seconds': amount})
    atomic(run / 'ledger.json', ledger)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'launch', 'run', 'status', 'pause', 'verify', 'export'))
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    run = args.directory.expanduser().resolve()
    if args.action == 'prepare':
        prepare(run)
        return
    if args.action == 'status':
        value = read(run / 'status.json') if (run / 'status.json').exists() else {'status': 'PREPARED_NOT_STARTED'}
        print(json.dumps(value, indent=2))
        return
    if Path(__file__).resolve() != frozen(run):
        os.execv(sys.executable, [sys.executable, str(frozen(run)), args.action, str(run)])
    if args.action == 'pause':
        launcher = read(run / 'launcher.json')
        if process(launcher['pid'])['start_ticks'] != launcher['start_ticks']:
            raise RuntimeError('Owned controller is not running')
        os.kill(launcher['pid'], signal.SIGTERM)
        print('REPAIR_PAUSE_REQUESTED')
        return
    inherited = os.environ.pop('CONWAY_REPAIR_LOCK_FD', None)
    owner = os.fdopen(int(inherited), 'a+') if inherited and args.action == 'run' else lock(run)
    if os.fstat(owner.fileno()).st_ino != (run / 'controller.lock').stat().st_ino:
        raise RuntimeError('Lock handoff mismatch')
    try:
        ledger = verify_run(run)
        if args.action == 'launch':
            if int(Path('/proc/self/stat').read_text().split()[0]) != os.getpid():
                raise RuntimeError('Unsupported PID/procfs namespace: resource monitoring cannot be trusted')
            if not os.environ.get('WSL_DISTRO_NAME') or not shutil.which('powershell.exe'):
                raise RuntimeError('Production requires Ryzen WSL and Windows PowerShell host clock')
            if (run / 'RESULT.json').exists():
                previous = read(run / 'RESULT.json')
                if previous['status'] != 'PAUSED_OR_INCOMPLETE' or previous['reason'] != 'USER_PAUSE':
                    raise RuntimeError('Finished campaign or diagnosis required; no automatic budget extension')
                os.replace(run / 'RESULT.json', run / f'RESULT_before_session_{len(ledger["sessions"])}.json')
            reserve(run, 'launch')
            with (run / 'controller.log').open('ab') as log:
                proc = subprocess.Popen([sys.executable, str(frozen(run)), 'run', str(run)],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, **THREAD_ENV, 'PYTHONNOUSERSITE': '1', 'CONWAY_REPAIR_LOCK_FD': str(owner.fileno())},
                                        start_new_session=True, pass_fds=(owner.fileno(),))
            atomic(run / 'launcher.json', process(proc.pid))
            print('REPAIR_LAUNCHED ' + json.dumps({'pid': proc.pid, 'directory': str(run), 'log': str(run / 'controller.log')}), flush=True)
        elif args.action == 'run':
            from controller import Controller
            Controller(run).execute()
        elif args.action == 'verify':
            from audit import audit
            reserve(run, 'verify', 60)
            result = audit(run)
            atomic(run / 'AUDIT.json', result)
            print(json.dumps(result))
        elif args.action == 'export':
            if not (run / 'RESULT.json').exists():
                raise RuntimeError('Export only after stop/completion')
            from audit import audit
            reserve(run, 'export', 120)
            atomic(run / 'AUDIT.json', audit(run))
            destination = run.parent / (run.name + '_results.tar.gz')
            if destination.exists() or Path(str(destination) + '.partial').exists():
                raise FileExistsError('Export destination exists; never overwrite')
            temporary = Path(str(destination) + '.partial')
            with tarfile.open(temporary, 'w:gz') as archive:
                archive.add(run, arcname=run.name)
            os.replace(temporary, destination)
            hash_value = digest(destination)
            Path(str(destination) + '.sha256').write_text(hash_value + '  ' + destination.name + '\n')
            if cpu() > 119:
                raise RuntimeError('Export exceeded reserved CPU; archive retained, diagnosis required')
            print(json.dumps({'archive': str(destination), 'sha256': hash_value}))
    finally:
        owner.close()


if __name__ == '__main__':
    main()
