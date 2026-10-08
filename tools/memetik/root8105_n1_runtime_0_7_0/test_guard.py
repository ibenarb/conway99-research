"""Synthetic controls for aggregate decision points and resource-stop recovery."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import accounting as accounts
import guard
import runtime as r
from test_runtime import wait_state


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def pigeonhole():
    n, h = 22, 21
    clauses = [[i*h+j+1 for j in range(h)] for i in range(n)]
    clauses += [[-(i*h+j+1), -(k*h+j+1)] for j in range(h) for i in range(n) for k in range(i)]
    return 'p cnf %d %d\n' % (n*h, len(clauses))+''.join(' '.join(map(str,c))+' 0\n' for c in clauses)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--worker', type=Path, required=True)
    p.add_argument('--checker', type=Path, required=True)
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    rows = []
    safe = dict(free_bytes=10**12, available_bytes=10**12, rss_bytes=1024)

    def record(name, **details):
        rows.append(dict(test=name, passed=True, **details))
        print(name, 'PASS', flush=True)

    def command(root, action, *extra, fake=False, fault=None):
        env = dict(os.environ)
        if fake:
            env['N1_TEST_RESOURCES'] = '1'
        if fault:
            env['N1_TEST_FAULT'] = fault
        log = out/(root.name+'-'+action+'-'+str(time.time_ns())+'.log')
        with log.open('wb') as stream:
            return subprocess.Popen([sys.executable,r.__file__,action,str(root),*map(str,extra)],
                env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)

    def new(name, native=60, total=60, formula=None):
        root = out/name
        cnf = out/(name+'.cnf')
        cnf.write_text(formula or pigeonhole())
        require(command(root, 'init', '--cnf', cnf, '--worker',args.worker,'--checker',args.checker,
            '--budget',native,'--total-budget',total,'--max-rss-bytes',10**10,
            '--min-free-bytes',10**7,'--min-available-bytes',10**7).wait() == 0,'init')
        (root/'ALLOW_TEST_FAULTS').touch()
        r.raw_atomic(root/'TEST_RESOURCES.json',safe)
        return root

    def reply(root, req, seconds, answer, scope):
        require(command(root,'reply','--request',req,'--seconds',seconds,'--answer-id',answer,
                        '--scope',scope).wait() == 0,'reply')

    # All four explicit limits are required; no guessed target-machine limits.
    try:
        guard.config(1,None,1,1)
    except ValueError:
        pass
    else:
        raise AssertionError('partial config accepted')
    record('explicit_budget_and_all_resource_limits_required')
    root = new('two_budgets',native=0.01,total=0.01)
    proc = command(root,'run',fake=True)
    s = wait_state(root,lambda s:s['request'] and s['guard']['request'] and s.get('child'),proc)
    ident = s['child']; start = s['live_cpu']; request = s['guard']['request']['id']
    s = wait_state(root,lambda s:s['live_cpu'] > start+0.15,proc)
    require(s['child']==ident and not s['stop'],'no-response stopped solver')
    record('EOF_no_reply_continues_same_worker_with_both_requests')
    reply(root,'stale',9,'stale','total')
    wait_state(root,lambda s:s['replies'].get('stale')=='REJECTED',proc)
    s=r.read(root/'state.json')
    require(s['guard']['budget']==0.01 and s['budget']==0.01,'stale extension')
    record('stale_total_reply_rejected')
    reply(root,request,1,'totalextend','total')
    reply(root,request,1,'totalextend','total')
    s=wait_state(root,lambda s:s['replies'].get('totalextend')=='ACCEPTED',proc)
    require(s['guard']['budget']==1.01 and s['budget']==0.01 and s['child']==ident,'scope/dedup')
    reply(root,s['request']['id'],2,'nativeextend','native')
    s=wait_state(root,lambda s:s['replies'].get('nativeextend')=='ACCEPTED',proc)
    require(s['budget']==2.01 and s['guard']['budget']==1.01,'native modified total')
    record('two_scopes_extend_independently_once_without_restart')
    s=wait_state(root,lambda s:s['guard']['request'] and s['guard']['request']['id']!=request,proc)
    require(s['child']==ident,'repeated total budget restarted worker')
    reply(root,s['guard']['request']['id'],0,'totalzero','total')
    require(proc.wait()==0,'controlled total zero')
    stopped=r.read(root/'state.json')
    require(stopped['status']=='STOPPED_UNRESOLVED' and stopped['accounting_complete'],'stop/account')
    old={str(f.relative_to(root)):r.sha(f) for f in (root/'attempts').rglob('*') if f.is_file()}
    record('repeated_total_budget_zero_seals_partial_proof_and_end_accounts')
    proc=command(root,'resume',fake=True)
    s=wait_state(root,lambda s:s['guard']['request'] and s.get('child'),proc)
    require(s['guard']['budget']==1.01 and s['budget']==2.01 and
            s['guard']['consumed_lower_bound_s']>=stopped['guard']['consumed_lower_bound_s'],'resume reset budgets/CPU')
    reply(root,s['guard']['request']['id'],0,'resumezero','total')
    require(proc.wait()==0,'resume zero')
    require(all(r.sha(root/n)==h for n,h in old.items()),'old proof/account changed')
    record('resume_preserves_budgets_answers_CPU_and_old_artifacts')

    for key,reason,value in [('free_bytes','DISK_RESERVE',0),
                             ('available_bytes','MEMORY_AVAILABLE',0),
                             ('rss_bytes','RUN_RSS',10**11)]:
        root=new(reason)
        proc=command(root,'run',fake=True)
        wait_state(root,lambda s:s.get('child') and s['live_cpu']>0.05,proc)
        r.raw_atomic(root/'TEST_RESOURCES.json',dict(safe,**{key:value}))
        require(proc.wait()==0,'resource stop')
        s=r.read(root/'state.json')
        require(s['status']=='RESOURCE_STOPPED' and s['guard']['stop_reason']['reason']==reason
                and s['accounting_complete'] and not (root/'emergency.reserve').exists(),'resource cause/reserve/account')
        old_count=len(list((root/'attempts').iterdir()))
        require(command(root,'resume',fake=True).wait()==0,'unsafe preflight')
        require(len(list((root/'attempts').iterdir()))==old_count,'unsafe resumed search')
        r.raw_atomic(root/'TEST_RESOURCES.json',safe)
        proc=command(root,'resume',fake=True)
        wait_state(root,lambda s:s.get('child') and len(s['attempts'])==old_count,proc)
        r.raw_atomic(root/'TEST_RESOURCES.json',dict(safe,free_bytes=0))
        require(proc.wait()==0,'cleanup')
        require(len(list((root/'attempts').iterdir()))==old_count+1,'cleared resume missing')
        record(reason+'_stops_only_own_run_and_rechecks_before_resume')

    root=new('sensor_failure')
    proc=command(root,'run',fake=True)
    wait_state(root,lambda s:s.get('child') and s['live_cpu']>0.05,proc)
    (root/'TEST_RESOURCES.json').unlink()
    require(proc.wait()==0,'sensor failure stop')
    require(r.read(root/'state.json')['guard']['stop_reason']['reason']=='MONITOR_ERROR','missing sensor ignored')
    record('missing_resource_sensor_is_explicit_controlled_stop')

    # Ordinary completion closes an outstanding total request without waiting.
    unsat='p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n'
    root=new('normal_completion',total=0.001,formula=unsat)
    require(command(root,'run').wait()==0,'real-sensor completion')
    s=r.read(root/'state.json')
    require(s['status']=='UNSAT_CERTIFIED' and s['guard']['request'] is None and
            any(e['reason']=='REQUEST_CLOSED_ON_TASK_END' for e in s['guard']['events']),'unfinished request at completion')
    require(not s['guard']['snapshot']['resources']['synthetic'],'real sensor path not exercised')
    record('normal_certified_completion_closes_request_real_sensors')

    # The scanner must not add native subreceipts to the inclusive end total.
    report=accounts.audit(root)
    require(s['guard']['consumed_lower_bound_s'] <= report['accounted_lower_bound_s']+0.03,
            'live estimate exceeds completed inclusive account')
    record('aggregate_live_vs_final_disjoint_account_reconciliation')
    # A committed total-budget reply survives an immediate interpreter exit.
    root=new('reply_transaction',formula=unsat)
    state=r.read(root/'state.json')
    state['guard']['request']=dict(id='transaction',scope=guard.SCOPE)
    r.atomic(root/'state.json',state)
    r.reply(root,'transaction',7,'once','total')
    script=("import sys;from pathlib import Path;sys.path.insert(0,"+repr(str(Path(r.__file__).parent))+
        ");import runtime as r;root=Path("+repr(str(root))+");r.service(root,r.read(root/'state.json'))")
    env=dict(os.environ,N1_TEST_FAULT='state_after_generation')
    require(subprocess.run([sys.executable,'-c',script],env=env).returncode==91,'transaction fault')
    require(command(root,'recover','--apply').wait()==0,'transaction recovery')
    require(command(root,'run',fake=True).wait()==0,'transaction completion')
    state=r.read(root/'state.json')
    require(state['guard']['budget']==67 and len(state['reply_events'])==1,'duplicate total extension')
    record('total_reply_and_budget_commit_together_across_real_exit')
    # A resealed state cannot silently increase the recorded total budget.
    root=new('budget_tamper',formula=unsat)
    state=r.read(root/'state.json');state['guard']['budget']+=10
    r.atomic(root/'state.json',state)
    require(command(root,'run',fake=True).wait()!=0 and not list((root/'attempts').iterdir()),
            'unexplained total budget accepted')
    record('unexplained_resealed_budget_change_rejected_before_search')

    buddy=new('independent_buddy')
    other=command(buddy,'run',fake=True)
    wait_state(buddy,lambda s:s.get('child') and s['live_cpu']>0.05,other)
    root=new('independent_stop')
    proc=command(root,'run',fake=True)
    wait_state(root,lambda s:s.get('child') and s['live_cpu']>0.05,proc)
    r.raw_atomic(root/'TEST_RESOURCES.json',dict(safe,free_bytes=0))
    require(proc.wait()==0 and other.poll() is None,'unrelated run stopped')
    current=r.read(buddy/'state.json')['live_cpu']
    wait_state(buddy,lambda s:s['live_cpu']>current+0.1,other)
    r.raw_atomic(buddy/'TEST_RESOURCES.json',dict(safe,free_bytes=0))
    require(other.wait()==0,'buddy cleanup')
    record('resource_stop_leaves_independent_real_worker_running')

    wrapper=out/'delayed_checker.py'
    wrapper.write_text('#!'+sys.executable+'\nimport pathlib,subprocess,sys\n'
        +'p=subprocess.run(['+repr(str(args.checker))+']+sys.argv[1:])\n'
        +"pathlib.Path('READY_CHECK').touch()\n"
        +"while not (pathlib.Path.cwd().parents[1]/'RELEASE').exists():\n"
        +'    sum(i*i for i in range(5000))\n'+'sys.exit(p.returncode)\n')
    wrapper.chmod(0o755)
    # Create explicitly with the delayed checker, preserving its pinned identity.
    root=out/'checker_resource'
    source=out/'checker_resource.cnf';source.write_text(unsat)
    require(command(root,'init','--cnf',source,'--worker',args.worker,'--checker',wrapper,
        '--budget',60,'--total-budget',60,'--max-rss-bytes',10**10,
        '--min-free-bytes',10**7,'--min-available-bytes',10**7).wait()==0,'checker init')
    (root/'ALLOW_TEST_FAULTS').touch();r.raw_atomic(root/'TEST_RESOURCES.json',safe)
    proc=command(root,'run',fake=True)
    wait_state(root,lambda s:s.get('phase')=='check' and s.get('child'),proc)
    while not list((root/'attempts').glob('*/READY_CHECK')):
        require(proc.poll() is None,'checker ended');time.sleep(0.02)
    source=next((root/'attempts').glob('*/proof.partial'));digest=r.sha(source)
    r.raw_atomic(root/'TEST_RESOURCES.json',dict(safe,available_bytes=0))
    require(proc.wait()==0 and r.read(root/'state.json')['status']=='RESOURCE_STOPPED','checker stop')
    require(r.sha(source)==digest,'proof altered')
    (root/'RELEASE').touch();r.raw_atomic(root/'TEST_RESOURCES.json',safe)
    require(command(root,'resume',fake=True).wait()==0,'checker resume')
    require(r.read(root/'state.json')['status']=='UNSAT_CERTIFIED' and r.sha(source)==digest and
            len(list((root/'attempts').glob('*/search_receipt.json')))==1,'checker re-searched')
    record('resource_stop_preserves_sealed_proof_then_checker_only_resume')

    # Controlled accounting fixtures: 257 directories, no real tasks or CPU claims.
    root=out/'scanner_fixture';root.mkdir()
    meta=accounts.ensure(root)
    folder=accounts.ledger(root)/'sessions'
    observer=r.identity(os.getpid())
    for i in range(257):
        sid=format(i,'032x');directory=folder/sid;directory.mkdir()
        intent=dict(id=sid,ledger_id=meta['id'],root=str(root),observer=observer,action='fixture')
        r.raw_atomic(directory/'intent.json',intent)
        if i<256:
            r.raw_atomic(directory/'receipt.json',dict(session_id=sid,ledger_id=meta['id'],
                intent_sha256=r.sha(directory/'intent.json'),inclusive_wait4_cpu_s=1.5,
                observer_cpu_lower_bound_s=0.5,user_s=1.0,system_s=0.5))
    os.environ[accounts.ENV]=format(256,'032x')
    try:
        scanner=guard.Scanner(root);counts=[]
        while not scanner.first_pass_done:
            counts.append(scanner.tick({})['entries_examined'])
        first=sum(scanner.values[x] for x in scanner.closed)
        for _ in range(10):counts.append(scanner.tick({})['entries_examined'])
        require(max(counts)<=32 and first==512 and sum(scanner.values[x] for x in scanner.closed)==512,
                'unbounded scan or duplicate accounting')
        # Deterministic exit race: receipt appears after first exists() check
        # and before the observer process lookup reports it gone.
        original_stat=guard.stat
        current=folder/format(256,'032x')
        def exit_race(ident):
            r.raw_atomic(current/'receipt.json',dict(session_id=current.name,ledger_id=meta['id'],
                intent_sha256=r.sha(current/'intent.json'),inclusive_wait4_cpu_s=1.5,
                observer_cpu_lower_bound_s=0.5,user_s=1.0,system_s=0.5))
            return None
        guard.stat=exit_race
        try:
            require(scanner.sample(current.name,{})==(2.0,0),'normal exit misread as missing account')
        finally:
            guard.stat=original_stat
        record('receipt_commit_observer_exit_race_rechecked_without_false_stop')
        scanner.iterator.close()
    finally:
        os.environ.pop(accounts.ENV)
    record('bounded_257_entry_scan_no_repeated_booking',max_entries=max(counts),ticks=len(counts))

    result=dict(complete=True,tests=rows,N1_class_searches=0,production_approved=False)
    r.raw_atomic(out/'TEST_RESULTS.json',result)
    print('PASS',len(rows),flush=True)


if __name__=='__main__':
    main()
