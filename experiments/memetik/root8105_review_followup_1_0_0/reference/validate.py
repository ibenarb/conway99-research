"""Independent mathematical controls. Finite test cases, no time cutoffs."""
import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
from pysat.solvers import Glucose4

import historical_core as core
from filters import check, label_forbidden
from kernel import Geo, VertexSampler, count, load_roots, overflow_bound, width
from runtime import BASE, atomic


def enumerate_sat(g, rows, t):
    cg = core.Geometry(g.m)
    cnf, variables = core.encode(cg, rows, t)
    fixed, free = core.projection(cg, rows, t, variables)
    result = set()
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        while solver.solve():
            positive = set(v for v in solver.get_model() if v > 0)
            row = fixed | sum(1 << v for v, literal in free if literal in positive)
            if row in result:
                raise AssertionError('duplicate projected row')
            result.add(row)
            solver.add_clause([-literal if literal in positive else literal for _, literal in free])
    return result


def random_root(g, rng):
    while True:
        labels = list(range(1, g.n))
        rng.shuffle(labels)
        degrees, row = [0] * g.b, 0
        for i in labels:
            a, b = g.labels[i]
            if degrees[a] < g.margins(0)[a] and degrees[b] < g.margins(0)[b]:
                degrees[a] += 1
                degrees[b] += 1
                row |= 1 << i
        if degrees == g.margins(0):
            return row


def verify_bvls():
    # Reconstruct full graph, independently check all codegrees, then test prefixes.
    raw = json.loads((BASE / 'fixtures/bvls.json').read_text())
    rows = {int(k): int(v, 16) for k, v in raw['rows_m11'].items()}
    g = Geo(11)
    g.verify(rows)
    a = np.zeros((243, 243), dtype=np.int64)
    for b in range(g.b):
        a[0, 1 + b] = a[1 + b, 0] = 1
        c = (b + 11) % 22
        a[1 + b, 1 + c] = 1
    for u, label in enumerate(g.labels):
        for b in label:
            a[1 + b, 23 + u] = a[23 + u, 1 + b] = 1
        for v in range(g.n):
            a[23 + u, 23 + v] = rows[u] >> v & 1
    assert np.array_equal(a, a.T) and np.all(a.sum(1) == 22) and not np.diag(a).any()
    assert np.array_equal(a @ a, 20 * np.eye(243, dtype=np.int64) - a + 2 * np.ones_like(a))
    rng = random.Random(8105)
    n = 0
    for depth in (1, 2, 5, 10, 20, 40, 80, 120, 150, 200, 219, 220):
        built = rng.sample(list(rows), depth)
        state = {u: rows[u] for u in built}
        assert check(g, state)['pass']
        banned = label_forbidden(g, state)
        assert all(not (rows[v] >> w & 1) for v, w in banned)
        n += 1
    return {'srg_243_verified_independently': True, 'prefixes_LD_CAP_pass': n,
            'forbidden_pairs_full': len(label_forbidden(g, rows)),
            'scope': 'positive witness controls, not free completion performance'}


