"""Separate S1 coverage/readback auditor; no search or setup imports.

Reconstructs literal base capacities, exact unary root masks and coloured
matching automorphisms independently. Search closure is evidenced by the
immutable solver's exhaustive transcripts; this is not a third search solver.
Attachment completeness remains a dependency on the disclosed setup routine.
"""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
from math import lcm
import argparse
import gzip
import hashlib
import json
import time

BASE = Path(__file__).resolve().parent
REVISION = 'd73a176f942b1fd67bac3b60c07d181487d84b66'
PINNED = {
    'singleton_exact_v1.cpp': '6c80069212bce1242ccb03c5ec72042890c22ebe22e4db9178fd993618c954af',
    'singleton_exact_v1_checked': '3b6344efe4dd5b23a218ebcfddce95b2521c8d5135473cdb340c3baf23a2d8ca',
    'singleton_setup_v1.py': '570a6c38e9e75ffd8885a34f3233d7735ddd6d5862962532d3f80c61881f4e12',
    'own_local.py': '598ca0b991659ad05e639f9f0a9d07cb9207e96b912da83e68d50e9da4b7abd4',
    'own_setup.py': '8f3179d112054b64db045ed9cea00b42af91ce50f506a5678ed3080346046810',
    'layouts.tsv': '2b776dcaadb5edea804fa38b7821ab91b703216d4ab99ca9f7497f5e9743ccce',
    'jobs_manifest_v1.json': '39fdc990b7e0d008bea8f48f70f546e56d1d76778880a229a03e02c841c3f487',
}
UNARY_SHA = '15f84a5dac12bb4b4d21bdbc170d95992de1d4ba73fd807cc64e648f5c4bffdb'
FIELDS = 'chart roots planned open matches quartets tcaps hpsd hdet lifts fpsd fdet rank first second pair_calls pair_pass'.split()
COUNTERS = FIELDS[4:]
LABELS = [(j, k, t) for j in range(6) for k in range(j + 1, 6) for t in (0, 1)]
BALANCED = [sum(1 << i for i in c) for c in combinations(range(12), 6)]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def base_graph(p, n):
    edges = {(0, 1), (0, 2), (1, 2)}
    for i in range(12):
        edges.update([(0, 3 + i), (3 + i, 3 + (i ^ 1)),
                      (1, 15 + i), (2, 27 + i), (15 + i, 3 + i),
                      (27 + i, 3 + (i ^ 1)), (15 + i, 15 + p[i]),
                      (27 + i, 27 + p[i]), (15 + i, 27 + n[i])])
    graph = [0] * 39
    for x, y in edges:
        assert x != y
        graph[x] |= 1 << y
        graph[y] |= 1 << x
    valid = all(row.bit_count() <= 14 for row in graph)
    valid &= all((graph[x] & graph[y]).bit_count() <= 2 - ((graph[x] >> y) & 1)
                 for x in range(39) for y in range(x))
    return graph, valid


def inverse(matrix):
    size = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for col in range(size):
        pivot = next((i for i in range(col, size) if rows[i][col]), None)
        assert pivot is not None, 'singular matrix'
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            determinant = -determinant
        value = rows[col][col]
        determinant *= value
        rows[col] = [x / value for x in rows[col]]
        for i in range(size):
            if i != col and rows[i][col]:
                value = rows[i][col]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[col])]
    return [row[size:] for row in rows], determinant


def model(p, n):
    groups = []
    unseen = set(range(12))
    while unseen:
        group, todo = set(), [min(unseen)]
        while todo:
            x = todo.pop()
            if x not in group:
                group.add(x)
                todo.extend([x ^ 1, p[x], n[x]])
        groups.append(group)
        unseen -= group
    component = {i: g for g, group in enumerate(groups) for i in group}
    h = [[5 * (i == j) - ((i ^ 1) == j) - 2 * (p[i] == j) - 2 * (n[i] == j)
          for j in range(12)] for i in range(12)]
    f = [[11 * (i == j) + ((i ^ 1) == j) - 4 * (p[i] == j) + 4 * (n[i] == j) - 1
          for j in range(12)] for i in range(12)]
    hi, _ = inverse([[h[i][j] + (component[i] == component[j]) for j in range(12)] for i in range(12)])
    fi, _ = inverse([[x + 1 for x in row] for row in f])
    den = lcm(*(x.denominator for row in hi for x in row))
    integer = [[int(x * den) for x in row] for row in hi]
    roots = []
    for mask in BALANCED:
        signs = [1 if mask & (1 << i) else -1 for i in range(12)]
        same = sum(signs[i] == signs[p[i]] for i in range(12)) + sum(signs[i] == signs[n[i]] for i in range(12))
        if same not in (0, 4):
            continue
        if any(sum(signs[i] for i in group) for group in groups):
            continue
        norm = sum(signs[i] * integer[i][j] * signs[j] for i in range(12) for j in range(12))
        assert norm >= 0
        if norm <= 2 * den:
            roots.append(mask)
    basis = [i for i in range(12) if i != max(groups[component[i]])]
    _, dh = inverse([[h[i][j] for j in basis] for i in basis])
    _, df = inverse([row[:11] for row in f[:11]])
    assert dh > 0 and df > 0 and dh.denominator == df.denominator == 1
    return dict(roots=sorted(roots), h=h, f=f, hi=hi, fi=fi, hrank=len(basis), dh=dh, df=df)


