"""Eleven-job C2 calibration; complete eight-cube cover and three controls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import pilot as p
from prepare_partition import prepare, CNF_HASH

SOLVER_HASH = 'd24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad'
ROOT = Path.home() / 'conway99_workspace/c2_reference_v1'
CAKE = Path.home() / 'conway99_workspace/o3_reconciliation_runs/k66_v4_cert_20260908_231256_132359/tools/cake_lpr'


def verdict(records):
    cubes = [r for r in records if r['kind'] == 'cube']
    if any(r['status'] == 'GRAPH_VERIFIED' for r in records):
        return 'C2_GRAPH_FOUND'
    if any(r['kind'] == 'baseline' and r['status'] == 'UNSAT_CERTIFIED' for r in records):
        return 'BASELINE_UNSAT_CERTIFIED'
    if len(cubes) == 8 and all(r['status'] == 'UNSAT_CERTIFIED' for r in cubes):
        return 'ALL_EIGHT_CUBES_CERTIFIED'
    if any(r['status'] in ('SOLVER_ERROR', 'CHECK_FAILED', 'INVALID_SAT_MODEL', 'INPUT_CHANGED') for r in records):
        return 'CALIBRATION_ERROR'
    return 'CALIBRATION_OPEN'


def execute(jobs, out, solver, cake, seconds):
    records, active = [], []
    start, last = time.monotonic(), 0.0
    reason = None
    try:
        for job in jobs:
            folder = out / job['id']
            folder.mkdir()
            cnf = folder / 'input.cnf'
            shutil.copyfile(job['cnf'], cnf)
            assert p.sha(cnf) == job['sha256']
            cmd = p.command(solver, cnf, folder / 'proof.lrat', seconds, job['seed'])
            log = (folder / 'solver.log').open('w')
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            record = {k: v for k, v in job.items() if k != 'cnf'}
            record.update(status='RUNNING', command=cmd, pid=proc.pid, cnf=str(cnf), started_utc=datetime.now(timezone.utc).isoformat())
            records.append(record)
            active.append((proc, log, folder, record, time.monotonic()))
            p.save(out / 'jobs.json', records)
        while active:
            now = time.monotonic()
            reason = p.resource_reason(out)
            if reason:
                break
            for item in active[:]:
                proc, log, folder, record, begun = item
                if proc.poll() is None and now - begun >= seconds + 60:
                    p.stop(proc)
                    record['status'] = 'WATCHDOG_OPEN'
                if proc.poll() is not None:
                    log.close()
                    text = (folder / 'solver.log').read_text(errors='replace')
                    if record['status'] == 'RUNNING':
                        record['status'] = p.classify(proc.returncode, '\n'.join(l for l in text.splitlines() if l.startswith('s ')))
                    record.update(exit=proc.returncode, wall_seconds=round(now-begun, 2))
                    p.save(folder / 'result.json', record)
                    active.remove(item)
            snapshot = {'phase': 'CALIBRATION_SEARCH', 'utc': datetime.now(timezone.utc).isoformat(),
                        'elapsed_seconds': round(now-start), 'ETA_search_seconds': max(0, round(seconds+60-(now-start))),
                        'active': len(active), 'free_disk_GiB': round(shutil.disk_usage(out).free/2**30, 2),
                        'available_RAM_GiB': round(p.memory_gib(), 2), 'jobs': {r['id']: r['status'] for r in records},
                        'proof_GiB': {r['id']: round((out/r['id']/'proof.lrat').stat().st_size/2**30, 3) for r in records if (out/r['id']/'proof.lrat').exists()}}
            p.save(out / 'status.json', snapshot)
            if now-last >= 600 or not active:
                print('STATUS ' + json.dumps(snapshot), flush=True)
                p.save(out / ('snapshot_' + str(round(now-start)) + '.json'), snapshot)
                for r in records:
                    (out/r['id']/'statistics_latest.txt').write_text(p.tail(out/r['id']/'solver.log'))
                last = now
            time.sleep(2)
    finally:
        for proc, log, folder, record, begun in active:
            p.stop(proc)
            log.close()
            record.update(status='STOPPED_OPEN', reason=reason or 'CONTROLLER_INTERRUPTED', exit=proc.returncode)
            p.save(folder / 'result.json', record)
        p.save(out / 'jobs.json', records)
    # All solver processes have finished before any production checker starts.
    for record in records:
        folder, cnf = out/record['id'], Path(record['cnf'])
        if p.sha(cnf) != record['sha256']:
            record['status'] = 'INPUT_CHANGED'
        elif record['status'] == 'UNSAT_PENDING_CHECK':
            p.CNF_HASH = record['sha256']
            checked = p.check_proof(cake, cnf, folder/'proof.lrat', folder, out)
            record.update(status=checked['status'], verification=checked)
        elif record['status'] == 'SAT_PENDING_CHECK':
            c, frame = p.CNF(), p.Frame(14)
            try:
                frame.allocate(c)
                values = p.read_primary_model(folder/'solver.log', len(frame.map))
                graph = p.reconstruct(frame, values)
                valid = p.verify_graph(graph, 14) and all(values[abs(v)] == (v > 0) for v in record['assumptions'])
                record['status'] = 'GRAPH_VERIFIED' if valid else 'INVALID_SAT_MODEL'
                if valid:
                    p.save(folder/'graph.json', graph)
            except (ValueError, KeyError) as error:
                record.update(status='INVALID_SAT_MODEL', error=str(error))
            finally:
                c.close()
        proof = folder/'proof.lrat'
        record['proof_bytes'] = proof.stat().st_size if proof.exists() else 0
        p.save(folder/'result.json', record)
    report = {'status': verdict(records), 'stop_reason': reason, 'jobs': records,
              'wall_seconds': round(time.monotonic()-start, 2), 'baseline_sha256': CNF_HASH,
              'scope': 'Eight exhaustive cubes plus baseline controls; C2 interpretation additionally requires the pinned encoder and fixed-frame completeness argument.'}
    p.save(out/'summary.json', report)
    p.save(out/'status.json', report)
    print('C2_CALIBRATION_RESULT ' + json.dumps(report), flush=True)
    return report


def run(args):
    solver = Path.home()/'.local/bin/cadical'
    assert p.sha(solver) == SOLVER_HASH and p.sha(CAKE) == p.CAKE_HASH
    assert p.sha(Path(__file__).with_name('c2_reference.py')) == p.REF_HASH
    assert subprocess.check_output([str(solver), '--version'], text=True).strip() == '2.2.1'
    assert not p.resource_reason(args.out), 'Insufficient resources'
    # Rebuild from pinned baseline and map; do not trust edited cube manifests.
    manifest = prepare(args.base, args.out/'partition')
    jobs = [{'id': c['id'], 'kind': 'cube', 'seed': 0, 'assumptions': c['assumptions'], 'cnf': str(args.out/'partition'/(c['id']+'.cnf')), 'sha256': c['sha256']} for c in manifest['cases']]
    jobs += [{'id': 'baseline_'+str(i), 'kind': 'baseline', 'seed': i, 'assumptions': [], 'cnf': str(args.out/'partition/baseline.cnf'), 'sha256': CNF_HASH} for i in range(3)]
    p.save(args.out/'inputs.json', {'seconds': args.seconds, 'jobs': jobs, 'solver_sha256': p.sha(solver), 'cake_sha256': p.sha(CAKE), 'controller_sha256': p.sha(__file__)})
    p.controls(solver, CAKE, args.out)
    execute(jobs, args.out, solver, CAKE, args.seconds)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, default=ROOT/'partition_20260914_203703_421425')
    ap.add_argument('--out', type=Path, default=ROOT/('calibration_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')))
    ap.add_argument('--seconds', type=int, default=3600)
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    if args.seconds <= 0:
        ap.error('Positive calibration budget required')
    if not args.run:
        args.out.mkdir(parents=True, exist_ok=False)
        cmd = [sys.executable, str(Path(__file__).resolve()), '--run', '--base', str(args.base.resolve()), '--out', str(args.out.resolve()), '--seconds', str(args.seconds)]
        with (args.out/'driver.log').open('w') as log:
            proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        result = {'status': 'C2_CALIBRATION_LAUNCHED', 'pid': proc.pid, 'output': str(args.out), 'workers': 11, 'seconds_per_job': args.seconds, 'note': 'Launch only; actual toolchain checks and progress are in driver.log/status.json.'}
        p.save(args.out/'launch.json', result)
        print(json.dumps(result), flush=True)
    else:
        def interrupted(signum, frame):
            raise KeyboardInterrupt('Controller signal ' + str(signum))
        signal.signal(signal.SIGTERM, interrupted)
        try:
            run(args)
        except BaseException as error:
            p.save(args.out/'failure.json', {'status': 'CONTROLLER_FAILED', 'error': repr(error)})
            print('CONTROLLER_FAILED ' + repr(error), flush=True)
            raise
