"""Install only after real Windows sharing tests; never launches research solvers."""
import datetime
import fcntl
import json
import subprocess
import time
from pathlib import Path
from common import ROOT, VERSION, sha, save, REF_HASH
from windows_guard import Guard, powershell, encoded, ps_quote

HERE = Path(__file__).resolve().parent
LOCK = Path.home() / 'conway99_workspace/c2_matching_v1/campaign.lock'


def sharing_test(guard, name, share, milliseconds, expect_failure=False):
    marker = guard.directory / (name + '.ready')
    target = guard.windows_dir + '\\heartbeat'
    markwin = guard.windows_dir + '\\' + marker.name
    script = "$ErrorActionPreference='Stop'; $f=$null; try { $f=[IO.File]::Open(" + ps_quote(target) + ",[IO.FileMode]::Open,[IO.FileAccess]::Read," + share + "); [IO.File]::WriteAllText(" + ps_quote(markwin) + ",'ready'); Start-Sleep -Milliseconds " + str(milliseconds) + " } finally { if($null -ne $f){$f.Dispose()} }"
    proc = subprocess.Popen([powershell(), '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded(script)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 15
        while not marker.exists():
            if proc.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('Windows lock helper failed: ' + name)
            time.sleep(.01)
        before = guard.write_retries
        old = (guard.directory / 'heartbeat').read_bytes()
        started = time.monotonic()
        failed = False
        try:
            guard.beat()
        except RuntimeError as exc:
            if 'WINDOWS_HEARTBEAT_WRITE_FAILED' not in str(exc):
                raise
            failed = True
        elapsed = time.monotonic() - started
        assert failed == expect_failure, (name, failed)
        if failed:
            assert (guard.directory / 'heartbeat').read_bytes() == old
            assert 4.9 <= elapsed <= 7, elapsed
        retries = guard.write_retries - before
        if share == '[IO.FileShare]::Read':
            assert retries > 0, 'Lock not reproduced; no validation claim'
        else:
            assert retries == 0, 'Delete-sharing did not prevent conflict'
        proc.communicate(timeout=10)
        assert proc.returncode == 0
        guard.beat()
        guard.read()
        return {'test': name, 'write_retries': retries, 'seconds': round(elapsed, 3), 'expected_failure': failed}
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.communicate(timeout=10)


def main():
    with LOCK.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config_bytes = (ROOT / 'setup.json').read_bytes()
        config = json.loads(config_bytes)
        assert sha(config['solver']) == config['solver_sha256']
        assert sha(HERE / 'c2_reference.py') == REF_HASH
        manifest = json.loads((ROOT / 'partitions/manifest.json').read_text())
        assert len(manifest['jobs']) == 11 and manifest['cover']['transports_checked'] == 10395
        assert len({j['id'] for j in manifest['jobs']}) == 11
        for job in manifest['jobs']:
            assert job['group'] == 'totalizer' and sha(job['cnf']) == job['cnf_sha256']
        print('WINDOWS_SHARING_SELFTEST_START: about 30-60 seconds; no solvers', flush=True)
        guard = Guard(ROOT / 'guard-sharing-selftest')
        tests = []
        observations = set()
        try:
            tests.append(sharing_test(guard, 'short_lock', '[IO.FileShare]::Read', 700))
            tests.append(sharing_test(guard, 'delete_shared', '([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)', 700))
            tests.append(sharing_test(guard, 'persistent_lock', '[IO.FileShare]::Read', 7000, True))
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                guard.beat()
                observations.add(guard.read()['unix'])
                time.sleep(.1)
            assert len(observations) >= 3, 'Insufficient fresh Windows observations'
            receipt = {'status': 'WINDOWS_SHARING_SELFTEST_PASS', 'version': VERSION, 'tests': tests,
                       'fresh_updates': len(observations), 'write_retries': guard.write_retries,
                       'read_retries': guard.read_retries, 'directory': guard.windows_dir,
                       'production_solver_runs': 0,
                       'scope': 'Real Windows file locks and WSL recovery, persistent failure, live telemetry; no overnight guarantee or Windows emergency-killer test.'}
        finally:
            guard.close()
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
        backup = ROOT / ('setup_before_guard_fix_' + stamp + '.json')
        with backup.open('xb') as stream:
            stream.write(config_bytes)
        config.update(version=VERSION, source=str(HERE), guard_selftest=receipt)
        save(ROOT / ('guard_selftest_' + stamp + '.json'), receipt)
        save(ROOT / 'setup.json', config)
        print(json.dumps(receipt), flush=True)
        print(json.dumps({'status': 'GUARD_FIX_ACTIVATED_NOT_LAUNCHED', 'source': str(HERE),
                          'next_command': 'python3 ' + str(HERE / 'run_matching.py') + ' --seconds 64800',
                          'inputs_changed': False, 'solver_changed': False}), flush=True)


if __name__ == '__main__':
    main()
