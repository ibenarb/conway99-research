"""Integration tests of the real supervisor with tiny busy-loop children."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from common import alive, proc, read, save
from progress import ProofCounter
from worker import budget_update, reasons


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='c2_runtime_test_')
        self.root = Path(self.temp.name)
        self.job = self.root / 'work/jobs/test'
        self.job.mkdir(parents=True)
        config = read(ROOT / 'config.json')
        config.update(min_ram_gib=0, min_disk_gib=0, poll_s=0.02, checkpoint_s=0.02, status_s=1)
        save(self.root / 'config.json', config)
        self.config = config
        self.process = None

    def tearDown(self):
        if self.process and self.process.poll() is None:
            save(self.job / 'control.json', {'sequence': 999, 'extend_seconds': 0})
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.process and self.process.stdout:
            self.process.stdout.close()
        self.temp.cleanup()

    def launch(self, seconds=0.8, target=0.1):
        script = 'import time; t=time.process_time();\nwhile time.process_time()-t<' + str(seconds) + ': pass\n'
        save(self.job / 'spec.json', {'id': 'test', 'root': str(self.root), 'command': [sys.executable, '-c', script],
             'category': 'solver', 'inputs': [], 'outputs': [], 'target_cpu_s': target})
        self.process = subprocess.Popen([sys.executable, str(ROOT / 'src/worker.py'), str(self.job)],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def until(self, predicate, seconds=10):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            value = read(self.job / 'state.json', {})
            if predicate(value):
                return value
            time.sleep(0.02)
        self.fail('State timeout: ' + str(read(self.job / 'state.json')))

    def test_soft_target_does_not_stop(self):
        self.launch()
        state = self.until(lambda s: s.get('time_extension_request'))
        self.assertTrue(alive(state['child']))
        self.process.wait(timeout=10)
        result = read(self.job / 'result.json')
        self.assertEqual(result['returncode'], 0)
        self.assertIsNone(result['reason'])
        self.assertGreater(result['cpu_seconds'], 0.7)

    def test_extend_and_explicit_zero(self):
        self.launch(seconds=20)
        self.until(lambda s: s.get('time_extension_request'))
        save(self.job / 'control.json', {'sequence': 1, 'extend_seconds': 100})
        state = self.until(lambda s: s.get('control_sequence') == 1)
        self.assertIsNone(state['time_extension_request'])
        save(self.job / 'control.json', {'sequence': 2, 'extend_seconds': 0})
        self.process.wait(timeout=15)
        result = read(self.job / 'result.json')
        self.assertEqual(result['reason'], 'EXPLICIT_STOP')
        self.assertLess(result['returncode'], 0)

    def test_resource_pause_then_resume(self):
        self.config['min_ram_gib'] = 10 ** 9
        save(self.root / 'config.json', self.config)
        self.launch(seconds=0.5, target=100)
        state = self.until(lambda s: s.get('phase') == 'RESOURCE_PAUSED')
        first = state['cpu_s']
        time.sleep(0.15)
        second = read(self.job / 'state.json')['cpu_s']
        self.assertLess(second - first, 0.05)
        self.config['min_ram_gib'] = 0
        save(self.root / 'config.json', self.config)
        self.process.wait(timeout=10)
        self.assertEqual(read(self.job / 'result.json')['returncode'], 0)
        self.assertGreaterEqual(read(self.job / 'result.json')['resource_pause_events'], 1)

    def test_supervisor_failure_preserves_child(self):
        self.launch(seconds=30, target=100)
        state = self.until(lambda s: s.get('child') and s.get('phase') == 'RUNNING')
        self.process.terminate()
        self.process.wait(timeout=5)
        saved = read(self.job / 'state.json')
        self.assertEqual(saved['phase'], 'ERROR_PRESERVED')
        self.assertTrue(alive(saved['child']))
        live = proc(saved['child']['pid'])
        self.assertEqual(live['state'], 'T')
        # Explicit cleanup of the test child only.
        import signal
        os.killpg(live['pid'], signal.SIGKILL)

    def test_binary_counters_chunk_boundaries(self):
        p = self.root / 'proof.lrat'
        p.write_bytes(b'a\x02\x02\x00\x04\x00d\x02\x00a\x04\x00\x02\x00')
        counter = ProofCounter(p, 'lrat')
        while counter.offset < p.stat().st_size:
            value = counter.sample(1)
        self.assertEqual(value['complete_addition_records_in_scanned_prefix'], 2)
        self.assertEqual(value['complete_deletion_records_in_scanned_prefix'], 1)
        self.assertIsNone(value['error'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
