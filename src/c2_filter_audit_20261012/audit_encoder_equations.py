"""Compare every actual encoder equation with an independent E1/E2/E3 construction.

The original encoder is instrumented before sum normalization. The generated CNF
is hashed, so the observed equation stream is tied to the pinned production base.
No satisfiability search is performed. Correctness of BDD/totalizer compilation is
proved separately in ENCODER_ADAEQUANZ.md, not inferred from this finite comparison.
"""
import argparse
import collections
import hashlib
import itertools
import json
from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(source))
    from counter import CounterCNF, encode_variant
    from c2_reference import Frame

    class Observed(CounterCNF):
        def __init__(self):
            super().__init__()
            self.monomials = {}
            self.equations = []

        def conjunction(self, a, b):
            value = super().conjunction(a, b)
            if value is not False and value is not True:
                factors = tuple(sorted({x for x in (a, b) if x is not True}))
                assert all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= 1722 for x in factors)
                if value in self.monomials:
                    assert self.monomials[value] == factors
                self.monomials[value] = factors
            return value

        def exact(self, terms, target):
            polynomial = collections.Counter()
            for term in terms:
                if term is True:
                    polynomial[()] += 1
                elif term is not False:
                    polynomial[self.monomials.get(term, (term,))] += 1
            self.equations.append((tuple(sorted(polynomial.items())), target))
            return super().exact(terms, target)

    encoder = Observed()
    frame = Frame(14)
    frame.allocate(encoder)
    encode_variant(encoder, frame)
    cnf = encoder.write(args.work / 'observed_base.cnf')
    assert cnf['sha256'] == '7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd'
    observed = encoder.equations
    encoder.close()

    # Define the exterior labels without Frame, and recover orbit representatives.
    labels_all = [tuple(sorted((a, b))) for a in range(14) for b in range(a + 1, 14) if a // 2 != b // 2]
    partner = lambda pair: tuple(sorted((pair[0] ^ 1, pair[1] ^ 1)))
    reps = [pair for pair in labels_all if pair < partner(pair)]
    labels = reps + [partner(pair) for pair in reps]
    assert len(labels) == len(set(labels)) == 84 and labels == frame.labels
    assert len(reps) == 42
    # Number unordered pairs directly: B precedes C, then lexicographic pair order.
    pairs = [(i, j) for i in range(42) for j in range(i + 1, 42)]
    primary = {(block, i, j): 1 + b * 861 + k for b, block in enumerate(('B', 'C')) for k, (i, j) in enumerate(pairs)}
    assert sorted(primary.values()) == list(range(1, 1723))
    matrix = []
    for x in range(84):
        row = []
        for y in range(84):
            i, j = sorted((x % 42, y % 42))
            row.append(None if i == j else primary['B' if (x < 42) == (y < 42) else 'C', i, j])
        matrix.append(row)
    assert all((frame.edge(x, y) or None) == matrix[x][y] for x in range(84) for y in range(84))
    expected = []
    counts = collections.Counter()

    def equation(terms, rhs, family):
        polynomial = collections.Counter(tuple(sorted(set(term))) for term in terms)
        expected.append((tuple(sorted(polynomial.items())), rhs))
        counts[family] += 1

    for x in range(84):
        equation([(v,) for v in matrix[x] if v is not None], 12, 'E1')
    for x in range(84):
        for a in range(14):
            equation([(matrix[x][z],) for z in range(84) if a in labels[z] and matrix[x][z] is not None],
                     2 - (a in labels[x]) - ((a ^ 1) in labels[x]), 'E2')
    for x in range(84):
        for y in range(x + 1, 84):
            terms = [(matrix[x][z], matrix[z][y]) for z in range(84) if matrix[x][z] is not None and matrix[z][y] is not None]
            if matrix[x][y] is not None:
                terms.append((matrix[x][y],))
            equation(terms, 2 - len(set(labels[x]).intersection(labels[y])), 'E3')
    assert observed == expected
    assert counts == {'E1': 84, 'E2': 1176, 'E3': 3486}
    assert len(set(expected)) == 2394
    canonical = json.dumps(expected, separators=(',', ':')).encode()
    report = {
        'status': 'PASS', 'checked_at': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
        'scope': 'All requested equations of the actual pinned encoder, before sum normalization, equal independently constructed model equations with full multiplicities.',
        'equations': dict(counts), 'raw_equations': len(expected), 'distinct_equations': len(set(expected)),
        'equation_stream_sha256': hashlib.sha256(canonical).hexdigest(),
        'primary_variables': 1722, 'all_7056_matrix_entries_match_independent_mapping': True,
        'cnf': cnf, 'source_hashes': {name: sha(source / name) for name in ('counter.py', 'c2_reference.py')},
        'auditor_sha256': sha(__file__),
        'limits': ['No satisfiability solver or proof checker was run.', 'Gate and sum-encoding correctness relies on the separate general mathematical proof.', 'No UNSAT or general C2 exclusion follows from encoder adequacy alone.']
    }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print('ENCODER_EQUATION_BINDING_PASS', json.dumps(dict(counts)), cnf['sha256'])


if __name__ == '__main__':
    main()
