import bootstrap
"""Install in a NEW package-specific environment; never touch an existing research venv."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import venv

base = Path(__file__).resolve().parent
if sys.version_info < (3, 10):
    raise SystemExit('Python >=3.10 required')
manifest_path = base / 'SHA256.json'
if manifest_path.exists():
    for name, expected in json.loads(manifest_path.read_text()).items():
        if hashlib.sha256((base / name).read_bytes()).hexdigest() != expected:
            raise SystemExit('Package checksum mismatch: ' + name)
target = base / '.venv'
if target.exists():
    raise SystemExit('Environment already exists. Reuse it; no automatic overwrite.')
venv.EnvBuilder(with_pip=True).create(target)
python = target / 'bin/python'
subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(base / 'requirements.txt')], check=True)
subprocess.run([str(python), '-c', 'import numpy,pynauty,pysat; print("DEPENDENCIES_READY")'], check=True)
print('SETUP_COMPLETE ' + str(python))
