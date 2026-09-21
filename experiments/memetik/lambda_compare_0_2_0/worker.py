"""Budgeted resumable lambda worker; no child processes and no early plateau stop."""
import bootstrap
from common import atomic, checked, core, cpu, sha, verifier
from search import key, tuple_state
from archive import Archive, make_item
from engine import Engine, increment
from pathlib import Path
import argparse
import json
import math
import os
import random
import resource
import signal
import time

STOP = False
PARENT = os.getppid()


def read(path):
    return json.loads(Path(path).read_text())


def stopping(*args):
    global STOP
    STOP = True


class Halt(core.BudgetEnd):
    pass


class Guard:
    def __init__(self, deadline, root):
        self.deadline,self.root,self.callback = deadline,root,lambda:None
        self.generated = 0

    def check(self):
        if STOP or os.getppid()!=PARENT:
            raise Halt('PAUSED')
        if (self.root/'SOLUTION.json').exists():
            raise Halt('SOLUTION')
        if cpu() >= self.deadline:
            raise Halt('CPU_LIMIT')
        self.callback()


class Observer:
    def __init__(self, directory, task, state, archive, guard, base, ceiling):
        self.directory,self.task,self.s,self.archive = directory,task,state,archive
        self.guard,self.base,self.ceiling = guard,base,ceiling
        self.save = lambda:None
        self.last_save = time.monotonic()

    def clock(self):
        return self.base+cpu()

    def event(self, filename, value):
        with (self.directory/filename).open('a') as handle:
            handle.write(json.dumps(value,separators=(',',':'))+'\n')
            handle.flush()

    def tick(self):
        now = self.clock()
        limits = sorted(set(self.task['config']['milestones_cpu_seconds']+[self.ceiling]))
        for mark in limits:
            if mark>self.ceiling or mark>now or str(mark) in self.s['milestones']:
                continue
            self.capture(mark,now)
        if time.monotonic()-self.last_save >= self.task['config']['checkpoint_wall_seconds']:
            self.save()
            self.last_save = time.monotonic()

    def capture(self, mark, now):
        value = next(p for p in reversed(self.s['curves']) if p['cpu']<=mark)
        self.s['milestones'][str(mark)] = {'budget_cpu':mark,'observed_cpu':now,
                                         'scores':value['scores'],'graph6':value['graph6'],
                                         'episodes_at_observation':self.s['episodes'],
                                         'iterations_at_observation':self.s['iterations']}
        self.event('milestones.jsonl',self.s['milestones'][str(mark)])

    def evaluated(self, rows, scores, name, origin):
        increment(self.s['evaluated_moves'],name)
        targets = [t for t,p in self.s['observed_best'].items() if key(scores,t)<key(p['scores'],t)]
        if not targets and scores['F']:
            return
        item = make_item(rows,origin,self.guard)
        if scores != item['scores']:
            raise ValueError('Incremental score mismatch')
        self.archive.put(item)
        now = self.clock()
        for target in targets:
            self.s['observed_best'][target] = item
            self.archive.record(target,now,item,'OBSERVED')
        if scores['F']==0:
            self.solution(item)

    def solution(self, item):
        result = verifier.check_graph(item['graph6'],'lambda')
        if not result['is_solution']:
            raise ValueError('False zero-residual candidate')
        payload = {'candidate':item,'verification':result,'id':self.task['id'],
                   'cpu':self.clock(),'graph6_sha256':sha(item['graph6'].encode())}
        atomic(self.directory/'SOLUTION.json',payload)
        atomic(self.directory.parent.parent/'SOLUTION.json',payload)

    def adopt(self, rows, scores, name, origin, guard):
        item = make_item(rows,origin,guard)
        if scores != item['scores']:
            raise ValueError('Adopted score mismatch')
        guard.check()
        self.archive.put(item)
        increment(self.s['adopted_moves'],name)
        target = self.task['target']
        if key(scores,target)<key(self.s['best']['scores'],target):
            now = self.clock()
            self.s['best'] = item
            self.s['curves'].append({'cpu':now,'scores':scores,'graph6':item['graph6']})
            self.archive.record(target,now,item,'ACTIVE')
            wall = time.time()
            self.event('improvements.jsonl',{'id':self.task['id'],'arm':'lambda','target':target,
                       'variant':self.task['variant'],'replicate':self.task['replicate'],
                       'scores':scores,'cpu':now,'wall':wall,
                       'gap_wall_seconds':wall-self.s['last_improvement_wall']})
            self.s['last_improvement_wall'] = wall
        if scores['F']==0:
            self.solution(item)
        return item

    def endpoint(self, item, reason):
        self.archive.put(item,endpoint=True)
        self.event('endpoints.jsonl',{'cpu':self.clock(),'class':item['class'],
                                    'scores':item['scores'],'line':item['line'],'reason':reason})

    def family_event(self):
        counts = {}
        for item in self.s['population']:
            increment(counts,item['family'])
        self.event('families.jsonl',{'cpu':self.clock(),'epoch':self.s['epoch'],'counts':counts})


