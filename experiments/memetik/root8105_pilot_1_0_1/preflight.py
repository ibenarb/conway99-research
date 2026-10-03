"""Target-machine correctness tests and concurrent real-path calibration."""
import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import psutil
from campaign import code_fingerprint
from core import atomic
from selftest import run_tests
from depth_controls import run_tests as depth_tests
from level2 import benchmark
from operations_test import controls as operation_controls

BASE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    args = p.parse_args()
    out = Path(args.directory).resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    controls = out / ('preflight_' + str(time.time_ns()))
    controls.mkdir()
    fingerprint_before = code_fingerprint()
    started = 0.0  # Include preflight interpreter/import CPU.
    children0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    result = run_tests(controls / 'controls')
    depth_tests(controls / 'depth_controls')
    operation_controls(controls / 'pause_resume')
    atomic(out / 'level2_benchmark.json', benchmark(json.loads((out / 'selected_roots.json').read_text())))
    cfg = dict(manifest['config'])
    cfg.update({'job_cpu_s': 20, 'node_cpu_s': 2, 'projection_cap': 4096,
                'proofs_per_job': 0, 'beam_width': 8, 'row_reservoir': 8})
    calibration = controls / 'calibration'
    (calibration / 'jobs').mkdir(parents=True)
    names = manifest['jobs'][:manifest['config']['workers']]
    # One concurrent wave; no fabricated speedup or full campaign ETA.
    atomic(calibration / 'manifest.json', {'jobs': names, 'config': cfg})
    for name in names:
        job = json.loads((out / 'jobs' / (name + '.json')).read_text())
        job['config'] = cfg
        atomic(calibration / 'jobs' / (name + '.json'), job)
    checked = subprocess.run([sys.executable, str(BASE / 'campaign.py'), str(calibration), '--test'],
                             stdout=(controls / 'calibration.log').open('w'), stderr=subprocess.STDOUT,
                             timeout=1200)
    if checked.returncode:
        raise RuntimeError('calibration controller failed')
    receipts = json.loads((calibration / 'receipts.json').read_text())
    if len(receipts) != len(names) or any(r['exit'] != 0 for r in receipts):
        raise RuntimeError('not every calibration task finished cleanly')
    children1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    auxiliary = (time.process_time() - started + children1.ru_utime + children1.ru_stime
                 - children0.ru_utime - children0.ru_stime)
    ledger = out / 'aux_ledger.json'
    previous = json.loads(ledger.read_text())['cpu_s'] if ledger.exists() else 0
    atomic(ledger, {'cpu_s': previous + auxiliary})
    if fingerprint_before != code_fingerprint():
        raise RuntimeError('source changed during preflight')
    calibration_status = json.loads((calibration / 'status.json').read_text())
    atomic(out / 'preflight.json', {'status': result['status'], 'code_fingerprint': code_fingerprint(),
                                  'manifest_sha256': hashlib.sha256((out / 'manifest.json').read_bytes()).hexdigest(),
                                  'unix': time.time(), 'platform': platform.platform(),
                                  'logical_cpus': psutil.cpu_count(), 'physical_cpus': psutil.cpu_count(logical=False),
                                  'available_memory_bytes': psutil.virtual_memory().available,
                                  'scheduled_task_count': len(names),
                                  'peak_active_workers': calibration_status['peak_active_workers'],
                                  'peak_worker_rss_kib': max(r['max_rss_kib'] for r in receipts),
                                  'auxiliary_cpu_s': auxiliary,
                                  'calibration_path': str(calibration),
                                  'host_clock_validated': False,
                                  'runtime_prediction': None})
    print((out / 'preflight.json').read_text(), flush=True)


if __name__ == '__main__':
    main()
