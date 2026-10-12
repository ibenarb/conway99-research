"""Independent S7 coverage audit; no project-module or coverage.cpp imports."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def population(path):
    lines = Path(path).read_bytes().splitlines(keepends=True)
    assert lines[0].decode().strip() == 'code\taut\tmutual_edges\tdegrees\tstratum'
    codes = [int(line.split(b'\t')[0]) for line in lines[1:]]
    assert len(codes) == len(set(codes))
    assert all(0 <= code < 2 ** 42 for code in codes)
    return lines, codes


def arc_variables(mapping):
    labels = [tuple(row) for row in mapping['labels']]
    lookup = {label: i for i, label in enumerate(labels)}
    variables = {(block, i, j): v for v, block, i, j in mapping['primary_variables']}
    assert mapping['pair_count'] == 42
    result = {}
    for a in range(7):
        for b in range(7):
            if a == b:
                continue
            x = lookup[tuple(sorted((2 * a, 2 * b))) ]
            y = lookup[tuple(sorted((2 * a, 2 * b + 1))) ]
            block = 'B' if x // 42 == y // 42 else 'C'
            i, j = sorted((x % 42, y % 42))
            result[variables[block, i, j]] = (a, b)
    assert len(result) == 42
    return result


def cover(codes, units, variable_arcs):
    # Independent algorithm: enumerate all permutations; intersect sets of rows.
    # Each column is a Python integer bitset, not per-graph backtracking.
    pairs = [(a, b) for a in range(7) for b in range(7) if a != b]
    bits = {pair: i for i, pair in enumerate(pairs)}
    buffers = [bytearray((len(codes) + 7) // 8) for _ in pairs]
    for row, code in enumerate(codes):
        for bit in range(42):
            if code & (1 << bit):
                buffers[bit][row // 8] |= 1 << (row % 8)
    columns = [int.from_bytes(buf, 'little') for buf in buffers]
    full = (1 << len(codes)) - 1
    result = 0
    for permutation in itertools.permutations(range(7)):
        matching = full
        for unit in units:
            a, b = variable_arcs[abs(unit)]
            column = columns[bits[permutation[a], permutation[b]]]
            matching &= column if unit > 0 else full ^ column
            if not matching:
                break
        result |= matching
    return {codes[i] for i in range(len(codes)) if result >> i & 1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    parser.add_argument('--remaining', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    mapping = json.loads(args.mapping.read_text())
    variables = arc_variables(mapping)
    pins = json.loads((args.package / 'inputs/priority_candidates.json').read_text())
    source = args.package / 'inputs/remaining_234691.tsv'
    lines, codes = population(source)
    candidates = pins['candidates']
    covered = cover(codes, candidates[0]['units'], variables)
    reconstructed = lines[0] + b''.join(line for line, code in zip(lines[1:], codes) if code not in covered)
    assert reconstructed == args.remaining.read_bytes()
    rest = set(codes) - covered
    subsets = {c['id']: cover(sorted(rest), c['units'], variables) for c in candidates[1:]}
    ids = list(subsets)
    pairwise = []
    for a, b in itertools.combinations(ids, 2):
        pairwise.append({'a': a, 'b': b, 'intersection': len(subsets[a] & subsets[b]),
                         'union': len(subsets[a] | subsets[b]),
                         'remaining': len(rest - subsets[a] - subsets[b])})
    signatures = {}
    for flags in itertools.product((0, 1), repeat=3):
        selected = {code for code in rest if tuple(int(code in subsets[i]) for i in ids) == flags}
        signatures[''.join(map(str, flags))] = len(selected)
    report = {'status': 'PASS', 'method': 'exhaustive S7 column-bitset intersections; independent of production matcher',
              'scope': 'checks set coverage and mapping from supplied variables.json; does not prove census completeness or frame necessity',
              'source_sha256': sha(source), 'mapping_sha256': sha(args.mapping),
              'remaining_sha256': sha(args.remaining), 'total': len(codes), 'covered': len(covered),
              'remaining': len(rest), 'rest_byte_identical': True,
              'standalone': {i: len(subsets[i]) for i in ids}, 'pairwise': pairwise,
              'signature_order': ids, 'signatures': signatures,
              'all_three_remaining': len(rest - set.union(*subsets.values())),
              'arc_variable_mapping': {str(v): pair for v, pair in variables.items()},
              'script_sha256': sha(__file__)}
    (args.out / 'independent_coverage_result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'arc_variable_mapping'}, indent=2))


if __name__ == '__main__':
    main()
