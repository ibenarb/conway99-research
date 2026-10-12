"""Enumeration jobs, independent orbit audit and reproducible stratified sampling."""
import collections
import itertools
import json
import math
from pathlib import Path
import random
import sys


def decode(code, n=7):
    out = [set() for _ in range(n)]
    bit = 0
    for a in range(n):
        for b in range(n):
            if a != b:
                if code >> bit & 1:
                    out[a].add(b)
                bit += 1
    if code >> bit:
        raise ValueError('Code has excess bits')
    return out


def c4_free(out):
    n = len(out)
    # Independent characterization: two vertices cannot have two mutual neighbors.
    mutual = [{j for j in out[i] if i in out[j]} for i in range(n)]
    return all(len(mutual[i] & mutual[j]) < 2 for i in range(n) for j in range(i))


def canonical(out):
    n = len(out)
    groups = collections.defaultdict(list)
    for i in range(n):
        groups[len(out[i]), sum(i in out[j] for j in range(n)),
               sum(j in out[i] and i in out[j] for j in range(n))].append(i)
    groups = [groups[k] for k in sorted(groups)]
    best = None
    aut = 0
    # No neighbor refinement here: this audits the C++ refinement independently.
    for blocks in itertools.product(*(itertools.permutations(g) for g in groups)):
        order = sum(blocks, ())
        code = sum(1 << (n * a + b) for a, i in enumerate(order)
                   for b, j in enumerate(order) if j in out[i])
        if best is None or code < best:
            best, aut = code, 1
        elif code == best:
            aut += 1
    return best, aut


def profiles():
    return [[6] * six + [4] * four + [3] * (7 - six - four)
            for six in range(7) for four in range(7 - six)]


def jobs():
    result = []
    for degree in profiles():
        name = 'd' + ''.join(map(str, degree))
        for mask in range(128):
            if not mask & 1 and mask.bit_count() == degree[0]:
                result.append({'id': name + '_r%03d' % mask, 'degrees': degree, 'firstmask': mask})
    return result


def read_reps(path):
    seen = set()
    with Path(path).open() as stream:
        for line in stream:
            code, aut, mutual = map(int, line.split())
            if code in seen or aut < 1 or math.factorial(7) % aut:
                raise ValueError('Duplicate or invalid representative record')
            seen.add(code)
            yield code, aut, mutual


