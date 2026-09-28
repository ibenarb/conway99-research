"""Small CPU work unit; parent compares it with Windows Stopwatch and wait4."""
import sys
from common import *

begin = cpu()
value = 0
while cpu() - begin < 2:
    for i in range(1000):
        value = (value * 33 + i) & 0xffffffff
atomic(Path(sys.argv[1]) / 'result.json', {'status': 'PASS', 'cpu_seconds': cpu(), 'checksum': value})
