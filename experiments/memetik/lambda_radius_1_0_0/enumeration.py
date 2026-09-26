"""Exact labelled BFS layers. Whole-parent SQLite transactions survive interruption."""
import boot
from support import *
from kernel import catalogue, Scorer

EXPECTED = {'2076': (99, 5222, 526476), '2077': (95, 4768, 459185)}


def lower_layers(start, guard):
    root = tuple(core.decode_g6(start['graph6']))
    base = Scorer(root).scores
    states = {root: []}
    first = []
    evaluations = 0
    for _, move in catalogue(root, False, guard):
        child, score = Scorer(root).evaluate(move)
        evaluations += 1
        if key(score) < key(base):
            raise RuntimeError('Unexpected depth-1 improvement')
        r = tuple(child)
        if r not in states:
            states[r] = [move]
            first.append(r)
    for r in first:
        sc = Scorer(r)
        for _, move in catalogue(r, False, guard):
            child, score = sc.evaluate(move)
            evaluations += 1
            if key(score) < key(base):
                raise RuntimeError('Unexpected depth-2 improvement')
            states.setdefault(tuple(child), states[r] + [move])
    return states, len(first), evaluations


def prepare_task(task, directory, guard):
    start = task['start']
    states, n1, evaluations = lower_layers(start, guard)
    arm = task['arm']
    n2 = sum(len(p) == 2 for p in states.values())
    if (n1, n2) != EXPECTED[arm][:2]:
        raise RuntimeError('Depth-2 census mismatch')
    dbpath = directory / 'lower.sqlite'
    # Preparation restarts atomically rather than admitting half a BFS layer.
    temp = directory / 'lower.build.sqlite'
    if temp.exists():
        temp.unlink()
    db = connect(temp)
    for rows, path in states.items():
        node(db, rows, len(path), path)
    putmeta(db, 'task_sha256', digest(directory / 'task.json'))
    db.commit()
    guard.check()
    bounds = db.execute('SELECT min(id),max(id),count(*) FROM nodes WHERE depth=2').fetchone()
    db.close()
    os.replace(temp, dbpath)
    return {'status': 'DONE', 'n_L1': n1, 'n_L2': n2, 'evaluations': evaluations,
            'bounds': bounds, 'lower_sha256': digest(dbpath)}


def expand(task, directory, guard):
    source = Path(task['input'])
    src = connect(source, True)
    db = connect(directory / 'work.sqlite')
    binding = sha(json.dumps(task, sort_keys=True).encode())
    if meta(db, 'binding', binding) != binding:
        raise RuntimeError('Changed task/checkpoint binding')
    putmeta(db, 'binding', binding)
    progress = meta(db, 'progress', {'last': task['lo'] - 1, 'parents': 0, 'children': 0, 'witness': None})
    db.commit()
    base = task['start']['scores']
    try:
        for idx, blob, rawpath in src.execute('SELECT id,rows,path FROM nodes WHERE depth=? AND id>=? AND id<=? ORDER BY id',
                                             (task['depth'] - 1, max(task['lo'], progress['last'] + 1), task['hi'])):
            guard.check()
            rows = unpack(blob)
            sc = Scorer(rows)
            path = json.loads(rawpath)
            count = 0
            found = None
            db.execute('BEGIN')
            for _, move in catalogue(rows, False, guard):
                child, scores = sc.evaluate(move)
                count += 1
                if key(scores) < key(base):
                    found = witness(task['start'], path + [move], guard)
                    if not found['strict_improvement'] or found['scores'] != scores:
                        raise RuntimeError('Independent witness mismatch')
                    break
                if task['depth'] == 3:
                    node(db, child, 3, path + [move])
            progress = {'last': idx, 'parents': progress['parents'] + 1,
                        'children': progress['children'] + count, 'witness': found}
            putmeta(db, 'progress', progress)
            db.commit()
            if found:
                return {'status': 'FOUND', **progress}
        return {'status': 'DONE', **progress}
    except BaseException:
        db.rollback()
        raise
    finally:
        src.close()
        db.close()


def merge(task, directory, guard):
    """Union L0..L2 and complete L3 fragments. No isomorphism pruning."""
    dbpath = directory / 'layers.sqlite'
    db = connect(dbpath)
    binding = sha(json.dumps(task, sort_keys=True).encode())
    if meta(db, 'binding', binding) != binding:
        raise RuntimeError('Changed merge binding')
    putmeta(db, 'binding', binding)
    completed = meta(db, 'completed', [])
    db.commit()
    try:
        for filename, expected in task['sources']:
            if filename in completed:
                continue
            guard.check()
            if digest(filename) != expected:
                raise RuntimeError('Merge input hash mismatch')
            src = connect(filename, True)
            db.execute('BEGIN')
            try:
                for blob, depth, path in src.execute('SELECT rows,depth,path FROM nodes ORDER BY id'):
                    guard.check()
                    db.execute('INSERT OR IGNORE INTO nodes(rows,depth,path) VALUES (?,?,?)', (blob, depth, path))
                completed.append(filename)
                putmeta(db, 'completed', completed)
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                src.close()
        counts = dict(db.execute('SELECT depth,count(*) FROM nodes GROUP BY depth'))
        bounds = db.execute('SELECT min(id),max(id),count(*) FROM nodes WHERE depth=3').fetchone()
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise RuntimeError('Merged SQLite corrupt')
        return {'status': 'DONE', 'counts': counts, 'bounds': bounds}
    finally:
        db.close()
