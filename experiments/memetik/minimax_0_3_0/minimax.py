"""Durable minimax Dijkstra search over labelled Conway-99 graphs."""
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sqlite3
import time

from core import decode_g6, encode_g6
from search import neighbors, families, short, independent, check_independent, atomic

VERSION = 'minimax-0.3.0'
TERMINAL = {'IMPROVEMENT_FOUND', 'COMPONENT_EXHAUSTED', 'WALLTIME_LIMIT'}


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA cache_size=-8192')
    db.execute('CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY,g6 TEXT NOT NULL UNIQUE,value INTEGER NOT NULL,metrics TEXT NOT NULL,peak INTEGER NOT NULL,parent INTEGER,move TEXT,closed INTEGER NOT NULL DEFAULT 0,census TEXT)')
    db.execute('CREATE INDEX IF NOT EXISTS frontier ON nodes(closed,peak,value,id)')
    db.execute('CREATE TABLE IF NOT EXISTS meta(name TEXT PRIMARY KEY,value TEXT NOT NULL)')
    db.commit()
    return db


def getmeta(db, name, default=None):
    row = db.execute('SELECT value FROM meta WHERE name=?', (name,)).fetchone()
    return json.loads(row[0]) if row else default


def putmeta(db, name, value):
    db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (name, json.dumps(value)))


def front(db):
    return db.execute('SELECT * FROM nodes WHERE closed=0 ORDER BY peak,value,id LIMIT 1').fetchone()


def relax(db, parent, graph, metrics, move, objective):
    value = metrics[objective]
    peak = max(parent['peak'], value)
    previous = db.execute('SELECT id,peak,closed FROM nodes WHERE g6=?', (graph,)).fetchone()
    if previous is None:
        db.execute('INSERT INTO nodes(g6,value,metrics,peak,parent,move) VALUES(?,?,?,?,?,?)', (graph, value, json.dumps(metrics), peak, parent['id'], json.dumps(move)))
        return 1, 0
    if peak < previous['peak']:
        assert not previous['closed'], 'A settled Dijkstra label cannot decrease'
        db.execute('UPDATE nodes SET peak=?,parent=?,move=? WHERE id=?', (peak, parent['id'], json.dumps(move), previous['id']))
        return 0, 1
    return 0, 0


def seed_database(path, seed, config):
    assert not Path(path).exists(), 'Never overwrite a checkpoint'
    db = connect(path)
    root = seed['root']
    baseline = seed['baseline']
    objective = seed['objective']
    db.execute('INSERT INTO nodes(g6,value,metrics,peak) VALUES(?,?,?,?)', (root, baseline, json.dumps(seed['metrics'][root]), baseline))
    edges = {}
    for a, b, move in seed['edges']:
        edges.setdefault(a, []).append((b, move))
    inside = set(seed['inside'])
    count, settled, updates = 1, 0, 0
    db.commit()
    while True:
        node = front(db)
        if node['peak'] >= seed['strict_threshold']:
            break
        assert node['g6'] in inside and node['value'] >= baseline
        census = seed['censuses'][node['g6']]
        assert set(census) == set(families(seed['arm'])) and all(x['complete'] for x in census.values())
        db.execute('BEGIN')
        for graph, move in edges[node['g6']]:
            n, u = relax(db, node, graph, seed['metrics'][graph], move, objective)
            count += n
            updates += u
        db.execute('UPDATE nodes SET closed=1,census=? WHERE id=?', (json.dumps(census), node['id']))
        settled += 1
        db.commit()
    assert {r[0] for r in db.execute('SELECT g6 FROM nodes WHERE closed=1')} == inside
    assert node['peak'] == seed['strict_threshold']
    assert count == len(seed['metrics'])
    putmeta(db, 'config', config)
    putmeta(db, 'counts', {'discovered': count, 'expanded': settled, 'relaxations': updates})
    putmeta(db, 'seed', {'inside': len(inside), 'boundary_nodes': count-len(inside), 'strict_threshold': seed['strict_threshold'], 'source_certificate_sha256': seed['source_certificate_sha256']})
    putmeta(db, 'last_settled_peak', max(r[0] for r in db.execute('SELECT peak FROM nodes WHERE closed=1')))
    db.commit()
    report = snapshot(db, seed, config, 0, 'PREPARED')
    db.close()
    return report


def snapshot(db, seed, config, cpu_seconds, status):
    counts = getmeta(db, 'counts')
    node = front(db)
    peak = node['peak'] if node else None
    return {'version': VERSION, 'task': seed['name'], 'arm': seed['arm'], 'objective': seed['objective'], 'baseline': seed['baseline'], 'status': status, **counts, 'frontier_peak': peak, 'necessary_barrier_at_least': peak-seed['baseline'] if peak is not None else None, 'no_improvement_below_objective_height': peak, 'frontier_node_value': node['value'] if node else None, 'cpu_seconds': cpu_seconds, 'remaining_wall_seconds': max(0, config['deadline_epoch']-time.time()), 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'scope': 'Current operator catalogue; labelled states; minimax barrier, no shortest-length claim'}


