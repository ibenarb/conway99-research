"""Frozen 4-CPU-hour A0 engine comparison; no main campaign auto-launch."""
import argparse
import copy
import importlib.metadata
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid

import bootstrap
from common import ROOT, atomic, checked, core, sha
import runtime
from runtime import Pool, read, THREAD_ENV
from resources import snapshot
from search import key

HERE = Path(__file__).resolve().parent
RELATIVE = Path('experiments/memetik/move_accel_0_1_0')
TARGETS = ('W', 'L1', 'F', 'Linf')


def environment():
    return {'python': sys.version, 'packages': {p: importlib.metadata.version(p)
            for p in ('pynauty', 'ortools', 'numpy')}}


def audit_source(source):
    expected = read(source / 'fingerprint.json')
    if environment() != {k: expected[k] for k in ('python', 'packages')}:
        raise RuntimeError('Use the original memetik environment; runtime differs')
    for relative, digest in expected['files'].items():
        if sha((source / 'bundle' / relative).read_bytes()) != digest:
            raise RuntimeError('Original frozen code differs: '+relative)
    if read(source / 'evaluation.json')['status'] != 'PAIRED_COMPARISON_VERIFIED':
        raise RuntimeError('Source pilot is not complete and verified')
    if sha((source / 'confirmation.json').read_bytes()) != read(source / 'calibration_result.json')['confirmation_manifest_sha256']:
        raise RuntimeError('Source manifest hash mismatch')
    return expected


def prepare(source):
    source = source.resolve()
    expected = audit_source(source)
    workspace = Path.home() / 'conway99_workspace'
    host = snapshot(workspace)
    if not host['may_launch']:
        raise RuntimeError(json.dumps(host))
    split = read(source / 'founder_split.json')['confirmation']
    cases = []
    for arm, founders in split.items():
        seen = set()
        for f in founders:
            _, scores = checked(f['graph6'], arm)
            if scores != f['scores']:
                raise RuntimeError('Founder score mismatch')
            if f['family'] not in seen:
                cases.append(dict(id=f['line'], arm=arm, graph6=f['graph6']))
                seen.add(f['family'])
        for target in ('L1', 'Linf'):
            r = read(source / 'tasks' / f'{arm}-{target}-00-A0' / 'result.json')
            cases.append(dict(id=arm+'-endpoint-'+target, arm=arm, graph6=r['best']['graph6']))
    exemplar = read(source / 'tasks/omega-W-00-A0/task.json')
    config = exemplar['config']
    jobs = []
    for replicate in range(3):
        for arm in ('omega', 'lambda'):
            for target in TARGETS:
                engines = ('reference', 'fast') if (replicate+TARGETS.index(target)) % 2 == 0 else ('fast', 'reference')
                for engine in engines:
                    jobs.append({'id': f'{engine}--{arm}-{target}-{replicate:02d}',
                                 'kind': 'compare', 'arm': arm, 'target': target,
                                 'variant': 'A0', 'engine': engine, 'replicate': replicate,
                                 'seed': core.derive_seed(2026092101, ['engine', replicate]),
                                 'worker_cpu_seconds': 300, 'config': config, 'founders': split[arm]})
    assert len(jobs) == 48 and sum(t['worker_cpu_seconds'] for t in jobs) == 14400
    run = Path(tempfile.mkdtemp(prefix='ryzen_move_accel_010_', dir=workspace))
    paths = {}
    for relative, digest in expected['files'].items():
        dest = run / 'bundle' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = (source / 'bundle' / relative).read_bytes()
        dest.write_bytes(data)
        paths[relative] = sha(data)
    for p in HERE.glob('*.py'):
        relative = str(RELATIVE / p.name)
        dest = run / 'bundle' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())
        paths[relative] = sha(dest.read_bytes())
    manifest = {'version': 'move-accel-0.1.0', 'jobs': jobs, 'workers': 18,
                'comparison_cpu_seconds': 14400, 'controls_cpu_ceiling': 600,
                'controls': {'id': 'ordered-controls', 'kind': 'controls', 'cases': cases,
                             'worker_cpu_seconds': 600},
                'source_manifest_sha256': sha((source / 'confirmation.json').read_bytes()),
                'decision': 'Exploratory engineering comparison; no three-seed significance claim',
                'main_campaign_authorized': False}
    atomic(run / 'manifest.json', manifest)
    atomic(run / 'fingerprint.json', dict(environment(), files=paths,
                                         manifest_sha256=sha((run / 'manifest.json').read_bytes())))
    launch(run)


def verify_bundle(run):
    signature = read(run / 'fingerprint.json')
    if environment() != {k: signature[k] for k in ('python', 'packages')}:
        raise RuntimeError('Runtime changed')
    for relative, digest in signature['files'].items():
        if sha((run / 'bundle' / relative).read_bytes()) != digest:
            raise RuntimeError('Frozen file changed: '+relative)
    if sha((run / 'manifest.json').read_bytes()) != signature['manifest_sha256']:
        raise RuntimeError('Frozen manifest changed')


