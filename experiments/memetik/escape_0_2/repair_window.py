"""Explicit induced H windows; exact Omega repair, no symmetry assumptions."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
import ortools
from ortools.sat.python import cp_model
from core import OUTER, decode_g6, reconstruct, encode_g6, validate, apply_move
from search import independent, short


def solve(founder, excluded, size, seconds):
    old = decode_g6(founder['graph6'])
    others = [decode_g6(g) for g in excluded]
    touched = {u for u in range(84) if any(old[u+15] != graph[u+15] for graph in others)}
    remaining = sorted(set(range(84)) - touched)
    random.Random(20260916).shuffle(remaining)
    window = sorted(touched | set(remaining[:max(0, size-len(touched))]))
    model = cp_model.CpModel()
    variables = {(i,j): model.new_bool_var(f'h_{i}_{j}') for i in window for j in window if i < j}
    def value(i,j):
        if i == j:
            return 0
        return variables.get((min(i,j),max(i,j)), int(bool(old[i+15] & (1 << (j+15)))))
    for u in window:
        for a in range(14):
            target = 1 if a in OUTER[u] or (a+7)%14 in OUTER[u] else 2
            model.add(sum(value(u,v) for v in range(84) if a in OUTER[v]) == target)
    for graph in others:
        assert all(graph[u+15] == old[u+15] for u in range(84) if u not in window)
        model.add(sum(1-x if graph[i+15] & (1 << (j+15)) else x for (i,j),x in variables.items()) >= 1)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = 20260916
    started = time.monotonic()
    status = solver.solve(model)
    result = {'solver':'ortools '+ortools.__version__, 'source_graph6':founder['graph6'], 'window_outer_indices':window, 'variables':len(variables), 'excluded_graph6':excluded, 'solver_status':solver.status_name(status), 'wall_seconds':time.monotonic()-started, 'scope':'Only H edges with both endpoints in the listed window may change; all remaining edges fixed. Omega margins and eight exclusions; no symmetry constraints.', 'status':'NO_SOLUTION_IN_WINDOW_UNCERTIFIED' if status == cp_model.INFEASIBLE else 'UNKNOWN'}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        h = [row >> 15 for row in old[15:]]
        for (i,j),x in variables.items():
            if solver.value(x):
                h[i] |= 1 << j
                h[j] |= 1 << i
            else:
                h[i] &= ~(1 << j)
                h[j] &= ~(1 << i)
        child = reconstruct(h)
        validate(child,'omega')
        assert short(child) == independent(child)
        g6 = encode_g6(child)
        assert g6 not in excluded
        removed = [(i,j) for i in range(99) for j in range(i+1,99) if old[i] & (1 << j) and not child[i] & (1 << j)]
        added = [(i,j) for i in range(99) for j in range(i+1,99) if child[i] & (1 << j) and not old[i] & (1 << j)]
        assert apply_move(old,(tuple(removed),tuple(added))) == child
        result.update(status='OUTSIDE_OLD_COMPONENT',graph6=g6,sha256=hashlib.sha256((g6+'\n').encode()).hexdigest(),deleted=removed,added=added,metrics=short(child),toggled_edges=len(removed)+len(added),minimum_trade_size_proven=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--component',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=30)
    args = parser.parse_args()
    founder = next(f for f in json.loads((Path(__file__).parent/'founders.json').read_text()) if f['id']=='A_legacy')
    excluded = [n['graph6'] for n in json.loads(args.component.read_text())['nodes']]
    results = []
    for size in (24,32,40,48,64):
        result = solve(founder,excluded,size,args.seconds)
        results.append(result)
        args.output.write_text(json.dumps(results,indent=4)+'\n')
        print({k:result[k] for k in ('variables','solver_status','wall_seconds','status')},flush=True)
        if result['status']=='OUTSIDE_OLD_COMPONENT':
            print(result['metrics'], result['toggled_edges'],flush=True)
            break


if __name__ == '__main__':
    main()
