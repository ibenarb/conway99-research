"""Glucose DRAT to LRAT for the 25 instances not settled by root propagation."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from pysat.solvers import Glucose4
from unit_audit import parse

base, output = Path(sys.argv[1]), Path(sys.argv[2])
drat_trim, lrat_check = sys.argv[3:5]
records = json.loads((output/'unit_audit.json').read_text())['records']
results = []
started = time.monotonic()
for rec in records:
    if rec['status'] != 'NOT_ROOT_UP':
        continue
    cnf = base/rec['path']
    dest = output/Path(rec['path']).with_suffix('.lrat')
    dest.parent.mkdir(parents=True, exist_ok=True)
    header, clauses = parse(cnf)
    tick = time.monotonic()
    with Glucose4(bootstrap_with=clauses, with_proof=True) as solver:
        assert solver.solve() is False, rec['path']
        proof = solver.get_proof()
    drat = dest.with_suffix('.drat')
    drat.write_text('\n'.join(proof)+'\n')
    trim = subprocess.run([drat_trim, str(cnf), str(drat), '-L', str(dest)], capture_output=True)
    dest.with_suffix('.trim.out').write_bytes(trim.stdout)
    dest.with_suffix('.trim.err').write_bytes(trim.stderr)
    assert trim.returncode == 0 and b's VERIFIED' in trim.stdout
    check = subprocess.run([lrat_check, str(cnf), str(dest)], capture_output=True)
    dest.with_suffix('.check.out').write_bytes(check.stdout)
    dest.with_suffix('.check.err').write_bytes(check.stderr)
    assert check.returncode == 0 and b'c VERIFIED' in check.stdout.splitlines()
    row = dict(path=rec['path'], status='GLUCOSE_DRAT_TO_LRAT_CHECKED',
               cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),
               proof_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
               seconds=time.monotonic()-tick, proof_bytes=dest.stat().st_size)
    results.append(row)
    (output/'remaining_audit.json').write_text(json.dumps(results, indent=2)+'\n')
    elapsed = time.monotonic()-started
    print('CHECKED',len(results),'/ 25',rec['path'],'seconds',round(row['seconds'],2),'ETA_seconds',round(elapsed/len(results)*(25-len(results))),flush=True)
assert len(results) == 25
