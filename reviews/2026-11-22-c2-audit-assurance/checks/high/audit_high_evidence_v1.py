"""Independent ledger/readback audit for S2; never treats missing work as closed."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
SOURCES = ['own_pair2.cpp', 'own_pair2_checked', 'star_dump.cpp',
           'star_dump_checked', 'own_local.py', 'own_setup.py',
           'layouts.tsv', 'jobs_manifest.json']


def digest_stream(stream):
    result = hashlib.sha256()
    count = 0
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        count += len(block)
        result.update(block)
    return result.hexdigest(), count


def digest(path):
    with path.open('rb') as stream:
        return digest_stream(stream)[0]


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def parse_ledger(path):
    records = defaultdict(list)
    for line in path.read_text().splitlines():
        words = line.split()
        assert len(words) >= 4 and words[2] == 'mode', (path, line)
        key = tuple(map(int, [words[0], words[1], words[3]]))
        assert 'open' in words and words[words.index('open') + 1] == '0'
        assert 'truncated' in words and words[words.index('truncated') + 1] == '0'
        records[key].append(words)
    return records


def validate_plan():
    manifest = load(BASE / 'jobs_manifest.json')
    jobs = manifest['jobs']
    assert len(jobs) == 3156
    assert Counter(j['kind'] for j in jobs) == {'baseline': 3050, 'strong': 106}
    expected = {}
    for kind, amount in [('baseline', 3050), ('strong', 106)]:
        records = parse_ledger(BASE / (kind + '_expected.tsv'))
        assert len(records) == amount
        for key, rows in records.items():
            assert key not in expected
            if kind == 'baseline':
                assert len(rows) == 1
            else:
                next_start = 0
                for index, words in enumerate(rows):
                    start = int(words[words.index('range') + 1])
                    end = int(words[words.index('range') + 2])
                    checked = int(words[words.index('checked') + 1])
                    limited = int(words[words.index('limited') + 1])
                    assert start == next_start and start <= end
                    assert 0 <= checked <= end - start
                    assert limited == (index < len(rows) - 1)
                    next_start = start + checked
            expected[key] = kind
    planned = {}
    for job in jobs:
        key = (job['chart'], job['packet_parity'], job['mode'])
        assert key not in planned and job['kind'] == expected[key]
        assert job['id'] == '.'.join(map(str, key))
        assert job['own_parity'] == 1 - job['packet_parity']
        planned[key] = job
    assert planned.keys() == expected.keys()
    assert {key[1] for key in planned} == {0, 1}
    assert {key[2] for key in planned} == {0, 1}
    return planned


def audit_job(directory, expected, source_hashes, star_counts, orbit_result):
    record = load(directory / 'result.json')
    assert record['job'] == expected
    assert record['status'] == 'SECOND_SOLVER_CLOSED'
    assert record['depth_limit'] == 30
    assert record['source_hashes'] == source_hashes
    assert record['open'] == 0 and record['closed'] == record['stars'] > 0
    own_key = f"{expected['chart']},{expected['own_parity']}"
    target = (star_counts[own_key] if expected['kind'] == 'baseline'
              else orbit_result['counts'][own_key]['orbits'])
    assert record['stars'] == target
    assert set(record['input_archives']) == {'setup.txt', 'stars.txt'}
    for name, receipt in record['input_archives'].items():
        archive = directory / (name + '.gz')
        assert archive.stat().st_size == receipt['compressed_bytes']
        assert digest(archive) == receipt['compressed_sha256']
        with gzip.open(archive, 'rb') as stream:
            actual, _ = digest_stream(stream)
        assert actual == receipt['uncompressed_sha256']
    with gzip.open(directory / 'stars.txt.gz', 'rt') as stream:
        lines = set()
        for line in stream:
            words = tuple(map(int, line.split()))
            assert len(words) == 24 and words not in lines
            for position in range(0, 24, 2):
                support, sign = words[position:position + 2]
                assert support >= 0 and sign >= 0 and sign & ~support == 0
            lines.add(words)
    assert len(lines) == target
    assert set(record['output_hashes']) == {'solver.stdout', 'solver.stderr'}
    for name, expected_hash in record['output_hashes'].items():
        assert digest(directory / name) == expected_hash
    output = (directory / 'solver.stdout').read_text()
    errors = (directory / 'solver.stderr').read_text()
    summaries = re.findall(r'^stars (\d+) open (\d+) closed (\d+)\s*$', output, re.M)
    assert len(summaries) == 1
    assert tuple(map(int, summaries[0])) == (target, 0, target)
    assert not re.search(r'runtime error:|AddressSanitizer|Assertion.*failed', errors)
    return {'id': expected['id'], 'stars': target,
            'result_sha256': digest(directory / 'result.json')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    output = BASE / args.output
    assert not output.exists(), 'Audit records are immutable; select a new output name'
    plan = validate_plan()
    source_hashes = {name: digest(BASE / name) for name in SOURCES}
    star_counts = load(BASE / 'star_counts_own.json')
    orbit_result = load(BASE / 'orbits_result.json')
    assert orbit_result['status'] == 'ALL_98_ORBIT_REGENERATIONS_PASS'
    by_id = {job['id']: job for job in plan.values()}
    paths = sorted((BASE / 'jobs').glob('*/result.json'))
    assert len({p.parent.name for p in paths}) == len(paths)
    assert all(path.parent.name in by_id for path in paths)
    snapshot_count = len(paths)
    if args.limit:
        assert args.limit > 0
        paths = paths[:args.limit]
    passed, failures = [], []
    for path in paths:
        try:
            passed.append(audit_job(path.parent, by_id[path.parent.name], source_hashes,
                                    star_counts, orbit_result))
        except Exception as error:
            failures.append({'id': path.parent.name, 'error': repr(error)})
    complete = len(passed) == 3156 and not failures and not args.limit
    report = {
        'status': ('COMPLETE_S2_LEDGER_AND_READBACK_PASS' if complete else
                   'PARTIAL_AUDIT_PASS_NOT_COMPLETE' if not failures else 'AUDIT_FAILURE'),
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'expected_jobs': 3156, 'available_results_at_start': snapshot_count,
        'audited': len(passed), 'pending_or_not_audited': 3156 - len(passed),
        'coverage_complete': complete, 'failures': failures, 'passed': passed,
        'source_hashes': source_hashes, 'audit_source_sha256': digest(Path(__file__)),
        'scope': 'Ledger completeness, natural exhaustion, source identity and full gzip readback; not a new mathematical review of the solver.'}
    with output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=4)
    print(json.dumps({k: v for k, v in report.items() if k not in ['passed', 'source_hashes']}))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
