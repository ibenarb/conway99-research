"""Real short two-wave scheduling and isolated-lineage smoke test."""
import boot
from util import *
from integration_tests import execute, task
from prepare import ORIGINS, validate_founders
from search import select
import tempfile
import random


def main():
    bank = read(boot.HERE / 'ISOLATED_BANKS.json')[ORIGINS[0]]['population']
    validate_founders(bank)
    selected = select(bank, bank, 'lambda', 'W', random.Random(24), 0, [bank[0]['family']])
    assert len(selected) == 16 and len({p['class'] for p in selected}) == 16
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        jobs = []
        for name, group, variant in [('A', 'V1', 'P'), ('B', 'V1', 'PCesc'), ('C', 'V3', 'P')]:
            d = root / 'runs' / 'comparison' / 'tasks' / name
            d.mkdir(parents=True)
            t = task(variant, 9, bank)
            t['id'] = name
            atomic(d / 'task.json', t)
            jobs.append({'id': name, 'group': group, 'variant': variant, 'target': 'W',
                         'directory': str(d.relative_to(root)), 'initial_actual_cpu': 0,
                         'cumulative_budget_seconds': 9, 'additional_cpu_seconds': 9})
        atomic(root / 'runs/comparison/budget.json', {'per_job_cpu_seconds': 9})
        plan = {'workers': 16, 'jobs': jobs, 'queue': ['A', 'B', 'C']}
        assert execute(root, plan) == 'COMPLETE'
        receipts = [receipt_valid(root / j['directory']) for j in jobs]
        assert receipts[2]['sessions'][0]['host_start'] >= max(r['sessions'][0]['host_end'] for r in receipts[:2])
        for j in jobs:
            result = read(root / j['directory'] / 'result.json')
            assert all(p['line'] == ORIGINS[0] and p['family'] != 'HoG' for p in result['final_population'])
            assert 'experiment_metrics' in result
    print(json.dumps({'status': 'WAVE_PASS', 'V3_waits_for_all_V1': True,
                      'isolated_selection_and_real_workers': True,
                      'test_host_is_fixture': True, 'child_cpu': child_cpu()}))


if __name__ == '__main__':
    main()
