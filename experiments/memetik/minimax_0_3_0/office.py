"""Office minimax campaign, two workers and a shared absolute deadline."""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import zipfile

from minimax import VERSION, TERMINAL, seed_database, run_worker
from search import atomic

BASE = Path.home()/'conway99_workspace/conway99_minimax_office_0.3.0'
NAMES = ('HoG57338__bfs_F', 'B_escape_W2082__bfs_W')


def payload(name):
    if zipfile.is_zipfile(sys.argv[0]):
        with zipfile.ZipFile(sys.argv[0]) as z:
            return z.read(name)
    return (Path(__file__).parent/name).read_bytes()


def preflight():
    manifest = json.loads(payload('manifest.json'))
    assert manifest['version'] == VERSION
    for name, digest in manifest['files'].items():
        assert hashlib.sha256(payload(name)).hexdigest() == digest, name
    return manifest


def seeds():
    return {name: json.loads(gzip.decompress(payload(name+'.seed.json.gz'))) for name in NAMES}


def resolve_run(explicit):
    return Path(explicit).resolve() if explicit else Path(json.loads((BASE/'active.json').read_text())['run_dir'])


def locked(path):
    file = Path(path).open('a')
    fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return file


def controller(directory):
    directory = Path(directory).resolve()
    lock = locked(directory/'controller.lock')
    manifest = preflight()
    config = json.loads((directory/'config.json').read_text())
    assert manifest == config['manifest'] and config['version'] == VERSION
    all_seeds = seeds()
    context = multiprocessing.get_context('fork')
    processes = {}
    stopping = False
    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    for name in NAMES:
        worker = context.Process(target=run_worker, args=(str(directory), all_seeds[name], config), name=name)
        worker.start()
        processes[name] = worker
    last_report = 0
    sent_stop = False
    started = time.monotonic()
    while True:
        if stopping and not sent_stop:
            for worker in processes.values():
                if worker.is_alive():
                    os.kill(worker.pid, signal.SIGTERM)
            sent_stop = True
        summary = {}
        active = []
        for name, worker in processes.items():
            path = directory/(name+'.json')
            state = json.loads(path.read_text()) if path.exists() else {'status': 'STARTING'}
            if worker.is_alive():
                active.append({'task': name, 'pid': worker.pid, **{k: state.get(k) for k in ('status', 'discovered', 'expanded', 'frontier_peak', 'necessary_barrier_at_least', 'cpu_seconds')}})
            else:
                worker.join()
                if worker.exitcode or state['status'] in ('RUNNING', 'PREPARED', 'STARTING'):
                    state = {**state, 'status': 'INTERRUPTED', 'worker_exitcode': worker.exitcode}
                summary[name] = state
        remaining = max(0, config['deadline_epoch']-time.time())
        status = {'phase': 'SEARCH' if active else ('FINISHED' if all(s['status'] in TERMINAL for s in summary.values()) else 'STOPPED'), 'version': VERSION, 'elapsed_wall_seconds_since_launch': round(time.time()-config['started_epoch']), 'session_seconds': round(time.monotonic()-started), 'deadline_utc': config['deadline_utc'], 'remaining_wall_seconds': round(remaining), 'done': len(summary), 'total': 2, 'active': active, 'statuses': {n: s['status'] for n, s in summary.items()}, 'eta_scope': 'Time to shared campaign deadline; not an estimate of mathematical success.'}
        atomic(directory/'summary.json', summary)
        atomic(directory/'status.json', status)
        if not active or time.monotonic()-last_report >= 600:
            print(json.dumps(status), flush=True)
            last_report = time.monotonic()
        if not active:
            break
        time.sleep(2)


