"""Test 22-worker execution and wave barrier using a dummy solver, simulated guard."""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import run_matching
from common import save, sha


def check():
    root = Path(tempfile.mkdtemp(prefix='counter_ab_control_'))
    (root / 'partitions').mkdir()
    out = root / 'run'
    out.mkdir()
    solver = root / 'dummy_solver'
    solver.write_text('#!/usr/bin/env python3\nimport time\ntime.sleep(0.1)\nprint("s UNSATISFIABLE")\nraise SystemExit(20)\n')
    solver.chmod(0o755)
    cnf = root / 'unsat.cnf'
    cnf.write_text('p cnf 1 2\n1 0\n-1 0\n')
    save(root / 'setup.json', {'solver': str(solver), 'solver_sha256': sha(solver)})
    jobs = [dict(id=f'{g}__tiny_{i}', group=g, seed=0, cnf=str(cnf),
                 cnf_sha256=sha(cnf), assumptions=[]) for g in ('totalizer',) for i in range(11)]
    save(root / 'partitions/manifest.json', {'jobs': jobs, 'cover': {'transports_checked': 10395}})
    class Guard:
        windows_dir = 'SIMULATED'
        def __init__(self, *args):
            pass
        def beat(self):
            pass
        def read(self):
            return {'free_bytes': 100 * 1024**3}
        def close(self):
            pass
    run_matching.ROOT, run_matching.LOCK_PATH = root, root / 'lock'
    run_matching.Guard = Guard
    run_matching.controller(SimpleNamespace(out=str(out), seconds=3, workers=11))
    report = json.loads((out / 'summary.json').read_text())
    assert report['status'] == 'TOTALIZER_LONG_COMPLETE_NO_CERTIFICATION', report
    assert len(report['results']) == 11
    assert all(r['status'] == 'UNSAT_UNCERTIFIED' for r in report['results'])
    assert not list(root.rglob('*.lrat'))
    return dict(status='PASS', completed=11, budget_limit_seconds=64800,
                solver='dummy; control-flow test only', Windows_guard='simulated')


if __name__ == '__main__':
    print(json.dumps(check()), flush=True)
