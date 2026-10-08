"""End-to-end Linux CLI with explicitly synthetic Windows protocol transport.
No production test switch is added to runtime or platform_adapter.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import accounting
import platform_adapter as pa
import runtime as r

CFG = dict(original_budget=600, min_available_bytes=128*1024**2,
           min_free_bytes=16*1024**2, max_rss_bytes=1024**3)


def driver(argv):
    action, root = argv[0], Path(argv[1]).resolve()
    def start(self):
        self.clock_record = None
        stop = threading.Event()
        def pulse():
            sequence = 0
            while not stop.is_set():
                value = dict(schema='N1_WINDOWS_CLOCK_1', session_id=self.session, sequence=sequence,
                    pid=123, birth='1', frequency=10**9, ticks=time.monotonic_ns(), utc_ticks=time.time_ns(),
                    high_resolution=True, cpu_lower_bound_s=0.01, available_physical_bytes=2**40,
                    synthetic=False)
                temp = self.folder/'fixture.tmp'
                temp.write_text(json.dumps(value))
                os.replace(temp, self.folder/'heartbeat.json')
                self.clock_record = value
                sequence += 1
                stop.wait(0.03)
        thread = threading.Thread(target=pulse)
        thread.start()
        class FakeTransport:
            returncode = 0
            def wait(inner):
                stop.set()
                thread.join()
                (self.folder/'sampler-final.json').write_text(json.dumps(self.clock_record))
                (self.folder/'receipt.json').write_text(json.dumps(dict(
                    schema='N1_WINDOWS_END_1', session_id=self.session, pid=123, birth='1', exit_code=1 if root.name=='bad_end' else 0,
                    sampler_cpu_end_s=0.02, owner_cpu_lower_bound_s=0.03,
                    owner_tail_complete=False, synthetic=False)))
                return 0
        self.child = FakeTransport()
        while self.clock_record is None:
            time.sleep(0.01)
        self.tick()
        if self.fault:
            raise ValueError(self.fault)
    pa.Observer.start = start
    # This driver is a test program only and always emits an explicit fixture marker.
    print('SYNTHETIC WINDOWS TRANSPORT; NOT WINDOWS ACCEPTANCE', flush=True)
    return accounting.launch(root, action, argv, CFG if action in ('init','run','resume','preflight') else None)


def main():
    if len(sys.argv)>1 and sys.argv[1] == '--driver':
        sys.exit(driver(sys.argv[2:]))
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--worker', type=Path, required=True)
    ap.add_argument('--checker', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=False)
    results = []
    def cmd(root, action, *extra, expected_code=0):
        log = out/(root.name+'-'+action+'.log')
        with log.open('wb') as stream:
            code = subprocess.call([sys.executable, __file__, '--driver', action, str(root), *map(str, extra)],
                stdout=stream, stderr=subprocess.STDOUT)
        assert code == expected_code, log.read_text()
    for name, text, expected in [('sat','p cnf 1 1\n1 0\n','SAT_CNF_VERIFIED'),
        ('unsat','p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','UNSAT_CERTIFIED')]:
        root = out/name
        cnf = out/(name+'.cnf')
        cnf.write_text(text)
        cmd(root, 'init', '--cnf', cnf, '--worker', args.worker.resolve(), '--checker', args.checker.resolve(),
            '--budget', 60, '--platform-wsl', '--total-budget', 600, '--max-rss-bytes', CFG['max_rss_bytes'],
            '--min-free-bytes', CFG['min_free_bytes'], '--min-available-bytes', CFG['min_available_bytes'])
        cmd(root, 'run')
        assert r.read(root/'state.json')['status'] == expected
        cmd(root, 'resume')
        assert len(r.read(root/'state.json')['attempts']) == 1
        report = accounting.audit(root)
        assert report['observed_commands_complete'] and not report['gaps']
        assert len(report['sessions']) == 3
        assert abs(report['host_sampler_end_confirmed_s']-0.06) < 1e-9
        assert abs(report['host_observer_lower_bound_s']-0.09) < 1e-9
        assert abs(report['accounted_lower_bound_s']-report['inclusive_wait4_confirmed_s']-
                   report['observer_cpu_lower_bound_s']-0.15) < 1e-9
        assert all(x['platform']['samples'] >= 1 for x in report['sessions'])
        r.raw_atomic(out/(name+'-ACCOUNTS.json'), report)
        results.append(dict(test=name+'_full_CLI_platform_accounts_and_completed_reuse',passed=True))
    directory = next((accounting.ledger(root)/'sessions').iterdir())
    final_path = directory/'platform'/'final.json'
    original = final_path.read_bytes()
    final_path.write_bytes(original+b' ')
    try:
        accounting.audit(root)
        raise AssertionError('changed host receipt accepted')
    except ValueError:
        pass
    final_path.write_bytes(original)
    results.append(dict(test='host_receipt_bytes_bound_to_outer_receipt',passed=True))
    bad_root = out/"bad_end"
    cmd(bad_root, "init", "--cnf", out/"sat.cnf", "--worker", args.worker.resolve(),
        "--checker", args.checker.resolve(), "--budget", 60, "--platform-wsl",
        "--total-budget", 600, "--max-rss-bytes", CFG["max_rss_bytes"],
        "--min-free-bytes", CFG["min_free_bytes"], "--min-available-bytes",
        CFG["min_available_bytes"], expected_code=78)
    report = accounting.audit(bad_root)
    assert report["gaps"] and not report["observed_commands_complete"]
    assert report["sessions"][0]["platform"]["host"] is None
    results.append(dict(test="missing_host_end_nonzero_exit_and_unknown_not_zero", passed=True))
    r.raw_atomic(out/'TEST_RESULTS.json', dict(complete=True, tests=results, Windows_executed=False,
        fixtures_are_synthetic=True, N1_class_searches=0, production_approved=False))
    print('PASS',len(results))


if __name__ == '__main__':
    main()
