"""Durable run database, budget requests, immutable identities, bounded I/O."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

BASE = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def atomic(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
    with tmp.open('w') as stream:
        stream.write(canonical(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def fingerprint():
    names = ['kernel.py', 'filters.py', 'runtime.py', 'census.py', 'worker.py',
             'host_clock.ps1', 'validate.py', 'operations_test.py', 'preflight.py',
             'historical_core.py', 'requirements.txt', 'roots.tsv', 'setup.py',
             'fixtures/bvls.json', 'fixtures/reviewer_widths128.jsonl']
    hashes = {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in names}
    return {'code_hash': digest(hashes), 'files': hashes}


def connect(run):
    con = sqlite3.connect(Path(run) / 'run.sqlite', timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA synchronous=FULL')
    return con


def schema(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS roots (id INTEGER PRIMARY KEY, spec TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'PENDING', partial TEXT NOT NULL DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, started REAL, ended REAL,
            cpu REAL DEFAULT 0, state TEXT, boot TEXT, pid INTEGER, identity TEXT);
        CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, root INTEGER, session TEXT,
            pid INTEGER, identity TEXT, started REAL, ended REAL, cpu REAL DEFAULT 0,
            cpu_exact INTEGER DEFAULT 0, state TEXT, output TEXT, error TEXT);
        CREATE TABLE IF NOT EXISTS results (root INTEGER PRIMARY KEY, attempt TEXT,
            payload TEXT NOT NULL, digest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, scope TEXT, budget REAL,
            used REAL, eta TEXT, created REAL, state TEXT, seconds INTEGER, applied REAL);
        CREATE TABLE IF NOT EXISTS inputs (id INTEGER PRIMARY KEY, request TEXT, raw TEXT,
            created REAL, outcome TEXT);
    ''')


def get(con, key, default=None):
    row = con.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
    return json.loads(row[0]) if row else default


def put(con, key, value):
    con.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, canonical(value)))


def budget_tick(con, run, used, eta='unknown'):
    # One persistent request per threshold. No stdin and no blocking input anywhere.
    request = con.execute("SELECT * FROM requests WHERE state='OPEN'").fetchone()
    budget = get(con, 'budget_cpu_s')
    if request is None and used >= budget and not get(con, 'stop_requested', False):
        rid = uuid.uuid4().hex
        with con:
            con.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?,NULL,NULL)',
                        (rid, 'entire P0/P1 census run', budget, used, eta, time.time(), 'OPEN'))
        request = con.execute('SELECT * FROM requests WHERE id=?', (rid,)).fetchone()
        print(f"Run {get(con, 'run_id')}; entire P0/P1 census; aggregate CPU seconds "
              f"{used:.3f}/{budget:.3f}; request {rid}", flush=True)
        print(f'time limit reached. ETA {eta}. Extend [seconds] ?', flush=True)
    if request:
        atomic(Path(run) / 'time_request.json', dict(request) | {'run_id': get(con, 'run_id'),
                                                               'unit': 'aggregate CPU seconds'})
    return bool(request)


def answer(run, run_id, request_id, raw):
    con = connect(run)
    con.execute('BEGIN IMMEDIATE')
    try:
        if run_id != get(con, 'run_id'):
            raise ValueError('wrong run ID')
        request = con.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
        text = str(raw)
        valid = text.isascii() and text.isdigit() and len(text) <= 12
        if request is None:
            outcome = 'UNKNOWN_REQUEST'
        elif request['state'] != 'OPEN':
            outcome = 'ALREADY_PROCESSED'
        elif not valid:
            outcome = 'INVALID_INPUT_CONTINUING'
        else:
            seconds = int(text)
            outcome = 'STOP_REQUESTED' if seconds == 0 else 'EXTENDED'
            if seconds:
                put(con, 'budget_cpu_s', get(con, 'budget_cpu_s') + seconds)
            else:
                put(con, 'stop_requested', True)
            con.execute('UPDATE requests SET state=?,seconds=?,applied=? WHERE id=?',
                        (outcome, seconds, time.time(), request_id))
        con.execute('INSERT INTO inputs(request,raw,created,outcome) VALUES (?,?,?,?)',
                    (request_id, text, time.time(), outcome))
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()
    return outcome


def close_requests(con, state):
    with con:
        con.execute("UPDATE requests SET state=? WHERE state='OPEN'", (state,))


def process_stat(pid, proc_pid=None, identity=None):
    # Some container supervisors expose virtual PIDs while /proc uses host PIDs.
    # Never read an unrelated /proc/N just because subprocess returned virtual N.
    self_text = Path('/proc/self/stat').read_text()
    self_proc_pid = int(self_text.split(' ', 1)[0])
    if pid == os.getpid() and proc_pid is None:
        raw = self_text
    else:
        if proc_pid is None and self_proc_pid != os.getpid():
            return None
        proc_pid = proc_pid if proc_pid is not None else pid
        try:
            raw = Path(f'/proc/{proc_pid}/stat').read_text()
        except FileNotFoundError:
            return None
    fields = raw.rsplit(')', 1)[1].split()
    if identity is not None and fields[19] != identity:
        raise ValueError('process identity changed; refusing unrelated CPU counters')
    cpu = (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')
    return {'cpu_s': cpu, 'identity': fields[19], 'state': fields[0],
            'proc_pid': int(raw.split(' ', 1)[0])}


def resources(path):
    info = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    free = int(info['MemAvailable'].split()[0]) * 1024
    st = os.statvfs(path)
    return {'mem_available_bytes': free, 'disk_free_bytes': st.f_bavail * st.f_frsize,
            'logical_cpus': os.cpu_count(), 'loadavg': os.getloadavg()}
