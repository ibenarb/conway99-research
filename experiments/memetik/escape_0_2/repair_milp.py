"""Independent sparse MILP formulation of minimum edge-change Omega repair."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import csc_matrix
from core import OUTER, decode_g6, encode_g6, reconstruct, validate, apply_move
from search import independent, short


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--component', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=120)
    args = parser.parse_args()
    founder = next(f for f in json.loads((Path(__file__).parent / 'founders.json').read_text()) if f['id'] == 'A_legacy')
    old = decode_g6(founder['graph6'])
    excluded = [n['graph6'] for n in json.loads(args.component.read_text())['nodes']]
    pairs = [(i, j) for i in range(84) for j in range(i + 1, 84)]
    rr, cc, vv = [], [], []
    lower, upper = [], []
    for u, label in enumerate(OUTER):
        for a in range(14):
            row = len(lower)
            target = 1 if a in label or (a + 7) % 14 in label else 2
            lower.append(target)
            upper.append(target)
            for k, (i, j) in enumerate(pairs):
                if i == u and a in OUTER[j] or j == u and a in OUTER[i]:
                    rr.append(row); cc.append(k); vv.append(1)
    # Summing the 14 margins yields 24, hence degree 12 automatically.
    for g6 in excluded:
        graph = decode_g6(g6)
        row = len(lower)
        present = [int(bool(graph[i + 15] & (1 << (j + 15)))) for i, j in pairs]
        lower.append(1 - sum(present))
        upper.append(np.inf)
        for k, bit in enumerate(present):
            rr.append(row); cc.append(k); vv.append(1 - 2 * bit)
    matrix = csc_matrix((vv, (rr, cc)), shape=(len(lower), len(pairs)), dtype=float)
    c = np.array([1 - 2 * int(bool(old[i + 15] & (1 << (j + 15)))) for i, j in pairs], dtype=float)
    started = time.monotonic()
    solution = milp(c, integrality=np.ones(len(pairs)), bounds=Bounds(0, 1), constraints=LinearConstraint(matrix, lower, upper), options={'time_limit': args.seconds, 'mip_rel_gap': 0})
    result = {'solver': 'scipy.milp ' + scipy.__version__, 'solver_status': int(solution.status), 'message': solution.message, 'wall_seconds': time.monotonic() - started, 'source_graph6': founder['graph6'], 'excluded_graph6': excluded, 'scope': 'All H edges free; exactly Omega margins; exclude eight known labelled states; minimize total toggled edges.', 'negative_proof_certified': False, 'status': 'UNKNOWN'}
    if solution.x is not None:
        assert max(abs(solution.x - np.rint(solution.x))) < 1e-5
        h = [0] * 84
        for (i, j), value in zip(pairs, np.rint(solution.x)):
            if value:
                h[i] |= 1 << j
                h[j] |= 1 << i
        child = reconstruct(h)
        validate(child, 'omega')
        assert short(child) == independent(child)
        g6 = encode_g6(child)
        assert g6 not in excluded
        deleted = [(i, j) for i in range(99) for j in range(i + 1, 99) if old[i] & (1 << j) and not child[i] & (1 << j)]
        added = [(i, j) for i in range(99) for j in range(i + 1, 99) if child[i] & (1 << j) and not old[i] & (1 << j)]
        assert apply_move(old, (tuple(deleted), tuple(added))) == child
        result.update(status='OUTSIDE_OLD_COMPONENT', graph6=g6, sha256=hashlib.sha256((g6 + '\n').encode()).hexdigest(), deleted=deleted, added=added, metrics=short(child), toggled_edges=len(deleted)+len(added), path_length_new_operator=1, solver_claims_optimal=solution.status == 0, exact_minimum_certified=False, mip_gap=float(solution.mip_gap))
    args.output.write_text(json.dumps(result, indent=4) + '\n')
    print({k:v for k,v in result.items() if k not in ('source_graph6', 'excluded_graph6', 'graph6', 'deleted', 'added')})


if __name__ == '__main__':
    main()
