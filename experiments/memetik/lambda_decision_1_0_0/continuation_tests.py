"""Real archived V3 states plus fresh V2 tasks; reduced budgets only in harness."""
import boot
from util import *
import prepare
import evaluate
from checks import run_checks
from integration_tests import execute
from unittest.mock import patch
import tempfile


def main():
    source = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    expected_env = read(source / 'FINGERPRINT.json')['environment']
    expected = read(boot.HERE / 'SOURCE_RUN.json')
    old_worker = source / 'program/experiments/memetik/lambda_prechecks_1_0_0/worker.py'
    expected_worker = old_worker.read_text().replace(
        "ceiling = read(root/'budget.json')['per_job_cpu_seconds'] if task['kind']=='compare' else task['worker_cpu_seconds']",
        "ceiling = read(root/'budget.json')['per_job_cpu_seconds']")
    assert (boot.HERE / 'worker.py').read_text() == expected_worker
    report = {'worker_change_only_external_budget_lookup': True,
              'fixture': 'Source environment check uses archived Python version; Windows clock/resources mocked only here.'}
    with tempfile.TemporaryDirectory() as temp:
        run = Path(temp) / 'run'
        with patch.object(prepare, 'env', return_value=expected_env):
            prepare.prepare(source, run)
            plan = prepare.verify(run)
            report['controls'] = run_checks(run)
            # Verify both replicas have byte-equal populations and distinct seeds.
            tasks = [read(run / j['directory'] / 'task.json') for j in plan['jobs'][:6]]
            for a, b in zip(tasks[::2], tasks[1::2]):
                assert a['founders'] == b['founders'] and a['seed'] != b['seed']
            # The production manifest is never changed: only this in-memory test plan and budgets.
            for job in plan['jobs']:
                if job['group'] == 'V2':
                    job['cumulative_budget_seconds'] = 9
                    job['additional_cpu_seconds'] = 9
                else:
                    job['cumulative_budget_seconds'] = 7209
                    job['additional_cpu_seconds'] = 9
            atomic(run / 'runs/comparison/budget.json', {'per_job_cpu_seconds': 9})
            atomic(run / 'runs/records/budget.json', {'per_job_cpu_seconds': 7209})
            assert execute(run, plan) == 'COMPLETE'
            # Both families must have overlapped in host time.
            starts = {}; ends = {}
            for j in plan['jobs']:
                receipt = receipt_valid(run / j['directory'])
                starts[j['id']] = receipt['sessions'][-1]['host_start']
                ends[j['id']] = receipt['sessions'][-1]['host_end']
            assert max(starts.values()) < min(ends.values())
            with patch.object(evaluate, 'verify', return_value=plan):
                report['evaluation'] = evaluate.evaluate(run)
            for job in plan['jobs'][6:]:
                d = run / job['directory']
                baseline = run / 'baseline' / job['id']
                before = read(baseline / 'checkpoint.json')['state']
                after = read(d / 'checkpoint.json')['state']
                assert after['iterations'] >= before['iterations']
                assert after['evaluated_moves'] != before['evaluated_moves']
                assert read(d / 'result.json')['endpoint_cpu_seconds'] == 7209
                assert len(receipt_valid(d)['sessions']) == len(read(baseline / 'receipt.json')['sessions']) + 1
            report['all_8_real_v3_states_advanced'] = True
            report['all_14_workers_overlapped'] = True
            report['same_bank_different_v2_seeds'] = True
            # Frozen-budget tampering is rejected by real verifier.
            try:
                prepare.verify(run)
            except RuntimeError as error:
                assert 'Frozen input changed' in str(error)
            else:
                raise AssertionError('Changed budget accepted')
            report['budget_tamper_rejected'] = True
        # All original task/receipt/checkpoint/result/archive bytes remain unchanged.
        for jid, hashes in expected['jobs'].items():
            for name, digest in hashes.items():
                assert file_sha(source / 'runs/records/tasks' / jid / name) == digest
        report['original_source_unchanged'] = True
    report.update(status='CONTINUATION_INTEGRATION_PASS', own_cpu=own_cpu(), waited_child_cpu=child_cpu())
    atomic(output, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
