"""Office-only C2 technical pilot 1.0.1: four sequential, bounded, proof-free jobs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

VERSION = '1.0.1'
GIB = 1024 ** 3
SOLVER_SHA = '82c88e3027d35e7c60293ea9440fc97576e1161ee9e103785bdb6962748ba996'
SOLVER_COMMIT = '4198d817d0dcde5b1240eefbff70b555b7df2af9'
MAP_SHA = 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'
PINNED = {
    'totalizer': '5b4c87e8ce377f0e9f9b8714e461cf1a8a77897e87773dd1978b7069470b7134',
    'lex': '0313ff8950052b054edb34d3934d4a828f3cfc3c2d473a5f7cd973c71f427d67',
    'triangles': '7c9e4885d76cc8501d03f112a40f9936977523e0b2b4a4a2d794f25d31ce6a53',
    'both': '5e2a8dd8b1a52da34c5590d408fc64a0038df0de542c7789f1a944811758a387',
}
# Predeclared mixed order; a technical pilot, not a statistically balanced benchmark.
ORDER = ('totalizer', 'both', 'lex', 'triangles')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def linux_available():
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) * 1024
    raise RuntimeError('MemAvailable missing')


def windows_free():
    executable = shutil.which('powershell.exe')
    if not executable:
        path = Path('/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe')
        if path.is_file():
            executable = str(path)
    if not executable:
        raise RuntimeError('Windows free-space probe unavailable; no solver launched')
    command = [executable, '-NoLogo', '-NoProfile', '-NonInteractive', '-Command',
               '[Console]::WriteLine((Get-PSDrive -Name C -ErrorAction Stop).Free)']
    try:
        result = subprocess.run(command, capture_output=True, timeout=8, check=True)
        value = int(result.stdout.decode('utf-8-sig').strip())
    except (subprocess.SubprocessError, ValueError, UnicodeError) as error:
        raise RuntimeError('Windows free-space probe failed; no next solver launched') from error
    if value < 20 * GIB:
        raise RuntimeError('Windows C: reserve below 20 GiB')
    return value


def preflight(root):
    memory = linux_available()
    disk = shutil.disk_usage(root).free
    if memory < 3 * GIB:
        raise RuntimeError('Need at least 3 GiB MemAvailable before a job')
    if disk < 2 * GIB:
        raise RuntimeError('Linux disk reserve below 2 GiB')
    busy = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit() or int(entry.name) in (os.getpid(), os.getppid()):
            continue
        try:
            name = (entry / 'comm').read_text().strip()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if name.startswith(('python', 'cadical', 'kissat', 'glucose', 'minisat')):
            busy.append({'pid': int(entry.name), 'name': name})
    if busy:
        raise RuntimeError('Other potential research processes active; no launch: ' + repr(busy))
    return {'linux_available_bytes': memory, 'linux_disk_free_bytes': disk,
            'windows_C_free_bytes': windows_free(), 'load_average': os.getloadavg()}


def child_limits():
    os.nice(10)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024 ** 2,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 ** 2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))


def process_sample(pid):
    try:
        fields = {}
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            key, _, value = line.partition(':')
            if key in ('VmRSS', 'VmHWM'):
                fields[key] = int(value.split()[0]) * 1024
        return fields
    except (FileNotFoundError, ProcessLookupError):
        return {}


def live_guard(root):
    if linux_available() < GIB:
        return 'RAM_RESERVE'
    if shutil.disk_usage(root).free < 2 * GIB:
        return 'LINUX_DISK_RESERVE'
    return None


def classify_exit(returncode, text, wall, cpu, stop_reason=None, solver_wall_limit=None):
    announced = [s.strip() for s in text.splitlines() if s.startswith('s ')]
    if stop_reason:
        state = 'STOPPED_' + stop_reason
    elif returncode == 10 and 's SATISFIABLE' in announced:
        state = 'SAT_UNVERIFIED'
    elif returncode == 20 and 's UNSATISFIABLE' in announced:
        state = 'UNSAT_UNCERTIFIED'
    elif returncode == 0 and ('s UNKNOWN' in announced or 'c UNKNOWN' in text.splitlines()):
        state = 'UNKNOWN'
    elif (returncode == -signal.SIGALRM and solver_wall_limit is not None
          and solver_wall_limit > 0
          and wall >= solver_wall_limit - min(1.0, 0.05 * solver_wall_limit)
          and f'c setting time limit to {solver_wall_limit} seconds real time' in text
          and f'c raising signal {int(signal.SIGALRM)} (SIGALRM)' in text.splitlines()
          and not any(s in announced for s in ('s SATISFIABLE', 's UNSATISFIABLE'))):
        state = 'WALL_TIME_LIMIT'
    elif returncode == -signal.SIGKILL and cpu >= 59:
        state = 'CPU_LIMIT'
    else:
        state = 'EXECUTION_ERROR'
    return state


def run_job(command, output, guard, wall_limit=75, solver_wall_limit=None):
    """Own process group only; wait4 provides per-process CPU and peak RSS."""
    started = time.monotonic()
    peak = 0
    stop_reason = None
    stop_at = None
    interrupted = False
    with output.open('xb') as stream:
        proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stream,
                                stderr=subprocess.STDOUT, start_new_session=True,
                                preexec_fn=child_limits)
        try:
            while True:
                pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
                if pid:
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    break
                peak = max(peak, process_sample(proc.pid).get('VmHWM', 0))
                elapsed = time.monotonic() - started
                if stop_reason is None:
                    stop_reason = guard()
                    if stop_reason is None and elapsed >= wall_limit:
                        stop_reason = 'WALL_LIMIT'
                    if stop_reason:
                        stop_at = time.monotonic()
                        try:
                            os.killpg(proc.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                elif time.monotonic() - stop_at >= 2:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                time.sleep(0.25)
        except BaseException:
            interrupted = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
            raise
        finally:
            if interrupted:
                print('Stopped own pilot process; earlier logs retained.', flush=True)
    wall = time.monotonic() - started
    cpu = usage.ru_utime + usage.ru_stime
    text = output.read_text(errors='replace')
    state = classify_exit(proc.returncode, text, wall, cpu, stop_reason, solver_wall_limit)
    statistics = [line for line in text.splitlines() if line.startswith('c ') and any(
        token in line.lower() for token in ('conflicts:', 'decisions:', 'maximum resident',
                                            'process time', 'real time', 'seconds total'))]
    return {'status': state, 'returncode': proc.returncode, 'stop_reason': stop_reason,
            'wall_seconds': wall, 'cpu_seconds': cpu,
            'peak_rss_bytes': usage.ru_maxrss * 1024, 'sampled_peak_bytes': peak,
            'statistics_lines': statistics, 'log_bytes': output.stat().st_size,
            'log_sha256': digest(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    solver = Path.home() / 'conway99_workspace/cadical_office_2.2.1/build/cadical'
    directory = root / 'office_variants_6'
    if digest(solver) != SOLVER_SHA:
        raise RuntimeError('Office solver binary hash mismatch')
    if subprocess.check_output([str(solver), '--version'], text=True, timeout=5).strip() != '2.2.1':
        raise RuntimeError('Wrong solver version')
    for file, status in [('office_controls.json', 'C2_RESIDUAL_SMALL_CONTROLS_PASS'),
                         ('office_solver_controls.json', 'OFFICE_SOLVER_CONTROLS_PASS'),
                         ('office_up_6/report.json', 'C2_STRUCTURED_UP_PASS')]:
        if json.loads((root / file).read_text())['status'] != status:
            raise RuntimeError('Missing prerequisite: ' + file)
    if digest(directory / 'variables.json') != MAP_SHA:
        raise RuntimeError('Primary mapping mismatch')
    for variant, sha in PINNED.items():
        if digest(directory / f'matching_6__{variant}.cnf') != sha:
            raise RuntimeError('CNF identity mismatch: ' + variant)
    manifest = json.loads((directory / 'manifest.json').read_text())
    if {j['variant']: j['sha256'] for j in manifest['jobs']} != PINNED:
        raise RuntimeError('Variant manifest mismatch')
    first_resources = preflight(root)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    out = root / 'office_pilot_runs' / ('pilot_' + stamp)
    out.mkdir(parents=True, exist_ok=False)
    report = {'version': VERSION, 'status': 'RUNNING', 'scope': 'Technical scout only; no proof',
              'runner_sha256': digest(__file__), 'solver_sha256': SOLVER_SHA,
              'solver_source_commit': SOLVER_COMMIT, 'variant_hashes': PINNED,
              'mapping_sha256': MAP_SHA, 'seed': 0, 'case': 'matching_6', 'order': ORDER,
              'limits': {'parallel_jobs': 1, 'cpu_seconds': 60, 'solver_wall_seconds': 55,
                         'wrapper_wall_seconds': 75, 'virtual_memory_MiB': 1536,
                         'max_log_MiB_per_job': 16, 'proof_logging': False, 'nice': 10},
              'first_resources': first_resources, 'jobs': [], 'run_dir': str(out)}
    save(out / 'summary.json', report)
    print('OFFICE_PILOT_STARTED ' + json.dumps({'run_dir': str(out), 'jobs': 4}), flush=True)
    try:
        for index, variant in enumerate(ORDER):
            resources = first_resources if index == 0 else preflight(root)
            command = [str(solver), '--seed=0', '-t', '55',
                       str(directory / f'matching_6__{variant}.cnf')]
            print('START ' + variant + ' (max 60 CPU-s, one process)', flush=True)
            save(out / (variant + '_job.json'), {'command': command, 'resources': resources})
            result = run_job(command, out / (variant + '.log'), lambda: live_guard(root), solver_wall_limit=55)
            result['variant'] = variant
            result['command'] = command
            report['jobs'].append(result)
            save(out / 'summary.json', report)
            print('DONE ' + json.dumps(result), flush=True)
            if result['status'] not in ('UNKNOWN', 'CPU_LIMIT', 'WALL_TIME_LIMIT'):
                report['status'] = 'STOPPED_FOR_REVIEW'
                break
        else:
            report['status'] = 'TECHNICAL_PILOT_COMPLETE'
    except (Exception, KeyboardInterrupt) as error:
        report['status'] = 'ABORTED'
        report['error'] = repr(error)
    save(out / 'summary.json', report)
    print('OFFICE_PILOT_RESULT ' + json.dumps(report), flush=True)
    if report['status'] == 'ABORTED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
