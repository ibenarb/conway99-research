"""Meaningful lifecycle/coverage controls; mock tasks only, no C99 search."""
import copy
import json
from pathlib import Path
import signal
import sys
import tempfile
import time
from unittest.mock import patch
import cube_plan
import engine
import experiment


def run():
    rows = []
    data = json.loads((experiment.ROOT/'results/c2_autonomous_20260919/cube_plan.json').read_text())
    tasks = experiment.task_plan(data)
    assert len(tasks)==216 and sum(t['cpu_budget'] for t in tasks)==37440
    assert experiment.task_plan(data)==tasks
    for case in cube_plan.CASES:
        leaves = cube_plan.validate_tree(data['cases'][case]['tree'])
        assert len(leaves)==8 and len({tuple(c) for c in leaves})==8
        bad = copy.deepcopy(data['cases'][case]['tree'])
        bad['children'].pop()
        try:
            cube_plan.validate_tree(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Missing cover branch accepted')
        for variant in experiment.VARIANTS:
            for seed in (0,1):
                actual = [t['cube'] for t in tasks if (t['phase'],t['case'],t['variant'],t['seed'])==('cubes',case,variant,seed)]
                assert {tuple(c) for c in actual}=={tuple(c) for c in leaves}
    rows.append('216 fixed tasks; 37440 CPU-s; same complete cover across variants/seeds; damaged cover rejected')
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = root/'base.cnf'
        source.write_text('p cnf 2 1\n1 2 0\n')
        dest = root/'cube.cnf'
        path,digest = experiment.make_input(source,dest,[1,-2])
        assert path.read_text()=='p cnf 2 3\n1 2 0\n1 0\n-2 0\n'
        assert source.read_text()=='p cnf 2 1\n1 2 0\n'
        rows.append('Cube input header/body/units preserved')
        # Two simultaneous processes; real OS signals and wait4, not mocked.
        jobs=[]
        for i in range(2):
            attempt=root/f'cpu{i}'
            attempt.mkdir()
            task={'id':f'cpu{i}','cpu_budget':1,'wall_budget':10}
            jobs.append(engine.Job(task,[sys.executable,'-c','while True: pass'],attempt))
        completed=[]
        started=time.monotonic()
        while jobs:
            for job in list(jobs):
                r=job.poll()
                if r is not None:
                    assert r['status']=='CPU_BUDGET',r
                    assert r['cpu_seconds']>=0.5 and r['cpu_seconds']<4
                    completed.append(r)
                    jobs.remove(job)
            assert time.monotonic()-started<15
            time.sleep(0.05)
        assert len(completed)==2
        rows.append('Two concurrent CPU-limited children reaped with per-job resource usage')
        attempt=root/'interrupted'
        attempt.mkdir()
        job=engine.Job({'id':'sleep','cpu_budget':5},[sys.executable,'-c','import time; time.sleep(30)'],attempt)
        job.stop('INTERRUPTED')
        r=None
        while r is None:
            r=job.poll()
            time.sleep(0.05)
        assert r['status']=='INTERRUPTED'
        engine.save(attempt/'latest.json',r)
        assert experiment.recorded_result(attempt) is None
        rows.append('Interrupted task is resumable and own child is stopped')
        # Whole scheduler with tiny mock solver tasks, plus a completed restart.
        fake=root/'fake_solver'
        fake.write_text('#!'+sys.executable+'\nimport time\ntime.sleep(0.1)\nprint("c UNKNOWN")\n')
        fake.chmod(0o755)
        selected=[]
        paths={}
        for i,variant in enumerate(experiment.VARIANTS):
            selected.append({'id':'tiny_'+variant,'phase':'roots','case':'matching_6',
                             'variant':variant,'seed':0,'cube_index':0,'cube':[], 'cpu_budget':2})
            paths['matching_6',variant]=source
        work=root/'scheduler'
        work.mkdir()
        with patch.object(experiment,'SOLVER',fake),patch.object(experiment,'foreign_processes',return_value=[]),patch.object(experiment,'require_resources',return_value={}),patch.object(experiment,'available',return_value=4*engine.GIB):
            summary=experiment.execute(work,selected,paths)
            assert summary['status']=='COMPLETE' and summary['completed_budget_tasks']==4
            before=sorted(str(p) for p in work.rglob('solver.log'))
            summary=experiment.execute(work,selected,paths)
            assert summary['status']=='COMPLETE'
            assert before==sorted(str(p) for p in work.rglob('solver.log'))
        rows.append('Scheduler completes four tasks; restart creates no duplicate attempts')
        latest=work/'jobs'/'tiny_totalizer'/'latest.json'
        r=json.loads(latest.read_text())
        (Path(r['attempt'])/'solver.log').write_text('changed')
        try:
            experiment.recorded_result(latest.parent)
        except RuntimeError:
            rows.append('Changed archived log rejected')
        else:
            raise AssertionError('Changed completed result trusted')
    return {'status':'C2_AUTONOMOUS_CONTROLS_PASS','controls':rows,
            'scope':'Small lifecycle and coverage tests, no C99 SAT search.',
            'sources':{p.name:engine.sha(p) for p in Path(__file__).parent.glob('*.py')}}


if __name__=='__main__':
    if not __debug__:
        raise RuntimeError('Assertions required')
    result=run()
    Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
