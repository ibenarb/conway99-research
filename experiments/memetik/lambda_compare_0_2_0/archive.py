"""Disk-backed canonical archive: no fixed number of graph slots."""
import bootstrap
from common import core, checked, sha
from search import key
import json
import sqlite3


class Archive:
    def __init__(self, path, cache_kib=16384):
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute(f'PRAGMA cache_size=-{int(cache_kib)}')
        self.db.execute('PRAGMA journal_size_limit=16777216')
        self.db.execute('CREATE TABLE IF NOT EXISTS graphs (id INTEGER PRIMARY KEY, class TEXT UNIQUE NOT NULL, value TEXT NOT NULL, endpoint INTEGER NOT NULL DEFAULT 0)')
        self.db.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, target TEXT NOT NULL, cpu REAL NOT NULL, value TEXT NOT NULL, role TEXT NOT NULL)')
        self.db.commit()

    def put(self, item, endpoint=False):
        self.db.execute('INSERT OR IGNORE INTO graphs(class,value,endpoint) VALUES(?,?,?)',
                        (item['class'],json.dumps(item,separators=(',',':')),int(endpoint)))
        if endpoint:
            self.db.execute('UPDATE graphs SET endpoint=1 WHERE class=?',(item['class'],))
        self.db.commit()

    def record(self, target, cpu_value, item, role):
        self.db.execute('INSERT INTO records(target,cpu,value,role) VALUES(?,?,?,?)',
                        (target,cpu_value,json.dumps(item,separators=(',',':')),role))
        self.db.commit()

    def count(self, endpoints=False):
        return self.db.execute('SELECT COUNT(*) FROM graphs'+(' WHERE endpoint=1' if endpoints else '')).fetchone()[0]

    def choose(self, rng, target, explore, tournament):
        count = self.count()
        samples = []
        for _ in range(1 if rng.random() < explore else tournament):
            row = self.db.execute('SELECT value FROM graphs ORDER BY id LIMIT 1 OFFSET ?', (rng.randrange(count),)).fetchone()
            samples.append(json.loads(row[0]))
        return min(samples,key=lambda p:key(p['scores'],target))

    def close(self):
        self.db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        self.db.close()


def make_item(rows, origin, guard):
    text = core.encode_g6(rows)
    _, scores = checked(text,'lambda')
    certificate = core.canonical(tuple(rows))
    guard.check()
    return {'graph6':text,'scores':scores,'class':certificate,'state':sha(text.encode()),
            'family':origin['family'],'line':origin['line'],'parent':origin['state']}


def file_sha(path):
    """Hash growing archives without loading the full database into RAM."""
    import hashlib
    digest = hashlib.sha256()
    with open(path,'rb') as stream:
        while block := stream.read(1024*1024):
            digest.update(block)
    return digest.hexdigest()
