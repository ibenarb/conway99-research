"""Retry only proven pre-search resource refusals from the immutable main controller."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
with (BASE/'retry_controller_identity_v1.json').open('x') as out:
    json.dump(dict(identity=identity(os.getpid()),started=time.time()),out,indent=4)
seen=set()
active=None
results=[]
while True:
    if active and active['process'].poll() is not None:
        active['out'].close()
        active['err'].close()
        cid=active['chart']
        result=BASE/'jobs'/str(cid)/'result.json'
        data=json.loads(result.read_text()) if result.exists() else {}
        results.append(dict(chart=cid,exit_code=active['process'].returncode,status=data.get('status','MISSING_RESULT')))
        active=None
    progress=json.loads((BASE/'full_progress.json').read_text())
    retryable=[]
    for failure in progress.get('failures',[]):
        cid=failure['chart']
        if cid in seen or failure.get('status')!='MISSING_RESULT':
            continue
        stderr=BASE/'driver_logs'/f'{cid}.stderr'
        text=stderr.read_text() if stderr.exists() else ''
        proved=('system_busy_cpu' in text and 'AssertionError' in text
                and 'run_one_singleton_v2.py' in text
                and not (BASE/'jobs'/str(cid)).exists()
                and str(cid) not in progress.get('active',{}))
        if proved:
            retryable.append(cid)
    resource=measure()
    gate=(max(x['system_busy_cpu'] for x in resource['intervals'])+2<=20
          and resource['ram_free_gib']>=12 and resource['disk_free_gib']>=35.4)
    if retryable and active is None and gate:
        cid=min(retryable)
        # The main controller has already reaped this process and removed the key.
        # Its fixed todo list contains each chart once, so it cannot restart this key.
        directory=BASE/'retry_logs'
        directory.mkdir(exist_ok=True)
        out=(directory/f'{cid}.stdout').open('xb')
        err=(directory/f'{cid}.stderr').open('xb')
        process=subprocess.Popen([sys.executable,'run_one_singleton_v3.py',str(cid)],cwd=BASE,
            stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        active=dict(chart=cid,process=process,out=out,err=err)
        seen.add(cid)
    snapshot=dict(status='MONITORING_RESOURCE_REFUSALS',updated=time.time(),resource=resource,
                  attempted=sorted(seen),results=results,
                  active=dict(chart=active['chart'],pid=active['process'].pid) if active else None,
                  main_status=progress['status'])
    (BASE/'retry_progress_v1.json').write_text(json.dumps(snapshot,indent=4))
    if progress['status']=='ALL_JOBS_FINISHED_RECONCILIATION_REQUIRED' and not active and not retryable:
        break
    time.sleep(10)
