"""Enumerate every local proposal and test fixed-prefix historical F membership."""
import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from widths import save


def verify_model(rows, assigned, target, candidate, variables, model):
    # Direct arithmetic check of historical_core.encode(rows, target).
    # Independent labels and sums; no encoder helper or Geometry.verify calls.
    labels = [set(p) for p in itertools.combinations(range(14), 2) if p[1] - p[0] != 7]
    positive = {v for v in model if v > 0}
    def edge(u, v):
        if u == v:
            return 0
        if u in rows:
            bit = (rows[u] >> v) & 1
            if v in rows:
                assert bit == ((rows[v] >> u) & 1)
            return bit
        if v in rows:
            return (rows[v] >> u) & 1
        key = tuple(sorted((u, v)))
        assert key in variables, ('missing', key)
        return int(variables[key] in positive)
    assert all(edge(target, v) == ((candidate >> v) & 1) for v in range(84))
    for pair, literal in variables.items():
        if pair in assigned:
            assert int(literal in positive) == assigned[pair]
    special = labels[target] | {(a + 7) % 14 for a in labels[target]}
    for c in range(14):
        assert sum(edge(target, w) for w in range(84) if c in labels[w]) == (1 if c in special else 2)
    for u, row in rows.items():
        neighbors = [w for w in range(84) if row >> w & 1]
        for v in range(84):
            if v in rows or (v != target and not (row >> v & 1)):
                continue
            expected = 2 - ((row >> v) & 1) - len(labels[u] & labels[v])
            assert sum(edge(v, w) for w in neighbors) == expected
    return [[u, v] for (u, v), literal in variables.items() if literal in positive]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = args.repo / 'experiments/memetik/root8105_review_followup_1_0_1'
    prefix_dir = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    output = args.output or args.repo / 'docs/augmentation/root8105_frontier_20261006'
    sys.path.insert(0, str(source))
    import bootstrap
    import historical_core as core
    from kernel import Geo
    from row_sampler import RowProposal
    from pysat.solvers import Glucose4
    g, cg = Geo(), core.Geometry()
    for width_path in sorted(output.glob('*_widths.json')):
        widths = json.loads(width_path.read_text())
        if not widths['complete']:
            continue
        input_path = prefix_dir / (widths['prefix'] + '.json')
        assert hashlib.sha256(input_path.read_bytes()).hexdigest() == widths['input_sha256']
        data = json.loads(input_path.read_text())
        rows = {int(u): sum(1 << v for v in vs) for u, vs in data['rows'].items()}
        assigned = {(u, v): bit for u, v, bit in data['assignments']}
        path = output / (widths['prefix'] + '_F.json')
        if path.exists():
            result = json.loads(path.read_text())
            assert result['input_sha256'] == widths['input_sha256']
        else:
            result = {'prefix': widths['prefix'], 'input_sha256': widths['input_sha256'],
                      'definition': 'historical target projection F intersected with saved propagation assignments',
                      'complete': False, 'results': []}
        done = {r['target'] for r in result['results']}
        for width in widths['results']:
            target = width['target']
            if target in done:
                continue
            beginning = time.process_time()
            total = width['proposal_width']
            record = {'target': target, 'proposal_width': total, 'F_width': 0,
                      'accepted': [], 'rejected_ranks': [], 'status': 'EXACT_COMPUTATIONAL_ENUMERATION'}
            if total:
                proposal = RowProposal(g, rows, target, assigned)
                assert proposal.total == total
                cnf, variables = core.encode(cg, rows, target)
                _, free = core.projection(cg, rows, target, variables)
                fixed = [lit if assigned[p] else -lit for p, lit in variables.items() if p in assigned]
                with Glucose4(bootstrap_with=cnf.clauses) as solver:
                    for rank in range(total):
                        candidate = proposal.unrank(rank)
                        assumptions = fixed + [lit if candidate >> v & 1 else -lit for v, lit in free]
                        if solver.solve(assumptions=assumptions):
                            witness = verify_model(rows, assigned, target, candidate, variables, solver.get_model())
                            record['accepted'].append({'rank': rank, 'neighbors': [v for v in range(84) if candidate >> v & 1],
                                                       'witness_ones': witness})
                        else:
                            record['rejected_ranks'].append(rank)
                proposal.rec.cache_clear()
                record['F_width'] = len(record['accepted'])
                assert record['F_width'] + len(record['rejected_ranks']) == total
            record['cpu_s'] = time.process_time() - beginning
            result['results'].append(record)
            result['complete'] = len(result['results']) == 71
            save(path, result)
        print(json.dumps({'prefix': widths['prefix'], 'complete': result['complete'],
                          'proposal_sum': sum(r['proposal_width'] for r in result['results']),
                          'F_sum': sum(r['F_width'] for r in result['results']),
                          'zero_F_targets': sum(r['F_width'] == 0 for r in result['results'])}), flush=True)


if __name__ == '__main__':
    main()
