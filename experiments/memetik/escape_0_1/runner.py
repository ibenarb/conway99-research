"""Escape 0.1: finite, auditable one-trade census before multi-step search."""
import argparse
import concurrent.futures
import datetime
import fcntl
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import random
import resource
import shutil
import signal
import subprocess
import sys
import time
import zipfile

from core import BudgetEnd, apply_move, decode_g6, encode_g6, metrics, validate
from operators import apex_moves, rotation_moves, omega_moves

VERSION = 'escape-0.1.0'
OBJECTIVES = ('W', 'L1', 'F', 'Linf')


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def atomic(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=4) + '\n')
    os.replace(temp, path)


def founders():
    if zipfile.is_zipfile(sys.argv[0]):
        with zipfile.ZipFile(sys.argv[0]) as archive:
            return json.loads(archive.read('founders.json'))
    return json.loads((Path(__file__).parent / 'founders.json').read_text())


def key(data, objective):
    return (data['Linf'], data['Nmax'], data['L1']) if objective == 'Linf' else (data[objective],)


def independent(rows):
    neighbors = [{j for j in range(99) if rows[i] & (1 << j)} for i in range(99)]
    residuals = [len(neighbors[i] & neighbors[j]) + int(j in neighbors[i]) - 2 for i in range(99) for j in range(i)]
    maximum = max(map(abs, residuals))
    return {'W': sum(r != 0 for r in residuals), 'L1': sum(map(abs, residuals)), 'F': sum(r*r for r in residuals), 'Linf': maximum, 'Nmax': sum(abs(r) == maximum for r in residuals)}


def preflight(items):
    for item in items:
        raw = (item['graph6'] + '\n').encode()
        assert hashlib.sha256(raw).hexdigest() == item['sha256']
        rows = decode_g6(item['graph6'])
        validate(rows, item['arm'])
        assert json.loads(json.dumps(metrics(rows))) == item['metrics']
        assert all(item['metrics'][k] == v for k, v in independent(rows).items())


class TaskBudget:
    def __init__(self, seconds, callback, run_dir):
        self.started = time.process_time()
        self.deadline = self.started + seconds
        self.last = 0
        self.callback = callback
        self.run_dir = run_dir

    def check(self):
        if time.monotonic() - self.last > 10:
            self.callback()
            self.last = time.monotonic()
            if shutil.disk_usage(self.run_dir).free < 10 * 2**30:
                raise BudgetEnd('DISK_FLOOR_10_GiB')
        if time.process_time() >= self.deadline:
            raise BudgetEnd('CPU_BUDGET')


def task(item, family, seconds, run_dir):
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 2**20, 1024 * 2**20))
    name = item['id'] + '__' + family
    path = Path(run_dir) / (name + '.json')
    start = time.process_time()
    rows = decode_g6(item['graph6'])
    stats = {'task': name, 'founder': item['id'], 'arm': item['arm'], 'family': family,
             'status': 'RUNNING', 'complete': False, 'cpu_budget_seconds': seconds,
             'valid_trades': 0, 'baseline': item['metrics'], 'source_sha256': item['sha256'],
             'better': dict.fromkeys(OBJECTIVES, 0), 'equal': dict.fromkeys(OBJECTIVES, 0),
             'worse': dict.fromkeys(OBJECTIVES, 0), 'best_witness': {},
             'scope': 'One move in the named existing generator family; not all admissible trades.'}

    def save():
        stats['cpu_seconds'] = time.process_time() - start
        stats['utc'] = utc()
        atomic(path, stats)

    budget = TaskBudget(seconds, save, run_dir)
    reserve = bytearray(2**20)
    try:
        rng = random.Random(20260915)
        if family == 'apex':
            stream = apex_moves(rows, rng, budget)
        elif family == 'rotation':
            stream = rotation_moves(rows, rng, budget)
        else:
            stream = omega_moves(rows, family, rng, budget)
        for deleted, added in stream:
            budget.check()
            child = apply_move(rows, (deleted, added))
            validate(child, item['arm'])
            data = metrics(child)
            stats['valid_trades'] += 1
            for objective in OBJECTIVES:
                old, new = key(item['metrics'], objective), key(data, objective)
                relation = 'better' if new < old else 'equal' if new == old else 'worse'
                stats[relation][objective] += 1
                previous = stats['best_witness'].get(objective)
                if new < old and (previous is None or new < key(previous['metrics'], objective)):
                    assert all(data[k] == v for k, v in independent(child).items())
                    g6 = encode_g6(child)
                    stats['best_witness'][objective] = {'graph6': g6, 'sha256': hashlib.sha256((g6+'\n').encode()).hexdigest(), 'metrics': data, 'deleted': deleted, 'added': added, 'path_length': 1, 'deleted_edges': len(deleted), 'added_edges': len(added)}
        stats.update(status='EXHAUSTED', complete=True)
    except BudgetEnd as error:
        stats.update(status=str(error), complete=False)
    except MemoryError:
        del reserve
        stats.update(status='MEMORY_LIMIT', complete=False)
    except Exception as error:
        stats.update(status='ERROR', error=repr(error), complete=False)
    save()
    return stats