def evaluate(run):
    manifest = read(run / 'manifest.json')
    results = {}
    actual = 0.0
    if len(manifest['jobs']) != 48 or sum(t['worker_cpu_seconds'] for t in manifest['jobs']) != 14400:
        raise ValueError('Unexpected benchmark design')
    if read(run / 'tasks/ordered-controls/result.json')['status'] != 'ORDER_RNG_VALIDITY_PASS':
        raise ValueError('Missing successful differential gate')
    for task in manifest['jobs']:
        directory = run / 'tasks' / task['id']
        result, receipt = read(directory / 'result.json'), read(directory / 'receipt.json')
        assert read(directory / 'task.json') == task
        assert receipt['exit_code'] == 0 and result['status'] == 'COMPLETE'
        assert receipt['task_sha256'] == sha((directory / 'task.json').read_bytes())
        assert receipt['result_sha256'] == sha((directory / 'result.json').read_bytes())
        limit = task['worker_cpu_seconds']
        assert limit-2.05 <= receipt['cpu_seconds'] <= limit
        _, scores = checked(result['best']['graph6'], task['arm'])
        assert scores == result['best']['scores'] == result['curves'][-1]['scores']
        assert result['curves'][0]['cpu'] == 0
        assert result['curves'][0]['scores'] == min(task['founders'], key=lambda f: key(f['scores'], task['target']))['scores']
        assert all(0 <= p['cpu'] <= limit for p in result['curves'])
        assert all(a['cpu'] <= b['cpu'] and key(a['scores'], task['target']) >= key(b['scores'], task['target'])
                   for a, b in zip(result['curves'], result['curves'][1:]))
        results[task['id']] = result
        actual += receipt['cpu_seconds']
    groups = []
    for arm in ('omega', 'lambda'):
        for target in TARGETS:
            pairs = [(results[f'reference--{arm}-{target}-{i:02d}'], results[f'fast--{arm}-{target}-{i:02d}']) for i in range(3)]
            wins = sum(key(b['best']['scores'], target) < key(a['best']['scores'], target) for a, b in pairs)
            losses = sum(key(b['best']['scores'], target) > key(a['best']['scores'], target) for a, b in pairs)
            groups.append({'arm': arm, 'target': target, 'fast_wins': wins, 'ties': 3-wins-losses, 'fast_losses': losses,
                           'median_episode_ratio': statistics.median(b['episodes']/max(1, a['episodes']) for a, b in pairs),
                           'pairs': [{'reference': a['best']['scores'], 'fast': b['best']['scores'],
                                      'reference_episodes': a['episodes'], 'fast_episodes': b['episodes']} for a, b in pairs]})
    report = {'status': 'ENGINE_COMPARISON_VERIFIED', 'groups': groups,
              'actual_worker_cpu_hours': actual/3600, 'nominal_worker_cpu_hours': 4,
              'main_campaign_authorized': False,
              'caveat': 'Three paired seeds; engineering screen, not confirmed superiority'}
    atomic(run / 'evaluation.json', report)
    return report


def controller(run):
    verify_bundle(run)
    manifest = read(run / 'manifest.json')
    runtime.HERE = HERE  # Only this isolated experiment launches the wrapper.
    import progress
    original_render = progress.render
    progress.render = lambda e: original_render(e)+' ['+e['id'].split('--')[0]+']'
    pool = Pool(run)
    if (run / 'controller_error.json').exists():
        (run / 'controller_error.json').rename(run / ('controller_error_'+uuid.uuid4().hex+'.json'))
    try:
        control = pool.run([manifest['controls']], 1, 'controls')
        if control['results'][0]['status'] != 'ORDER_RNG_VALIDITY_PASS':
            raise RuntimeError('Differential controls failed')
        print('ORDER_RNG_VALIDITY_PASS; starting 48 paired engine jobs', flush=True)
        pool.run(manifest['jobs'], manifest['workers'], 'confirmation')
        print(json.dumps(evaluate(run), indent=2), flush=True)
    except Exception as error:
        pool.emergency_stop_owned()
        atomic(run / 'controller_error.json', {'error': str(error)})
        raise


def launch(run):
    verify_bundle(run)
    host = snapshot(run)
    if not host['may_launch']:
        raise RuntimeError(json.dumps(host))
    if len(os.sched_getaffinity(0)) < 18:
        raise RuntimeError('Need the calibrated Ryzen affinity')
    with (run / 'console.log').open('ab') as log:
        proc = subprocess.Popen([sys.executable, str(run / 'bundle' / RELATIVE / 'run.py'), 'controller', str(run)],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True, env={**os.environ, **THREAD_ENV})
    print(json.dumps({'status': 'LAUNCHED', 'directory': str(run), 'pid': proc.pid,
                      'workers': 18, 'comparison_worker_cpu_hours': 4,
                      'main_campaign_started': False}, indent=2))


def export(run):
    verify_bundle(run)
    evaluate(run)
    target = run / 'move_accel_verified.tar.gz'
    paths = [run / name for name in ('manifest.json', 'fingerprint.json', 'evaluation.json', 'status.json')]
    paths += list((run / 'tasks').glob('*/result.json'))+list((run / 'tasks').glob('*/receipt.json'))
    paths += list((run / 'tasks').glob('*/task.json'))
    hashes = {str(p.relative_to(run)): sha(p.read_bytes()) for p in paths}
    atomic(run / 'export_manifest.json', hashes)
    with target.open('xb') as raw:
        with tarfile.open(fileobj=raw, mode='w:gz') as archive:
            for p in paths+[run / 'export_manifest.json']:
                archive.add(p, arcname=str(p.relative_to(run)), recursive=False)
    with tarfile.open(target) as archive:
        for name, digest in hashes.items():
            assert sha(archive.extractfile(name).read()) == digest
    target.with_name(target.name+'.sha256').write_text(sha(target.read_bytes())+'  '+target.name+'\n')
    print(target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'controller', 'resume', 'status', 'export'))
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    run = args.directory.resolve()
    if args.action == 'prepare':
        prepare(run)
    elif args.action == 'controller':
        controller(run)
    elif args.action == 'resume':
        launch(run)
    elif args.action == 'export':
        export(run)
    else:
        print(json.dumps(read(run / ('evaluation.json' if (run / 'evaluation.json').exists() else 'status.json')), indent=2))
        if (run / 'controller_error.json').exists():
            print(json.dumps(read(run / 'controller_error.json'), indent=2))


if __name__ == '__main__':
    main()
