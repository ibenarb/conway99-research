"""Eight fresh seeds from two frozen 16-class frontier populations."""
import boot
from util import *
import shutil


def package_verify():
    info = read(boot.HERE / 'PACKAGE.json')
    for name, digest in info['files'].items():
        if file_sha(boot.ROOT / name) != digest:
            raise RuntimeError('Package mismatch: ' + name)
    return info


def validate_founders(items):
    if len(items) != 16 or len({p['class'] for p in items}) != 16:
        raise RuntimeError('Need sixteen distinct classes')
    for p in items:
        rows, scores = checked(p['graph6'], 'lambda')
        if (scores != p['scores'] or core.canonical(rows) != p['class']
                or sha(p['graph6'].encode()) != p['state'] or p['family'] != 'HoG'):
            raise RuntimeError('Invalid founder')


def specifications():
    return [{'id': f'F-W{w}-{rep}', 'group': f'F{w}', 'variant': 'P', 'target': 'W',
             'frontier_W': w, 'replicate': rep, 'seed': 2026092700 + 4 * i + rep,
             'cumulative_budget_seconds': 14400, 'additional_cpu_seconds': 14400}
            for i, w in enumerate((2096, 2101)) for rep in range(4)]


def prepare(source, run):
    info = package_verify()
    banks = read(boot.HERE / 'FRONTIER_BANKS.json')
    for w, bank in banks.items():
        validate_founders(bank['population'])
        if min(p['scores']['W'] for p in bank['population']) != int(w):
            raise RuntimeError('Wrong frontier bank')
    if run.exists():
        raise FileExistsError('New destination required')
    run.mkdir(parents=True)
    ledger = AuxiliaryLedger(run)
    try:
        files = list(info['files']) + [str((boot.HERE / 'PACKAGE.json').relative_to(boot.ROOT))]
        for name in files:
            dest = run / 'program' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(boot.ROOT / name, dest)
        jobs = []
        for spec in specifications():
            d = run / 'runs/comparison/tasks' / spec['id']
            d.mkdir(parents=True)
            cfg = read(boot.FROZEN / 'config.json')
            cfg['milestones_cpu_seconds'] = [3600, 7200, 14400]
            task = {**spec, 'kind': 'compare', 'arm': 'lambda', 'worker_cpu_seconds': 14400,
                    'founders': banks[str(spec['frontier_W'])]['population'], 'config': cfg}
            atomic(d / 'task.json', task)
            jobs.append({**spec, 'directory': str(d.relative_to(run)), 'initial_actual_cpu': 0,
                         'task_sha256': file_sha(d / 'task.json')})
        atomic(run / 'runs/comparison/budget.json', {'per_job_cpu_seconds': 14400})
        plan = {'version': 'lambda-frontier-1.0.0', 'workers': 8, 'jobs': jobs,
                'queue': [j['id'] for j in jobs], 'search_additional_cpu_seconds': 115200,
                'authorized_search_cpu_hours': 32, 'maximum_aux_cpu_hours': 1,
                'automatic_extension': False, 'primary_threshold': 2096,
                'decision_by_successful_jobs': {'0': 'PAUSE_W_FRONTIER', '1': 'SINGLE_SIGNAL_REVIEW_ONLY',
                                                '2_or_more': 'REPEATED_SIGNAL_REVIEW_ONLY'},
                'interpretation': 'Concrete populations, not independent basins or causal founder comparison.'}
        atomic(run / 'plan.json', plan)
        (run / 'diagnostics').mkdir()
        immutable = {str(p.relative_to(run)): file_sha(p) for p in (run / 'program').rglob('*') if p.is_file()}
        for p in [run / 'plan.json', run / 'runs/comparison/budget.json', *run.glob('runs/*/tasks/*/task.json')]:
            immutable[str(p.relative_to(run))] = file_sha(p)
        atomic(run / 'FINGERPRINT.json', {'files': immutable, 'environment': env()})
        atomic(run / 'PREPARED.json', {'status': 'PREPARED_NOT_STARTED', 'jobs': 8})
    finally:
        ledger.charge_infrastructure(own_cpu(), 'prepare')
    print(json.dumps({'status': 'PREPARED_NOT_STARTED', 'run': str(run), 'jobs': 8,
                      'additional_search_cpu_hours': 32, 'maximum_aux_cpu_hours': 1}), flush=True)


def verify(run):
    signature = read(run / 'FINGERPRINT.json')
    if signature['environment'] != env():
        raise RuntimeError('Environment changed')
    for name, digest in signature['files'].items():
        if file_sha(run / name) != digest:
            raise RuntimeError('Frozen input changed: ' + name)
    plan = read(run / 'plan.json')
    expected = specifications()
    if (len(plan['jobs']) != 8 or plan['workers'] != 8
            or sum(j['additional_cpu_seconds'] for j in plan['jobs']) != 115200
            or plan['queue'] != [j['id'] for j in expected]):
        raise RuntimeError('Invalid campaign')
    for job, spec in zip(plan['jobs'], expected):
        if any(job[k] != v for k, v in spec.items()):
            raise RuntimeError('Changed job specification')
        if file_sha(run / job['directory'] / 'task.json') != job['task_sha256']:
            raise RuntimeError('Changed task')
    return plan
