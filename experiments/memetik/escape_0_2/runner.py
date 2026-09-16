"""Office follow-up: three isolated workers, detached execution, durable state."""
import argparse
import concurrent.futures
import datetime
import fcntl
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zipfile
from core import decode_g6
from search import VERSION, atomic, check_independent, execute


def payload(name):
    if zipfile.is_zipfile(sys.argv[0]):
        with zipfile.ZipFile(sys.argv[0]) as archive:
            return archive.read(name)
    return (Path(__file__).parent / name).read_bytes()


def founders():
    return json.loads(payload('founders.json'))


def preflight():
    for item in founders():
        assert hashlib.sha256((item['graph6'] + '\n').encode()).hexdigest() == item['sha256']
        check_independent(decode_g6(item['graph6']), item['arm'])
    manifest = json.loads(payload('manifest.json'))
    for name, digest in manifest['files'].items():
        assert hashlib.sha256(payload(name)).hexdigest() == digest, name
    return manifest


def tasks():
    items = [{'id': 'Codex_C08__neutral_W', 'founder': 'Codex_C08', 'mode': 'neutral', 'objective': 'W'},
             {'id': 'HoG57338__bfs_F', 'founder': 'HoG57338', 'mode': 'bfs', 'objective': 'F'},
             {'id': 'B_original__bfs_W', 'founder': 'B_original', 'mode': 'bfs', 'objective': 'W'}]
    for name in ('Codex_C02', 'B_end_F', 'lambda_Linf2'):
        for objective in ('L1', 'F', 'Linf', 'W'):
            items.append({'id': name + '__descent_' + objective, 'founder': name, 'mode': 'descent', 'objective': objective})
    return items


def run(args):
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    directory = Path(args.run_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    lock = (directory / 'run.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = preflight()
    selected = [t for t in tasks() if not args.only or t['id'] in args.only.split(',')]
    assert selected, 'No matching tasks'
    limits = {'cpu_seconds': args.cpu_seconds, 'max_states': args.max_states, 'max_depth': args.max_depth, 'max_descent_steps': args.max_descent_steps}
    config = {'version': VERSION, 'manifest': manifest, 'tasks': selected, 'limits': limits, 'workers': args.workers}
    config_path = directory / 'config.json'
    if config_path.exists():
        assert json.loads(config_path.read_text()) == config, 'Changed configuration; use a new run directory'
    else:
        atomic(config_path, config)
    items = {f['id']: f for f in founders()}
    results = {}
    started = time.monotonic()
    atomic(directory / 'status.json', {'phase': 'STARTED', 'total': len(selected), 'version': VERSION})
    last_print = -1000
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('fork')) as pool:
        pending = {pool.submit(execute, task, items[task['founder']], directory, limits): task['id'] for task in selected}
        while pending:
            completed, _ = concurrent.futures.wait(pending, timeout=10, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in completed:
                name = pending.pop(future)
                try:
                    result = future.result()
                    results[name] = {k: v for k, v in result.items() if k != 'witness'}
                    if 'witness' in result:
                        results[name]['path_length'] = result['witness']['path_length']
                        results[name]['endpoint'] = result['witness']['path'][-1]['metrics']
                        results[name]['barrier_above_start'] = result['witness'].get('barrier_above_start')
                except Exception as error:
                    results[name] = {'status': 'WORKER_ERROR', 'error': repr(error)}
            active = []
            remaining = 0
            for name in pending.values():
                path = directory / (name + '.json')
                state = json.loads(path.read_text()) if path.exists() else {}
                used = state.get('cpu_seconds', 0)
                remaining += max(0, args.cpu_seconds - used)
                if state:
                    active.append({'task': name, 'cpu_seconds': round(used), 'status': state['status']})
            status = {'phase': 'SEARCH', 'version': VERSION, 'elapsed_seconds': round(time.monotonic() - started), 'done': len(results), 'total': len(selected), 'active': active, 'remaining_cpu_budget_seconds': round(remaining), 'ideal_remaining_budget_hours': round(remaining / args.workers / 3600, 3), 'eta_scope': 'Remaining budget at full utilization; not a solution ETA.'}
            atomic(directory / 'status.json', status)
            atomic(directory / 'summary.json', results)
            if time.monotonic() - last_print >= 600:
                print(json.dumps(status), flush=True)
                last_print = time.monotonic()
    atomic(directory / 'summary.json', results)
    final = {'phase': 'FOLLOWUP_FINISHED', 'version': VERSION, 'tasks': len(results), 'statuses': {name: data['status'] for name, data in results.items()}, 'elapsed_seconds': round(time.monotonic() - started)}
    atomic(directory / 'status.json', final)
    print(json.dumps(final), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('start', 'run', 'verify'))
    parser.add_argument('--run-dir')
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--cpu-seconds', type=float, default=3600)
    parser.add_argument('--max-states', type=int, default=50000)
    parser.add_argument('--max-depth', type=int, default=4)
    parser.add_argument('--max-descent-steps', type=int, default=1000)
    parser.add_argument('--only', default='')
    args = parser.parse_args()
    assert 1 <= args.workers <= 3 and args.cpu_seconds > 0 and args.max_states > 1 and args.max_depth >= 1 and args.max_descent_steps > 0
    if args.mode == 'verify':
        preflight()
        print('PASS: source manifest, founder hashes, arms and independent metrics')
    elif args.mode == 'run':
        assert args.run_dir
        run(args)
    else:
        preflight()
        base = Path(sys.argv[0]).resolve().parent
        directory = Path(args.run_dir).resolve() if args.run_dir else base / 'runs' / datetime.datetime.now().strftime('followup_%Y%m%d_%H%M%S_%f')
        directory.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, str(Path(sys.argv[0]).resolve()), 'run', '--run-dir', str(directory), '--workers', str(args.workers), '--cpu-seconds', str(args.cpu_seconds), '--max-states', str(args.max_states), '--max-depth', str(args.max_depth), '--max-descent-steps', str(args.max_descent_steps)]
        if args.only:
            command.extend(['--only', args.only])
        with (directory / 'console.log').open('ab') as log:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        record = {'pid': process.pid, 'run_dir': str(directory), 'log': str(directory / 'console.log')}
        atomic(base / 'active_followup.json', record)
        for _ in range(100):
            if process.poll() is not None:
                if process.returncode:
                    raise RuntimeError('Startup failed; inspect ' + record['log'])
                break
            if (directory / 'status.json').exists():
                break
            time.sleep(0.1)
        print(json.dumps(record, indent=4))


if __name__ == '__main__':
    main()
