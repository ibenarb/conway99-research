"""S3 independent result/coverage audit; imports no search, setup, or controller code."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
INPUT_HASHES = {
    'unary.log': '59502c3cfd34e93679442e85e46bec6807b0b24a9275e616265c66d2d8306504',
    'independent-stars.tsv': 'f619b88135c111c7693995496338fb41a09698d975c17da01ac18bc470bfa38c',
    'generic-low.tsv': '97a4a3db71a00d43a86e9afdcd28165d3bac57cfdfb5a2e1e9887604a8a80a77',
    'generic-low-1.tsv': 'b5588bf6c9cea9782fcabc90102507183221722e54256abe9551b3fa1bfb1fc2'}
SOURCE_NAMES = ['residual_gram_v1.cpp', 'residual_gram_v1_checked', 'low_setup_v1.py',
                'own_setup.py', 'own_local.py', 'star_dump_checked', 'geometry_own.json',
                'layouts.tsv', 'run_one_low_v1.py']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def determinant(matrix):
    a = [[v % 7 for v in row] for row in matrix]
    value = 1
    for col in range(len(a)):
        pivot = next((i for i in range(col, len(a)) if a[i][col]), None)
        assert pivot is not None, 'Singular pivot restriction'
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            value = -value
        value = value * a[col][col] % 7
        inverse = pow(a[col][col], -1, 7)
        for i in range(col + 1, len(a)):
            factor = a[i][col] * inverse % 7
            a[i] = [(u - factor * v) % 7 for u, v in zip(a[i], a[col])]
    return value % 7


def chart_data(row):
    p, n = row[1:13], row[13:25]
    assert sorted(p) == sorted(n) == list(range(12))
    f = [[(11 * (i == j) + ((i ^ 1) == j) - 4 * (p[i] == j) + 4 * (n[i] == j) - 1) % 7
          for j in range(12)] for i in range(12)]
    h = [[5 * (i == j) - ((i ^ 1) == j) - 2 * (p[i] == j) - 2 * (n[i] == j)
          for j in range(12)] for i in range(12)]
    basis, selected = [], []
    for column in range(12):
        vector = [f[i][column] for i in range(12)]
        for pivot, old in basis:
            scalar = vector[pivot]
            vector = [(u - scalar * v) % 7 for u, v in zip(vector, old)]
        pivot = next((i for i, v in enumerate(vector) if v), None)
        if pivot is not None:
            factor = pow(vector[pivot], -1, 7)
            basis.append((pivot, [(factor * v) % 7 for v in vector]))
            selected.append(column)
    assert len(selected) == row[0]
    det = determinant([[f[i][j] for j in selected] for i in selected])
    return det, h


def plan():
    inputs = BASE / 'audit_inputs_v1'
    for name, expected in INPUT_HASHES.items():
        assert sha(inputs / name) == expected
    assert sha(BASE / 'layouts.tsv') == '2b776dcaadb5edea804fa38b7821ab91b703216d4ab99ca9f7497f5e9743ccce'
    layouts = [list(map(int, line.split())) for line in (BASE / 'layouts.tsv').read_text().splitlines()]
    assert len(layouts) == 3580 and all(len(r) == 25 for r in layouts)
    physical, bad = {}, set()
    for line in (inputs / 'unary.log').read_text().splitlines():
        words = line.split()
        cid = int(words[0])
        if words[1] == 'bad':
            assert cid not in bad
            bad.add(cid)
            continue
        parity = int(words[1])
        assert words[2] == 'rank' and int(words[3]) == layouts[cid][0]
        assert words[words.index('truncated') + 1] == '0'
        key = f'{cid}.{parity}'
        assert key not in physical
        physical[key] = int(words[words.index('full') + 1]) > 0
    counts = {}
    for line in (inputs / 'independent-stars.tsv').read_text().splitlines():
        cid, parity, count = map(int, line.split())
        key = f'{cid}.{parity}'
        assert key not in counts and count >= 0
        counts[key] = count
    own_counts = load(BASE / 'star_counts_own.json')
    expected, classification = {}, {}
    for cid, row in enumerate(layouts):
        if row[0] not in (8, 9):
            continue
        det, h = chart_data(row)
        for parity in (0, 1):
            key = f'{cid}.{parity}'
            if cid in bad:
                assert key not in physical and key not in counts
                classification[key] = 'NONPHYSICAL_BASE'
                continue
            assert key in physical and key in counts
            count = counts[key]
            assert bool(count) == physical[key]
            assert own_counts[f'{cid},{1-parity}'] == count
            classification[key] = 'FULL_SEARCH_REQUIRED' if count else 'NO_SIGNED_STAR'
            if count:
                kind = '57_planes' if row[0] == 8 else ('split_all_images' if det in (1, 2, 4) else '8_lines')
                expected[key] = dict(id=key, chart=cid, rank=row[0], packet_parity=parity,
                                     own_parity=1-parity, stars=count, determinant=det,
                                     common_image=kind, h=h)
    assert len(classification) == 204 and len(expected) == 92
    assert Counter(j['common_image'] for j in expected.values()) == {'57_planes': 6, 'split_all_images': 22, '8_lines': 64}
    manifest = load(BASE / 'jobs_manifest.json')
    assert len(manifest['jobs']) == 92 and len(manifest['all_rank8_rank9_entries']) == 204
    assert {j['id']:j['status'] for j in manifest['all_rank8_rank9_entries']} == classification
    assert {j['id'] for j in manifest['jobs']} == set(expected)
    for job in manifest['jobs']:
        assert all(job[k] == v for k, v in expected[job['id']].items() if k != 'h')
    plane_counts = {}
    for name in ('generic-low.tsv', 'generic-low-1.tsv'):
        for line in (inputs / name).read_text().splitlines():
            w = line.split()
            if int(w[w.index('r') + 1]) != 8:
                continue
            key = f'{w[0]}.{w[1]}'
            assert w[w.index('open') + 1] == w[w.index('truncated') + 1] == '0'
            assert int(w[w.index('star') + 1]) == expected[key]['stars']
            plane_counts[key] = int(w[w.index('Wdomains') + 1])
    assert len(plane_counts) == 6
    return expected, plane_counts


def fields(line, marker):
    words = line.split()
    assert words[0] == marker and len(words) % 2 == 1
    keys = words[1::2]
    assert len(keys) == len(set(keys))
    return dict(zip(keys, map(int, words[2::2])))


def audit_one(directory, job, source_hashes, geometry, plane_counts):
    report = load(directory / 'result.json')
    assert report['status'] == 'SECOND_LOW_SOLVER_CLOSED', 'Result is not closed'
    for key in ('chart', 'packet_parity', 'own_parity', 'rank'):
        assert report[key] == job[key], 'Result job key/rank mismatch'
    assert report['source_hashes'] == source_hashes
    assert report['open'] == 0 and report['stars'] == report['closed'] == report['expected_stars'] == job['stars']
    assert report['full_depth'] == 30 and report['depth_cutoff'] is False
    assert report['viable_planes'] == report['closed_planes']
    assert set(report['evidence_hashes']) == {'identity.json', 'progress.json', 'setup.txt', 'stars.txt',
                                           'solver.stdout', 'solver.stderr', 'stars.stderr'}
    for name, expected in report['evidence_hashes'].items():
        assert sha(directory / name) == expected, 'Evidence hash mismatch: ' + name
    for name in ('solver.stderr', 'stars.stderr'):
        assert not (directory / name).read_text(encoding='utf-8').strip(), 'Nonempty error stream'
    with (directory / 'setup.txt').open() as stream:
        header = stream.readline().split()
    assert header[0] == 'LOWGRAM1' and list(map(int, header[1:3])) == [job['rank'], job['determinant']]
    assert len(header) == 4 and int(header[3]) > 0
    central = geometry[str(job['own_parity'])]['central']
    seen = set()
    with (directory / 'stars.txt').open() as stream:
        for line in stream:
            word = tuple(map(int, line.split()))
            assert len(word) == 24 and word not in seen, 'Malformed or duplicate star'
            seen.add(word)
            used = 0
            for i in range(12):
                support, signs = word[2*i:2*i+2]
                assert support in central[i//2] and signs >= 0 and signs & ~support == 0
                assert signs & ~used == 0, 'Noncanonical first coordinate sign'
                used |= support
                for j in range(i+1):
                    overlap = support & word[2*j]
                    assert overlap.bit_count() - 2 * ((signs ^ word[2*j+1]) & overlap).bit_count() == job['h'][i][j]
    assert len(seen) == job['stars']
    lines = (directory / 'solver.stdout').read_text(encoding='utf-8').splitlines()
    assert len(lines) == job['stars'] + 1, 'Missing progress/exhaustion line'
    previous_planes = 0
    for index, line in enumerate(lines[:-1], 1):
        row = fields(line, 'PROGRESS')
        assert row['stars'] == row['closed'] == index and row['open'] == 0
        assert row['viable_planes'] >= previous_planes and 0 <= row['maximum_depth'] < 30
        previous_planes = row['viable_planes']
    final = fields(lines[-1], 'FINAL')
    for key in ('stars', 'open', 'closed', 'viable_planes', 'closed_planes', 'full_depth'):
        assert final[key] == report[key], 'Final exhaustion mismatch'
    assert final['viable_planes'] == previous_planes and final['maximum_depth'] < 30
    if job['rank'] == 8:
        assert report['python_cpp_star_sets_equal'] is True
        assert final['viable_planes'] == plane_counts[job['id']]
    return dict(id=job['id'], result_sha256=sha(directory / 'result.json'),
                stars=final['stars'], planes=final['viable_planes'], maximum_depth=final['maximum_depth'],
                evidence_files=len(report['evidence_hashes']), full_readback=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    expected, plane_counts = plan()
    sources = {name:sha(BASE / name) for name in SOURCE_NAMES}
    geometry = load(BASE / 'geometry_own.json')
    checked, pending = [], []
    for key, job in expected.items():
        directory = BASE / 'jobs' / key
        if not (directory / 'result.json').exists():
            pending.append(key)
            continue
        checked.append(audit_one(directory, job, sources, geometry, plane_counts))
    assert set(r['id'] for r in checked).isdisjoint(pending)
    assert len(checked) + len(pending) == 92
    result = dict(status='ALL_92_SECOND_LOW_RESULTS_AUDITED' if not pending else 'PARTIAL_SECOND_LOW_RESULTS_AUDITED',
                  created_utc=datetime.now(timezone.utc).isoformat(), all_92_covered=not pending,
                  checked=checked, pending=pending, source_hashes=sources, frozen_input_hashes=INPUT_HASHES,
                  auditor_sha256=sha(Path(__file__)), no_solver_code_imported=True,
                  scope='Coverage, input integrity, canonical stars and natural full-search exhaustion; not a new proof of solver correctness.')
    with Path(args.output).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=4)
    print(json.dumps(dict(status=result['status'], checked=len(checked), pending=len(pending))), flush=True)


if __name__ == '__main__':
    main()
