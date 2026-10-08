"""Isolated protocol/resource faults plus real Linux native children.
All Windows-shaped records in this suite are synthetic fixtures, not host evidence.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import platform_adapter as p
import preflight
import runtime as r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--worker', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    tests = []
    def record(name):
        tests.append(dict(test=name, passed=True))
        print(name, 'PASS', flush=True)
    def rejected(fn):
        try:
            fn()
        except (ValueError, OSError, KeyError):
            return
        raise AssertionError('invalid record accepted')
    base = dict(schema='N1_WINDOWS_CLOCK_1', session_id='fixture', sequence=0,
                pid=100, birth='123', frequency=10000000, ticks=1000, utc_ticks=10000,
                high_resolution=True, cpu_lower_bound_s=0.01, available_physical_bytes=2**30,
                synthetic=False)
    clock = p.Clock('fixture')
    clock.accept(base, now=1)
    clock.accept(dict(base, sequence=1, ticks=1100, cpu_lower_bound_s=0.02), now=2)
    record('monotonic_host_sequence_and_cpu')
    for name, changes in (
        ('foreign_session', dict(session_id='other')),
        ('reused_pid_identity', dict(birth='124')),
        ('regressed_sequence', dict(sequence=0)),
        ('regressed_ticks', dict(ticks=999)),
        ('regressed_cpu', dict(cpu_lower_bound_s=0.0)),
        ('nonfinite_cpu', dict(cpu_lower_bound_s=float('nan'))),
        ('invalid_frequency', dict(frequency=0)),
        ('non_monotonic_clock_source', dict(high_resolution=False)),
    ):
        rejected(lambda changes=changes: clock.accept(dict(clock.previous, **changes), now=3))
        record(name)
    rejected(lambda: clock.accept(dict(clock.previous, utc_ticks=20000), now=3))
    record('changed_duplicate_sequence_rejected')
    rejected(lambda: clock.accept(clock.previous, now=40))
    record('stale_heartbeat_is_liveness_fault_not_budget_timeout')
    end = dict(schema='N1_WINDOWS_END_1', session_id='fixture', pid=100, birth='123',
               exit_code=0, sampler_cpu_end_s=0.03, owner_cpu_lower_bound_s=0.02,
               owner_tail_complete=False, synthetic=False)
    clock.end(end)
    rejected(lambda: clock.end(dict(end, sampler_cpu_end_s=0.001)))
    rejected(lambda: clock.end(dict(end, exit_code=1)))
    rejected(lambda: clock.end(dict(end, owner_tail_complete=True)))
    record('host_end_account_identity_lower_bound_and_failure_checked')
    cfg = dict(min_available_bytes=100, min_free_bytes=100, max_rss_bytes=2**30)
    def snap(maximum=1000, current=200, events='oom 0\noom_kill 0'):
        return dict(membership='/team', mount='/cg', directory='/cg/team', visible_ancestors=[
            {'path':'/cg/team', 'memory.max':maximum, 'memory.current':current,
             'memory.events':events}])
    cg = p.Cgroup()
    cg.sample(snap(), cfg)
    rejected(lambda: cg.sample(snap(current=950), cfg))
    record('continuous_cgroup_headroom_drop')
    cg = p.Cgroup()
    cg.sample(snap(), cfg)
    rejected(lambda: cg.sample(snap(events='oom 1\noom_kill 0'), cfg))
    record('new_OOM_event_latched')
    cg = p.Cgroup()
    cg.sample(snap(events='oom 2\noom_kill 1'), cfg)
    rejected(lambda: cg.sample(snap(), cfg))
    record('event_counter_reset_rejected')
    rejected(lambda: p.Cgroup().sample(snap(current=None), cfg))
    rejected(lambda: p.Cgroup().sample(snap(events=None), cfg))
    record('missing_cgroup_counters_not_zero')
    cg = p.Cgroup()
    cg.sample(snap(), cfg)
    changed = snap()
    changed['membership'] = '/other'
    rejected(lambda: cg.sample(changed, cfg))
    record('changed_cgroup_membership_rejected')
    unlimited = p.Cgroup().sample(snap(maximum='max'), cfg)
    assert unlimited['observed_finite_headroom_bytes'] is None
    record('unlimited_cgroup_explicit_not_fake_finite_capacity')
    # Live real Linux child stop. No fault gates are installed in production code.
    root = out/'run'
    directory = root/'attempts'/'native'
    directory.mkdir(parents=True)
    session = out/'sessions'/'fixture'
    session.mkdir(parents=True)
    observer = p.Observer(root, session, cfg)
    (observer.folder/'heartbeat.json').write_text(json.dumps(base))
    cnf = out/'pigeonhole.cnf'
    holes = 21
    var = lambda i,j: i*holes+j+1
    clauses = [[var(i,j) for j in range(holes)] for i in range(22)]
    clauses += [[-var(i,j),-var(k,j)] for j in range(holes) for i in range(22) for k in range(i)]
    cnf.write_text('p cnf 462 '+str(len(clauses))+'\n'+''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
    log = (out/'worker.log').open('wb')
    worker = subprocess.Popen([str(args.worker.resolve()), str(cnf)], cwd=directory, stdout=log, stderr=log)
    ident = r.identity(worker.pid)
    r.raw_atomic(observer.folder/'native.json', dict(identity=ident, directory=str(directory), phase='search'))
    unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(3)'])
    with patch.object(preflight, 'cgroup_probe', return_value=snap(current=950)):
        observer.tick()
    assert observer.fault is not None and (directory/'STOP').exists()
    assert unrelated.poll() is None
    pid, status, usage = os.wait4(worker.pid, 0)
    worker.returncode = os.waitstatus_to_exitcode(status)
    assert worker.returncode == 0
    assert json.loads((directory/'worker.json').read_text())['stop_seen']
    assert usage.ru_utime+usage.ru_stime >= 0
    log.close()
    unrelated.wait()
    observer.log.close()
    record('resource_fault_cooperatively_stops_real_solver_only_and_wait4_retained')
    # The checker signal goes through a process handle, not an unverified PID.
    checker = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    r.raw_atomic(observer.folder/'native.json', dict(identity=r.identity(checker.pid), directory=str(directory), phase='check'))
    p.stop_native(observer.folder, root)
    assert checker.wait() == -15
    record('checker_stop_uses_pidfd')
    # A mismatched birth cannot signal a live child.
    innocent = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(1)'])
    bad_ident = dict(r.identity(innocent.pid), birth='0')
    r.raw_atomic(observer.folder/'native.json', dict(identity=bad_ident, directory=str(directory), phase='check'))
    p.stop_native(observer.folder, root)
    assert innocent.wait() == 0
    record('foreign_birth_cannot_signal_process')
    # The observer remains active while the inner process does CPU-only validation.
    session2 = out/'sessions'/'heavy'
    session2.mkdir()
    monitor = p.Observer(root, session2, cfg)
    heavy = subprocess.Popen([sys.executable, '-c', 'import time; end=time.process_time()+0.4\nwhile time.process_time()<end: pass'])
    monitor.inner = r.identity(heavy.pid)
    seq = 0
    while heavy.poll() is None:
        (monitor.folder/'heartbeat.json').write_text(json.dumps(dict(base,session_id='heavy',sequence=seq,ticks=1000+seq)))
        with patch.object(preflight, 'cgroup_probe', return_value=snap()):
            monitor.tick()
        assert monitor.fault is None
        seq += 1
        time.sleep(0.03)
    assert seq > 2 and r.read(monitor.folder/'health.json')['samples'] == seq
    monitor.log.close()
    record('monitor_samples_during_non_solver_CPU_work')
    result = dict(complete=True, tests=tests, Windows_executed=False,
                  fixtures_are_synthetic=True, real_Linux_children=True,
                  production_approved=False, N1_class_searches=0)
    r.raw_atomic(out/'TEST_RESULTS.json', result)
    print('PASS', len(tests))


if __name__ == '__main__':
    main()
