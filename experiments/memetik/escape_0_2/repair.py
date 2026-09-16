"""Bounded exact Omega repair with all H edges free and eight exclusions."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from ortools.sat.python import cp_model
import ortools
from core import OUTER, decode_g6, encode_g6, reconstruct, validate, metrics, apply_move


def repair(founder, excluded, max_toggles, seconds, hints=True, hint_graph6=None, minimize=False):
    start = decode_g6(founder['graph6'])
    model = cp_model.CpModel()
    variables = {(i, j): model.new_bool_var(f'h_{i}_{j}') for i in range(84) for j in range(i + 1, 84)}
    def var(i, j):
        return variables[min(i, j), max(i, j)]
    for u, pair in enumerate(OUTER):
        model.add(sum(var(u, v) for v in range(84) if v != u) == 12)
        for a in range(14):
            target = 1 if a in pair or (a + 7) % 14 in pair else 2
            model.add(sum(var(u, v) for v, label in enumerate(OUTER) if v != u and a in label) == target)
    changes = [1 - x if start[i + 15] & (1 << (j + 15)) else x for (i, j), x in variables.items()]
    model.add(sum(changes) <= max_toggles)
    for g6 in excluded:
        old = decode_g6(g6)
        model.add(sum(1 - x if old[i + 15] & (1 << (j + 15)) else x for (i, j), x in variables.items()) >= 1)
    # Feasibility only: no optimization or unrequested symmetry constraints.
    if hints:
        hint = decode_g6(hint_graph6) if hint_graph6 else start
        for (i, j), x in variables.items():
            model.add_hint(x, int(bool(hint[i + 15] & (1 << (j + 15)))))
    if minimize:
        model.minimize(sum(changes))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 20260916
    then = time.monotonic()
    status = solver.solve(model)
    result = {'solver': 'ortools ' + ortools.__version__, 'solver_status': solver.status_name(status),
              'wall_seconds': time.monotonic() - then, 'max_toggled_edges': max_toggles,
              'excluded_graph6': excluded, 'source_graph6': founder['graph6'],
              'variables': len(variables), 'hints': hints, 'hint_graph6': hint_graph6, 'minimize_changes': minimize, 'scope': 'All H edge variables, fixed canonical frame, Omega only, at most max_toggled_edges differences from A.',
              'negative_proof_certified': False}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        h = [0] * 84
        for (i, j), x in variables.items():
            if solver.value(x):
                h[i] |= 1 << j
                h[j] |= 1 << i
        child = reconstruct(h)
        validate(child, 'omega')
        g6 = encode_g6(child)
        assert g6 not in excluded
        deleted = [(i, j) for i in range(99) for j in range(i + 1, 99) if start[i] & (1 << j) and not child[i] & (1 << j)]
        added = [(i, j) for i in range(99) for j in range(i + 1, 99) if child[i] & (1 << j) and not start[i] & (1 << j)]
        assert len(deleted) + len(added) <= max_toggles
        assert apply_move(start, (tuple(deleted), tuple(added))) == child
        result.update(status='OUTSIDE_OLD_COMPONENT', graph6=g6, sha256=hashlib.sha256((g6 + '\n').encode()).hexdigest(), deleted=deleted, added=added, metrics=metrics(child), path_length_new_operator=1, minimum_trade_size_proven=False)
    else:
        result['status'] = 'NO_SOLUTION_WITHIN_BOUND_UNCERTIFIED' if status == cp_model.INFEASIBLE else 'UNKNOWN'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--component', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-toggles', type=int, default=64)
    parser.add_argument('--seconds', type=float, default=120)
    parser.add_argument('--no-hints', action='store_true')
    parser.add_argument('--hint-file', type=Path)
    parser.add_argument('--minimize-changes', action='store_true')
    args = parser.parse_args()
    founders = json.loads((Path(__file__).parent / 'founders.json').read_text())
    founder = next(x for x in founders if x['id'] == 'A_legacy')
    excluded = [n['graph6'] for n in json.loads(args.component.read_text())['nodes']]
    assert len(set(excluded)) == 8
    result = repair(founder, excluded, args.max_toggles, args.seconds, not args.no_hints, args.hint_file.read_text().strip() if args.hint_file else None, args.minimize_changes)
    args.output.write_text(json.dumps(result, indent=4) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('excluded_graph6', 'source_graph6', 'graph6', 'deleted', 'added', 'metrics', 'hint_graph6')}))
    if 'metrics' in result:
        print({k: result['metrics'][k] for k in ('W', 'L1', 'F', 'Linf', 'Nmax')})


if __name__ == '__main__':
    main()
