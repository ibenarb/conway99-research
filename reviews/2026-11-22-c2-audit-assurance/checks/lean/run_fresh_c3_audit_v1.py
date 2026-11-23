"""One-shot, resource-gated post-build audit; no reruns or source changes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2] / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

source = BASE / 'audit_fresh_c3_v1.py'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
with (BASE / 'fresh_c3_audit_identity_v1.json').open('x') as stream:
    json.dump(dict(identity=identity(os.getpid()), source_sha256=source_hash, started=time.time()), stream, indent=4)
while not (BASE / 'fresh_build_archive_driver_result_v1.json').exists():
    time.sleep(10)
archive_driver = json.loads((BASE / 'fresh_build_archive_driver_result_v1.json').read_text())
if archive_driver['exit_code'] != 0:
    report = dict(status='ARCHIVE_FAILED_AUDIT_NOT_STARTED', archive_driver=archive_driver)
else:
    controller = json.loads((BASE / 'ram_lean_controller_result_v3.json').read_text())
    if controller['status'] != 'ALL_FOUR_COMMAND_STAGES_PASSED_AUDIT_PENDING':
        report = dict(status='CHECKER_STAGE_INCOMPLETE_NO_ACCEPTANCE', controller_status=controller['status'])
    else:
        while True:
            resource = measure()
            if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35:
                break
            time.sleep(10)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
        with (BASE / 'fresh_c3_audit_v1.stdout').open('wb') as out, (BASE / 'fresh_c3_audit_v1.stderr').open('wb') as err:
            result = subprocess.run(['wsl.exe', '--distribution', 'Ubuntu-24.04', '--cd', str(BASE),
                                     '--exec', 'python3', 'audit_fresh_c3_v1.py'],
                                    stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
        report = dict(status='AUDIT_PROCESS_FINISHED' if result.returncode == 0 else 'AUDIT_ERROR_NO_ACCEPTANCE',
                      exit_code=result.returncode, resource=resource, source_sha256=source_hash)
(BASE / 'fresh_c3_audit_driver_result_v1.json').write_text(json.dumps(report, indent=4))
