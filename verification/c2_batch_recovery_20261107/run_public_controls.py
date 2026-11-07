"""Standalone Linux regression entry point; use a fresh downloaded directory."""
from pathlib import Path
import subprocess
import sys
P=Path(__file__).resolve().parent
for name in ('batch-engine','batch-verify'):
    subprocess.run(['g++','-O3','-mpopcnt','-std=c++17',str(P/(name+'.cpp')),'-o',str(P/name)],check=True,timeout=60)
for script in ('test_recovery.py','test_hard_kill.py','test_scaling.py','test_unknown_prefix.py','screen_rows.py'):
    subprocess.run([sys.executable,str(P/script)],check=True,timeout=180)
print('PASS: recovery, process-kill, scaling, UNKNOWN prefix and row-screen controls')
