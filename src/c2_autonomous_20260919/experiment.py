"""C2 Office autonomous 1.1.0: fixed 24 root and up to 192 cube jobs, two slots."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time
import zipfile
from engine import GIB, TERMINAL, Job, available, foreign_processes, limits, save, sha
from cube_plan import CASES, validate_tree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src/c2_residual_20260919'))
from office_pilot import SOLVER_SHA, windows_free

VERSION = '1.1.0'
VARIANTS = ('totalizer','lex','triangles','both')
LEGACY = Path.home()/'conway99_workspace/Conway99_C2_Office_Residual_1.0.0'
SOLVER = Path.home()/'conway99_workspace/cadical_office_2.2.1/build/cadical'


def task_plan(cubes):
    phases = []
    rng = random.Random(20260919)
    for phase,budget in [('roots',600),('cubes',120)]:
        rows = []
        for case in CASES:
            leaves = [[]] if phase == 'roots' else cubes['cases'][case]['leaves']
            if phase == 'cubes' and not cubes['cases'][case]['cube_gate']:
                continue
            for index,cube in enumerate(leaves):
                for variant in VARIANTS:
                    for seed in (0,1):
                        name = f'{phase}__{case}__{variant}__s{seed}__c{index}'
                        rows.append({'id':name,'phase':phase,'case':case,'variant':variant,
                                     'seed':seed,'cube_index':index,'cube':cube,'cpu_budget':budget})
        rng.shuffle(rows)
        phases.extend(rows)
    return phases


def bounded(command, log, cpu=600):
    with log.open('wb') as stream:
        proc = subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL,start_new_session=True,
                                preexec_fn=limits(cpu,output=256*1024**2))
        try:
            began = time.monotonic()
            last_notice = began
            while proc.poll() is None:
                if available() < GIB or shutil.disk_usage(log.parent).free < 2*GIB:
                    raise RuntimeError('Preparation resource reserve reached')
                if time.monotonic()-began > 4*cpu+30:
                    raise RuntimeError('Preparation wall deadline')
                if time.monotonic()-last_notice >= 600:
                    print('PREPARE_STATUS '+json.dumps({'log':str(log),'elapsed_s':round(time.monotonic()-began)}),flush=True)
                    last_notice = time.monotonic()
                time.sleep(0.25)
            code = proc.returncode
        except BaseException:
            proc.kill()
            proc.wait()
            raise
    if code:
        raise RuntimeError(f'Preparation failed ({code}); inspect {log}')


def require_resources(root, minimum=3*GIB):
    if available() < minimum:
        raise RuntimeError('Insufficient available RAM; no launch')
    if shutil.disk_usage(root).free < 5*GIB:
        raise RuntimeError('Need 5 GiB Linux reserve')
    return {'mem_available':available(),'linux_free':shutil.disk_usage(root).free,
            'windows_C_free':windows_free(),'load_average':os.getloadavg(),'time':time.time()}


def prepare(work, pinned, cubes):
    paths = {}
    for case in CASES:
        directory = work/'variants'/case
        if not (directory/'manifest.json').exists():
            temporary = directory.with_name(case+'_preparing')
            if temporary.exists():
                temporary.rename(temporary.with_name(temporary.name+'_'+str(time.time_ns())))
            directory.parent.mkdir(parents=True,exist_ok=True)
            if case == 'matching_6' and (LEGACY/'office_variants_6/manifest.json').exists():
                temporary.mkdir()
                for name in ['manifest.json','variables.json',*[case+'__'+v+'.cnf' for v in VARIANTS]]:
                    source = LEGACY/'office_variants_6'/name
                    try:
                        os.link(source,temporary/name)
                    except OSError:
                        shutil.copyfile(source,temporary/name)
            else:
                print('PREPARE '+case,flush=True)
                require_resources(work)
                bounded([sys.executable,str(ROOT/'src/c2_residual_20260919/residual.py'),
                         'prepare','--certificates',str(ROOT/'results/c2_residual_20260919/certificates'),
                         '--out',str(temporary),'--case',case],work/(case+'_prepare.log'))
            temporary.rename(directory)
        if sha(directory/'variables.json') != 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e':
            raise RuntimeError('Prepared primary mapping mismatch')
        for variant in VARIANTS:
            path = directory/(case+'__'+variant+'.cnf')
            if sha(path) != pinned[case,variant]:
                raise RuntimeError('Prepared CNF hash mismatch: '+str(path))
            paths[case,variant] = path
    binary = work/'up'
    source = ROOT/'src/c2_residual_20260919/up.cpp'
    if not binary.exists():
        bounded(['g++','-O2','-std=c++17',str(source),'-o',str(binary)],work/'up_build.log',120)
    marker = work/'cube_validation.json'
    if marker.exists():
        old = json.loads(marker.read_text())
        if old['cube_sha256'] != sha(ROOT/'results/c2_autonomous_20260919/cube_plan.json') or old['up_sha256'] != sha(binary):
            raise RuntimeError('Stored cube validation identity changed')
    else:
        rows = []
        for case in CASES:
            leaves = validate_tree(cubes['cases'][case]['tree'])
            if leaves != cubes['cases'][case]['leaves']:
                raise RuntimeError('Leaf list differs from tree')
            base = paths[case,'totalizer']
            if sha(base) != cubes['cases'][case]['base_sha256']:
                raise RuntimeError('Cube base mismatch')
            for i,cube in enumerate(leaves):
                log = work/'up_check.json'
                bounded([str(binary),str(base),*map(str,cube)],log,60)
                result = json.loads(log.read_text())
                rows.append({'case':case,'cube_index':i,**result})
            opened = sum(not r['conflict'] for r in rows if r['case']==case)
            if opened != cubes['cases'][case]['up_open_leaves']:
                raise RuntimeError('Office cube UP differs from frozen plan')
            print('CUBE_COVER_VERIFIED '+case+' open='+str(opened)+'/8',flush=True)
        save(marker,{'cube_sha256':sha(ROOT/'results/c2_autonomous_20260919/cube_plan.json'),
                     'up_sha256':sha(binary),'rows':rows,'coverage':'Complete binary tree checked; no proof percentage.'})
    return paths


def make_input(source, target, cube):
    if not cube:
        return source,sha(source)
    with source.open('rb') as src,target.open('xb') as dst:
        header = src.readline().decode().split()
        if header[:2] != ['p','cnf']:
            raise ValueError('Bad input header')
        dst.write(f'p cnf {header[2]} {int(header[3])+len(cube)}\n'.encode())
        shutil.copyfileobj(src,dst)
        for literal in cube:
            dst.write(f'{literal} 0\n'.encode())
    return target,sha(target)


def check_sat(log, task, attempt):
    from residual import CNF, Frame
    from c2_reference import read_primary_model, reconstruct, verify_graph
    c,f = CNF(),Frame(14)
    try:
        f.allocate(c)
        values = read_primary_model(log,len(f.map))
        if any(values[abs(x)] != (x>0) for x in task['cube']):
            raise ValueError('SAT witness violates cube')
        graph = reconstruct(f,values)
        if not verify_graph(graph,14):
            raise ValueError('SAT witness fails direct graph check')
        save(attempt/'verified_graph.json',graph)
    finally:
        c.close()


def recorded_result(directory):
    latest = directory/'latest.json'
    completed_attempts = sorted(directory.glob('attempt_*/result.json'))
    if completed_attempts:
        result = json.loads(completed_attempts[-1].read_text())
    elif latest.exists():
        result = json.loads(latest.read_text())
    else:
        return None
    if result['status'] not in TERMINAL:
        return None
    log = Path(result['attempt'])/'solver.log'
    if not log.exists() or sha(log) != result['log_sha256']:
        raise RuntimeError('Archived result log identity mismatch')
    if result['task_id'] != directory.name:
        raise RuntimeError('Archived result task mismatch')
    return result


def finish(job, result, results):
    if result['status'] == 'SAT_REQUIRES_CHECK':
        try:
            check_sat(job.log,job.task,job.attempt)
            result['status'] = 'SAT_VERIFIED'
        except Exception as error:
            result['status'] = 'INVALID_SAT_WITNESS'
            result['error'] = repr(error)
    save(job.attempt/'result.json',result)
    save(job.attempt.parent/'latest.json',result)
    results[job.task['id']] = result
    # Only a derived, reproducible cube input is removed, never a log or proof.
    temporary = job.attempt/'input.cnf'
    if temporary.exists():
        temporary.unlink()
    print('DONE '+json.dumps({'task':job.task['id'],'status':result['status'],
                             'cpu_s':round(result['cpu_seconds'],2),
                             'rss_MiB':round(result['peak_rss_bytes']/1024**2,1)}),flush=True)


def aggregate(tasks, results):
    rows = []
    for phase in ('roots','cubes'):
        for case in CASES:
            for variant in VARIANTS:
                selected = [t for t in tasks if (t['phase'],t['case'],t['variant'])==(phase,case,variant)]
                done = [(t,results[t['id']]) for t in selected if t['id'] in results]
                counts = {}
                for _,r in done:
                    counts[r['status']] = counts.get(r['status'],0)+1
                # A surviving side is a property of the frozen labelled split,
                # not a fraction of the graph solution space or a proof progress bar.
                sides = {}
                for t,r in done:
                    if t['cube'] and r['status'] != 'UNSAT_UNCERTIFIED':
                        side = str(t['cube'][0])
                        sides[side] = sides.get(side,0)+1
                rows.append({'phase':phase,'case':case,'variant':variant,'planned':len(selected),
                             'finished':len(done),'statuses':counts,
                             'cpu_seconds':sum(r['cpu_seconds'] for _,r in done),
                             'max_rss_bytes':max((r['peak_rss_bytes'] for _,r in done),default=0),
                             'unclosed_leaf_seed_tasks_by_first_split':sides,
                             'by_seed':{str(seed):{'tasks':sum(t['seed']==seed for t,r in done),
                                                  'unsat_uncertified':sum(t['seed']==seed and r['status']=='UNSAT_UNCERTIFIED' for t,r in done),
                                                  'cpu_seconds':sum(r['cpu_seconds'] for t,r in done if t['seed']==seed)} for seed in (0,1)}})
    return rows


def report(work, status, tasks, results, detail=None):
    result = {'version':VERSION,'status':status,'work_dir':str(work),'detail':detail,
              'task_count':len(tasks),'completed_budget_tasks':sum(r['status'] in TERMINAL for r in results.values()),
              'cpu_seconds':sum(r['cpu_seconds'] for r in results.values()),'rows':aggregate(tasks,results),
              'interpretation':'Timeouts are censored. UNSAT without proof is uncertified. Lex may close a labelled cube by representative choice. No automatic winner; inspect full cover and seeds.',
              'solver_sha256':SOLVER_SHA,'cube_plan_sha256':sha(ROOT/'results/c2_autonomous_20260919/cube_plan.json')}
    attempts = [json.loads(p.read_text()) for p in (work/'jobs').glob('*/attempt_*/result.json')]
    result['all_recorded_attempt_cpu_seconds'] = sum(r['cpu_seconds'] for r in attempts)
    result['unrecorded_interruption_cost'] = 'A process interrupted before result.json cannot be assigned a measured final CPU cost.'
    save(work/'summary.json',result)
    lines = ['# C2 Office autonomous '+VERSION, '', 'Status: '+status, '',
             'Timeouts remain open; UNSAT is uncertified. No automatic performance winner.', '',
             '| Phase | Case | Variant | Done | UNSAT (uncertified) | CPU seconds |',
             '|---|---|---|---:|---:|---:|']
    for row in result['rows']:
        lines.append('| '+row['phase']+' | '+row['case']+' | '+row['variant']+' | '+str(row['finished'])+
                     ' | '+str(row['statuses'].get('UNSAT_UNCERTIFIED',0))+' | '+str(round(row['cpu_seconds'],2))+' |')
    lines.extend(['', 'Use summary.json for both seeds separately and surviving first-split sides.',
                  'Lex can close labelled cubes through representative choice. Assess the complete cover.',
                  'Completed budget tasks are reused on restart, including censored timeouts. Interrupted tasks restart from scratch.',
                  '', 'Detail: '+str(detail)])
    (work/'REPORT.md').write_text('\n'.join(lines)+'\n')
    return result


def archive(work):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    path = work/f'Conway99_C2_Autonomous_{VERSION}_{stamp}.zip'
    candidates = [p for p in work.rglob('*') if p.is_file() and
                  ('variants' not in p.relative_to(work).parts) and
                  p.suffix in ('.json','.log','.md') and p.name != 'up_check.json']
    size = sum(p.stat().st_size for p in candidates)
    if shutil.disk_usage(work).free < 5*GIB+size:
        raise RuntimeError('Insufficient Linux export reserve')
    with zipfile.ZipFile(path,'x',zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT/'FILES_SHA256.json','package/FILES_SHA256.json')
        for p in sorted(candidates):
            z.write(p,'run/'+str(p.relative_to(work)))
        for directory in ('src','docs','results','releases'):
            for p in (ROOT/directory).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.md','.json'):
                    z.write(p,'package/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise RuntimeError('Export CRC failure')
    output = {'archive':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
    downloads = Path('/mnt/c/Users/rb/Downloads')
    try:
        if downloads.is_dir() and windows_free() > 20*GIB+path.stat().st_size:
            dest = downloads/path.name
            with path.open('rb') as src,dest.open('xb') as dst:
                shutil.copyfileobj(src,dst)
            if sha(dest) != output['sha256']:
                raise RuntimeError('Copied export hash mismatch')
            output['windows_download'] = str(dest)
    except Exception as error:
        output['windows_copy_error'] = repr(error)
    save(work/'export_receipt.json',output)
    return output


def execute(work, tasks, paths):
    results,active = {},{}
    for task in tasks:
        result = recorded_result(work/'jobs'/task['id'])
        if result is not None:
            results[task['id']] = result
    if any(r['status']=='SAT_VERIFIED' for r in results.values()):
        return report(work,'SAT_REVIEW_REQUIRED',tasks,results,'Existing verified SAT witness; no further search')
    start = time.monotonic()
    last_status,last_external,last_host = 0.0,0.0,0.0
    stopped = None
    resources = []
    try:
        for phase in ('roots','cubes'):
            queue = [t for t in tasks if t['phase']==phase and t['id'] not in results]
            while queue or active:
                now = time.monotonic()
                if available() < GIB or shutil.disk_usage(work).free < 2*GIB:
                    raise RuntimeError('RESOURCE_STOP: RAM or Linux reserve')
                if now-last_external >= 30:
                    foreign = foreign_processes({j.proc.pid for j in active.values()})
                    if foreign:
                        raise RuntimeError('EXTERNAL_ACTIVITY: '+repr(foreign))
                    last_external = now
                # Probe between launches at most once a minute; hard child limits
                # remain effective even during the bounded Windows query.
                if queue and len(active)<2 and now-last_host>=60:
                    resources.append(require_resources(work,minimum=int(2.5*GIB)))
                    save(work/'resources.json',resources)
                    last_host = time.monotonic()
                while queue and len(active)<2:
                    if available() < int(2.5*GIB):
                        if not active:
                            raise RuntimeError('RESOURCE_STOP: cannot safely admit next job')
                        break
                    task = queue.pop(0)
                    directory = work/'jobs'/task['id']
                    directory.mkdir(parents=True,exist_ok=True)
                    attempt = directory/('attempt_'+str(time.time_ns()))
                    attempt.mkdir()
                    file,hash_value = make_input(paths[task['case'],task['variant']],attempt/'input.cnf',task['cube'])
                    save(attempt/'input.json',{'sha256':hash_value,'cube':task['cube'],
                                             'base_sha256':sha(paths[task['case'],task['variant']])})
                    command = [str(SOLVER),f'--seed={task["seed"]}',str(file)]
                    job = Job(task,command,attempt)
                    active[job.proc.pid] = job
                    print('START '+task['id'],flush=True)
                for pid,job in list(active.items()):
                    result = job.poll()
                    if result is not None:
                        finish(job,result,results)
                        del active[pid]
                        if result['status'] == 'SAT_VERIFIED':
                            raise RuntimeError('SAT_VERIFIED: stop for independent inspection')
                        if result['status'] not in TERMINAL:
                            raise RuntimeError('TECHNICAL_STOP: '+result['status'])
                if now-last_status>=600:
                    done = sum(r['status'] in TERMINAL for r in results.values())
                    remaining = sum(t['cpu_budget'] for t in tasks if t['id'] not in results)
                    remaining -= sum(min(j.cpu_sample,j.task['cpu_budget']) for j in active.values())
                    print('STATUS '+json.dumps({'phase':phase,'completed':done,'total':len(tasks),
                                               'active':len(active),'elapsed_s':round(now-start),
                                               'nominal_remaining_wall_h_at_two_CPUs':round(remaining/7200,2),
                                               'ETA_note':'Nominal budget bound plus overhead; background load can delay.'}),flush=True)
                    report(work,'RUNNING',tasks,results)
                    last_status = now
                time.sleep(0.5)
    except (Exception,KeyboardInterrupt) as error:
        stopped = repr(error)
        reason = 'INTERRUPTED' if isinstance(error,KeyboardInterrupt) else 'RESOURCE_STOP'
        for job in active.values():
            job.stop(reason)
        while active:
            for pid,job in list(active.items()):
                result = job.poll()
                if result is not None:
                    finish(job,result,results)
                    del active[pid]
            time.sleep(0.1)
    return report(work,'PAUSED' if stopped else 'COMPLETE',tasks,results,stopped)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Prepare, run and resume this fixed experiment')
    args = parser.parse_args()
    if not args.run:
        parser.error('Use --run to launch the fixed experiment')
    work = ROOT/'work'
    work.mkdir(exist_ok=True)
    lock = (work/'controller.lock').open('a+')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('Another controller already owns this experiment')
    manifest = json.loads((ROOT/'FILES_SHA256.json').read_text())
    for name,expected in manifest.items():
        if sha(ROOT/name)!=expected:
            raise RuntimeError('Package identity mismatch: '+name)
    if sha(SOLVER)!=SOLVER_SHA:
        raise RuntimeError('Office solver identity mismatch')
    if foreign_processes(set()):
        raise RuntimeError('Other research processes detected; nothing launched')
    print('AUTONOMOUS_PREPARING: source hashes checked; two slots; no proof logging.',flush=True)
    require_resources(work)
    cubes = json.loads((ROOT/'results/c2_autonomous_20260919/cube_plan.json').read_text())
    for case in CASES:
        if validate_tree(cubes['cases'][case]['tree']) != cubes['cases'][case]['leaves']:
            raise RuntimeError('Invalid cube coverage')
    tasks = task_plan(cubes)
    plan = {'version':VERSION,'tasks':tasks,'cube_plan_sha256':sha(ROOT/'results/c2_autonomous_20260919/cube_plan.json'),
            'slots':2,'seeds':[0,1],'cpu_budget_sum':sum(t['cpu_budget'] for t in tasks)}
    planfile = work/'task_plan.json'
    if planfile.exists() and json.loads(planfile.read_text()) != plan:
        raise RuntimeError('Existing task plan differs; no mixed experiment')
    save(planfile,plan)
    source = json.loads((ROOT/'results/c2_residual_20260919/variants.json').read_text())
    pinned = {(j['case'],j['variant']):j['sha256'] for j in source['jobs']}
    paths = prepare(work,pinned,cubes)
    result = execute(work,tasks,paths)
    receipt = archive(work)
    print('C2_AUTONOMOUS_RESULT '+json.dumps({'status':result['status'],
          'completed':result['completed_budget_tasks'],'tasks':len(tasks),
          'cpu_hours':result['cpu_seconds']/3600,'detail':result['detail'],**receipt}),flush=True)


if __name__ == '__main__':
    main()
