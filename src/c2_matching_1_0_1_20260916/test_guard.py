"""Regression controls for brief missing telemetry versus genuine guard faults."""
import json
from pathlib import Path
import tempfile
import threading
import time
from unittest.mock import patch
from windows_guard import Guard


def check():
    g = Guard.__new__(Guard)
    g.directory = Path(tempfile.mkdtemp(prefix='guard-regression-'))
    g.read_retries = 0
    g.floor_bytes = 50*1024**3
    path = g.directory/'state.json'
    healthy = {'unix': int(time.time()), 'free_bytes': 100*1024**3, 'stop_reason': None}
    def publish():
        time.sleep(.15)
        tmp = g.directory/'new.tmp'
        tmp.write_text(json.dumps(healthy))
        tmp.replace(path)
    writer = threading.Thread(target=publish)
    writer.start()
    assert g.read()['stop_reason'] is None and g.read_retries > 0
    writer.join()
    for fault in [FileNotFoundError(2, 'gone', str(path)), PermissionError(13, 'busy', str(path)),
                  json.JSONDecodeError('partial', '', 0)]:
        with patch.object(Path, 'read_text', side_effect=[fault, json.dumps(healthy)]):
            assert g.read()['free_bytes'] == healthy['free_bytes']
    path.unlink()
    started = time.monotonic()
    try:
        g.read()
        raise AssertionError('Persistent disappearance was accepted')
    except RuntimeError as exc:
        assert 'WINDOWS_GUARD_READ_FAILED' in str(exc) and str(path) in str(exc)
        assert isinstance(exc.__cause__, FileNotFoundError)
    assert 1.9 <= time.monotonic()-started < 4
    for state in [dict(healthy, unix=int(time.time())-40),
                  dict(healthy, free_bytes=49*1024**3),
                  dict(healthy, stop_reason='WINDOWS_DISK_RESERVE')]:
        path.write_text(json.dumps(state))
        started = time.monotonic()
        try:
            g.read()
            raise AssertionError('Real guard fault was accepted')
        except RuntimeError:
            pass
        assert time.monotonic()-started < .5
    return {'status': 'GUARD_REGRESSION_PASS', 'real_missing_then_publish': True,
            'transient_read_faults': 3, 'permanent_missing_stops_with_path': True,
            'stale_low_disk_and_explicit_fault_stop_immediately': True,
            'target_Windows_writer': 'not executed by this Linux regression test'}


if __name__ == '__main__':
    print(json.dumps(check()))
