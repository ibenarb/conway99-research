"""Reproduce archive consistency checks and solver statistics; no SAT proof claim."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
import zipfile


def analyze(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names = {n.replace('\\', '/'): n for n in z.namelist()}
        assert len(names) == len(z.namelist())
        def raw(n):
            return z.read(names[n])
        def obj(n):
            return json.loads(raw(n))
        s = obj('summary.json')
        assert s['status'] == 'TOTALIZER_LONG_COMPLETE_NO_CERTIFICATION'
        assert s['error'] is None and not s['interrupted_jobs']
        assert len(s['results']) == 11 and len({r['id'] for r in s['results']}) == 11
        rows = []
        for r in s['results']:
            name = r['id']
            assert obj(name + '/result.json') == r
            job = obj(name + '/job.json')
            assert all(r[k] == v for k, v in job.items())
            log = raw(name + '/solver.log')
            assert len(log) == r['log_bytes']
            text = log.decode()
            assert r['status'] == 'OPEN_BUDGET' and r['exit'] == 0
            assert r['budget_seconds'] == 122400 and r['proof_files_created'] == 0
            assert '\nc UNKNOWN\n' in text and '\nc exit 0\n' in text
            assert not re.search(r'^s (?:SATISFIABLE|UNSATISFIABLE)$', text, re.M)
            counts = {k: int(re.search(r'^c ' + k + r':\s+(\d+)', text, re.M)[1]) for k in ('conflicts','decisions','propagations','restarts','fixed','eliminated')}
            search_percent = float(re.search(r'^c\s+[\d.]+\s+([\d.]+)% search$', text, re.M)[1])
            points = []
            for line in text.splitlines():
                t = line.split()
                if len(t) >= 18 and t[0] == 'c' and len(t[1]) == 1 and re.fullmatch(r'\d+\.\d+', t[2]) and t[-1].endswith('%'):
                    points.append({'cpu_seconds': float(t[2]), 'remaining_variables': int(t[-2]), 'irredundant_clauses': int(t[-3])})
            assert points
            snapshots = {}
            for hours in (1, 8, 24, 34):
                eligible = [p for p in points if p['cpu_seconds'] <= hours*3600]
                if eligible:
                    snapshots[str(hours)] = eligible[-1]
            rows.append(dict(id=name, counts=counts, search_percent=search_percent,
                             peak_rss_MiB=r['peak_rss_KiB']/1024, cpu_seconds=r['solver_cpu_seconds'],
                             snapshots=snapshots, last=points[-1], cnf_sha256=r['cnf_sha256']))
        cpu = sum(r['solver_cpu_seconds'] for r in s['results'])
        assert abs(cpu-s['groups']['totalizer']['cpu_seconds']) < .001
        assert sum(r['labelled_count'] for r in s['results']) == 10395
        return {'archive_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                'archive_bytes': Path(path).stat().st_size, 'entries': len(names),
                'checks': 'CRC, eleven summary/result/job agreements, log lengths, UNKNOWN and exit 0, budgets, group totals',
                'scope': 'Archive consistency only; CNFs and solver binary absent, not rehashed here; no proofs.',
                'config': obj('config.json'), 'cpu_hours': cpu/3600,
                'wall_seconds': s['wall_seconds'], 'guard_read_retries': s['guard_read_retries'],
                'guard_write_retries': s['guard_write_retries'], 'rows': rows,
                'conflicts_total': sum(r['counts']['conflicts'] for r in rows),
                'search_percent_median': statistics.median(r['search_percent'] for r in rows)}


if __name__ == '__main__':
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('C2_Totalizer_34h_20260919_073526.zip')
    print(json.dumps(analyze(p), indent=2))