def witness(db, node_id, objective, arm):
    path = []
    visited = set()
    while node_id is not None:
        assert node_id not in visited
        visited.add(node_id)
        row = db.execute('SELECT * FROM nodes WHERE id=?', (node_id,)).fetchone()
        rows = decode_g6(row['g6'])
        check_independent(rows, arm)
        assert short(rows) == json.loads(row['metrics'])
        path.append({'graph6': row['g6'], 'metrics': json.loads(row['metrics']), 'transition': json.loads(row['move']) if row['move'] else None})
        node_id = row['parent']
    path.reverse()
    for previous, current in zip(path, path[1:]):
        rows = list(decode_g6(previous['graph6']))
        for a, b in current['transition']['deleted']:
            assert rows[a] & (1 << b)
            rows[a] &= ~(1 << b)
            rows[b] &= ~(1 << a)
        for a, b in current['transition']['added']:
            assert not rows[a] & (1 << b)
            rows[a] |= 1 << b
            rows[b] |= 1 << a
        assert tuple(rows) == decode_g6(current['graph6'])
    maximum = max(p['metrics'][objective] for p in path)
    return {'path': path, 'path_length': len(path)-1, 'maximum_objective': maximum, 'barrier_above_start': maximum-path[0]['metrics'][objective], 'minimum_barrier_in_catalogue': True, 'shortest_path_length_claimed': False}


class StopSearch(Exception):
    pass


class Guard:
    def __init__(self, directory, deadline, progress):
        self.directory = directory
        self.deadline = deadline
        self.progress = progress
        self.last = 0
        self.stopping = False

    def check(self):
        if self.stopping:
            raise StopSearch('INTERRUPTED')
        if time.time() >= self.deadline:
            raise StopSearch('WALLTIME_LIMIT')
        if time.monotonic()-self.last >= 10:
            import shutil
            paths = [self.directory]
            if Path('/mnt/c').is_dir():
                paths.append(Path('/mnt/c'))
            if any(shutil.disk_usage(p).free < 10*2**30 for p in paths):
                raise StopSearch('DISK_FLOOR')
            available = next(int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
            if available < 512*2**20:
                raise StopSearch('SYSTEM_MEMORY_FLOOR')
            self.progress()
            self.last = time.monotonic()


def run_worker(directory, seed, config):
    directory = Path(directory)
    name = seed['name']
    lock = (directory/(name+'.lock')).open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    resource.setrlimit(resource.RLIMIT_AS, (896*2**20, 896*2**20))
    db = connect(directory/(name+'.sqlite'))
    assert getmeta(db, 'config') == config
    previous = getmeta(db, 'result')
    if previous and previous['status'] in TERMINAL:
        atomic(directory/(name+'.json'), previous)
        return
    status_path = directory/(name+'.json')
    prior_cpu = json.loads(status_path.read_text()).get('cpu_seconds', 0) if status_path.exists() else 0
    started = time.process_time()
    elapsed = lambda: prior_cpu+time.process_time()-started
    # A separate read connection sees committed state only during an expansion.
    observer = sqlite3.connect('file:'+str((directory/(name+'.sqlite')).resolve())+'?mode=ro', uri=True)
    observer.row_factory = sqlite3.Row
    guard = Guard(directory, config['deadline_epoch'], lambda: atomic(status_path, snapshot(observer, seed, config, elapsed(), 'RUNNING')))
    def request_stop(signum, frame):
        guard.stopping = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    reserve = bytearray(2**20)
    status = 'ERROR'
    extra = {}
    try:
        while True:
            node = front(db)
            if node is None:
                status = 'COMPONENT_EXHAUSTED'
                break
            if node['value'] < seed['baseline']:
                proof = witness(db, node['id'], seed['objective'], seed['arm'])
                assert proof['maximum_objective'] == node['peak']
                status = 'IMPROVEMENT_FOUND'
                extra['witness'] = proof
                break
            guard.check()
            assert node['peak'] >= getmeta(db, 'last_settled_peak')
            counts = dict(getmeta(db, 'counts'))
            census = {}
            db.execute('BEGIN')
            for family, move, child in neighbors(decode_g6(node['g6']), seed['arm'], guard, census):
                n, u = relax(db, node, encode_g6(child), short(child), {'family': family, 'deleted': move[0], 'added': move[1]}, seed['objective'])
                counts['discovered'] += n
                counts['relaxations'] += u
            assert set(census) == set(families(seed['arm'])) and all(v['complete'] for v in census.values())
            db.execute('UPDATE nodes SET closed=1,census=? WHERE id=?', (json.dumps(census), node['id']))
            counts['expanded'] += 1
            putmeta(db, 'counts', counts)
            putmeta(db, 'last_settled_peak', node['peak'])
            db.commit()
    except StopSearch as exc:
        db.rollback()
        status = str(exc)
    except MemoryError:
        del reserve
        db.rollback()
        status = 'MEMORY_LIMIT'
    except Exception as exc:
        db.rollback()
        status = 'ERROR'
        extra['error'] = repr(exc)
    finally:
        observer.close()
    result = snapshot(db, seed, config, elapsed(), status)
    result.update(extra)
    result['component_complete'] = status == 'COMPONENT_EXHAUSTED'
    if status == 'IMPROVEMENT_FOUND':
        result['minimum_escape_barrier'] = extra['witness']['barrier_above_start']
    putmeta(db, 'result', result)
    db.commit()
    db.close()
    atomic(status_path, result)
