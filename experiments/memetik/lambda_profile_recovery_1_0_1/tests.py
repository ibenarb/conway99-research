"""Race regression, input immutability, receipt-preserving real worker resume."""
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(source / 'program/experiments/memetik/lambda_profile_1_0_0'))
import boot
from tests import FakeHost
from support import read, digest
from campaign import snapshot, execute_profile
from controller_fixed import Controller, directory_bytes
import start


class Vanished:
    def stat(self):
        raise FileNotFoundError('simulated journal deletion')


class Present:
    def __init__(self):
        self.calls = 0

    def stat(self):
        self.calls += 1
        assert self.calls == 1
        return type('S', (), {'st_mode': 0o100644, 'st_size': 17})()


class Root:
    def __init__(self, paths):
        self.paths = paths

    def rglob(self, pattern):
        return iter(self.paths)


class Denied:
    def stat(self):
        raise PermissionError('must propagate')


assert directory_bytes(Root([Vanished(), Present()])) == 17
try:
    directory_bytes(Root([Denied()]))
    raise AssertionError('PermissionError hidden')
except PermissionError:
    pass
with tempfile.TemporaryDirectory() as temp:
    dest = Path(temp) / 'recovered'
    start.prepare(source, dest)
    initial = read(dest / 'ledger.json')
    try:
        start.prepare(source, dest)
        raise AssertionError('overwrite allowed')
    except FileExistsError:
        pass
    controller = Controller(dest, FakeHost(), test=True)
    try:
        name = '2076_k12'
        directory = dest / 'jobs' / name
        task = read(directory / 'task.json')
        before = snapshot(controller, name, task)
        import sqlite3
        db = sqlite3.connect(directory / 'work.sqlite')
        oldrows = db.execute('SELECT idx,value FROM episodes ORDER BY idx').fetchall()
        db.close()
        assert before['episode'] is not None
        result = execute_profile(controller, [(name, task, name)], before['next'] + 1, 'RECOVERY_TEST')
        after = snapshot(controller, name, task)
        assert after['next'] > before['next']
        db = sqlite3.connect(directory / 'work.sqlite')
        newrows = db.execute('SELECT idx,value FROM episodes ORDER BY idx').fetchall()
        db.close()
        assert newrows[:len(oldrows)] == oldrows
        first = json.loads(newrows[len(oldrows)][1])
        assert first['path'][:len(before['episode']['path'])] == before['episode']['path']
        assert controller.state['used'][name] > initial['used'][name]
        for category in initial['used']:
            if category not in (name, 'aux'):
                assert controller.state['used'][category] == initial['used'][category]
    finally:
        controller.close()
    assert not read(dest / 'ledger.json')['active']
    assert not (dest / 'session_active.json').exists()
    start.verify_files(source, read(HERE / 'INPUTS.json'))
import campaign_fixed
with tempfile.TemporaryDirectory() as temp:
    dest = Path(temp)
    campaign_fixed.N = 1
    campaign_fixed.LENGTHS = (2,)
    campaign_fixed.campaign(dest, FakeHost(), test=True)
    result = read(dest / 'RESULT.json')
    assert result['status'] == 'COMPLETE'
    assert (dest / 'jobs/recovery_clock_probe/receipt.json').exists()
    assert len(result['cells']) == 2
print(json.dumps({'status': 'PASS', 'journal_race': True, 'permission_errors_propagate': True,
    'original_unchanged': True, 'overwrite_rejected': True, 'real_checkpoint_resume': True,
    'old_episodes_byte_identical': True, 'partial_path_preserved': True,
    'prior_cpu_charges_retained': True, 'remaining_cell_limits_unchanged': True}))
