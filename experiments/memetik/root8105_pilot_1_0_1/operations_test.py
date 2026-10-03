"""Real clean pause/resume and unclosed-ledger rejection."""
import json
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from core import atomic, load_roots

BASE = Path(__file__).resolve().parent


def controls(directory=None):
    out = Path(directory or tempfile.mkdtemp(prefix='root8105_resume_'))
    (out / 'jobs').mkdir(parents=True)
    cfg = json.loads((BASE / 'config.json').read_text())
    cfg.update({'workers': 1, 'job_cpu_s': 4, 'node_cpu_s': 0.2,
                'projection_cap': 256, 'beam_width': 4, 'row_reservoir': 4,
                'proofs_per_job': 0, 'available_memory_reserve_gib': 0.1,
                'emergency_available_gib': 0.01, 'free_disk_reserve_gib': 0.01})
    root = load_roots(BASE / 'roots.tsv')[0]
    atomic(out / 'manifest.json', {'jobs': ['resume'], 'config': cfg})
    atomic(out / 'jobs' / 'resume.json', {'root_id': root['id'], 'row': root['row'],
                                         'arm': 'dynamic', 'seed': 9, 'config': cfg})
    command = [sys.executable, str(BASE / 'campaign.py'), str(out), '--test']
    log = (out / 'pause.log').open('w')
    proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    checkpoint = out / 'work' / 'resume' / 'checkpoint.json'
    end = time.monotonic() + 15
    while not checkpoint.exists() and time.monotonic() < end and proc.poll() is None:
        time.sleep(0.02)
    if not checkpoint.exists():
        proc.terminate()
        proc.wait(timeout=30)
        raise AssertionError('no real checkpoint before pause')
    proc.send_signal(signal.SIGTERM)
    assert proc.wait(timeout=40) == 0
    log.close()
    receipts = json.loads((out / 'receipts.json').read_text())
    assert len(receipts) == 1 and receipts[0]['status'] == 'PAUSED'
    first_cpu = receipts[0]['cpu_s']
    assert 0 < first_cpu < cfg['job_cpu_s']
    serial = json.loads(checkpoint.read_text())['serial']
    resumed = subprocess.run(command, capture_output=True, timeout=60)
    (out / 'resume.log').write_bytes(resumed.stdout + resumed.stderr)
    assert resumed.returncode == 0
    receipts = json.loads((out / 'receipts.json').read_text())
    assert len(receipts) == 2 and receipts[0]['cpu_s'] == first_cpu
    assert abs(sum(r['cpu_s'] for r in receipts) - 4) < 0.5
    assert json.loads(checkpoint.read_text())['serial'] > serial
    assert not (out / 'session_open.json').exists()
    # Fabricated marker only in this isolated test directory; never erase one
    # from a real run. An unaccounted crash must not silently become zero CPU.
    marker = out / 'session_open.json'
    marker.write_text('{"simulated_unclosed_session": true}')
    before = marker.read_bytes()
    refused = subprocess.run(command, capture_output=True, timeout=15)
    assert refused.returncode != 0 and marker.read_bytes() == before
    result = {'status': 'PASS', 'real_pause_resume': True, 'preserved_prior_cpu_s': first_cpu,
              'total_wait4_cpu_s': sum(r['cpu_s'] for r in receipts),
              'unclosed_session_refused_and_preserved': True}
    atomic(out / 'operations_controls.json', result)
    return result


if __name__ == '__main__':
    print(json.dumps(controls()), flush=True)