def automorphisms(p, n):
    """Extend a bijection by forced images of all three edge colours.

    Every full automorphism has exactly one branch in this construction:
    the image of the least unmapped vertex is tried among all unused images.
    """
    neighbours = [(i ^ 1, p[i], n[i]) for i in range(12)]
    result = []

    def extend(mapping, occupied):
        if len(mapping) == 12:
            result.append(tuple(mapping[i] for i in range(12)))
            return
        x = next(i for i in range(12) if i not in mapping)
        for y in range(12):
            if y in occupied:
                continue
            trial, used, stack = dict(mapping), set(occupied), [(x, y)]
            valid = True
            while stack:
                a, b = stack.pop()
                if a in trial:
                    if trial[a] != b:
                        valid = False
                        break
                    continue
                if b in used:
                    valid = False
                    break
                trial[a] = b
                used.add(b)
                stack.extend(zip(neighbours[a], neighbours[b]))
            if valid:
                extend(trial, used)
    extend({}, set())
    assert result and len(set(result)) == len(result) and 46080 % len(result) == 0
    return result


def plan():
    for name, digest in PINNED.items():
        assert sha(BASE / name) == digest, ('bound source', name)
    manifest = load(BASE / 'jobs_manifest_v1.json')
    unary_path = BASE / 'audit_inputs_v1/unary_result_v2.json'
    assert sha(unary_path) == UNARY_SHA == manifest['unary_result_sha256']
    unary = load(unary_path)
    rows = [list(map(int, line.split())) for line in (BASE / 'layouts.tsv').read_text().splitlines()]
    assert len(rows) == len(unary['charts']) == manifest['catalogue_count'] == 3580
    assert manifest['frozen_original'] == REVISION
    good, bad = [], []
    for cid, row in enumerate(rows):
        assert len(row) == 25 and row[0] in (7, 8, 9, 10, 11)
        p, n = row[1:13], row[13:]
        for matching in (p, n):
            assert sorted(matching) == list(range(12))
            assert all(matching[i] != i and matching[matching[i]] == i for i in range(12))
        _, physical = base_graph(p, n)
        u = unary['charts'][cid]
        assert u['chart'] == cid and u['physical'] == physical
        (good if physical else bad).append(cid)
    assert good == manifest['search_charts'] and bad == manifest['nonphysical']
    assert len(good) == 3308 and len(bad) == 272
    assert sum(len(x['surviving_sign_masks']) for x in unary['charts']) == manifest['raw_root_signs'] == 177842
    control = load(BASE / 'controls_result_v1.json')
    assert control['status'] == 'SINGLETON_CORE_CONTROLS_PASS'
    assert (control['cases'], control['positive'], control['negative'], control['local_positive_fixtures']) == (2540, 1258, 1282, 58)
    for name, digest in control['hashes'].items():
        assert sha(BASE / name) == digest, ('core control hash', name)
    return rows, unary, good, bad


def transcript(line):
    tokens = line.split()
    assert len(tokens) == 1 + 2 * len(FIELDS)
    assert tokens[1::2] == FIELDS
    values = list(map(int, tokens[2::2]))
    assert min(values) >= 0
    return dict(zip(FIELDS, values))


