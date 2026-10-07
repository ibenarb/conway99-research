"""N1 encoder controls and external DRAT verification; no class search."""
import argparse
import hashlib
import itertools
import json
import resource
import subprocess
import time
from pathlib import Path
from pysat.solvers import Glucose4
from model import encode, check, decode, labels_for


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def external(binary, cnf, proof, log):
    # Upstream -O disables the timeout; finite optimization fixpoint, no
    # imposed time budget and no modification of checking semantics.
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    begin = usage.ru_utime + usage.ru_stime
    result = subprocess.run([str(binary), str(cnf), str(proof), '-O'], text=True, capture_output=True)
    log.write_text(result.stdout + result.stderr)
    lines = result.stdout.replace('\r', '\n').splitlines()
    verified = 's VERIFIED' in lines and 's NOT VERIFIED' not in lines
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'verified': verified, 'returncode': result.returncode,
            'cpu_s': usage.ru_utime + usage.ru_stime - begin,
            'log': log.name, 'checker_sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}


def solve(m, rows, matching, output, name, checker):
    started = time.process_time()
    cnf, variables, meta = encode(m, rows, matching)
    cp, pp = output / (name + '.cnf'), output / (name + '.drat')
    cnf.to_file(str(cp))
    with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
        proof = solver.get_proof() if not sat else None
        stats = solver.accum_stats()
    result = {'name': name, 'metadata': meta, 'solver_stats': stats}
    if sat:
        witness = decode(m, rows, matching, variables, model)
        checked = check(m, rows, matching, witness)
        save(output / (name + '_witness.json'), witness)
        result.update(status='SAT_DIRECT_VERIFIED', check=checked)
    else:
        pp.write_text('\n'.join(proof or []) + '\n0\n')
        checked = external(checker, cp, pp, output / (name + '_drat_check.log'))
        assert checked['verified'], checked
        result.update(status='EXTERNAL_DRAT_VERIFIED_UNSAT', check=checked,
                      cnf_bytes=cp.stat().st_size, proof_bytes=pp.stat().st_size)
    result['parent_cpu_s'] = time.process_time() - started
    save(output / (name + '_result.json'), result)
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--checker', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = []
    # Explicit 3x3 rook graph; derive H labels through actual border adjacency.
    vertices = list(itertools.product(range(3), repeat=2))
    def adjacent(x, y):
        return x != y and (x[0] == y[0] or x[1] == y[1])
    for u in vertices:
        assert sum(adjacent(u, v) for v in vertices) == 4
        for v in vertices:
            if u != v:
                assert sum(adjacent(u, w) and adjacent(v, w) for w in vertices) == (1 if adjacent(u, v) else 2)
    border = [(0, 1), (1, 0), (0, 2), (2, 0)]
    outside = [v for v in vertices if v != (0, 0) and not adjacent(v, (0, 0))]
    mapped = {frozenset(i for i, b in enumerate(border) if adjacent(v, b)): v for v in outside}
    h = [mapped[frozenset(label)] for label in labels_for(2)]
    full = {u: {v for v in range(4) if adjacent(h[u], h[v])} for u in range(4)}
    results.append(solve(2, full, [], output, 'rook_fully_fixed', args.checker))
    root = {0: full[0]}
    results.append(solve(2, root, [], output, 'rook_free_N1', args.checker))
    cnf, variables, meta = encode(2, root, [])
    exhaustive = []
    for bits in itertools.product((0, 1), repeat=len(variables)):
        assumptions = [lit if bit else -lit for lit, bit in zip(variables.values(), bits)]
        with Glucose4(bootstrap_with=cnf.clauses) as solver:
            sat = solver.solve(assumptions=assumptions)
        witness = decode(2, root, [], variables, assumptions)
        try:
            check(2, root, [], witness)
            valid = True
        except (AssertionError, ValueError):
            valid = False
        assert sat == valid
        exhaustive.append({'bits': bits, 'CNF_SAT': sat, 'direct_valid': valid})
    assert sum(x['direct_valid'] for x in exhaustive) == 1
    save(output / 'ROOK_EXHAUSTIVE.json', {'metadata': meta, 'cases': exhaustive})
    # The external checker must reject a forged empty clause for satisfiable CNF.
    cp, pp = output / 'bad_control.cnf', output / 'bad_control.drat'
    cp.write_text('p cnf 1 1\n1 0\n')
    pp.write_text('0\n')
    invalid = external(args.checker, cp, pp, output / 'bad_control.log')
    assert not invalid['verified']
    save(output / 'EXTERNAL_NEGATIVE_CONTROL.json', invalid)
    prefix_dir = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    for path in sorted(prefix_dir.glob('prefix_*.json')):
        data = json.loads(path.read_text())
        rows = {int(u): set(ns) for u, ns in data['rows'].items()}
        result = solve(7, rows, data['matching'], output, path.stem, args.checker)
        assert result['status'] == 'EXTERNAL_DRAT_VERIFIED_UNSAT'
        result['input_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        results.append(result)
    assert len(results) == 19
    receipt = {'complete': True, 'results': results, 'rook_exhaustive_cases': len(exhaustive),
               'external_invalid_proof_rejected': True, 'class_searches': 0, 'root_exclusions': 0,
               'peak_parent_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'checker_source_commit': '2e3b2dc0ecf938addbd779d42877b6ed69d9a985',
               'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}}
    save(output / 'FINAL_RECEIPT.json', receipt)


if __name__ == '__main__':
    main()
