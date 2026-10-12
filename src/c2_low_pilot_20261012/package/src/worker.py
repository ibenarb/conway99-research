"""Detached per-job supervisor. Controller exit does not kill this supervisor."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

from progress import ProofCounter
from common import GIB, alive, busy_cpu, cpu_clock, host, identity, lock, proc, read, require, save


def child_setup():
    os.nice(5)
    # No PDEATHSIG: preserving expensive work takes precedence over parent cleanup.
    resource.setrlimit(resource.RLIMIT_CPU, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def reasons(config, resources, live, proof_bytes, category):
    out = []
    if resources['available_ram_gib'] < config['min_ram_gib']:
        out.append('LOW_AVAILABLE_RAM')
    if min(x for x in (resources['linux_free_gib'], resources['windows_c_free_gib']) if x is not None) < config['min_disk_gib']:
        out.append('LOW_PHYSICAL_DISK')
    if live and config['rss_pause_gib'].get(category) is not None and live['rss_bytes'] > config['rss_pause_gib'][category] * GIB:
        out.append('PROCESS_RSS_RESERVE')
    if config.get('max_proof_gib') is not None and proof_bytes > config['max_proof_gib'] * GIB:
        out.append('PROOF_SIZE_REVIEW')
    return out


def budget_update(target, cpu_s, control, sequence):
    stopped = False
    if control and control.get('sequence', 0) > sequence:
        amount = float(control['extend_seconds'])
        require(amount >= 0, 'Invalid negative extension')
        sequence = control['sequence']
        if amount == 0:
            stopped = True
        else:
            target = max(target, cpu_s) + amount
    return target, sequence, stopped


def run(directory):
    directory = Path(directory).resolve()
    held = lock(directory / 'worker.lock')
    spec = read(directory / 'spec.json')
    root = Path(spec['root'])
    work = root / 'work'
    require(not (directory / 'result.json').exists(), 'Receipt exists; no duplicate execution')
    require(not (directory / 'launch.json').exists(), 'Prior launch exists; automatic restart forbidden')
    start_self_cpu = time.process_time()
    def interrupted(signum, frame):
        raise RuntimeError('Supervisor signal: ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    counters = [ProofCounter(p, 'lrat' if str(p).endswith('.lrat') else 'drat')
                for p in spec.get('outputs', []) if str(p).endswith(('.lrat', '.drat'))]
    pause_events = 0
    state = {'job': spec['id'], 'supervisor': proc(os.getpid()), 'phase': 'HASHING_INPUTS',
             'child': None, 'target_cpu_s': spec['target_cpu_s'], 'eta': None}
    save(directory / 'state.json', state)
    inputs = [identity(path) for path in spec.get('inputs', [])]
    started = time.time()
    child = None
    paused = False
    stop_requested = False
    sequence = 0
    stop_time = None
    target = float(spec['target_cpu_s'])
    last_status = last_detail = last_checkpoint = 0.0
    previous = cpu_clock()
    previous_cpu = 0.0
    background_sum = background_n = 0
    peak_outputs = peak_rss = 0
    proof_previous_size = 0
    proof_previous_time = time.monotonic()
    try:
        with (directory / 'output.log').open('wb') as output:
            child = subprocess.Popen(spec['command'], cwd=spec.get('cwd') or root,
                                     stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                     start_new_session=True, preexec_fn=child_setup)
        live = proc(child.pid)
        state.update(child=live or {'pid': child.pid, 'birth': None}, phase='RUNNING')
        save(directory / 'launch.json', {'command': spec['command'], 'started_unix': started,
                                        'inputs': inputs, 'supervisor': state['supervisor'], 'child': state['child']})
        save(directory / 'state.json', state)
        while True:
            waited, status, usage = os.wait4(child.pid, os.WNOHANG)
            if waited:
                child.returncode = os.waitstatus_to_exitcode(status)
                break
            config = read(root / 'config.json')
            live = proc(child.pid)
            if live:
                require(state['child']['birth'] in (None, live['birth']), 'PID identity changed')
                state['child'] = live
                peak_rss = max(peak_rss, live['rss_bytes'])
            now = time.monotonic()
            resources = host(work)
            sizes = sum(Path(p).stat().st_size for p in spec.get('outputs', []) if Path(p).exists())
            peak_outputs = max(peak_outputs, sizes)
            cpu_s = live['cpu_s'] if live else previous_cpu
            target, sequence, explicit = budget_update(target, cpu_s, read(directory / 'control.json'), sequence)
            if explicit or (work / 'STOP').exists():
                stop_requested = True
                if stop_time is None:
                    os.killpg(child.pid, signal.SIGTERM)
                    os.killpg(child.pid, signal.SIGCONT)
                    stop_time = now
                elif now - stop_time > 10:
                    os.killpg(child.pid, signal.SIGKILL)
            resource_reasons = reasons(config, resources, live, sizes, spec['category'])
            warnings = []
            if live and live['rss_bytes'] > config['rss_warning_gib'][spec['category']] * GIB:
                warnings.append('HIGH_PROCESS_RSS_INFORMATION_ONLY')
            if sizes > config['proof_warning_gib'] * GIB:
                warnings.append('LARGE_PROOF_INFORMATION_ONLY')
            # Cake / read-only validation must still finish when writers are disk-paused.
            if not any(str(p).endswith(('.lrat', '.cnf', '.drat')) for p in spec.get('outputs', [])):
                resource_reasons = [x for x in resource_reasons if x != 'LOW_PHYSICAL_DISK']
            manual_pause = (directory / 'PAUSE').exists()
            want_pause = bool(resource_reasons or manual_pause)
            if not stop_requested and want_pause != paused:
                os.killpg(child.pid, signal.SIGSTOP if want_pause else signal.SIGCONT)
                paused = want_pause
                if paused:
                    pause_events += 1
            exceeded = cpu_s >= target
            state.update(phase='STOP_REQUESTED' if stop_requested else 'RESOURCE_PAUSED' if paused else 'RUNNING',
                         child=state['child'], target_cpu_s=target, cpu_s=cpu_s,
                         time_extension_request=(f'time limit reached. ETA unknown. Extend [seconds] ?'
                                                 if exceeded and not stop_requested else None),
                         time_budget_action='REQUEST_ONLY_KEEP_RUNNING',
                         resources=resources, resource_reasons=resource_reasons, resource_warnings=warnings,
                         manual_pause=manual_pause, output_bytes=sizes, peak_output_bytes=peak_outputs,
                         peak_rss_bytes=peak_rss, updated_unix=time.time(), control_sequence=sequence,
                         eta=None, eta_scope='No prediction of SAT/UNSAT or checker completion')
            current = cpu_clock()
            total_busy = busy_cpu(previous, current)
            elapsed = max(0.001, now - proof_previous_time)
            own_busy = max(0, cpu_s - previous_cpu) / elapsed
            background_sum += max(0, total_busy - own_busy)
            background_n += 1
            state['mean_background_cpu_equivalents'] = background_sum / background_n
            state['proof_growth_bytes_per_second'] = max(0, sizes - proof_previous_size) / elapsed
            previous, previous_cpu = current, cpu_s
            proof_previous_size, proof_previous_time = sizes, now
            if now - last_checkpoint >= config['checkpoint_s']:
                state['proof_counters'] = [counter.sample() for counter in counters]
                for telemetry in state['proof_counters']:
                    telemetry['prefix_additions_per_cpu_hour'] = telemetry['complete_addition_records_in_scanned_prefix'] * 3600 / max(cpu_s, 0.001)
                    telemetry['file_bytes_per_cpu_hour'] = telemetry['file_bytes'] * 3600 / max(cpu_s, 0.001)
                save(directory / 'state.json', state)
                last_checkpoint = now
            # Lightweight OS samples only; no /proc/mem attach or memory probes.
            if now - last_status >= config['status_s']:
                with (directory / 'resources.jsonl').open('a') as stream:
                    stream.write(json.dumps(state) + '\n')
                last_status = now
            from datetime import datetime
            from zoneinfo import ZoneInfo
            stamp = datetime.now(ZoneInfo(config['timezone']))
            slot = stamp.strftime('%Y-%m-%dT%H')
            if stamp.hour in (8, 14, 20) and stamp.minute == 0 and slot != last_detail:
                # Read tail of normal progress log; no instrumentation of running binary.
                with (directory / 'output.log').open('rb') as stream:
                    stream.seek(max(0, stream.seek(0, 2) - 8192))
                    tail = stream.read().decode(errors='replace')
                save(directory / ('progress_' + stamp.strftime('%Y%m%d_%H00') + '.json'),
                     {'local_time': stamp.isoformat(), 'state': state, 'log_tail': tail})
                last_detail = slot
            time.sleep(config['poll_s'])
        state.update(phase='FINALIZING', child=None, cpu_s=usage.ru_utime + usage.ru_stime)
        save(directory / 'state.json', state)
        require(inputs == [identity(path) for path in spec.get('inputs', [])], 'INPUT_CHANGED_DURING_JOB')
        outputs = [identity(path) for path in spec.get('outputs', []) if Path(path).is_file()]
        result = {'id': spec['id'], 'command': spec['command'], 'category': spec['category'],
                  'returncode': child.returncode, 'reason': 'EXPLICIT_STOP' if stop_requested else None,
                  'cpu_seconds': usage.ru_utime + usage.ru_stime,
                  'supervisor_cpu_seconds': time.process_time() - start_self_cpu,
                  'max_rss_kib': usage.ru_maxrss, 'started_unix': started, 'finished_unix': time.time(),
                  'mean_background_cpu_equivalents': background_sum / max(1, background_n),
                  'target_cpu_s': target, 'inputs': inputs, 'outputs': outputs,
                  'resource_pause_events': pause_events,
                  'proof_counters': [counter.result() for counter in counters],
                  'peak_output_bytes': max(peak_outputs, sum(p['bytes'] for p in outputs)),
                  'log': identity(directory / 'output.log'), 'supervisor': state['supervisor']}
        save(directory / 'result.json', result)
        save(directory / 'state.json', {**state, 'phase': 'FINISHED', 'child': None,
                                       'returncode': child.returncode, 'time_extension_request': None})
    except BaseException as error:
        # Expensive child survives a supervisor failure, but is deliberately paused.
        if child and child.returncode is None:
            try:
                os.killpg(child.pid, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        state.update(phase='ERROR_PRESERVED', error=repr(error), updated_unix=time.time())
        save(directory / 'state.json', state)
        raise


if __name__ == '__main__':
    run(sys.argv[1])
