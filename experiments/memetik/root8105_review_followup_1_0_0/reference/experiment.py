"""Finite paired experiment and its deterministic post-run checks."""
import collections
import json
import time
from pathlib import Path
from filters import check
from kernel import Geo, VertexSampler
from plan import VARIANTS, choose_controls
from runtime import atomic, connect, digest


def sample_target(root, target, stop, progress):
    g = Geo()
    parent = int(root['row'], 16)
    started = time.process_time()
    sampler = VertexSampler(g, parent, target['target'])
    build_cpu = time.process_time() - started
    if sampler.total != target['width']:
        raise ValueError('sampler disagrees with frozen census width')
    cases = []
    try:
        for index, rank in enumerate(target['ranks']):
            if stop():
                return None
            start = time.process_time()
            row = sampler.unrank(rank)
            unrank_cpu = time.process_time() - start
            state = {0: parent, target['target']: row}
            outcomes = {}
            # Rotate invocation order; no repeated timings or resampling.
            variants = VARIANTS[index % 4:] + VARIANTS[:index % 4]
            for name, ld, cap in variants:
                start = time.process_time()
                outcomes[name] = check(g, state, ld, cap)
                outcomes[name]['cpu_s'] = time.process_time() - start
            if not outcomes['F']['pass']:
                raise ValueError('F sample failed F verification')
            cases.append({'root': root['id'], 'type': root['type'], 'target': target['target'],
                          'rank': rank, 'parent': root['row'], 'row': hex(row),
                          'unrank_cpu_s': unrank_cpu, 'variants': outcomes})
            progress(index + 1)
        return {'width': sampler.total, 'cpu_s': build_cpu + sum(c['unrank_cpu_s'] +
                    sum(v['cpu_s'] for v in c['variants'].values()) for c in cases),
                'sampler_build_cpu_s': build_cpu, 'sampler_cache': sampler.rec.cache_info()._asdict(),
                'target_position': next(i for i, t in enumerate(root['targets']) if t == target),
                'cases': cases}
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
    if len(cases) != 4608:
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
    groups = {}
    totals = {'states': 0, 'samplers': 0, 'sampler_build_cpu_s': 0., 'unrank_cpu_s': 0., 'max_worker_peak_rss_bytes': 0}
    controls = None
    for rec in con.execute('SELECT root,payload,digest FROM results ORDER BY root'):
        data = json.loads(rec['payload'])
        if digest(data) != rec['digest']:
            raise ValueError('result digest mismatch')
        totals['max_worker_peak_rss_bytes'] = max(totals['max_worker_peak_rss_bytes'], data.get('peak_rss_bytes', 0))
        if rec['root'] == 0:
            controls = data['counts']['1']
            continue
        for entry in data['counts'].values():
            totals['samplers'] += 1
            totals['sampler_build_cpu_s'] += entry['sampler_build_cpu_s']
            for case in entry['cases']:
                key = str(case['type']) + ':' + ['minimum', 'median_rank', 'maximum'][entry['target_position']]
                group = groups.setdefault(key, {'states': 0, 'variants': {n: {'passed': 0, 'rejected': 0,
                    'cpu_s': 0., 'reasons': {}} for n, _, _ in VARIANTS}, 'LD_CAP_overlap': 0,
                    'combined_only_rejections': 0})
                group['states'] += 1
                totals['states'] += 1
                totals['unrank_cpu_s'] += case['unrank_cpu_s']
                v = case['variants']
                group['LD_CAP_overlap'] += int(not v['F_LD']['pass'] and not v['F_CAP']['pass'])
                group['combined_only_rejections'] += int(v['F_LD']['pass'] and v['F_CAP']['pass']
                                                         and not v['F_LD_CAP']['pass'])
                for name, val in v.items():
                    g = group['variants'][name]
                    g['passed' if val['pass'] else 'rejected'] += 1
                    g['cpu_s'] += val['cpu_s']
                    if val['reason']:
                        g['reasons'][val['reason']] = g['reasons'].get(val['reason'], 0) + 1
    accepted = totals['states'] == 4608 and controls is not None and controls['status'] == 'PASS'
    return {'status': 'PILOT_COMPLETE' if accepted else 'INCOMPLETE_OR_UNVERIFIED',
            'totals': totals, 'strata_type_target_position': groups, 'controls': controls,
            'scope': 'stratified paired sample; no exact filtered widths, no root exclusions, no SAT witnesses',
            'census_repeated': False}
