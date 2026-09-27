"""Reduced full controller and actual CPU-slice checkpoint/resume tests."""
import boot
from support import *
from tests import FakeHost
from controller import Controller
from campaign import execute_profile, snapshot
import campaign as pipeline
import tempfile


def main():
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        small = root / 'small'
        small.mkdir()
        pipeline.N = 1
        pipeline.LENGTHS = (2, 8)
        pipeline.campaign(small, FakeHost(), test=True)
        result = read(small / 'RESULT.json')
        assert result['status'] == 'COMPLETE'
        assert len(result['cells']) == 4 and all(x['completed'] == 1 for x in result['cells'].values())
        assert not read(small / 'ledger.json')['active']
        assert not (small / 'session_active.json').exists()
        out['full_reduced_pipeline'] = True
        out['calibration_observations_retained'] = True
        starts = read(boot.HERE / 'STARTS.json')
        task = {'kind': 'profile', 'arm': '2076', 'k': 32, 'n': 1, 'start': starts['2076']}
        paused = root / 'paused'
        paused.mkdir()
        c = Controller(paused, FakeHost(), test=True)
        try:
            d = c.job('2076_k32', task)
            assert c.spawn('2076_k32', d, '2076_k32', 6)
            results = []
            while c.active:
                c.host.sample()
                results.extend(c.reap())
                time.sleep(.02)
            assert results[0][1]['status'] == 'PAUSED'
            state = snapshot(c, '2076_k32', task)
            assert state['episode'] is not None and state['episode']['path']
            first_charge = c.state['used']['2076_k32']
            assert 0 < first_charge <= 6
            r = execute_profile(c, [('2076_k32', task, '2076_k32')], 1, 'CPU_RESUME')
            assert r['2076_k32']['status'] == 'DONE'
            receipt = read(d / 'receipt.json')
            assert len(receipt['sessions']) >= 2
            assert abs(sum(s['cpu_seconds'] for s in receipt['sessions']) - c.state['used']['2076_k32']) < 1e-8
            out['actual_cpu_pause_resume_and_wait4_sum'] = True
        finally:
            c.close()
    out['status'] = 'PASS'
    atomic(boot.HERE / 'INTEGRATION_RESULTS.json', out)
    print(json.dumps(out))


if __name__ == '__main__':
    main()
