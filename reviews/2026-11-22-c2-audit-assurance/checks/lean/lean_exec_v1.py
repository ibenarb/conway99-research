"""WSL wrapper: bound only this process and descendants; no system or security changes."""
from pathlib import Path
import json
import os
import sys

base = Path(__file__).resolve().parent
allowed = sorted(os.sched_getaffinity(0))
os.sched_setaffinity(0,{allowed[0]})
binary = base/'toolchain/lean-4.35.0-rc2-linux/bin'
env = os.environ.copy()
env['PATH'] = str(binary)+os.pathsep+env['PATH']
env['LEAN_NUM_THREADS'] = '1'
env['OMP_NUM_THREADS'] = '1'
env['MATHLIB_CACHE_DIR'] = str(base/'mathlib_cache')
print(json.dumps(dict(own_process_affinity=sorted(os.sched_getaffinity(0)),lean_threads=1,
                      argv=sys.argv[1:])),flush=True)
os.chdir(base/'c3formal')
os.execve(str(binary/'lake'),['lake']+sys.argv[1:],env)
