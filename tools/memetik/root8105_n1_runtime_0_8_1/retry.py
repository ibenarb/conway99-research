"""One new Root210 test, linked to the unchanged stopped predecessor."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import accounting
import calibration
import runtime as r

DIAGNOSIS_SHA = 'b7c133be4e60d0bdb6481cecca74a0d4eb9cc668b2af7387ab666064bc106034'


def prepare(output):
    workspace = Path.home()/'conway99_workspace'
    oldbase = workspace/'ROOT8105_N1_Kalibrierung_20261008'
    old = oldbase/'r210_class000'
    if output.exists():
        raise ValueError('Output exists; refusing to overwrite')
    archive = Path(__file__).with_name('STOP_DIAGNOSIS.zip')
    if r.sha(archive) != DIAGNOSIS_SHA:
        raise ValueError('Changed predecessor evidence')
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            path = oldbase/name
            if path.read_bytes() != z.read(name):
                raise ValueError('Predecessor changed: '+name)
    state = r.read(old/'state.json')
    if state['status'] != 'RESOURCE_STOPPED' or state['child'] is not None:
        raise ValueError('Predecessor not closed')
    # Complete old CLI receipts, with the exact resource-only fault reclassified.
    accounts = accounting.inventory(old)
    if not accounts['observed_commands_complete'] or accounts['active']:
        raise ValueError('Predecessor accounting is not complete')
    predecessor = dict(root=str(old), run_id=state['run_id'],
                       diagnosis_sha256=DIAGNOSIS_SHA,
                       native_cpu_s=accounts['native_search_confirmed_s'],
                       aggregate_cpu_lower_bound_s=accounts['accounted_lower_bound_s'],
                       old_state_sha256=r.sha(old/'state.json'),
                       restart_kind='new_search_no_CDCL_checkpoint', old_files_modified=False,
                       budgets='New test: native 21600s and aggregate 28800s; predecessor retained separately')
    # Controls exercise only their own temporary processes and synthetic samples.
    control_log = output.with_name(output.name+'-pause-control.log')
    with control_log.open('xb') as log:
        subprocess.run([sys.executable, '-m', 'unittest', 'test_memory_pause', 'test_resource_accounts'],
                       cwd=Path(__file__).parent, stdout=log, stderr=subprocess.STDOUT, check=True)
    receipt = calibration.prepare(output, roots=(210,))
    r.raw_atomic(output/'PREDECESSOR.json', predecessor)
    r.raw_atomic(output/'PRESSURE_CONTROL.json', dict(status='PASS',
                 pressure_samples='synthetic, isolated from real run',
                 process_signals='real on current target', log_sha256=r.sha(control_log)))
    print(json.dumps(dict(status='RETRY_READY', predecessor=predecessor,
                         run=str(output/'r210_class000'), solver_started=False), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    prepare(parser.parse_args().output.resolve())
