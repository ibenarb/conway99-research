"""Fixed-root P episodes, persisted after every accepted move.
Catalogue interruption replays the current batch, charges all CPU, and preserves RNG.
"""
import boot
from support import *
from kernel import catalogue, Scorer
from search import tuple_state
import random


def seed_for(task, index):
    value = f"lambda-profile-v2|{task['start']['state']}|{task['k']}|{index}"
    return int.from_bytes(hashlib.sha256(value.encode()).digest(), 'big')


def new_episode(task, index):
    s = task['start']
    return {'index': index, 'phase': 'perturb', 'graph6': s['graph6'],
            'rng': random.Random(seed_for(task, index)).getstate(), 'path': [],
            'perturb': 0, 'descent': 0, 'phase_cpu': {'perturb': 0.0, 'descent': 0.0, 'verify': 0.0},
            'maxima': dict(s['scores']), 'scores': dict(s['scores']), 'intermediate_better': []}


def advance(ep, task, guard):
    """One frozen P decision. Equal keys preserve the original catalogue order."""
    if ep['phase'] == 'perturb' and ep['perturb'] == task['k']:
        ep['phase'] = 'descent'
    if ep['phase'] == 'verify':
        return False
    rows = core.decode_g6(ep['graph6'])
    sc = Scorer(rows)
    choices = []
    for name, move in catalogue(rows, False, guard):
        child, scores = sc.evaluate(move)
        guard.check()
        choices.append((name, move, scores))
    guard.check()
    rng = random.Random()
    rng.setstate(tuple_state(ep['rng']))
    if ep['phase'] == 'perturb':
        if not choices:
            ep['phase'] = 'descent'
            return True
        choice = rng.choice(choices)
    else:
        better = [c for c in choices if key(c[2]) < key(sc.scores)]
        if not better:
            ep['phase'] = 'verify'
            return True
        choice = min(better, key=lambda c: key(c[2]))
    name, move, scores = choice
    child = core.apply_move(rows, move)
    ep['graph6'] = core.encode_g6(child)
    ep['rng'] = rng.getstate()
    ep['path'].append({'operator': name, 'move': move, 'scores': scores, 'phase': ep['phase']})
    ep[ep['phase']] += 1
    ep['scores'] = scores
    for metric in ep['maxima']:
        ep['maxima'][metric] = max(ep['maxima'][metric], scores[metric])
    if key(scores) < key(task['start']['scores']):
        ep['intermediate_better'].append(len(ep['path']))
    return True


def finish(ep, task, guard):
    guard.check()
    rows, scores = checked(ep['graph6'], 'lambda')
    if scores != ep['scores']:
        raise RuntimeError('INDEPENDENT_ENDPOINT_SCORE_MISMATCH')
    cls = core.canonical(rows)
    guard.check()
    better = key(scores) < key(task['start']['scores'])
    proof = None
    if better or ep['intermediate_better']:
        proof = witness(task['start'], [p['move'] for p in ep['path']], guard)
        if proof['graph6'] != ep['graph6'] or proof['scores'] != scores:
            raise RuntimeError('WITNESS_MISMATCH')
        # Any improving visited prefix of length <= 4 contradicts radius result.
        if any(i <= 4 for i in ep['intermediate_better']):
            raise RuntimeError('RADIUS4_COUNTEREXAMPLE_REQUIRES_DIAGNOSIS')
    return {'index': ep['index'], 'block': ep['index'] // 100,
            'seed': str(seed_for(task, ep['index'])), 'start_state': task['start']['state'],
            'start_class': task['start']['class'], 'k': task['k'], 'actual_k': ep['perturb'],
            'descent_length': ep['descent'], 'graph6': ep['graph6'], 'scores': scores,
            'state': sha(ep['graph6'].encode()), 'class': cls, 'path': ep['path'],
            'returned': ep['graph6'] == task['start']['graph6'],
            'isomorphic_return': cls == task['start']['class'], 'improved': better,
            'global_W_record': scores['W'] < 2076, 'solution': scores['W'] == 0,
            'observed_maxima': ep['maxima'], 'intermediate_better': ep['intermediate_better'],
            'witness': proof, 'stop': 'LOCAL_MIN_EXACT_AP'}


def database(directory, task):
    db = connect(Path(directory) / 'work.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS episodes(idx INTEGER PRIMARY KEY, value TEXT NOT NULL)')
    binding = sha(json.dumps(task, sort_keys=True).encode())
    if meta(db, 'binding', binding) != binding:
        raise RuntimeError('TASK_CHECKPOINT_MISMATCH')
    putmeta(db, 'binding', binding)
    db.commit()
    return db


def work(task, directory, guard, chunk=10):
    db = database(directory, task)
    progress = meta(db, 'progress', {'next': 0, 'episode': None, 'solution': False})
    end = min(task['n'], progress['next'] + chunk)
    try:
        while progress['next'] < end:
            guard.check()
            if progress['episode'] is None:
                progress['episode'] = new_episode(task, progress['next'])
            ep = progress['episode']
            # Set phase before charging so perturbation and descent CPU are separate.
            if ep['phase'] == 'perturb' and ep['perturb'] == task['k']:
                ep['phase'] = 'descent'
            phase = ep['phase']
            started = own_cpu()
            result = None
            try:
                if phase == 'verify':
                    result = finish(ep, task, guard)
                else:
                    advance(ep, task, guard)
            finally:
                ep['phase_cpu'][phase] += own_cpu() - started
                putmeta(db, 'progress', progress)
                db.commit()
            if result is not None:
                result['phase_cpu_seconds'] = dict(ep['phase_cpu'])
                result['episode_cpu_seconds'] = sum(ep['phase_cpu'].values())
                db.execute('INSERT INTO episodes VALUES (?,?)', (ep['index'], json.dumps(result)))
                progress['next'] += 1
                progress['episode'] = None
                progress['solution'] |= result['solution']
                putmeta(db, 'progress', progress)
                db.commit()
                atomic(Path(directory) / 'progress.json', {'completed': progress['next'], 'last_scores': result['scores'], 'solution': progress['solution']})
                if result['solution']:
                    break
        return {'status': 'DONE' if progress['next'] == task['n'] else 'YIELD',
                'completed': progress['next'], 'solution': progress['solution']}
    finally:
        putmeta(db, 'progress', progress)
        db.commit()
        db.close()
