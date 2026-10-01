"""Actual pinned archive recovery, tamper rejection, and real child pause/resume."""
import argparse
import shutil
import subprocess
import tarfile
import tempfile
import threading
import time
import signal
from common import *


def rejection(call):
    try:
        call()
    except (RuntimeError, AssertionError, FileExistsError):
        return
    raise AssertionError('Expected rejection did not occur')


def integration(run):
    import controller
    from controller import Controller
    from tests import FakeHost
    from audit import audit
    from run import verify_run
    c = Controller(run, host=FakeHost(), test=True)
    def pause():
        while c.phase != 'REPAIR' or not c.active:
            time.sleep(0.05)
        time.sleep(0.4)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=pause, daemon=True).start()
    c.execute()
    assert read(run / 'RESULT.json')['reason'] == 'USER_PAUSE'
    audit(run)
    verify_run(run)
    before = dict(read(run / 'ledger.json')['used'])
    controller.PAUSE = False
    c = Controller(run, host=FakeHost(), test=True)
    c.execute()
    final = audit(run)
    assert len(read(run / 'ledger.json')['done']) == 4
    assert all(read(run / 'ledger.json')['used'][k] >= v for k, v in before.items())
    assert read(run / 'status.json')['recovery']['campaign_jobs_complete'] == 340
    assert final['recovery']['exact_combined_cpu_hours'] is None
    assert (run / 'heartbeat.json').exists()
    atomic(run.parent / 'INTEGRATION.json', {'status': 'PASS', 'real_children': True,
        'pause_resume': True, 'heartbeat': True, 'audit': final,
        'scope': 'Shortened four-cell test; FakeHost only. Real WSL preflight runs before production.'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--child', type=Path)
    args = parser.parse_args()
    if args.child:
        integration(args.child)
        return
    from recovery import prepare_recovery, verify_predecessor, verify_link, source_paths
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    workspace = out / 'workspace'
    workspace.mkdir()
    with tarfile.open(args.archive) as archive:
        archive.extractall(workspace, filter='data')
    plan = read(HERE / 'RECOVERY_PLAN.json')
    old = workspace / plan['predecessor_run']
    original = {n: digest(p) for n, p in source_paths(old).items()}
    run = prepare_recovery(workspace, args.archive)
    assert original == {n: digest(p) for n, p in source_paths(old).items()}
    assert len(read(run / 'program/MANIFEST.json')['tasks']) == 184
    assert not (run / 'jobs').exists(), 'No previous hints/results copied into new jobs'
    rejection(lambda: prepare_recovery(workspace, args.archive))
    victim = old / 'ledger.json'
    data = victim.read_bytes()
    victim.write_bytes(data + b' ')
    rejection(lambda: verify_predecessor(old, args.archive))
    victim.write_bytes(data)
    victim = run / 'predecessor' / plan['archive_name']
    with victim.open('r+b') as stream:
        byte = stream.read(1)
        stream.seek(0)
        stream.write(bytes([byte[0] ^ 1]))
    rejection(lambda: verify_link(run))
    with victim.open('r+b') as stream:
        stream.write(byte)
    verify_link(run)
    # Disposable fixture only: one complete paired group, short CPU targets.
    program = run / 'program'
    m = read(program / 'MANIFEST.json')
    m['tasks'] = m['tasks'][:4]
    assert len({(t['source_window'], t['seed']) for t in m['tasks']}) == 1
    for t in m['tasks']:
        t['cpu_limit_seconds'] = 15
    atomic(program / 'MANIFEST.json', m)
    package = read(program / 'PACKAGE.json')
    package['files']['MANIFEST.json'] = digest(program / 'MANIFEST.json')
    atomic(program / 'PACKAGE.json', package)
    fingerprint = read(run / 'FINGERPRINT.json')
    fingerprint['package_sha256'] = digest(program / 'PACKAGE.json')
    fingerprint['manifest_sha256'] = digest(program / 'MANIFEST.json')
    atomic(run / 'FINGERPRINT.json', fingerprint)
    ledger = read(run / 'ledger.json')
    ledger['used'] = {'aux': ledger['used']['aux'], **{t['id']: 0 for t in m['tasks']}}
    atomic(run / 'ledger.json', ledger)
    with (out / 'integration.log').open('w') as log:
        subprocess.run([sys.executable, str(program / 'recovery_tests.py'), '--child', str(run)],
            check=True, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, **THREAD_ENV})
    atomic(out / 'RESULT.json', {'status': 'PASS', 'predecessor_unchanged': True,
        'partition': {'completed': 336, 'rerun': 12, 'unstarted': 172},
        'archive_tamper_rejected': True, 'ledger_tamper_rejected': True,
        'existing_destination_rejected': True, 'no_old_hints': True,
        'integration': read(workspace / 'INTEGRATION.json')})
    print(json.dumps(read(out / 'RESULT.json')))


if __name__ == '__main__':
    main()
