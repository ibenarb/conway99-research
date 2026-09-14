"""Simulated process tests; not LRAT verification."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import calibrate as c


def main():
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cnf = root/'input.cnf'
        cnf.write_text('p cnf 1 2\n1 0\n-1 0\n')
        solver = root/'solver'
        jobs = [{'id': 'cube_'+str(i), 'kind': 'cube', 'seed': 0, 'assumptions': [], 'cnf': str(cnf), 'sha256': c.p.sha(cnf)} for i in range(8)]
        jobs += [{'id': 'baseline_'+str(i), 'kind': 'baseline', 'seed': i, 'assumptions': [], 'cnf': str(cnf), 'sha256': c.p.sha(cnf)} for i in range(3)]
        c.p.resource_reason = lambda out: None
        for mode, expected in [('none', 'CALIBRATION_OPEN'), ('one', 'CALIBRATION_OPEN'), ('cubes', 'ALL_EIGHT_CUBES_CERTIFIED'), ('baseline', 'BASELINE_UNSAT_CERTIFIED'), ('reject', 'CALIBRATION_ERROR')]:
            solver.write_text('#!'+sys.executable+'\nimport sys\nfrom pathlib import Path\np=Path(sys.argv[-1]); p.write_text("MOCK ONLY")\nname=p.parent.name\nmode='+repr(mode)+'\nyes=(mode in ("one","reject") and name=="cube_0") or (mode=="cubes" and name.startswith("cube_")) or (mode=="baseline" and name=="baseline_0")\nprint("s UNSATISFIABLE" if yes else "s UNKNOWN")\nsys.exit(20 if yes else 0)\n')
            solver.chmod(0o755)
            def checker(cake, input_path, proof, folder, out):
                assert c.p.sha(input_path) == c.p.CNF_HASH
                assert proof.read_text() == 'MOCK ONLY'
                return {'status': 'CHECK_FAILED' if mode == 'reject' else 'UNSAT_CERTIFIED', 'scope': 'SIMULATION ONLY'}
            c.p.check_proof = checker
            out = root/mode
            out.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                report = c.execute(jobs, out, solver, 'unused', 10)
            assert report['status'] == expected, report
            assert len(report['jobs']) == 11
            assert all(r['status'] != 'RUNNING' for r in report['jobs'])
            results[mode] = 'PASS'
    print(json.dumps({'status': 'SIMULATED_CONTROLLER_TESTS_PASS', 'cases': results, 'scope': 'Fake solver and fake certificate checker; no mathematical proof verification.'}))


if __name__ == '__main__':
    main()
