"""Ensure the isolated audit interpreter, then optionally run Python arguments."""
from pathlib import Path
import argparse
import fcntl
import json
import os
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[2]
PROBE = '''import importlib.metadata, json, pynauty, sys
assert importlib.metadata.version("pynauty") == "2.8.8.1"
adj = {i: [(i-1)%5, (i+1)%5] for i in range(5)}
p = [2, 4, 1, 0, 3]
a = pynauty.Graph(5, adjacency_dict=adj)
b = pynauty.Graph(5, adjacency_dict={p[i]: [p[j] for j in adj[i]] for i in adj})
c = pynauty.Graph(5, adjacency_dict={i: [j for j in (i-1,i+1) if 0 <= j < 5] for i in range(5)})
assert pynauty.certificate(a) == pynauty.certificate(b)
assert pynauty.certificate(a) != pynauty.certificate(c)
g = pynauty.autgrp(a)
assert g[1] * 10**g[2] == 10
print(json.dumps({"status": "AUDIT_ENV_READY", "python": sys.executable,
                  "pynauty": "2.8.8.1", "canonical_and_automorphism_checks": "PASS"}))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv', type=Path, default=ROOT.parent / 'venvs/memetik-audit')
    parser.add_argument('python_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    target = args.venv.expanduser().absolute()
    target.parent.mkdir(parents=True, exist_ok=True)
    child_env = {**os.environ, 'PYTHONNOUSERSITE': '1'}
    child_env.pop('PYTHONPATH', None)
    child_env.pop('PYTHONHOME', None)
    with (target.parent / (target.name + '.setup.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not target.exists():
            venv.EnvBuilder(with_pip=True).create(target)
        python = target / 'bin/python'
        if not (target / 'pyvenv.cfg').is_file() or not python.exists():
            raise SystemExit('Existing environment is incomplete; choose a fresh --venv path. No files deleted.')
        result = subprocess.run([str(python), '-c', PROBE], env=child_env, capture_output=True, text=True)
        if result.returncode:
            print('Preparing pinned audit dependency in ' + str(target), file=sys.stderr, flush=True)
            if result.stderr:
                print(result.stderr.strip(), file=sys.stderr)
            subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                            '-r', str(Path(__file__).with_name('requirements-audit.txt'))],
                           env=child_env, check=True, stdout=sys.stderr)
            result = subprocess.run([str(python), '-c', PROBE], env=child_env, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError('Audit environment failed self-test: ' + result.stderr)
        print(result.stdout.strip(), file=sys.stderr if args.python_args else sys.stdout, flush=True)
    rest = args.python_args
    if rest[:1] == ['--']:
        rest = rest[1:]
    if rest:
        raise SystemExit(subprocess.run([str(python), *rest], env=child_env).returncode)


if __name__ == '__main__':
    main()
