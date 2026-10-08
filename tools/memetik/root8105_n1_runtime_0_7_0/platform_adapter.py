"""Windows clock and continuous resource observer; no production approval.
Windows helper end CPU and owner lower bound remain separate from Linux wait4.
"""
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import time
import runtime as r

ENV = 'N1_PLATFORM_SESSION'
LIVENESS_SECONDS = 30.0


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def configuration(root, argv):
    path = root / 'manifest.json'
    if path.exists():
        return r.read(path).get('platform_wsl', False)
    return '--platform-wsl' in argv


def current():
    value = os.environ.get(ENV)
    if value is None:
        return None
    import accounting
    root = Path(value)
    require(root.name == 'platform' and root.parent.name == os.environ.get(accounting.ENV),
            'platform session mismatch')
    return root


def health():
    folder = current()
    if folder is None:
        return None
    report = r.read(folder / 'health.json')
    require(report['session_id'] == folder.parent.name, 'foreign platform report')
    require(finite(report['guest_monotonic']) and
            0 <= time.monotonic() - report['guest_monotonic'] <= LIVENESS_SECONDS,
            'platform observer stale')
    require(report['ok'], 'platform fault: ' + str(report['fault']))
    if (folder / 'fault.json').exists():
        raise ValueError('latched platform fault: ' + str(r.read(folder / 'fault.json')))
    return report


def before_native():
    if current() is not None:
        health()


def register_native(ident, directory, phase):
    folder = current()
    if folder is not None:
        r.raw_atomic(folder / 'native.json', dict(identity=ident, directory=str(directory), phase=phase))


def unregister_native():
    folder = current()
    if folder is not None:
        r.raw_atomic(folder / 'native.json', dict(identity=None))


class Clock:
    def __init__(self, session):
        self.session = session
        self.previous = None
        self.last_progress = time.monotonic()

    def accept(self, record, now=None):
        now = time.monotonic() if now is None else now
        require(record['schema'] == 'N1_WINDOWS_CLOCK_1' and record['session_id'] == self.session,
                'foreign host heartbeat')
        require(record['synthetic'] is False and record['high_resolution'] is True,
                'not a real high resolution Windows clock')
        for key in ('pid', 'frequency', 'ticks', 'utc_ticks', 'available_physical_bytes'):
            require(type(record[key]) is int and record[key] > 0, 'invalid host field: ' + key)
        require(type(record['sequence']) is int and record['sequence'] >= 0 and
                isinstance(record['birth'], str) and record['birth'].isdecimal() and
                finite(record['cpu_lower_bound_s']), 'invalid host identity/CPU')
        old = self.previous
        if old is not None:
            require(all(record[k] == old[k] for k in ('pid', 'birth', 'frequency')), 'host identity changed')
            require(record['sequence'] >= old['sequence'] and record['ticks'] >= old['ticks'] and
                    record['cpu_lower_bound_s'] >= old['cpu_lower_bound_s'], 'host counters regressed')
            if record['sequence'] == old['sequence']:
                require(record == old, 'changed duplicate host sequence')
            else:
                require(record['ticks'] > old['ticks'], 'host clock did not advance')
                self.last_progress = now
        else:
            self.last_progress = now
        require(now - self.last_progress <= LIVENESS_SECONDS, 'host heartbeat stopped advancing')
        self.previous = record
        return record

    def end(self, value):
        require(self.previous is not None, 'no host heartbeat before end receipt')
        require(value['schema'] == 'N1_WINDOWS_END_1' and value['session_id'] == self.session and
                value['synthetic'] is False and value['exit_code'] == 0 and
                value['pid'] == self.previous['pid'] and value['birth'] == self.previous['birth'],
                'invalid Windows end identity/exit')
        require(finite(value['sampler_cpu_end_s']) and finite(value['owner_cpu_lower_bound_s']) and
                value['sampler_cpu_end_s'] >= self.previous['cpu_lower_bound_s'] and
                value['owner_tail_complete'] is False, 'invalid host end account')
        return value


class Cgroup:
    def __init__(self):
        self.identity = None
        self.events = None

    def sample(self, snapshot, cfg):
        identity = (snapshot['membership'], snapshot['mount'], snapshot['directory'])
        if self.identity is not None:
            require(identity == self.identity, 'cgroup membership changed')
        self.identity = identity
        events = {}
        headroom = []
        for row in snapshot['visible_ancestors']:
            maximum, current = row['memory.max'], row['memory.current']
            # A cgroup2 mount root may omit memory-controller files. A partially
            # exposed controller is not accepted as an unlimited healthy one.
            if maximum is None and current is None and row['memory.events'] is None:
                continue
            require(type(current) is int and current >= 0 and
                    (maximum == 'max' or type(maximum) is int and maximum >= 0), 'missing cgroup counter')
            if type(maximum) is int:
                headroom.append(maximum - current)
            require(isinstance(row['memory.events'], str), 'missing cgroup events')
            pairs = [line.split() for line in row['memory.events'].splitlines()]
            require(all(len(x) == 2 and x[1].isdecimal() for x in pairs), 'invalid cgroup events')
            counters = {k: int(v) for k, v in pairs}
            require(len(counters) == len(pairs) and all(k in counters for k in ('oom', 'oom_kill')),
                    'incomplete cgroup events')
            events[row['path']] = counters
        require(bool(events), 'no visible memory controller')
        if self.events is not None:
            require(events.keys() == self.events.keys(), 'cgroup ancestry changed')
            for path, counters in events.items():
                for key in ('oom', 'oom_kill'):
                    require(counters[key] == self.events[path][key], 'new/regressed cgroup OOM event')
        self.events = events
        if headroom:
            require(min(headroom) >= cfg['min_available_bytes'], 'CGROUP_MEMORY_RESERVE')
        return dict(snapshot, observed_finite_headroom_bytes=min(headroom) if headroom else None,
                    continuous=True, observation_only=True)


