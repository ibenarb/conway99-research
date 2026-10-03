"""Install into a new dedicated venv and compile the vendored proof checker."""
import subprocess
import sys
import venv
from pathlib import Path

BASE = Path(__file__).resolve().parent
if sys.version_info < (3, 10):
    raise SystemExit('Python >=3.10 required')
if sys.platform != 'linux':
    raise SystemExit('Run inside Linux/WSL, not Windows Python')
target = BASE / '.venv'
if not target.exists():
    venv.EnvBuilder(with_pip=True).create(target)
python = target / 'bin' / 'python'
subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(BASE / 'requirements.txt')], check=True)
(BASE / 'bin').mkdir(exist_ok=True)
subprocess.run(['cc', '-O2', '-o', str(BASE / 'bin' / 'drat-trim'), str(BASE / 'vendor' / 'drat-trim.c')], check=True)
print('SETUP_COMPLETE: ' + str(python))
