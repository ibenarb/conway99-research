"""Frozen 192-worker-CPU-hour paired campaign, resumable without new tasks."""
import bootstrap
from common import atomic, checked, core, sha
from archive import file_sha
from runtime import read, process
from queueing import Queue, validate_receipt
from resources import snapshot
from search import key
from pathlib import Path
import argparse
import fcntl
import importlib.metadata
import json
import os
import resource
import shutil
import subprocess
import sys
import tarfile
import time

HERE = bootstrap.HERE
RELATIVE = Path('experiments/memetik/lambda_compare_0_2_0')
TARGETS = ('W','L1','F','Linf')
VARIANTS = ('B0','P','T','TC')


def environment():
    return {'python':sys.version,'pynauty':importlib.metadata.version('pynauty')}


def prepare(run):
    if run.exists():
        raise FileExistsError('Choose a new run directory')
    pins = read(HERE.parent/'lambda_strategy_0_1_0/source_hashes.json')
    for name,digest in pins.items():
        if sha((bootstrap.ROOT/name).read_bytes())!=digest:
            raise RuntimeError('Pinned reference changed: '+name)
    founders = read(HERE/'founders.json')
    for item in founders:
        rows,scores = checked(item['graph6'],'lambda')
        if scores!=item['scores'] or core.canonical(rows)!=item['class'] or sha(item['graph6'].encode())!=item['state']:
            raise ValueError('Invalid founder')
    if len(founders)!=16 or len({f['class'] for f in founders})!=16:
        raise ValueError('Expected 16 distinct founder classes')
    config = read(HERE/'config.json')
    jobs = []
    for replicate in range(config['replicates']):
        seed = core.derive_seed(config['seed_master'],['lambda-compare',replicate])
        for ti,target in enumerate(TARGETS):
            shift = (replicate+ti)%4
            for variant in VARIANTS[shift:]+VARIANTS[:shift]:
                jobs.append({'id':f'{variant}--lambda-{target}-{replicate:02d}','kind':'compare',
                             'arm':'lambda','target':target,'variant':variant,'replicate':replicate,
                             'seed':seed,'worker_cpu_seconds':config['worker_cpu_seconds'],
                             'founders':founders,'config':config})
    if len(jobs)!=192 or sum(t['worker_cpu_seconds'] for t in jobs)!=192*3600:
        raise ValueError('Unexpected initial design')
    run.mkdir(parents=True)
    paths = []
    for sub in ('ryzen_compare_0_4_0','move_accel_0_1_0','lambda_strategy_0_1_0','lambda_review_20260921','lambda_compare_0_2_0'):
        paths.extend((HERE.parent/sub).glob('*.py'))
    paths += [HERE/name for name in ('founders.json','config.json')]
    paths += [HERE.parent/'lambda_strategy_0_1_0/source_hashes.json']
    paths += [bootstrap.ROOT/p for p in ('src/memetic_v2/core.py','src/memetic_v2/verify.py','experiments/memetik/escape_0_2/operators.py',
                                      'docs/memetik/lambda_review_20260921/CHECK.json')]
    hashes = {}
    for source in sorted(set(paths)):
        relative = source.relative_to(bootstrap.ROOT)
        dest = run/'bundle'/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(source.read_bytes())
        hashes[str(relative)] = sha(dest.read_bytes())
    manifest = {'version':config['version'],'jobs':jobs,'workers':config['workers'],
                'initial_comparison_cpu_seconds':192*3600,
                'controls':{'id':'controls','kind':'controls','worker_cpu_seconds':config['controls_worker_cpu_seconds']},
                'initial_campaign_authorized':True,'automatic_extension':False}
    atomic(run/'manifest.json',manifest)
    atomic(run/'fingerprint.json',{'environment':environment(),'files':hashes,'manifest_sha256':sha((run/'manifest.json').read_bytes())})
    atomic(run/'budget.json',{'revision':0,'per_job_cpu_seconds':3600,
                             'history':[{'revision':0,'per_job_cpu_seconds':3600,'reason':'initial authorized 192 CPU-hour comparison'}]})
    print(json.dumps({'status':'PREPARED_NOT_STARTED','run':str(run),'jobs':192,'comparison_cpu_hours':192,
                      'controls_cpu_ceiling_hours':1,'workers':18},indent=2))