def summarize(items, results):
    summary = {}
    for item in items:
        families = ('4x4', '4x6', '6x6') if item['arm'] == 'omega' else ('apex', 'rotation')
        rows = [results.get(item['id'] + '__' + family) for family in families]
        complete = all(row and row['complete'] for row in rows)
        objectives = {}
        for objective in OBJECTIVES:
            found = sum(row['better'][objective] for row in rows if row)
            neutral = sum(row['equal'][objective] for row in rows if row)
            objectives[objective] = {'status': 'IMPROVEMENT_AT_DISTANCE_1' if found else ('NO_IMPROVING_ONE_TRADE_NEIGHBOR' if complete else 'UNKNOWN'), 'improving_trades_found': found, 'neutral_trades_found': neutral}
        summary[item['id']] = {'arm': item['arm'], 'families_complete': complete, 'objectives': objectives}
    return summary


def run(args):
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    directory = Path(args.run_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    lock = (directory / 'run.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    items = founders()
    preflight(items)
    config = {'version': VERSION, 'workers': args.workers, 'cpu_seconds_per_family': args.cpu_seconds, 'founders': items, 'depth': 1}
    config_path = directory / 'config.json'
    if config_path.exists():
        assert json.loads(config_path.read_text()) == config, 'Run configuration differs; use a new directory.'
    else:
        atomic(config_path, config)
    tasks = [(item, family) for item in items for family in (('4x4', '4x6', '6x6') if item['arm'] == 'omega' else ('apex', 'rotation'))]
    results = {}
    todo = []
    for item, family in tasks:
        name = item['id'] + '__' + family
        path = directory / (name + '.json')
        previous = json.loads(path.read_text()) if path.exists() else None
        if previous and previous['status'] != 'RUNNING':
            results[name] = previous
        else:
            todo.append((item, family))
    started = time.monotonic()
    last_print = -1000
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('fork')) as pool:
        pending = {pool.submit(task, item, family, args.cpu_seconds, str(directory)): item['id']+'__'+family for item, family in todo}
        while pending:
            done, _ = concurrent.futures.wait(pending, timeout=10, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                name = pending.pop(future)
                try:
                    results[name] = future.result()
                except Exception as error:
                    raise RuntimeError('Worker failed: '+name+': '+repr(error)) from error
            active = []
            remaining = 0
            for name in pending.values():
                path = directory / (name+'.json')
                state = json.loads(path.read_text()) if path.exists() else None
                used = state.get('cpu_seconds',0) if state else 0
                remaining += max(0, args.cpu_seconds-used)
                if state:
                    active.append({'task':name,'cpu_seconds':used,'valid_trades':state['valid_trades']})
            status = {'version':VERSION,'phase':'NEIGHBORHOOD_CENSUS','utc':utc(),'elapsed_seconds':round(time.monotonic()-started),'done':len(results),'total':len(tasks),'active':active,'remaining_cpu_budget_seconds':round(remaining),'ideal_remaining_hours_at_full_utilization':round(remaining/args.workers/3600,2),'eta_scope':'Budget estimate only; not a solution ETA or wallclock guarantee.'}
            atomic(directory/'status.json',status)
            if time.monotonic()-last_print>=600:
                print(json.dumps(status),flush=True)
                last_print=time.monotonic()
    atomic(directory/'summary.json',summarize(items,results))
    status = {'version':VERSION,'phase':'CENSUS_FINISHED','utc':utc(),'done':len(results),'total':len(tasks),'exhausted':sum(r['complete'] for r in results.values()),'incomplete':sum(not r['complete'] for r in results.values()),'summary':str(directory/'summary.json'),'note':'No multi-step escape minimality claim. Neutral components remain unexplored.'}
    atomic(directory/'status.json',status)
    print(json.dumps(status),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['start','run','verify'])
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--cpu-seconds',type=float,default=3600)
    parser.add_argument('--run-dir')
    args=parser.parse_args()
    assert 1<=args.workers<=3 and args.cpu_seconds>0
    if args.mode=='verify':
        preflight(founders())
        print('PASS: eight founders, hard conditions and independent metrics')
        return
    if args.mode=='start':
        preflight(founders())
        base=Path(sys.argv[0]).resolve().parent
        active_path=base/'active_run.json'
        if active_path.exists():
            prior=json.loads(active_path.read_text())
            try:
                os.kill(prior['pid'],0)
                command = Path('/proc', str(prior['pid']), 'cmdline').read_bytes()
                if str(base).encode() in command and prior['run_dir'].encode() in command:
                    print(json.dumps({'already_running':prior},indent=4))
                    return
            except ProcessLookupError:
                pass
        directory=Path(args.run_dir).resolve() if args.run_dir else base/'runs'/datetime.datetime.now().strftime('census_%Y%m%d_%H%M%S')
        directory.mkdir(parents=True,exist_ok=True)
        with (directory/'console.log').open('ab') as log:
            process=subprocess.Popen([sys.executable,str(Path(sys.argv[0]).resolve()),'run','--run-dir',str(directory),'--workers',str(args.workers),'--cpu-seconds',str(args.cpu_seconds)],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        record={'pid':process.pid,'run_dir':str(directory),'status':str(directory/'status.json'),'console':str(directory/'console.log')}
        atomic(active_path,record)
        deadline = time.monotonic() + 15
        while not (directory/'status.json').exists() and time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError('Startup failed; inspect '+str(directory/'console.log'))
            time.sleep(0.1)
        record['status_file_ready'] = (directory/'status.json').exists()
        print(json.dumps(record,indent=4))
    else:
        assert args.run_dir, '--run-dir required'
        try:
            run(args)
        except Exception as error:
            atomic(Path(args.run_dir)/'status.json',{'phase':'ERROR','utc':utc(),'error':repr(error)})
            raise
