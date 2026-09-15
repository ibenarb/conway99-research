"""Three exact eight-cube partitions. No orbit reduction or proof claim."""
import itertools
import json
from pathlib import Path
from common import CNF_HASH, MAP_HASH, save, sha


def partition_specs(mapping):
    rows = {(block, i, j): v for v, block, i, j in mapping['primary_variables']}
    indices = {tuple(label): i for i, label in enumerate(mapping['labels'][:mapping['pair_count']])}

    def edge(block, left, right):
        i, j = sorted((indices[left], indices[right]))
        return rows[block, i, j]

    a, b, c = (0, 2), (4, 6), (8, 10)
    specs = {
        'disjoint_triangle': [edge('B', a, b), edge('B', a, c), edge('B', b, c)],
        'shared_triangle': [edge('B', a, (0, 4)), edge('B', a, (0, 6)), edge('B', (0, 4), (0, 6))],
        'bc_coupled': [edge('B', a, b), edge('C', a, b), edge('B', a, c)],
    }
    if specs['disjoint_triangle'] != [22, 36, 685]:
        raise ValueError('Old partition identity changed')
    return specs


def prepare(base, out):
    base, out = Path(base), Path(out)
    if sha(base/'baseline.cnf') != CNF_HASH or sha(base/'variables.json') != MAP_HASH:
        raise ValueError('Reference input identity mismatch')
    raw = (base/'baseline.cnf').read_bytes()
    header, body = raw.split(b'\n', 1)
    if header != b'p cnf 570171 1990821' or not body.endswith(b'\n'):
        raise ValueError('Unexpected DIMACS header')
    mapping = json.loads((base/'variables.json').read_text())
    specs = partition_specs(mapping)
    out.mkdir(parents=True, exist_ok=False)
    jobs = []
    for group, variables in specs.items():
        if len(set(variables)) != 3:
            raise ValueError('Non-distinct splitting variables')
        cases = []
        for bits in itertools.product((False, True), repeat=3):
            assumptions = [v if bit else -v for v, bit in zip(variables, bits)]
            name = group + '_' + ''.join(str(int(bit)) for bit in bits)
            cnf = out/(name+'.cnf')
            suffix = ''.join(f'{v} 0\n' for v in assumptions).encode()
            cnf.write_bytes(b'p cnf 570171 1990824\n' + body + suffix)
            if cnf.read_bytes().split(b'\n', 1)[1] != body + suffix:
                raise ValueError('Cube CNF prefix/suffix mismatch')
            case = {'id': name, 'group': group, 'seed': 0, 'cnf': str(cnf.resolve()),
                    'assumptions': assumptions, 'cnf_sha256': sha(cnf)}
            cases.append(case)
            jobs.append(case)
        for bits in itertools.product((False, True), repeat=3):
            assignment = dict(zip(variables, bits))
            if sum(all(assignment[abs(v)] == (v > 0) for v in case['assumptions']) for case in cases) != 1:
                raise ValueError('Partition not exhaustive/disjoint')
    for seed in range(3):
        jobs.append({'id': f'baseline_{seed}', 'group': 'baseline', 'seed': seed,
                     'cnf': str((base/'baseline.cnf').resolve()), 'assumptions': [], 'cnf_sha256': CNF_HASH})
    manifest = {'status': 'PARTITIONS_PREPARED_NOT_SOLVED', 'baseline_sha256': CNF_HASH,
                'mapping_sha256': MAP_HASH, 'split_variables': specs, 'jobs': jobs,
                'coverage_checks': 24, 'scope': 'Three independent full partitions; no equivalence between them asserted.'}
    save(out/'manifest.json', manifest)
    return manifest