def verify(run):
    signature = read(run/'fingerprint.json')
    if environment()!=signature['environment']:
        raise RuntimeError('Frozen environment changed')
    if sha((run/'manifest.json').read_bytes())!=signature['manifest_sha256']:
        raise RuntimeError('Frozen manifest changed')
    for name,digest in signature['files'].items():
        if sha((run/'bundle'/name).read_bytes())!=digest:
            raise RuntimeError('Frozen source changed: '+name)
    budget = read(run/'budget.json')
    history = budget['history']
    if not history or history[0]['per_job_cpu_seconds']!=3600 or budget['revision']!=len(history)-1:
        raise RuntimeError('Invalid budget ledger')
    for i,entry in enumerate(history):
        if entry['revision']!=i or (i and entry['per_job_cpu_seconds']<=history[i-1]['per_job_cpu_seconds']):
            raise RuntimeError('Non-monotone budget ledger')
    if budget['per_job_cpu_seconds']!=history[-1]['per_job_cpu_seconds']:
        raise RuntimeError('Budget/ledger mismatch')
    for entry in history[1:]:
        path = run/'stages'/entry['snapshot']/'manifest.json'
        if sha(path.read_bytes())!=entry['snapshot_sha256']:
            raise RuntimeError('Changed earlier endpoint manifest')
        for name,digest in read(path)['files'].items():
            if sha((path.parent/name).read_bytes())!=digest:
                raise RuntimeError('Changed earlier endpoint: '+name)


def unlocked(run):
    lock = (run/'controller.lock').open('a+')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if any((run/'tasks').glob('*/active.json')) or any(not read(p)['clean'] for p in run.glob('*_timing.json')):
        lock.close()
        raise RuntimeError('Unclean process/CPU state: diagnose before continuation')
    return lock


def evaluate(run):
    manifest = read(run/'manifest.json')
    limit = read(run/'budget.json')['per_job_cpu_seconds']
    control = run/'tasks'/'controls'
    receipt = validate_receipt(control)
    if read(control/'result.json')['status']!='CONTROLS_PASS' or receipt['cpu_seconds']>manifest['controls']['worker_cpu_seconds']:
        raise RuntimeError('Controls did not pass within budget')
    results,cpu_total = {},0.
    for task in manifest['jobs']:
        d = run/'tasks'/task['id']
        receipt = validate_receipt(d)
        result = read(d/'result.json')
        if read(d/'task.json')!=task or result['status']!='COMPLETE' or result['endpoint_cpu_seconds']!=limit:
            raise RuntimeError('Incomplete task: '+task['id'])
        reserve = task['config']['closing_reserve_cpu_seconds']
        if not limit-reserve-.1<=receipt['budget_cpu_seconds']<=limit or receipt['cpu_seconds']>receipt['budget_cpu_seconds']:
            raise RuntimeError('Unexpected CPU use: '+task['id'])
        for item in [result['best'],result['current']]+result['final_population']+list(result['observed_best'].values())+list(result['milestones'].values())+result['curves']:
            _,scores = checked(item['graph6'],'lambda')
            if scores!=item['scores']:
                raise RuntimeError('Invalid result score')
        if not all(0<=p['cpu']<=limit for p in result['curves']):
            raise RuntimeError('Record outside budget')
        if not all(a['cpu']<=b['cpu'] and key(a['scores'],task['target'])>key(b['scores'],task['target']) for a,b in zip(result['curves'],result['curves'][1:])):
            raise RuntimeError('Invalid improvement curve')
        for mark in task['config']['milestones_cpu_seconds']+[limit]:
            if str(mark) not in result['milestones']:
                raise RuntimeError('Missing milestone')
            point = next(p for p in reversed(result['curves']) if p['cpu']<=mark)
            if result['milestones'][str(mark)]['scores']!=point['scores']:
                raise RuntimeError('Milestone/curve disagreement')
        results[task['id']] = result
        cpu_total += receipt['cpu_seconds']
    groups = []
    milestones = sorted(set([600,1800,3600,limit]))
    for target in TARGETS:
        for variant,control_variant in (('P','B0'),('T','P'),('TC','T'),('T','B0'),('TC','B0'),('TC','P')):
            for mark in milestones:
                pairs = [[results[f'{v}--lambda-{target}-{i:02d}']['milestones'][str(mark)]['scores'] for v in (control_variant,variant)] for i in range(12)]
                wins = sum(key(b,target)<key(a,target) for a,b in pairs)
                losses = sum(key(b,target)>key(a,target) for a,b in pairs)
                groups.append({'target':target,'variant':variant,'comparator':control_variant,'milestone_cpu':mark,
                               'wins':wins,'ties':12-wins-losses,'losses':losses,
                               'descriptive_selection_gate':wins>=8 and losses<=2,'paired_scores':pairs})
    report = {'status':'COMPARISON_VERIFIED','per_job_cpu_seconds':limit,'actual_comparison_cpu_hours':cpu_total/3600,
              'groups':groups,'interpretation':'paired descriptive results; W at 3600 is primary; no automatic significance or optimality claim',
              'results':results,'automatic_extension':False}
    atomic(run/'evaluation.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','groups')},indent=2))
    return report


