"""One root per process; target checkpoints, cooperative stop, no time caps."""
import ctypes
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback

from runtime import atomic, process_stat

STOP = False


def stop(signum, frame):
    global STOP
    STOP = True


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    ctypes.CDLL(None).prctl(1, signal.SIGTERM)  # Linux: parent death asks cooperative stop.
    spec_path, output = map(Path, sys.argv[1:3])
    spec = json.loads(spec_path.read_text())
    # K6: compare with the controller PID from the spec, not with the PPID seen at startup. If the
    # controller died during interpreter start-up, PDEATHSIG is bound to init and would never fire.
    try:
        parent = process_stat(os.getppid(), proc_pid=spec['controller_proc_pid'],
                              identity=spec['controller_identity'])
        if os.getppid() != spec['controller_pid'] or parent is None or parent['state'] in ('Z', 'X'):
            stop(None, None)
    except (KeyError, ValueError, ProcessLookupError):
        stop(None, None)
    result = {'root': spec['root']['id'], 'attempt': spec['attempt'], 'model': spec['model'],
              'code_hash': spec['code_hash'], 'root_hash': spec['root_hash'],
              'model_hash': spec['model_hash'], 'root_row_hash': spec['root_row_hash'],
              'counts': spec['partial'], 'state': 'RUNNING', 'error': None}
    result['process'] = process_stat(os.getpid())
    result['worker_cpu_s'] = time.process_time()
    atomic(output, result)
    last_save = time.monotonic()
    try:
        if spec.get('test_mode'):
            # Test mode has a distinct run identity and can never produce census results.
            for t in range(1, 84):
                if STOP:
                    break
                if str(t) in result['counts']:
                    continue
                start = time.process_time()
                while time.process_time() - start < spec.get('test_cpu_s', 0.015):
                    sum(i * i for i in range(100))
                if spec.get('fail_root') == spec['root']['id'] and t == 3:
                    raise RuntimeError('deliberate isolated worker failure')
                result['counts'][str(t)] = {'width': t, 'cpu_s': time.process_time() - start}
                result['worker_cpu_s'] = time.process_time()
                atomic(output, result)
                if STOP:
                    break
        else:
            from kernel import Geo, width
            g, row = Geo(), int(spec['root']['row'], 16)
            for t in range(1, 84):
                if STOP:
                    break
                if str(t) in result['counts']:
                    continue
                start = time.process_time()
                value = width(g, row, t)
                result['counts'][str(t)] = {'width': value, 'cpu_s': time.process_time() - start}
                result['worker_cpu_s'] = time.process_time()
                if STOP or time.monotonic() - last_save >= 5:
                    atomic(output, result)
                    last_save = time.monotonic()
                if STOP:
                    break
        result['state'] = 'COMPLETE' if len(result['counts']) == 83 else 'STOPPED_PARTIAL'
    except Exception:
        result['state'], result['error'] = 'ERROR', traceback.format_exc()
    result['worker_cpu_s'] = time.process_time()
    atomic(output, result)
    return 1 if result['state'] == 'ERROR' else 0


if __name__ == '__main__':
    sys.exit(main())
