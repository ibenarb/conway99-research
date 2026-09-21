"""Reaudit supplied archives and enumerate the old lambda catalogue once."""
import bootstrap
from common import core, checked, sha, atomic, cpu
from search import key, Guard
import fast_moves
import json
from pathlib import Path
from collections import Counter
import argparse


def audit(folder):
    folder = Path(folder)
    hashes = json.loads((folder / 'export_manifest.json').read_text())
    assert all(sha((folder / name).read_bytes()) == digest for name, digest in hashes.items())
    fingerprint = json.loads((folder / 'fingerprint.json').read_text())
    assert all(sha((bootstrap.ROOT / name).read_bytes()) == digest for name, digest in fingerprint['files'].items())
    distinct, results = {}, []
    for path in sorted((folder / 'tasks').glob('*/task.json')):
        task = json.loads(path.read_text())
        if task.get('kind') != 'compare':
            continue
        result = json.loads(path.with_name('result.json').read_text())
        receipt = json.loads(path.with_name('receipt.json').read_text())
        assert receipt['task_sha256'] == sha(path.read_bytes())
        assert receipt['result_sha256'] == sha(path.with_name('result.json').read_bytes())
        assert receipt['exit_code'] == 0 and result['status'] == 'COMPLETE'
        assert task['worker_cpu_seconds'] - 2.05 <= receipt['cpu_seconds'] <= task['worker_cpu_seconds']
        curve = result['curves']
        assert all(0 <= x['cpu'] <= task['worker_cpu_seconds'] for x in curve)
        assert all(a['cpu'] <= b['cpu'] and key(a['scores'], task['target']) >= key(b['scores'], task['target']) for a, b in zip(curve, curve[1:]))
        assert curve[-1]['scores'] == result['best']['scores']
        assert curve[0]['scores'] == min(task['founders'], key=lambda f: key(f['scores'], task['target']))['scores']
        for item in task['founders'] + [result['best']]:
            tag = (item['graph6'], task['arm'])
            if tag not in distinct:
                rows, scores = checked(*tag)
                assert scores == item['scores']
                assert core.canonical(rows) == item['class']
                distinct[tag] = scores
        results.append((task, result, receipt))
    lambdas = [(t, r) for t, r, _ in results if t['arm'] == 'lambda']
    return {'manifest_files': len(hashes), 'jobs': len(results), 'graphs': len(distinct),
            'cpu_hours': sum(r['cpu_seconds'] for _, _, r in results) / 3600,
            'lambda_final_families': dict(Counter('|'.join(r['families']) for t, r in lambdas)),
            'lambda_by_target': {target: {'families': dict(Counter('|'.join(r['families']) for t, r in lambdas if t['target'] == target)),
                                       'episodes': [r['episodes'] for t, r in lambdas if t['target'] == target]}
                                 for target in ('W', 'L1', 'F', 'Linf')}}


def census(item, seconds=60):
    rows, scores = checked(item['graph6'], 'lambda')
    guard = Guard(cpu() + seconds)
    out = {'line': item['line'], 'scores': scores, 'families': {}}
    metrics = core.metrics(rows)
    assert sum(int(r)*n for r, n in metrics['residual_histogram'].items()) == 0
    assert scores['F'] == 4 * metrics['C4'] - 8316
    out['residual_histogram'] = metrics['residual_histogram']
    out['C4'] = metrics['C4']
    for family in ('apex', 'rotation'):
        count, deltas, best = 0, Counter(), dict.fromkeys(('W', 'L1', 'F', 'Linf'), 0)
        begin = cpu()
        complete = False
        try:
            for move in getattr(fast_moves, family + '_moves')(rows, None, guard):
                child = core.apply_move(rows, move)
                cs = core.metrics(child)
                core.validate(child, 'lambda')
                count += 1
                deltas[(cs['W']-scores['W'], cs['L1']-scores['L1'], cs['F']-scores['F'])] += 1
                for target in best:
                    best[target] += int(key(cs, target) < key(scores, target))
            complete = True
        except core.BudgetEnd:
            pass
        out['families'][family] = {'complete': complete, 'moves': count, 'improvements': best,
                                   'delta_histogram': [{'delta': list(d), 'count': n} for d, n in sorted(deltas.items())],
                                   'cpu_seconds': cpu()-begin}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('comparison', type=Path)
    parser.add_argument('acceleration', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    report = {'comparison': audit(args.comparison), 'acceleration': audit(args.acceleration)}
    split = json.loads((args.comparison / 'founder_split.json').read_text())
    founders = split['confirmation']['lambda']
    cases = [next(f for f in founders if f['family'] == family) for family in ('HoG', 'Z33_lift', 'triangle_packing')]
    cases += [json.loads((args.comparison / 'tasks' / name / 'result.json').read_text())['best'] for name in ('lambda-W-00-A1', 'lambda-Linf-00-A0')]
    report['census'] = [census(item) for item in cases]
    atomic(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k != 'census'}, indent=2))
    for c in report['census']:
        print(c['line'], c['scores'], {k: {a:b for a,b in v.items() if a != 'delta_histogram'} for k,v in c['families'].items()})


if __name__ == '__main__':
    main()
