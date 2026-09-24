"""Copy verified V3 checkpoints; fresh paired frontier banks. Never mutate source."""
import boot
from util import *
import copy
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
                or sha(p['graph6'].encode()) != p['state']):
            raise RuntimeError('Invalid founder')


def specifications():
    jobs = []
    for i, w in enumerate((2102, 2107, 2108)):
        for rep in range(2):
            jobs.append({'id': f'V2-W{w}-{rep}', 'group': 'V2', 'variant': 'P',
                         'target': 'W', 'replicate': rep, 'seed': 2026092600 + 2 * i + rep,
                         'frontier_W': w, 'cumulative_budget_seconds': 7200,
                         'additional_cpu_seconds': 7200})
    for jid in sorted(read(boot.HERE / 'SOURCE_RUN.json')['jobs']):
        jobs.append({'id': jid, 'group': 'V3', 'variant': 'P', 'target': 'W',
                     'cumulative_budget_seconds': 28800, 'additional_cpu_seconds': 21600})
    return jobs


def source_verify(source):
    expected = read(boot.HERE / 'SOURCE_RUN.json')
    if file_sha(source / 'FINGERPRINT.json') != expected['fingerprint_sha256']:
        raise RuntimeError('Wrong source campaign')
    signature = read(source / 'FINGERPRINT.json')
    if signature['environment'] != env():
        raise RuntimeError('Source Python/pynauty environment changed')
    for name, digest in signature['files'].items():
        if file_sha(source / name) != digest:
            raise RuntimeError('Source input changed: ' + name)
    if not (source / 'COMPLETE.json').exists() or any(source.glob('runs/*/tasks/*/active.json')):
        raise RuntimeError('Source not safely completed')
    for jid, hashes in expected['jobs'].items():
        d = source / 'runs/records/tasks' / jid
        for name, digest in hashes.items():
            if file_sha(d / name) != digest:
                raise RuntimeError('Source changed: ' + jid + '/' + name)
        receipt = receipt_valid(d)
        if receipt['status'] != 'COMPLETE' or read(d / 'result.json')['endpoint_cpu_seconds'] != 7200:
            raise RuntimeError('Invalid source endpoint')
        sqlite_frozen(d / 'archive.sqlite')
    return expected


def prepare(source, run):
    info = package_verify()
    source = source or Path.home() / 'conway99_workspace/ryzen_lambda_prechecks_100_20260924'
    expected = source_verify(source)
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
            part = 'comparison' if spec['group'] == 'V2' else 'records'
            d = run / 'runs' / part / 'tasks' / spec['id']
            d.parent.mkdir(parents=True, exist_ok=True)
            if spec['group'] == 'V3':
                src = source / 'runs/records/tasks' / spec['id']
                shutil.copytree(src, d)
                for name, digest in expected['jobs'][spec['id']].items():
                    if file_sha(d / name) != digest:
                        raise RuntimeError('Copy mismatch')
                baseline = run / 'baseline' / spec['id']
                baseline.mkdir(parents=True)
                for name in ('task.json', 'result.json', 'receipt.json', 'checkpoint.json'):
                    shutil.copyfile(d / name, baseline / name)
                initial_cpu = receipt_valid(d)['cpu_seconds']
            else:
                d.mkdir()
                cfg = read(boot.FROZEN / 'config.json')
                cfg['milestones_cpu_seconds'] = [600, 1800, 3600, 7200]
                task = {**spec, 'kind': 'compare', 'arm': 'lambda', 'worker_cpu_seconds': 7200,
                        'founders': banks[str(spec['frontier_W'])]['population'], 'config': cfg}
                atomic(d / 'task.json', task)
                initial_cpu = 0
            jobs.append({**spec, 'directory': str(d.relative_to(run)), 'initial_actual_cpu': initial_cpu,
                         'task_sha256': file_sha(d / 'task.json')})
        for part, budget in [('comparison', 7200), ('records', 28800)]:
            atomic(run / 'runs' / part / 'budget.json', {'per_job_cpu_seconds': budget})
        plan = {'version': 'lambda-decision-1.0.0', 'workers': 14, 'jobs': jobs,
                'queue': [j['id'] for j in jobs], 'search_additional_cpu_seconds': 216000,
                'authorized_search_cpu_hours': 60, 'maximum_aux_cpu_hours': 2,
                'automatic_extension': False, 'criteria': {'V2': 'any W < 2102', 'V3': 'any W < 2150'},
                'interpretation': 'Budget decision, not basin exhaustion or proof of algorithm superiority'}
        atomic(run / 'plan.json', plan)
        (run / 'diagnostics').mkdir()
        immutable = {str(p.relative_to(run)): file_sha(p) for root in (run / 'program', run / 'baseline')
                     if root.exists() for p in root.rglob('*') if p.is_file()}
        for p in [run / 'plan.json', *run.glob('runs/*/budget.json'), *run.glob('runs/*/tasks/*/task.json')]:
            immutable[str(p.relative_to(run))] = file_sha(p)
        atomic(run / 'FINGERPRINT.json', {'files': immutable, 'environment': env()})
        atomic(run / 'PREPARED.json', {'status': 'PREPARED_NOT_STARTED', 'jobs': 14})
    finally:
        ledger.charge_infrastructure(own_cpu(), 'prepare')
    print(json.dumps({'status': 'PREPARED_NOT_STARTED', 'run': str(run), 'jobs': 14,
                      'additional_search_cpu_hours': 60, 'maximum_aux_cpu_hours': 2}), flush=True)


def verify(run):
    signature = read(run / 'FINGERPRINT.json')
    if signature['environment'] != env():
        raise RuntimeError('Environment changed')
    for name, digest in signature['files'].items():
        if file_sha(run / name) != digest:
            raise RuntimeError('Frozen input changed: ' + name)
    plan = read(run / 'plan.json')
    expected = specifications()
    if (len(plan['jobs']) != 14 or plan['workers'] != 14
            or sum(j['additional_cpu_seconds'] for j in plan['jobs']) != 216000
            or plan['queue'] != [j['id'] for j in expected]):
        raise RuntimeError('Invalid campaign')
    for job, spec in zip(plan['jobs'], expected):
        if any(job[k] != v for k, v in spec.items()):
            raise RuntimeError('Changed job specification')
        if file_sha(run / job['directory'] / 'task.json') != job['task_sha256']:
            raise RuntimeError('Changed task')
    return plan
