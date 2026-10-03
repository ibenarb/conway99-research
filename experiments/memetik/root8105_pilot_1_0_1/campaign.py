"""Linux/WSL controller: explicit wait4 accounting and conservative admission."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import resource
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil
from core import atomic

BASE = Path(__file__).resolve().parent
STOP = False


def request_stop(signum, frame):
    global STOP
    STOP = True


def cpu_and_memory(pid):
    try:
        parent = psutil.Process(pid)
        family = [parent] + parent.children(recursive=True)
        cpu, rss = 0.0, 0
        for proc in family:
            try:
                times = proc.cpu_times()
                cpu += times.user + times.system
                rss += proc.memory_info().rss
            except psutil.NoSuchProcess:
                continue
        return cpu, rss
    except psutil.NoSuchProcess:
        return 0.0, 0


def run_size(directory):
    total = 0
    for root, dirs, files in os.walk(directory):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except FileNotFoundError:
                continue
    return total


def code_fingerprint():
    hashes = {}
    files = list(BASE.glob('*.py')) + [BASE / 'config.json', BASE / 'roots.tsv', BASE / 'requirements.txt']
    files += list((BASE / 'vendor').glob('*')) + list((BASE / 'fixtures').glob('*'))
    for path in sorted(files):
        if path.is_file():
            hashes[str(path.relative_to(BASE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()


def run(directory, allow_test=False):
    global STOP
    directory = Path(directory).resolve()
    manifest = json.loads((directory / 'manifest.json').read_text())
    cfg = manifest['config']
    if (directory / 'solution.json').exists():
        from completion import verify_complete
        from core import Geometry, unpack
        solution = json.loads((directory / 'solution.json').read_text())
        verify_complete(Geometry(solution['m']), unpack(solution['rows']))
        print('VERIFIED_SRG_ALREADY_FOUND', flush=True)
        return {'status': 'VERIFIED_SRG_ALREADY_FOUND'}
    if not allow_test:
        gate = json.loads((directory / 'preflight.json').read_text())
        if gate['status'] != 'PASS' or gate['code_fingerprint'] != code_fingerprint():
            raise ValueError('fresh target-machine preflight required')
        if gate['manifest_sha256'] != hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest():
            raise ValueError('manifest changed since preflight')
        for name, expected in manifest['job_sha256'].items():
            if hashlib.sha256((directory / 'jobs' / (name + '.json')).read_bytes()).hexdigest() != expected:
                raise ValueError('job changed since preparation')
    lock = (directory / 'controller.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    session = directory / 'session_open.json'
    if session.exists():
        raise RuntimeError('Unclosed previous session: CPU accounting requires recovery audit; no marker removed.')
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    receipts_path = directory / 'receipts.json'
    receipts = json.loads(receipts_path.read_text()) if receipts_path.exists() else []
    # A receipt is authoritative for resources. A worker marker alone is not.
    attempts = len(receipts)
    used_by_job = {}
    finished = set()
    for r in receipts:
        used_by_job[r['job']] = used_by_job.get(r['job'], 0) + r['cpu_s']
        if r['terminal']:
            finished.add(r['job'])
    tasks = []
    for name in manifest['jobs']:
        if name in finished or used_by_job.get(name, 0) >= cfg['job_cpu_s']:
            continue
        tasks.append((name, 'search', cfg['job_cpu_s'] - used_by_job.get(name, 0), None))
    pending = list(tasks)
    active = {}
    proof_phase = False
    peak_active = 0
    t0, mono0, raw0 = time.time(), time.monotonic(), time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    controller_cpu0 = 0.0  # Include interpreter/import/controller setup CPU.
    initial_aux = json.loads((directory / 'aux_ledger.json').read_text()) if (directory / 'aux_ledger.json').exists() else {'cpu_s': 0}
    aux_previous = initial_aux['cpu_s']
    stopping = False
    reason = None
    solution_found = False
    last_report, last_size = 0, 0
    bytes_used = 0
    atomic(session, {'pid': os.getpid(), 'boot_id': boot, 'started_unix': t0,
                     'code_fingerprint': code_fingerprint()})
    try:
        while pending or active or not proof_phase:
            now = time.monotonic()
            for pid, info in list(active.items()):
                ended, status, usage = os.wait4(pid, os.WNOHANG)
                if not ended:
                    continue
                info['process'].returncode = os.waitstatus_to_exitcode(status)
                info['log'].close()
                cpu = usage.ru_utime + usage.ru_stime
                result_path = info['out'] / 'worker_result.json'
                if info['kind'] == 'proof':
                    result_path = Path(info['artifact']) / 'certificate.json'
                result = json.loads(result_path.read_text()) if result_path.exists() else {}
                outcome = result.get('status', 'WORKER_FAILED_UNKNOWN')
                if outcome == 'SRG_FOUND_VERIFIED' and info['process'].returncode == 0:
                    from completion import verify_complete
                    from core import Geometry, unpack
                    solution = json.loads((info['out'] / 'solution.json').read_text())
                    checked = verify_complete(Geometry(solution['m']), unpack(solution['rows']))
                    atomic(directory / 'solution.json', {**solution, **checked, 'job': info['name']})
                    solution_found = True
                if info['process'].returncode != 0:
                    outcome = 'WORKER_FAILED_UNKNOWN'
                if result.get('status') == 'INTEGRITY_OR_WORKER_ERROR':
                    STOP = True
                # Exit errors are local and visible. Clean pause is resumable.
                terminal = outcome != 'PAUSED' and not (info.get('term_at') and reason == 'USER_PAUSE')
                receipt = {'job': info['name'], 'kind': info['kind'], 'attempt': info['attempt'],
                           'pid': pid, 'exit': info['process'].returncode, 'status': outcome,
                           'cpu_s': cpu, 'user_cpu_s': usage.ru_utime, 'system_cpu_s': usage.ru_stime,
                           'max_rss_kib': usage.ru_maxrss, 'allocated_cpu_s': info['allocation'],
                           'soft_target_exceeded': cpu > info['allocation'] + 0.25,
                           'terminal': terminal, 'ended_unix': time.time(),
                           'max_depth': result.get('state', {}).get('max_depth'),
                           'artifact': info['artifact']}
                receipts.append(receipt)
                atomic(receipts_path, receipts)
                del active[pid]
            live_cpu, live_rss = 0.0, 0
            for pid, info in active.items():
                cpu, rss = cpu_and_memory(pid)
                live_cpu += cpu
                live_rss += rss
                info['live_cpu'] = cpu
                if (cpu >= info['allocation'] + 25 or now - info['started'] > info['allocation'] * 6 + 300):
                    if not info.get('term_at'):
                        os.killpg(pid, signal.SIGTERM)
                        info['term_at'] = now
                    elif now - info['term_at'] > 10:
                        os.killpg(pid, signal.SIGKILL)
            used_cpu = sum(r['cpu_s'] for r in receipts) + live_cpu + aux_previous + time.process_time() - controller_cpu0
            available = psutil.virtual_memory().available
            if now - last_size >= 30:
                bytes_used = run_size(directory)
                last_size = now
            free = shutil.disk_usage(directory).free
            emergency = (available < cfg['emergency_available_gib'] * 2**30 or
                         free < cfg['free_disk_reserve_gib'] * 2**30 or
                         bytes_used > cfg['max_run_disk_gib'] * 2**30 or
                         used_cpu >= cfg['campaign_cpu_s'])
            if STOP or emergency or solution_found:
                stopping = True
                reason = 'VERIFIED_SRG_FOUND' if solution_found else ('USER_PAUSE' if STOP else 'GLOBAL_RESOURCE_STOP')
                pending = []
                proof_phase = True
                for pid, info in active.items():
                    if not info.get('term_at'):
                        os.killpg(pid, signal.SIGTERM)
                        info['term_at'] = now
                    elif now - info['term_at'] > 15:
                        os.killpg(pid, signal.SIGKILL)
            if not pending and not active and not proof_phase:
                proof_phase = True
                for name in manifest['jobs']:
                    checkpoint = directory / 'work' / name / 'checkpoint.json'
                    if not checkpoint.exists():
                        continue
                    state = json.loads(checkpoint.read_text())
                    for i, artifact in enumerate(state.get('proof_candidates', [])):
                        proof_name = name + f'_proof{i}'
                        remaining_proof = cfg['proof_cpu_s'] - used_by_job.get(proof_name, 0)
                        if proof_name not in finished and remaining_proof > 0:
                            pending.append((proof_name, 'proof', remaining_proof, artifact))
            # Admit only against currently AVAILABLE RAM; existing C2 memory is
            # already subtracted by the OS. One 1.5-GiB reservation per new worker.
            unfilled_reservations = max(0, len(active) * cfg['worker_memory_gib'] * 2**30 - live_rss)
            slots_by_ram = max(0, int((available - unfilled_reservations - cfg['available_memory_reserve_gib'] * 2**30)
                                     / (cfg['worker_memory_gib'] * 2**30)))
            slots = min(cfg['workers'] - len(active), slots_by_ram)
            while pending and slots > 0 and not stopping:
                name, kind, allocation, artifact = pending.pop(0)
                outstanding = sum(max(0, i['allocation'] + 30 - i.get('live_cpu', 0)) for i in active.values())
                if used_cpu + outstanding + allocation + 30 > cfg['campaign_cpu_s']:
                    stopping, reason = True, 'GLOBAL_CPU_RESERVATION_STOP'
                    pending = []
                    proof_phase = True
                    break
                out = directory / 'work' / name
                out.mkdir(parents=True, exist_ok=True)
                attempts += 1
                if kind == 'search':
                    command = [sys.executable, str(BASE / 'worker.py'), str(directory / 'jobs' / (name + '.json')),
                               str(out), '--cpu', str(allocation), '--memory', str(cfg['worker_memory_gib'])]
                    (out / 'worker_result.json').unlink(missing_ok=True)
                else:
                    command = [sys.executable, str(BASE / 'proof.py'), artifact, str(BASE / 'bin' / 'drat-trim'),
                               '--cpu', str(max(1, allocation - 20))]
                log = (out / f'attempt_{attempts:05d}.log').open('w')
                def child_limits():
                    resource.setrlimit(resource.RLIMIT_AS, (int(cfg['worker_memory_gib'] * 2**30),) * 2)
                    resource.setrlimit(resource.RLIMIT_CPU, (int(allocation + 30), int(allocation + 31)))
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                        start_new_session=True, preexec_fn=child_limits)
                active[proc.pid] = {'process': proc, 'log': log, 'name': name, 'kind': kind, 'out': out,
                                    'artifact': artifact, 'attempt': attempts, 'allocation': allocation,
                                    'started': now, 'live_cpu': 0}
                slots -= 1
            peak_active = max(peak_active, len(active))
            status = {'peak_active_workers': peak_active, 'status': reason or ('RUNNING' if active or pending else 'PILOT_COMPLETE'),
                      'snapshot_unix': time.time(), 'boot_id': boot,
                      'active_workers': len(active), 'pending_in_phase': len(pending),
                      'phase': 'proof' if proof_phase else 'search', 'receipts': len(receipts),
                      'used_cpu_s_including_live': used_cpu, 'live_rss_bytes': live_rss,
                      'available_memory_bytes': available, 'run_disk_bytes': bytes_used,
                      'guest_unix_elapsed_s': time.time() - t0,
                      'guest_monotonic_elapsed_s': now - mono0,
                      'guest_raw_elapsed_s': time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - raw0,
                      'host_clock_validated': False,
                      'budget_projection_at_full_slots_s': (
                          sum(t[2] for t in pending) + sum(max(0, i['allocation'] - i['live_cpu']) for i in active.values()))
                          / max(1, cfg['workers']),
                      'projection_is_not_eta': True,
                      'active': [{'pid': p, 'job': i['name'], 'cpu_s': i['live_cpu']} for p, i in active.items()]}
            atomic(directory / 'status.json', status)
            if now - last_report >= cfg['report_s'] or (not active and not pending):
                print(json.dumps(status), flush=True)
                last_report = now
            if active or pending:
                time.sleep(1)
        atomic(directory / 'aux_ledger.json', {'cpu_s': aux_previous + time.process_time() - controller_cpu0})
        session.unlink()
    except BaseException:
        # Keep the session marker unless every child has a wait4 end receipt.
        for pid in active:
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        raise
    finally:
        lock.close()
    return status


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    ap.add_argument('--test', action='store_true')
    args = ap.parse_args()
    run(args.directory, args.test)
