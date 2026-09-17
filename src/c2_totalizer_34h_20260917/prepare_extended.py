"""Reuse the passed Windows guard test; change only source selection and budget."""
import datetime
import fcntl
import json
from pathlib import Path
from common import ROOT, VERSION, sha, save

HERE = Path(__file__).resolve().parent
LOCK = Path.home() / 'conway99_workspace/c2_matching_v1/campaign.lock'


def main():
    with LOCK.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raw = (ROOT / 'setup.json').read_bytes()
        config = json.loads(raw)
        receipt = config.get('guard_selftest', {})
        assert receipt.get('status') == 'WINDOWS_SHARING_SELFTEST_PASS', 'Run guard activation first'
        expected = (HERE / 'expected_guard.txt').read_text().strip()
        assert sha(HERE / 'windows_guard.py') == expected
        assert sha(Path(config['source']) / 'windows_guard.py') == expected, 'Tested guard source differs'
        assert sha(config['solver']) == config['solver_sha256']
        manifest = json.loads((ROOT / 'partitions/manifest.json').read_text())
        assert len(manifest['jobs']) == 11 and manifest['cover']['transports_checked'] == 10395
        assert len({j['id'] for j in manifest['jobs']}) == 11
        for job in manifest['jobs']:
            assert job['group'] == 'totalizer' and sha(job['cnf']) == job['cnf_sha256']
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
        with (ROOT / ('setup_before_34h_' + stamp + '.json')).open('xb') as stream:
            stream.write(raw)
        config.update(version=VERSION, source=str(HERE))
        save(ROOT / 'setup.json', config)
        print(json.dumps({'status': 'TOTALIZER_34H_PREPARED', 'version': VERSION,
                          'seconds_per_case': 122400, 'workers': 11,
                          'guard_selftest_reused': True, 'source': str(HERE),
                          'inputs_changed': False, 'solver_changed': False}), flush=True)


if __name__ == '__main__':
    main()
