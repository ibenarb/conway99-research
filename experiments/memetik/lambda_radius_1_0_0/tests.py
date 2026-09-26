"""Bounded controls for exact coverage, witnesses, transactional resume and accounting."""
import boot
from support import *
from enumeration import expand, merge
from controller import Controller
from worker import controls
from kernel import catalogue, Scorer
import tempfile


class FakeHost:
    def __init__(self):
        self.start = time.monotonic()
        self.last = self.sample()

    def sample(self):
        self.last = {'host_seconds': time.monotonic() - self.start, 'windows_cpu_seconds': 0,
                     'utc': 'TEST_ONLY_NATIVE_CLOCK', 'physical_free_bytes': 100 * GIB}
        return self.last

    def close(self):
        return 0


class Countdown(Guard):
    def __init__(self, count):
        self.left = count

    def check(self):
        self.left -= 1
        if self.left == 0:
            raise Pause('TEST_INTERRUPTION')


def main():
    starts = read(boot.HERE / 'STARTS.json')
    output = {'status': 'TESTS_RUNNING'}
    with tempfile.TemporaryDirectory(prefix='radius-controls-') as temp:
        root = Path(temp)
        proof = controls({}, root, Guard())
        output['controls'] = proof
        print('MATHEMATICAL_CONTROLS_PASS', flush=True)
        # Reuse three steps of the independent positive control as a depth-3 parent.
        start = starts['2079']
        path = [x['move'] for x in proof['positive_depth4_witness']['steps'][:3]]
        rows = core.decode_g6(proof['positive_depth4_witness']['steps'][2]['graph6'])
        srcpath = root / 'positive.sqlite'
        src = connect(srcpath)
        node(src, rows, 3, path)
        src.commit()
        src.close()
        task = {'kind': 'expand', 'arm': 'control', 'depth': 4, 'start': start,
                'input': str(srcpath), 'lo': 1, 'hi': 1}
        d = root / 'positive'
        d.mkdir()
        atomic(d / 'task.json', task)
        result = expand(task, d, Guard())
        assert result['status'] == 'FOUND' and result['witness']['strict_improvement']
        assert len(result['witness']['steps']) == 4
        output['positive_depth4_worker'] = {'status': result['status'], 'scores': result['witness']['scores']}
        # Enumerate one parent by two paths: independent set and resumable SQL worker.
        base = core.decode_g6(starts['2076']['graph6'])
        srcpath = root / 'one.sqlite'
        src = connect(srcpath)
        node(src, base, 2, [])
        src.commit()
        src.close()
        task = {'kind': 'expand', 'arm': '2076', 'depth': 3, 'start': starts['2076'],
                'input': str(srcpath), 'lo': 1, 'hi': 1}
        d = root / 'resume'
        d.mkdir()
        atomic(d / 'task.json', task)
        try:
            expand(task, d, Countdown(100))
            raise AssertionError('Failed to interrupt')
        except Pause:
            pass
        db = connect(d / 'work.sqlite')
        assert db.execute('SELECT count(*) FROM nodes').fetchone()[0] == 0
        assert meta(db, 'progress') is None
        db.close()
        result = expand(task, d, Guard())
        expected = {pack(core.apply_move(base, m)) for _, m in catalogue(base, False, Guard())}
        db = connect(d / 'work.sqlite', True)
        actual = {r[0] for r in db.execute('SELECT rows FROM nodes')}
        db.close()
        assert expected == actual and result['children'] == 99 and result['parents'] == 1
        replay = expand(task, d, Guard())
        assert replay == result
        output['interrupted_resume_exact'] = True
        output['independent_one_parent_children'] = len(actual)
        # The merge must retain shallow depth even if identical rows occur in a later fragment.
        low = root / 'low.sqlite'
        db = connect(low)
        child = unpack(next(iter(expected)))
        node(db, child, 1, [])
        db.commit()
        db.close()
        taskmerge = {'kind': 'merge', 'sources': [(str(low), digest(low)), (str(d / 'work.sqlite'), digest(d / 'work.sqlite'))]}
        merged = root / 'merge'
        merged.mkdir()
        try:
            merge(taskmerge, merged, Countdown(12))
            raise AssertionError('Failed to interrupt merge')
        except Pause:
            pass
        m = merge(taskmerge, merged, Guard())
        assert m['counts'] == {1: 1, 3: 98}
        assert merge(taskmerge, merged, Guard()) == m
        output['merge_dedup_and_resume'] = True
        # Actual processes and wait4, with an explicitly test-only native clock.
        run = root / 'controller'
        run.mkdir()
        c = Controller(run, FakeHost(), test=True)
        jobs = [('spin1', {'kind': 'spin', 'seconds': 0.1}, 'aux'),
                ('spin2', {'kind': 'spin', 'seconds': 0.1}, 'aux')]
        values = c.execute(jobs, 'TEST_WAIT4', allocation=6)
        assert len(values) == 2
        charged = c.state['used']['aux']
        assert charged > 0
        assert c.execute(jobs, 'TEST_RESUME', allocation=6) == values
        assert c.state['used']['aux'] == charged
        # No allocation beyond the category limit; no silent extension on resume.
        c.state['used']['2076'] = 72000
        extra = [('exhausted', {'kind': 'spin', 'seconds': 1}, '2076')]
        assert c.execute(extra, 'TEST_EXHAUSTED', allocation=6) == {}
        assert c.stopping == 'CPU_BUDGET_INCOMPLETE'
        c.close()
        assert not (run / 'session_active.json').exists()
        output['wait4_resume_budget_gate'] = True
        # An unresolved session must not create a new accounting epoch.
        atomic(run / 'session_active.json', {'test': True})
        try:
            Controller(run, FakeHost(), test=True)
            raise AssertionError('Unclean restart allowed')
        except RuntimeError:
            pass
        output['unclean_restart_refused'] = True
        output['status'] = 'CONTROLS_AND_INTEGRATION_PASS'
        output['cpu_seconds'] = own_cpu()
        atomic(Path(sys.argv[1]), output)
        print(json.dumps({k: v for k, v in output.items() if k != 'controls'}, indent=2))


if __name__ == '__main__':
    main()
