"""Targeted regressions: synthetic pressure, real Linux/WSL process signals."""
import copy
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import platform_adapter as p
import runtime as r
import guard

GIB = 1024**3


def sample(sequence, seconds, available=10*GIB):
    return dict(sequence=sequence, ticks=int(seconds*10000000), frequency=10000000,
                available_physical_bytes=available)


class Policy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.folder = self.root / 'session' / 'platform'
        self.folder.mkdir(parents=True)
        self.attempt = self.root / 'attempts' / 'case'
        self.attempt.mkdir(parents=True)
        self.ident = {'pid': 7}
        r.raw_atomic(self.folder/'native.json', dict(identity=self.ident,
                     directory=str(self.attempt), phase='search'))
        self.pause = p.HostMemoryPause(self.root, self.folder, 8*GIB)
        self.signals = []
        self.mock = patch.object(p, 'signal_native', side_effect=lambda ident, sig:
                                 self.signals.append((ident, sig)) or True)
        self.mock.start()

    def tearDown(self):
        self.mock.stop()
        self.tmp.cleanup()

    def test_low_pauses_once_and_records_exact_sample(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        self.pause.tick(sample(0, 0, 7*GIB))
        self.assertEqual([s for _,s in self.signals], [signal.SIGSTOP])
        self.assertEqual(r.read(self.folder/'pause.json')['host']['available_physical_bytes'], 7*GIB)

    def test_ten_host_seconds_then_same_identity_continues(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        self.pause.tick(sample(1, 1))
        self.pause.tick(sample(2, 10.99))
        self.assertEqual(len(self.signals), 1)
        self.pause.tick(sample(3, 11))
        self.assertEqual(self.signals[-1], (self.ident, signal.SIGCONT))
        self.assertFalse(self.pause.low)

    def test_duplicate_heartbeat_never_completes_recovery(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        self.pause.tick(sample(1, 1))
        for _ in range(20):
            self.pause.tick(sample(1, 1))
        self.assertEqual(len(self.signals), 1)

    def test_hysteresis_and_repeated_pressure(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        self.pause.tick(sample(1, 1))
        self.pause.tick(sample(2, 20, 8*GIB))
        self.pause.tick(sample(3, 21))
        self.pause.tick(sample(4, 30))
        self.assertEqual(len(self.signals), 1)
        self.pause.tick(sample(5, 31))
        self.pause.tick(sample(6, 32, 7*GIB))
        self.assertEqual([s for _,s in self.signals], [signal.SIGSTOP, signal.SIGCONT, signal.SIGSTOP])

    def test_stop_wakes_and_does_not_repause(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        r.raw_atomic(self.attempt/'STOP', {})
        self.pause.tick(sample(1, 1, 7*GIB))
        self.pause.tick(sample(2, 2, 7*GIB))
        self.assertEqual(sum(s == signal.SIGSTOP for _,s in self.signals), 1)
        self.assertIsNone(self.pause.paused)

    def test_checker_stop_marker_wakes(self):
        self.pause.tick(sample(0, 0, 7*GIB))
        r.raw_atomic(self.folder/'stop-requested.json', dict(identity=self.ident))
        self.pause.tick(sample(1, 1, 7*GIB))
        self.assertEqual(self.signals[-1][1], signal.SIGCONT)

    def test_no_child_yet_then_registration(self):
        (self.folder/'native.json').unlink()
        self.pause.tick(sample(0, 0, 7*GIB))
        self.assertEqual(self.signals, [])
        r.raw_atomic(self.folder/'native.json', dict(identity=self.ident,
                     directory=str(self.attempt), phase='search'))
        self.pause.tick(sample(1, 1, 7*GIB))
        self.assertEqual(self.signals[-1][1], signal.SIGSTOP)

    def test_foreign_path_rejected(self):
        r.raw_atomic(self.folder/'native.json', dict(identity=self.ident,
                     directory='/unrelated', phase='search'))
        with self.assertRaises(ValueError):
            self.pause.tick(sample(0, 0, 7*GIB))
        self.assertEqual(self.signals, [])

    def test_signal_failure_does_not_claim_paused(self):
        self.mock.stop()
        with patch.object(p, 'signal_native', return_value=False):
            result = self.pause.tick(sample(0, 0, 7*GIB))
        self.assertIsNone(result['identity'])
        self.assertEqual(result['status'], 'HOST_MEMORY_WAIT')
        self.mock.start()


class RealProcess(unittest.TestCase):
    def test_same_process_keeps_in_memory_counter_across_two_pauses(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root/'session'/'platform'
            folder.mkdir(parents=True)
            attempt = root/'attempts'/'case'
            attempt.mkdir(parents=True)
            counter = root/'counter.json'
            script = 'import os,json,time,sys; from pathlib import Path\np=Path(sys.argv[1]); n=0\nwhile True:\n n+=1\n q=p.with_suffix(".tmp"); q.write_text(json.dumps([os.getpid(),n])); q.replace(p); time.sleep(.01)\n'
            proc = subprocess.Popen([sys.executable, '-c', script, str(counter)])
            ident = r.identity(proc.pid)
            try:
                deadline = time.monotonic()+5
                while not counter.exists():
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(.01)
                r.raw_atomic(folder/'native.json', dict(identity=ident,
                             directory=str(attempt), phase='search'))
                pause = p.HostMemoryPause(root, folder, 8*GIB)
                for cycle in range(2):
                    offset = cycle*30
                    pause.tick(sample(cycle*3, offset, 7*GIB))
                    deadline = time.monotonic()+5
                    while Path('/proc/'+str(ident['proc_pid'])+'/stat').read_text().rsplit(')',1)[1].split()[0] != 'T':
                        self.assertLess(time.monotonic(), deadline)
                        time.sleep(.01)
                    saved = json.loads(counter.read_text())
                    cpu = guard.stat(ident)['self_cpu_s']
                    time.sleep(.15)
                    self.assertEqual(json.loads(counter.read_text()), saved)
                    self.assertEqual(guard.stat(ident)['self_cpu_s'], cpu)
                    pause.tick(sample(cycle*3+1, offset+1))
                    pause.tick(sample(cycle*3+2, offset+11))
                    deadline = time.monotonic()+5
                    while json.loads(counter.read_text())[1] <= saved[1]:
                        self.assertLess(time.monotonic(), deadline)
                        time.sleep(.01)
                    self.assertEqual(r.identity(proc.pid), ident)
                # Explicit stop while paused must wake the same process.
                pause.tick(sample(7, 70, 7*GIB))
                with patch.dict(os.environ, {p.ENV: str(folder), 'N1_ACCOUNTING_SESSION': 'session'}):
                    p.request_native_stop()
                pause.tick(sample(8, 71, 7*GIB))
                proc.terminate()
                self.assertEqual(proc.wait(timeout=5), -signal.SIGTERM)
            finally:
                p.signal_native(ident, signal.SIGCONT)
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)

    def test_wrong_birth_is_never_signalled(self):
        ident = r.identity(os.getpid())
        ident['birth'] = '0'
        self.assertFalse(p.signal_native(ident, signal.SIGSTOP))


class ObserverIntegration(unittest.TestCase):
    def test_pressure_is_healthy_observation_and_fatal_error_wakes_child(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root/'session'
            directory.mkdir()
            attempt = root/'attempts'/'case'
            attempt.mkdir(parents=True)
            cfg = dict(min_available_bytes=8*GIB, max_rss_bytes=24*GIB, min_free_bytes=100*GIB)
            observer = p.Observer(root, directory, cfg)
            host = dict(sample(0, 1, 7*GIB), schema='N1_WINDOWS_CLOCK_1', session_id='session',
                        pid=17, birth='123', utc_ticks=123, synthetic=False,
                        high_resolution=True, cpu_lower_bound_s=1.0)
            (observer.folder/'heartbeat.json').write_text(json.dumps(host))
            r.raw_atomic(observer.folder/'native.json', dict(identity=r.identity(os.getpid()),
                         directory=str(attempt), phase='search'))
            import preflight
            try:
                with patch.object(observer.cgroup, 'sample', return_value={}), patch.object(preflight, 'cgroup_probe', return_value={}), patch.object(guard, 'sensors', return_value=dict(rss_bytes=1000, available_bytes=40*GIB, free_bytes=500*GIB)), patch.object(p, 'signal_native', return_value=True) as signals:
                    observer.tick()
                    self.assertIsNone(observer.fault)
                    health = r.read(observer.folder/'health.json')
                    self.assertTrue(health['ok'])
                    self.assertEqual(health['pressure']['status'], 'PAUSED_HOST_MEMORY')
                    observer.latch('ValueError: broken clock')
                    self.assertTrue((attempt/'STOP').exists())
                    self.assertEqual(signals.call_args.args[1], signal.SIGCONT)
            finally:
                observer.log.close()


if __name__ == '__main__':
    unittest.main()
