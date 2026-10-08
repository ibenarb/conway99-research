"""Real CLI end accounting and fault controls; no ROOT8105 search."""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import accounting as a
import runtime as r
from test_runtime import wait_state

UNSAT = 'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=Path, required=True)
    p.add_argument('--checker', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    rows = []

    def record(name, **details):
        rows.append(dict(test=name, passed=True, **details))
        print(name, 'PASS', flush=True)

    def command(root, action, *extra, fault=None):
        env = dict(os.environ)
        if fault:
            env['N1_TEST_FAULT'] = fault
        log = out/(root.name+'-'+action+'-'+str(time.time_ns())+'.log')
        with log.open('wb') as stream:
            return subprocess.Popen([sys.executable, r.__file__, action, str(root),
                *map(str, extra)], env=env, stdout=stream, stderr=subprocess.STDOUT)

    def new(name, cnf=UNSAT, budget=60, checker=None):
        source = out/(name+'.cnf')
        source.write_text(cnf)
        root = out/name
        require(command(root, 'init', '--cnf', source, '--worker', args.worker,
            '--checker', checker or args.checker, '--budget', budget).wait() == 0, 'init')
        (root/'ALLOW_TEST_FAULTS').touch()
        return root

    root = new('normal')
    require(command(root, 'run').wait() == 0, 'normal run')
    report = a.audit(root)
    require(report['observed_commands_complete'] and len(report['sessions']) == 2, 'closed CLI history')
    expected = report['native_search_confirmed_s']+report['native_check_confirmed_s']+report['supervisor_confirmed_s']
    require(abs(expected-report['inclusive_wait4_confirmed_s']) < 1e-9, 'partition sum')
    require(report['supervisor_confirmed_s'] > 0 and report['observer_cpu_lower_bound_s'] > 0, 'overheads missing')
    require(not report['all_system_cpu_complete'] and report['host_cpu_s'] is None, 'false global accounting')
    record('init_search_checker_supervisor_partition_without_double_count', report=report)
    again = a.audit(root)
    require(again == report, 'audit not idempotent')
    record('readonly_repeated_audit_does_not_rebook_CPU')
    before = len(list((root/'attempts').iterdir()))
    require(command(root, 'resume').wait() == 0, 'terminal reuse')
    after = a.audit(root)
    require(after['native_search_confirmed_s'] == report['native_search_confirmed_s'] and
            len(list((root/'attempts').iterdir())) == before and
            after['inclusive_wait4_confirmed_s'] > report['inclusive_wait4_confirmed_s'], 'reuse overhead or duplicate search')
    record('terminal_reuse_charges_only_new_control_work')
    require(command(root, 'accounts').wait() == 0, 'accounts CLI')
    require(len(a.audit(root)['sessions']) == 4, 'inspection command not booked')
    record('account_inspection_itself_has_an_end_receipt')

    root = new('inner_crash')
    require(command(root, 'run', fault='search_after_receipt').wait() == 91, 'inner fault')
    prior = a.audit(root)
    require(not prior['gaps'] and not prior['partition_complete'], 'lost inner snapshot wrongly exact')
    require(command(root, 'recover', '--apply').wait() == 0, 'recovery')
    require(command(root, 'resume').wait() == 0, 'checker continuation')
    require(r.read(root/'state.json')['status'] == 'UNSAT_CERTIFIED', 'recovered result')
    require(len(list((root/'attempts').glob('*/search_receipt.json'))) == 1, 'repeated search')
    require(a.audit(root)['inclusive_wait4_confirmed_s'] > prior['inclusive_wait4_confirmed_s'], 'recovery CPU missing')
    record('crashed_inner_has_outer_end_total_and_checker_only_resume')

    root = new('outer_after_receipt')
    require(command(root, 'status', fault='observer_after_receipt').wait() == 91, 'outer sealed fault')
    require(a.audit(root)['observed_commands_complete'], 'sealed receipt lost')
    require(command(root, 'run').wait() == 0, 'sealed outer resume')
    record('outer_exit_after_receipt_preserves_account_without_cache')

    root = new('outer_missing_receipt')
    require(command(root, 'status', fault='observer_after_wait4').wait() == 91, 'outer missing fault')
    report = a.audit(root)
    require(len(report['gaps']) == 1 and report['gaps'][0]['cpu_s'] is None, 'missing end treated as zero')
    before = {str(f): r.sha(f) for f in (root/'states').glob('*.json')}
    require(command(root, 'run').wait() != 0, 'unsafe resume accepted')
    require(before == {str(f): r.sha(f) for f in (root/'states').glob('*.json')} and
            not list((root/'attempts').iterdir()), 'blocked run modified scientific state')
    record('missing_observer_wait4_receipt_blocks_search_without_zero_or_repair')

    root = new('bad_cpu')
    receipt = next((a.ledger(root)/'sessions').glob('*/receipt.json'))
    original = receipt.read_bytes()
    value = r.read(receipt)
    value['inclusive_wait4_cpu_s'] = -1
    r.raw_atomic(receipt, value)
    try:
        a.audit(root)
    except ValueError:
        pass
    else:
        raise AssertionError('negative CPU accepted')
    receipt.write_bytes(original)
    record('negative_CPU_rejected_even_with_recomputed_envelope')

    # Same real checker, delayed wrapper completion to exercise stop and reuse.
    checker = out/'checker_wrapper.py'
    checker.write_text('#!'+sys.executable+'\nimport pathlib,subprocess,sys,time\n'
        +'p=subprocess.run(['+repr(str(args.checker))+']+sys.argv[1:])\n'
        +"pathlib.Path('READY_CHECK').touch()\n"
        +"while not (pathlib.Path.cwd().parents[1]/'RELEASE').exists():\n"
        +'    sum(i*i for i in range(10000))\n'
        +'sys.exit(p.returncode)\n')
    checker.chmod(0o755)
    root = new('stop_resume', budget=0.01, checker=checker)
    proc = command(root, 'run')
    state = wait_state(root, lambda x: x.get('phase') == 'check' and x['request'], proc)
    while not list((root/'attempts').glob('*/READY_CHECK')):
        require(proc.poll() is None, 'checker ended early')
        time.sleep(0.02)
    old = state['live_cpu']
    state = wait_state(root, lambda x: x['live_cpu'] > old+0.08, proc)
    require(command(root, 'reply', '--request', state['request']['id'], '--seconds', 0,
                    '--answer-id', 'stopchecker').wait() == 0, 'reply process')
    require(proc.wait() == 0, 'stop completion')
    stopped = a.audit(root)
    require(stopped['observed_commands_complete'], 'stopped account incomplete')
    (root/'RELEASE').touch()
    require(command(root, 'resume').wait() == 0, 'resume checker')
    final = a.audit(root)
    require(final['observed_commands_complete'] and
            final['native_search_confirmed_s'] == stopped['native_search_confirmed_s'] and
            final['native_check_confirmed_s'] > stopped['native_check_confirmed_s'], 'stop/resume totals')
    require(r.read(root/'state.json')['status'] == 'UNSAT_CERTIFIED', 'final status')
    require(any(x['action'] == 'reply' for x in final['sessions']), 'reply CPU absent')
    record('concurrent_reply_zero_resume_keeps_disjoint_cumulative_accounts', report=final)
    result = dict(complete=True, tests=rows, N1_class_searches=0, production_approved=False)
    r.raw_atomic(out/'TEST_RESULTS.json', result)
    print('PASS', len(rows), flush=True)


if __name__ == '__main__':
    main()
