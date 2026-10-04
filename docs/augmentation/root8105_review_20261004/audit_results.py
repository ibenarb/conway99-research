"""Read-only consistency audit of the supplied reports, not a proof recheck."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


def main():
    base = Path(__file__).resolve().parent
    raw = base / 'raw'
    summary = json.loads((raw / 'summary.json').read_text())
    receipts = json.loads((raw / 'receipts.json').read_text())
    aux = json.loads((raw / 'aux_ledger.json').read_text())
    with (raw / 'roots_summary.csv').open(newline='') as handle:
        roots = list(csv.DictReader(handle))
    with (raw / 'growth_by_depth.csv').open(newline='') as handle:
        levels = list(csv.DictReader(handle))
    assert len(receipts) == len({r['job'] for r in receipts}) == 768
    assert len(roots) == len({r['job'] for r in roots}) == 256
    by_kind = {k: [r for r in receipts if r['kind'] == k] for k in ('search', 'proof')}
    assert len(by_kind['search']) == 256 and len(by_kind['proof']) == 512
    assert {r['job'] for r in roots} == {r['job'] for r in by_kind['search']}
    assert dict(Counter(r['status'] for r in receipts)) == summary['outcomes']
    assert all(r['status'] == 'CPU_LIMIT_UNKNOWN' for r in by_kind['search'])
    assert all(r['status'] == 'PROJECTED_COVERAGE_DRAT_VERIFIED' for r in by_kind['proof'])
    assert all(r['exit'] == 0 for r in receipts)
    assert sum(int(r['observed_rows']) for r in levels) == summary['observed_rows']
    assert sum(int(r['observed_models']) for r in roots) == summary['observed_rows']
    assert max(int(r['max_depth']) for r in roots) == summary['max_depth'] == 16
    assert math.isclose(sum(r['cpu_s'] for r in receipts), summary['wait4_cpu_s'], abs_tol=1e-6)
    pairs = defaultdict(dict)
    for r in roots:
        root, arm = r['job'].rsplit('_', 1)
        pairs[root][arm] = int(r['max_depth'])
    assert len(pairs) == 128 and all(set(p) == {'ordered', 'dynamic'} for p in pairs.values())
    arms = {}
    for arm in ('ordered', 'dynamic'):
        rr = [r for r in roots if r['job'].endswith('_' + arm)]
        ll = [r for r in levels if r['arm'] == arm]
        integer_fields = ('observed_rows', 'projections', 'complete', 'censored',
                          'sampled_children', 'duplicates_against_retained_sample')
        entry = {f: sum(int(r[f]) for r in ll) for f in integer_fields}
        for f in ('projection_cpu_s', 'encoding_cpu_s', 'canonical_cpu_s'):
            entry[f] = sum(float(r[f]) for r in ll)
        entry['depth_distribution'] = dict(sorted(Counter(int(r['max_depth']) for r in rr).items()))
        entry['median_max_depth'] = median(int(r['max_depth']) for r in rr)
        entry['restarts'] = sum(int(r['restarts']) for r in rr)
        entry['early_projection_cpu_fraction'] = sum(float(r['projection_cpu_s']) for r in ll if int(r['depth']) <= 5) / entry['projection_cpu_s']
        d1 = next(r for r in ll if int(r['depth']) == 1)
        entry['depth1'] = {f: int(d1[f]) for f in ('projections', 'complete', 'censored', 'observed_rows')}
        entry['depth1']['mean_observed_width'] = int(d1['observed_rows']) / int(d1['projections'])
        assert entry['complete'] + entry['censored'] == entry['projections']
        arms[arm] = entry
    result = {
        'status': 'REPORT_CONSISTENCY_PASS',
        'scope': 'Counts and CPU reconciliation only; no DRAT, CNF or H-fibre reproduction',
        'source_archive_sha256': hashlib.sha256((base / 'ROOT8105_Abschlussberichte.tar.gz').read_bytes()).hexdigest(),
        'search_jobs': 256, 'proof_jobs': 512, 'root_classes': 128,
        'cpu_hours': {k: sum(r['cpu_s'] for r in rr) / 3600 for k, rr in by_kind.items()},
        'aux_cpu_hours': aux['cpu_s'] / 3600,
        'total_cpu_hours': (summary['wait4_cpu_s'] + aux['cpu_s']) / 3600,
        'paired_depth_comparison': dict(Counter('dynamic_deeper' if p['dynamic'] > p['ordered'] else 'ordered_deeper' if p['ordered'] > p['dynamic'] else 'equal' for p in pairs.values())),
        'arms': arms,
        'same_capped_pilot_scenario_not_full_search': {
            'search_cpu_hours': 8105 * 2,
            'ideal_days_at_11_cores_without_overhead': 8105 * 2 / 11 / 24,
            'projection_bytes_linear_mean': summary['projection_record_bytes'] * 8105 / 128,
            'qualification': 'Illustrative unweighted extrapolation; stratified sample, fixed old one-hour caps; not new GC-19 runtime prediction'
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
