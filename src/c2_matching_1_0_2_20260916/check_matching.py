"""Reproduce matching coverage and targeted controller controls; no large SAT search."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from common import sha, save
from matching_orbits import check_cover


def controller_control(solver):
    import run_matching
    root = Path(tempfile.mkdtemp(prefix='c2_matching_control_'))
    (root/'partitions').mkdir()
    out = root/'run'
    out.mkdir()
    cnf = root/'unsat.cnf'
    cnf.write_text('p cnf 1 2\n1 0\n-1 0\n')
    save(root/'setup.json', {'solver': solver, 'solver_sha256': sha(solver)})
    jobs = [{'id': 'tiny_'+str(i), 'group': 'control', 'seed': 0, 'cnf': str(cnf),
             'cnf_sha256': sha(cnf), 'assumptions': []} for i in range(11)]
    save(root/'partitions/manifest.json', {'jobs': jobs, 'cover': {'transports_checked': 10395}})

    class SimulatedGuard:
        windows_dir = 'SIMULATED_IN_CONTROLLER_TEST'

        def __init__(self, *args):
            pass

        def beat(self):
            pass

        def read(self):
            return {'free_bytes': 100*1024**3}

        def close(self):
            pass

    run_matching.ROOT = root
    run_matching.Guard = SimulatedGuard
    run_matching.controller(SimpleNamespace(out=str(out), seconds=3, workers=11))
    result = json.loads((out/'summary.json').read_text())
    assert result['status'] == 'MATCHING_SEARCH_COMPLETE_NO_CERTIFICATION'
    assert len(result['results']) == 11
    assert all(r['status'] == 'UNSAT_UNCERTIFIED' for r in result['results'])
    assert not list(root.rglob('*.lrat'))
    return {'tiny_controller_jobs': 11, 'status': 'PASS', 'Windows_observer': 'simulated'}


if __name__ == '__main__':
    report = check_cover()
    if len(sys.argv) > 1:
        report['controller_control'] = controller_control(str(Path(sys.argv[1]).resolve()))
    report['production_solver_runs'] = 0
    print(json.dumps(report), flush=True)
