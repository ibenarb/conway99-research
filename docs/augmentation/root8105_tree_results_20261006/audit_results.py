"""Audit stored results only; no search, sampler recount or SAT invocation.
Usage: python3 audit_results.py EXTRACTED_RUN OUTPUT_DIRECTORY
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import sqlite3
import sys
import time


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    started = time.process_time()
    source, destination = map(Path, sys.argv[1:3])
    destination.mkdir(parents=True, exist_ok=True)
    envelope = json.loads((source / 'final_receipt.json').read_text())
    receipt = envelope['payload']
    assert digest(receipt) == envelope['sha256'] == '5e7f8273b87c4c4c0c5916238e42b2262cfdf81ba90096d04c645df0c1cdaea8'
    assert receipt['complete'] and receipt['run_id'] == 'fb64e03e22304cb496455ceaa0af1c27'
    summary = json.loads((source / 'summary.json').read_text())
    manifest = json.loads((source / 'manifest.json').read_text())
    assert receipt['summary'] == summary
    assert receipt['fingerprint'] == manifest['fingerprint']
    assert receipt['fingerprint']['code_hash'] == '15fde20b5a11afa4de4bcd942eb5ef50cee2dfc2355449f3e3d987a9e585821a'
    database = sqlite3.connect('file:' + str(source.resolve() / 'run.sqlite') + '?mode=ro', uri=True)
    database.row_factory = sqlite3.Row
    assert database.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    for table in ('roots', 'attempts', 'sessions'):
        rows = [dict(row) for row in database.execute('SELECT * FROM ' + table + ' ORDER BY id')]
        assert rows == receipt[table], table
    assert len(receipt['results']) == len(receipt['roots']) == len(receipt['attempts']) == 96
    assert all(row['state'] == 'DONE' for row in receipt['roots'])
    assert all(row['ended'] is not None and row['cpu_exact'] for row in receipt['attempts'])
    assert all(row['state'] == 'COMPLETE' and row['ended'] is not None for row in receipt['sessions'])
    specs = {row['id']: json.loads(row['spec']) for row in receipt['roots']}
    cell_jobs = collections.defaultdict(list)
    positive_paths, root_statistics = [], []
    steps_checked = 0
    for record in receipt['results']:
        value = record['result']
        row = database.execute('SELECT payload,digest FROM results WHERE root=?', (record['root'],)).fetchone()
        assert digest(value) == record['digest'] == row['digest']
        assert value == json.loads(row['payload']) and value['state'] == 'COMPLETE'
        spec = specs[record['root']]
        assert value['root_row_hash'] == digest(spec['row'])
        assert value['code_hash'] == receipt['fingerprint']['code_hash']
        job = value['counts']['1']
        assert job['root_id'] == spec['root_id'] and job['cell'] == spec['cell']
        assert job['width'] == len(job['records']) == spec['walks']
        assert [walk['index'] for walk in job['records']] == list(range(spec['walks']))
        for walk in job['records']:
            rng = random.Random(spec['seed'] + walk['index'] * 1000000007)
            assert rng.randrange(job['matching_orbits']) == walk['matching_class']
            assert walk['weights'][0] == job['matching_orbits']
            assert len(walk['weights']) == walk['target_depth'] == 13
            depth = walk['reached_rows']
            assert all(w > 0 for w in walk['weights'][:depth])
            assert all(w == 0 for w in walk['weights'][depth:])
            assert len(walk['steps']) in (depth - 1, depth)
            for index, step in enumerate(walk['steps']):
                assert rng.randrange(step['proposal_width']) == step['rank']
                if index < depth - 1:
                    assert step['F_projection_member'] is True
                    assert walk['weights'][index + 1] == walk['weights'][index] * step['proposal_width']
                steps_checked += 1
            assert (walk['termination'] == 'DEPTH_REACHED') == (depth == 13)
            if depth == 13:
                positive_paths.append({'job_id': record['root'], 'root_id': spec['root_id'],
                                       'spec': spec, 'record': walk})
        cell_jobs[job['cell']].append((job, value))
        root_statistics.append({'cell': job['cell'], 'root_id': job['root_id'], 'walks': job['width'],
            'mean_cumulative_nodes': sum(sum(w['weights']) for w in job['records']) / job['width'],
            'positive_depth13': sum(w['weights'][-1] > 0 for w in job['records']),
            'worker_cpu_s_wait4': next(a['cpu'] for a in receipt['attempts'] if a['id'] == value['attempt'])})
    result = {'status': 'STORED_RESULTS_AUDIT_PASS', 'receipt_sha256': envelope['sha256'],
              'run_id': receipt['run_id'], 'walks': 40000, 'random_draws_and_weight_steps_verified': steps_checked,
              'new_searches_or_recounts': 0, 'independent_graph_witness_verification': False,
              'cells': {}, 'root_statistics': root_statistics}
    for cell, pairs in sorted(cell_jobs.items()):
        assert len(pairs) == 24
        jobs = [pair[0] for pair in pairs]
        walks = [walk for job in jobs for walk in job['records']]
        assert len(walks) == 10000
        means = [sum(sum(w['weights']) for w in job['records']) / job['width'] for job in jobs]
        mean = sum(means) / 24
        assert math.isclose(math.log10(mean), summary['cells'][str(cell)]['log10_mean_cumulative_nodes_per_selected_root'], abs_tol=1e-12)
        terminal = [w['weights'][-1] for w in walks]
        terminal_sum = sum(terminal)
        squares = sum(w * w for w in terminal)
        table = []
        for depth in range(13):
            mean_depth = sum(sum(w['weights'][depth] for w in job['records']) / job['width'] for job in jobs) / 24
            count = sum(w['weights'][depth] > 0 for w in walks)
            assert count == summary['cells'][str(cell)]['depth_survival'][depth]['positive_walks']
            table.append({'depth': depth + 1, 'positive_walks': count,
                          'log10_equal_root_mean': math.log10(mean_depth) if mean_depth else None})
        result['cells'][str(cell)] = {'mean_cumulative_nodes': mean, 'log10_mean_cumulative_nodes': math.log10(mean),
            'terminal_weight_ESS': terminal_sum * terminal_sum / squares if squares else 0,
            'terminal_max_weight_fraction': max(terminal) / terminal_sum if terminal_sum else None,
            'positive_depth13': sum(w > 0 for w in terminal),
            'root_ids_reaching_depth13': [job['root_id'] for job in jobs if any(w['weights'][-1] for w in job['records'])],
            'worker_cpu_s_wait4': sum(next(a['cpu'] for a in receipt['attempts'] if a['id'] == value['attempt']) for _, value in pairs),
            'peak_worker_rss_mib': max(value['peak_rss_bytes'] / 2**20 for _, value in pairs),
            'depth_profile_equal_root_weighting': table}
    means = [result['cells'][str(c)]['mean_cumulative_nodes'] for c in range(4)]
    result['exploratory_point_ratios'] = {'old_F_over_new_propagation': means[0] / means[3],
        'old_F_over_new_F': means[0] / means[2], 'old_F_over_old_propagation': means[0] / means[1],
        'new_F_over_new_propagation': means[2] / means[3], 'confidence_bound': None,
        'preregistered_adoption_gate_passed': False}
    base = {r['root_id']: r['mean_cumulative_nodes'] for r in root_statistics if r['cell'] == 0}
    strong = {r['root_id']: r['mean_cumulative_nodes'] for r in root_statistics if r['cell'] == 3}
    ratios = [base[r] / strong[r] for r in base]
    result['rootwise_old_F_over_new_propagation'] = {'minimum': min(ratios), 'maximum': max(ratios),
                                                   'all_24_above_100': all(r > 100 for r in ratios)}
    session = receipt['sessions'][0]
    result['session_utc_elapsed_s'] = session['ended'] - session['started']
    result['accounts_reported'] = summary['accounts']
    result['accounting_scope_note'] = 'Recorded preflight, workers, controller and pre-seal export; final seal serialization/verification tail is not separately timed in this version.'
    assert math.isclose(sum(a['cpu'] for a in receipt['attempts']), summary['accounts']['worker_cpu_s'], abs_tol=1e-6)
    result['analysis_cpu_s'] = time.process_time() - started
    (destination / 'AUDIT_ANALYSIS.json').write_text(json.dumps(result, indent=2) + '\n')
    (destination / 'DEPTH13_PATHS.json').write_text(json.dumps(positive_paths, separators=(',', ':')) + '\n')
    database.close()
    print(json.dumps({k: v for k, v in result.items() if k not in ('cells', 'root_statistics', 'accounts_reported')}, indent=2))
    print('cells', [(k, {a: b for a, b in v.items() if a != 'depth_profile_equal_root_weighting'}) for k, v in result['cells'].items()])


if __name__ == '__main__':
    main()
