"""Finite arithmetic, local matching census, and optional historical-list membership.

No SAT solver, graph-existence test, canonical graph census, or proof checker.
"""
import argparse
import collections
import hashlib
import json
import math
import tarfile
import zipfile
from fractions import Fraction
from pathlib import Path


def matchings(vertices):
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for i in range(1, len(vertices)):
        b = vertices[i]
        rest = vertices[1:i] + vertices[i + 1:]
        for tail in matchings(rest):
            yield ((a, b),) + tail


def matching_type(edges):
    adjacency = [set([i ^ 1]) for i in range(12)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    unseen = set(range(12))
    parts = []
    while unseen:
        stack = [unseen.pop()]
        count = 0
        while stack:
            a = stack.pop()
            count += 1
            for b in adjacency[a] & unseen:
                unseen.remove(b)
                stack.append(b)
        assert count % 2 == 0
        parts.append(count // 2)
    return tuple(sorted(parts))


def finite_checks():
    counts = collections.Counter(matching_type(m) for m in matchings(tuple(range(12))))
    assert sum(counts.values()) == 10395 and len(counts) == 11
    rows = []
    for parts, observed in sorted(counts.items(), key=lambda x: (-x[0].count(1), x[0])):
        denominator = math.prod(parts) * math.prod(math.factorial(v) for v in collections.Counter(parts).values())
        expected = 2 ** (6 - len(parts)) * math.factorial(6) // denominator
        assert observed == expected
        rows.append({'partition': parts, 'anchor_degree': parts.count(1), 'labelled_matchings': observed})
    assert {r['anchor_degree'] for r in rows} == {0, 1, 2, 3, 4, 6}
    assert sum(r['anchor_degree'] <= 2 for r in rows) == 8
    # Algebraic frame counts and group orders, independent of existence of a solution.
    structural = {'outer_vertices': math.comb(14, 2) - 7, 'outer_orbits': 42,
                  'primary_bits': 2 * math.comb(42, 2), 'frame_group_order': 2 ** 7 * math.factorial(7),
                  'anchor_stabilizer_order': 2 ** 6 * math.factorial(6)}
    assert structural == {'outer_vertices': 84, 'outer_orbits': 42, 'primary_bits': 1722,
                          'frame_group_order': 645120, 'anchor_stabilizer_order': 46080}
    stages = [('Generalize', 4686633), ('One3 additional', 1032), ('Generalize2 additional', 2466285),
              ('Two3 additional', 7), ('seed_172_step_45', 228040), ('A union B additional', 6245),
              ('C additional', 188), ('Rest218 trim/cake', 217), ('Rest218 direct cake', 1)]
    remaining = 7388648
    ledger = []
    for name, count in stages:
        remaining -= count
        ledger.append({'stage': name, 'additional_excluded_claimed': count, 'remaining': remaining})
    assert remaining == 0 and ledger[3]['remaining'] == 234691
    return {'status': 'PASS', 'matching_types': rows, 'structural_counts': structural,
            'historical_coverage_arithmetic': ledger,
            'coverage_scope': 'Arithmetic consistency of inherited stage counts, not fresh certificate or coverage verification.'}


def list_membership(census_tsv, continuation_tar, rest_pyz):
    with tarfile.open(continuation_tar) as archive:
        raw = archive.extractfile('inputs/remaining_234691.tsv').read()
    assert hashlib.sha256(raw).hexdigest() == '3c4155233a8969ecbaa8dec288491aced9034b9af6ea606971f5c6c74c0074fb'
    lines = raw.splitlines()
    header = b'code\taut\tmutual_edges\tdegrees\tstratum'
    assert lines[0] == header
    records = {int(line.split(b'\t', 1)[0]): line for line in lines[1:]}
    assert len(records) == len(lines) - 1 == 234691
    pending = set(records)
    n3_counts = collections.Counter()
    full_sha = hashlib.sha256()
    with Path(census_tsv).open('rb') as stream:
        first = stream.readline()
        full_sha.update(first)
        assert first.rstrip(b'\r\n') == header
        for line in stream:
            full_sha.update(line)
            code = int(line.split(b'\t', 1)[0])
            if code in pending:
                assert line.rstrip(b'\r\n') == records[code], 'Metadata changed between census and rest list'
                pending.remove(code)
    assert not pending
    assert full_sha.hexdigest() == 'd003dd431ce506b0bbf936441b970cf80d99027e7d35219b26763312bffbb538'
    for line in records.values():
        n3_counts[line.split(b'\t')[3].split(b',').count(b'3')] += 1
    with zipfile.ZipFile(rest_pyz) as archive:
        rest_raw = archive.read('payload/inputs/remaining_218.tsv')
    assert hashlib.sha256(rest_raw).hexdigest() == 'ade2b458fbf77a272fa058eee97e49daf34f0de24e9fb37403e8a17dd18d87f5'
    rest_lines = rest_raw.splitlines()
    assert rest_lines[0] == header
    small = {int(line.split(b'\t', 1)[0]): line for line in rest_lines[1:]}
    assert len(small) == len(rest_lines) - 1 == 218
    assert all(records.get(code) == row for code, row in small.items())
    return {'status': 'PASS', 'rest234691_count': len(records), 'all_rest234691_rows_byte_identical_in_census': True,
            'all_rest218_rows_byte_identical_in_rest234691': True, 'rest218_count': len(small),
            'rest234691_distribution_by_number_of_degree3_anchors': dict(sorted(n3_counts.items())),
            'census_sha256': full_sha.hexdigest(), 'rest234691_sha256': hashlib.sha256(raw).hexdigest(),
            'rest218_sha256': hashlib.sha256(rest_raw).hexdigest(),
            'limit': 'Membership only; no claim that the rest lists are the exact complements of the prior exclusions.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--census-tsv')
    parser.add_argument('--continuation-tar')
    parser.add_argument('--rest-pyz')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = finite_checks()
    inputs = [args.census_tsv, args.continuation_tar, args.rest_pyz]
    if any(inputs):
        if not all(inputs):
            parser.error('All three input paths are required for membership verification')
        report['list_membership'] = list_membership(*inputs)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
