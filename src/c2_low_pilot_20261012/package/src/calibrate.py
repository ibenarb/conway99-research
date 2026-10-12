"""Extract recorded costs, retaining repeated attempts and missing entries."""
import json
import re
import sys
from pathlib import Path


def quantiles(values):
    values = sorted(values)
    if not values:
        return None
    return {'n': len(values), 'median': (values[(len(values)-1)//2]+values[len(values)//2])/2,
            'p90_nearest_rank': values[(9*len(values)+9)//10-1], 'maximum': values[-1], 'sum': sum(values)}


def main(source, destination):
    records = []
    for p in sorted(Path(source).glob('*/work/jobs/*/result.json')):
        r = json.loads(p.read_text())
        match = re.match(r'p(\d+)_', p.parent.name)
        if not match:
            continue
        proof_sizes = [v['bytes'] for v in r.get('outputs', []) if v['path'].endswith(('.lrat', '.drat'))]
        log = p.parent / 'output.log'
        conflicts = []
        if log.exists():
            conflicts = re.findall(r'^c conflicts:\s*(\d+)', log.read_text(errors='replace'), re.M)
        records.append({'profile': match[1], 'job': p.parent.name, 'source': str(p.relative_to(source)),
                        'category': r.get('category'), 'returncode': r.get('returncode'),
                        'cpu_seconds': r.get('cpu_seconds'), 'max_rss_kib': r.get('max_rss_kib'),
                        'proof_bytes': sum(proof_sizes) if proof_sizes else None,
                        'conflicts': int(conflicts[-1]) if conflicts else None})
    totals = {}
    for r in records:
        row = totals.setdefault(r['profile'], {'solver': 0, 'checker': 0, 'aux': 0})
        if r['cpu_seconds'] is not None:
            row[r['category']] = row.get(r['category'], 0) + r['cpu_seconds']
    summary = {'scope': 'Completed recorded jobs only, repeated attempts retained; no reconstruction of unrecorded CPU. Not a LOW forecast.',
               'profiles_with_receipts': len(totals), 'records': len(records),
               'per_profile_recorded_cpu': {c: quantiles([r[c] for r in totals.values()]) for c in ['solver','checker','aux']},
               'proof_bytes_per_job': quantiles([r['proof_bytes'] for r in records if r['proof_bytes'] is not None]),
               'missing_conflict_counts': sum(r['conflicts'] is None for r in records),
               'missing_cpu_counts': sum(r['cpu_seconds'] is None for r in records),
               'rows': records, 'profile_totals': totals}
    Path(destination).write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','profile_totals']},indent=2))


if __name__ == '__main__':
    main(*sys.argv[1:])
