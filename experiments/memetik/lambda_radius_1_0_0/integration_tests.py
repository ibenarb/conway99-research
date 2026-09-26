"""Current-controller and genuine lower-layer tests, without Windows claims."""
import boot
from support import *
from tests import FakeHost
from controller import Controller
from enumeration import lower_layers, EXPECTED, expand
from campaign import chunks
from kernel import catalogue, Scorer
import tempfile


def main():
    starts = read(boot.HERE / 'STARTS.json')
    out = {}
    with tempfile.TemporaryDirectory(prefix='radius-integration-') as temp:
        root = Path(temp)
        for arm in ('2076', '2077'):
            states, first, ev = lower_layers(starts[arm], Guard())
            layer2 = [(r, p) for r, p in states.items() if len(p) == 2]
            assert (first, len(layer2)) == EXPECTED[arm][:2]
            # Genuine depth-2 paths and independently evaluated children at three spread positions.
            samples = [layer2[i] for i in (0, len(layer2) // 2, len(layer2) - 1)]
            source = root / (arm + '.sqlite')
            db = connect(source)
            expected = set()
            n = 0
            for rows, path in samples:
                replay = core.decode_g6(starts[arm]['graph6'])
                for move in path:
                    replay = core.apply_move(replay, move)
                assert tuple(replay) == rows
                node(db, rows, 2, path)
                sc = Scorer(rows)
                for _, move in catalogue(rows, False, Guard()):
                    child, scores = sc.evaluate(move)
                    _, full = checked(core.encode_g6(child), 'lambda')
                    assert scores == full
                    expected.add(pack(child))
                    n += 1
            db.commit()
            db.close()
            jobs = chunks(arm, 3, source, (1, 3, 3), starts[arm], size=1)
            assert [(t['lo'], t['hi']) for _, t, _ in jobs] == [(1, 1), (2, 2), (3, 3)]
            actual = set()
            count = 0
            for name, task, category in jobs:
                d = root / name
                d.mkdir()
                atomic(d / 'task.json', task)
                result = expand(task, d, Guard())
                assert result['status'] == 'DONE'
                count += result['children']
                db = connect(d / 'work.sqlite', True)
                actual.update(r[0] for r in db.execute('SELECT rows FROM nodes'))
                db.close()
            assert count == n and actual == expected
            out[arm] = {'n_L1': first, 'n_L2': len(layer2), 'sampled_depth2_parents': 3,
                        'independently_verified_children': n, 'chunk_union_exact': True}
        run = root / 'controller'
        run.mkdir()
        c = Controller(run, FakeHost(), test=True)
        jobs = [('short', {'kind': 'spin', 'seconds': 0.05}, 'aux')]
        r = c.execute(jobs, 'CURRENT_CONTROLLER', allocation=6)
        assert r['short']['status'] == 'DONE'
        receipt = read(run / 'jobs/short/receipt.json')
        assert 0 < receipt['cpu_seconds'] <= receipt['sessions'][0]['host_elapsed'] * 1.02 + 0.1
        assert not c.state['active']
        c.close()
        # A changed durable output must be rejected, not accepted as completed work.
        p = run / 'jobs/short/slice_result.json'
        p.write_text('{}')
        c = Controller(run, FakeHost(), test=True)
        try:
            c.done(p.parent)
            raise AssertionError('Tampered result accepted')
        except RuntimeError:
            out['tampered_result_refused'] = True
        finally:
            c.close()
        out['status'] = 'GENUINE_LAYERS_AND_CURRENT_CONTROLLER_PASS'
        atomic(Path(sys.argv[1]), out)
        print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
