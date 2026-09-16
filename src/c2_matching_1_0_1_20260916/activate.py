"""Validate existing inputs, exercise the real Windows observer, activate fresh source."""
import datetime
import fcntl
import json
from pathlib import Path
import time
from common import ROOT, VERSION, REF_HASH, CNF_HASH, MAP_HASH, sha, save
from windows_guard import Guard

HERE = Path(__file__).resolve().parent


def main():
    with (ROOT/'campaign.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raw = (ROOT/'setup.json').read_bytes()
        config = json.loads(raw)
        assert sha(HERE/'c2_reference.py') == REF_HASH, 'Reference source identity'
        assert config['baseline_sha256'] == CNF_HASH and config['mapping_sha256'] == MAP_HASH
        assert sha(config['solver']) == config['solver_sha256'], 'Solver changed'
        manifest = json.loads((ROOT/'partitions/manifest.json').read_text())
        assert len(manifest['jobs']) == 11
        for job in manifest['jobs']:
            assert sha(job['cnf']) == job['cnf_sha256'], 'Case CNF changed: '+job['id']
        print('GUARD_SELFTEST_START: about 15 seconds, no solver processes', flush=True)
        guard = Guard(ROOT/'observer-selftest')
        observations = set()
        try:
            deadline = time.monotonic()+15
            while time.monotonic() < deadline:
                guard.beat()
                state = guard.read()
                observations.add(state['unix'])
                time.sleep(.1)
            if len(observations) < 3:
                raise RuntimeError('Windows observer did not publish enough fresh updates')
            receipt = {'status': 'WINDOWS_GUARD_SELFTEST_PASS', 'version': VERSION,
                       'fresh_updates': len(observations), 'read_retries': guard.read_retries,
                       'directory': guard.windows_dir, 'last_observation': state,
                       'scope': 'Actual WSL/Windows telemetry updates; not an overnight guarantee or emergency-kill test.'}
        finally:
            guard.close()
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
        with (ROOT/('setup_before_guard_fix_'+stamp+'.json')).open('xb') as stream:
            stream.write(raw)
        config.update(version=VERSION, source=str(HERE), guard_selftest=receipt)
        save(ROOT/('guard_selftest_'+stamp+'.json'), receipt)
        save(ROOT/'setup.json', config)
        print(json.dumps(receipt), flush=True)
        print(json.dumps({'status': 'C2_MATCHING_1_0_1_ACTIVATED', 'source': str(HERE),
                          'inputs_changed': False, 'solver_changed': False, 'production_solver_runs': 0}), flush=True)


if __name__ == '__main__':
    main()