def extend(run,hours):
    # Explicit command creates a new stage; old task seeds and states never change.
    lock = unlocked(run)
    try:
        verify(run)
        evaluate(run)
        budget = read(run/'budget.json')
        limit = int(hours*3600)
        if limit<=budget['per_job_cpu_seconds']:
            raise ValueError('New cumulative per-job hours must be greater')
        revision = budget['revision']+1
        stage = run/'stages'/f'endpoint-{budget["per_job_cpu_seconds"]}'
        if stage.exists():
            raise RuntimeError('Stage already exists; inspect before retry')
        stage.mkdir(parents=True)
        paths = [run/'budget.json',run/'evaluation.json']
        for pattern in ('*/task.json','*/receipt.json','*/result.json','*/checkpoint.json'):
            paths += list((run/'tasks').glob(pattern))
        hashes = {}
        for path in paths:
            relative = path.relative_to(run)
            dest = stage/relative
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(path,dest)
            hashes[str(relative)] = sha(dest.read_bytes())
        atomic(stage/'manifest.json',{'files':hashes,'archive_note':'receipt hashes bind archive at endpoint; active SQLite continues cumulatively'})
        entry = {'revision':revision,'per_job_cpu_seconds':limit,'reason':'explicit extend command',
                 'snapshot':stage.name,'snapshot_sha256':sha((stage/'manifest.json').read_bytes())}
        atomic(run/'budget.json',{'revision':revision,'per_job_cpu_seconds':limit,'history':budget['history']+[entry]})
        print(json.dumps({'status':'EXTENSION_PREPARED_NOT_STARTED','cumulative_per_job_hours':hours,
                          'additional_comparison_cpu_hours':192*(limit-budget['per_job_cpu_seconds'])/3600}))
    finally:
        lock.close()


def controller(run):
    verify(run)
    host = snapshot(run)
    if not host['may_launch'] or len(os.sched_getaffinity(0))<18:
        raise RuntimeError('Host guard/18 CPU affinity failed: '+json.dumps(host))
    pool = Queue(run)
    manifest = read(run/'manifest.json')
    try:
        gate = pool.run([manifest['controls']],1,'controls')
        if gate[0]['status']!='CONTROLS_PASS':
            raise RuntimeError('Controls failed')
        pool.run(manifest['jobs'],manifest['workers'],'comparison')
        evaluate(run)
    except Exception:
        pool.emergency_stop_owned()
        raise
    finally:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        atomic(run/('controller_cpu_'+str(time.time_ns())+'.json'),{'cpu_seconds':usage.ru_utime+usage.ru_stime,
                  'scope':'controller itself, including receipt verification; host probe child infrastructure separate'})
        pool.lock.close()


def export(run):
    lock = unlocked(run)
    try:
        verify(run)
        destination = run.with_suffix('.tar.gz')
        if destination.exists():
            raise FileExistsError(destination)
        hashes = {str(p.relative_to(run)):file_sha(p) for p in run.rglob('*') if p.is_file() and p.name!='export_manifest.json'}
        atomic(run/'export_manifest.json',{'files':hashes})
        with tarfile.open(destination,'w:gz') as archive:
            archive.add(run,arcname=run.name)
        print(json.dumps({'archive':str(destination),'sha256':file_sha(destination)}))
    finally:
        lock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','preflight','launch','run','status','evaluate','extend','export'))
    parser.add_argument('directory',type=Path)
    parser.add_argument('--cpu-hours',type=float)
    args = parser.parse_args()
    run = args.directory.resolve()
    if args.action=='prepare':
        prepare(run)
        return
    if args.action=='preflight':
        host = snapshot(run if run.exists() else run.parent)
        print(json.dumps({'environment':environment(),'affinity_cpus':len(os.sched_getaffinity(0)),'host':host},indent=2))
        if not host['may_launch'] or len(os.sched_getaffinity(0))<18:
            raise SystemExit(1)
        return
    verify(run)
    frozen = run/'bundle'/RELATIVE/'run.py'
    if Path(__file__).resolve()!=frozen:
        os.execv(sys.executable,[sys.executable,str(frozen)]+sys.argv[1:])
    if args.action=='run':
        controller(run)
    elif args.action=='launch':
        lock = unlocked(run)
        lock.close()
        with (run/'controller.log').open('ab') as log:
            child = subprocess.Popen([sys.executable,str(frozen),'run',str(run)],stdin=subprocess.DEVNULL,
                                     stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        atomic(run/'launcher.json',{'pid':child.pid,'start_ticks':process(child.pid)['start_ticks']})
        print(json.dumps({'status':'LAUNCHED_CHECK_LOG','pid':child.pid,'run':str(run)}))
    elif args.action=='status':
        print(json.dumps(read(run/'status.json'),indent=2))
    elif args.action=='evaluate':
        lock = unlocked(run)
        try:
            evaluate(run)
        finally:
            lock.close()
    elif args.action=='extend':
        if args.cpu_hours is None:
            parser.error('extend requires --cpu-hours (new cumulative hours PER JOB)')
        extend(run,args.cpu_hours)
    elif args.action=='export':
        export(run)


if __name__=='__main__':
    main()
