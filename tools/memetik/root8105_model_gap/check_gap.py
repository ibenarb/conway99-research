"""Targeted R / R+LD / R+LD+A diagnosis; immutable prefix, no new walks.

Uses the published independent R encoder and RUP checker. Direct witness
checks and assignment derivations use integer equations, not SAT auxiliaries.
"""
import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def geometry(data):
    labels = [set(p) for p in itertools.combinations(range(14), 2) if p[1] - p[0] != 7]
    assert data['labels'] == [sorted(p) for p in labels]
    rows = {int(u): set(vs) for u, vs in data['rows'].items()}
    return labels, rows


def ld_edges(labels, rows):
    """Both historical LD rules, with explicit necessary-condition origins."""
    result = {}
    for u, ns in sorted(rows.items()):
        for v in sorted(ns):
            if labels[u] & labels[v]:
                for w in sorted(ns - {v}):
                    pair = tuple(sorted((v, w)))
                    result.setdefault(pair, []).append(['zero_codegree', u, v])
        for v, w in itertools.combinations(sorted(ns), 2):
            if labels[v] & labels[w]:
                result.setdefault((v, w), []).append(['two_known_common_neighbors', u, min(labels[v] & labels[w])])
    return result


def derive_assignments(data):
    """Independent saturation from full prefix, with no saved A as premises.

Every inference names a necessary equality or a directly derived LD zero.
The original propagation's matching-singleton deductions are already degree
one equalities in these stars/fibres; feasibility tests add no assignments.
"""
    labels, rows = geometry(data)
    fixed = {}
    trace = []
    def impose(u, v, bit, reason):
        pair = tuple(sorted((u, v)))
        if pair in fixed:
            assert fixed[pair] == bit, (pair, reason)
            return False
        fixed[pair] = bit
        trace.append({'pair': pair, 'value': bit, 'reason': reason})
        return True
    for u in range(84):
        impose(u, u, 0, ['diagonal'])
    for u, ns in sorted(rows.items()):
        for v in range(84):
            impose(u, v, int(v in ns), ['prefix', u])
    for (u, v), reasons in sorted(ld_edges(labels, rows).items()):
        impose(u, v, 0, reasons[0])
    equations = []
    for t in range(84):
        if t in rows:
            continue
        special = labels[t] | {(c + 7) % 14 for c in labels[t]}
        equations.append((t, list(range(84)), 12, ['degree', t]))
        for c in range(14):
            equations.append((t, [v for v in range(84) if c in labels[v]],
                              1 if c in special else 2, ['border', t, c]))
        for u, ns in sorted(rows.items()):
            equations.append((t, sorted(ns), 2 - int(t in ns) - len(labels[t] & labels[u]), ['pair', t, u]))
    changed = True
    while changed:
        changed = False
        for t, vs, rhs, reason in equations:
            pairs = [tuple(sorted((t, v))) for v in vs]
            ones = sum(fixed.get(p) == 1 for p in pairs)
            free = [p for p in pairs if p not in fixed]
            assert ones <= rhs <= ones + len(free), (reason, ones, rhs, len(free))
            if free and (rhs == ones or rhs == ones + len(free)):
                for u, v in free:
                    changed |= impose(u, v, int(rhs > ones), reason)
    missing = []
    for u, v, bit in data['assignments']:
        pair = tuple(sorted((u, v)))
        if pair not in fixed:
            missing.append([u, v, bit])
        else:
            assert fixed[pair] == bit
    return {'saved_count': len(data['assignments']), 'missing': missing,
            'derived_without_saved_A': not missing, 'trace': trace}


