"""Independent, reconnectable monitoring. Never sends signals to research jobs."""
import fcntl
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from common import alive, host, lock, proc, read, save


def stamp(t):
    return datetime.fromtimestamp(t, ZoneInfo('Europe/Berlin')).strftime('%y.%m.%d %H.%M.%S')


def emit(work, kind, **details):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    event = {'time': time.time(), 'event': kind, **details}
    with (work / 'events.jsonl').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.write(json.dumps(event, ensure_ascii=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return event


def finite_eta(done, total, elapsed):
    # Only for bounded, comparable work units; never infer SAT completion from cases solved.
    if done <= 0 or elapsed <= 0:
        return {'seconds': None, 'reason': 'Noch keine gemessene Rate.'}
    seconds = max(0, total - done) * elapsed / done
    return {'seconds': seconds, 'basis': f'{done}/{total} Einheiten in {elapsed:.1f}s',
            'uncertainty': 'Grobe Phasenhochrechnung; unterschiedliche Einheiten können abweichen.'}


def solver_tail(path):
    """Bounded normal-log tail; raw CaDiCaL reports retain their own header/units."""
    if not path.exists():
        return {'bytes': 0, 'tail': []}
    with path.open('rb') as stream:
        header_lines = stream.read(65536).decode(errors='replace').splitlines()
        header = [line for line in header_lines if any(word in line for word in ('seconds  reduction conflicts', 'MB    restarts', 'level     rate'))]
        size = stream.seek(0, 2)
        stream.seek(max(0, size - 16384))
        lines = stream.read().decode(errors='replace').replace('\r', '\n').splitlines()
    return {'header': header, 'bytes': size, 'tail': [s for s in lines if s.startswith('c ')][-6:]}


def snapshot(root, started, previous=None, now=None):
    now = time.time() if now is None else now
    work = root / 'work'
    status = read(work / 'status.json', {})
    tasks = status.get('tasks', {})
    complete = {'UNSAT_CERTIFIED', 'INTERFACE_VERIFIED_ONLY', 'GRAPH_VERIFIED'}
    jobs, cpu, proof, latest = {}, 0.0, 0, None
    for d in sorted((work / 'jobs').glob('*')):
        if not d.is_dir():
            continue
        state = read(d / 'state.json', {})
        result = read(d / 'result.json')
        cpu += result['cpu_seconds'] if result else state.get('cpu_s', 0)
        proof += result.get('peak_output_bytes', 0) if result else state.get('output_bytes', 0)
        if result:
            latest = max(latest or 0, result.get('finished_unix', 0))
            continue
        launch = read(d / 'launch.json', {})
        child = state.get('child')
        live = proc(child['pid']) if child and alive(child) else None
        io = (live or {}).get('io', {})
        log = solver_tail(d / 'output.log')
        old = (previous or {}).get('jobs', {}).get(d.name, {})
        cpu_delta = state.get('cpu_s', 0) - old.get('cpu_s', 0)
        proof_delta = state.get('output_bytes', 0) - old.get('proof_bytes', 0)
        counters = state.get('proof_counters', [])
        additions = sum(c.get('complete_addition_records_in_scanned_prefix', 0) for c in counters)
        jobs[d.name] = {'phase': state.get('phase', 'STARTING'), 'cpu_s': state.get('cpu_s', 0),
            'wall_s': now - launch.get('started_unix', now), 'cpu_delta_s': cpu_delta,
            'proof_bytes': state.get('output_bytes', 0), 'proof_delta_bytes': proof_delta,
            'prefix_additions': additions, 'prefix_additions_delta': additions - old.get('prefix_additions', 0),
            'proof_counters': counters, 'log': log,
            'rss_bytes': (live or child or {}).get('rss_bytes'),
            'io': io, 'read_chars_delta': io.get('rchar', 0) - old.get('io', {}).get('rchar', 0),
            'telemetry_age_s': now - state.get('updated_unix', launch.get('started_unix', now)),
            'supervisor_alive': alive(state.get('supervisor')), 'child_alive': alive(child),
            'pause_reasons': state.get('resource_reasons', []) + (['MANUAL'] if state.get('manual_pause') else []),
            'warnings': state.get('resource_warnings', []),
            'budget_request': state.get('time_extension_request'),
            'activity': ('PAUSIERT' if 'PAUSED' in state.get('phase', '') else
                         'CPU/Proof aktiv; noch kein Abschluss' if cpu_delta > 0 or proof_delta > 0 else
                         'Keine gemessene CPU-/Proofänderung; Zustand prüfen'),
            'eta': {'seconds': None, 'reason': 'Unbekannter Suchraum / keine belastbare Restarbeitsgröße; Proofgröße und gelöste Fälle sind keine Abschlussprognose.'}}
    try:
        resources = host(work)
        oldres = (previous or {}).get('resources', {})
        elapsed = max(.001, now - (previous or {}).get('time', now))
        resources['swap_in_pages_per_s'] = ((resources['swap_in_pages'] - oldres['swap_in_pages']) / elapsed if 'swap_in_pages' in oldres else None)
        resources['swap_out_pages_per_s'] = ((resources['swap_out_pages'] - oldres['swap_out_pages']) / elapsed if 'swap_out_pages' in oldres else None)
    except Exception as error:
        resources = {'error': repr(error)}
    finished = sum(v in complete for v in tasks.values())
    return {'time': now, 'wall_s': now - started, 'phase': status.get('status', 'INITIALISIERUNG'),
            'stage': status.get('stage'), 'done': finished, 'known_total': len(tasks) or None,
            'open': sum(v not in complete for v in tasks.values()), 'active_jobs': len(jobs),
            'cpu_s': cpu, 'cpu_delta_s': cpu - (previous or {}).get('cpu_s', 0),
            'done_delta': finished - (previous or {}).get('done', 0), 'proof_bytes': proof,
            'proof_delta_bytes': proof - (previous or {}).get('proof_bytes', 0),
            'since_last_result_s': now - latest if latest else None,
            'jobs': jobs, 'resources': resources,
            'eta': {'seconds': None, 'scope': 'Abschluss der Pilotstufe',
                    'reason': 'SAT/UNSAT-Laufzeiten und nachfolgende Prüfzeiten unbekannt; offene Fälle werden nicht aus der Rate bereits gelöster Fälle hochgerechnet.'}}


def render(e):
    prefix = stamp(e['time']) + ' — ' + e['event']
    if e['event'] != 'HEARTBEAT':
        return prefix + ' ' + json.dumps({k:v for k,v in e.items() if k not in ('time','event')}, ensure_ascii=False)
    s = e['snapshot']; r = s['resources']
    lines = [prefix + f" | Phase {s['phase']} / {s['stage']} | Laufzeit {s['wall_s']/3600:.2f}h | CPU {s['cpu_s']/3600:.2f}h (+{s['cpu_delta_s']:.1f}s)",
        f"  Fälle fertig {s['done']}/{s['known_total']} (+{s['done_delta']}), offen {s['open']}, aktive Jobs {s['active_jobs']}; Zeit seit letztem Jobresultat: {s['since_last_result_s']}",
        f"  ETA unbekannt ({s['eta']['scope']}): {s['eta']['reason']}",
        f"  Nächster Heartbeat: {stamp(e['next_heartbeat_unix'])} (Kontrollzeitpunkt, keine Abschluss-ETA)",
        '  Ressourcen: ' + json.dumps(r, ensure_ascii=False)]
    for name, j in s['jobs'].items():
        lines += [f"  {name}: {j['phase']}; {j['activity']}; CPU +{j['cpu_delta_s']:.1f}s; Proof +{j['proof_delta_bytes']} Bytes; gescannte Additionen +{j['prefix_additions_delta']}; RSS {j['rss_bytes']}; Telemetrie {j['telemetry_age_s']:.1f}s alt",
                  f"    Pause {j['pause_reasons']}; Warnungen {j['warnings']}; Budget {j['budget_request']}; ETA unbekannt."]
        if not j['supervisor_alive'] or j['telemetry_age_s'] > 60:
            lines += ['    WARNUNG: Supervisor fehlt oder Telemetrie veraltet; Fortschritt nicht bestätigt.']
        lines += [f"    Gelesene Bytes (Systemaufrufe) +{j['read_chars_delta']}; I/O-Aktivität ist kein verifizierter Proof-Fortschritt."]
        lines += ['    Log: ' + line for line in j['log'].get('header', []) + j['log']['tail']]
    return '\n'.join(lines)


def observe(root, started):
    root = Path(root); work = root / 'work'
    held = lock(work / 'observer.lock')
    save(work / 'observer.json', {'process': proc(os.getpid()), 'started_unix': started})
    previous, due, absent_since = None, 0, None
    emit(work, 'MONITOR_STARTED', interval_s=read(root / 'config.json').get('heartbeat_s', 900))
    while True:
        config = read(root / 'config.json')
        interval = min(900, max(.05, float(config.get('heartbeat_s', 900))))
        now = time.time()
        if time.monotonic() >= due:
            previous = snapshot(root, started, previous)
            emit(work, 'HEARTBEAT', snapshot=previous, next_heartbeat_unix=now + interval)
            save(work / 'heartbeat.json', previous)
            due = time.monotonic() + interval
        launch = read(work / 'controller_launch.json', {})
        # During startup the launch receipt may not yet exist. Allow startup grace.
        controller_alive = alive(launch.get('process'))
        unfinished = any(not (d / 'result.json').exists() for d in (work / 'jobs').glob('*') if d.is_dir())
        if not controller_alive and now - started > 2:
            if absent_since is None:
                absent_since = now
                emit(work, 'CONTROLLER_EXITED', status=read(work / 'status.json', {}).get('status'),
                     error=read(work / 'controller_error.json'), unfinished_jobs=unfinished)
            if not unfinished:
                emit(work, 'HEARTBEAT', snapshot=snapshot(root, started, previous), next_heartbeat_unix=now)
                emit(work, 'MONITOR_COMPLETE', note='Keine aktiven Jobs. Alle Ereignisse bleiben in work/events.jsonl.')
                return
        time.sleep(float(config.get('observer_poll_s', 2)))


def ensure_observer(root, started):
    import subprocess
    work = root / 'work'
    guard = lock(work / 'observer_launch.lock')
    if alive(read(work / 'observer.json', {}).get('process')):
        return
    with (work / 'observer.log').open('ab') as output:
        child = subprocess.Popen([sys.executable, '-u', str(root / 'src/monitor.py'), str(root), str(started)],
            stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(100):
        if alive(read(work / 'observer.json', {}).get('process')):
            return
        if child.poll() is not None:
            raise RuntimeError('MONITOR_START_FAILED: work/observer.log')
        time.sleep(.05)
    raise RuntimeError('MONITOR_START_UNCERTAIN: work/observer.log')


def watch(root, offset=0):
    work = root / 'work'
    print('Liveansicht: Strg+C beendet nur diese Ansicht. Rechenjobs und Monitor laufen weiter.', flush=True)
    try:
        with (work / 'events.jsonl').open('r') as stream:
            stream.seek(offset)
            last_warning = 0
            while True:
                pos = stream.tell(); line = stream.readline()
                if line and line.endswith('\n'):
                    e = json.loads(line); print(render(e), flush=True)
                    if e['event'] == 'MONITOR_COMPLETE':
                        # Old completion records must not terminate a reconnected current run.
                        if not alive(read(work / 'observer.json', {}).get('process')):
                            return
                    continue
                stream.seek(pos)
                if not alive(read(work / 'observer.json', {}).get('process')):
                    print('Monitor beendet. Bei laufenden Jobs: watch erneut aufrufen; Diagnose: work/observer.log.', flush=True)
                    return
                hb = read(work / 'heartbeat.json', {})
                if time.time() - hb.get('time', time.time()) > 960 and time.time() - last_warning > 60:
                    print('WARNUNG: Heartbeat überfällig; work/observer.log prüfen.', flush=True)
                    last_warning = time.time()
                time.sleep(.25)
    except KeyboardInterrupt:
        print('\nLiveansicht geschlossen; Berechnungen bleiben unberührt.', flush=True)


if __name__ == '__main__':
    observe(Path(sys.argv[1]), float(sys.argv[2]))
