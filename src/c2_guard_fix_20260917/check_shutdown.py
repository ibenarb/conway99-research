"""Real dummy workers/children; injected permanent guard failure must stop all."""
import errno
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
import run_matching as rm
from common import save, sha
from windows_guard import Guard as RealGuard


def run():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'partitions').mkdir()
        out = root / 'run'
        out.mkdir()
        solver = root / 'dummy_solver'
        solver.write_text('#!/usr/bin/env python3\nimport os,sys,time\nfrom pathlib import Path\nPath(sys.argv[-1]).with_suffix(".pid").write_text(str(os.getpid()))\ntime.sleep(60)\n')
        solver.chmod(0o755)
        jobs = []
        for i in range(11):
            cnf = root / f'job_{i}.cnf'
            cnf.write_text('p cnf 1 1\n1 0\n')
            jobs.append(dict(id=f'totalizer__tiny_{i}', group='totalizer', seed=0,
                             cnf=str(cnf), cnf_sha256=sha(cnf), assumptions=[]))
        save(root / 'setup.json', {'solver': str(solver), 'solver_sha256': sha(solver)})
        save(root / 'partitions/manifest.json', {'jobs': jobs, 'cover': {'transports_checked': 10395}})

        class Guard:
            windows_dir = 'SIMULATED'
            write_retries = 0
            def __init__(self, *args):
                self.calls = 0
            def beat(self):
                self.calls += 1
                if self.calls > 1:
                    assert len(list(root.glob('*.pid'))) == 11, 'Dummy children did not all start'
                    actual = RealGuard.__new__(RealGuard)
                    actual.directory = root
                    actual.write_retries = 0
                    def deny(*args):
                        raise PermissionError(errno.EACCES, 'persistent injected')
                    try:
                        with patch.object(Path, 'replace', side_effect=deny):
                            actual.beat()
                    finally:
                        self.write_retries = actual.write_retries
            def read(self):
                return {'free_bytes': 100 * 1024**3}
            def close(self):
                pass

        with patch.object(rm, 'ROOT', root), patch.object(rm, 'LOCK_PATH', root / 'lock'), patch.object(rm, 'Guard', Guard), patch.object(rm, 'linux_safety', return_value={'output_bytes': 0}):
            rm.controller(SimpleNamespace(out=str(out), seconds=60, workers=11))
        report = json.loads((out / 'summary.json').read_text())
        assert report['status'] == 'TOTALIZER_LONG_FAILED'
        assert 'WINDOWS_HEARTBEAT_WRITE_FAILED' in report['error']
        assert len(report['interrupted_jobs']) == 11 and report['guard_write_retries'] > 0
        deadline = time.monotonic() + 5
        while True:
            alive = []
            for file in root.glob('*.pid'):
                stat = Path('/proc') / file.read_text() / 'stat'
                if stat.exists() and stat.read_text().split(') ', 1)[1][0] != 'Z':
                    alive.append(file.read_text())
            if not alive or time.monotonic() >= deadline:
                break
            time.sleep(.05)
        assert not alive, alive
        assert not list(root.rglob('*.lrat'))
        return {'status': 'GUARD_FAILURE_SHUTDOWN_PASS', 'dummy_solver_children': 11,
                'remaining_live_solver_children': 0, 'proof_files': 0,
                'scope': 'Real Linux controller cleanup and parent-death signals; Windows killer not exercised.'}


if __name__ == '__main__':
    print(json.dumps(run()))
