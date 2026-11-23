from pathlib import Path
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity


def main():
    assert json.loads((BASE/'pilot_v3_result.json').read_text())['status'] == 'SECOND_SOLVER_PILOT_PASS'
    plan = json.loads((BASE/'jobs_manifest.json').read_text())
    assert len(plan['jobs']) == 3156
    lock = BASE/'controller_identity.json'
    with lock.open('x') as f:
        json.dump({'identity':identity(os.getpid()),'started':time.time(),'max_own_workers':4,'timeout':None}, f, indent=4)
    (BASE/'jobs').mkdir(exist_ok=True)
    active = {}
    launched = set()
    for job in plan['jobs']:
        p = BASE/'jobs'/job['id']
        if p.exists():
            raise RuntimeError('An earlier job exists; reconcile before a restart.')
    while True:
        for jid, item in list(active.items()):
            if item['process'].poll() is not None:
                item['out'].close()
                item['err'].close()
                del active[jid]
        results = []
        for path in (BASE/'jobs').glob('*/result.json'):
            results.append(json.loads(path.read_text()))
        closed = sum(r['status']=='SECOND_SOLVER_CLOSED' for r in results)
        failures = [r['job']['id'] for r in results if r['status']!='SECOND_SOLVER_CLOSED']
        sample = measure()
        busy = max(x['system_busy_cpu'] for x in sample['intervals'])
        gate = busy+len(active)+1 <= 20 and sample['ram_free_gib'] >= 8+2*(len(active)+1) and sample['disk_free_gib'] >= 35
        pending = [j for j in plan['jobs'] if j['id'] not in launched]
        eligible = [j for j in pending if j['kind']=='baseline' or (BASE/'orbits_result.json').exists()]
        if len(active)<4 and eligible and gate:
            job = eligible[0]
            jid = job['id']
            out = (BASE/'jobs'/f'{jid}.driver.stdout').open('wb')
            err = (BASE/'jobs'/f'{jid}.driver.stderr').open('wb')
            p = subprocess.Popen([sys.executable,'-u',str(BASE/'run_one_high_v1.py'),jid],cwd=BASE,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
            active[jid]={'process':p,'out':out,'err':err}
            launched.add(jid)
        record = {'updated':time.time(),'status':'RUNNING' if active or pending else ('COMPLETE_SECOND_SOLVER_CLOSED' if closed==3156 else 'INCOMPLETE_WITH_ERRORS'),'planned':3156,'launched':len(launched),'closed':closed,'failures':failures,'active':{k:v['process'].pid for k,v in active.items()},'pending':len(plan['jobs'])-len(launched),'resource':sample,'admission_open':gate,'original_solver_modified':False}
        temp=BASE/'full_progress.tmp'
        temp.write_text(json.dumps(record,indent=4))
        os.replace(temp,BASE/'full_progress.json')
        if not active and not pending:
            break
        time.sleep(10)


if __name__ == '__main__':
    main()
