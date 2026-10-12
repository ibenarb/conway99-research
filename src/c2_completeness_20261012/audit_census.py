"""Audit uploaded census data; not an independent exhaustive enumeration or SAT proof."""
import hashlib
import itertools
import json
import math
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parent
archive = Path(sys.argv[1]).resolve()
historical = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
expected_sha = 'd003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538'
names = ['README.md', 'expected_census.json', 'work/enumeration/census.json', 'work/enumeration/representatives.tsv']
report = {
    'checked_at': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
    'archive_name': archive.name,
    'archive_bytes': archive.stat().st_size,
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'checks': {},
    'files': {},
    'limitations': [
        'No fresh exhaustive enumeration of all admissible directed graphs.',
        'No fresh isomorphism or automorphism-order computation; exact code uniqueness is checked.',
        'Orbit-weight sums use the automorphism orders stored in the TSV.',
        'No fresh SAT solver or UNSAT certificate checking.',
        'No proof here of mathematical admissibility of census filters or general C2 exclusion.'
    ]
}
with zipfile.ZipFile(archive) as z:
    assert sorted(z.namelist()) == sorted(names), 'Unexpected archive members'
    assert z.testzip() is None, 'ZIP CRC failure'
    report['checks']['zip_crc_and_expected_members'] = True
    expected = json.loads(z.read('expected_census.json'))
    census = json.loads(z.read('work/enumeration/census.json'))
    for name in names:
        digest = hashlib.sha256()
        with z.open(name) as stream:
            for block in iter(lambda: stream.read(1048576), b''):
                digest.update(block)
        report['files'][name] = {'bytes': z.getinfo(name).file_size, 'sha256': digest.hexdigest()}
    tsv = root / 'representatives.tsv'
    with z.open(names[-1]) as source, tsv.open('wb') as target:
        shutil.copyfileobj(source, target)
    if historical:
        with tarfile.open(historical) as old:
            old_names = {m.name: m for m in old.getmembers() if m.isfile()}
            historical_comparison = {}
            for name in names[:-1]:
                raw = old.extractfile(old_names[name]).read()
                historical_comparison[name] = raw == z.read(name)
            report['historical_companion_comparison'] = historical_comparison
            assert all(historical_comparison.values()), 'Historical companion differs'
        report['historical_archive_name'] = historical.name
        report['historical_archive_sha256'] = hashlib.sha256(historical.read_bytes()).hexdigest()
assert report['files'][names[-1]]['sha256'] == expected_sha == census['representatives_sha256'] == expected['representatives_sha256']
report['checks']['representatives_hash_matches_prior_evidence'] = True
result = subprocess.run([str(root / 'validate_records'), str(tsv)], text=True, capture_output=True)
(root / 'validation_output.txt').write_text(result.stdout + result.stderr)
assert result.returncode == 0, result.stderr
profiles = {}
strata = {}
aut_histogram = {}
for line in result.stdout.splitlines():
    fields = line.split('\t')
    if fields[0] == 'TOTAL':
        records, weights = map(int, fields[1:])
    elif fields[0] == 'PROFILE':
        profiles[tuple(map(int, fields[1].split(',')))] = tuple(map(int, fields[2:]))
    elif fields[0] == 'STRATUM':
        strata[fields[1]] = int(fields[2])
    elif fields[0] == 'AUT':
        aut_histogram[fields[1]] = int(fields[2])
assert records == census['orbits'] == expected['orbits'] == 7388648
assert weights == census['labelled'] == expected['labelled'] == 37030041152
all_profiles = {tuple(sorted(p, reverse=True)) for p in itertools.combinations_with_replacement([3, 4, 6], 7) if 3 in p}
assert len(census['profiles']) == len(expected['profiles']) == len(all_profiles) == 28
assert {tuple(p['degrees']) for p in census['profiles']} == all_profiles
assert {tuple(p['degrees']) for p in expected['profiles']} == all_profiles
assert set(profiles).issubset(all_profiles)
for group in (census['profiles'], expected['profiles']):
    for p in group:
        assert profiles.get(tuple(p['degrees']), (0, 0)) == (p['orbits'], p['labelled'])
for p in census['profiles']:
    counts = [p['degrees'].count(x) for x in (3, 4, 6)]
    multiplier = math.factorial(7) // math.prod(math.factorial(n) for n in counts)
    assert multiplier == p['label_multiplier']
    assert p['degree_sorted_labelled'] * multiplier == p['labelled'] == p['orbit_sum']
assert strata == {k: v['population'] for k, v in census['strata'].items()}
report['checks'].update({
    'all_rows_parse_and_codes_fit_42_bits': True,
    'all_codes_distinct': True,
    'all_decoded_degree_sequences_match_records': True,
    'all_degrees_in_3_4_6_with_at_least_one_3': True,
    'all_mutual_edge_counts_match_records': True,
    'all_mutual_graphs_have_no_four_cycle': True,
    'all_stratum_labels_match_decoded_graphs': True,
    'all_stored_automorphism_orders_positive_divisors_of_5040': True,
    'all_28_profile_counts_and_stored_aut_weight_sums_match_both_json_files': True,
    'all_stratum_populations_match_census_json': True,
    'label_multiplier_arithmetic_matches': True
})
report.update({'records': records, 'distinct_codes': records, 'stored_aut_weight_sum': weights,
               'degree_profiles_total': len(all_profiles), 'degree_profiles_nonempty': len(profiles),
               'strata_nonempty': len(strata), 'stored_automorphism_order_histogram': aut_histogram,
               'scope': census['scope'], 'result': 'PASS'})
report['documentation_note'] = 'README heading says 1.0.0; installation path, export name and correction section say 1.0.1. README bytes equal earlier 1.0.1 result export.'
for name in ('validate_records.cpp', 'audit_census.py'):
    report.setdefault('audit_source_sha256', {})[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
(root / 'audit.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps(report, indent=2, sort_keys=True))
