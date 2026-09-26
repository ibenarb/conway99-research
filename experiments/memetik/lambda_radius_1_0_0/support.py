"""Durable I/O, owned-process accounting and bounded worker slices."""
import boot
from common import atomic, sha, core, checked
from runtime import process, THREAD_ENV
from pathlib import Path
import fcntl
import hashlib
import json
import math
import os
import resource
import signal
import sqlite3
import subprocess
import sys
import time

GIB = 1024 ** 3
STOP = False


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def own_cpu():
    u = resource.getrusage(resource.RUSAGE_SELF)
    return u.ru_utime + u.ru_stime


def stopped(*args):
    global STOP
    STOP = True


class Pause(Exception):
    pass


class Guard:
    def __init__(self, ceiling=float('inf')):
        self.ceiling = ceiling
        self.generated = 0

    def check(self):
        if STOP or own_cpu() >= self.ceiling:
            raise Pause('SIGNAL_OR_CPU_SLICE')


def pack(rows):
    return b''.join(int(r).to_bytes(13, 'little') for r in rows)


def unpack(blob):
    if len(blob) != 1287:
        raise ValueError('Invalid 99-row state')
    return tuple(int.from_bytes(blob[i:i + 13], 'little') for i in range(0, len(blob), 13))


def key(scores):
    return scores['W'], scores['L1']


def connect(path, readonly=False):
    if readonly:
        return sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=DELETE')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA cache_size=-4096')
    db.execute('CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, rows BLOB UNIQUE NOT NULL, depth INTEGER NOT NULL, path TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    db.commit()
    return db


def meta(db, name, default=None):
    row = db.execute('SELECT value FROM meta WHERE key=?', (name,)).fetchone()
    return json.loads(row[0]) if row else default


def putmeta(db, name, value):
    db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (name, json.dumps(value, sort_keys=True)))


def node(db, rows, depth, path):
    db.execute('INSERT OR IGNORE INTO nodes(rows,depth,path) VALUES (?,?,?)', (pack(rows), depth, json.dumps(path, separators=(',', ':'))))


def normalize(move):
    return tuple(tuple(tuple(edge) for edge in edges) for edges in move)


def witness(start, path, guard=None):
    """Replay every exact catalogue edge; verify every graph with the independent verifier."""
    from kernel import catalogue
    guard = guard or Guard()
    rows, base = checked(start['graph6'], 'lambda')
    trace = []
    for raw in path:
        move = normalize(raw)
        if move not in {m for _, m in catalogue(rows, False, guard)}:
            raise ValueError('Witness step absent from catalogue')
        rows = core.apply_move(rows, move)
        g6 = core.encode_g6(rows)
        _, scores = checked(g6, 'lambda')
        trace.append({'move': move, 'graph6': g6, 'scores': scores})
    g6 = core.encode_g6(rows)
    _, scores = checked(g6, 'lambda')
    return {'start_state': start['state'], 'steps': trace, 'graph6': g6, 'state': sha(g6.encode()),
            'class': core.canonical(rows), 'scores': scores, 'strict_improvement': key(scores) < key(base),
            'global_W_record': scores['W'] < 2076}


def package_verify():
    p = read(boot.HERE / 'PACKAGE.json')
    for name, expected in p['files'].items():
        if digest(boot.ROOT / name) != expected:
            raise RuntimeError('SOURCE_HASH_MISMATCH: ' + name)
    return digest(boot.HERE / 'PACKAGE.json')