def stop_native(folder, root):
    """Only this session's published child; pidfd prevents PID-reuse signalling."""
    import guard
    path = folder / 'native.json'
    if not path.exists():
        return
    value = r.read(path)
    ident = value['identity']
    if ident is None:
        return
    directory = Path(value['directory'])
    require(directory.parent == root / 'attempts', 'foreign native path')
    observed = guard.stat(ident)
    if observed is None or observed["zombie"]:
        return
    if value['phase'] == 'search':
        r.raw_atomic(directory / 'STOP', dict(platform_fault=True))
    elif value['phase'] == 'check':
        try:
            fd = os.pidfd_open(ident['pid'])
        except ProcessLookupError:
            return
        try:
            if guard.stat(ident) is not None:
                signal.pidfd_send_signal(fd, signal.SIGTERM)
        finally:
            os.close(fd)
    else:
        raise ValueError('unknown native phase')


class Observer:
    def __init__(self, root, directory, cfg):
        self.root, self.folder, self.cfg = root, directory / 'platform', cfg
        self.folder.mkdir()
        self.session = directory.name
        self.clock, self.cgroup = Clock(self.session), Cgroup()
        self.fault = None
        self.child = None
        self.receipt = None
        self.self_identity = r.identity(os.getpid())
        self.inner = None
        self.samples = 0
        self.started = time.monotonic()
        self.log = (self.folder / 'host.log').open('xb')

    def start(self):
        require('microsoft' in platform.release().lower(), 'Windows adapter requires real WSL')
        shell = shutil.which('powershell.exe')
        convert = shutil.which('wslpath')
        require(shell is not None and convert is not None, 'Windows interop unavailable')
        script = Path(__file__).with_name('host_clock.ps1').resolve()
        windows = [subprocess.check_output([convert, '-w', str(p)], text=True).strip()
                   for p in (script, self.folder)]
        self.child = subprocess.Popen([shell, '-NoLogo', '-NoProfile', '-NonInteractive', '-File',
            windows[0], '-Directory', windows[1], '-Session', self.session],
            stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT)
        while not (self.folder / 'heartbeat.json').exists():
            require(self.child.poll() is None, 'Windows adapter exited before heartbeat')
            require(time.monotonic() - self.started <= LIVENESS_SECONDS, 'Windows adapter startup not observed')
            time.sleep(0.05)
        self.tick()
        require(self.fault is None, str(self.fault))

    def latch(self, error):
        if self.fault is None:
            self.fault = dict(reason=str(error), utc_ns=time.time_ns(), session_id=self.session)
            r.raw_atomic(self.folder / 'fault.json', self.fault)
        stop_native(self.folder, self.root)

    def tick(self):
        import preflight
        import guard
        try:
            host = self.clock.accept(json.loads((self.folder / 'heartbeat.json').read_text(encoding='utf-8-sig')))
            cg = self.cgroup.sample(preflight.cgroup_probe(), self.cfg)
            rss = guard.stat(self.self_identity)["rss_bytes"]
            if self.inner is not None:
                inner = guard.stat(self.inner)
                if inner is not None:
                    rss += inner["rss_bytes"]
            native_path = self.folder / "native.json"
            if native_path.exists():
                ident = r.read(native_path)["identity"]
                child = guard.stat(ident) if ident else None
                if child is not None:
                    rss += child["rss_bytes"]
            resources = guard.sensors(self.root if self.root.exists() else self.root.parent, rss)
            require(resources["rss_bytes"] <= self.cfg["max_rss_bytes"], "RUN_RSS")
            require(resources['available_bytes'] >= self.cfg['min_available_bytes'], 'GUEST_MEMORY_RESERVE')
            require(resources['free_bytes'] >= self.cfg['min_free_bytes'], 'DISK_RESERVE')
            require(host['available_physical_bytes'] >= self.cfg['min_available_bytes'], 'HOST_MEMORY_RESERVE')
            self.samples += 1
            report = dict(session_id=self.session, ok=self.fault is None, fault=self.fault,
                          host=host, cgroup=cg, samples=self.samples, guest_monotonic=time.monotonic(),
                          guest_utc_ns=time.time_ns())
            r.raw_atomic(self.folder / 'health.json', report)
        except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
            self.latch(type(exc).__name__ + ': ' + str(exc))
        if self.fault is not None:
            stop_native(self.folder, self.root)

    def finish(self):
        r.raw_atomic(self.folder / 'STOP', dict(session_id=self.session))
        if self.child is not None:
            # No budget timeout or kill escalation. The helper closes cooperatively.
            self.child.wait()
            try:
                final = json.loads((self.folder / 'sampler-final.json').read_text(encoding='utf-8-sig'))
                self.clock.accept(final)
                self.receipt = self.clock.end(json.loads((self.folder / 'receipt.json').read_text(encoding='utf-8-sig')))
                require(self.child.returncode == 0, 'Windows transport failed')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                self.latch('HOST_END_ACCOUNT_MISSING_OR_INVALID: ' + str(exc))
        else:
            self.latch('HOST_NOT_STARTED')
        self.log.close()
        result = dict(schema='N1_PLATFORM_END_1', session_id=self.session,
                      adapter_complete=self.receipt is not None, host=self.receipt,
                      fault=self.fault, samples=self.samples, all_system_cpu_complete=False,
                      exclusions=['Windows observer after its last sample',
                                  'Linux observer tail and interop transport', 'unrelated host services'])
        r.raw_atomic(self.folder / 'final.json', result)
        return result
