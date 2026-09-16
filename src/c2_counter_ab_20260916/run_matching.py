"""Bounded no-proof search on a complete local matching orbit cover."""
import argparse
from collections import deque
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback
from common import GIB, ROOT, VERSION, save, sha
from windows_guard import Guard

HERE = Path(__file__).resolve().parent
LOCK_PATH = Path.home()/'conway99_workspace/c2_matching_v1/campaign.lock'


def stop_workers(active):
    # Stop first, write reports afterwards: disk errors must not bypass cleanup.
    for proc, _, _, _ in active.values():
        try:
            proc.terminate()
        except ProcessLookupError:
            pass
    deadline = time.monotonic()+5
    for proc, _, _, _ in active.values():
        try:
            proc.wait(timeout=max(0.01, deadline-time.monotonic()))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def linux_safety(out):
    free = shutil.disk_usage(out).free
    mem = next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    if free < 25*GIB:
        raise RuntimeError('LINUX_DISK_RESERVE')
    if mem < 4*GIB:
        raise RuntimeError('LINUX_RAM_RESERVE')
    size = 0
    for p in out.rglob('*'):
        try:
            if p.is_file():
                size += p.stat().st_size
        except FileNotFoundError:
            # Only ephemeral atomic-write temporaries may disappear harmlessly.
            if not p.name.endswith('.tmp'):
                raise
    if size > 3*GIB:
        raise RuntimeError('CAMPAIGN_OUTPUT_LIMIT')
    return {'linux_free_GiB': round(free/GIB, 2), 'available_RAM_GiB': round(mem/GIB, 2), 'output_bytes': size}