def launch(directory):
    # Early lock check prevents a second controller; the controller also locks.
    probe = locked(directory/'controller.lock')
    probe.close()
    with (directory/'console.log').open('ab') as log:
        process = subprocess.Popen([sys.executable, str(Path(sys.argv[0]).resolve()), 'run', '--run-dir', str(directory)], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    record = {'pid': process.pid, 'run_dir': str(directory), 'log': str(directory/'console.log')}
    atomic(BASE/'active.json', record)
    for _ in range(100):
        if process.poll() is not None:
            if process.returncode:
                raise RuntimeError('Startup failed; inspect '+record['log'])
            break
        state = json.loads((directory/'status.json').read_text())
        if state['phase'] in ('SEARCH', 'FINISHED', 'STOPPED'):
            break
        time.sleep(0.1)
    print(json.dumps(record, indent=4))


def export(directory):
    probe = locked(directory/'controller.lock')
    for name in NAMES:
        worker_probe = locked(directory/(name+'.lock'))
        worker_probe.close()
    state = json.loads((directory/'status.json').read_text())
    if state['phase'] not in ('FINISHED', 'STOPPED'):
        raise ValueError('Use status/resume first; export requires a stopped campaign')
    target = Path('/mnt/c/Users/rb/Downloads')
    if not target.is_dir():
        target = BASE
    archive = target/('Ergebnisse_Minimax_030_'+directory.name+'.zip')
    temporary = archive.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(directory.iterdir()):
            if path.suffix in ('.json', '.sqlite', '.log'):
                z.write(path, path.name)
        z.write(Path(sys.argv[0]).resolve(), 'Conway99_Minimax_Office_0.3.0.pyz')
    os.replace(temporary, archive)
    digest = hashlib.sha256()
    with archive.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': digest.hexdigest()}, indent=4))
    probe.close()


def main():
    global BASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('start', 'status', 'resume', 'export', 'verify', 'run'))
    parser.add_argument('--hours', type=float, default=34)
    parser.add_argument('--run-dir')
    parser.add_argument('--base-dir', type=Path)
    args = parser.parse_args()
    if args.base_dir is not None:
        BASE = args.base_dir.resolve()
    if args.mode == 'run':
        assert args.run_dir
        controller(args.run_dir)
        return
    if args.mode == 'verify':
        preflight()
        print('PASS: source and seed manifests; no campaign started')
        return
    BASE.mkdir(parents=True, exist_ok=True)
    if args.mode == 'status':
        directory = resolve_run(args.run_dir)
        print(json.dumps({'run_dir': str(directory), 'status': json.loads((directory/'status.json').read_text()), 'summary': json.loads((directory/'summary.json').read_text()) if (directory/'summary.json').exists() else {}}, indent=4))
        return
    if args.mode == 'export':
        export(resolve_run(args.run_dir))
        return
    launch_lock = locked(BASE/'launch.lock')
    manifest = preflight()
    if args.mode == 'resume':
        directory = resolve_run(args.run_dir)
        config = json.loads((directory/'config.json').read_text())
        assert config['manifest'] == manifest
        state = json.loads((directory/'status.json').read_text())
        if state['phase'] == 'FINISHED':
            raise ValueError('Campaign finished; use export. Resume never grants a new budget.')
        launch(directory)
        return
    if not 0 < args.hours <= 34:
        raise ValueError('Require 0 < hours <= 34')
    active = BASE/'active.json'
    if active.exists():
        previous = Path(json.loads(active.read_text())['run_dir'])
        if (previous/'status.json').exists() and json.loads((previous/'status.json').read_text())['phase'] != 'FINISHED':
            raise ValueError('Existing campaign is unfinished; use status/resume')
    if any(shutil.disk_usage(p).free < 10*2**30 for p in [BASE]+([Path('/mnt/c')] if Path('/mnt/c').is_dir() else [])):
        raise RuntimeError('DISK_FLOOR')
    directory = Path(args.run_dir).resolve() if args.run_dir else BASE/'runs'/datetime.datetime.now().strftime('minimax_%Y%m%d_%H%M%S_%f')
    directory.mkdir(parents=True, exist_ok=False)
    started = time.time()
    deadline = started+args.hours*3600
    config = {'version': VERSION, 'manifest': manifest, 'started_epoch': started, 'deadline_epoch': deadline, 'deadline_utc': datetime.datetime.fromtimestamp(deadline, datetime.timezone.utc).isoformat(), 'workers': 2, 'wall_hours': args.hours, 'memory_mib_per_worker': 896, 'disk_floor_gib': 10, 'system_memory_floor_mib': 512}
    atomic(directory/'config.json', config)
    for name, seed in seeds().items():
        state = seed_database(directory/(name+'.sqlite'), seed, config)
        atomic(directory/(name+'.json'), state)
    atomic(directory/'status.json', {'phase': 'PREPARED', 'version': VERSION})
    launch(directory)


if __name__ == '__main__':
    main()
