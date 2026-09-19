"""Bounded Linux child lifecycle; controller owns only its own process groups."""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

GIB = 1024**3
TERMINAL = {'UNKNOWN', 'CPU_BUDGET', 'WALL_BUDGET', 'SAT_VERIFIED', 'UNSAT_UNCERTIFIED'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024**2), b''):
            h.update(data)
    return h.hexdigest()


def save(path, value):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(path)


def limits(cpu, memory=1536*1024**2, output=16*1024**2):
    parent = os.getpid()
    def apply():
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(1, signal.SIGTERM, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
        if os.getppid() != parent:
            os.kill(os.getpid(), signal.SIGTERM)
        os.nice(10)
        resource.setrlimit(resource.RLIMIT_CORE, (0,0))
        resource.setrlimit(resource.RLIMIT_AS, (memory,memory))
        resource.setrlimit(resource.RLIMIT_FSIZE, (output,output))
        resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(cpu),math.ceil(cpu)+2))
    return apply


def sample(pid):
    try:
        text = Path(f'/proc/{pid}/stat').read_text()
        fields = text[text.rfind(')')+2:].split()
        return (int(fields[11])+int(fields[12])) / os.sysconf('SC_CLK_TCK')
    except (FileNotFoundError, ProcessLookupError):
        return None


def classify(code, text, reason, cpu, budget):
    lines = text.splitlines()
    if code == 10 and 's SATISFIABLE' in lines:
        return 'SAT_REQUIRES_CHECK'
    if code == 20 and 's UNSATISFIABLE' in lines:
        return 'UNSAT_UNCERTIFIED'
    if reason in ('RESOURCE_STOP', 'INTERRUPTED', 'EXTERNAL_ACTIVITY'):
        return reason
    if reason == 'CPU_BUDGET':
        return 'CPU_BUDGET'
    if reason == 'WALL_BUDGET':
        return 'WALL_BUDGET'
    if code in (-signal.SIGXCPU, -signal.SIGKILL) and cpu >= budget-0.5:
        return 'CPU_BUDGET'
    if code == 0 and ('c UNKNOWN' in lines or 's UNKNOWN' in lines):
        return 'UNKNOWN'
    return 'EXECUTION_ERROR'


class Job:
    def __init__(self, task, command, attempt):
        self.task = task
        self.attempt = attempt
        self.started = time.monotonic()
        self.reason = None
        self.stop_at = None
        self.cpu_sample = 0.0
        self.log = attempt / 'solver.log'
        self.stream = self.log.open('xb')
        try:
            self.proc = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                         stdout=self.stream, stderr=subprocess.STDOUT,
                                         start_new_session=True,
                                         preexec_fn=limits(task['cpu_budget']))
        except BaseException:
            self.stream.close()
            raise
        self.command = command
        save(attempt/'launch.json', {'task':task, 'command':command, 'pid':self.proc.pid,
                                    'parent_pid':os.getpid(), 'started_unix':time.time(),
                                    'cpu_budget':task['cpu_budget'], 'nice':10,
                                    'max_virtual_memory_MiB':1536, 'max_log_MiB':16,
                                    'hard_cpu_grace_seconds':2, 'proof_logging':False})

    def stop(self, reason):
        if self.reason is None:
            self.reason = reason
            self.stop_at = time.monotonic()
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    def poll(self):
        pid, status, usage = os.wait4(self.proc.pid, os.WNOHANG)
        if pid:
            self.proc.returncode = os.waitstatus_to_exitcode(status)
            self.stream.close()
            cpu = usage.ru_utime+usage.ru_stime
            text = self.log.read_text(errors='replace')
            result = {'task_id':self.task['id'], 'returncode':self.proc.returncode,
                      'status':classify(self.proc.returncode,text,self.reason,cpu,self.task['cpu_budget']),
                      'termination_reason':self.reason, 'cpu_seconds':cpu,
                      'wall_seconds':time.monotonic()-self.started,
                      'peak_rss_bytes':usage.ru_maxrss*1024, 'log_sha256':sha(self.log),
                      'log_bytes':self.log.stat().st_size, 'attempt':str(self.attempt),
                      'statistics_lines':[s for s in text.splitlines() if s.startswith('c ') and
                                          any(t in s.lower() for t in ('conflicts:', 'decisions:',
                                                                      'total process time', 'resident set'))]}
            return result
        value = sample(self.proc.pid)
        if value is not None:
            self.cpu_sample = value
            if value >= self.task['cpu_budget']:
                self.stop('CPU_BUDGET')
        if time.monotonic()-self.started >= self.task.get('wall_budget',4*self.task['cpu_budget']+30):
            self.stop('WALL_BUDGET')
        if self.stop_at is not None and time.monotonic()-self.stop_at >= 2:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        return None


def available():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1])*1024
    raise RuntimeError('No MemAvailable')


def foreign_processes(own):
    ignored = {os.getpid(),os.getppid(),*own}
    found = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name) in ignored:
            continue
        try:
            name = (p/'comm').read_text().strip()
        except (FileNotFoundError,ProcessLookupError,PermissionError):
            continue
        if name.startswith(('python','cadical','kissat','glucose','minisat')):
            found.append({'pid':int(p.name),'name':name})
    return found
