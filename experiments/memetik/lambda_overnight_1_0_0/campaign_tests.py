"""Real eight-job smoke test; shortened budgets and host fixtures only here."""
import boot
from util import *
import prepare
import evaluate
from checks import run_checks
from integration_tests import execute
from unittest.mock import patch
import tempfile


def main():
    output = Path(sys.argv[1])
    report = {'fixture': 'Shortened CPU budgets; Windows host and resources mocked only in test harness.'}
    assert [evaluate.decision(i) for i in (0, 1, 2, 8)] == [
        'PAUSE_W_FRONTIER', 'SINGLE_SIGNAL_REVIEW_ONLY',
        'REPEATED_SIGNAL_REVIEW_ONLY', 'REPEATED_SIGNAL_REVIEW_ONLY']
    with tempfile.TemporaryDirectory() as temp:
        run = Path(temp) / 'run'
        prepare.prepare(None, run)
        plan = prepare.verify(run)
        report['controls'] = run_checks(run)
        assert plan['authorized_search_cpu_hours'] == 56
        assert [j['frontier_W'] for j in plan['jobs']] == [2081] * 6 + [2092] * 2
        assert [j['seed'] for j in plan['jobs']] == list(range(2026092800, 2026092808))
        assert all(j['cumulative_budget_seconds'] == 25200 for j in plan['jobs'])
        for job in plan['jobs']:
            job['cumulative_budget_seconds'] = 9
            job['additional_cpu_seconds'] = 9
        atomic(run / 'runs/comparison/budget.json', {'per_job_cpu_seconds': 9})
        assert execute(run, plan) == 'COMPLETE'
        receipts = [receipt_valid(run / j['directory']) for j in plan['jobs']]
        assert max(r['sessions'][0]['host_start'] for r in receipts) < min(r['sessions'][0]['host_end'] for r in receipts)
        with patch.object(evaluate, 'verify', return_value=plan):
            result = evaluate.evaluate(run)
        assert len(result['jobs']) == 8
        assert result['automatic_extension'] is False
        # Actual verifier rejects the changed budget.
        try:
            prepare.verify(run)
        except RuntimeError as error:
            assert 'Frozen input changed' in str(error)
        else:
            raise AssertionError('Changed budget accepted')
        report.update(all_eight_workers_overlapped=True, budget_tamper_rejected=True,
                      real_endpoint_evaluation=result, decision_branches_checked=True)
    report.update(status='CAMPAIGN_TEST_PASS', own_cpu=own_cpu(), waited_child_cpu=child_cpu())
    atomic(output, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
