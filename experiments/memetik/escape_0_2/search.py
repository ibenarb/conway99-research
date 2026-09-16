"""Deterministic labelled searches with transactional expansion checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import shutil
import sqlite3
import time
from core import BudgetEnd, apply_move, decode_g6, encode_g6, metrics, validate
from operators import apex_moves, rotation_moves, omega_moves

VERSION = 'escape-0.2.1'
FIELDS = ('W', 'L1', 'F', 'Linf', 'Nmax')


def atomic(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as output:
        json.dump(data, output, indent=4)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def short(rows):
    data = metrics(rows)
    return {k: data[k] for k in FIELDS}


def independent(rows):
    neighbors = [set(j for j in range(99) if row & (1 << j)) for row in rows]
    residuals = [len(neighbors[i] & neighbors[j]) + int(j in neighbors[i]) - 2 for i in range(99) for j in range(i)]
    maximum = max(map(abs, residuals))
    return {'W': sum(r != 0 for r in residuals), 'L1': sum(map(abs, residuals)), 'F': sum(r * r for r in residuals), 'Linf': maximum, 'Nmax': sum(abs(r) == maximum for r in residuals)}


def key(data, objective):
    return (data['Linf'], data['Nmax'], data['L1']) if objective == 'Linf' else (data[objective],)


def check_independent(rows, arm):
    validate(rows, arm)
    assert short(rows) == independent(rows)


def families(arm):
    return ('4x4', '4x6', '6x6') if arm == 'omega' else ('apex', 'rotation')


def neighbors(rows, arm, budget, counts):
    for family in families(arm):
        budget.check()
        rng = random.Random(20260915)
        stream = apex_moves(rows, rng, budget) if family == 'apex' else rotation_moves(rows, rng, budget) if family == 'rotation' else omega_moves(rows, family, rng, budget)
        counts[family] = {'trades': 0, 'complete': False}
        for move in stream:
            budget.check()
            child = apply_move(rows, move)
            validate(child, arm)
            counts[family]['trades'] += 1
            yield family, move, child
        counts[family]['complete'] = True


class Budget:
    def __init__(self, seconds, used, directory, callback):
        self.start = time.process_time()
        self.used = used
        self.seconds = seconds
        self.directory = directory
        self.callback = callback
        self.last = -1000

    def elapsed(self):
        return self.used + time.process_time() - self.start

    def check(self):
        if time.monotonic() - self.last >= 10:
            self.callback(self.elapsed())
            self.last = time.monotonic()
            if shutil.disk_usage(self.directory).free < 10 * 2**30:
                raise BudgetEnd('DISK_FLOOR')
            available = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
            if available < 512 * 2**20:
                raise BudgetEnd('SYSTEM_MEMORY_FLOOR')
        if self.elapsed() >= self.seconds:
            raise BudgetEnd('CPU_BUDGET')


def connection(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA cache_size=-8192')
    db.execute('CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, g6 TEXT UNIQUE, parent INTEGER, depth INTEGER, move TEXT, metrics TEXT, expanded INTEGER DEFAULT 0, census TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value TEXT)')
    db.commit()
    return db


def witness(db, endpoint, objective, arm):
    path = []
    node = db.execute('SELECT * FROM nodes WHERE id=?', (endpoint,)).fetchone()
    while node is not None:
        rows = decode_g6(node['g6'])
        check_independent(rows, arm)
        entry = {'graph6': node['g6'], 'sha256': hashlib.sha256((node['g6'] + '\n').encode()).hexdigest(), 'metrics': json.loads(node['metrics']), 'transition': json.loads(node['move']) if node['move'] else None}
        path.append(entry)
        node = db.execute('SELECT * FROM nodes WHERE id=?', (node['parent'],)).fetchone() if node['parent'] else None
    path.reverse()
    for first, second in zip(path, path[1:]):
        move = second['transition']
        assert encode_g6(apply_move(decode_g6(first['graph6']), (tuple(map(tuple, move['deleted'])), tuple(map(tuple, move['added']))))) == second['graph6']
    baseline = path[0]['metrics']
    peak = max(key(p['metrics'], objective) for p in path)
    result = {'path': path, 'path_length': len(path) - 1, 'maximum_objective_key_on_path': peak,
              'maximum_each_metric_minus_start': {k: max(p['metrics'][k] - baseline[k] for p in path) for k in FIELDS}}
    if objective != 'Linf':
        result['barrier_above_start'] = peak[0] - baseline[objective]
    return result


def execute(task, founder, directory, limits):
    resource.setrlimit(resource.RLIMIT_AS, (768 * 2**20, 768 * 2**20))
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / (task['id'] + '.json')
    db = connection(directory / (task['id'] + '.sqlite'))
    config = {'version': VERSION, 'task': task, 'founder': founder['sha256'], 'limits': limits}
    previous = db.execute("SELECT value FROM meta WHERE name='config'").fetchone()
    if previous:
        assert json.loads(previous[0]) == config, 'Checkpoint configuration mismatch'
    else:
        db.execute("INSERT INTO meta VALUES ('config', ?)", (json.dumps(config),))
        rows = decode_g6(founder['graph6'])
        check_independent(rows, founder['arm'])
        db.execute('INSERT INTO nodes (g6, depth, metrics) VALUES (?, 0, ?)', (founder['graph6'], json.dumps(short(rows))))
        db.commit()
    done = db.execute("SELECT value FROM meta WHERE name='result'").fetchone()
    if done:
        result = json.loads(done[0])
        atomic(output, result)
        db.close()
        return result
    progress = json.loads(output.read_text()) if output.exists() else {}
    result = {'version': VERSION, 'task': task, 'status': 'RUNNING', 'arm': founder['arm'], 'source_sha256': founder['sha256'], 'scope': 'Labelled graph6 identity; current finite operator catalog; all families rechecked at each expansion.', 'component_complete': False}
    def save(cpu):
        result.update(cpu_seconds=cpu, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        atomic(output, result)
    budget = Budget(limits['cpu_seconds'], progress.get('cpu_seconds', 0), directory, save)
    reserve = bytearray(2**20)
    objective = task['objective']
    baseline = short(decode_g6(founder['graph6']))
    endpoint = None
    try:
        while True:
            budget.check()
            node = db.execute('SELECT * FROM nodes WHERE expanded=0 ORDER BY id LIMIT 1').fetchone()
            if node is None:
                result.update(status='COMPONENT_EXHAUSTED', component_complete=True)
                break
            if task['mode'] == 'bfs' and node['depth'] >= limits['max_depth']:
                result.update(status='DEPTH_LIMIT', no_improvement_through_depth=limits['max_depth'])
                break
            rows = decode_g6(node['g6'])
            current = json.loads(node['metrics'])
            census = {}
            best = None
            db.execute('BEGIN')
            for family, move, child in neighbors(rows, founder['arm'], budget, census):
                data = short(child)
                g6 = encode_g6(child)
                transition = {'family': family, 'deleted': move[0], 'added': move[1]}
                if task['mode'] == 'descent':
                    if key(data, objective) < key(current, objective):
                        candidate = (key(data, objective), g6, data, transition)
                        if best is None or candidate[:2] < best[:2]:
                            best = candidate
                    continue
                improving = key(data, objective) < key(baseline, objective)
                if not improving and task['mode'] == 'neutral' and key(data, objective) != key(baseline, objective):
                    continue
                exists = db.execute('SELECT id FROM nodes WHERE g6=?', (g6,)).fetchone()
                if not exists:
                    count = db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
                    if count >= limits['max_states']:
                        raise BudgetEnd('STATE_LIMIT')
                    cursor = db.execute('INSERT INTO nodes (g6,parent,depth,move,metrics) VALUES (?,?,?,?,?)', (g6, node['id'], node['depth'] + 1, json.dumps(transition), json.dumps(data)))
                    child_id = cursor.lastrowid
                else:
                    child_id = exists['id']
                if improving:
                    endpoint = child_id
                    result.update(status='IMPROVEMENT_FOUND', shortest_length_in_search_scope=True,
                                  shortest_scope='All catalog paths' if task['mode'] == 'bfs' else 'Neutral prefixes followed by one improving move; no claim about paths using deterioration')
                    break
            if endpoint is not None:
                db.commit()
                break
            assert all(census[f]['complete'] for f in families(founder['arm']))
            db.execute('UPDATE nodes SET expanded=1,census=? WHERE id=?', (json.dumps(census), node['id']))
            if task['mode'] == 'descent':
                if best is None:
                    endpoint = node['id']
                    result.update(status='LOCAL_MINIMUM_VERIFIED', local_scope=list(families(founder['arm'])))
                else:
                    if node['depth'] >= limits['max_descent_steps']:
                        raise BudgetEnd('DESCENT_STEP_LIMIT')
                    _, g6, data, transition = best
                    db.execute('INSERT INTO nodes (g6,parent,depth,move,metrics) VALUES (?,?,?,?,?)', (g6, node['id'], node['depth'] + 1, json.dumps(transition), json.dumps(data)))
            db.commit()
            result['last_completed_depth'] = node['depth']
            if endpoint is not None:
                break
    except BudgetEnd as error:
        db.rollback()
        result['status'] = str(error)
    except MemoryError:
        del reserve
        db.rollback()
        result['status'] = 'MEMORY_LIMIT'
    except Exception as error:
        db.rollback()
        result.update(status='ERROR', error=repr(error))
    result['discovered'] = db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
    result['expanded'] = db.execute('SELECT COUNT(*) FROM nodes WHERE expanded=1').fetchone()[0]
    result['depth_counts'] = [dict(r) for r in db.execute('SELECT depth, COUNT(*) AS discovered, SUM(expanded) AS expanded FROM nodes GROUP BY depth ORDER BY depth')]
    if task['mode'] == 'bfs':
        unexpanded = db.execute('SELECT MIN(depth) FROM nodes WHERE expanded=0').fetchone()[0]
        if unexpanded is not None:
            result['fully_expanded_through_depth'] = unexpanded - 1
            result['no_improvement_through_depth'] = unexpanded
    if endpoint is not None:
        result['witness'] = witness(db, endpoint, objective, founder['arm'])
    elif task['mode'] == 'descent':
        last = db.execute('SELECT id FROM nodes ORDER BY id DESC LIMIT 1').fetchone()[0]
        result['witness'] = witness(db, last, objective, founder['arm'])
    result['cpu_seconds'] = budget.elapsed()
    db.execute("INSERT OR REPLACE INTO meta VALUES ('result', ?)", (json.dumps(result),))
    db.commit()
    db.close()
    atomic(output, result)
    return result
