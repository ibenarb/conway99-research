"""Prepare only by default; explicit run starts the proposed 18-CPU-hour screen."""
import bootstrap
from common import atomic, core, checked, sha, cpu
from search import key
from runtime import Pool, read
import runtime
from resources import snapshot
from pathlib import Path
import argparse
import importlib.metadata
import json
import os
import resource
import subprocess
import sys
import time

HERE = bootstrap.HERE
RELATIVE = Path('experiments/memetik/lambda_strategy_0_1_0')
TARGETS = ('W', 'L1', 'F', 'Linf')
VARIANTS = ('A0', 'CYCLE', 'CYCLE_QUOTA')


def controller_cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    return own.ru_utime + own.ru_stime


def environment():
    return {'python': sys.version, 'pynauty': importlib.metadata.version('pynauty')}


def prepare(run):
    if run.exists():
        raise FileExistsError('Choose a new run directory')
    for name, digest in read(HERE / 'source_hashes.json').items():
        if sha((bootstrap.ROOT / name).read_bytes()) != digest:
            raise RuntimeError('Pinned baseline changed: '+name)
    founders = read(HERE / 'founders.json')
    for f in founders:
        rows, scores = checked(f['graph6'], 'lambda')
        if scores != f['scores'] or core.canonical(rows) != f['class']:
            raise ValueError('Founder invalid')
    assert len(founders) == len({p['class'] for p in founders}) == 16
    config = read(HERE / 'config.json')
    jobs = []
    for replicate in range(9):
        seed = core.derive_seed(2026092103, ['lambda-confirmation', 100+replicate])
        for ti, target in enumerate(TARGETS):
            order = list(VARIANTS)
            shift = (replicate+ti) % 3
            order = order[shift:] + order[:shift]
            for variant in order:
                jobs.append({'id': f'{variant}--lambda-{target}-{replicate:02d}', 'kind': 'compare',
                             'arm': 'lambda', 'target': target, 'variant': variant,
                             'replicate': replicate, 'seed': seed, 'worker_cpu_seconds': 600,
                             'founders': founders, 'config': config})
    run.mkdir(parents=True)
    paths = []
    for sub in ('ryzen_compare_0_4_0','move_accel_0_1_0','lambda_strategy_0_1_0'):
        paths.extend((HERE.parent / sub).glob('*.py'))
    paths += [HERE / name for name in ('founders.json','config.json','source_hashes.json')]
    paths += [bootstrap.ROOT / p for p in ('src/memetic_v2/core.py','src/memetic_v2/verify.py','experiments/memetik/escape_0_2/operators.py')]
    hashes = {}
    for path in paths:
        relative = path.relative_to(bootstrap.ROOT)
        dest = run / 'bundle' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        hashes[str(relative)] = sha(dest.read_bytes())
    manifest = {'version': 'lambda-strategy-0.1.0', 'jobs': jobs, 'workers': 18,
                'comparison_cpu_seconds': 64800, 'control_cpu_seconds': 600,
                'controls': {'id': 'controls', 'kind': 'controls', 'worker_cpu_seconds': 600},
                'decision': 'Exploratory paired screen; independent fresh-seed confirmation needed before main campaign',
                'main_campaign_authorized': False}
    atomic(run / 'manifest.json', manifest)
    atomic(run / 'fingerprint.json', {'environment': environment(), 'files': hashes,
                                     'manifest': sha((run / 'manifest.json').read_bytes())})
    print(json.dumps({'status': 'PREPARED_NOT_STARTED', 'run': str(run), 'jobs': 108,
                      'worker_cpu_hours': 18, 'controls_cpu_hours': 1/6}, indent=4))


def verify(run):
    signature = read(run / 'fingerprint.json')
    if environment() != signature['environment']:
        raise RuntimeError('Runtime changed')
    if sha((run / 'manifest.json').read_bytes()) != signature['manifest']:
        raise RuntimeError('Manifest changed')
    for name, digest in signature['files'].items():
        if sha((run / 'bundle' / name).read_bytes()) != digest:
            raise RuntimeError('Frozen file changed: '+name)


class SuccessPool(Pool):
    def check(self):
        usage = super().check()
        if time.monotonic() - getattr(self, 'last_size_check', 0) >= 15:
            self.last_size_check = time.monotonic()
            size = sum(p.stat().st_size for p in self.directory.rglob('*') if p.is_file())
            if size >= 2 * 1024**3:
                self.stop = True
                self.last_reason = ['RUN_STORAGE_LIMIT']
        previous = sum(read(p)['cpu_seconds'] for p in self.directory.glob('controller_cpu_*.json'))
        if controller_cpu() + previous >= 600:
            self.stop = True
            self.last_reason = ['CONTROLLER_CPU_LIMIT']
        if (self.directory / 'SOLUTION.json').exists():
            item = read(self.directory / 'SOLUTION.json')['candidate']
            rows, scores = checked(item['graph6'], 'lambda')
            if scores['F'] != 0:
                raise RuntimeError('Invalid success marker')
            self.stop = True
            self.last_reason = ['VERIFIED_SOLUTION']
        return usage


