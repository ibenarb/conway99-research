"""Detached, bounded calibration; no automatic production/proof run."""
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
from common import GIB, ROOT, VERSION, save, sha
from windows_guard import Guard

HERE = Path(__file__).resolve().parent


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
    size = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    if size > 3*GIB:
        raise RuntimeError('CAMPAIGN_OUTPUT_LIMIT')
    return {'linux_free_GiB': round(free/GIB, 2), 'available_RAM_GiB': round(mem/GIB, 2), 'output_bytes': size}


def controller(args):
    out = Path(args.out).resolve()
    active, results, guard = {}, [], None
    lock = (ROOT/'campaign.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    started = time.monotonic()
    status = 'CALIBRATION_FAILED'
    error = None
    try:
        config = json.loads((ROOT/'setup.json').read_text())
        solver = config['solver']
        if sha(solver) != config['solver_sha256']:
            raise RuntimeError('Solver identity mismatch')
        manifest = json.loads((ROOT/'partitions/manifest.json').read_text())
        jobs = manifest['jobs']
        groups = list(manifest['split_variables'])
        # Baselines and interleaved cubes share the initial scheduling wave.
        order = [j for j in jobs if j['group']=='baseline']
        for bits in range(8):
            for group in groups:
                order.append(next(j for j in jobs if j['id']==group+'_'+format(bits, '03b')))
        queue = deque(order)
        guard = Guard(out)
        save(out/'config.json', {'version': VERSION, 'cube_wall_budget': args.seconds,
             'baseline_wall_budget': 8*args.seconds//3, 'strategy_wall_budget': 8*args.seconds,
             'workers': args.workers, 'solver_sha256': config['solver_sha256'],
             'windows_guard_directory': guard.windows_dir, 'proof_logging': False,
             'limits': {'log_MiB_per_job':64, 'AS_GiB_per_solver':4, 'host_reserve_GiB':50,
                        'linux_reserve_GiB':25, 'RAM_reserve_GiB':4},
             'scope':'Calibration only. All UNSAT results untrusted pending separate certificates.'})
        save(out/'ready.json', {'status':'CALIBRATION_READY', 'pid':os.getpid()})
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
            while queue and len(active)<args.workers:
                job = queue.popleft()
                folder = out/job['id']
                folder.mkdir()
                save(folder/'job.json',job)
                budget = 8*args.seconds//3 if job['group']=='baseline' else args.seconds
                proc = subprocess.Popen([sys.executable, str(HERE/'worker.py'), str(folder/'job.json'),
                        solver, str(budget), str(folder), str(os.getpid())],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                active[job['id']] = (proc, job, time.monotonic(), budget)
            elapsed = round(time.monotonic()-started)
            snapshot = dict(safety, phase='CALIBRATION_SEARCH', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 elapsed_seconds=elapsed, active=list(active), queued=len(queue), completed=len(results),
                 windows_free_GiB=round(host['free_bytes']/GIB,2), proof_files_created=0)
            save(out/'status.json',snapshot)
            if elapsed-last_print>=600:
                print(json.dumps(snapshot),flush=True)
                last_print=elapsed
            if active:
                time.sleep(3)
        if status!='GRAPH_FOUND_REQUIRES_REVIEW':
            status='CALIBRATION_COMPLETE_NO_CERTIFICATION'
    except BaseException as exc:
        error = repr(exc)
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
        report = {'status':status,'error':error,'results':results,'groups':totals,
             'interrupted_jobs':list(active),'wall_seconds':round(time.monotonic()-started),
             'proofs_checked':0, 'automatic_followup_runs':0,
             'interpretation':'No exclusions established. Unsolved jobs have no completion percentage. Compare actual CPU and solved cubes; no automatic winner from conflict counts.'}
        save(out/'summary.json', report)
        save(out/'status.json', {'phase':status,'error':error,'active':[], 'summary':str(out/'summary.json')})
        print(json.dumps({'status':status,'error':error,'output':str(out)}),flush=True)
        lock.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=int,default=1200,help='wall seconds per cube; each baseline receives 8/3 of this')
    parser.add_argument('--workers',type=int,default=11)
    parser.add_argument('--controller',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--out',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if not 3<=args.seconds<=1800 or args.seconds%3 or not 1<=args.workers<=11:
        parser.error('seconds: multiple of 3, 3..1800; workers: 1..11')
    if args.controller:
        controller(args)
        return
    if not (ROOT/'setup.json').exists():
        parser.error('Run setup.py first')
    out=ROOT/('calibration_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir()
    with (out/'driver.log').open('wb') as stream:
        proc=subprocess.Popen([sys.executable,str(HERE/'scout.py'),'--controller','--out',str(out),
              '--seconds',str(args.seconds),'--workers',str(args.workers)],stdout=stream,stderr=subprocess.STDOUT,
              stdin=subprocess.DEVNULL,start_new_session=True)
    for _ in range(30):
        if (out/'ready.json').exists():
            print(json.dumps({'status':'C2_SCOUT_READY','pid':proc.pid,'output':str(out),'proof_logging':False}),flush=True)
            return
        if proc.poll() is not None:
            raise RuntimeError('Startup failed; see '+str(out/'driver.log'))
        time.sleep(1)
    print(json.dumps({'status':'STARTUP_PENDING_NOT_CONFIRMED','pid':proc.pid,'output':str(out)}))

if __name__=='__main__':
    main()
