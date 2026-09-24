"""Prepare new independent tasks only; never resume or modify an earlier run."""
import boot
from util import *
import copy
import shutil

ORIGINS = ('gen-lambda-11', 'gen-lambda-13', 'gen-lambda-03', 'claude_v01_c')


def package_verify():
    info = read(boot.HERE / 'PACKAGE.json')
    for name, digest in info['files'].items():
        if file_sha(boot.ROOT / name) != digest:
            raise RuntimeError('Package mismatch: ' + name)
    return info


def validate_founders(items):
    if len(items) != 16 or len({p['class'] for p in items}) != 16:
        raise RuntimeError('Need sixteen different isomorphism classes')
    for p in items:
        rows, scores = checked(p['graph6'], 'lambda')
        if (scores != p['scores'] or core.canonical(rows) != p['class']
                or sha(p['graph6'].encode()) != p['state']):
            raise RuntimeError('Invalid founder')


def specifications():
    jobs = []
    for i in range(8):
        for variant in ('P', 'PCesc'):
            jobs.append({'id': f'V1-{i:02d}-{variant}', 'group': 'V1', 'variant': variant,
                         'target': 'W', 'replicate': i, 'seed': 2026092400 + i,
                         'cumulative_budget_seconds': 3600, 'additional_cpu_seconds': 3600})
    for i, origin in enumerate(ORIGINS):
        for rep in range(2):
            jobs.append({'id': f'V3-{origin}-{rep}', 'group': 'V3', 'variant': 'P',
                         'target': 'W', 'origin': origin, 'replicate': rep,
                         'seed': 2026092500 + 2 * i + rep,
                         'cumulative_budget_seconds': 7200, 'additional_cpu_seconds': 7200})
    return jobs


def prepare(source, run):
    info = package_verify()
    if run.exists():
        raise FileExistsError('New run directory required')
    # Source argument is retained for CLI compatibility, but no earlier run is read.
    run.mkdir(parents=True)
    ledger = AuxiliaryLedger(run)
    try:
        founders = read(boot.FROZEN / 'founders.json')
        validate_founders(founders)
        banks = read(boot.HERE / 'ISOLATED_BANKS.json')
        for origin in ORIGINS:
            bank = banks[origin]
            validate_founders(bank['population'])
            if any(p['family'] == 'HoG' or p['line'] != origin for p in bank['population']):
                raise RuntimeError('Mixed isolated provenance')
        files = list(info['files']) + [str((boot.HERE / 'PACKAGE.json').relative_to(boot.ROOT))]
        for name in files:
            dest = run / 'program' / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(boot.ROOT / name, dest)
        config = read(boot.FROZEN / 'config.json')
        jobs = []
        for spec in specifications():
            part = 'comparison' if spec['group'] == 'V1' else 'records'
            d = run / 'runs' / part / 'tasks' / spec['id']
            d.mkdir(parents=True)
            cfg = copy.deepcopy(config)
            cfg['version'] = 'lambda-prechecks-1.0.0'
            cfg['milestones_cpu_seconds'] = [600, 1800, 3600] + ([7200] if part == 'records' else [])
            task = {**spec, 'kind': 'compare' if part == 'comparison' else 'isolated',
                    'arm': 'lambda', 'worker_cpu_seconds': spec['cumulative_budget_seconds'],
                    'founders': founders if part == 'comparison' else banks[spec['origin']]['population'],
                    'config': cfg}
            atomic(d / 'task.json', task)
            jobs.append({**spec, 'directory': str(d.relative_to(run)), 'initial_actual_cpu': 0,
                         'task_sha256': file_sha(d / 'task.json')})
        for part, budget in [('comparison', 3600), ('records', 7200)]:
            atomic(run / 'runs' / part / 'budget.json', {'per_job_cpu_seconds': budget})
        # V1 gets an entire contemporaneous 16-worker wave; V3 then eight workers.
        plan = {'version': 'lambda-prechecks-1.0.0', 'authorized_cpu_hours': 34,
                'workers': 16, 'jobs': jobs, 'queue': [j['id'] for j in jobs],
                'search_additional_cpu_seconds': 32 * 3600, 'auxiliary_limits': AUX_LIMITS,
                'automatic_extension': False, 'waves': ['V1', 'V3'],
                'v1_primary': 'paired endpoint differences in (W,L1) at 3600 CPU seconds',
                'v1_decision': 'exploratory screen; no automatic acceptance/rejection',
                'v3_decision': 'report both repetitions and trajectories; W<2200 is a positive signal only',
                'bank_construction': 'fixed verified AP-walk populations; preparation cost separately recorded'}
        atomic(run / 'plan.json', plan)
        (run / 'diagnostics').mkdir()
        immutable = {str(p.relative_to(run)): file_sha(p) for p in (run / 'program').rglob('*') if p.is_file()}
        immutable['plan.json'] = file_sha(run / 'plan.json')
        for p in (run / 'runs').rglob('*.json'):
            immutable[str(p.relative_to(run))] = file_sha(p)
        atomic(run / 'FINGERPRINT.json', {'files': immutable, 'environment': env()})
        atomic(run / 'PREPARED.json', {'status': 'PREPARED_NOT_STARTED', 'jobs': 24})
    finally:
        ledger.charge_infrastructure(own_cpu(), 'prepare')
    print(json.dumps({'status': 'PREPARED_NOT_STARTED', 'run': str(run), 'jobs': 24, 'cpu_hours': 34}), flush=True)


def verify(run):
    signature = read(run / 'FINGERPRINT.json')
    if signature['environment'] != env():
        raise RuntimeError('Environment changed')
    for name, digest in signature['files'].items():
        if file_sha(run / name) != digest:
            raise RuntimeError('Frozen input changed: ' + name)
    plan = read(run / 'plan.json')
    expected = specifications()
    if (len(plan['jobs']) != 24 or plan['workers'] != 16
            or sum(j['additional_cpu_seconds'] for j in plan['jobs']) != 32 * 3600
            or plan['queue'] != [j['id'] for j in expected]):
        raise RuntimeError('Invalid plan')
    for job, spec in zip(plan['jobs'], expected):
        if any(job[k] != v for k, v in spec.items()):
            raise RuntimeError('Changed job specification')
        if file_sha(run / job['directory'] / 'task.json') != job['task_sha256']:
            raise RuntimeError('Changed task')
    return plan
