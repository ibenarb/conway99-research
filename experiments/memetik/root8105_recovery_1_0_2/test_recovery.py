"""Operational regressions using the unchanged real search/proof programs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

from disk_monitor import DiskMonitor

HERE = Path(__file__).resolve().parent


def disk_controls(directory):
    directory.mkdir()
    for i in range(40):
        child = directory / str(i)
        child.mkdir()
        for j in range(50):
            (child / str(j)).write_bytes(b'x' * 10)
    monitor = DiskMonitor(directory, max_entries=17, slice_s=1, interval_s=0)
    calls = 0
    while monitor.scans == 0:
        before = monitor.entries
        monitor.step()
        assert monitor.entries - before <= 17
        calls += 1
    assert monitor.high_water == 20000 and calls > 100
    (directory / 'new').write_bytes(b'y' * 400)
    while monitor.scans < 2:
        monitor.step()
    assert monitor.high_water == 20400
    missing = DiskMonitor(directory / 'missing')
    missing.step()
    assert missing.scans == 1
    with patch('disk_monitor.os.scandir', side_effect=PermissionError('deliberate')):
        try:
            DiskMonitor(directory).step()
            raise AssertionError('permission error suppressed')
        except PermissionError:
            pass
    return {'bounded_entry_slices': True, 'entries': 2040, 'calls': calls,
            'growth_detected': True, 'missing_tolerated_permission_denied_propagated': True}


def run_tests(package, directory):
    package = package.resolve()
    directory.mkdir(parents=True)
    sys.path.insert(0, str(package))
    import core
    import operations_test
    import depth_controls
    import recovery_campaign
    import selftest
    fake = directory / 'source'
    fake.mkdir()
    for path in package.iterdir():
        if path.name not in ('campaign.py', 'bin', '__pycache__', '.venv'):
            (fake / path.name).symlink_to(path)
    wrapper = ('import sys\nfrom pathlib import Path\n'
               f'sys.path.insert(0, {str(HERE)!r})\n'
               'import recovery_campaign as c\n'
               f'c.BASE=Path({str(fake)!r})\n'
               'c.run(sys.argv[1], allow_test=True)\n')
    (fake / 'campaign.py').write_text(wrapper)
    (fake / 'bin').mkdir()
    subprocess.run(['cc', '-O2', '-o', str(fake / 'bin' / 'drat-trim'),
                    str(package / 'vendor' / 'drat-trim.c')], check=True, capture_output=True)
    operations_test.BASE = fake
    depth_controls.BASE = fake
    selftest.BASE = fake
    result = {'status': 'PASS', 'scope': 'Cloud operational regressions; synthetic filesystem and real native workers',
              'disk': disk_controls(directory / 'disk'),
              'pause_resume': operations_test.controls(directory / 'pause'),
              'depth': depth_controls.run_tests(directory / 'depth'),
              'mathematics_and_proof': selftest.run_tests(directory / 'math', operational=False)}
    # Use a real previously generated UNSAT projection; completed searches must
    # be skipped and only their proof scheduled on restart.
    proof_run = directory / 'proof_resume'
    (proof_run / 'work' / 'done').mkdir(parents=True)
    cfg = json.loads((package / 'config.json').read_text())
    cfg.update({'workers': 1, 'available_memory_reserve_gib': 0.1,
                'emergency_available_gib': 0.01, 'free_disk_reserve_gib': 0.01})
    artifact = directory / 'math' / 'trivial_proof'
    core.atomic(proof_run / 'manifest.json', {'jobs': ['done'], 'config': cfg})
    prior = [{'job': 'done', 'kind': 'search', 'cpu_s': 3600, 'terminal': True,
              'status': 'CPU_LIMIT_UNKNOWN'}]
    core.atomic(proof_run / 'receipts.json', prior)
    core.atomic(proof_run / 'aux_ledger.json', {'cpu_s': 500})
    core.atomic(proof_run / 'work' / 'done' / 'checkpoint.json', {'proof_candidates': [str(artifact)]})
    done = subprocess.run([sys.executable, str(fake / 'campaign.py'), str(proof_run)],
                          capture_output=True, timeout=45)
    (directory / 'proof_resume.log').write_bytes(done.stdout + done.stderr)
    assert done.returncode == 0, done.stderr.decode()
    receipts = json.loads((proof_run / 'receipts.json').read_text())
    assert receipts[:1] == prior and len(receipts) == 2 and receipts[-1]['kind'] == 'proof'
    assert json.loads((artifact / 'certificate.json').read_text())['certified']
    assert json.loads((proof_run / 'aux_ledger.json').read_text())['cpu_s'] > 500
    result['real_proof_only_resume_preserves_old_receipt_and_cpu'] = True
    # Completed proof is not rerun.
    done = subprocess.run([sys.executable, str(fake / 'campaign.py'), str(proof_run)],
                          capture_output=True, timeout=15)
    assert done.returncode == 0 and len(json.loads((proof_run / 'receipts.json').read_text())) == 2
    result['completed_proof_not_repeated'] = True
    core.atomic(directory / 'VALIDATION.json', result)
    return result


if __name__ == '__main__':
    print(json.dumps(run_tests(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
