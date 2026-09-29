"""One repair attempt. Durable incumbent; restart, not solver-state continuation."""
import argparse
import math
import resource
import signal
import threading
import time
from common import *

STOP = threading.Event()
SOLVER = None


def stop(*args):
    STOP.set()
    if SOLVER is not None:
        SOLVER.stop_search()


def evaluate_assignment(model, hints, guard=None):
    """Evaluate every proto constraint at a complete assignment, without solving."""
    def expression(e):
        return e.offset + sum(c * hints[v] for v, c in zip(e.vars, e.coeffs))
    for i, var in enumerate(model.proto.variables):
        value = hints[i]
        assert any(lo <= value <= hi for lo, hi in zip(var.domain[::2], var.domain[1::2]))
    for count, constraint in enumerate(model.proto.constraints):
        if guard is not None and count % 1000 == 0:
            guard()
        if any((hints[x] if x >= 0 else 1 - hints[-x - 1]) == 0 for x in constraint.enforcement_literal):
            continue
        kind = constraint.WhichOneof('constraint')
        if kind == 'linear':
            c = constraint.linear
            value = sum(a * hints[v] for v, a in zip(c.vars, c.coeffs))
            assert any(lo <= value <= hi for lo, hi in zip(c.domain[::2], c.domain[1::2]))
        elif kind == 'bool_or':
            assert any(hints[x] if x >= 0 else 1 - hints[-x - 1] for x in constraint.bool_or.literals)
        elif kind == 'lin_max':
            c = constraint.lin_max
            assert expression(c.target) == max(expression(e) for e in c.exprs)
        else:
            raise AssertionError('Uncovered constraint: ' + str(kind))


