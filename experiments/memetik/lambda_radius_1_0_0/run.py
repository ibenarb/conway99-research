"""Frozen Ryzen radius campaign: launch, resume, status, pause and export."""
import boot
from support import *
from campaign import campaign
import argparse
import importlib.metadata
import shutil
import tarfile


def lock(run):
    stream = (run / 'controller.lock').open('a+')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return stream


def environment():
    if importlib.metadata.version('pynauty') != '2.8.8.1':
        raise RuntimeError('Requires existing pynauty==2.8.8.1; no environment changes performed')
    return {'python': sys.version, 'pynauty': '2.8.8.1'}


def frozen(run):
    return run / 'program/experiments/memetik/lambda_radius_1_0_0/run.py'


def prepare(run):
    fingerprint = package_verify()
    env = environment()
    if run.exists():
        raise FileExistsError('Existing run is never overwritten; use launch/status for the same frozen run')
    run.mkdir(parents=True)
    p = read(boot.HERE / 'PACKAGE.json')
    names = list(p['files']) + ['experiments/memetik/lambda_radius_1_0_0/PACKAGE.json']
    for name in names:
        dest = run / 'program' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(boot.ROOT / name, dest)
    atomic(run / 'FINGERPRINT.json', {'package_sha256': fingerprint, 'environment': env,
                                    'limits': {'aux_cpu_h': 2, '2076_cpu_h': 20, '2077_cpu_h': 20, 'host_wall_h': 8}})
    if own_cpu() > 10:
        raise RuntimeError('Preparation exceeded reserved 10 CPU seconds')
    atomic(run / 'ledger.json', {'used': {'aux': 10.0, '2076': 0.0, '2077': 0.0},
                                'host_wall_seconds': 0.0, 'sessions': [], 'active': {},
                                'cli_reservations': [{'action': 'prepare', 'reserved_cpu': 10, 'measured_before_exit': own_cpu()}]})
    print('RADIUS_PREPARED ' + str(run), flush=True)


def verify_run(run):
    p = read(run / 'FINGERPRINT.json')
    if p['package_sha256'] != package_verify() or p['environment'] != environment():
        raise RuntimeError('Frozen source/interpreter fingerprint mismatch')
    if (run / 'HOST_START_FAILED.json').exists():
        raise RuntimeError('Windows host clock previously failed; diagnosis required')
    active = read(run / 'ledger.json').get('active') if (run / 'ledger.json').exists() else None
    if (run / 'session_active.json').exists() or active:
        raise RuntimeError('Unresolved session; diagnosis required before resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'launch', 'run', 'status', 'pause', 'export'))
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    run = args.directory.expanduser().resolve()
    if args.action == 'prepare':
        prepare(run)
        return
    if args.action == 'status':
        print(json.dumps(read(run / 'status.json') if (run / 'status.json').exists() else {'status': 'PREPARED_NOT_STARTED'}, indent=2))
        return
    if Path(__file__).resolve() != frozen(run):
        os.execv(sys.executable, [sys.executable, str(frozen(run)), *sys.argv[1:]])
    if args.action == 'pause':
        launch = read(run / 'launcher.json')
        live = process(launch['pid'])
        if live['start_ticks'] is None or live['start_ticks'] != launch['start_ticks']:
            raise RuntimeError('No matching owned controller')
        os.kill(launch['pid'], signal.SIGTERM)
        print('PAUSE_REQUEST_SENT')
        return
    inherited = os.environ.pop('CONWAY_RADIUS_LOCK_FD', None)
    if inherited is not None and args.action == 'run':
        owner = os.fdopen(int(inherited), 'a+')
        if os.fstat(owner.fileno()).st_ino != (run / 'controller.lock').stat().st_ino:
            raise RuntimeError('Lock handoff invalid')
    else:
        owner = lock(run)
    try:
        verify_run(run)
        if args.action == 'launch':
            if (run / 'RESULT.json').exists():
                result = read(run / 'RESULT.json')
                if result['status'] not in ('INCOMPLETE',):
                    raise RuntimeError('Run finished or requires diagnosis; no automatic new campaign')
            if 'WSL_DISTRO_NAME' not in os.environ or not shutil.which('powershell.exe'):
                raise RuntimeError('Production requires Windows host clock in Ryzen WSL')
            ledger = read(run / 'ledger.json')
            if ledger['used']['aux'] + 10 > 7170 or own_cpu() > 9:
                raise RuntimeError('Insufficient helper budget for launch')
            ledger['used']['aux'] += 10
            ledger['cli_reservations'].append({'action': 'launch', 'reserved_cpu': 10, 'measured_before_spawn': own_cpu()})
            atomic(run / 'ledger.json', ledger)
            with (run / 'controller.log').open('ab') as log:
                proc = subprocess.Popen([sys.executable, str(frozen(run)), 'run', str(run)],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        start_new_session=True, pass_fds=(owner.fileno(),),
                                        env={**os.environ, 'CONWAY_RADIUS_LOCK_FD': str(owner.fileno()), 'PYTHONNOUSERSITE': '1'})
            atomic(run / 'launcher.json', {'pid': proc.pid, 'start_ticks': process(proc.pid)['start_ticks']})
            print('RADIUS_LAUNCHED ' + json.dumps({'pid': proc.pid, 'log': str(run / 'controller.log'),
                                                'note': 'controls and depth3 gates run autonomously before depth4'}), flush=True)
        elif args.action == 'run':
            campaign(run)
        elif args.action == 'export':
            if not (run / 'RESULT.json').exists():
                raise RuntimeError('No final/paused result to export')
            dest = run.parent / (run.name + '_results.tar.gz')
            if dest.exists():
                raise FileExistsError(dest)
            tmp = Path(str(dest) + '.partial')
            with tarfile.open(tmp, 'w:gz') as z:
                z.add(run, arcname=run.name)
            os.replace(tmp, dest)
            Path(str(dest) + '.sha256').write_text(digest(dest) + '  ' + dest.name + '\n')
            print(json.dumps({'archive': str(dest), 'sha256': digest(dest)}))
    finally:
        owner.close()


if __name__ == '__main__':
    main()
