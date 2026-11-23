"""Guarded single-slot orchestration; no timeouts, no duplicated stages, durable output logs."""
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

source = BASE / 'run_ram_lean_phase_v1.py'
expected = hashlib.sha256(source.read_bytes()).hexdigest()
with (BASE / 'ram_lean_controller_identity_v1.json').open('x') as stream:
    json.dump(dict(identity=identity(os.getpid()), started=time.time(), source_sha256=expected), stream, indent=4)
while not (BASE / 'ram_prepare_result_v1.json').exists():
    assert not (BASE / 'ram_prepare_error_v1.json').exists(), 'RAM preparation failed'
    time.sleep(10)
assert json.loads((BASE / 'ram_prepare_result_v1.json').read_text())['status'] == 'RAM_BUILD_TREE_READY'
records = []
for phase in ['build', 'axioms', 'comparator', 'paranoid']:
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    assert not (BASE / ('ram_' + phase + '_started_v1.json')).exists(), 'Phase already attempted'
    while True:
        resource = measure()
        if max(x['system_busy_cpu'] for x in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 13 and resource['disk_free_gib'] >= 35.4:
            break
        (BASE / 'ram_lean_wait_v1.json').write_text(json.dumps(dict(phase=phase, resource=resource), indent=4))
        time.sleep(10)
    started = time.time()
    command = ['wsl.exe', '--distribution', 'Ubuntu-24.04', '--cd', str(BASE), '--exec',
               'python3', 'run_ram_lean_phase_v1.py', phase]
    with (BASE / ('ram_' + phase + '_v1.stdout')).open('wb') as out, (BASE / ('ram_' + phase + '_v1.stderr')).open('wb') as err:
        result = subprocess.run(command, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    records.append(dict(phase=phase, exit_code=result.returncode, started=started,
                        elapsed_seconds=time.time() - started, resource=resource))
    report = dict(status='STAGES_RUNNING' if result.returncode == 0 else 'STAGE_ERROR_NO_C3_REBUILD_VERDICT',
                  records=records, source_sha256=expected)
    (BASE / 'ram_lean_controller_progress_v1.json').write_text(json.dumps(report, indent=4))
    if result.returncode:
        break
else:
    report['status'] = 'ALL_FOUR_COMMAND_STAGES_PASSED_AUDIT_PENDING'
(BASE / 'ram_lean_controller_result_v1.json').write_text(json.dumps(report, indent=4))
