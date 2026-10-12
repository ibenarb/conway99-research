"""Common six-input threshold counter and exact, disjoint N partition."""
import json
from pathlib import Path
import shutil

from c2_reference import CNF, Frame, sha256, write_json
from counter import CounterCNF, encode_variant

BASE_SHA = '7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd'
MAP_SHA = 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'


def threshold_counter(cnf, inputs):
    outputs = []
    for value in inputs:
        updated = []
        for previous in outputs:
            high = cnf.variable()
            low = cnf.variable()
            cnf.clause(-previous, high)
            cnf.clause(-value, high)
            cnf.clause(previous, value, -high)
            cnf.clause(-low, previous)
            cnf.clause(-low, value)
            cnf.clause(low, -previous, -value)
            updated.append(high)
            value = low
        outputs = updated + [value]
    return outputs


def exact_cube(outputs, value):
    if not 0 <= value <= len(outputs):
        raise ValueError('Counter value outside domain')
    if value == 0:
        return [-outputs[0]]
    if value == len(outputs):
        return [outputs[-1]]
    return [outputs[value - 1], -outputs[value]]


def augment(source, target, variables, clauses):
    target = Path(target)
    temporary = target.with_suffix('.writing')
    with Path(source).open('rb') as src, temporary.open('wb') as dst:
        header = src.readline().decode().split()
        if header[:2] != ['p', 'cnf'] or variables < int(header[2]):
            raise ValueError('Unexpected DIMACS header')
        if any(abs(lit) > variables or lit == 0 for row in clauses for lit in row):
            raise ValueError('Invalid appended literal')
        dst.write(f'p cnf {variables} {int(header[3]) + len(clauses)}\n'.encode())
        shutil.copyfileobj(src, dst)
        for clause in clauses:
            dst.write((' '.join(map(str, clause)) + (' ' if clause else '') + '0\n').encode())
    temporary.replace(target)
    return sha256(target)


def header_variables(path):
    return int(Path(path).open().readline().split()[2])


def build_base(directory, k=14):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    cnf, frame = CounterCNF(), Frame(k)
    frame.allocate(cnf)
    try:
        phases = encode_variant(cnf, frame)
        result = cnf.write(directory / 'base.cnf')
        if k == 14 and result['sha256'] != BASE_SHA:
            raise ValueError('Reference base hash mismatch')
        write_json(directory / 'variables.json', frame.mapping())
        if k == 14 and sha256(directory / 'variables.json') != MAP_SHA:
            raise ValueError('Reference mapping mismatch')
        write_json(directory / 'base.json', {**result, 'phases': phases})
    finally:
        cnf.close()


def case_extension(base, certfile, mapping):
    cert = json.loads(Path(certfile).read_text())
    indexed = {v: (block, i, j) for v, block, i, j in mapping['primary_variables']}
    reverse = {(block, i, j): v for v, block, i, j in mapping['primary_variables']}
    edges = [indexed[lit] for lit in cert['units'] if lit > 0]
    if len(edges) != 6 or any(block != 'B' or not 0 <= i < j < 12 for block, i, j in edges):
        raise ValueError('Unexpected hub-0 matching certificate')
    if sorted(i for _, a, b in edges for i in (a, b)) != list(range(12)):
        raise ValueError('Positive units are not a perfect matching')
    inputs = [reverse['C', i, j] for _, i, j in edges]
    extra = CNF(retain=True)
    extra.variables = header_variables(base)
    try:
        outputs = threshold_counter(extra, inputs)
        return {'units': cert['units'], 'inputs': inputs, 'outputs': outputs,
                'variables': extra.variables, 'counter_clauses': extra.saved}
    finally:
        extra.close()


def write_proof(path, clauses):
    Path(path).write_text(''.join(' '.join(map(str, row)) + (' ' if row else '') + '0\n'
                                for row in clauses))
