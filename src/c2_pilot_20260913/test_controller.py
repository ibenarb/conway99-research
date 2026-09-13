"""Process-control tests with explicit fake solvers; not proof verification."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

import pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert pilot.accepted(0, 's VERIFIED UNSAT\n', '')
    assert not pilot.accepted(1, 's VERIFIED UNSAT\n', '')
    assert not pilot.accepted(0, '', '')
    assert not pilot.accepted(0, 's VERIFIED UNSAT\n', 'error')
    assert pilot.classify(20, 's UNSATISFIABLE\n') == 'UNSAT_PENDING_CHECK'
    assert pilot.classify(10, 's SATISFIABLE\n') == 'SAT_PENDING_CHECK'
    assert pilot.classify(0, 's UNKNOWN\n') == 'TIMEOUT_OPEN'
    assert pilot.classify(20, '') == 'SOLVER_ERROR'
    assert "-t" not in pilot.command("solver", "cnf", "proof", 0, 10)
    assert "-t" in pilot.command("solver", "cnf", "proof", 30, 0)
    outcomes = {}
    original_hash, original_resources = pilot.CNF_HASH, pilot.resource_reason
    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cnf = root/'input.cnf'
            cnf.write_text('p cnf 1 2\n1 0\n-1 0\n')
            pilot.CNF_HASH = pilot.sha(cnf)
            pilot.resource_reason = lambda *a, **k: None
            for mode, expected in [('timeout', 'PILOT_OPEN'), ('unsat', 'C2_UNSAT_CERTIFIED'), ('reject', 'PILOT_ERROR')]:
                solver, cake = root/'fake_solver', root/'fake_cake'
                solver.write_text('#!' + sys.executable + '\n' + '''import sys
from pathlib import Path
if '--version' in sys.argv:
    print('2.2.1'); sys.exit(0)
p=Path(sys.argv[-1]); p.write_text('FAKE PROOF FOR CONTROLLER TEST ONLY\\n')
''' + f"mode={mode!r}\n" + '''if mode=='timeout' and p.parent.name!='controls':
    print('s UNKNOWN'); sys.exit(0)
print('s UNSATISFIABLE'); sys.exit(20)
''')
                cake.write_text('#!' + sys.executable + '\n' + '''import sys
from pathlib import Path
''' + f"mode={mode!r}\n" + '''if Path(sys.argv[1]).name=='sat.cnf' or (mode=='reject' and Path(sys.argv[2]).parent.name!='controls'):
    sys.exit(1)
print('s VERIFIED UNSAT')
''')
                solver.chmod(0o755)
                cake.chmod(0o755)
                pilot.CAKE_HASH = pilot.sha(cake)
                out = root/mode
                out.mkdir()
                with contextlib.redirect_stdout(io.StringIO()):
                    pilot.run(SimpleNamespace(out=out, solver=str(solver), cake=str(cake), cnf=str(cnf), seconds=0, workers=11))
                record = json.loads((out/'summary.json').read_text())
                assert record['status'] == expected, record
                assert (out/'inputs.json').is_file() and (out/'jobs.json').is_file()
                inputs = json.loads((out/'inputs.json').read_text())
                assert inputs['seeds'] == list(range(11)) and inputs['seconds_per_seed'] == 0
                outcomes[mode] = 'EXPECTED_CONTROLLER_TRANSITION_PASS'
            proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
            pilot.stop(proc)
            assert proc.poll() is not None
    finally:
        pilot.CNF_HASH, pilot.resource_reason = original_hash, original_resources
    report = {'status': 'CONTROLLER_TESTS_PASS', 'simulated_transitions': outcomes,
              'strict_acceptance_checks': 4, 'solver_status_checks': 4,
              'unlimited_search_and_eleven_workers': 'PASS', 'child_termination': 'PASS', 'controller_sha256': pilot.sha(Path(pilot.__file__)),
              'scope': 'Fake solver/checker process tests only; no actual LRAT verification or Conway99 result.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
