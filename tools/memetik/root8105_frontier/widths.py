"""Exact local proposal counts for the fixed 17 x 71 frontier, with checkpoints."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = args.repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    prefix_dir = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    output = args.output or args.repo / 'docs/augmentation/root8105_frontier_20261006'
    manifest = json.loads((args.repo / 'docs/augmentation/root8105_tree_results_20261006/manifest.json').read_text())
    for name, expected in manifest['fingerprint']['files'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == expected, name
    sys.path.insert(0, str(source))
    import bootstrap
    from kernel import Geo
    from row_sampler import RowProposal
    g = Geo()
    receipts = json.loads((prefix_dir / 'RESULTS.json').read_text())
    assert receipts['complete'] and len(receipts['results']) == 17
    for receipt in receipts['results']:
        input_path = prefix_dir / receipt['file']
        assert hashlib.sha256(input_path.read_bytes()).hexdigest() == receipt['sha256']
        data = json.loads(input_path.read_text())
        rows = {int(u): sum(1 << v for v in vs) for u, vs in data['rows'].items()}
        assigned = {(u, v): bit for u, v, bit in data['assignments']}
        name = input_path.stem
        path = output / (name + '_widths.json')
        if path.exists():
            result = json.loads(path.read_text())
            assert result['input_sha256'] == receipt['sha256']
        else:
            result = {'prefix': name, 'input_sha256': receipt['sha256'],
                      'root_id': data['root_id'], 'walk_index': data['walk_index'],
                      'model': 'original RowProposal with saved necessary propagation; no star witness edges',
                      'results': [], 'complete': False}
        done = {r['target'] for r in result['results']}
        for target in sorted(set(range(g.n)) - set(rows)):
            if target in done:
                continue
            beginning = time.process_time()
            proposal = RowProposal(g, rows, target, assigned)
            count = proposal.total
            cache = proposal.rec.cache_info()._asdict()
            proposal.rec.cache_clear()
            result['results'].append({'target': target, 'proposal_width': count,
                                      'cpu_s': time.process_time() - beginning, 'cache': cache})
            result['complete'] = len(result['results']) == 71
            save(path, result)
        values = [r['proposal_width'] for r in result['results']]
        print(json.dumps({'prefix': name, 'targets': len(values), 'min': min(values),
                          'max': max(values), 'sum': sum(values), 'zeros': values.count(0)}), flush=True)


if __name__ == '__main__':
    main()
