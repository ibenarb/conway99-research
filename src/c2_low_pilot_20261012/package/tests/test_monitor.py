"""Fast wall-clock monitoring tests, with real detached processes and journals."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from common import alive, proc, read, save
from monitor import emit, finite_eta, render, snapshot


class MonitorTests(unittest.TestCase):
    def test_eta_has_scope_and_no_solver_extrapolation(self):
        self.assertEqual(finite_eta(10, 30, 20)['seconds'], 40)
        self.assertIsNone(finite_eta(0, 30, 20)['seconds'])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'work').mkdir()
            s = snapshot(root, time.time())
            self.assertIsNone(s['eta']['seconds'])
            text = render({'event':'HEARTBEAT','time':time.time(),'snapshot':s,'next_heartbeat_unix':time.time()+900})
            self.assertIn('ETA unbekannt', text)
            self.assertIn('keine Abschluss-ETA', text)
            self.assertIn('swap_used_gib', text)

    def test_concurrent_event_records_are_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            script = 'from monitor import emit; import sys; [emit(sys.argv[1], "TEST", n=i) for i in range(20)]'
            env = {**os.environ, 'PYTHONPATH': str(ROOT/'src')}
            children = [subprocess.Popen([sys.executable,'-c',script,temp],env=env) for _ in range(3)]
            for p in children:
                self.assertEqual(p.wait(timeout=10), 0)
            rows = [json.loads(x) for x in (Path(temp)/'events.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),60)

    def test_heartbeats_without_results_and_detached_view(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); work = root/'work'; work.mkdir()
            shutil.copytree(ROOT/'src',root/'src')
            save(root/'config.json', {'heartbeat_s':.15,'observer_poll_s':.02})
            # Test process stands in for an idle controller; it must survive closing the view.
            controller = subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
            save(work/'controller_launch.json',{'process':proc(controller.pid),'started_unix':time.time()})
            observer = subprocess.Popen([sys.executable,str(root/'src/monitor.py'),str(root),str(time.time())],start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            viewer = None
            try:
                deadline=time.monotonic()+10
                while time.monotonic()<deadline:
                    if (work/'events.jsonl').exists() and (work/'events.jsonl').read_text().count('"event": "HEARTBEAT"')>=3:
                        break
                    time.sleep(.05)
                rows=[json.loads(x) for x in (work/'events.jsonl').read_text().splitlines()]
                beats=[x for x in rows if x['event']=='HEARTBEAT']
                self.assertGreaterEqual(len(beats),3)
                self.assertTrue(all(x['snapshot']['since_last_result_s'] is None for x in beats))
                env={**os.environ,'PYTHONPATH':str(root/'src')}
                viewer=subprocess.Popen([sys.executable,'-u','-c','from pathlib import Path; from monitor import watch; import sys; watch(Path(sys.argv[1]))',str(root)],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                time.sleep(.2); viewer.send_signal(signal.SIGINT); output=viewer.communicate(timeout=5)[0].decode()
                self.assertIn('bleiben unberührt',output)
                self.assertIsNone(observer.poll()); self.assertIsNone(controller.poll())
                controller.terminate(); controller.wait(timeout=5)
                observer.wait(timeout=10)
                self.assertEqual(observer.returncode,0,observer.stdout.read().decode())
                self.assertIn('MONITOR_COMPLETE',(work/'events.jsonl').read_text())
            finally:
                for p in [viewer,observer,controller]:
                    if p and p.poll() is None:
                        p.kill();p.wait(timeout=5)
                    if p and p.stdout:p.stdout.close()


if __name__=='__main__': unittest.main(verbosity=2)
