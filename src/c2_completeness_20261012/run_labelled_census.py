"""Independent exhaustive labelled census and comparison to the audited orbit sum."""
import argparse
import collections
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def parse(text):
    profiles = {}
    total = None
    for line in text.splitlines():
        fields = line.split('\t')
        if fields[0] == 'PROFILE':
            degree = tuple(map(int, fields[1].split(',')))
            assert degree not in profiles
            profiles[degree] = dict(zip(('degree_sorted_labelled', 'label_multiplier', 'labelled'), map(int, fields[2:])))
        elif fields[0] == 'TOTAL':
            total = {'profiles': int(fields[1]), 'labelled': int(fields[2]), 'elapsed_seconds': float(fields[3])}
        else:
            raise ValueError('Unexpected output')
    assert total is not None and total['profiles'] == len(profiles)
    return profiles, total


def direct_four_vertex_counts():
    arcs = [(i, j) for i in range(4) for j in range(4) if i != j]
    cycles = [(0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3)]
    counts = collections.Counter()
    for code in range(1 << 12):
        edges = {arc for bit, arc in enumerate(arcs) if code & (1 << bit)}
        if any(all((cycle[i], cycle[(i + 1) % 4]) in edges and (cycle[(i + 1) % 4], cycle[i]) in edges for i in range(4)) for cycle in cycles):
            continue
        degree = tuple(sorted((sum(i == a for a, b in edges) for i in range(4)), reverse=True))
        counts[degree] += 1
    assert sum(counts.values()) == 4050
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expected-census', required=True)
    parser.add_argument('--isomorphism-audit', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(__file__).with_name('count_labelled.cpp')
    output = Path(args.output)
    expected_path = Path(args.expected_census)
    expected = json.loads(expected_path.read_text())
    iso_path = Path(args.isomorphism_audit)
    iso = json.loads(iso_path.read_text())
    assert iso['status'] == 'PASS' and iso['mode'] == 'full'
    flags = ['-O3', '-std=c++17']
    with tempfile.TemporaryDirectory(prefix='c2_labelled_count_') as temp:
        binary = Path(temp) / 'counter'
        subprocess.run(['g++', *flags, str(source), '-o', str(binary)], check=True, capture_output=True, text=True)
        compiler = subprocess.run(['g++', '--version'], check=True, capture_output=True, text=True).stdout.splitlines()[0]
        cp = subprocess.run([str(binary), '--control4'], check=True, capture_output=True, text=True)
        controls, control_total = parse(cp.stdout)
        brute = direct_four_vertex_counts()
        assert len(controls) == 35
        assert all(row['labelled'] == brute.get(degree, 0) for degree, row in controls.items())
        assert control_total['labelled'] == 4050
        print('CONTROL4_PASS all 4096 directed graphs; 35 degree profiles; 4050 C4-free graphs', flush=True)
        lines = []
        with output.with_suffix('.log').open('w') as log:
            log.write(cp.stdout)
            with subprocess.Popen([str(binary), '--count7'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as process:
                for line in process.stdout:
                    lines.append(line)
                    log.write(line)
                    log.flush()
                    print(line, end='', flush=True)
                assert process.wait() == 0, 'Enumeration failed'
        observed, total = parse(''.join(lines))
    expected_profiles = {tuple(row['degrees']): row for row in expected['profiles']}
    assert set(observed) == set(expected_profiles) and len(observed) == 28
    assert all(row['labelled'] == expected_profiles[degree]['labelled'] for degree, row in observed.items())
    assert total['labelled'] == expected['labelled'] == iso['labelled_orbit_sum'] == 37030041152
    result = {
        'status': 'PASS', 'checked_at': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
        'method': 'Exhaust every row mask for every nonincreasing degree sequence; prune only a mutual C4 on already assigned vertices. No canonicalization, SAT, or historical shard reuse.',
        'scope': 'Loopless digraphs on seven vertices, all outdegrees in {3,4,6}, at least one outdegree 3, mutual graph C4-free.',
        'labelled': total['labelled'], 'elapsed_seconds': total['elapsed_seconds'],
        'profiles': [{'degrees': degree, **row} for degree, row in observed.items()],
        'independent_orbit_sum': iso['labelled_orbit_sum'], 'nonisomorphic_representatives': iso['records'],
        'exhaustiveness_conclusion': 'The structurally audited, pairwise nonisomorphic representatives have independently verified orbit sizes summing to the independently counted entire labelled domain; hence they represent every orbit of this exact domain.',
        'control4': {'all_directed_graphs_tested': 4096, 'degree_profiles': 35, 'c4_free': 4050, 'independent_bruteforce_agrees': True},
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'expected_census_sha256': hashlib.sha256(expected_path.read_bytes()).hexdigest(),
        'isomorphism_audit_sha256': hashlib.sha256(iso_path.read_bytes()).hexdigest(),
        'compiler': compiler, 'compiler_flags': flags,
        'limits': ['Does not prove admissibility of the C4/Profile46 filters for SRG solutions.',
                   'Does not prove CNF adequacy or inherited UNSAT/coverage assertions.',
                   'Does not exclude C2 cases outside the Profile346 branch.',
                   'Finite exhaustive software audit with explicit counting argument; not a proof-assistant-verified implementation.']
    }
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print('INDEPENDENT_CENSUS_COMPLETENESS_PASS', result['labelled'], result['nonisomorphic_representatives'], flush=True)


if __name__ == '__main__':
    main()
