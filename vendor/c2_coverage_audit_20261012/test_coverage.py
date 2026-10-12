"""Independent exhaustive permutation oracle for the C++ pattern matcher."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile


def images(n, pos, neg):
    edges = [(a, b) for a in range(n) for b in range(n) if a != b]
    index = {e: i for i, e in enumerate(edges)}
    result = set()
    for perm in itertools.permutations(range(n)):
        masks = []
        for value in (pos, neg):
            masks.append(sum(1 << index[perm[a], perm[b]] for i, (a, b) in enumerate(edges) if value >> i & 1))
        result.add(tuple(masks))
    return result


def run(exe, n, codes, patterns):
    orbits = [images(n, p, q) for p, q in patterns]
    expected_hits = [0] * len(patterns)
    expected_uncovered = []
    for code in codes:
        hits = [any(code & p == p and code & q == 0 for p, q in orbit) for orbit in orbits]
        expected_hits = [a + b for a, b in zip(expected_hits, hits)]
        if not any(hits):
            expected_uncovered.append(code)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'p.txt').write_text(''.join(f'{p} {q}\n' for p, q in patterns))
        (root / 'r.tsv').write_text('code\taut\tmutual_edges\tdegrees\tstratum\n' + ''.join(f'{c}\t1\t0\t3,3,3\ttest\n' for c in codes))
        result = subprocess.run([exe, str(n), root / 'p.txt', root / 'r.tsv', root / 'u.tsv'],
                                check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        assert report == {'total': len(codes), 'covered': len(codes) - len(expected_uncovered),
                          'remaining': len(expected_uncovered), 'hits': expected_hits}
        assert [int(line.split()[0]) for line in (root / 'u.tsv').read_text().splitlines()[1:]] == expected_uncovered


def main(exe):
    rng = random.Random(20260927)
    pats = [(0, 0), (1, 0), (0, 1), (4095, 0), (0, 4095)]
    for _ in range(20):
        p = rng.randrange(4096)
        q = rng.randrange(4096) & ~p
        pats.append((p, q))
    run(exe, 4, list(range(4096)), pats)
    run(exe, 4, list(range(4096)), pats[3:])
    run(exe, 4, list(range(4096)), [])
    codes = [0, (1 << 42) - 1] + [rng.getrandbits(42) for _ in range(80)]
    pats = []
    for _ in range(8):
        p = rng.getrandbits(42)
        q = rng.getrandbits(42) & ~p
        pats.append((p, q))
    pats += [(1, 0), (0, 1)]
    run(exe, 7, codes, pats)
    print('COVERAGE_CONTROLS_PASS exhaustive_n4=4096 random_n7=82', flush=True)


if __name__ == '__main__':
    main(str(Path(sys.argv[1]).resolve()))
