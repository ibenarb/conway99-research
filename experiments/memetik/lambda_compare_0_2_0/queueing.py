"""Owned children only; wait4 accounts all worker CPU, including resume replay."""
import bootstrap
from common import atomic, sha, checked
from archive import file_sha
from runtime import Pool, read, immutable, process, THREAD_ENV
from pathlib import Path
from progress import Progress
import os
import signal
import subprocess
import sys
import time


def validate_receipt(directory):
    receipt = read(directory/'receipt.json')
    for filename, field in [('task.json','task_sha256'),('result.json','result_sha256')]:
        if receipt[field] != sha((directory/filename).read_bytes()):
            raise RuntimeError('Receipt mismatch: '+str(directory/filename))
    if receipt['kind']=='compare':
        if receipt['checkpoint_sha256'] != sha((directory/'checkpoint.json').read_bytes()):
            raise RuntimeError('Checkpoint receipt mismatch')
        if receipt['archive_sha256'] != file_sha(directory/'archive.sqlite'):
            raise RuntimeError('Archive receipt mismatch')
    if abs(sum(s['cpu_seconds'] for s in receipt['sessions'])-receipt['cpu_seconds'])>1e-6:
        raise RuntimeError('CPU session sum mismatch')
    if receipt['budget_cpu_seconds']<receipt['cpu_seconds'] or receipt['closed_reserve_cpu_seconds']<0:
        raise RuntimeError('Invalid reserved CPU accounting')
    if receipt['exit_code'] or receipt['status'] not in ('COMPLETE','PAUSED','SOLUTION','CONTROLS_PASS'):
        raise RuntimeError('Failed task needs diagnosis: '+str(directory))
    return receipt


