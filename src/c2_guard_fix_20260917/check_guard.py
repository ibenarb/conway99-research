"""Fault injection: bounded write recovery, stale/disk checks, controller cleanup."""
import errno
import json
from pathlib import Path
import tempfile
import time
from unittest.mock import patch
import windows_guard as wg


def run():
    checks = []
    with tempfile.TemporaryDirectory() as td:
        g = wg.Guard.__new__(wg.Guard)
        g.directory = Path(td)
        g.write_retries = g.read_retries = 0
        g.floor_bytes = 50 * 1024**3
        heartbeat = g.directory / 'heartbeat'
        heartbeat.write_text('100')
        original_replace = Path.replace
        calls = [0]

        def transient(path, target):
            calls[0] += 1
            if calls[0] <= 4:
                assert heartbeat.read_text() == '100'
                raise PermissionError(errno.EACCES, 'injected sharing violation')
            return original_replace(path, target)

        with patch.object(Path, 'replace', transient):
            g.beat()
        assert g.write_retries == 4 and int(heartbeat.read_text()) > 100
        checks.append('transient_replace_recovers_preserving_old_heartbeat')
        original_write = Path.write_text
        calls[0] = 0

        def transient_write(path, *args, **kwargs):
            calls[0] += 1
            if calls[0] <= 3:
                raise PermissionError(errno.EACCES, 'injected temp lock')
            return original_write(path, *args, **kwargs)

        with patch.object(Path, 'write_text', transient_write):
            g.beat()
        assert g.write_retries == 7
        checks.append('transient_temp_write_recovers')
        previous = heartbeat.read_bytes()
        clock = [0.0]
        with patch.object(Path, 'replace', side_effect=PermissionError(13, 'persistent')), patch.object(wg.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(wg.time, 'sleep', side_effect=lambda n: clock.__setitem__(0, clock[0] + n)):
            try:
                g.beat()
                raise AssertionError('persistent error swallowed')
            except RuntimeError as exc:
                assert 'WINDOWS_HEARTBEAT_WRITE_FAILED' in str(exc)
        assert 5 <= clock[0] <= 5.1 and heartbeat.read_bytes() == previous
        checks.append('persistent_permission_fails_bounded_old_heartbeat_retained')
        for code in (errno.ENOSPC, errno.EIO, errno.ENOENT):
            before = g.write_retries
            with patch.object(Path, 'replace', side_effect=OSError(code, 'injected')):
                try:
                    g.beat()
                    raise AssertionError('fatal error swallowed')
                except OSError as exc:
                    assert exc.errno == code
            assert before == g.write_retries
            checks.append('fatal_errno_' + str(code) + '_not_retried')
        for state, expected in [
            ({'unix': time.time()-100, 'free_bytes': 100*1024**3}, 'stale'),
            ({'unix': time.time(), 'free_bytes': 1}, 'WINDOWS_DISK_RESERVE'),
            ({'stop_reason': 'CONTROLLER_HEARTBEAT_STALE'}, 'CONTROLLER_HEARTBEAT_STALE'),
        ]:
            (g.directory / 'state.json').write_text(json.dumps(state))
            try:
                g.read()
                raise AssertionError('safety error swallowed')
            except RuntimeError as exc:
                assert expected in str(exc)
            checks.append('reject_' + expected)
    return {'status': 'GUARD_FAULT_CONTROLS_PASS', 'checks': checks,
            'scope': 'Linux fault injection; Windows sharing tested separately on target.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
