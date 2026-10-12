"""Real solver/checker end-to-end tests on known inconsistent controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from common import read, save, sha


class ControllerTest(unittest.TestCase):
    def test_staged_certification_and_reentry(self):
        with tempfile.TemporaryDirectory(prefix='low_controller_') as temp:
            root = Path(temp)
            for name in ['src', 'legacy']:
                shutil.copytree(ROOT / name, root / name)
            (root / 'bin').symlink_to(ROOT / 'bin', target_is_directory=True)
            (root / 'inputs').mkdir()
            (root / 'work').mkdir()
            config = read(ROOT / 'config.json')
            config.update(min_ram_gib=0, min_disk_gib=0, poll_s=0.05, checkpoint_s=0.05,
                          cake_heap_mb=512, cake_stack_mb=64, status_s=10000)
            save(root / 'config.json', config)
            tasks = []
            for ident, filename in [('negative_full', 'invalid_full.cnf'), ('negative_X', 'invalid_X.cnf')]:
                mode = 'X' if ident.endswith('X') else 'R'
                task = {'id': ident, 'mode': mode, 'root_id': 'negative_fixture', 'stage': 'initial'}
                d = root / 'work/cases' / ident
                d.mkdir(parents=True)
                shutil.copyfile(ROOT / 'work/controls' / filename, d / 'formula.cnf')
                save(d / 'formula.json', {'task': task, 'sha256': sha(d / 'formula.cnf')})
                tasks.append(task)
            save(root / 'inputs/pilot.json', {'tasks': tasks})
            for name in ['prepare', 'validation']:
                save(root / 'work' / (name + '.json'), {'status': 'PASS', 'scope': 'Known UNSAT test fixture only'})
            command = [sys.executable, str(root / 'src/control.py'), 'initial']
            first = subprocess.run(command, capture_output=True, text=True, timeout=60)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(read(root / 'work/status.json')['status'], 'STAGE_COMPLETE')
            for task in tasks:
                self.assertEqual(read(root / 'work/cases' / task['id'] / 'verdict.json')['status'], 'UNSAT_CERTIFIED')
            second = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            # A changed proof must invalidate re-entry rather than reuse verdict.
            proof = root / 'work/jobs/negative_X_solve/proof.lrat'
            with proof.open('ab') as stream:
                stream.write(b'corrupt')
            third = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(third.returncode, 0)
            self.assertIn('ARTIFACT_CHANGED', read(root / 'work/controller_error.json')['error'])


if __name__ == '__main__':
    unittest.main()
