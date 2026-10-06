"""One independently encoded single-row impossibility certificate per prefix.

Only explicit prefix rows, target symmetry, border margins and pair equations.
No saved propagation assignments, RowProposal, historical encoder or star witnesses.
"""
import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4
from rup_check import verify
from widths import save


def encode(data, target):
    labels = [set(p) for p in itertools.combinations(range(14), 2) if p[1] - p[0] != 7]
    assert data['labels'] == [sorted(p) for p in labels]
    rows = {int(u): set(vs) for u, vs in data['rows'].items()}
    assert target not in rows
    pool = IDPool(start_from=85)
    cnf = CNF()
    equations = []
    cnf.append([-(target + 1)])
    for u, neighbors in rows.items():
        cnf.append([u + 1 if target in neighbors else -(u + 1)])
    special = labels[target] | {(a + 7) % 14 for a in labels[target]}
    for c in range(14):
        equations.append(([w for w in range(84) if c in labels[w]], 1 if c in special else 2))
    for u, neighbors in sorted(rows.items()):
        equations.append((sorted(neighbors), 2 - int(target in neighbors) - len(labels[u] & labels[target])))
    for vertices, rhs in equations:
        if rhs < 0 or rhs > len(vertices):
            cnf.append([])
        else:
            cnf.extend(CardEnc.equals(lits=[v + 1 for v in vertices], bound=rhs,
                                     vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf, equations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    prefixes = args.repo / 'docs/augmentation/root8105_prefix_audit_20261006'
    output = args.output or args.repo / 'docs/augmentation/root8105_frontier_20261006'
    for path in sorted(output.glob('*_widths.json')):
        widths = json.loads(path.read_text())
        if not widths['complete']:
            continue
        name = widths['prefix']
        destination = output / (name + '_exclusion.json')
        if destination.exists():
            continue
        data = json.loads((prefixes / (name + '.json')).read_text())
        assert hashlib.sha256((prefixes / (name + '.json')).read_bytes()).hexdigest() == widths['input_sha256']
        attempts = []
        started = time.process_time()
        for target in sorted(r['target'] for r in widths['results'] if r['proposal_width'] == 0):
            cnf, equations = encode(data, target)
            with Glucose4(bootstrap_with=cnf.clauses, with_proof=True) as solver:
                sat = solver.solve()
                proof = solver.get_proof() if not sat else None
            attempts.append({'target': target, 'single_row_relaxation': 'SAT' if sat else 'UNSAT'})
            if sat:
                continue
            cnf_path = output / (name + '_t%02d.cnf' % target)
            proof_path = output / (name + '_t%02d.rup' % target)
            cnf.to_file(str(cnf_path))
            proof_path.write_text('\n'.join(proof) + '\n')
            verified = verify(cnf_path, proof_path)
            report = {'prefix': name, 'target': target, 'status': verified['status'],
                      'scope': 'this fixed labeled 13-row prefix has no full SRG completion; not its root class',
                      'model': 'one row: symmetry, 14 border margins, 13 built-row pair equations',
                      'saved_propagation_used': False, 'historical_encoder_used': False,
                      'star_witness_used': False, 'attempts': attempts, 'cnf': cnf_path.name,
                      'proof': proof_path.name, 'proof_check': verified,
                      'equations': [{'vertices': vs, 'rhs': rhs} for vs, rhs in equations],
                      'cpu_s': time.process_time() - started}
            save(destination, report)
            print(json.dumps({k:report[k] for k in ['prefix','target','status','cpu_s']}), flush=True)
            break
        else:
            print(json.dumps({'prefix':name,'status':'NO_SINGLE_ROW_CERTIFICATE_FOUND','attempts':attempts}),flush=True)


if __name__ == '__main__':
    main()
