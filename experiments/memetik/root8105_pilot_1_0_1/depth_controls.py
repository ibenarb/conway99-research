"""Synthetic depth-boundary tests, plus real rook completion and campaign stop."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import worker
from completion import verify_complete
from core import Geometry, atomic

BASE = Path(__file__).resolve().parent


class SyntheticGeometry:
    n = 84

    def __init__(self, m):
        pass

    def verify(self, rows):
        assert set(rows) == set(range(len(rows)))

    def key(self, rows):
        return str(sorted(rows)).encode()

    def targets(self, rows, *args):
        return [len(rows)]


def synthetic(directory, seconds):
    cfg = json.loads((BASE / 'config.json').read_text())
    cfg['proofs_per_job'] = 0
    job = directory / 'job.json'
    atomic(job, {'root_id': 0, 'row': '0x0', 'arm': 'ordered', 'seed': 0, 'config': cfg})
    clock = [0.0]
    visited = []
    def enumerate_fake(g, rows, target, *args, **kwargs):
        visited.append(target)
        clock[0] += 1
        artifact = Path(kwargs['artifact'])
        artifact.mkdir(parents=True)
        return [0], {'count': 1, 'status': 'LIMIT_UNRESOLVED'}
    def complete_fake(g, rows):
        assert len(rows) == 84
        return {'status': 'SYNTHETIC_CONTROL_ONLY'}
    argv = ['worker.py', str(job), str(directory / 'work'), '--cpu', str(seconds)]
    worker.STOP = False
    with patch.object(sys, 'argv', argv), patch.object(worker, 'limits'), \
         patch.object(worker, 'Geometry', SyntheticGeometry), \
         patch.object(worker, 'encode', return_value=(None, None)), \
         patch.object(worker, 'enumerate_projection', side_effect=enumerate_fake), \
         patch.object(worker, 'verify_complete', side_effect=complete_fake), \
         patch.object(worker.time, 'process_time', side_effect=lambda: clock[0]):
        worker.main()
    result = json.loads((directory / 'work' / 'worker_result.json').read_text())
    return result, visited


def run_tests(directory=None):
    out = Path(directory or tempfile.mkdtemp(prefix='root8105_depth101_'))
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((BASE / 'config.json').read_text())
    comparisons = 0
    for remaining in (1.0, 300.0, 3600.0):
        for depth in range(1, 29):
            old = min(remaining, max(cfg['node_cpu_s'], remaining / (32 - depth)))
            assert worker.level_cpu_budget(remaining, depth, cfg) == old
            comparisons += 1
    assert worker.level_cpu_budget(3600, 32, cfg) == 900
    for depth in range(1, 84):
        assert 0 < worker.level_cpu_budget(300, depth, cfg) <= 300
    a = out / 'synthetic_complete'; a.mkdir()
    result, visited = synthetic(a, 100)
    assert visited == list(range(1, 84)) and result['state']['max_depth'] == 84
    assert 32 in result['state']['milestones_reached']
    assert result['status'] == 'SRG_FOUND_VERIFIED'
    b = out / 'synthetic_budget'; b.mkdir()
    limited, visited = synthetic(b, 34)
    assert limited['status'] == 'CPU_LIMIT_UNKNOWN'
    assert limited['state']['max_depth'] == 35 and 32 in visited
    # Actual mathematical positive control, NOT a 99-vertex existence claim.
    full = {0: 6, 1: 9, 2: 9, 3: 6}
    exact = verify_complete(Geometry(2), full)
    assert exact['parameters'] == [9, 4, 1, 2]
    try:
        verify_complete(Geometry(2), {**full, 3: 7})
        raise AssertionError('corrupt graph accepted')
    except ValueError:
        pass
    real = out / 'rook_campaign'
    (real / 'jobs').mkdir(parents=True)
    cfg.update({'workers': 1, 'job_cpu_s': 10, 'node_cpu_s': 1,
                'proofs_per_job': 0, 'milestones': [2, 3, 4],
                'available_memory_reserve_gib': 0.1, 'emergency_available_gib': 0.01,
                'free_disk_reserve_gib': 0.01})
    atomic(real / 'manifest.json', {'jobs': ['rook', 'pending'], 'config': cfg})
    for name in ('rook', 'pending'):
        atomic(real / 'jobs' / (name + '.json'), {'m': 2, 'root_id': 0, 'row': '0x6',
                                                'arm': 'ordered', 'seed': 1, 'config': cfg})
    done = subprocess.run([sys.executable, str(BASE / 'campaign.py'), str(real), '--test'],
                          capture_output=True, timeout=30)
    (real / 'controller.log').write_bytes(done.stdout + done.stderr)
    assert done.returncode == 0, done.stderr.decode()
    assert json.loads((real / 'status.json').read_text())['status'] == 'VERIFIED_SRG_FOUND'
    assert len(json.loads((real / 'receipts.json').read_text())) == 1
    assert json.loads((real / 'solution.json').read_text())['parameters'] == [9, 4, 1, 2]
    answer = {'status': 'PASS', 'shallow_budget_comparisons': comparisons,
              'synthetic_path_crosses_32_and_reaches_84': True,
              'synthetic_budget_stops_at_35_unknown': True,
              'synthetic_tests_are_not_99_vertex_graphs': True,
              'actual_rook_verified_and_campaign_stopped': True,
              'corrupt_full_graph_rejected': True}
    atomic(out / 'depth_controls.json', answer)
    return answer


if __name__ == '__main__':
    print(json.dumps(run_tests()), flush=True)