def initial(task):
    population = task['founders']
    best = min(population,key=lambda p:key(p['scores'],task['target']))
    return {'population':population,'children':[],'epoch':0,'episodes':0,'iterations':0,
            'restarts':0,'best':best,'curves':[{'cpu':0.0,'scores':best['scores'],'graph6':best['graph6']}],
            'observed_best':{t:min(population,key=lambda p:key(p['scores'],t)) for t in ('W','L1','F','Linf')},
            'episode':None,'path':None,'batch':None,'tabu':{},'histogram':{},'parent_families':{},
            'evaluated_moves':{},'adopted_moves':{},'replayed_moves':0,'complete_batches':0,
            'milestones':{},'last_improvement_wall':time.time()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    args = parser.parse_args()
    directory = args.directory.resolve()
    root = directory.parent.parent
    task = read(directory/'task.json')
    ceiling = read(root/'budget.json')['per_job_cpu_seconds'] if task['kind']=='compare' else task['worker_cpu_seconds']
    signal.signal(signal.SIGTERM,stopping)
    signal.signal(signal.SIGINT,stopping)
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    if task['kind']=='controls':
        resource.setrlimit(resource.RLIMIT_CPU,(math.ceil(ceiling)-1,math.ceil(ceiling)))
        import controls
        report = controls.run()
        atomic(directory/'result.json',report)
        return
    receipt_path = directory/'receipt.json'
    previous = read(receipt_path) if receipt_path.exists() else None
    base = previous.get('budget_cpu_seconds',previous['cpu_seconds']) if previous else 0.0
    if previous and previous['status']=='COMPLETE':
        base = max(base,read(directory/'result.json')['endpoint_cpu_seconds'])
    task_hash = sha((directory/'task.json').read_bytes())
    if previous:
        if previous['task_sha256']!=task_hash or previous['result_sha256']!=sha((directory/'result.json').read_bytes()):
            raise ValueError('Previous receipt mismatch')
    resource.setrlimit(resource.RLIMIT_CPU,(max(1,math.ceil(ceiling-base)+2),max(2,math.ceil(ceiling-base)+3)))
    reserve = task['config']['closing_reserve_cpu_seconds']
    deadline = max(0,ceiling-base-reserve)
    checkpoint = directory/'checkpoint.json'
    rng = random.Random(task['seed'])
    if checkpoint.exists():
        wrapper = read(checkpoint)
        state = wrapper['state']
        if wrapper['sha256']!=sha(json.dumps(state,sort_keys=True).encode()) or state['task_sha256']!=task_hash:
            raise ValueError('Changed or corrupt checkpoint')
        if previous and previous['checkpoint_sha256']!=sha(checkpoint.read_bytes()):
            raise ValueError('Receipt/checkpoint mismatch')
        rng.setstate(tuple_state(state['rng']))
    else:
        if previous:
            raise ValueError('Receipt without search state')
        state = initial(task)
        state['task_sha256'] = task_hash
    archive = Archive(directory/'archive.sqlite',task['config']['sqlite_cache_kib'])
    for item in task['founders']:
        archive.put(item)
    guard = Guard(deadline,root)
    observer = Observer(directory,task,state,archive,guard,base,ceiling)
    engine = Engine(task,state,rng,observer)

    def save():
        state['rng'] = rng.getstate()
        state['checkpoint_cpu_seconds'] = base+cpu()
        state['archive_classes'] = archive.count()
        state['endpoint_classes'] = archive.count(True)
        payload = json.loads(json.dumps(state))
        atomic(checkpoint,{'state':payload,'sha256':sha(json.dumps(payload,sort_keys=True).encode())})

    observer.save = save
    guard.callback = observer.tick
    reason = 'CPU_LIMIT'
    try:
        while True:
            guard.check()
            engine.step(guard)
    except Halt as error:
        reason = str(error)
    state['status'] = 'SOLUTION' if (root/'SOLUTION.json').exists() else 'COMPLETE' if reason=='CPU_LIMIT' else 'PAUSED'
    observer.tick()
    current = state['episode']['current'] if state['episode'] else state['path']['current'] if state['path'] else state['best']
    observer.endpoint(current,'BUDGET_OR_PAUSE_OBSERVATION')
    if state['status']=='COMPLETE' and str(ceiling) not in state['milestones']:
        # No search is performed in the common closing reserve. Carry last best forward.
        observer.capture(ceiling,base+cpu())
    save()
    atomic(directory/'result.json',{'status':state['status'],'best':state['best'],'curves':state['curves'],
           'observed_best':state['observed_best'],'milestones':state['milestones'],'episodes':state['episodes'],
           'iterations':state['iterations'],'restarts':state['restarts'],'histogram':state['histogram'],
           'continuing_path':state['path'],'current':current,'final_population':state['population'],
           'archive_classes':state['archive_classes'],'endpoint_classes':state['endpoint_classes'],
           'evaluated_moves':state['evaluated_moves'],'adopted_moves':state['adopted_moves'],
           'parent_families':state['parent_families'],'replayed_moves':state['replayed_moves'],
           'complete_batches':state['complete_batches'],'endpoint_cpu_seconds':ceiling,
           'search_stop_cpu_seconds':base+cpu(),'closing_reserve_cpu_seconds':reserve,
           'continuation_retains':{'episode':state['episode'] is not None,'path':state['path'] is not None,
                                   'pending_batch':state['batch'] is not None}})
    archive.close()


if __name__=='__main__':
    main()