def controller(args):
    out = Path(args.out).resolve()
    active, results, guard = {}, [], None
    lock = LOCK_PATH.open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    started = time.monotonic()
    status = 'COUNTER_AB_FAILED'
    error = None
    error_details = None
    try:
        config = json.loads((ROOT/'setup.json').read_text())
        solver = config['solver']
        if sha(solver) != config['solver_sha256']:
            raise RuntimeError('Solver identity mismatch')
        manifest = json.loads((ROOT/'partitions/manifest.json').read_text())
        jobs = manifest['jobs']
        if len(jobs) != 22 or len({j['id'] for j in jobs}) != 22 or manifest['cover']['transports_checked'] != 10395:
            raise RuntimeError('Unexpected matching case cover')
        if [j['group'] for j in jobs] != ['reference'] * 11 + ['totalizer'] * 11:
            raise RuntimeError('Expected two ordered eleven-job waves')
        for a, b in zip(jobs[:11], jobs[11:]):
            if a['assumptions'] != b['assumptions'] or a['seed'] != b['seed']:
                raise RuntimeError('Unmatched experiment inputs')
        queue = deque(jobs)
        guard = Guard(out)
        save(out/'config.json', {'version': VERSION, 'source': str(HERE),
             'controller_sha256': sha(HERE/'run_matching.py'), 'guard_sha256': sha(HERE/'windows_guard.py'), 'case_wall_budget': args.seconds,
             'total_allocated_wall_budget': 22*args.seconds, 'case_count': 22,
             'workers': args.workers, 'solver_sha256': config['solver_sha256'],
             'windows_guard_directory': guard.windows_dir, 'proof_logging': False,
             'limits': {'log_MiB_per_job':64, 'AS_GiB_per_solver':4, 'host_reserve_GiB':50,
                        'linux_reserve_GiB':25, 'RAM_reserve_GiB':4},
             'scope':'Two nonoverlapping waves: reference and E3 totalizer, eleven identical matching cases per wave. No certification.'})
        save(out/'ready.json', {'status':'MATCHING_CONTROLLER_READY', 'pid':os.getpid()})
        last_print = -600
        while queue or active:
            guard.beat()
            host = guard.read()
            safety = linux_safety(out)
            if (out/'STOP').exists():
                raise RuntimeError('USER_STOP_FILE')
            for name, (proc, job, start, budget) in list(active.items()):
                if proc.poll() is not None:
                    rp = out/name/'result.json'
                    record = json.loads(rp.read_text()) if rp.exists() else {'status':'WORKER_RESULT_MISSING'}
                    record['id'] = name
                    results.append(record)
                    del active[name]
                    if record['status'] not in ('OPEN_BUDGET','UNSAT_UNCERTIFIED','GRAPH_VERIFIED'):
                        raise RuntimeError(name+': '+record['status'])
                    if record['status']=='GRAPH_VERIFIED':
                        status = 'GRAPH_FOUND_REQUIRES_REVIEW'
                        queue.clear()
                        stop_workers(active)
                        active.clear()
                        break
                elif time.monotonic()-start > budget+110:
                    raise RuntimeError(name+': WORKER_WALL_WATCHDOG')
            while queue and len(active)<args.workers and (not active or next(iter(active.values()))[1]['group'] == queue[0]['group']):
                job = queue.popleft()
                folder = out/job['id']
                folder.mkdir()
                save(folder/'job.json',job)
                budget = args.seconds
                proc = subprocess.Popen([sys.executable, str(HERE/'worker.py'), str(folder/'job.json'),
                        solver, str(budget), str(folder), str(os.getpid())],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                active[job['id']] = (proc, job, time.monotonic(), budget)
            elapsed = round(time.monotonic()-started)
            snapshot = dict(safety, phase='COUNTER_AB_SEARCH', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 elapsed_seconds=elapsed, active=list(active), queued=len(queue), completed=len(results),
                 windows_free_GiB=round(host['free_bytes']/GIB,2), proof_files_created=0,
                 guard_read_retries=getattr(guard, 'read_retries', 0),
                 ETA_note='Two waves, each with the selected wall budget; decision time unknown')
            save(out/'status.json',snapshot)
            if elapsed-last_print>=600:
                print(json.dumps(snapshot),flush=True)
                last_print=elapsed
            if active:
                time.sleep(3)
        if status!='GRAPH_FOUND_REQUIRES_REVIEW':
            status='COUNTER_AB_COMPLETE_NO_CERTIFICATION'
    except BaseException as exc:
        error = str(exc) or repr(exc)
        error_details = {'type': type(exc).__name__, 'repr': repr(exc),
                         'filename': str(getattr(exc, 'filename', '') or ''),
                         'filename2': str(getattr(exc, 'filename2', '') or ''),
                         'traceback': traceback.format_exc()}
        print(error_details['traceback'], file=sys.stderr, flush=True)
    finally:
        stop_workers(active)
        if guard:
            try:
                guard.close()
            except Exception:
                pass
        totals = {}
        for result in results:
            group = result.get('group','unknown')
            item = totals.setdefault(group, {'jobs':0,'unsat_uncertified':0,'cpu_seconds':0.0})
            item['jobs']+=1
            item['unsat_uncertified']+=result['status']=='UNSAT_UNCERTIFIED'
            item['cpu_seconds']+=result.get('solver_cpu_seconds',0)
        report = {'status':status,'error':error,'error_details':error_details,'results':results,'groups':totals,
             'interrupted_jobs':list(active),'wall_seconds':round(time.monotonic()-started),
             'proofs_checked':0, 'automatic_followup_runs':0,
             'guard_read_retries':getattr(guard, 'read_retries', 0),
             'interpretation':'No certified exclusions. The 11 cases cover matching orbits, not equal fractions of full solutions. Unknown cases stay open; no automatic follow-up.'}
        save(out/'summary.json', report)
        save(out/'status.json', {'phase':status,'error':error,'active':[], 'summary':str(out/'summary.json')})
        print(json.dumps({'status':status,'error':error,'output':str(out)}),flush=True)
        lock.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=int,default=1200,help='wall seconds per matching case; 1200 for scout, explicit longer budget up to 28800')
    parser.add_argument('--workers',type=int,default=11)
    parser.add_argument('--controller',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--out',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if not 3<=args.seconds<=28800 or not 1<=args.workers<=11:
        parser.error('seconds: 3..28800; workers: 1..11')
    if args.controller:
        controller(args)
        return
    if not (ROOT/'setup.json').exists():
        parser.error('Run prepare_matching.py first')
    out=ROOT/('matching_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir()
    with (out/'driver.log').open('wb') as stream:
        proc=subprocess.Popen([sys.executable,str(HERE/'run_matching.py'),'--controller','--out',str(out),
              '--seconds',str(args.seconds),'--workers',str(args.workers)],stdout=stream,stderr=subprocess.STDOUT,
              stdin=subprocess.DEVNULL,start_new_session=True)
    for _ in range(30):
        if (out/'ready.json').exists():
            print(json.dumps({'status':'C2_COUNTER_AB_READY','version':VERSION,'pid':proc.pid,'output':str(out),'proof_logging':False}),flush=True)
            return
        if proc.poll() is not None:
            raise RuntimeError('Startup failed; see '+str(out/'driver.log'))
        time.sleep(1)
    print(json.dumps({'status':'STARTUP_PENDING_NOT_CONFIRMED','pid':proc.pid,'output':str(out)}))

if __name__=='__main__':
    main()
