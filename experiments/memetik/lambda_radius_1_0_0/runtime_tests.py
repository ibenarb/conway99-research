"""Early-found cancellation and interruption after actual SQLite inserts."""
import boot
from support import *
from controller import Controller
from tests import FakeHost
import enumeration
import tempfile


def main():
    starts = read(boot.HERE / 'STARTS.json')
    proof = read(boot.HERE / 'TEST_RESULTS.json')['controls']['positive_depth4_witness']
    out = {}
    with tempfile.TemporaryDirectory(prefix='radius-runtime-') as temp:
        root = Path(temp)
        srcpath = root / 'source.sqlite'
        db = connect(srcpath)
        node(db, core.decode_g6(proof['steps'][2]['graph6']), 3, [s['move'] for s in proof['steps'][:3]])
        db.commit()
        db.close()
        run = root / 'run'
        run.mkdir()
        task = {'kind': 'expand', 'arm': '2076', 'depth': 4, 'start': starts['2079'],
                'input': str(srcpath), 'lo': 1, 'hi': 1}
        c = Controller(run, FakeHost(), test=True)
        jobs = [('positive', task, '2076'), ('companion', {'kind': 'spin', 'seconds': 20}, '2076'),
                ('other_arm', {'kind': 'spin', 'seconds': 0.5}, '2077')]
        results = c.execute(jobs, 'EARLY_FOUND', early_found=True, allocation=15)
        assert results['positive']['status'] == 'FOUND'
        assert results['other_arm']['status'] == 'DONE'
        assert 'companion' not in results
        assert c.stopping is None and not c.active
        assert read(run / 'jobs/companion/slice_result.json')['status'] == 'PAUSED'
        before = dict(c.state['used'])
        assert c.execute(jobs, 'RESTART_FOUND', early_found=True, allocation=15) == results
        assert c.state['used'] == before
        c.close()
        out['found_arm_stopped_other_arm_completed'] = True
        out['found_resume_no_extra_cpu'] = True
        srcpath = root / 'interrupt.sqlite'
        db = connect(srcpath)
        node(db, core.decode_g6(starts['2076']['graph6']), 2, [])
        db.commit()
        db.close()
        task = {'kind': 'expand', 'arm': '2076', 'depth': 3, 'start': starts['2076'],
                'input': str(srcpath), 'lo': 1, 'hi': 1}
        d = root / 'interrupt'
        d.mkdir()
        original = enumeration.Scorer
        calls = []
        class FailAfterFour(original):
            def evaluate(self, move):
                if len(calls) == 4:
                    raise Pause('INJECTED_AFTER_FOUR_INSERTS')
                calls.append(move)
                return super().evaluate(move)
        enumeration.Scorer = FailAfterFour
        try:
            enumeration.expand(task, d, Guard())
            raise AssertionError('Interruption missed')
        except Pause:
            assert len(calls) == 4
        finally:
            enumeration.Scorer = original
        db = connect(d / 'work.sqlite')
        assert db.execute('SELECT count(*) FROM nodes').fetchone()[0] == 0
        assert meta(db, 'progress') is None
        db.close()
        result = enumeration.expand(task, d, Guard())
        assert result['children'] == 99 and result['parents'] == 1
        out['rollback_after_four_actual_insertions'] = True
        out['status'] = 'EARLY_FOUND_AND_TRANSACTION_PASS'
        atomic(Path(sys.argv[1]), out)
        print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
