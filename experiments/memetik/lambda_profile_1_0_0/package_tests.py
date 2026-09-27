"""Validate extracted release prepare, no overwrite, fingerprint, Windows-only launch."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
archive = ROOT / 'releases/memetik/lambda_profile_1_0_0.zip'
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        z.extractall(base)
    cli = base / 'lambda_profile_1_0_0/experiments/memetik/lambda_profile_1_0_0/run.py'
    run = base / 'run'
    env = {k: v for k, v in os.environ.items() if k != 'WSL_DISTRO_NAME'}
    def call(action):
        return subprocess.run([sys.executable, str(cli), action, str(run)], capture_output=True, text=True, env=env)
    r = call('prepare')
    assert r.returncode == 0, r.stderr
    assert call('prepare').returncode != 0
    r = call('launch')
    assert r.returncode != 0 and 'requires Windows host clock' in r.stderr
    frozen = run / 'program/experiments/memetik/lambda_profile_1_0_0/episodes.py'
    frozen.write_text(frozen.read_text() + '\n# tampered\n')
    r = call('launch')
    assert r.returncode != 0 and 'SOURCE_HASH_MISMATCH' in r.stderr
    ledger = json.loads((run / 'ledger.json').read_text())
    assert sum(ledger['used'].values()) == 10 and not ledger['active']
out = {'status': 'PASS', 'standalone_prepare': True, 'no_overwrite': True,
       'no_linux_clock_fallback': True, 'frozen_tamper_rejected': True}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out))