def validate(quick=False):
    start = time.process_time()
    report = {'status': 'RUNNING', 'scope': 'local validation, not Ryzen calibration', 'checks': []}
    assert overflow_bound(Geo()) == 134744793483572 < 2 ** 63 - 1
    try:
        count(Geo(11), 1)
    except ValueError as exc:
        assert 'int64' in str(exc)
    else:
        raise AssertionError('m11 int64 guard missing')
    roots = load_roots()
    assert len(roots) == 8105
    assert sum(r['stab'] == 1 for r in roots) == 6722
    rng = random.Random(81052026)
    cases, bijections = 0, 0
    for m in (2, 3, 4, 5):
        g = Geo(m)
        for _ in range(1 if quick else 2):
            root = random_root(g, rng)
            for t in range(1, g.n):
                exact = enumerate_sat(g, {0: root}, t)
                value = width(g, root, t)
                assert value == len(exact), (m, t, value, len(exact))
                sampler = VertexSampler(g, root, t)
                assert sampler.total == value
                if value <= 300:
                    ranks = {sampler.unrank(i) for i in range(value)}
                    assert ranks == exact and len(ranks) == value
                    bijections += 1
                elif value:
                    for i in (0, value // 2, value - 1):
                        assert sampler.unrank(i) in exact
                cases += 1
    report['checks'].append({'SAT_DP_vertex_cases': cases, 'exhaustive_rank_bijections': bijections})
    print(json.dumps(report['checks'][-1]), flush=True)
    saved = {r['id']: r for r in map(json.loads, (BASE / 'fixtures/reviewer_widths128.jsonl').read_text().splitlines())}
    count_cases = 0
    for rid in ((1,) if quick else (1, 64, 8098)):
        root = roots[rid - 1]
        for t in (list(range(1, 84)) if not quick else [1, 7, 13, 42, 83]):
            value = width(Geo(), int(root['row'], 16), t)
            # Original reviewer file uses widths, not a production completion flag.
            reference = saved[rid].get('widths_t1_to_t83', saved[rid].get('w'))
            assert value == reference[t - 1], (rid, t, value, reference[t - 1])
            count_cases += 1
    report['checks'].append({'m7_reviewer_count_matches': count_cases})
    g = Geo()
    paired = []
    for rid in ((1,) if quick else (1, 64, 8098)):
        root = int(roots[rid - 1]['row'], 16)
        target = g.index[(0, 8)]
        sampler = VertexSampler(g, root, target)
        assert sampler.total == width(g, root, target)
        cg = core.Geometry()
        cnf, variables = core.encode(cg, {0: root}, target)
        _, free = core.projection(cg, {0: root}, target, variables)
        with Glucose4(bootstrap_with=cnf.clauses) as solver:
            for rank in sorted(set([0, sampler.total // 2, sampler.total - 1] +
                                  [rng.randrange(sampler.total) for _ in range(5)])):
                row = sampler.unrank(rank)
                assert solver.solve(assumptions=[lit if row >> v & 1 else -lit for v, lit in free])
                state = {0: root, target: row}
                cg.verify(state)
                paired.append({'root': rid, 'target': target, 'rank': rank,
                               'row': hex(row), 'parent': hex(root),
                               'LD': check(g, state, capacity=False),
                               'CAP': check(g, state, label_disjoint=False), 'LD_CAP': check(g, state)})
    report['checks'].append({'m7_independent_vertex_totals': 1 if quick else 3,
                             'm7_ranked_rows_historical_F_SAT': len(paired)})
    report['paired_filter_cases'] = paired
    cap_witnesses = 0
    for case in paired:
        failure = case['LD_CAP']
        if failure['reason'] == 'capacity':
            child = {0: int(case['parent'], 16), case['target']: int(case['row'], 16)}
            cnf, _ = core.encode(core.Geometry(), child, failure['row'])
            with Glucose4(bootstrap_with=cnf.clauses) as solver:
                assert not solver.solve()
            cap_witnesses += 1
    report['capacity_rejections_independent_SAT_UNSAT'] = cap_witnesses
    report['bvls'] = verify_bvls()
    # Deliberate algebraic negatives with verify bypassed isolate each filter predicate.
    class Shape:
        def __init__(self, base):
            self.__dict__.update(base.__dict__)
            self.margins = base.margins
        def verify(self, rows):
            pass
    small = Shape(Geo(3))
    pair = next((v, w) for v in range(1, small.n) for w in range(v + 1, small.n)
                if small.sets[v] & small.sets[w])
    v, w = pair
    invalid = {0: (1 << v) | (1 << w), v: (1 << 0) | (1 << w)}
    assert check(small, invalid, capacity=False)['reason'] == 'label_disjoint'
    assert not check(small, {v: 0 for v in range(small.n - 1)}, label_disjoint=False)['pass']
    report['filter_predicate_negatives'] = 2
    ids = {check(small, {}, ld, cap)['model'] for ld in (True, False) for cap in (True, False)}
    assert len(ids) == 4 and 'F-historical-core-1.0.1-depth1' not in ids
    report['filter_model_ids_distinct'] = sorted(ids)
    report['status'], report['cpu_s'] = 'PASS', time.process_time() - start
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    result = validate(args.quick)
    atomic(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'paired_filter_cases'}), flush=True)