def direct_check(data, target, selected, mode):
    labels, rows = geometry(data)
    x = set(selected)
    assert target not in x and len(x) == 12
    assert all((u in x) == (target in ns) for u, ns in rows.items())
    special = labels[target] | {(c + 7) % 14 for c in labels[target]}
    margins = [sum(c in labels[v] for v in x) for c in range(14)]
    assert margins == [1 if c in special else 2 for c in range(14)]
    pairs = {u: len(x & ns) for u, ns in rows.items()}
    assert all(pairs[u] == 2 - int(target in ns) - len(labels[u] & labels[target]) for u, ns in rows.items())
    ld_violations = [[u, v] for u, v in ld_edges(labels, rows)
                     if target in (u, v) and (v if u == target else u) in x]
    a_violations = [[u, v, b] for u, v, b in data['assignments']
                    if target in (u, v) and int((v if u == target else u) in x) != b]
    if mode != 'R':
        assert not ld_violations
    if mode == 'R_LD_A':
        assert not a_violations
    return {'status': 'DIRECT_INTEGER_CHECK_PASS', 'degree': len(x), 'margins': margins,
            'pair_codegrees': pairs, 'LD_violations': ld_violations, 'A_violations': a_violations}


def run(repo, output):
    sys.path.insert(0, str(repo / 'tools/memetik/root8105_frontier'))
    from certify_dead import encode
    from rup_check import verify
    from pysat.solvers import Glucose4
    source = repo / 'docs/augmentation/root8105_prefix_audit_20261006/prefix_r6682_w290.json'
    data = json.loads(source.read_text())
    output.mkdir(parents=True, exist_ok=False)
    begun = time.process_time()
    derivation = derive_assignments(data)
    save(output / 'ASSIGNMENT_DERIVATION.json', derivation)
    assert derivation['derived_without_saved_A'], derivation['missing']
    labels, rows = geometry(data)
    results = []
    for target in (13, 15):
        for mode in ('R', 'R_LD', 'R_LD_A'):
            start = time.process_time()
            cnf, equations = encode(data, target)
            ld_units = []
            if mode != 'R':
                for u, v in sorted(ld_edges(labels, rows)):
                    if target in (u, v):
                        w = v if u == target else u
                        ld_units.append(-(w + 1))
                        cnf.append([-(w + 1)])
            a_units = []
            if mode == 'R_LD_A':
                for u, v, bit in data['assignments']:
                    if target in (u, v):
                        w = v if u == target else u
                        literal = w + 1 if bit else -(w + 1)
                        a_units.append(literal)
                        cnf.append([literal])
            stem = 't%02d_%s' % (target, mode)
            cnf_path = output / (stem + '.cnf')
            cnf.to_file(str(cnf_path))
            with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
                sat = solver.solve()
                model = solver.get_model() if sat else None
                proof = solver.get_proof() if not sat else None
                stats = solver.accum_stats()
            report = {'target': target, 'mode': mode, 'cnf': cnf_path.name,
                      'variables': cnf.nv, 'clauses': len(cnf.clauses), 'solver_stats': stats,
                      'LD_units': ld_units, 'A_units': a_units}
            if sat:
                selected = [v for v in range(84) if v + 1 in model]
                checked = direct_check(data, target, selected, mode)
                # Independently reject a deliberately damaged row.
                try:
                    direct_check(data, target, selected[:-1], mode)
                except AssertionError:
                    pass
                else:
                    raise AssertionError('damaged witness accepted')
                save(output / (stem + '_witness.json'), {'neighbors': selected, 'sat_model': model, 'check': checked})
                report.update(status='SAT_DIRECT_VERIFIED', witness=stem + '_witness.json', check=checked)
            else:
                proof_path = output / (stem + '.rup')
                # Loading contradiction can yield no solver additions. The
                # independent checker must then verify the empty clause itself.
                proof_path.write_text('\n'.join(proof or []) + '\n0\n')
                checked = verify(cnf_path, proof_path)
                report.update(status=checked['status'], proof=proof_path.name, check=checked)
            report['cpu_s'] = time.process_time() - start
            results.append(report)
            save(output / (stem + '_result.json'), report)
            print(json.dumps({'target': target, 'mode': mode, 'status': report['status'], 'cpu_s': report['cpu_s']}), flush=True)
    receipt = {'complete': True, 'base_commit': '84180ad8bffe6905b8384e4acf889879b85a3fa9',
               'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'results': results, 'cpu_s': time.process_time() - begun,
               'assignment_count': derivation['saved_count'], 'assignments_derived': True,
               'new_walks': 0, 'root_exclusions': 0,
               'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}}
    save(output / 'FINAL_RECEIPT.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.repo.resolve(), args.output.resolve())
