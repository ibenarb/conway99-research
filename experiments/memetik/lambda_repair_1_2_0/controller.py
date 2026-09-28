"""Owned children, wait4 receipts, immutable tasks, Windows-clock deadlines."""
import math
import os
import shutil
import signal
import subprocess
import sys
import time
from common import *
from verify import checked, key, record, window_check

PAUSE = False


def request_pause(*args):
    global PAUSE
    PAUSE = True


def child_limits(allowance):
    import ctypes
    # A lost parent cannot silently leave productive workers running.
    parent = os.getppid()
    ctypes.CDLL(None).prctl(1, signal.SIGTERM)
    if os.getppid() != parent:
        os._exit(125)
    maximum = max(1, math.floor(allowance - 2))
    resource.setrlimit(resource.RLIMIT_CPU, (maximum, maximum))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


class Controller:
    def __init__(self, run, host=None, test=False):
        from hostclock import HostClock
        self.run = Path(run)
        self.state = read(self.run / 'ledger.json')
        if self.state['active'] or (self.run / 'session_active.json').exists():
            raise RuntimeError('Unresolved session; preserve records and diagnose before resume')
        self.test = test
        if not test and int(Path('/proc/self/stat').read_text().split()[0]) != os.getpid():
            raise RuntimeError('PID/procfs mismatch; cannot safely monitor workers')
        self.host = host or HostClock(self.run)
        self.start = self.host.sample()
        self.phase = 'CLOCK'
        self.active = {}
        self.reason = None
        self.last_status = -1000.0
        self.last_save = 0.0
        self.max_workers = min(12, len(os.sched_getaffinity(0)))
        self.per_worker = 2 * GIB
        self.manifest = read(HERE / 'MANIFEST.json')
        self.tasks = {t['id']: t for t in self.manifest['tasks']}
        self.policy = read(HERE / 'BUDGET_POLICY.json')
        self.repair_started_host = None
        self.repair_cpu_baseline = sum(self.state['used'][k] for k in self.tasks)
        self.founders = {g['id']: g for g in self.manifest['founders']}
        self.host_baseline = self.state['host_wall_seconds']
        self.aux_baseline = self.state['used']['aux']
        signal.signal(signal.SIGTERM, request_pause)
        signal.signal(signal.SIGINT, request_pause)
        atomic(self.run / 'session_active.json', process(os.getpid()))

    def save(self):
        atomic(self.run / 'ledger.json', self.state)

    def remaining(self, category):
        ceiling = self.policy['aux_cpu_limit_seconds'] if category == 'aux' else self.tasks[category]['cpu_limit_seconds'] + self.policy['task_shutdown_grace_cpu_seconds']
        used = self.state['used'][category]
        if category == 'aux':
            used += cpu() + self.host.last['windows_cpu_seconds']
        return ceiling - used - sum(e['allocation'] for e in self.active.values() if e['category'] == category)

    def remaining_total(self):
        return (self.policy['total_cpu_limit_seconds'] - sum(self.state['used'].values())
                - cpu() - self.host.last['windows_cpu_seconds']
                - sum(e['allocation'] for e in self.active.values()) - 120)

    def monitor(self):
        h = self.host.sample()
        elapsed = h['host_seconds'] - self.start['host_seconds']
        live = {pid: process(pid) for pid in self.active}
        memory = {line.split(':')[0]: int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()}
        self.free_ram = memory['MemAvailable']
        group_ram = sum(v['rss'] for v in live.values()) + process(os.getpid())['rss']
        if not self.test:
            if group_ram > 24 * GIB:
                self.reason = 'GROUP_RAM_LIMIT'
            if self.free_ram < 2 * GIB:
                self.reason = 'CRITICAL_FREE_RAM'
            if shutil.disk_usage(self.run).free < 25 * GIB or h['physical_free_bytes'] < 25 * GIB:
                self.reason = 'DISK_RESERVE'
        if self.host_baseline + elapsed >= self.policy['active_host_wall_limit_seconds']:
            self.reason = 'HOST_WALL_LIMIT'
        if self.remaining_total() < 0:
            self.reason = 'TOTAL_CPU_LIMIT'
        if self.remaining('aux') < 60:
            self.reason = 'AUX_CPU_LIMIT'
        if PAUSE:
            self.reason = 'USER_PAUSE'
        for pid, entry in self.active.items():
            if live[pid]['cpu'] >= entry['soft_target']:
                self.signal_worker(pid, 'CPU_TARGET')
        if self.reason:
            for pid in list(self.active):
                self.signal_worker(pid, self.reason)
        # Escalation uses Windows monotonic seconds, never WSL elapsed time.
        for pid, entry in self.active.items():
            if entry.get('stop_host') is not None and h['host_seconds'] - entry['stop_host'] >= self.policy['shutdown_host_seconds']:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        if elapsed - self.last_save >= 30:
            # Session marker prevents reuse of this provisional wall counter after a crash.
            self.state['host_wall_seconds'] = self.host_baseline + elapsed
            self.save()
            self.last_save = elapsed
        if elapsed - self.last_status >= 600:
            self.status(h, elapsed, live, group_ram)
            self.last_status = elapsed
        return h

    def status(self, host=None, elapsed=None, live=None, group_ram=None, final=None):
        host = host or self.host.last
        elapsed = elapsed if elapsed is not None else host['host_seconds'] - self.start['host_seconds']
        live = live if live is not None else {pid: process(pid) for pid in self.active}
        pending = [t for t in self.tasks if not self.state['done'].get(t)]
        live_by_task = {e['category']: live[p]['cpu'] for p, e in self.active.items() if e['category'] != 'aux'}
        remaining_by_task = [max(0, self.tasks[t]['cpu_limit_seconds'] - self.state['used'][t] - live_by_task.get(t, 0)) for t in pending]
        remaining = sum(remaining_by_task)
        charged = dict(self.state['used'])
        if final is None:
            charged['aux'] += cpu() + host['windows_cpu_seconds']
        actual_task_cpu = sum(charged[k] for k in self.tasks) + sum(v['cpu'] for p, v in live.items() if self.active[p]['category'] != 'aux')
        repair_seconds = None if self.repair_started_host is None else host['host_seconds'] - self.repair_started_host
        throughput = (actual_task_cpu - self.repair_cpu_baseline) / repair_seconds if repair_seconds and repair_seconds >= 120 else None
        slots = min(self.max_workers, len(pending))
        per_slot_rate = min(1.0, throughput / max(1, self.max_workers)) if throughput and throughput > 0 else None
        eta = max(remaining / max(1, slots), max(remaining_by_task, default=0)) / per_slot_rate if per_slot_rate else None
        value = {'status': final or 'RUNNING', 'phase': self.phase, 'jobs_complete': len(self.tasks) - len(pending),
                 'jobs_total': len(self.tasks), 'active_workers': len(self.active), 'worker_limit': self.max_workers,
                 'charged_cpu_seconds': charged, 'active_cpu_seconds': sum(v['cpu'] for v in live.values()),
                 'host_wall_seconds': self.host_baseline + elapsed, 'utc': host['utc'], 'reason': self.reason,
                 'rss_bytes': group_ram, 'eta_seconds': None if final else eta,
                 'budget_projection_seconds': None if final else max(remaining / max(1, slots), max(remaining_by_task, default=0)),
                 'measured_task_cpu_per_host_second': throughput,
                 'local_error_count': sum(v == 'LOCAL_WORKER_ERROR' for v in self.state['done'].values()),
                 'cpu_target_warning_count': len(self.state.get('cpu_target_warnings', [])),
                 'eta_scope': 'Remaining CPU ceilings minus live CPU; capped measured per-slot rate and longest-task tail; budget projection, not predicted early completion',
                 'active': [{'job': e['category'], 'cpu_seconds': live[p]['cpu']} for p, e in self.active.items()]}
        atomic(self.run / 'status.json', value)
        print('REPAIR_STATUS ' + json.dumps(value), flush=True)

    def signal_worker(self, pid, reason):
        e = self.active[pid]
        if e.get('stop_host') is None:
            e['stop_host'] = self.host.last['host_seconds']
            e['stop_reason'] = reason
            e['stop_cpu_observed'] = process(pid)['cpu']
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    def launch(self, category, command, directory, allowance, soft_target=None, probe=False):
        if allowance < 3 or self.remaining(category) < allowance - 0.001 or self.remaining_total() < allowance:
            raise RuntimeError('Invalid CPU reservation')
        serial = self.state['next_attempt']
        self.state['next_attempt'] += 1
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        token = str(serial)
        self.state['active'][token] = {'category': category, 'allocation': allowance, 'pid': None}
        self.save()
        log = (directory / f'attempt_{serial:04d}.log').open('ab')
        try:
            proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, **THREAD_ENV, 'PYTHONNOUSERSITE': '1'},
                                    preexec_fn=lambda: child_limits(allowance), start_new_session=True)
        except BaseException:
            log.close()
            del self.state['active'][token]
            self.save()
            raise
        entry = {'category': category, 'allocation': allowance, 'directory': str(directory), 'token': token,
                 'proc': proc, 'log': log, 'stop_host': None,
                 'soft_target': allowance - 5 if soft_target is None else soft_target, 'probe': probe}
        self.active[proc.pid] = entry
        self.state['active'][token]['pid'] = proc.pid
        self.state['active'][token]['start_ticks'] = process(proc.pid)['start_ticks']
        self.save()

    def collect(self):
        for pid, e in list(self.active.items()):
            found, status, usage = os.wait4(pid, os.WNOHANG)
            if not found:
                continue
            e['proc'].returncode = os.waitstatus_to_exitcode(status)
            e['log'].close()
            spent = usage.ru_utime + usage.ru_stime
            directory = Path(e['directory'])
            result_path = directory / 'result.json'
            result = None
            integrity_error = None
            try:
                result = read(result_path) if result_path.exists() else None
                if e['category'] != 'aux':
                    best = read(directory / 'best.json')
                    task = self.tasks[e['category']]
                    founder = self.founders[task['founder']]
                    assert window_check(best['graph6'], founder['graph6'], task['vertices']) == best['scores']
                    assert key(best['scores']) <= key(founder['scores'])
                    if best['scores']['W'] == 0:
                        self.reason = 'VERIFIED_W_ZERO'
            except Exception as error:
                integrity_error = repr(error)
                self.reason = 'RESULT_INTEGRITY_ERROR'
            # Always settle the reaped process before reacting to bad output.
            # Invalid evidence is retained; it cannot turn into a successful audit.
            receipt = {'category': e['category'], 'allocation': e['allocation'], 'pid': pid,
                       'cpu_seconds': spent, 'wait_status': status, 'exit_code': e['proc'].returncode,
                       'max_rss_bytes': usage.ru_maxrss * 1024, 'stop_reason': e.get('stop_reason'),
                       'soft_target_cpu_seconds': e['soft_target'],
                       'stop_request_cpu_observed': e.get('stop_cpu_observed'),
                       'stop_request_host_seconds': e.get('stop_host'),
                       'collected_host_seconds': self.host.last['host_seconds'],
                       'worker_final_cpu_seconds': result.get('process_cpu_seconds') if result else None,
                       'worker_final_proc_cpu_seconds': result.get('proc_cpu_seconds') if result else None,
                       'python_process_time_seconds': result.get('python_process_time_seconds') if result else None,
                       'active_peers_at_collection': len(self.active) - 1,
                       'preflight_probe': e['probe'],
                       'integrity_error': integrity_error,
                       'result_sha256': digest(result_path) if result_path.exists() else None,
                       'best_sha256': digest(directory / 'best.json') if (directory / 'best.json').exists() else None}
            snapshots = self.run / 'receipts'
            snapshots.mkdir(exist_ok=True)
            if result_path.exists():
                shutil.copyfile(result_path, snapshots / (e['token'] + '.result.json'))
            if (directory / 'best.json').exists():
                shutil.copyfile(directory / 'best.json', snapshots / (e['token'] + '.best.json'))
            atomic(snapshots / (e['token'] + '.json'), receipt)
            self.state['used'][e['category']] += spent
            self.state['receipts'].append(e['token'])
            del self.state['active'][e['token']]
            del self.active[pid]
            self.state['peak_worker_rss'] = max(self.state.get('peak_worker_rss', 0), usage.ru_maxrss * 1024)
            if spent > e['soft_target'] + 0.25:
                self.state.setdefault('cpu_target_warnings', []).append({'receipt': e['token'], 'category': e['category'], 'measured_cpu_seconds': spent, 'soft_target_cpu_seconds': e['soft_target']})
            if spent > e['allocation'] + self.policy['receipt_measurement_tolerance_seconds']:
                self.state.setdefault('local_hard_overruns', []).append(e['token'])
            if e['category'] != 'aux':
                name = e['category']
                if result and result['status'] == 'OPTIMAL_UNCERTIFIED':
                    self.state['done'][name] = 'OPTIMAL_UNCERTIFIED'
                elif self.tasks[name]['cpu_limit_seconds'] - self.state['used'][name] < self.policy['minimum_search_attempt_seconds']:
                    self.state['done'][name] = 'CPU_LIMIT_UNKNOWN'
                elif e['proc'].returncode != 0 and not e.get('stop_reason'):
                    self.state['done'][name] = 'LOCAL_WORKER_ERROR'
                if spent > e['allocation'] + self.policy['receipt_measurement_tolerance_seconds']:
                    self.state['done'][name] = 'LOCAL_HARD_LIMIT_UNKNOWN'
            elif e['proc'].returncode != 0 and not e.get('stop_reason'):
                self.reason = 'CONTROLS_FAILED'
            self.save()

    def await_children(self):
        while self.active:
            self.monitor()
            self.collect()
            if self.active:
                time.sleep(0.25)

    def task(self, name, allowance=None):
        task = self.tasks[name]
        directory = self.run / 'jobs' / name
        directory.mkdir(parents=True, exist_ok=True)
        atomic(directory / 'task.json', task)
        if (directory / 'result.json').exists():
            os.replace(directory / 'result.json', directory / f'result_before_{self.state["next_attempt"]}.json')
        if (directory / 'error.json').exists():
            raise RuntimeError('Prior worker error requires diagnosis')
        if not (directory / 'best.json').exists():
            atomic(directory / 'best.json', record(self.founders[task['founder']]['graph6']))
        soft = min(self.tasks[name]['cpu_limit_seconds'] - self.state['used'][name], allowance if allowance is not None else self.tasks[name]['cpu_limit_seconds'])
        if soft < self.policy['minimum_search_attempt_seconds']:
            self.state['done'][name] = 'CPU_LIMIT_UNKNOWN'
            self.save()
            return
        allocation = min(soft + self.policy['attempt_shutdown_grace_cpu_seconds'], self.remaining(name) - 1)
        if self.remaining_total() < allocation:
            self.reason = 'TOTAL_CPU_LIMIT'
            return
        self.launch(name, [sys.executable, str(HERE / 'worker.py'), str(directory / 'task.json'), str(directory), str(allocation), '--stop-cpu', str(soft)], directory, allocation, soft_target=soft)

    def scheduler_preflight(self):
        self.phase = 'SCHEDULER_PREFLIGHT'
        start_receipts = len(self.state['receipts'])
        before = self.host.sample()
        for i in range(12):
            delayed = i < 2
            target = 2 if delayed else 8
            directory = self.run / 'scheduler_preflight' / str(i)
            self.launch('aux', [sys.executable, str(HERE / 'shutdown_probe.py'),
                               str(directory), str(target), str(3 if delayed else 0)],
                        directory, target + 10, soft_target=target, probe=True)
        self.await_children()
        if self.reason:
            return
        reports = []
        for token in self.state['receipts'][start_receipts:]:
            receipt = read(self.run / 'receipts' / (token + '.json'))
            result = read(self.run / 'receipts' / (token + '.result.json'))
            assert result['status'] == 'PASS' and receipt['exit_code'] == 0
            assert receipt['cpu_seconds'] <= receipt['allocation'] + self.policy['receipt_measurement_tolerance_seconds']
            assert abs(result['process_cpu_seconds'] - result['proc_cpu_seconds']) < 0.25
            assert abs(result['process_cpu_seconds'] - result['python_process_time_seconds']) < 0.25
            assert receipt['cpu_seconds'] >= result['process_cpu_seconds'] - 0.05
            reports.append({'receipt': token, **receipt, 'worker': result})
        delayed = [r for r in reports if r['worker']['delayed']]
        assert len(reports) == 12 and len(delayed) == 2
        assert all(r['cpu_seconds'] > r['soft_target_cpu_seconds'] + 2 for r in delayed)
        assert any(r['active_peers_at_collection'] > 0 for r in delayed)
        after = self.host.sample()
        value = {'status': 'PASS', 'clock': 'FAKEHOST_CLOUD_TEST' if self.test else 'WINDOWS_STOPWATCH',
                 'host_seconds': after['host_seconds'] - before['host_seconds'],
                 'cpu_seconds': sum(r['cpu_seconds'] for r in reports),
                 'parallel_workers': 12, 'delayed_workers': 2,
                 'other_workers_continued': True, 'receipts': reports,
                 'guest_before': before.get('guest_after'), 'guest_after': after.get('guest_after'),
                 'scope': 'Real child CPU and delayed shutdown through the campaign scheduler; no proof of long-term clock stability'}
        atomic(self.run / 'SCHEDULER_PREFLIGHT.json', value)
        print('SCHEDULER_PREFLIGHT_PASS ' + json.dumps({k: v for k, v in value.items() if k != 'receipts'}), flush=True)

    def execute(self):
        try:
            probe = self.run / ('clock_' + str(len(self.state['sessions'])))
            before = self.host.sample()['host_seconds']
            self.launch('aux', [sys.executable, str(HERE / 'clock_probe.py'), str(probe)], probe, 10)
            self.await_children()
            if self.reason:
                return
            interval = self.host.sample()['host_seconds'] - before
            proof = read(probe / 'result.json')
            if proof['status'] != 'PASS' or proof['cpu_seconds'] < 2 or interval < 0.5:
                raise RuntimeError('Host monotonic/CPU probe failed')
            atomic(probe / 'CLOCK_VERIFIED.json', {'host_interval_seconds': interval, 'child_cpu_seconds': proof['cpu_seconds'], 'clock': 'TEST_FAKE' if self.test else 'WINDOWS_STOPWATCH'})
            if not (self.run / 'SCHEDULER_PREFLIGHT.json').exists():
                self.scheduler_preflight()
                if self.reason:
                    return
            self.phase = 'CONTROLS'
            controls = self.run / 'controls'
            if not (controls / 'result.json').exists():
                self.launch('aux', [sys.executable, str(HERE / 'controls.py'), str(controls)], controls,
                            min(1800, self.remaining('aux') - 120))
                self.await_children()
            if self.reason:
                return
            report = read(controls / 'result.json')
            assert report['status'] == 'PASS'
            for name, item in report['boundaries'].items():
                if item['rigid']:
                    self.state['done'][name] = 'RIGID_BOUNDARY_VERIFIED'
            self.save()
            self.phase = 'CALIBRATION'
            if not self.state.get('calibrated'):
                for size in (24, 40, 60):
                    task = next(t for t in self.tasks.values() if t['size'] == size and not self.state['done'].get(t['id']))
                    self.task(task['id'], self.policy['calibration_cpu_seconds'])
                    self.await_children()
                    if self.reason:
                        return
                self.state['calibrated'] = True
                self.save()
            self.per_worker = max(512 * 1024 ** 2, 2 * self.state['peak_worker_rss'])
            self.max_workers = max(1, min(self.max_workers, int((23 * GIB) // self.per_worker)))
            atomic(self.run / 'CAPACITY.json', {'workers': self.max_workers, 'estimated_bytes_per_worker': self.per_worker,
                                               'calibration_peak_bytes': self.state['peak_worker_rss'],
                                               'note': 'Calibration CPU charged to original task; later attempts restart with saved incumbent.'})
            self.phase = 'REPAIR'
            self.repair_started_host = self.host.sample()['host_seconds']
            self.repair_cpu_baseline = sum(self.state['used'][k] for k in self.tasks)
            self.last_status = -1000
            first_launch_status = True
            # Fixed interleaving: founder index, size, policy, origin.
            ordered = sorted(self.tasks, key=lambda name: (int(name.split('_')[1]), self.tasks[name]['size'], self.tasks[name]['rule'], name))
            while True:
                self.monitor()
                self.collect()
                if self.reason:
                    self.await_children()
                    break
                busy = {e['category'] for e in self.active.values()}
                todo = [name for name in ordered if name not in self.state['done'] and name not in busy]
                if not todo and not self.active:
                    break
                other_load = max(0, os.getloadavg()[0] - len(self.active))
                capacity = max(0, min(self.max_workers, int(len(os.sched_getaffinity(0)) - other_load)))
                while todo and len(self.active) < capacity and (self.test or self.free_ram >= 6 * GIB + self.per_worker):
                    self.task(todo.pop(0))
                    if self.reason:
                        break
                    self.free_ram -= self.per_worker
                if first_launch_status:
                    self.status()
                    first_launch_status = False
                time.sleep(0.25)
        except BaseException:
            self.reason = self.reason or 'CONTROLLER_EXCEPTION'
            raise
        finally:
            if self.active:
                self.reason = self.reason or 'CONTROLLER_EXCEPTION'
                for pid in list(self.active):
                    self.signal_worker(pid, self.reason)
                self.await_children()
            sample = self.host.sample()
            elapsed = sample['host_seconds'] - self.start['host_seconds']
            host_cpu = self.host.close()
            own = cpu()
            self.state['used']['aux'] += own + host_cpu + 5
            self.state['host_wall_seconds'] = self.host_baseline + elapsed
            self.state['sessions'].append({'controller_cpu_seconds': own, 'host_helper_cpu_seconds': host_cpu,
                                            'host_wall_seconds': elapsed, 'finalization_cpu_reserved': 5})
            self.save()
            (self.run / 'session_active.json').unlink()
            finished = len(self.state['done']) == len(self.tasks)
            terminal = 'COMPLETED_BUDGETED_PILOT' if finished else 'PAUSED_OR_INCOMPLETE'
            if self.reason and self.reason not in ('USER_PAUSE', 'HOST_WALL_LIMIT', 'TOTAL_CPU_LIMIT', 'AUX_CPU_LIMIT', 'VERIFIED_W_ZERO'):
                terminal = 'DIAGNOSIS_REQUIRED'
            if finished and any(v == 'LOCAL_WORKER_ERROR' for v in self.state['done'].values()):
                terminal = 'COMPLETED_WITH_LOCAL_ERRORS'
            if self.reason == 'VERIFIED_W_ZERO':
                terminal = 'SOLUTION_VERIFIED'
            bests = {p.parent.name: read(p) for p in (self.run / 'jobs').glob('*/best.json')}
            atomic(self.run / 'RESULT.json', {'status': terminal, 'reason': self.reason, 'done': self.state['done'],
                                            'cpu_seconds': self.state['used'], 'host_wall_seconds': self.state['host_wall_seconds'],
                                            'bests': bests, 'proof_scope': 'No certified CP-SAT exclusion claims.'})
            # Avoid counting this already settled session twice in terminal status.
            self.aux_baseline = self.state['used']['aux']
            self.status(sample, elapsed, {}, final=terminal)
