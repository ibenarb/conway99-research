"""One real process interruption: HUP survival, SQLite rollback, resume."""
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / 'releases/Conway99_Escape_Office_0.2.1.pyz'
with tempfile.TemporaryDirectory() as directory:
    run = Path(directory) / 'run'
    common = ['--run-dir', str(run), '--only', 'HoG57338__bfs_F', '--cpu-seconds', '8', '--max-depth', '3', '--max-states', '1000', '--workers', '1']
    launch = subprocess.run([sys.executable, str(APP), 'start'] + common, capture_output=True, text=True, check=True)
    record = json.loads(launch.stdout)
    pid = record['pid']
    try:
        os.kill(pid, signal.SIGHUP)
        deadline = time.monotonic() + 15
        committed = 0
        database = run / 'HoG57338__bfs_F.sqlite'
        while time.monotonic() < deadline:
            if database.exists():
                with sqlite3.connect(database) as db:
                    try:
                        committed = db.execute('SELECT COUNT(*) FROM nodes WHERE expanded=1').fetchone()[0]
                    except sqlite3.OperationalError:
                        pass
            if committed:
                break
            time.sleep(0.1)
        assert committed > 0, 'No committed expansion after SIGHUP'
        os.killpg(pid, signal.SIGKILL)
    finally:
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    retry = subprocess.run([sys.executable, str(APP), 'run'] + common, capture_output=True, text=True, check=True, timeout=30)
    result = json.loads((run / 'HoG57338__bfs_F.json').read_text())
    with sqlite3.connect(database) as db:
        integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
    assert integrity == 'ok'
    assert result['expanded'] >= committed
    assert result['status'] == 'CPU_BUDGET'
    assert not result['component_complete']
    print(json.dumps({'test': 'SIGHUP, kill process group during search, resume same checkpoint', 'pass': True, 'committed_before_kill': committed, 'expanded_after_resume': result['expanded'], 'sqlite_integrity': integrity, 'final_status': result['status']}))
