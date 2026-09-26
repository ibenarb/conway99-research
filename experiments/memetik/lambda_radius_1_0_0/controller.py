"""Fixed global budgets, wait4 receipts, persistent Windows wall time, owned workers."""
import boot
from support import *
from hostclock import HostClock
from enumeration import EXPECTED
import shutil

LIMITS = {'aux': 7200, '2076': 72000, '2077': 72000}


class Controller:
    def __init__(self, run, host=None, test=False):
        self.run = Path(run)
        self.test = test
        self.statepath = self.run / 'ledger.json'
        self.state = read(self.statepath) if self.statepath.exists() else {
            'used': {k: 0.0 for k in LIMITS}, 'host_wall_seconds': 0.0, 'sessions': [], 'active': {}}
        if self.state['active'] or (self.run / 'session_active.json').exists():
            raise RuntimeError('Unresolved prior session: preserve checkpoints and diagnose CPU receipts before resume')
        self.host = host or HostClock(run)
        self.host0 = self.host.sample()
        self.cpu0 = 0.0  # Include interpreter startup and imports.
        self.active = {}
        self.last_status = -1000.0
        self.last_host_poll = time.monotonic()
        self.phase_started = self.host0['host_seconds']
        self.phase_initial_done = 0
        self.last_disk = -1000.0
        self.disk_bytes = 0
        self.phase = 'initializing'
        self.max_workers = min(12, len(os.sched_getaffinity(0)))
        self.stopping = None
        atomic(self.run / 'session_active.json', {'pid': os.getpid(), 'start_ticks': process(os.getpid())['start_ticks']})
        signal.signal(signal.SIGTERM, stopped)
        signal.signal(signal.SIGINT, stopped)
        self.save()

    def save(self):
        atomic(self.statepath, self.state)

    def used(self, category):
        total = self.state['used'][category]
        if category == 'aux':
            total += own_cpu() + self.host.last['windows_cpu_seconds']
        return total

    def remaining(self, category):
        return LIMITS[category] - self.used(category) - sum(e['allocation'] for e in self.active.values() if e['category'] == category)

    def monitor(self):
        if time.monotonic() - self.last_host_poll >= 1:
            self.host.sample()
            self.last_host_poll = time.monotonic()
        h = self.host.last
        elapsed = h['host_seconds'] - self.host0['host_seconds']
        usage = {pid: process(pid) for pid in self.active}
        if not self.test:
            mem = {line.split(':')[0]: int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()}
            if mem['MemAvailable'] < 6 * GIB:
                self.stopping = 'RAM_RESERVE'
            if sum(x['rss'] for x in usage.values()) + process(os.getpid())['rss'] > 8 * GIB:
                self.stopping = 'GROUP_RAM_LIMIT'
            if shutil.disk_usage(self.run).free < 25 * GIB or h['physical_free_bytes'] < 25 * GIB:
                self.stopping = 'DISK_RESERVE'
            if elapsed - self.last_disk >= 60:
                self.disk_bytes = sum(p.stat().st_size for p in self.run.rglob('*') if p.is_file())
                self.last_disk = elapsed
            if self.disk_bytes > 10 * GIB:
                self.stopping = 'OUTPUT_DISK_LIMIT'
        if self.state['host_wall_seconds'] + elapsed >= 28800:
            self.stopping = 'HOST_WALL_LIMIT'
        if self.used('aux') + sum(process(pid)['cpu'] for pid, e in self.active.items() if e['category'] == 'aux') >= 7170:
            self.stopping = 'AUX_CPU_LIMIT'
        if STOP or __import__('support').STOP:
            self.stopping = 'USER_PAUSE'
        return h, elapsed, usage

    def job(self, name, task):
        d = self.run / 'jobs' / name
        d.mkdir(parents=True, exist_ok=True)
        p = d / 'task.json'
        if p.exists() and read(p) != task:
            raise RuntimeError('Immutable task changed: ' + name)
        if not p.exists():
            atomic(p, task)
        return d

    def done(self, directory):
        p = directory / 'receipt.json'
        if not p.exists():
            return None
        r = read(p)
        if r['task_sha256'] != digest(directory / 'task.json'):
            raise RuntimeError('Task receipt mismatch')
        if r['result_sha256'] != digest(directory / 'slice_result.json'):
            raise RuntimeError('Result receipt mismatch')
        checkpoint = directory / 'work.sqlite'
        if checkpoint.exists() and r['checkpoint_sha256'] != digest(checkpoint):
            raise RuntimeError('Checkpoint receipt mismatch')
        if r['exit_code']:
            raise RuntimeError('Failed worker requires diagnosis: ' + str(directory))
        for filename, expected in r.get('output_sha256', {}).items():
            if digest(directory / filename) != expected:
                raise RuntimeError('Output receipt mismatch')
        result = read(directory / 'slice_result.json')
        return result if result['status'] in ('DONE', 'FOUND') else None

    def spawn(self, name, directory, category, allocation):
        allocation = int(allocation)
        if allocation < 6 or self.remaining(category) < allocation + 5:
            return False
        # Durable reservation precedes spawn: an interrupted handoff cannot silently lose CPU.
        self.state['active'][name] = {'category': category, 'allocation': allocation, 'status': 'RESERVED'}
        self.save()
        with (directory / 'worker.log').open('ab') as log:
            proc = subprocess.Popen([sys.executable, str(boot.HERE / 'worker.py'), str(directory), str(allocation)],
                                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, **THREAD_ENV, 'PYTHONNOUSERSITE': '1'})
        self.active[proc.pid] = dict(proc=proc, name=name, directory=directory, category=category,
                                     allocation=allocation, sent=None, host_start=self.host.last['host_seconds'])
        self.state['active'][name].update(pid=proc.pid, start_ticks=process(proc.pid)['start_ticks'])
        self.save()
        return True

    def reap(self):
        finished = []
        for pid in list(self.active):
            waited, status, usage = os.wait4(pid, os.WNOHANG)
            if not waited:
                continue
            e = self.active.pop(pid)
            code = os.waitstatus_to_exitcode(status)
            e['proc'].returncode = code
            self.host.sample()
            self.last_host_poll = time.monotonic()
            cpu = usage.ru_utime + usage.ru_stime
            self.state['used'][e['category']] += cpu
            d = e['directory']
            result = read(d / 'slice_result.json') if code == 0 and (d / 'slice_result.json').exists() else {'status': 'FAILED'}
            p = d / 'receipt.json'
            old = read(p) if p.exists() else {'sessions': []}
            entry = {'cpu_seconds': cpu, 'allocation': e['allocation'], 'exit_code': code,
                     'maxrss_kib': usage.ru_maxrss, 'host_elapsed': self.host.last['host_seconds'] - e['host_start']}
            receipt = {'sessions': old['sessions'] + [entry], 'exit_code': code,
                       'cpu_seconds': sum(x['cpu_seconds'] for x in old['sessions']) + cpu,
                       'task_sha256': digest(d / 'task.json'),
                       'result_sha256': digest(d / 'slice_result.json') if (d / 'slice_result.json').exists() else None,
                       'checkpoint_sha256': digest(d / 'work.sqlite') if (d / 'work.sqlite').exists() else None}
            receipt['output_sha256'] = {name: digest(d / name) for name in ('lower.sqlite', 'layers.sqlite')
                                        if result['status'] == 'DONE' and (d / name).exists()}
            atomic(p, receipt)
            del self.state['active'][e['name']]
            self.save()
            if cpu > e['allocation'] or code:
                self.stopping = 'WORKER_FAILED_OR_BUDGET_OVERRUN:' + e['name']
            finished.append((e, result))
        return finished

    def report(self, jobs, results, force=False):
        h, elapsed, usage = self.monitor()
        if not force and elapsed - self.last_status < 600:
            return
        partial = []
        for pid, e in self.active.items():
            path = e['directory'] / 'slice_result.json'
            partial.append({'job': e['name'], 'slice_cpu': usage[pid]['cpu']})
        count = len(results)
        # Estimate by completed disjoint chunks, not by Linux/WSL elapsed time.
        phase_elapsed = h['host_seconds'] - self.phase_started
        new_done = count - self.phase_initial_done
        rate = new_done / phase_elapsed if phase_elapsed > 0 and new_done > 0 else 0
        report = {'status': 'RUNNING' if not self.stopping else 'PAUSING', 'phase': self.phase,
                  'jobs_complete': count, 'jobs_total': len(jobs), 'active_workers': len(self.active),
                  'charged_cpu_seconds': {k: self.used(k) for k in LIMITS},
                  'active_cpu_seconds': sum(x['cpu'] for x in usage.values()),
                  'rss_bytes': sum(x['rss'] for x in usage.values()) + process(os.getpid())['rss'],
                  'host_wall_seconds': self.state['host_wall_seconds'] + elapsed,
                  'eta_seconds': (len(jobs) - count) / rate if rate else None,
                  'eta_scope': 'rough current-phase chunk completion; no guarantee of budget sufficiency',
                  'utc': h['utc'], 'reason': self.stopping, 'active': partial}
        atomic(self.run / 'status.json', report)
        print('RADIUS_STATUS ' + json.dumps(report), flush=True)
        self.last_status = elapsed

    def execute(self, jobs, phase, early_found=False, allocation=60):
        self.phase = phase
        results = {}
        pending = []
        found_arms = set()
        for name, task, category in jobs:
            d = self.job(name, task)
            result = self.done(d)
            if result:
                results[name] = result
                if result['status'] == 'FOUND':
                    found_arms.add(category)
            else:
                pending.append((name, d, category))
        self.phase_started = self.host.last['host_seconds']
        self.phase_initial_done = len(results)
        while pending or self.active:
            self.monitor()
            finished = self.reap()
            for e, result in finished:
                if result['status'] in ('DONE', 'FOUND'):
                    results[e['name']] = result
                    if result['status'] == 'FOUND':
                        found_arms.add(e['category'])
                        atomic(self.run / ('WITNESS_' + read(e['directory'] / 'task.json')['arm'] + '.json'), result['witness'])
                        print('VERIFIED_WITNESS ' + json.dumps({'job': e['name'], 'scores': result['witness']['scores']}), flush=True)
                elif not self.stopping:
                    pending.append((e['name'], e['directory'], e['category']))
            for pid, e in self.active.items():
                if self.stopping or (early_found and e['category'] in found_arms):
                    if e['sent'] is None:
                        os.kill(pid, signal.SIGTERM)
                        e['sent'] = self.host.last['host_seconds']
                    elif self.host.last['host_seconds'] - e['sent'] > 10:
                        os.kill(pid, signal.SIGKILL)
            if not self.stopping:
                eligible = [p for p in pending if not (early_found and p[2] in found_arms)]
                pending = eligible
                stalled = []
                while pending and len(self.active) < self.max_workers:
                    name, d, category = pending.pop(0)
                    cap = min(allocation, self.remaining(category) - 10)
                    if cap < 6 or not self.spawn(name, d, category, cap):
                        stalled.append((name, d, category))
                pending += stalled
                if pending and not self.active:
                    self.stopping = 'CPU_BUDGET_INCOMPLETE'
            self.report(jobs, results)
            if self.stopping and not self.active:
                break
            if pending or self.active:
                time.sleep(0.1)
        self.report(jobs, results, True)
        return results

    def close(self):
        # Best-effort drain; only PIDs created and still owned here are signalled.
        for pid in self.active:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        for _ in range(100):
            if not self.active:
                break
            self.host.sample()
            self.reap()
            time.sleep(0.1)
        for pid in list(self.active):
            os.kill(pid, signal.SIGKILL)
        while self.active:
            self.reap()
            time.sleep(0.05)
        elapsed = self.host.last['host_seconds'] - self.host0['host_seconds']
        hostcpu = self.host.close()
        self.state['used']['aux'] += own_cpu() + hostcpu
        self.state['host_wall_seconds'] += elapsed
        self.state['sessions'].append({'cpu_self': own_cpu(), 'host_cpu': hostcpu, 'host_wall': elapsed})
        self.save()
        (self.run / 'session_active.json').unlink()
