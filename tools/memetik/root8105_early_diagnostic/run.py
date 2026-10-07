"""Preregistered stored-path calibration, no new walks and no time abort."""
import argparse
import gzip
import hashlib
import json
import resource
import sys
import time
from pathlib import Path


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def compact(value):
    return {"root_id": value["root_id"], "cpu_s": value["cpu_s"],
            "states": [{k: state[k] for k in ("depth", "weight", "Q")} for state in value["states"]]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--count', type=int, choices=(4, 40), default=4)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    prior = output / "FINAL_RECEIPT.json"
    if prior.exists():
        receipt = json.loads(prior.read_text())
        for name, digest in receipt["files"].items():
            assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest
    source = repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    manifest = json.loads((repo / 'docs/augmentation/root8105_tree_results_20261006/manifest.json').read_text())
    for name, digest in manifest['fingerprint']['files'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    sys.path[:0] = [str(source), str(repo / 'tools/memetik/root8105_model_gap'), str(repo / 'tools/memetik/root8105_frontier')]
    import bootstrap
    from kernel import Geo
    from matching import root_objects
    from propagation import propagate
    from row_sampler import RowProposal
    from check_gap import direct_check, ld_edges, geometry
    from certify_dead import encode
    from rup_check import verify
    from pysat.solvers import Glucose4
    from pysat.formula import Formula, IDPool
    selection = repo / 'docs/augmentation/root8105_early_diagnostic_20261006/SELECTED_PATHS.json.gz'
    groups = json.loads(gzip.decompress(selection.read_bytes()))
    g = Geo()
    summaries = []
    begun = time.process_time()
    for group in groups:
        spec = group['spec']
        rid = spec['root_id']
        objects = None
        for record in group['records'][:args.count]:
            name = 'r%04d_w%03d' % (rid, record['index'])
            result_path = output / (name + '.json')
            if result_path.exists():
                value = json.loads(result_path.read_text())
                assert value['complete']
                summaries.append(compact(value))
                continue
            start = time.process_time()
            if objects is None:
                objects = root_objects(g, int(spec['row'], 16))
                assert objects['stabilizer_order'] == spec['stab']
            matching = objects['classes'][record['matching_class']]['matching']
            mset = set(matching)
            rows = {0: int(spec['row'], 16)}
            ns = [v for v in range(g.n) if rows[0] >> v & 1]
            m = {(u, v): int((u, v) in mset) for i, u in enumerate(ns) for v in ns[i + 1:]}
            assigned = dict(m)
            states = []
            for step in record['steps'][:2]:
                prop = propagate(g, rows, assigned)
                assert prop['pass']
                assigned = prop['assigned']
                proposal = RowProposal(g, rows, step['target'], assigned)
                assert proposal.total == step['proposal_width']
                rows[step['target']] = proposal.unrank(step['rank'])
                proposal.rec.cache_clear()
                prop = propagate(g, rows, assigned)
                assert prop['pass']
                assigned = prop['assigned']
                data = {'labels': [list(p) for p in g.labels],
                        'rows': {str(u): [v for v in range(84) if mask >> v & 1] for u, mask in rows.items()},
                        'assignments': [], 'matching': matching}
                labels, sets = geometry(data)
                zeros = ld_edges(labels, sets)
                results = {'R': [], 'R_LD': []}
                for target in sorted(set(range(84)) - set(rows)):
                    Formula.attach_vpool(IDPool())
                    cnf, _ = encode(data, target)
                    for (u, v), bit in m.items():
                        if target in (u, v):
                            w = v if u == target else u
                            cnf.append([w + 1 if bit else -(w + 1)])
                    previous = None
                    for mode in ('R', 'R_LD'):
                        if results[mode] and results[mode][-1]['status'] == 'RUP_VERIFIED_UNSAT':
                            continue
                        if mode == 'R_LD':
                            for u, v in zeros:
                                if target in (u, v):
                                    cnf.append([-((v if u == target else u) + 1)])
                        selected = None
                        if mode == 'R_LD' and previous is not None and not previous['check']['LD_violations']:
                            selected = previous['neighbors']
                        else:
                            with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
                                sat = solver.solve()
                                if sat:
                                    model = set(solver.get_model())
                                    selected = [v for v in range(84) if v + 1 in model]
                                else:
                                    proof = solver.get_proof()
                        if selected is not None:
                            check = direct_check(data, target, selected, mode)
                            for (u, v), bit in m.items():
                                if target in (u, v):
                                    assert int((v if u == target else u) in selected) == bit
                            result = {'target': target, 'status': 'SAT_DIRECT_VERIFIED', 'neighbors': selected, 'check': check}
                        else:
                            stem = name + '_d%d_t%d_%s' % (len(rows), target, mode)
                            cp, pp = output / (stem + '.cnf'), output / (stem + '.rup')
                            cnf.to_file(str(cp))
                            pp.write_text('\n'.join(proof or []) + '\n0\n')
                            check = verify(cp, pp)
                            result = {'target': target, 'status': check['status'], 'check': check, 'cnf': cp.name, 'proof': pp.name}
                        results[mode].append(result)
                        previous = result if selected is not None else None
                states.append({'depth': len(rows), 'weight': record['weights'][len(rows) - 1], 'input': data,
                               'results': results, 'Q': {mode: all(x['status'] == 'SAT_DIRECT_VERIFIED' for x in items)
                                                        for mode, items in results.items()}})
            value = {'complete': True, 'root_id': rid, 'index': record['index'], 'population': group['population'],
                     'states': states, 'cpu_s': time.process_time() - start}
            assert len(states) == 2
            save(result_path, value)
            summaries.append(compact(value))
        print(json.dumps({'root': rid, 'paths_done': len(summaries), 'cpu_s': time.process_time() - begun,
                          'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}), flush=True)
    summary = {'complete': True, 'paths': len(summaries), 'per_root': args.count,
               'preregistered_commit': 'cff611b49f33dda61e54174b3430b9db9401a3b4',
               'selection_sha256': hashlib.sha256(selection.read_bytes()).hexdigest(),
               'invocation_cpu_s': time.process_time() - begun,
               'path_cpu_s': sum(x['cpu_s'] for x in summaries),
               'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'statistics': {}}
    for mode in ('R', 'R_LD'):
        for depth in (2, 3):
            weighted, raw, alive = [], [], []
            for value in summaries:
                s = value['states'][depth - 2]
                j = all(x['Q'][mode] for x in value['states'][:depth - 1])
                raw.append(s['weight'])
                weighted.append(s['weight'] * j)
                alive.append(j)
            summary['statistics'][mode + '_d' + str(depth)] = {
                'surviving_sample_paths': sum(alive), 'sample_paths': len(alive),
                'mean_nodes_equal_root_weight': sum(weighted) / len(weighted),
                'unpruned_mean_nodes_same_sample': sum(raw) / len(raw),
                'weighted_survival_ratio': sum(weighted) / sum(raw),
                'weight_ESS': sum(raw) ** 2 / sum(w*w for w in raw),
                'max_weight_fraction': max(raw) / sum(raw)}
    summary['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.name != 'FINAL_RECEIPT.json'}
    save(output / 'FINAL_RECEIPT.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    main()
