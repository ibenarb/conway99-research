"""Mathematical controls, interrupted replay, accounting, exported package guards."""
import boot
from support import *
from episodes import *
from controls import controls
from campaign import execute_profile, summarize
from controller import Controller
from settings import LIMITS
import tempfile
import copy


class CountGuard:
    def __init__(self, n):
        self.n = n
    def check(self):
        self.n -= 1
        if self.n <= 0:
            raise Pause('INJECTED')


class FakeHost:
    def __init__(self):
        self.begin = time.monotonic()
        self.sample()
    def sample(self, *args, **kwargs):
        self.last = {'host_seconds': time.monotonic() - self.begin, 'windows_cpu_seconds': 0,
                     'utc': 'TEST_ONLY', 'physical_free_bytes': 100 * GIB}
        return self.last
    def close(self):
        self.sample()
        return 0


def run():
    out = {'controls': controls(Guard())}
    starts = read(boot.HERE / 'STARTS.json')
    task = {'kind': 'profile', 'start': starts['2076'], 'arm': '2076', 'k': 2, 'n': 2}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for label in ('reference', 'interrupted'):
            d = root / label
            d.mkdir()
            if label == 'interrupted':
                try:
                    work(task, d, CountGuard(100))
                except Pause:
                    pass
                else:
                    raise AssertionError('Interruption not exercised')
            assert work(task, d, Guard())['status'] == 'DONE'
        arrays = []
        for label in ('reference', 'interrupted'):
            db = connect(root / label / 'work.sqlite', True)
            a = [json.loads(x[0]) for x in db.execute('SELECT value FROM episodes ORDER BY idx')]
            db.close()
            for row in a:
                row.pop('phase_cpu_seconds')
                row.pop('episode_cpu_seconds')
            arrays.append(a)
        assert arrays[0] == arrays[1]
        out['interrupted_catalogue_same_paths_rng_endpoints'] = True
        import episodes
        original = episodes.advance
        def after_move(ep, task, guard):
            result = original(ep, task, guard)
            if ep['path']:
                raise Pause('AFTER_COMMITTED_MOVE')
            return result
        d = root / 'after_move'
        d.mkdir()
        episodes.advance = after_move
        try:
            work(task, d, Guard())
        except Pause:
            pass
        else:
            raise AssertionError('Move interruption missed')
        finally:
            episodes.advance = original
        assert work(task, d, Guard())['status'] == 'DONE'
        db = connect(d / 'work.sqlite', True)
        values = [json.loads(x[0]) for x in db.execute('SELECT value FROM episodes ORDER BY idx')]
        db.close()
        for row in values:
            row.pop('phase_cpu_seconds')
            row.pop('episode_cpu_seconds')
        assert values == arrays[0]
        out['pause_after_move_same_paths_and_indices'] = True
        # Actual worker sessions, receipts and no additional CPU on a completed resume.
        run = root / 'controller'
        run.mkdir()
        c = Controller(run, FakeHost(), test=True)
        runtime_task = dict(task, n=12)
        jobs = [('2076_k02', runtime_task, '2076_k02')]
        try:
            result = execute_profile(c, jobs, 12, 'TEST')
            assert result['2076_k02']['status'] == 'DONE'
            before = dict(c.state['used'])
            assert execute_profile(c, jobs, 12, 'RESUME') == result
            assert c.state['used']['2076_k02'] == before['2076_k02']
            profile = summarize(c, jobs)
            assert profile['2076_k02']['completed'] == 12
            assert len(read(run / 'jobs/2076_k02/receipt.json')['sessions']) == 2
            out['wait4_receipts_and_completed_resume'] = True
            # Task tamper rejected, and checkpoint remains readable without changing its hash.
            p = run / 'jobs/2076_k02/task.json'
            original = p.read_bytes()
            p.write_text('{}')
            try:
                c.done(p.parent)
            except RuntimeError:
                out['task_tamper_rejected'] = True
            else:
                raise AssertionError('Tamper missed')
            p.write_bytes(original)
        finally:
            c.close()
        # Exhausted cell must not prevent another cell from running.
        run2 = root / 'budget'
        run2.mkdir()
        c = Controller(run2, FakeHost(), test=True)
        c.state['used']['2076_k02'] = 3595
        task2 = dict(task, k=1, n=1)
        try:
            r = execute_profile(c, [('2076_k02', task, '2076_k02'), ('2076_k01', task2, '2076_k01')], 1, 'BUDGET')
            assert r['2076_k02']['status'] == 'INCOMPLETE'
            assert r['2076_k01']['status'] == 'DONE'
            assert c.state['used']['2076_k02'] == 3595
            out['cell_budget_isolation'] = True
        finally:
            c.close()
    out['status'] = 'PASS'
    atomic(boot.HERE / 'TEST_RESULTS.json', out)
    print(json.dumps(out))


if __name__ == '__main__':
    run()