def solve_task(founder, task, directory, allowance, degree=14, lam=1, target=2, seed=1, stop_cpu=None):
    global SOLVER
    STOP.clear()
    SOLVER = None
    from ortools.sat.python import cp_model
    from model import build, extract
    from verify import checked, record, encode, key, task_check
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    configured_seed = task.get('seed', seed)
    linearization = task.get('linearization_level', 2)
    if type(configured_seed) is not int or not 0 <= configured_seed <= 2147483647:
        raise ValueError('Invalid task seed')
    if type(linearization) is not int or linearization not in (0, 2):
        raise ValueError('linearization_level must be 0 or 2')
    parameters = {'degree': degree, 'lam': lam, 'target': target}
    rows, base_scores = checked(founder['graph6'], **parameters)
    bestpath = directory / 'best.json'
    best = read(bestpath) if bestpath.exists() else record(founder['graph6'], **parameters)
    hint_rows, best_scores = checked(best['graph6'], **parameters)
    assert best_scores == best['scores'] and key(best_scores) <= key(base_scores)
    task_check(best['graph6'], founder['graph6'], task, **parameters)
    atomic(bestpath, best)
    started = cpu()
    stop_cpu = max(0.0, allowance - 10) if stop_cpu is None else stop_cpu
    timings = {'build_started_cpu': started, 'soft_target_cpu': stop_cpu, 'hard_reservation_cpu': allowance}
    def guard():
        if STOP.is_set() or cpu() >= stop_cpu:
            raise InterruptedError('CPU_OR_PAUSE_DURING_MODEL')

    try:
        guard()
        model, edges, objective, multiplier, hints = build(rows, task.get('vertices', []), hint_rows, guard=guard, edge_mask=task.get('edge_mask'), radius=task.get('radius'), **parameters)
        model.add(objective <= multiplier * best_scores['W'] + best_scores['L1'])
        evaluate_assignment(model, hints, guard=guard)
    except InterruptedError:
        return {'status': 'INTERRUPTED_DURING_BUILD', 'best': best, 'process_cpu_seconds': cpu(), 'timings': timings}
    model_bytes = model.proto.ByteSize()
    atomic(directory / 'model.json', {'variables': len(model.proto.variables), 'constraints': len(model.proto.constraints),
                                     'proto_bytes': model_bytes, 'build_cpu_seconds': cpu() - started,
                                     'complete_hint_checked': True, 'objective_multiplier': multiplier,
                                     'seed': configured_seed, 'linearization_level': linearization,
                                     'radius': task.get('radius'), 'distance_center': founder.get('state', hashlib.sha256(founder['graph6'].encode()).hexdigest())})
    if STOP.is_set():
        return {'status': 'INTERRUPTED_DURING_BUILD', 'best': best}

    class Save(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            nonlocal best
            graph = encode(extract(rows, edges, self.value))
            candidate = record(graph, **parameters)
            task_check(graph, founder['graph6'], task, **parameters)
            expected = multiplier * candidate['scores']['W'] + candidate['scores']['L1']
            if abs(self.objective_value - expected) > 0.1:
                raise RuntimeError('Solver objective disagrees with independent scorer')
            if key(candidate['scores']) < key(best['scores']):
                candidate['found_at_process_cpu_seconds'] = cpu()
                best = candidate
                atomic(bestpath, best)
                atomic(directory / ('candidate_' + candidate['state'] + '.json'), candidate)
            if STOP.is_set():
                self.stop_search()

    SOLVER = cp_model.CpSolver()
    SOLVER.parameters.num_search_workers = 1
    SOLVER.parameters.random_seed = configured_seed
    SOLVER.parameters.linearization_level = linearization
    SOLVER.parameters.log_search_progress = True
    # No WSL wall clock limit: CPU watchdog and parent Windows clock enforce limits.
    remaining_cpu = max(0.0, stop_cpu - cpu())
    deadline = cpu() + remaining_cpu

    def watch():
        while not STOP.wait(0.1):
            if cpu() >= deadline:
                stop()
                return

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    timings['solver_started_cpu'] = cpu()
    status = SOLVER.solve(model, Save()) if remaining_cpu > 0 else cp_model.UNKNOWN
    timings['solver_returned_cpu'] = cpu()
    STOP.set()
    watcher.join(timeout=1)
    names = {cp_model.OPTIMAL: 'OPTIMAL_UNCERTIFIED', cp_model.FEASIBLE: 'FEASIBLE_CPU_OR_PAUSE',
             cp_model.UNKNOWN: 'UNKNOWN_CPU_OR_PAUSE', cp_model.INFEASIBLE: 'ERROR_INFEASIBLE_START_EXISTS',
             cp_model.MODEL_INVALID: 'ERROR_MODEL_INVALID'}
    result = {'status': names[status], 'best': best, 'process_cpu_seconds': cpu(),
              'bound': SOLVER.best_objective_bound if remaining_cpu > 0 else None,
              'objective_multiplier': multiplier, 'proof_certificate': None,
              'timings': timings,
              'note': 'CP-SAT optimality/bounds are solver reports, not independently certified exclusions.'}
    if status in (cp_model.MODEL_INVALID, cp_model.INFEASIBLE):
        raise RuntimeError(result['status'])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=Path)
    parser.add_argument('directory', type=Path)
    parser.add_argument('allowance', type=float)
    parser.add_argument('--stop-cpu', type=float)
    args = parser.parse_args()
    hard = max(1, math.floor(args.allowance - 2))
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, hard - 3), hard))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGXCPU, stop)
    task = read(args.task)
    manifest = read(HERE / 'MANIFEST.json')
    founder = next(g for g in manifest['founders'] if g['id'] == task['founder'])
    try:
        result = solve_task(founder, task, args.directory, args.allowance,
                            seed=int(hashlib.sha256(task['id'].encode()).hexdigest()[:7], 16), stop_cpu=args.stop_cpu)
        result['process_cpu_seconds'] = cpu()
        result['proc_cpu_seconds'] = process(os.getpid())['cpu']
        result['python_process_time_seconds'] = time.process_time()
        atomic(args.directory / 'result.json', result)
    except BaseException as error:
        atomic(args.directory / 'error.json', {'error': repr(error), 'cpu_seconds': cpu()})
        raise


if __name__ == '__main__':
    main()
