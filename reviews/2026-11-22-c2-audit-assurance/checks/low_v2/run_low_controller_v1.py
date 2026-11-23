from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(value):
    temporary = BASE/'full_progress.tmp'
    temporary.write_text(json.dumps(value,indent=4))
    temporary.replace(BASE/'full_progress.json')

def main():
    own_identity = identity(os.getpid())
    with (BASE/'controller_identity.json').open('x') as out:
        json.dump(dict(identity=own_identity,started=time.time(),max_workers=2),out,indent=4)
    manifest = json.loads((BASE/'jobs_manifest.json').read_text())
    for p,h in manifest['source_hashes'].items():
        assert sha(BASE/p) == h
    for name,expected in [('gram_controls_result.json','GRAM_CONTROLS_PASS'),
                          ('pair_controls_result.json','EXACT_PAIR_CONTROLS_PASS')]:
        control = json.loads((BASE/name).read_text())
        assert control['status'] == expected and sha(BASE/'residual_gram_v1.cpp') == control['hashes']['residual_gram_v1.cpp']
    pilot = json.loads((BASE/'jobs/306.0/result.json').read_text())
    assert pilot['status'] == 'SECOND_LOW_SOLVER_CLOSED' and pilot['closed_planes'] == 2786
    pending, closed, failures = [], [], []
    for job in manifest['jobs']:
        directory = BASE/'jobs'/job['id']
        if directory.exists():
            result = json.loads((directory/'result.json').read_text())
            assert result['status'] == 'SECOND_LOW_SOLVER_CLOSED' and result['stars'] == job['stars']
            assert result['source_hashes']['residual_gram_v1.cpp'] == sha(BASE/'residual_gram_v1.cpp')
            closed.append(job['id'])
        else:
            pending.append(job)
    active = {}
    handles = {}
    while pending or active:
        for key,process in list(active.items()):
            if process.poll() is None:
                continue
            for stream in handles.pop(key):
                stream.close()
            result_path = BASE/'jobs'/key/'result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else {}
            if process.returncode == 0 and result.get('status') == 'SECOND_LOW_SOLVER_CLOSED':
                closed.append(key)
            else:
                failures.append(dict(id=key,exit_code=process.returncode,status=result.get('status','LAUNCH_ERROR_NOT_EXCLUSION')))
            del active[key]
        resource = measure()
        busy = max(row['system_busy_cpu'] for row in resource['intervals'])
        # Additional idle/startup margin, besides the required four-CPU reserve.
        admissible = (busy+len(active)+2 <= 20 and resource['disk_free_gib'] >= 35
                      and resource['ram_free_gib'] >= 8+2*(len(active)+1))
        if pending and len(active) < 2 and admissible:
            job = pending.pop(0)
            key = job['id']
            out = (BASE/f'launch_{key}.stdout').open('wb')
            err = (BASE/f'launch_{key}.stderr').open('wb')
            process = subprocess.Popen([sys.executable,'-B','run_one_low_v1.py',str(job['chart']),str(job['own_parity'])],
                                       cwd=BASE,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            active[key] = process
            handles[key] = (out,err)
        save(dict(status='RUNNING',updated=time.time(),planned=92,closed=len(closed),closed_keys=closed,
                  active={k:dict(pid=p.pid,identity=identity(p.pid)) for k,p in active.items()},
                  pending=len(pending),failures=failures,resource=resource,admission_open=admissible))
        if pending or active:
            time.sleep(10)
    save(dict(status='ALL_JOBS_FINISHED_RECONCILIATION_REQUIRED',updated=time.time(),
              planned=92,closed=len(closed),closed_keys=closed,active={},pending=0,failures=failures))
    # No automatic claim of S3 completion: independent coverage/hash reconciliation remains.

if __name__ == '__main__':
    main()
