import bootstrap
"""Durable run database, budget requests, immutable identities, bounded I/O."""
import contextlib
import hashlib
import json
import math
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
    names = sorted(str(f.relative_to(BASE)) for f in BASE.rglob('*')
                   if f.is_file() and '__pycache__' not in f.parts and '.venv' not in f.parts
                   and ('work' not in f.relative_to(BASE).parts)
                   and (f.suffix in ('.py', '.ps1', '.tsv') or
                        f.name in ('requirements.txt', 'supplement_manifest.json', 'bvls.json', 'reviewer_widths128.jsonl')))
    hashes = {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in names}
    return {'code_hash': digest(hashes), 'files': hashes}


def connect(run, readonly=False):
    database = Path(run) / 'run.sqlite'
    if readonly:
        con = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True, timeout=30)
        con.row_factory = sqlite3.Row
        return con
    con = sqlite3.connect(database, timeout=30)
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


def budget_tick(con, run, used, eta='unknown', announce=False):
    # One persistent request per threshold. No stdin and no blocking input anywhere.
    request = con.execute("SELECT * FROM requests WHERE state='OPEN'").fetchone()
    budget = get(con, 'budget_cpu_s')
    if request is None and used >= budget and not get(con, 'stop_requested', False):
        rid = uuid.uuid4().hex
        with con:
            con.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?,NULL,NULL)',
                        (rid, 'entire review follow-up lemma test', budget, used, eta, time.time(), 'OPEN'))
        request = con.execute('SELECT * FROM requests WHERE id=?', (rid,)).fetchone()
        print(f"Run {get(con, 'run_id')}; entire review follow-up lemma test; aggregate CPU seconds "
              f"{used:.3f}/{budget:.3f}; request {rid}", flush=True)
        print(f'time limit reached. ETA {eta}. Extend [seconds] ?', flush=True)
    elif request is not None and announce:  # K8: restarted controller shows the still-open request
        print(f"Run {get(con, 'run_id')}; entire review follow-up lemma test; aggregate CPU seconds "
              f"{used:.3f}/{budget:.3f}; request {request['id']} (open since {request['created']:.0f})",
              flush=True)
        print(f'time limit reached. ETA {eta}. Extend [seconds] ?', flush=True)
    sync_request(con)
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
        sync_request(con)
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()
    return outcome


def close_requests(con, state):
    with con:
        con.execute("UPDATE requests SET state=? WHERE state IN ('OPEN','STOP_REQUESTED')", (state,))
    sync_request(con)


def sync_request(con):
    # Lock DB while reading and replacing the mirror to prevent an old writer
    # from restoring OPEN after a concurrent answer/close. DB is authoritative.
    con.execute('BEGIN IMMEDIATE')
    try:
        row = con.execute('SELECT * FROM requests ORDER BY created DESC, rowid DESC LIMIT 1').fetchone()
        run = Path(con.execute('PRAGMA database_list').fetchone()[2]).parent
        if row:
            atomic(run / 'time_request.json', dict(row) | {'run_id': get(con, 'run_id'),
                                                        'unit': 'aggregate CPU seconds'})
        con.commit()
    except BaseException:
        con.rollback()
        raise


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


def read_host_clock(path):
    """Snapshot of the Windows clock helper file. Never raises (K2).

    Returns (data, None), (None, None) if the file is absent, or (None, reason)."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        values = [data[key] for key in ('stopwatch_s', 'utc_s', 'cpu_s')]
        if not all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in values):
            raise ValueError('non-finite or negative host clock field')
        return data, None
    except FileNotFoundError:
        return None, None
    except Exception as exc:  # partial/locale-formatted/missing keys/permission: count, never abort
        return None, repr(exc)[:200]


# SQLite WAL needs a local POSIX filesystem with shared memory (K7).
FS_DENY = {'9p', 'v9fs', 'drvfs', 'cifs', 'smb3', 'smbfs', 'nfs', 'nfs4', 'virtiofs', 'afs', 'ceph'}


def filesystem_type(path):
    target, best, fstype = str(Path(path).resolve()), '', None
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        left, right = line.split(' - ', 1)
        mount = left.split()[4].replace('\\040', ' ')
        inside = target == mount or target.startswith(mount.rstrip('/') + '/')
        if inside and len(mount) >= len(best):
            best, fstype = mount, right.split()[0]
    return fstype


def require_local_filesystem(path):
    fstype = filesystem_type(path)
    if fstype is None or fstype in FS_DENY or fstype.startswith('fuse'):
        raise ValueError(f'RUN_DIR filesystem {fstype!r} is not allowed for SQLite WAL; use the WSL '
                         'Linux filesystem (ext4 under ~), never /mnt/c, network or synced folders')
    return fstype


def resources(path):
    info = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    free = int(info['MemAvailable'].split()[0]) * 1024
    st = os.statvfs(path)
    return {'mem_available_bytes': free, 'disk_free_bytes': st.f_bavail * st.f_frsize,
            'logical_cpus': os.cpu_count(), 'loadavg': os.getloadavg()}