def evaluate(run):
    manifest = read(run / 'manifest.json')
    assert len(manifest['jobs']) == 108
    assert sum(t['worker_cpu_seconds'] for t in manifest['jobs']) == 64800
    control = run / 'tasks' / 'controls'
    gate, receipt = read(control / 'result.json'), read(control / 'receipt.json')
    assert gate['status'] == 'CONTROLS_PASS' and receipt['exit_code'] == 0
    assert receipt['cpu_seconds'] <= 600
    assert receipt['task_sha256'] == sha((control / 'task.json').read_bytes())
    assert receipt['result_sha256'] == sha((control / 'result.json').read_bytes())
    result = {}
    cpu_total = 0
    for task in manifest['jobs']:
        d = run / 'tasks' / task['id']
        t, r, q = read(d / 'task.json'), read(d / 'result.json'), read(d / 'receipt.json')
        assert t == task and r['status'] == 'COMPLETE' and q['exit_code'] == 0
        assert q['task_sha256'] == sha((d / 'task.json').read_bytes())
        assert q['result_sha256'] == sha((d / 'result.json').read_bytes())
        assert task['worker_cpu_seconds']-2.05 <= q['cpu_seconds'] <= task['worker_cpu_seconds']
        for item in [r['best']] + list(r['observations']['archive'].values()) + r['final_population']:
            _, scores = checked(item['graph6'], 'lambda')
            assert scores == item['scores']
        assert all(0 <= p['cpu'] <= task['worker_cpu_seconds'] for p in r['curves'])
        assert all(a['cpu'] <= b['cpu'] and key(a['scores'],task['target']) >= key(b['scores'],task['target']) for a,b in zip(r['curves'],r['curves'][1:]))
        cpu_total += q['cpu_seconds']
        result[task['id']] = r
    groups = []
    for target in TARGETS:
        for variant, comparator in (('CYCLE','A0'),('CYCLE_QUOTA','A0'),('CYCLE_QUOTA','CYCLE')):
            pairs = [(result[f'{comparator}--lambda-{target}-{i:02d}'],result[f'{variant}--lambda-{target}-{i:02d}']) for i in range(9)]
            wins = sum(key(b['best']['scores'],target) < key(a['best']['scores'],target) for a,b in pairs)
            losses = sum(key(b['best']['scores'],target) > key(a['best']['scores'],target) for a,b in pairs)
            groups.append({'target':target,'variant':variant,'comparator':comparator,'wins':wins,'ties':9-wins-losses,'losses':losses,
                           'pairs':[{'control':a['best']['scores'],'strategy':b['best']['scores'],
                                     'control_observed_W':a['observations']['archive']['W']['scores'],
                                     'strategy_observed_W':b['observations']['archive']['W']['scores']} for a,b in pairs]})
    report = {'status':'LAMBDA_SCREEN_VERIFIED','actual_worker_cpu_hours':cpu_total/3600,'controls_cpu_seconds':receipt['cpu_seconds'],'groups':groups,
              'decision':'Apply preregistered report rules; no automatic main campaign','main_campaign_authorized':False}
    atomic(run / 'evaluation.json', report)
    print(json.dumps(report,indent=4))


def controller(run):
    verify(run)
    host = snapshot(run)
    if not host['may_launch']:
        raise RuntimeError(json.dumps(host))
    if len(os.sched_getaffinity(0)) < 18:
        raise RuntimeError('Expected calibrated Ryzen affinity')
    runtime.HERE = HERE
    pool = SuccessPool(run)
    manifest = read(run / 'manifest.json')
    try:
        gate = pool.run([manifest['controls']],1,'controls')
        if gate['results'][0]['status'] != 'CONTROLS_PASS':
            raise RuntimeError('Controls failed')
        pool.run(manifest['jobs'],18,'confirmation')
        evaluate(run)
    except Exception:
        pool.emergency_stop_owned()
        if (run / 'SOLUTION.json').exists():
            print('VERIFIED_SOLUTION; campaign stopped',flush=True)
        else:
            raise
    finally:
        atomic(run / ('controller_cpu_'+str(time.time_ns())+'.json'), {'cpu_seconds': controller_cpu(), 'scope': 'controller process including imports; Windows probe infrastructure separately'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','run','evaluate'))
    parser.add_argument('directory',type=Path)
    args = parser.parse_args()
    run = args.directory.resolve()
    if args.action == 'prepare':
        prepare(run)
    elif args.action == 'evaluate':
        verify(run)
        evaluate(run)
    else:
        verify(run)
        frozen = run / 'bundle' / RELATIVE / 'run.py'
        if Path(__file__).resolve() != frozen:
            os.execv(sys.executable,[sys.executable,str(frozen),'run',str(run)])
        controller(run)


if __name__ == '__main__':
    main()
