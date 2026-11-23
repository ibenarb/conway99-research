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
with (BASE/'cache_expansion_identity_v1.json').open('x') as out:
    json.dump(dict(identity=identity(os.getpid()),started=time.time()),out,indent=4)
while True:
    r=measure()
    if max(x['system_busy_cpu'] for x in r['intervals'])+1<=20 and r['ram_free_gib']>=14 and r['disk_free_gib']>=35.4:
        break
    time.sleep(10)
with (BASE/'cache_expansion_v1.stdout').open('wb') as out,(BASE/'cache_expansion_v1.stderr').open('wb') as err:
    p=subprocess.run(['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec',
                      'python3','preflight_cache_expansion_v1.py'],stdout=out,stderr=err,
                      creationflags=subprocess.CREATE_NO_WINDOW)
(BASE/'cache_expansion_driver_result_v1.json').write_text(json.dumps(dict(exit_code=p.returncode,resource=r),indent=4))
