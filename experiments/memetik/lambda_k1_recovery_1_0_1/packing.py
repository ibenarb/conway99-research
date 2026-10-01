"""C2 packing arms. No packing is represented as a valid lambda candidate.

CPU ceilings are absolute RUSAGE_SELF seconds, as in repair worker.py.
Projection is greedy deletion: its deficit is an achieved upper bound on
minimum deletions, never an optimality certificate. Restart resumes best
incumbents, not RNG/tabu/search state; the caller accounts every attempt.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import resource


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def atomic(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    with temporary.open('w', encoding='utf-8') as output:
        json.dump(data, output, sort_keys=True, indent=2, allow_nan=False)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    descriptor = os.open(str(path.parent), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def decode(graph6):
    values = [ord(c) - 63 for c in graph6.strip()]
    if not values or any(v < 0 or v > 63 for v in values):
        raise ValueError('Invalid graph6')
    if values[0] == 63:
        if len(values) < 4:
            raise ValueError('Short graph6 header')
        n = (values[1] << 12) | (values[2] << 6) | values[3]
        values = values[4:]
    else:
        n, values = values[0], values[1:]
    if not 1 <= n <= 99 or len(values) != (n * (n - 1) // 2 + 5) // 6:
        raise ValueError('Invalid graph6 size')
    rows = [0] * n
    position = 0
    for v in range(n):
        for u in range(v):
            if values[position // 6] & (1 << (5 - position % 6)):
                rows[u] |= 1 << v
                rows[v] |= 1 << u
            position += 1
    if position % 6 and values[-1] & ((1 << (6 - position % 6)) - 1):
        raise ValueError('Nonzero graph6 padding')
    return rows


def encode(rows):
    n = len(rows)
    values = [n] if n < 63 else [63, (n >> 12) & 63, (n >> 6) & 63, n & 63]
    bits = [int(bool(rows[u] & (1 << v))) for v in range(n) for u in range(v)]
    bits += [0] * (-len(bits) % 6)
    values.extend(sum(bits[i + j] << (5 - j) for j in range(6)) for i in range(0, len(bits), 6))
    return ''.join(chr(value + 63) for value in values)


def simple_check(rows):
    n = len(rows)
    if not 1 <= n <= 99:
        raise ValueError('Invalid graph size')
    for u, row in enumerate(rows):
        if type(row) is not int or row < 0 or row >> n or row & (1 << u):
            raise ValueError('Invalid adjacency row')
        for v in range(u):
            if bool(row & (1 << v)) != bool(rows[v] & (1 << u)):
                raise ValueError('Asymmetric adjacency')


def packing_check(value, degree=14):
    """Independent exhaustive set-based check, separate from fast add test."""
    rows = decode(value) if isinstance(value, str) else list(value)
    simple_check(rows)
    adjacency = [set(vertices(row)) for row in rows]
    if any(len(row) > degree for row in adjacency):
        raise ValueError('Packing degree exceeded')
    for u in range(len(rows)):
        for v in range(u):
            count = len(adjacency[u].intersection(adjacency[v]))
            if count > (1 if v in adjacency[u] else 2):
                raise ValueError('Packing common-neighbor bound exceeded')
    edges = sum(map(len, adjacency)) // 2
    return {'edges': edges, 'deficit': len(rows) * degree // 2 - edges}


def packing_record(value, degree=14):
    rows = decode(value) if isinstance(value, str) else list(value)
    scores = packing_check(rows, degree)
    graph6 = encode(rows)
    return {'kind': 'packing', 'graph6': graph6, 'state': hashlib.sha256(graph6.encode()).hexdigest(),
            'scores': scores, 'n': len(rows), 'degree_ceiling': degree,
            'claim': 'validated packing; deficit is not an exact minimum deletion count'}


def lambda_record(rows, degree=14):
    simple_check(rows)
    if any(row.bit_count() != degree for row in rows):
        raise ValueError('Lambda degree violated')
    w = l1 = 0
    for u in range(len(rows)):
        for v in range(u):
            edge = int(bool(rows[u] & (1 << v)))
            common = (rows[u] & rows[v]).bit_count()
            if edge and common != 1:
                raise ValueError('Lambda violated')
            residual = common + edge - 2
            w += residual != 0
            l1 += abs(residual)
    graph6 = encode(rows)
    return {'kind': 'lambda_parent', 'graph6': graph6,
            'state': hashlib.sha256(graph6.encode()).hexdigest(), 'scores': {'W': w, 'L1': l1}}


def add_allowed(rows, u, v, degree=14):
    """Exact affected-pair test, assuming input is a valid packing."""
    if u == v or rows[u] & (1 << v):
        return False
    if rows[u].bit_count() >= degree or rows[v].bit_count() >= degree:
        return False
    if (rows[u] & rows[v]).bit_count() > 1:
        return False
    for a, b in ((u, v), (v, u)):
        for x in vertices(rows[b]):
            cap = 1 if rows[a] & (1 << x) else 2
            if (rows[a] & rows[x]).bit_count() + 1 > cap:
                return False
    return True


def add(rows, u, v):
    rows[u] |= 1 << v
    rows[v] |= 1 << u


def remove(rows, u, v):
    rows[u] &= ~(1 << v)
    rows[v] &= ~(1 << u)


def edge_list(rows):
    return [(u, v) for u in range(len(rows)) for v in vertices(rows[u]) if u < v]


def project(rows, rng, degree=14, guard=lambda: None):
    """Randomized greedy deletions, monotonically reducing violations."""
    rows = list(rows)
    simple_check(rows)
    deleted = 0
    while True:
        guard()
        overloaded = [u for u, row in enumerate(rows) if row.bit_count() > degree]
        if overloaded:
            u = rng.choice(overloaded)
            remove(rows, u, rng.choice(list(vertices(rows[u]))))
            deleted += 1
            continue
        violation = None
        order = list(range(len(rows)))
        rng.shuffle(order)
        for u in order:
            for v in range(u):
                common = rows[u] & rows[v]
                if common.bit_count() > (1 if rows[u] & (1 << v) else 2):
                    violation = (u, v, common)
                    break
            if violation is not None:
                break
        if violation is None:
            packing_check(rows, degree)
            return rows, deleted
        u, v, common = violation
        k = rng.choice(list(vertices(common)))
        remove(rows, rng.choice((u, v)), k)
        deleted += 1



def run_task(founder, task, directory, allowance, stop_cpu=None, stop_event=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    started = cpu()
    ceiling = min(float(allowance), float(stop_cpu) if stop_cpu is not None else float(allowance))
    if not math.isfinite(ceiling):
        raise ValueError('Finite CPU ceiling required')
    degree = int(task.get('degree', 14))
    arm = task.get('arm', 'packing_tabu')
    if arm not in ('packing_tabu', 'lambda_descent_projection'):
        raise ValueError('Unknown packing arm: ' + str(arm))
    rng = random.Random(int(task.get('seed', 1)))
    original = decode(founder['graph6'])
    original_lambda = lambda_record(original, degree)
    bestpath = directory / 'best.json'
    resumed = bestpath.exists()
    best = packing_record([0] * len(original), degree)
    if resumed:
        saved = json.loads(bestpath.read_text())
        checked = packing_record(saved['graph6'], degree)
        if saved.get('kind') != 'packing' or checked['scores'] != saved['scores'] or checked['state'] != saved['state']:
            raise ValueError('Packing checkpoint mismatch')
        if checked['n'] != len(original):
            raise ValueError('Packing checkpoint size mismatch')
        best = checked
    atomic(bestpath, best)
    parentpath = directory / 'lambda_best.json'
    lambda_best = original_lambda
    if parentpath.exists():
        saved = json.loads(parentpath.read_text())
        checked = lambda_record(decode(saved['graph6']), degree)
        if checked != saved:
            raise ValueError('Lambda checkpoint mismatch')
        lambda_best = min((lambda_best, checked), key=lambda x: (x['scores']['W'], x['scores']['L1']))
    atomic(parentpath, lambda_best)
    stats = {'arm': arm, 'projection_calls': 0, 'projection_deletions': 0, 'add_tests': 0,
             'adds': 0, 'perturbations': 0, 'deleted_edges': 0, 'lambda_trials': 0,
             'lambda_valid': 0, 'lambda_adopted': 0, 'lambda_improvements': 0,
             'packing_improvements': 0, 'restarts': 0, 'checkpoint_resume': resumed,
             'complete_catalogues': 0, 'empty_catalogues': 0, 'lambda_kicks': 0, 'operators': {}}
    last_progress = cpu()

    def guard():
        if (stop_event is not None and stop_event.is_set()) or cpu() >= ceiling:
            raise InterruptedError('SIGNAL_OR_CPU_TARGET')

    def keep(rows):
        nonlocal best
        edges = sum(r.bit_count() for r in rows) // 2
        if edges > best['scores']['edges']:
            best = packing_record(rows, degree)
            atomic(bestpath, best)
            stats['packing_improvements'] += 1

    def projection(rows):
        projected, deleted = project(rows, rng, degree, guard)
        stats['projection_calls'] += 1
        stats['projection_deletions'] += deleted
        keep(projected)
        return projected

    status = 'CPU_TARGET'
    try:
        guard()
        current = projection(original)
        if best['scores']['edges'] > sum(r.bit_count() for r in current) // 2:
            current = decode(best['graph6'])
        parent = decode(lambda_best['graph6'])
        parent_record = lambda_record(parent, degree)
        tabu = {}
        iteration = 0
        target_edges = len(original) * degree // 2
        while best['scores']['edges'] < target_edges:
            guard()
            iteration += 1
            if arm == 'packing_tabu':
                candidates = [(u, v) for u in range(len(current)) for v in range(u)
                              if not current[u] & (1 << v) and tabu.get((v, u), 0) <= iteration]
                rng.shuffle(candidates)
                for u, v in candidates:
                    guard()
                    stats['add_tests'] += 1
                    if add_allowed(current, u, v, degree):
                        add(current, u, v)
                        stats['adds'] += 1
                keep(current)
                if best['scores']['edges'] == target_edges:
                    break
                edges = edge_list(current)
                if edges:
                    number = min(len(edges), rng.choice((2, 3, 5, 8, 12)))
                    for u, v in rng.sample(edges, number):
                        remove(current, u, v)
                        tabu[(u, v)] = iteration + rng.randint(2, 5)
                    stats['perturbations'] += 1
                    stats['deleted_edges'] += number
                tabu = {e: expiry for e, expiry in tabu.items() if expiry > iteration}
                if iteration % 100 == 0:
                    current = projection(original) if rng.random() < 0.5 else decode(best['graph6'])
                    tabu.clear()
                    stats['restarts'] += 1
            else:
                from catalog import catalogue, Scorer
                class CatalogueGuard:
                    def check(self):
                        guard()
                scorer = Scorer(parent)
                winner = random_move = None
                generated = 0
                oldkey = (parent_record['scores']['W'], parent_record['scores']['L1'])
                for operator, move in catalogue(parent, include_star=True, guard=CatalogueGuard()):
                    guard()
                    child, score = scorer.evaluate(move)
                    generated += 1
                    stats['lambda_trials'] += 1
                    newkey = (score['W'], score['L1'])
                    if rng.randrange(generated) == 0:
                        random_move = (child, score, operator)
                    if newkey < oldkey and (winner is None or newkey < (winner[1]['W'], winner[1]['L1'])):
                        winner = (child, score, operator)
                stats['complete_catalogues'] += 1
                choice = winner if winner is not None else random_move
                if choice is None:
                    # An empty exact catalogue does not exhaust the packing projections.
                    stats['empty_catalogues'] += 1
                    projection(parent)
                else:
                    child, expected, operator = choice
                    candidate = lambda_record(child, degree)
                    if candidate['scores'] != {k: expected[k] for k in ('W', 'L1')}:
                        raise ValueError('Lambda incremental/full score mismatch')
                    stats['lambda_valid'] += 1
                    stats['lambda_adopted'] += 1
                    stats['lambda_kicks'] += winner is None
                    stats['operators'][operator] = stats['operators'].get(operator, 0) + 1
                    parent, parent_record = child, candidate
                    newkey = (candidate['scores']['W'], candidate['scores']['L1'])
                    if newkey < (lambda_best['scores']['W'], lambda_best['scores']['L1']):
                        lambda_best = candidate
                        atomic(parentpath, lambda_best)
                        stats['lambda_improvements'] += 1
                    projection(parent)
                if iteration % 128 == 0:
                    parent = decode(lambda_best['graph6'])
                    parent_record = lambda_best
                    stats['restarts'] += 1
            if cpu() - last_progress >= 60:
                atomic(directory / 'packing_progress.json', {'stats': stats, 'best': best,
                       'process_cpu_seconds': cpu(), 'attempt_cpu_seconds': cpu() - started})
                last_progress = cpu()
        else:
            status = 'PACKING_EDGE_TARGET_REACHED'
        if best['scores']['edges'] == target_edges:
            status = 'PACKING_EDGE_TARGET_REACHED'
    except InterruptedError:
        status = 'PAUSED' if stop_event is not None and stop_event.is_set() else 'CPU_TARGET'
    # Independently verify durable incumbents even after interruption.
    packing_check(best['graph6'], degree)
    result = {'status': status, 'kind': 'packing_result', 'best': best, 'lambda_best': lambda_best,
              'stats': stats, 'process_cpu_seconds': cpu(), 'attempt_cpu_seconds': cpu() - started,
              'projection_scope': 'heuristic deletion upper bound; no exact minimum certificate',
              'resume_scope': 'best-incumbent restart; RNG and tabu state not resumed'}
    atomic(directory / 'packing_result.json', result)
    return result
