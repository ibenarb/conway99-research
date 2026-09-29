"""Small independent K1 mask/radius and real founder/witness controls."""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

from model import build, extract
from verify import checked, encode, mask_check, task_check
from worker import evaluate_assignment, solve_task
from common import cpu
from ortools.sat.python import cp_model


def require_failure(fn):
    try:
        fn()
    except (ValueError, AssertionError):
        return
    raise AssertionError('Expected rejection')


def triangles(parts):
    rows = [set() for _ in range(6)]
    for part in parts:
        for u in part:
            rows[u].update(v for v in part if v != u)
    return rows


def main():
    a = triangles([(0, 1, 2), (3, 4, 5)])
    b = triangles([(0, 1, 3), (2, 4, 5)])
    ga, gb = encode(a), encode(b)
    params = dict(degree=2, lam=1, target=2)
    mask = [(u, v) for v in range(6) for u in range(v) if (v in a[u]) != (v in b[u])]
    distance = len(mask)
    for hint in (a, b):
        model, edges, objective, multiplier, hints = build(a, [], hint, edge_mask=mask, radius=distance, **params)
        evaluate_assignment(model, hints)
        mask_check(encode(hint), ga, mask, distance, **params)
        for level in (0, 2):
            solver = cp_model.CpSolver()
            solver.parameters.num_search_workers = 1
            solver.parameters.linearization_level = level
            assert solver.solve(model) == cp_model.OPTIMAL
            mask_check(encode(extract(a, edges, solver.value)), ga, mask, distance, **params)
    require_failure(lambda: mask_check(gb, ga, mask[:-1], distance, **params))
    require_failure(lambda: mask_check(gb, ga, mask, distance - 1, **params))
    m, _, _, _, h = build(a, [], b, edge_mask=mask, radius=distance - 1, **params)
    require_failure(lambda: evaluate_assignment(m, h))
    for bad in ([[1, 0]], [[0, 0]], [[0, 6]], [[0, 1], [0, 1]]):
        require_failure(lambda: build(a, [], edge_mask=bad, **params))
        require_failure(lambda: mask_check(ga, ga, bad, **params))
    for level in (0, 2):
        with tempfile.TemporaryDirectory() as directory:
            task = {'edge_mask': mask, 'radius': distance, 'seed': 1234, 'linearization_level': level}
            result = solve_task({'graph6': ga}, task, directory, cpu() + 30, stop_cpu=cpu() + 20, **params)
            assert result['status'] == 'OPTIMAL_UNCERTIFIED'
            task_check(result['best']['graph6'], ga, task, **params)
    witnesses = json.loads((HERE / 'STAR_WITNESSES.json').read_text())
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    witness = witnesses[0]
    founder = next(f for f in manifest['founders'] if f['state'] == witness['state'])
    original, _ = checked(founder['graph6'])
    alternate, _ = checked(witness['graph6'])
    difference = [(u, v) for v in range(99) for u in range(v) if (v in original[u]) != (v in alternate[u])]
    assert sorted(difference) == sorted(map(tuple, witness['changed']))
    for hint in (original, alternate):
        m, _, _, _, h = build(original, [], hint, edge_mask=difference)
        evaluate_assignment(m, h)
        mask_check(encode(hint), founder['graph6'], difference)
        solver = cp_model.CpSolver(); solver.parameters.num_search_workers = 1
        assert solver.solve(m) == cp_model.OPTIMAL
        assert solver.objective_value <= 50000 * witness['score'][0] + witness['score'][1]
    print(json.dumps({'status': 'PASS', 'small_mask_distance': distance, 'linearization_levels': [0, 2], 'C1_D_both_parents_complete_assignment': True, 'star_witness_distance': len(difference), 'negative_mask_and_radius_checks': True}))


if __name__ == '__main__':
    main()
