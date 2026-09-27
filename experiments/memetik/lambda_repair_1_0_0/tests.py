"""Isolated package/runtime tests. Never run the production Ryzen campaign."""
import argparse
import datetime
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from common import *


class FakeHost:
    """Cloud-only test clock; production CLI cannot select this class."""
    def __init__(self):
        self.begin = time.monotonic()
        self.last = self.sample()

    def sample(self, *args, **kwargs):
        self.last = {'host_seconds': time.monotonic() - self.begin, 'windows_cpu_seconds': 0,
                     'physical_free_bytes': 100 * GIB, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        return self.last

    def close(self):
        return 0


def integration(run):
    import controller
    from controller import Controller
    from run import prepare, verify_run
    from audit import audit
    prepare(run)
    state = read(run / 'ledger.json')
    state['calibrated'] = True
    state['peak_worker_rss'] = 256 * 1024 ** 2
    atomic(run / 'ledger.json', state)
    c = Controller(run, host=FakeHost(), test=True)

    def pause_when_searching():
        while c.phase != 'REPAIR' or not c.active:
            time.sleep(0.05)
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    thread = threading.Thread(target=pause_when_searching, daemon=True)
    thread.start()
    c.execute()
    first = read(run / 'RESULT.json')
    assert first['reason'] == 'USER_PAUSE', first
    assert not read(run / 'ledger.json')['active']
    old_usage = dict(first['cpu_seconds'])
    old_best = {p.parent.name: read(p)['scores'] for p in (run / 'jobs').glob('*/best.json')}
    audit(run)
    # Clean resume uses the same frozen program, ledger, founders and windows.
    verify_run(run)
    controller.PAUSE = False
    c = Controller(run, host=FakeHost(), test=True)
    c.execute()
    final = read(run / 'RESULT.json')
    assert final['status'] == 'COMPLETED_BUDGETED_PILOT', final
    assert all(final['cpu_seconds'][k] >= v for k, v in old_usage.items())
    from verify import key
    assert all(key(read(run / 'jobs' / name / 'best.json')['scores']) <= key(scores) for name, scores in old_best.items())
    result = audit(run)
    assert read(run / 'status.json')['eta_seconds'] is None
    assert read(run / 'status.json')['charged_cpu_seconds'] == read(run / 'ledger.json')['used']
    # Damaged frozen source must not pass a resume audit.
    victim = run / 'program' / 'README.md'
    original = victim.read_bytes()
    victim.write_bytes(original + b'\ncorrupt\n')
    try:
        try:
            audit(run)
            raise RuntimeError('Corruption accepted')
        except AssertionError:
            pass
    finally:
        victim.write_bytes(original)
    # Unresolved reservations must not be interpreted as unused CPU.
    state = read(run / 'ledger.json')
    state['active']['unresolved'] = {'allocation': 1}
    atomic(run / 'ledger.json', state)
    try:
        try:
            verify_run(run)
            raise AssertionError('Unresolved reservation accepted')
        except RuntimeError:
            pass
    finally:
        state['active'].clear()
        atomic(run / 'ledger.json', state)
    atomic(run / 'TEST_INTEGRATION.json', {'status': 'PASS', 'pause_resume': True, 'wait4_audit': result,
                                          'source_corruption_rejected': True, 'unresolved_cpu_rejected': True,
                                          'clock': 'FakeHost; not a Windows validation'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--child', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.child:
        integration(args.child)
        return
    target = args.out.resolve()
    target.mkdir(parents=True, exist_ok=False)
    program = target / 'fixture'
    shutil.copytree(HERE, program, ignore=shutil.ignore_patterns('__pycache__'))
    manifest = read(program / 'MANIFEST.json')
    manifest['tasks'] = [next(t for t in manifest['tasks'] if t['size'] == size) for size in (24, 40, 60)]
    for task in manifest['tasks']:
        task['cpu_limit_seconds'] = 20
    atomic(program / 'MANIFEST.json', manifest)
    package = read(program / 'PACKAGE.json')
    package['files']['MANIFEST.json'] = digest(program / 'MANIFEST.json')
    atomic(program / 'PACKAGE.json', package)
    with (target / 'integration.log').open('w') as log:
        subprocess.run([sys.executable, str(program / 'tests.py'), '--child', str(target / 'run')],
                       stdout=log, stderr=subprocess.STDOUT, check=True, env={**os.environ, **THREAD_ENV})
    result = read(target / 'run/TEST_INTEGRATION.json')
    atomic(target / 'RESULT.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
