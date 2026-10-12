import itertools
import json
import subprocess
import sys
import time
from pathlib import Path
from common import read, save, sha, require, log_has
from encode import ROOT, frame, units, arc_variables, full, interface, model_values, verify_full, verify_x
from c2_reference import CNF
from model import build_base, threshold_counter


def propagate(clauses, values):
    values = dict(values)
    pending = list(clauses)
    while True:
        left = []
        changed = False
        for clause in pending:
            if any(abs(v) in values and values[abs(v)] == (v > 0) for v in clause):
                continue
            unknown = [v for v in clause if abs(v) not in values]
            if not unknown:
                return False, values
            if len(unknown) == 1:
                v = unknown[0]
                values[abs(v)] = v > 0
                changed = True
            else:
                left.append(tuple(unknown))
        if not changed:
            return True, values
        pending = left


def run_native(command, output):
    with Path(output).open('wb') as stream:
        r = subprocess.run(list(map(str, command)), stdout=stream, stderr=subprocess.STDOUT)
    return r.returncode


def check_proof(formula, proof, directory):
    out = directory / 'cake.log'
    rc = run_native([ROOT / 'bin/cake', '--CML_HEAP_SIZE=512', '--CML_STACK_SIZE=64', formula, proof], out)
    require(rc == 0 and log_has(out, 's VERIFIED UNSAT'), 'CONTROL_PROOF_FAILED')


def controls():
    directory = ROOT / 'work/controls'
    directory.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    findings = {}
    # Independent exhaustive truth table for the counter used by both rules.
    c = CNF(retain=True)
    inputs = [c.variable() for _ in range(12)]
    outputs = threshold_counter(c, inputs)
    for bits in itertools.product((False, True), repeat=12):
        ok, values = propagate(c.saved, dict(zip(inputs, bits)))
        require(ok and all(values[v] == (sum(bits) >= i + 1) for i, v in enumerate(outputs)), 'COUNTER_TRUTH_FAILED')
    c.close()
    findings['counter_12_all_assignments'] = 4096
    # Mapping for every LOW root: independent decoding using labels in mapping.
    mapping = read(ROOT / 'inputs/variables.json')
    roots = read(ROOT / 'inputs/roots.json')
    f = frame()
    for row in roots:
        literal_map = {abs(v): v > 0 for v in units(f, row)}
        seen = 0
        for v, block, i, j in mapping['primary_variables']:
            if v not in literal_map:
                continue
            a = mapping['labels'][i]
            b = mapping['labels'][j + (mapping['pair_count'] if block == 'C' else 0)]
            require(a[0] == 0, 'EXPECTED_WA_LABEL')
            ai = a[1] - 2
            if b[0] == 0:
                expected = row['L'][ai] == b[1] - 2
            else:
                require(b[0] == 1, 'EXPECTED_WB_LABEL')
                expected = row['N'][ai] == (b[1] ^ 1) - 2
            require(literal_map[v] == expected, 'INDEPENDENT_MAPPING_FAILED')
            seen += 1
        require(seen == 132, 'UNIT_COUNT')
    findings['all_root_mappings'] = len(roots)
    # Full native positive controls: real srg(9,4,1,2), both normalization rules.
    small = directory / 'k4'
    build_base(small, k=4)
    row = {'L': [1, 0], 'N': [1, 0], 'd_plus': 1, 'd_minus': 1}
    for mode in ['R', 'MIN']:
        target = small / (mode + '.cnf')
        full(small / 'base.cnf', row, mode, target, k=4)
        output = small / (mode + '.log')
        require(run_native([ROOT / 'bin/solver', target], output) == 10, 'POSITIVE_CONTROL_NOT_SAT')
        verify_full(model_values(output), row, mode, k=4)
    findings['native_full_k4'] = 'SAT_AND_GRAPH_VERIFIED_BOTH_RULES'
    # Native negative control with proof checking; no full LOW search.
    bad = {'L': [2,3,0,1,5,4,7,6,9,8,11,10],
           'N': [3,2,1,0,5,4,7,6,9,8,11,10], 'd_plus':4, 'd_minus':4}
    negative = directory / 'invalid_X.cnf'
    interface(bad, negative)
    proof = directory / 'invalid_X.lrat'
    require(run_native([ROOT / 'bin/solver', '--lrat=1', negative, proof], directory / 'invalid_X.log') == 20, 'NEGATIVE_CONTROL_NOT_UNSAT')
    check_proof(negative, proof, directory)
    findings['invalid_X'] = 'UNSAT_CAKE_VERIFIED'
    # The same local contradiction in F0; conflicts/decisions forbidden.
    negative_full = directory / 'invalid_full.cnf'
    full(ROOT / 'work/base.cnf', bad, 'MIN', negative_full)
    proof_full = directory / 'invalid_full.lrat'
    rc = run_native([ROOT / 'bin/solver', '-c', '0', '-d', '0', '--lrat=1', negative_full, proof_full], directory / 'invalid_full.log')
    require(rc == 20, 'FULL_LOCAL_CONTRADICTION_NOT_RESOLVED_WITHOUT_SEARCH')
    check_proof(negative_full, proof_full, directory)
    findings['invalid_full_no_search'] = 'UNSAT_CAKE_VERIFIED'
    # k4 interface is empty: control covers boundary behavior only.
    xfile = directory / 'k4_X.cnf'
    meta = interface(row, xfile)
    out = directory / 'k4_X.log'
    require(run_native([ROOT / 'bin/solver', xfile], out) == 10, 'K4_X_CONTROL')
    verify_x(model_values(out), row, meta)
    findings['k4_X'] = 'SAT_EMPTY_INTERFACE_BOUNDARY_ONLY'
    test = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'], capture_output=True, text=True)
    (directory / 'runtime_tests.log').write_text(test.stdout + test.stderr)
    require(test.returncode == 0, 'RUNTIME_TESTS_FAILED')
    findings['runtime_tests'] = 'PASS'
    findings['status'] = 'PASS'
    findings['seconds'] = time.monotonic() - start
    findings['limitations'] = ['No known positive 99-vertex instance.', 'No production LOW SAT search or runtime forecast.',
                               'WSL host telemetry must additionally pass on target machine.']
    save(ROOT / 'work/validation.json', findings)
    print(json.dumps(findings, indent=2))


if __name__ == '__main__':
    controls()
