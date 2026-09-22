"""Cross-check source pins, proposal consistency and deliverable hashes."""
from pathlib import Path
import hashlib
import json
import subprocess
from analyse import check, key, load, sha

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/memetik/lambda_plan_codex_20260922'
CODE = ROOT / 'experiments/memetik/lambda_plan_codex_20260922'
PIN = 'b659cb8743dd6036d91dafb466b2d12cb21a29b0'


def main():
    files = []
    parent = ROOT / 'experiments/memetik'
    for directory in ('ryzen_compare_0_4_0', 'move_accel_0_1_0',
                      'lambda_strategy_0_1_0', 'lambda_review_20260921',
                      'lambda_compare_0_2_0'):
        files.extend((parent / directory).glob('*.py'))
    files += [parent / 'lambda_compare_0_2_0' / n for n in ('founders.json', 'config.json')]
    files.append(parent / 'lambda_strategy_0_1_0/source_hashes.json')
    files += [ROOT / n for n in ('src/memetic_v2/core.py', 'src/memetic_v2/verify.py',
              'experiments/memetik/escape_0_2/operators.py',
              'docs/memetik/lambda_review_20260921/CHECK.json')]
    sources = {}
    for path in sorted(set(files)):
        relative = str(path.relative_to(ROOT))
        original = subprocess.check_output(['git', 'show', PIN + ':' + relative], cwd=ROOT)
        assert path.read_bytes() == original, relative
        sources[relative] = sha(original)
    assert len(sources) == 46
    source_report = {'status': 'SOURCE_COMMIT_EQUALITY_PASS', 'commit': PIN,
                     'files_checked': len(sources), 'sha256': sources,
                     'scope': 'local Git source equality; not the original Ryzen bundle fingerprint'}
    (OUT / 'SOURCE_CHECK.json').write_text(json.dumps(source_report, indent=2) + '\n')
    manifest = load(OUT / 'PROPOSED_MANIFEST.json')
    old = load(ROOT / 'docs/memetik/lambda_results_20260922/RECEIPTS.json')
    founders = load(parent / 'lambda_compare_0_2_0/founders.json')
    assert manifest['authorized_to_launch'] is False
    assert manifest['automatic_extension'] is False
    assert manifest['workers_max_global'] == 18
    a, r = manifest['continuation_jobs'], manifest['record_jobs']
    assert {j['id'] for j in a} == {f'{v}--lambda-W-{i:02d}' for v in ('P', 'TC') for i in range(12)}
    assert len(a) == 24 and len(r) == 12
    for job in a:
        assert job['old_receipt'] == old[job['id']]
        assert job['new_authorization_cpu_seconds'] == job['new_endpoint_budget_seconds'] - job['old_endpoint_budget_seconds'] == 10800
        assert job['no_migration']
    for target, start in manifest['record_starts'].items():
        assert check(start['graph6']) == start['scores']
        assert sha(start['graph6'].encode()) == start['state']
        assert len(start['retained_founder_states_in_original_order']) == 15
        assert set(start['retained_founder_states_in_original_order']) | {start['replace_original_founder_state']} == {f['state'] for f in founders}
        assert key(start['scores'], target) < min(key(f['scores'], target) for f in founders)
    assert sum(j['new_authorization_cpu_seconds'] for j in a) == 72 * 3600
    assert sum(j['worker_cpu_seconds'] for j in r) == 24 * 3600
    assert sum(d['jobs'] * d['cpu_seconds_each'] for d in manifest['diagnostic']) == 2 * 3600
    assert sum(manifest['budget_cpu_hours'][k] for k in ('diagnostic', 'continuation', 'record', 'infrastructure_and_host_probes')) == manifest['budget_cpu_hours']['total_ceiling'] == 100
    assert len({j['seed'] for j in r}) == len(r)
    assert not {j['seed'] for j in r} & {j['seed'] for j in a}
    # Deliberately invalid fixtures for the independent decoder/invariants.
    valid = manifest['record_starts']['W']['graph6']
    from analyse import decode, measure
    neighbors = decode(valid)
    u, v = 0, next(iter(neighbors[0]))
    neighbors[u].remove(v)
    neighbors[v].remove(u)
    try:
        measure(neighbors)
    except AssertionError:
        pass
    else:
        raise AssertionError('Missing edge was accepted')
    try:
        check(valid[:-1])
    except AssertionError:
        pass
    else:
        raise AssertionError('Truncated graph6 was accepted')
    # W must dominate L1, and Linf must dominate Nmax.
    assert key({'W': 2120, 'L1': 9999}, 'W') < key({'W': 2121, 'L1': 2440}, 'W')
    assert key({'Linf': 2, 'Nmax': 999, 'L1': 9999}, 'Linf') < key({'Linf': 3, 'Nmax': 1, 'L1': 10}, 'Linf')
    for path in CODE.glob('*.py'):
        assert '\t' not in path.read_text()
        compile(path.read_text(), str(path), 'exec')
    paths = sorted(p for folder in (OUT, CODE) for p in folder.iterdir()
                   if p.is_file() and p.name != 'DELIVERY_MANIFEST.json')
    delivery = {'status': 'DELIVERY_CROSSCHECK_PASS', 'authorized_to_launch': False,
                'source_file_count': len(sources), 'proposal_search_jobs': len(a) + len(r),
                'proposal_total_cpu_hours': 100,
                'negative_controls': ['removed edge rejected', 'truncated graph6 rejected'],
                'ordering_controls': ['W dominates L1', 'Linf dominates Nmax'],
                'files': {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size,
                                                   'sha256': sha(p.read_bytes())} for p in paths}}
    (OUT / 'DELIVERY_MANIFEST.json').write_text(json.dumps(delivery, indent=2) + '\n')
    print(json.dumps({k: v for k, v in delivery.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