def audit_and_sample(work, count=200):
    from runtime import save, sha
    work = Path(work)
    groups = collections.defaultdict(list)
    for job in jobs():
        groups[tuple(job['degrees'])].append(job)
    strata = collections.defaultdict(lambda: {'population': 0, 'reservoir': []})
    summaries = []
    rng = random.Random(20260926)
    total = 0
    out_file = work / 'representatives.tsv'
    out_file.write_text('code\taut\tmutual_edges\tdegrees\tstratum\n')
    for degree, shards in sorted(groups.items(), reverse=True):
        merged = {}
        leaves = 0
        inputs = []
        for job in shards:
            prefix = work / 'shards' / job['id']
            summary_file = prefix.with_suffix('.json')
            reps_file = prefix.with_suffix('.tsv')
            data = json.loads(summary_file.read_text())
            if (data['status'] != 'COMPLETE' or data['n'] != 7 or data['degrees'] != list(degree)
                    or data['firstmask'] != job['firstmask']):
                raise ValueError('Shard identity mismatch')
            leaves += data['degree_sorted_labelled']
            records = list(read_reps(reps_file))
            if len(records) != data['representatives_in_shard']:
                raise ValueError('Shard record count mismatch')
            for code, aut, mutual in records:
                if code in merged and merged[code] != (aut, mutual):
                    raise ValueError('Duplicate shard record disagrees')
                merged[code] = aut, mutual
            inputs.append({'id': job['id'], 'reps_sha256': sha(reps_file), 'summary_sha256': sha(summary_file)})
        multiplicity = math.factorial(7)
        for frequency in collections.Counter(degree).values():
            multiplicity //= math.factorial(frequency)
        labelled = leaves * multiplicity
        orbit_sum = 0
        signatures = set()
        degree_list = list(degree)
        emitted = []
        for code, (expected_aut, mutual) in sorted(merged.items()):
            out = decode(code)
            if tuple(map(len, out)) != degree or not c4_free(out):
                raise ValueError('Invalid graph in representative list')
            signature, aut = canonical(out)
            if signature in signatures or aut != expected_aut:
                raise ValueError('Isomorphism duplicate or wrong automorphism order')
            signatures.add(signature)
            if mutual != sum(i in out[j] for i in range(7) for j in out[i]) // 2:
                raise ValueError('Wrong mutual-edge count')
            orbit_sum += 5040 // aut
            key = (degree.count(3), degree.count(6), mutual // 4)
            row = {'code': code, 'aut': aut, 'mutual_edges': mutual,
                   'degrees': degree_list, 'stratum': '_'.join(map(str, key))}
            stratum = strata[row['stratum']]
            stratum['population'] += 1
            total += 1
            if len(stratum['reservoir']) < count:
                stratum['reservoir'].append(row)
            else:
                position = rng.randrange(stratum['population'])
                if position < count:
                    stratum['reservoir'][position] = row
            emitted.append(f"{code}\t{aut}\t{mutual}\t{','.join(map(str, degree))}\t{row['stratum']}\n")
            if len(emitted) >= 4096:
                with out_file.open('a') as stream:
                    stream.writelines(emitted)
                emitted.clear()
        with out_file.open('a') as stream:
            stream.writelines(emitted)
        if orbit_sum != labelled:
            raise ValueError('Orbit sum does not cover degree-sorted enumeration')
        summaries.append({'degrees': list(degree), 'degree_sorted_labelled': leaves,
                          'label_multiplier': multiplicity, 'labelled': labelled,
                          'orbits': len(merged), 'orbit_sum': orbit_sum, 'shards': inputs})
        print('CENSUS_PROFILE_VERIFIED ' + json.dumps({k: v for k, v in summaries[-1].items() if k != 'shards'}), flush=True)
    if total < count:
        raise ValueError('Fewer than requested sample cases; inspect census')
    # At most 28 degree profiles times three mutual-edge bands = 84 strata.
    allocation = {k: min(2, v['population']) for k, v in strata.items()}
    if sum(allocation.values()) > count:
        raise ValueError('Too many strata for minimum sample allocation')
    while sum(allocation.values()) < count:
        key = max((k for k in sorted(strata) if allocation[k] < strata[k]['population']),
                  key=lambda k: count * strata[k]['population'] / total - allocation[k])
        allocation[key] += 1
    selected = []
    for key in sorted(strata):
        selected.extend(rng.sample(sorted(strata[key]['reservoir'], key=lambda r: r['code']), allocation[key]))
    rng.shuffle(selected)
    for i, row in enumerate(selected):
        row['sample_index'] = i
    report = {'status': 'CENSUS_COVERAGE_VERIFIED', 'orbits': total,
              'labelled': sum(p['labelled'] for p in summaries), 'profiles': summaries,
              'strata': {k: {'population': strata[k]['population'], 'sample': allocation[k]} for k in sorted(strata)},
              'representatives_sha256': sha(out_file), 'sampling_seed': 20260926,
              'stratum_definition': '(number of degree-3 classes, number of degree-6 classes, floor(mutual_edges/4))',
              'scope': 'C4-free arrow digraphs with degrees in {3,4,6} and at least one degree 3; NOT SAT solutions.'}
    save(work / 'census.json', report)
    save(work / 'sample.json', {'census_sha256': sha(work / 'census.json'), 'cases': selected})
    print('CENSUS_COMPLETE ' + json.dumps({'orbits': total, 'labelled': report['labelled'], 'sample_cases': len(selected)}), flush=True)


if __name__ == '__main__':
    audit_and_sample(sys.argv[1])
