"""Separate controller for S1. Research code remains immutable during the run."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def safe_identity(pid):
    try:
        return identity(pid)
    except (AssertionError,ProcessLookupError,OSError):
        return None

def write_status(value):
    temporary=BASE/'full_progress.json.tmp'
    temporary.write_text(json.dumps(value,indent=4))
    temporary.replace(BASE/'full_progress.json')

def main():
    plan=json.loads((BASE/'jobs_manifest_v1.json').read_text())
    assert len(plan['search_charts'])==3308 and len(plan['nonphysical'])==272
    assert set(plan['search_charts']).isdisjoint(plan['nonphysical'])
    assert set(plan['search_charts'])|set(plan['nonphysical'])==set(range(3580))
    control=json.loads((BASE/'controls_result_v1.json').read_text())
    assert control['status']=='SINGLETON_CORE_CONTROLS_PASS'
    for name in ['singleton_exact_v1.cpp','singleton_exact_v1_checked']:
        assert sha(BASE/name)==control['hashes'][name]
    frozen={name:sha(BASE/name) for name in ['singleton_exact_v1.cpp','singleton_exact_v1_checked',
        'singleton_setup_v1.py','own_local.py','own_setup.py','layouts.tsv',
        'run_one_singleton_v2.py','jobs_manifest_v1.json']}
    with (BASE/'controller_identity_v1.json').open('x') as f:
        json.dump(dict(identity=identity(os.getpid()),started=time.time(),hashes=frozen),f,indent=4)
    while True:
        pilots=[]
        for cid in plan['pilot_charts']:
            result=BASE/'jobs'/str(cid)/'result.json'
            if result.exists():
                pilots.append(json.loads(result.read_text()))
        if len(pilots)==3:
            if not all(x['status']=='SECOND_SINGLETON_SOLVER_CLOSED' for x in pilots):
                write_status(dict(status='PILOT_REQUIRES_INVESTIGATION',pilots=pilots))
                return
            break
        write_status(dict(status='WAITING_FOR_THREE_PILOTS',finished=[x['chart'] for x in pilots],updated=time.time()))
        time.sleep(10)
    closed=list(plan['pilot_charts'])
    todo=[x for x in plan['search_charts'] if x not in closed]
    # Existing unclaimed outputs are never overwritten or silently skipped.
    for cid in todo:
        assert not (BASE/'jobs'/str(cid)).exists(),('Existing job requires inspection',cid)
    active={}
    failures=[]
    launched=len(closed)
    while todo or active:
        for cid,item in list(active.items()):
            code=item['process'].poll()
            if code is None:
                continue
            item['out'].close()
            item['err'].close()
            result_file=BASE/'jobs'/str(cid)/'result.json'
            result=json.loads(result_file.read_text()) if result_file.exists() else {}
            if code==0 and result.get('status')=='SECOND_SINGLETON_SOLVER_CLOSED':
                assert result['roots_completed']==result['roots_planned']
                closed.append(cid)
            else:
                failures.append(dict(chart=cid,exit_code=code,status=result.get('status','MISSING_RESULT')))
            del active[cid]
        resource=measure()
        gate=(max(x['system_busy_cpu'] for x in resource['intervals'])+len(active)+2<=20
              and resource['ram_free_gib']>=10+2*(len(active)+1)
              and resource['disk_free_gib']>=35.4)
        if todo and len(active)<2 and gate:
            for name,digest in frozen.items():
                assert sha(BASE/name)==digest,('Bound source changed',name)
            cid=todo.pop(0)
            logdir=BASE/'driver_logs'
            logdir.mkdir(exist_ok=True)
            out=(logdir/f'{cid}.stdout').open('xb')
            err=(logdir/f'{cid}.stderr').open('xb')
            p=subprocess.Popen([sys.executable,'run_one_singleton_v2.py',str(cid)],cwd=BASE,
                stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            active[cid]=dict(process=p,identity=safe_identity(p.pid),out=out,err=err)
            launched+=1
        status=dict(status='RUNNING',updated=time.time(),all_charts=3580,nonphysical_closed=272,
                    planned=3308,launched=launched,closed=len(closed),closed_keys=sorted(closed),
                    active={str(cid):dict(pid=x['process'].pid,identity=x['identity']) for cid,x in active.items()},
                    pending=len(todo),failures=failures,resource=resource,admission_open=gate)
        write_status(status)
        if todo or active:
            time.sleep(5)
    status['status']='ALL_JOBS_FINISHED_RECONCILIATION_REQUIRED'
    write_status(status)

if __name__=='__main__':
    main()