class Queue(Pool):
    def limit(self, task):
        return self.budget if task['kind']=='compare' else task['worker_cpu_seconds']

    def check(self):
        usage = super().check()
        if (self.directory/'SOLUTION.json').exists():
            marker = read(self.directory/'SOLUTION.json')
            _, scores = checked(marker['candidate']['graph6'],'lambda')
            if scores['F'] != 0:
                raise RuntimeError('False solution marker')
            self.stop,self.last_reason = True,['VERIFIED_SOLUTION']
        return usage

    def status(self, phase, pending, usage, force=False):
        now = time.monotonic()
        if not force and now-self.last_status < 600:
            return
        charged = sum(r['cpu_seconds'] for r in self.receipts())
        active_cpu = sum(p['cpu'] for p in usage.values())
        elapsed = now-self.started
        rate = (self.cpu_this_session+active_cpu)/elapsed if elapsed else 0
        remaining = sum(max(0,self.limit(t)-base) for t,base in pending)
        remaining += sum(max(0,self.limit(e['task'])-e['base']-usage[pid]['cpu']) for pid,e in self.active.items())
        report = {'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'phase':phase,'active_workers':len(self.active),'pending':len(pending),
                  'worker_cpu_seconds':charged+active_cpu,'session_wall_seconds':elapsed,
                  'observed_cpu_per_wall_second':rate,'cpu_budget_eta_seconds':remaining/rate if rate else None,
                  'eta_scope':'current phase CPU ceilings; no solution-time prediction',
                  'per_job_cpu_seconds':self.budget,'host':self.host,'stop_reason':self.last_reason}
        from search import key
        best,counts = {},{}
        for path in (self.directory/'tasks').glob('*/checkpoint.json'):
            state = read(path)['state']
            task = read(path.parent/'task.json')
            group = task['variant']+'/'+task['target']
            if group not in best or key(state['best']['scores'],task['target'])<key(best[group],task['target']):
                best[group] = state['best']['scores']
            counts[task['id']] = state['archive_classes']
        report.update(best_by_group=best,archive_classes=counts)
        atomic(self.directory/'status.json',report)
        print(json.dumps({k:v for k,v in report.items() if k not in ('host','archive_classes')}),flush=True)
        self.last_status = now

    def run(self, tasks, workers, phase):
        self.budget = read(self.directory/'budget.json')['per_job_cpu_seconds']
        immutable(self.directory/(phase+'_manifest.json'),tasks)
        timing_path = self.directory/(phase+'_timing.json')
        timing = read(timing_path) if timing_path.exists() else {'wall_seconds':0.,'clean':True}
        if not timing['clean']:
            raise RuntimeError('Unclean controller timing: diagnosis required')
        pending = []
        for task in tasks:
            d = self.directory/'tasks'/task['id']
            d.mkdir(parents=True,exist_ok=True)
            immutable(d/'task.json',task)
            if (d/'active.json').exists():
                raise RuntimeError('Unresolved CPU receipt: '+task['id'])
            receipt = validate_receipt(d) if (d/'receipt.json').exists() else None
            if not receipt and any((d/n).exists() for n in ('checkpoint.json','archive.sqlite','result.json')):
                raise RuntimeError('State without CPU receipt: '+task['id'])
            if receipt:
                result = read(d/'result.json')
                complete = receipt['status']=='CONTROLS_PASS' or (receipt['status']=='COMPLETE' and result['endpoint_cpu_seconds']==self.limit(task))
                if receipt['status']=='SOLUTION' or complete:
                    continue
                if receipt.get('budget_cpu_seconds',receipt['cpu_seconds'])>=self.limit(task):
                    raise RuntimeError('Budget exhausted without clean completion')
            base = receipt.get('budget_cpu_seconds',receipt['cpu_seconds']) if receipt else 0.
            if receipt and receipt['status']=='COMPLETE':
                base = max(base,result['endpoint_cpu_seconds'])
            pending.append((task,base))
        started = time.monotonic()
        progress = Progress(self.directory,quiet_seconds=60) if phase=='comparison' else None
        atomic(timing_path,{'wall_seconds':timing['wall_seconds'],'clean':False})
        while pending or self.active:
            self.check()
            if self.stop:
                for pid,entry in self.active.items():
                    if not entry.get('stop_sent'):
                        os.kill(pid,signal.SIGTERM)
                        entry['stop_sent'] = True
            while pending and len(self.active)<workers and not self.stop:
                task,base = pending.pop(0)
                d = self.directory/'tasks'/task['id']
                with (d/'worker.log').open('ab') as log:
                    proc = subprocess.Popen([sys.executable,str(bootstrap.HERE/'worker.py'),str(d)],
                                            stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                                            env={**os.environ,**THREAD_ENV})
                atomic(d/'active.json',{'pid':proc.pid,'base_cpu_seconds':base,'start_ticks':process(proc.pid)['start_ticks']})
                self.active[proc.pid] = {'proc':proc,'task':task,'base':base,'directory':d}
            for pid in list(self.active):
                waited,status,usage = os.wait4(pid,os.WNOHANG)
                if not waited:
                    continue
                entry = self.active.pop(pid)
                code = os.waitstatus_to_exitcode(status)
                entry['proc'].returncode = code
                actual = usage.ru_utime+usage.ru_stime
                self.cpu_this_session += actual
                d = entry['directory']
                output = d/'result.json'
                result = read(output) if output.exists() and code==0 else {'status':'FAILED'}
                previous = read(d/'receipt.json') if (d/'receipt.json').exists() else {}
                sessions = previous.get('sessions',[])+[{'cpu_seconds':actual,'budget':self.limit(entry['task']),
                                                       'exit_code':code,'status':result['status']}]
                receipt = {'id':entry['task']['id'],'kind':entry['task']['kind'],
                           'cpu_seconds':previous.get('cpu_seconds',0.)+actual,
                           'budget_cpu_seconds':entry['base']+actual,
                           'closed_reserve_cpu_seconds':entry['base']-previous.get('cpu_seconds',0.),
                           'session_cpu_seconds':actual,'sessions':sessions,
                           'exit_code':code,'status':result['status'],
                           'task_sha256':sha((d/'task.json').read_bytes()),
                           'result_sha256':sha(output.read_bytes()) if output.exists() else None}
                for name,field in [('checkpoint.json','checkpoint_sha256'),('archive.sqlite','archive_sha256')]:
                    receipt[field] = file_sha(d/name) if (d/name).exists() else None
                atomic(d/'receipt.json',receipt)
                (d/'active.json').unlink()
                if code or receipt['budget_cpu_seconds']>self.limit(entry['task']):
                    self.stop,self.last_reason = True,['WORKER_FAILED_OR_OVERRUN',entry['task']['id']]
            usage = {pid:process(pid) for pid in self.active}
            self.status(phase,pending,usage)
            if progress:
                progress.poll()
            if self.stop and not self.active:
                break
            if pending or self.active:
                time.sleep(.25)
        self.status(phase,pending,{},force=True)
        atomic(timing_path,{'wall_seconds':timing['wall_seconds']+time.monotonic()-started,'clean':True})
        if self.stop:
            raise RuntimeError('PAUSED: '+str(self.last_reason or 'requested'))
        return [read(self.directory/'tasks'/t['id']/'result.json') for t in tasks]


import json
