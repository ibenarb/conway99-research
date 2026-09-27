"""Exhaustive small-graph oracle, all boundaries, and known N-to-A repair."""
import itertools
import sys
from common import *
from verify import checked, decode, encode, key


def small_controls():
    from model import build, extract
    from worker import evaluate_assignment
    from ortools.sat.python import cp_model
    n = 6
    pairs = [(u, v) for v in range(n) for u in range(v)]
    results = []
    for lam in (0, 1):
        rows = ([{(u-1) % n, (u+1) % n} for u in range(n)] if lam == 0 else
                [set(range(3 * (u // 3), 3 * (u // 3) + 3)) - {u} for u in range(n)])
        legal = {}
        for chosen in itertools.combinations(pairs, 6):
            graph = [set() for _ in range(n)]
            for u, v in chosen:
                graph[u].add(v)
                graph[v].add(u)
            try:
                text = encode(graph)
                _, scores = checked(text, degree=2, lam=lam)
                legal[text] = scores
            except ValueError:
                pass
        assert len(legal) == (60 if lam == 0 else 10)
        for window in ([0, 1, 2], [0, 1, 2, 3], list(range(6))):
            expected = {g: s for g, s in legal.items() if all(
                (u in decode(g)[v]) == (u in rows[v]) for u, v in pairs if not (u in window and v in window))}
            model, edges, objective, weight, hints = build(rows, window, degree=2, lam=lam)
            evaluate_assignment(model, hints)
            solver = cp_model.CpSolver()
            solver.parameters.num_search_workers = 1
            assert solver.solve(model) == cp_model.OPTIMAL
            optimum = min(weight*s['W'] + s['L1'] for s in expected.values())
            assert round(solver.objective_value) == optimum
            model.clear_objective()
            found = {}

            class Collect(cp_model.CpSolverSolutionCallback):
                def on_solution_callback(self):
                    text = encode(extract(rows, edges, self.value))
                    _, score = checked(text, degree=2, lam=lam)
                    assert text in expected and score == expected[text]
                    found[text] = score

            solver.parameters.enumerate_all_solutions = True
            assert solver.solve(model, Collect()) == cp_model.OPTIMAL
            assert found == expected
            results.append({'lambda': lam, 'size': len(window), 'labelled_graphs': len(found), 'objective': optimum})
    return results


def main(directory):
    from boundary import propagate
    from worker import solve_task
    from model import build
    from worker import evaluate_assignment
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = read(HERE / 'MANIFEST.json')
    roots = {g['id']: g for g in manifest['founders']}
    for founder in roots.values():
        _, actual = checked(founder['graph6'])
        assert actual == founder['scores']
        assert hashlib.sha256(founder['graph6'].encode()).hexdigest() == founder['state']
    small = small_controls()
    published = {x['id']: x for x in read(HERE / 'BOUNDARY_CHECK.json')['tasks']}
    boundaries = {}
    for task in manifest['tasks']:
        rows = decode(roots[task['founder']]['graph6'])
        proof = propagate(rows, task['vertices'])
        assert proof['unfixed'] == published[task['id']]['unfixed_after_necessary_propagation']
        boundaries[task['id']] = {'rigid': proof['rigid'], 'unfixed': proof['unfixed']}
        if proof['rigid']:
            atomic(directory / ('boundary_' + task['id'] + '.json'), proof)
    # Verify complete seed assignments at representative sizes before release to workers.
    for size in (24, 40, 60):
        task = next(t for t in manifest['tasks'] if t['size'] == size)
        m, _, _, _, hints = build(decode(roots[task['founder']]['graph6']), task['vertices'])
        evaluate_assignment(m, hints)
    near = next(g for g in roots.values() if g['state'] == 'e1edc9cb193240624c35e8a2fe0502f523349ec3b828ea31d6316c467a3ea72d')
    target = roots['2076_01']
    carrier = [3, 26, 31, 33, 42, 66, 71, 72]
    # Optimize the near graph without constraining target edges.
    control_task = {'id': 'positive_N_to_A', 'vertices': carrier}
    result = solve_task(near, control_task, directory / 'positive', cpu() + 120)
    assert key(result['best']['scores']) < key(near['scores'])
    assert result['best']['scores']['W'] <= 2076
    # Separately check the exact known witness under all frozen edges.
    from verify import window_check
    assert window_check(target['graph6'], near['graph6'], carrier) == target['scores']
    output = {'status': 'PASS', 'small_exhaustive': small, 'founders': 24, 'boundaries': boundaries,
              'positive_control': result, 'cpu_seconds': cpu()}
    atomic(directory / 'result.json', output)
    print('REPAIR_CONTROLS_PASS', flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
