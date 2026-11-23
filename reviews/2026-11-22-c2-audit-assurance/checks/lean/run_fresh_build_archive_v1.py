from pathlib import Path
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2] / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

with (BASE / 'fresh_build_archive_identity_v1.json').open('x') as stream:
    json.dump(dict(identity=identity(os.getpid()), started=time.time()), stream, indent=4)
while not (BASE / 'ram_lean_controller_result_v3.json').exists():
    time.sleep(10)
while True:
    resource = measure()
    if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35.4:
        break
    time.sleep(10)
with (BASE / 'fresh_build_archive_v1.stdout').open('wb') as out, (BASE / 'fresh_build_archive_v1.stderr').open('wb') as err:
    result = subprocess.run(['wsl.exe', '--distribution', 'Ubuntu-24.04', '--cd', str(BASE),
                             '--exec', 'python3', 'archive_fresh_ram_build_v1.py'],
                            stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
(BASE / 'fresh_build_archive_driver_result_v1.json').write_text(json.dumps(
    dict(exit_code=result.returncode, resource=resource), indent=4))
