"""Replay only 17 recorded endpoints; no fresh walks and no campaign rerun."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from independent_check import check


def save(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    source = args.repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    prior = args.repo / 'docs/augmentation/root8105_tree_results_20261006'
    out = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((prior / 'manifest.json').read_text())
    for name, expected in manifest['fingerprint']['files'].items():
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('source fingerprint mismatch: ' + name)
    sys.path.insert(0, str(source))
    import bootstrap
    from kernel import Geo
    from matching import root_objects, edge_key
    from propagation import propagate
    from row_sampler import RowProposal
    records = [r for r in json.loads((prior / 'DEPTH13_PATHS.json').read_text())
               if r['spec']['cell'] == 3]
    assert len(records) == 17
    objects_cache = {}
    g = Geo()
    results = []
    begun = time.process_time()
    for number, item in enumerate(records, 1):
        start = time.process_time()
        spec, rec = item['spec'], item['record']
        rid = item['root_id']
        if rid not in objects_cache:
            objects_cache[rid] = root_objects(g, int(spec['row'], 16))
        objects = objects_cache[rid]
        assert objects['stabilizer_order'] == spec['stab']
        matching = objects['classes'][rec['matching_class']]['matching']
        assert objects['classes'][rec['matching_class']]['orbit_size'] == rec['matching_orbit_size']
        rows = {0: int(spec['row'], 16)}
        ns = [v for v in range(g.n) if rows[0] >> v & 1]
        mset = set(matching)
        assigned = {edge_key(u, v): int(edge_key(u, v) in mset)
                    for i, u in enumerate(ns) for v in ns[i + 1:]}
        order = [v for pair in matching for v in pair] + sorted(objects['special_border_paired'])
        assert len(rec['steps']) == 12 and [s['target'] for s in rec['steps']] == order
        for step in rec['steps']:
            prop = propagate(g, rows, assigned)
            assert prop['pass'], prop
            assigned = prop['assigned']
            proposal = RowProposal(g, rows, step['target'], assigned)
            assert proposal.total == step['proposal_width']
            row = proposal.unrank(step['rank'])
            proposal.rec.cache_clear()
            rows[step['target']] = row
            prop = propagate(g, rows, assigned)
            assert prop['pass'], prop
            assigned = prop['assigned']
        assert len(rows) == 13 and set(rows) == {0} | set(ns)
        data = {'m': 7, 'root_id': rid, 'job_id': item['job_id'], 'walk_index': rec['index'],
                'matching_class': rec['matching_class'], 'matching': matching,
                'labels': [list(p) for p in g.labels],
                'rows': {str(u): [v for v in range(g.n) if mask >> v & 1]
                         for u, mask in sorted(rows.items())},
                'assignments': [[u, v, bit] for (u, v), bit in sorted(assigned.items())],
                'recorded_steps': rec['steps'], 'source_commit': '05fee711592baebc469ab7461376be3ca89046d0',
                'run_id': manifest['run_id'], 'reconstruction_uses_original_sampler': True,
                'independent_checker_uses_search_modules': False}
        result = check(data)
        name = 'prefix_r%04d_w%03d.json' % (rid, rec['index'])
        data['independent_result'] = result
        save(out / name, data)
        brief = {'file': name, 'root_id': rid, 'walk_index': rec['index'],
                 'status': result['status'], 'cpu_s': time.process_time() - start,
                 'sha256': hashlib.sha256((out / name).read_bytes()).hexdigest(),
                 'counts': result['counts']}
        results.append(brief)
        save(out / 'RESULTS.json', {'complete': number == 17, 'results': results,
                                   'reconstruction_and_check_cpu_s': time.process_time() - begun,
                                   'new_walks': 0, 'frontier_rows_enumerated': 0})
        print(json.dumps({'completed': number, **brief}), flush=True)


if __name__ == '__main__':
    main()
