"""Synthetic CPU worker: deliberately spend three CPU seconds on shutdown."""
import signal
import sys
import time
from common import *

signalled = False


def stop(*args):
    global signalled
    signalled = True


def burn_until(target):
    value = 1
    while cpu() < target:
        for i in range(5000):
            value = (value * 1664525 + i + 1013904223) & 0xffffffff
    return value


def main():
    directory = Path(sys.argv[1])
    target = float(sys.argv[2])
    extra = float(sys.argv[3])
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGXCPU, stop)
    burn_until(target)
    at_target = cpu()
    burn_until(at_target + extra)
    end_cpu = cpu()
    result = {'status': 'PASS', 'soft_target': target, 'delayed': extra > 0,
              'cpu_at_target': at_target, 'process_cpu_seconds': end_cpu,
              'proc_cpu_seconds': process(os.getpid())['cpu'],
              'python_process_time_seconds': time.process_time(),
              'stop_signal_seen': signalled}
    atomic(directory / 'result.json', result)


if __name__ == '__main__':
    main()
