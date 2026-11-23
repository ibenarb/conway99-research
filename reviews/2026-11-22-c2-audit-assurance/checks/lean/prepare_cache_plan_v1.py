from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
resource=measure()
assert max(x['system_busy_cpu'] for x in resource['intervals'])+1<=20
assert resource['ram_free_gib']>=10 and resource['disk_free_gib']>=35.2
assert json.loads((BASE/'cachetool_result_v1.json').read_text())['status']=='CACHE_TOOL_READY'
files=list((BASE/'c3formal/C3formal').glob('*.lean'))+[BASE/'c3formal/Challenge.lean',BASE/'c3formal/Solution.lean']
modules=set()
for file in files:
    for line in file.read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('import Mathlib.'):
            parts=line.split('--',1)[0].split()[1:]
            assert all(re.fullmatch(r'Mathlib[.A-Za-z0-9_]+',name) for name in parts)
            modules.update(parts)
assert modules
record=dict(status='PLANNING',identity=identity(os.getpid()),resource=resource,modules=sorted(modules),started=time.time())
with (BASE/'cache_plan_started_v1.json').open('x') as f:
    json.dump(record,f,indent=4)
command=['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec',
         'python3','lean_exec_v1.py','env','lean','--run','../CachePlan_v1.lean']+sorted(modules)
with (BASE/'cache_plan_v1.stdout').open('wb') as out,(BASE/'cache_plan_v1.stderr').open('wb') as err:
    result=subprocess.run(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
record.update(status='PLAN_READY' if result.returncode==0 else 'PLAN_ERROR_NO_PROOF_VERDICT',
              exit_code=result.returncode,elapsed_seconds=time.time()-record['started'])
(BASE/'cache_plan_result_v1.json').write_text(json.dumps(record,indent=4))
print(json.dumps(record),flush=True)