def audit_one(directory, cid, row, unary_row):
    report = load(directory / 'result.json')
    assert report['status'] == 'SECOND_SINGLETON_SOLVER_CLOSED', 'result not closed'
    assert report['chart'] == cid and report['exit_code'] == 0, 'wrong key or exit'
    expected_files = {'identity.json', 'setup.txt.json', 'solver.stdout', 'solver.stderr'}
    archived = 'lossless_input_archive' in report
    expected_files.add('setup.txt.gz' if archived else 'setup.txt')
    assert set(report['hashes']) == expected_files, 'evidence file set'
    assert {p.name for p in directory.iterdir() if p.is_file()} == expected_files | {'result.json'}
    for name, digest in report['hashes'].items():
        assert sha(directory / name) == digest, ('evidence hash', cid, name)
    assert not (directory / 'solver.stderr').read_bytes(), 'nonempty solver error stream'
    if archived:
        record = report['lossless_input_archive']
        assert record['file'] == 'setup.txt.gz' and record['full_readback'] is True
        assert sha(directory / record['file']) == record['archive_sha256']
        raw = gzip.decompress((directory / record['file']).read_bytes())
        assert len(raw) == record['uncompressed_bytes']
        assert hashlib.sha256(raw).hexdigest() == record['uncompressed_sha256']
    else:
        raw = (directory / 'setup.txt').read_bytes()
    setup = load(directory / 'setup.txt.json')
    assert setup == report['setup'], 'setup metadata mismatch'
    assert setup['chart'] == cid
    assert setup['source_sha256'] == PINNED['singleton_setup_v1.py']
    assert setup['catalogue_sha256'] == PINNED['layouts.tsv']
    assert hashlib.sha256(raw).hexdigest() == setup['setup_sha256'], 'setup byte hash'
    p, n = row[1:13], row[13:]
    graph, physical = base_graph(p, n)
    assert physical
    reconstructed = model(p, n)
    roots = reconstructed['roots']
    assert roots == sorted(unary_row['surviving_sign_masks']), 'unary root coverage'
    assert len(roots) == setup['raw_root_signs']
    group = automorphisms(p, n)
    assert len(group) == setup['orbit_audit']['stabilizer_order'], 'stabilizer order'
    unseen, reps, orbit_records = set(roots), [], []
    while unseen:
        seed = min(unseen)
        positives = [i for i in range(12) if seed >> i & 1]
        orbit = {sum(1 << g[i] for i in positives) for g in group}
        orbit |= {4095 ^ image for image in list(orbit)}
        assert orbit <= unseen, 'orbit overlaps or leaves raw roots'
        orbit_records.append(dict(representative=min(orbit), members=sorted(orbit)))
        reps.append(min(orbit))
        unseen -= orbit
    assert orbit_records == setup['orbit_audit']['orbits'], 'orbit partition'
    assert len(reps) == setup['root_representatives'] == report['roots_planned'] == report['roots_completed']
    lines = raw.decode('ascii').splitlines()
    header = list(map(int, lines[0].split()))
    assert header == [cid, reconstructed['hrank'], reconstructed['dh'], reconstructed['df'], len(reps), setup['attachments']]
    assert list(map(int, lines[1].split())) == reps, 'input root list'
    assert list(map(int, lines[2].split())) == p and list(map(int, lines[3].split())) == n
    assert list(map(int, lines[4].split())) == graph
    for offset, matrix in [(5, reconstructed['hi']), (17, reconstructed['fi']), (29, reconstructed['f'])]:
        actual = [[Fraction(v) for v in line.split()] for line in lines[offset:offset + 12]]
        assert actual == matrix, ('input matrix', offset)
    assert len(lines) == 41 + setup['attachments'], 'truncated attachment table'
    assert setup['unsigned_star_rank'] == reconstructed['hrank'] and setup['signed_star_rank'] == 11
    assert Fraction(setup['unsigned_basis_determinant']) == reconstructed['dh']
    assert Fraction(setup['signed_basis_determinant']) == reconstructed['df']
    seen, unsigneds = set(), set()
    for line in lines[41:]:
        values = tuple(map(int, line.split()))
        assert len(values) == 39 and values not in seen, 'duplicate/malformed attachment'
        seen.add(values)
        label, mask, twin = values[:3]
        assert 0 <= label < 30 and 0 <= mask < (1 << 39) and 0 <= twin < (1 << 39)
        assert mask.bit_count() == twin.bit_count() == 6
        j, k, t = LABELS[label]
        a = [(mask >> (15 + i)) & 1 for i in range(12)]
        b = [(mask >> (27 + i)) & 1 for i in range(12)]
        assert sum(a) == sum(b) == 2
        assert mask & ((1 << 15) - 1) == (1 << (3 + 2 * j)) | (1 << (3 + 2 * k + t))
        twin_expected = (1 << (4 + 2 * j)) | (1 << (3 + 2 * k + 1 - t))
        twin_expected |= sum(a[i] << (27 + i) for i in range(12)) | sum(b[i] << (15 + i) for i in range(12))
        assert twin == twin_expected
        key = tuple(a[i] + b[i] for i in range(12))
        cross = [(-1) ** (i % 2) * ((i // 2 == j) + (-1) ** t * (i // 2 == k)) for i in range(12)]
        assert values[3:15] == key
        assert values[15:27] == tuple(-cross[i] - 4 * (a[i] - b[i]) for i in range(12))
        assert values[27:] == tuple(1 - abs(cross[i]) - 2 * key[i] for i in range(12))
        unsigneds.add((label, key))
    assert len(unsigneds) == setup['unsigned_patterns']
    output = (directory / 'solver.stdout').read_text(encoding='ascii').splitlines()
    last, done, first, final = {x: 0 for x in COUNTERS}, 0, 0, None
    for line in output:
        assert final is None, 'trailing output after FINAL'
        if line.startswith('FIRST '):
            words = line.split()
            assert words[:3] == ['FIRST', 'chart', str(cid)] and words[3] == 'root'
            assert len(words[4]) == 12 and set(words[4]) <= {'0', '1'}
            assert sum((c == '1') << i for i, c in enumerate(words[4])) in reps
            assert words[5] == 'labels' and words[10] == 'domains'
            labels = set(map(int, words[6:10]))
            assert len(labels) == 4 and labels <= set(range(30))
            pairs = [tuple(map(int, word.split(':'))) for word in words[11:]]
            assert len(pairs) == 26 and {x for x, _ in pairs} == set(range(30)) - labels
            assert all(count > 0 for _, count in pairs)
            first += 1
            continue
        assert line.startswith(('ROOT ', 'FINAL ')), 'unrecognized transcript row'
        current = transcript(line)
        assert current['chart'] == cid and current['planned'] == len(reps) and current['open'] == 0
        assert all(current[x] >= last[x] for x in COUNTERS), 'counter regression'
        assert current['first'] == current['second'] == first
        assert current['pair_pass'] <= current['pair_calls']
        if line.startswith('ROOT '):
            done += 1
            assert current['roots'] == done <= len(reps), 'missing/duplicate root completion'
        else:
            assert done == len(reps) == current['roots'], 'incomplete natural exhaustion'
            if done:
                assert all(current[x] == last[x] for x in COUNTERS), 'FINAL differs from last ROOT'
            final = line
        last = current
    assert final is not None and final == report['final_line'], 'missing or mismatched FINAL'
    return dict(chart=cid, raw_roots=len(roots), orbit_representatives=len(reps),
                group_order=len(group), attachments=setup['attachments'],
                first_survivors=last['first'], second_layer_calls=last['second'],
                full_input_readback=True, natural_exhaustion=True,
                result_sha256=sha(directory / 'result.json'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--jobs-root', type=Path, default=BASE / 'jobs')
    args = parser.parse_args()
    started = time.time()
    rows, unary, good, bad = plan()
    candidates, failed = [], []
    for directory in args.jobs_root.iterdir():
        assert directory.is_dir() and directory.name.isdigit(), 'unexpected job entry'
        cid = int(directory.name)
        assert str(cid) == directory.name and cid in good, 'unplanned job'
        path = directory / 'result.json'
        if path.exists():
            report = load(path)
            if report.get('status') == 'SECOND_SINGLETON_SOLVER_CLOSED':
                candidates.append(cid)
            else:
                failed.append(dict(chart=cid, status=report.get('status')))
    assert not failed, ('failed/open results require investigation', failed)
    candidates.sort()
    if args.limit is not None:
        candidates = candidates[:args.limit]
    audited = []
    for cid in candidates:
        audited.append(audit_one(args.jobs_root / str(cid), cid, rows[cid], unary['charts'][cid]))
        if len(audited) % 20 == 0:
            print(json.dumps(dict(audited=len(audited), elapsed_seconds=time.time() - started)), flush=True)
    remaining = sorted(set(good) - set(candidates))
    result = dict(status='SINGLETON_EVIDENCE_SNAPSHOT_PASS', full_S1_coverage=not remaining,
                  frozen_original=REVISION, total_charts=3580, nonphysical_independently_checked=len(bad),
                  search_required=len(good), audited_closed=len(audited), remaining=len(remaining),
                  remaining_charts=remaining, checked=audited, source_hashes=PINNED,
                  unary_input_sha256=UNARY_SHA, auditor_sha256=sha(Path(__file__)),
                  elapsed_seconds=time.time() - started,
                  scope='Full base partition; exact unary roots and complete stabilizer orbits for audited jobs; all bytes and exhaustive transcript rows reread. Attachment completeness and search predicate correctness retain the separately documented implementation/review dependencies. No independent reproduction of the original second-layer survivor ledger is claimed.')
    with Path(args.output).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=4)
    print(json.dumps({k: result[k] for k in ('status', 'full_S1_coverage', 'audited_closed', 'remaining', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
