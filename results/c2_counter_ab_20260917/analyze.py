"""Reproduce paired diagnostics from the received ZIP, without extracting it."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import zipfile


def analyze(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names = [n.replace('\\', '/') for n in z.namelist()]
        assert len(set(names)) == len(names)
        data = dict(zip(names, [z.read(n) for n in z.namelist()]))
    root = names[0].split('/')[0]
    summary = json.loads(data[root + '/summary.json'])
    config = json.loads(data[root + '/config.json'])
    assert summary['error'] is None and not summary['interrupted_jobs']
    assert len(summary['results']) == 22
    rows = {}
    for r in summary['results']:
        base = root + '/' + r['id']
        assert json.loads(data[base + '/result.json']) == r
        job = json.loads(data[base + '/job.json'])
        assert all(r[k] == v for k, v in job.items())
        log_bytes = data[base + '/solver.log']
        assert len(log_bytes) == r['log_bytes']
        log = log_bytes.decode()
        assert 'c UNKNOWN' in log and 's UNSATISFIABLE' not in log and 's SATISFIABLE' not in log
        assert r['status'] == 'OPEN_BUDGET' and r['exit'] == 0
        assert r['budget_seconds'] == 1200 and r['seed'] == 0 and r['proof_files_created'] == 0
        stats = {k: int(re.search(r'^c ' + k + r':\s+(\d+)', log, re.M)[1])
                 for k in ('conflicts', 'decisions', 'propagations', 'fixed', 'eliminated')}
        last = re.findall(r'^c \? .*$', log, re.M)[-1].split()
        group, case = r['id'].split('__')
        assert group == r['group']
        rows.setdefault(case, {})[group] = dict(stats, remaining_variables=int(last[-2]),
            irredundant_clauses=int(last[-3]), cpu_seconds=r['solver_cpu_seconds'],
            peak_RSS_MiB=r['peak_rss_KiB'] / 1024, assumptions=r['assumptions'])
    assert len(rows) == 11
    for pair in rows.values():
        assert set(pair) == {'reference', 'totalizer'}
        assert pair['reference']['assumptions'] == pair['totalizer']['assumptions']
        for row in pair.values():
            del row['assumptions']
    aggregates = {}
    for g in ('reference', 'totalizer'):
        rs = [pair[g] for pair in rows.values()]
        aggregates[g] = {key: statistics.median(r[key] for r in rs)
                        for key in ('peak_RSS_MiB', 'remaining_variables', 'irredundant_clauses', 'conflicts')}
        aggregates[g]['cpu_hours'] = sum(r['cpu_seconds'] for r in rs) / 3600
        aggregates[g]['conflicts_total'] = sum(r['conflicts'] for r in rs)
    changes = {key: 100 * (aggregates['totalizer'][key] / aggregates['reference'][key] - 1)
               for key in ('peak_RSS_MiB', 'remaining_variables', 'irredundant_clauses', 'conflicts_total')}
    return dict(status='RECEIVED_ARCHIVE_AUDIT_PASS', archive_bytes=path.stat().st_size,
        archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), entries=len(names),
        result_log_job_crosschecks=22, matching_pairs_checked=11, wall_seconds=summary['wall_seconds'],
        config=config, rows=rows, aggregates=aggregates, changes_percent=changes,
        guard_read_retries=summary['guard_read_retries'],
        scope='Logs and metadata only; input CNFs not in ZIP; no new SAT/UNSAT decision or proof.')


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    result = analyze(here / 'C2_Counter_AB_20260916.zip')
    (here / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'aggregates', 'changes_percent')}, indent=2))
