import bootstrap
"""Finite paired experiment and its deterministic post-run checks."""
import collections
import json
import time
from pathlib import Path
from filters import check
from kernel import Geo, VertexSampler
from plan import VARIANTS, choose_controls
from runtime import atomic, connect, digest


def sample_target(root, target, stop, progress, output):
    from depth2 import predict, exact_split, RestrictedSampler
    from matching import root_objects
    g = Geo()
    parent = int(root['row'], 16)
    start = time.process_time()
    sampler = VertexSampler(g, parent, target['target'])
    build_cpu = time.process_time() - start
    assert sampler.total == target['width']
    prepared = []
    try:
        for rank in target['ranks']:
            start = time.process_time()
            row = sampler.unrank(rank)
            prepared.append({'rank': rank, 'row': hex(row), 'prediction': predict(g, parent, target['target'], row),
                             'unrank_cpu_s': time.process_time() - start})
        # All predictions are durably committed BEFORE invoking any filter.
        prediction_path = Path(output).with_suffix('.predictions.' + str(target['target']) + '.json')
        atomic(prediction_path, {'root': root['id'], 'target': target['target'], 'states': prepared})
        exact = exact_split(g, parent, target['target'], target['width'])
        cases = []
        for index, item in enumerate(prepared):
            if stop():
                return None
            state = {0: parent, target['target']: int(item['row'], 16)}
            outcomes = {}
            for name, ld, cap in VARIANTS[index % 4:] + VARIANTS[:index % 4]:
                start = time.process_time()
                outcomes[name] = check(g, state, ld, cap)
                outcomes[name]['cpu_s'] = time.process_time() - start
            if any(outcomes[n]['pass'] != item['prediction'][n] for n, _, _ in VARIANTS):
                atomic(Path(output).with_suffix('.MISMATCH.json'), {'item': item, 'outcomes': outcomes})
                raise ValueError('reviewer theorem falsified: predicted/actual decision mismatch')
            cases.append({'root': root['id'], 'type': root['type'], 'target': target['target'],
                          'parent': root['row'], 'class_e_s': target['class_e_s'], **item, 'variants': outcomes})
            progress(index + 1)
        good = RestrictedSampler(g, parent, target['target'], forbid=exact['bad_common_neighbors'])
        try:
            for rank in sorted({0, good.total // 2, good.total - 1}) if good.total else []:
                assert check(g, {0: parent, target['target']: good.unrank(rank)}, True, True)['pass']
        finally:
            good.rec.cache_clear()
        return {'width': sampler.total, 'cpu_s': build_cpu + sum(c['unrank_cpu_s'] +
                sum(v['cpu_s'] for v in c['variants'].values()) for c in cases),
                'sampler_build_cpu_s': build_cpu, 'cases': cases, 'exact': exact,
                'prediction_digest': digest(prepared), 'prediction_mismatches': 0,
                'matching_objects': root_objects(g, parent) if target == root['targets'][0] else None}
    finally:
        sampler.rec.cache_clear()


def load_cases(run):
    con = connect(run, readonly=True)
    cases = []
    try:
        records = con.execute('SELECT payload,digest FROM results WHERE root!=0').fetchall()
        if len(records) != 24:
            raise ValueError('controls require all 24 completed sample jobs')
        for rec in records:
            data = json.loads(rec['payload'])
            if digest(data) != rec['digest']:
                raise ValueError('sample digest mismatch')
            for target in data['counts'].values():
                cases.extend(target['cases'])
    finally:
        con.close()
    if len(cases) != 3072:
        raise ValueError('incomplete sample')
    return cases


def control_job(run, output, stop, progress):
    import sat_control
    selected = choose_controls(load_cases(run))
    atomic(Path(output).with_suffix('.control_selection.json'), selected)
    checks = []
    for bucket in selected:
        for case in bucket['cases']:
            for name, ld, cap in VARIANTS:
                outcome = case['variants'][name]
                if outcome['pass'] or outcome['reason'] != bucket['reason']:
                    continue
                if stop():
                    return None
                rows = {0: int(case['parent'], 16), case['target']: int(case['row'], 16)}
                # LD failures need only their contradictory zero-edge equations;
                # CAP uses the specific open row named by the rejection witness.
                result = sat_control.check(rows, 7, ld, cap and outcome['reason'] == 'capacity',
                                           outcome.get('row'))
                rec = {k: case[k] for k in ('root', 'type', 'target', 'rank')}
                rec.update(variant=name, reason=bucket['reason'], **result)
                checks.append(rec)
                atomic(Path(output).with_suffix('.controls.json'), checks)
                progress(len(checks))
                if result['status'] == 'SAT':
                    raise ValueError('independent SAT control contradicts rejection: ' + str(rec))
    return {'width': len(checks), 'cpu_s': sum(r['encoding_cpu_s'] + r['solve_cpu_s'] for r in checks),
            'status': 'PASS' if all(r['status'] == 'UNSAT_UNCERTIFIED' for r in checks) else 'UNKNOWN',
            'selection': [{k: v for k, v in b.items() if k != 'cases'} | {'states': len(b['cases'])}
                          for b in selected], 'checks': checks, 'certified': False}


def summary(con):
    records = con.execute('SELECT root,payload,digest FROM results ORDER BY root').fetchall()
    if records and json.loads(records[0]['payload'])['counts'].get('1', {}).get('cell') is not None:
        from tree_probe import summarize
        return summarize(con)
    groups, exact, matchings = {}, [], []
    controls = None
    total = 0
    for rec in records:
        data = json.loads(rec['payload'])
        assert digest(data) == rec['digest']
        if rec['root'] == 0:
            controls = data['counts']['1']
            continue
        for entry in data['counts'].values():
            first = entry['cases'][0]
            exact.append({'root': first['root'], 'target': first['target'], 'class_e_s': first['class_e_s'], **entry['exact']})
            if entry['matching_objects']:
                matchings.append({'root': first['root'], **entry['matching_objects']})
            for c in entry['cases']:
                total += 1
                key = str(c['class_e_s'])
                group = groups.setdefault(key, {'states': 0, 'prediction_mismatches': 0,
                    'variants': {n: {'passed': 0, 'rejected': 0, 'cpu_s': 0.} for n, _, _ in VARIANTS}})
                group['states'] += 1
                for n, v in c['variants'].items():
                    group['prediction_mismatches'] += int(v['pass'] != c['prediction'][n])
                    group['variants'][n]['passed' if v['pass'] else 'rejected'] += 1
                    group['variants'][n]['cpu_s'] += v['cpu_s']
    passed = total == 3072 and controls and controls['status'] == 'PASS' and all(g['prediction_mismatches']==0 for g in groups.values())
    return {'status': 'LEMMA_FALSIFICATION_PASS' if passed else 'INCOMPLETE_OR_FAILED',
            'states': total, 'variant_decisions': total * 4, 'relation_classes': groups,
            'exact_width_partitions': exact, 'matching_objects': matchings, 'controls': controls,
            'census_repeated': False, 'scope': '48 previously untested targets; exact restricted widths; 24 matching quotients'}
