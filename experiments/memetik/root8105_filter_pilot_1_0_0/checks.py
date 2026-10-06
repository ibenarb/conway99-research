"""New pilot controls only: no repetition of the completed census/audit."""
import json
import math
from pathlib import Path
from plan import VARIANTS


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def check_payload(data, root):
    if root['kind'] == 'controls':
        if data['counts']:
            result = data['counts']['1']
            if result['status'] not in ('PASS', 'UNKNOWN') or result['width'] != len(result['checks']):
                raise ValueError('invalid control summary')
        return
    targets = {str(t['target']): t for t in root['targets']}
    for key, entry in data['counts'].items():
        target = targets[key]
        if entry['width'] != target['width'] or [c['rank'] for c in entry['cases']] != target['ranks']:
            raise ValueError('wrong width or sampled ranks')
        if len({c['row'] for c in entry['cases']}) != len(target['ranks']):
            raise ValueError('duplicate unranked row')
        if not finite(entry['sampler_build_cpu_s']):
            raise ValueError('sampler CPU')
        for c in entry['cases']:
            if (c['root'], c['type'], c['target'], c['parent']) != (root['id'], root['type'], target['target'], root['row']):
                raise ValueError('sample identity')
            if not finite(c['unrank_cpu_s']) or set(c['variants']) != {v[0] for v in VARIANTS}:
                raise ValueError('sample variants or CPU')
            for v in c['variants'].values():
                if type(v['pass']) is not bool or not finite(v['cpu_s']):
                    raise ValueError('variant status or CPU')
                if (v['pass'] and v['reason'] is not None) or (not v['pass'] and v['reason'] not in ('capacity', 'label_disjoint')):
                    raise ValueError('variant reason')
            if not c['variants']['F']['pass']:
                raise ValueError('invalid F sample')


def mathematical_controls():
    from validate import verify_bvls
    import sat_control
    from kernel import Geo
    from filters import check
    from runtime import BASE
    bvls = verify_bvls()
    raw = json.loads((BASE / 'fixtures/bvls.json').read_text())
    full = {int(k): int(v, 16) for k, v in raw['rows_m11'].items()}
    positives = []
    # Full independent matrix check above; exact witness pinned as assumptions.
    for depth in (1, 2, 10):
        rows = {u: full[u] for u in range(depth)}
        for name, ld, cap in VARIANTS:
            assert check(Geo(11), rows, ld, cap)['pass']
            outcome = sat_control.check(rows, 11, ld, cap, depth if cap else None, full)
            assert outcome['status'] == 'SAT', (depth, name, outcome)
            positives.append({'depth': depth, 'variant': name, **outcome})
    # Deliberately malformed predicates isolate both rejection implementations.
    class PredicateGeometry(Geo):
        def verify(self, rows):
            pass
    g = PredicateGeometry(3)
    pair = next((v, w) for v in range(1, g.n) for w in range(v + 1, g.n)
                if g.sets[v] & g.sets[w])
    v, w = pair
    bad = {0: (1 << v) | (1 << w), v: (1 << w) | 1}
    assert check(g, bad, True, False)['reason'] == 'label_disjoint'
    assert sat_control.check(bad, 3, True, False)['status'] == 'UNSAT_UNCERTIFIED'
    bad = {u: 0 for u in range(g.n - 1)}
    outcome = check(g, bad, False, True)
    assert outcome['reason'] == 'capacity'
    assert sat_control.check(bad, 3, False, True, outcome['row'])['status'] == 'UNSAT_UNCERTIFIED'
    return {'status': 'PASS', 'bvls': bvls, 'independent_CNF_positive_witnesses': positives,
            'predicate_only_invalid_negatives': 2, 'scope': 'new filter/CNF controls; no census recount'}


if __name__ == '__main__':
    import sys
    from runtime import atomic
    atomic(Path(sys.argv[1]), mathematical_controls())
