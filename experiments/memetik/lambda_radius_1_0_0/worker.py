"""One wait4-accounted CPU slice; checkpoints at complete parent states."""
import boot
from support import *
from enumeration import prepare_task, expand, merge, lower_layers
from kernel import catalogue, Scorer


def controls(task, directory, guard):
    starts = read(boot.HERE / 'STARTS.json')
    checked_moves = 0
    for label in ('2076', '2077'):
        rows, scores = checked(starts[label]['graph6'], 'lambda')
        assert sha(starts[label]['graph6'].encode()) == starts[label]['state']
        assert core.canonical(rows) == starts[label]['class']
        sc = Scorer(rows)
        for _, move in catalogue(rows, False, guard):
            child, incremental = sc.evaluate(move)
            _, independent = checked(core.encode_g6(child), 'lambda')
            if independent != incremental:
                raise RuntimeError('Incremental score mismatch')
            if tuple(core.apply_move(child, move[::-1])) != tuple(rows):
                raise RuntimeError('Inverse replay mismatch')
            if move[::-1] not in {m for _, m in catalogue(child, False, guard)}:
                raise RuntimeError('Catalogue not inverse-closed')
            checked_moves += 1
    a, _, _ = lower_layers(starts['2079'], guard)
    b, _, _ = lower_layers(starts['2076'], guard)
    overlap = a.keys() & b.keys()
    if not overlap or min(len(a[r]) + len(b[r]) for r in overlap) != 4:
        raise RuntimeError('Positive depth-4 control failed')
    meet = min(overlap, key=pack)
    path = a[meet] + [m[::-1] for m in reversed(b[meet])]
    proof = witness(starts['2079'], path, guard)
    if proof['state'] != starts['2076']['state'] or not proof['strict_improvement']:
        raise RuntimeError('Positive replay failed')
    return {'status': 'DONE', 'control_status': 'CONTROLS_PASS',
            'all_root_moves_independently_scored_and_inverted': checked_moves, 'positive_depth4_witness': proof}


def run(directory, allocation):
    directory = Path(directory)
    task = read(directory / 'task.json')
    signal.signal(signal.SIGTERM, stopped)
    signal.signal(signal.SIGINT, stopped)
    signal.signal(signal.SIGXCPU, stopped)
    hard = max(2, int(math.floor(allocation)))
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, hard - 1), hard))
    # Keep 3 s for SQLite rollback, close, independent receipts and interpreter exit.
    guard = Guard(max(0, allocation - 3))
    try:
        if task['kind'] == 'controls':
            result = controls(task, directory, guard)
        elif task['kind'] == 'prepare':
            result = prepare_task(task, directory, guard)
        elif task['kind'] == 'merge':
            result = merge(task, directory, guard)
        elif task['kind'] == 'spin':
            end = own_cpu() + task['seconds']
            while own_cpu() < end:
                guard.check()
        else:
            result = expand(task, directory, guard)
        if task['kind'] == 'spin':
            result = {'status': 'DONE', 'self_cpu': own_cpu()}
    except Pause as error:
        result = {'status': 'PAUSED', 'reason': str(error)}
    result['self_cpu'] = own_cpu()
    atomic(directory / 'slice_result.json', result)


if __name__ == '__main__':
    run(sys.argv[1], float(sys.argv[2]))
