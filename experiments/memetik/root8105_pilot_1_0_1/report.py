"""Observed widths, censoring and storage rates; no invented total-tree ETA."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from core import atomic


def report(directory):
    directory = Path(directory)
    levels = defaultdict(list)
    roots = []
    observed_bytes = 0
    for checkpoint in sorted((directory / 'work').glob('*/checkpoint.json')):
        state = json.loads(checkpoint.read_text())
        name = checkpoint.parent.name
        roots.append({'job': name, 'max_depth': state['max_depth'],
                      'observed_models': state['observed_models'],
                      'closed_projections': state['closed_projections'],
                      'limited_projections': state['limited_projections'],
                      'restarts': state.get('restarts', 0)})
        for meta in checkpoint.parent.glob('enumerations/*/enumeration.json'):
            item = json.loads(meta.read_text())
            levels[(item['arm'], item['depth'])].append(item)
            observed_bytes += (meta.parent / 'rows.txt').stat().st_size
    rows = []
    for (arm, depth), items in sorted(levels.items()):
        complete = [x['count'] for x in items if x['status'] == 'PROJECTED_ENUMERATION_COMPLETE']
        limited = [x['count'] for x in items if x['status'] != 'PROJECTED_ENUMERATION_COMPLETE']
        counts = sum(x['count'] for x in items)
        cpu = sum(x['cpu_s'] for x in items)
        rows.append({'arm': arm, 'depth': depth, 'projections': len(items),
                     'complete': len(complete), 'censored': len(limited),
                     'observed_rows': counts, 'largest_exact_width': max(complete, default=None),
                     'largest_censored_lower_bound': max(limited, default=None),
                     'projection_cpu_s': cpu, 'observed_rows_per_cpu_s': counts / cpu if cpu else None,
                     'encoding_cpu_s': sum(x.get('encode_cpu_s', 0) for x in items),
                     'max_worker_rss_kib': max(x.get('max_rss_kib', 0) for x in items),
                     'canonical_cpu_s': sum(x.get('canonical_cpu_s', 0) for x in items),
                     'sampled_children': sum(x.get('sampled_children', 0) for x in items),
                     'duplicates_against_retained_sample': sum(x.get('sample_duplicates', 0) for x in items)})
    for filename, records in [('growth_by_depth.csv', rows), ('roots_summary.csv', roots)]:
        if records:
            with (directory / filename).open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(records[0]))
                writer.writeheader()
                writer.writerows(records)
    receipts = json.loads((directory / 'receipts.json').read_text()) if (directory / 'receipts.json').exists() else []
    certs = [json.loads(p.read_text()) for p in (directory / 'work').glob('*/enumerations/*/certificate.json')]
    observations = sum(r['observed_rows'] for r in rows)
    summary = {'status': 'OBSERVATIONAL_PILOT_REPORT', 'max_depth': max((r['max_depth'] for r in roots), default=1),
               'jobs_with_checkpoint': len(roots), 'wait4_cpu_s': sum(r['cpu_s'] for r in receipts),
               'outcomes': dict(Counter(r['status'] for r in receipts)),
               'observed_rows': observations, 'projection_record_bytes': observed_bytes,
               'mean_bytes_per_projection_record': observed_bytes / observations if observations else None,
               'certified_projected_closures': sum(c.get('certified', False) for c in certs),
               'certificate_outcomes': dict(Counter(c['status'] for c in certs)),
               'certified_root_exclusions': 0,
               'full_tree_size': None, 'full_8105_runtime_prediction': None,
               'warning': 'Sampled parents, beam truncation and censored widths. No global depth barrier or root exhaustion.',
               'deep_state_storage_note': 'One raw partial state needs depth*(1+11) bytes before metadata; files also retain projections.'}
    atomic(directory / 'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    print(json.dumps(report(args.directory), indent=2))
