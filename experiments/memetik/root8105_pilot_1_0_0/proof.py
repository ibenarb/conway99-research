"""Independent DRAT check of one completed projected enumeration."""
import argparse
import hashlib
import json
import resource
import subprocess
import time
from pathlib import Path

from pysat.solvers import Glucose4
from core import Deadline, Geometry, atomic, encode, projection, unpack


def independent_unit_contradiction(clauses):
    assignment = {}
    while True:
        changed = False
        for clause in clauses:
            if any(assignment.get(abs(lit)) == (lit > 0) for lit in clause):
                continue
            undecided = [lit for lit in clause if abs(lit) not in assignment]
            if not undecided:
                return True
            if len(undecided) == 1:
                lit = undecided[0]
                assignment[abs(lit)] = lit > 0
                changed = True
        if not changed:
            return False


def certify(directory, checker, cpu_s=20, wall_s=120):
    directory = Path(directory)
    metadata = json.loads((directory / 'enumeration.json').read_text())
    if metadata['status'] != 'PROJECTED_ENUMERATION_COMPLETE':
        raise ValueError('censored enumeration cannot be certified complete')
    state = json.loads((directory / 'state.json').read_text())
    g = Geometry(state['m'])
    rows = unpack(state['rows'])
    target = state['target']
    cnf, variables = encode(g, rows, target)
    fixed, free = projection(g, rows, target, variables)
    raw = (directory / 'rows.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata['rows_sha256']:
        raise ValueError('projection digest mismatch')
    projections = [int(line, 16) for line in raw.splitlines()]
    if len(projections) != metadata['count'] or len(set(projections)) != len(projections):
        raise ValueError('projection count or duplicates')
    for row in projections:
        child = dict(rows)
        child[target] = row
        g.verify(child)
        if row & sum(1 << u for u in rows) != fixed:
            raise ValueError('projection fixed part mismatch')
        cnf.append([-lit if (row >> v) & 1 else lit for v, lit in free])
    formula = directory / 'closure.cnf'
    proof = directory / 'closure.drat'
    cnf.to_file(str(formula))
    start = time.process_time()
    with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
        with Deadline(solver, start + cpu_s, time.monotonic() + wall_s):
            result = solver.solve_limited(expect_interrupt=True)
        if result is not False:
            out = {'status': 'PROOF_LIMIT_UNKNOWN' if result is None else 'ENUMERATION_INVALID',
                   'certified': False}
            atomic(directory / 'certificate.json', out)
            return out
        proof.write_text('\n'.join(solver.get_proof()) + '\n')
    def checker_limit():
        resource.setrlimit(resource.RLIMIT_CPU, (20, 21))
    try:
        checked = subprocess.run([str(Path(checker).resolve()), str(formula), str(proof)],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=wall_s, preexec_fn=checker_limit)
        (directory / 'checker.log').write_bytes(checked.stdout)
        verified_line = b's VERIFIED' in [line.strip() for line in checked.stdout.splitlines()]
        trivial_exit_bug = (checked.returncode == 1 and verified_line and b'c trivial UNSAT' in checked.stdout
                            and independent_unit_contradiction(cnf.clauses))
        valid = verified_line and (checked.returncode == 0 or trivial_exit_bug)
        out = {'status': 'PROJECTED_COVERAGE_DRAT_VERIFIED' if valid else 'CHECKER_FAILED',
               'certified': valid, 'checker_exit': checked.returncode,
               'trivial_unsat_exit_bug_independently_checked': trivial_exit_bug,
               'cnf_sha256': hashlib.sha256(formula.read_bytes()).hexdigest(),
               'proof_sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
               'proof_bytes': proof.stat().st_size, 'cnf_bytes': formula.stat().st_size,
               'scope': 'No additional projected row in this relaxation; no root exclusion.'}
    except subprocess.TimeoutExpired as error:
        (directory / 'checker.log').write_bytes(error.stdout or b'')
        out = {'status': 'CHECKER_LIMIT_UNKNOWN', 'certified': False}
    atomic(directory / 'certificate.json', out)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('checker')
    ap.add_argument('--cpu', type=float, default=20)
    a = ap.parse_args()
    print(json.dumps(certify(a.directory, a.checker, a.cpu)), flush=True)
