"""Resumable no-timeout LRAT/Cake runner. Only run-owned files are modified."""
from __future__ import annotations

import concurrent.futures as cf
import fcntl
import gzip
import hashlib
import itertools
import json
import os
import shutil
import signal
import subprocess
import threading
import time
import zipfile
from pathlib import Path
from typing import Any

from k66_prepare import require, save, sha

GIB = 1024 ** 3
MARKER = b's VERIFIED UNSAT'


def memory_available() -> float:
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):
            return int(line.split()[1]) / 1024 ** 2
    raise RuntimeError('Cannot read Linux MemAvailable')


def memory_total() -> float:
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemTotal:'):
            return int(line.split()[1]) / 1024 ** 2
    raise RuntimeError('Cannot read Linux MemTotal')


def marker_present(path: Path) -> bool:
    with path.open('rb') as stream:
        return any(line.strip() == MARKER for line in stream)


def stamp() -> str:
    return time.strftime('%Y%m%d_%H%M%S') + f'_{time.time_ns() % 1000000000:09d}'


class Safety:
    def __init__(self, run: Path, disk_floor: float = 75.0, memory_floor: float = 2.0):
        self.run = run
        self.disk_floor = disk_floor
        self.memory_floor = memory_floor
        self.stop = threading.Event()
        self.processes: set[subprocess.Popen[Any]] = set()
        self.lock = threading.Lock()
        self.reason = ''

    def check(self) -> None:
        if self.stop.is_set():
            raise RuntimeError('RUN_STOPPED: ' + self.reason)
        # Proofs, terminal CNFs, solver output, and certificates are written
        # only below the run directory.  /mnt/c is used solely for the small
        # handoff ZIP, so the proof-volume safety floor must not be applied to C:.
        free = shutil.disk_usage(self.run).free / GIB
        if free < self.disk_floor:
            self.reason = f'RESOURCE_DISK {self.run}: {free:.2f} GiB < {self.disk_floor}'
            self.stop.set()
            raise RuntimeError(self.reason)
        available = memory_available()
        if available < self.memory_floor:
            self.reason = f'RESOURCE_RAM: {available:.2f} GiB < {self.memory_floor}'
            self.stop.set()
            raise RuntimeError(self.reason)

    def stop_all(self, reason: str) -> None:
        self.reason = reason
        self.stop.set()
        with self.lock:
            processes = list(self.processes)
        for process in processes:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass

    def execute(self, command: list[str], directory: Path, name: str) -> dict[str, Any]:
        self.check()
        out, err = directory / (name + '.out'), directory / (name + '.err')
        started = time.monotonic()
        environment = os.environ.copy()
        for key in ('CML_HEAP_SIZE', 'CML_STACK_SIZE'):
            environment.pop(key, None)
        with out.open('xb') as stdout, err.open('xb') as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                       start_new_session=True, env=environment)
            with self.lock:
                self.processes.add(process)
            try:
                while process.poll() is None:
                    self.check()
                    time.sleep(1)
                return_code = process.wait()
            finally:
                if process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait()
                with self.lock:
                    self.processes.discard(process)
        result = {'command': command, 'exit': return_code,
                  'wall_seconds': round(time.monotonic() - started, 3),
                  'stdout': str(out.relative_to(self.run)), 'stderr': str(err.relative_to(self.run))}
        save(directory / (name + '.json'), result)
        return result


def find_tools(home: Path, overrides: dict[str, str | None]) -> dict[str, Path]:
    preferred = {
        'cadical': [home / '.local/bin/cadical'],
        'lrat-check': [home / '.local/bin/lrat-check'],
        'cake_lpr': [home / 'conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr',
                     home / '.local/bin/cake_lpr',
                     home / 'conway99_workspace/conway99_o3_qsat_preflight_0.1.11/dependencies/bin/cake_lpr'],
    }
    found = {}
    for name, candidates in preferred.items():
        if overrides.get(name):
            candidates = [Path(str(overrides[name])).expanduser()]
        elif shutil.which(name):
            candidates.append(Path(str(shutil.which(name))))
        actual = next((p.resolve() for p in candidates if p.is_file() and os.access(p, os.X_OK)), None)
        require(actual is not None, f'Missing executable {name}; checked: {candidates}')
        found[name] = actual
    return found


def pin_tools(run: Path, tools: dict[str, Path]) -> dict[str, str]:
    location = run / 'tools'
    location.mkdir(exist_ok=True)
    record = {}
    for name, original in tools.items():
        destination = location / name
        digest = sha(original)
        if destination.exists():
            require(sha(destination) == digest, 'Resume tool differs: ' + name)
        else:
            shutil.copy2(original, destination)
            destination.chmod(0o555)
        require(sha(destination) == digest, 'Binary copy mismatch: ' + name)
        record[name] = {'original': str(original), 'frozen': str(destination), 'sha256': digest}
    file = run / 'toolchain.json'
    if file.exists():
        old = json.loads(file.read_text())
        for name in record:
            require(old[name]['sha256'] == record[name]['sha256'], 'Toolchain changed on resume')
    else:
        save(file, record)
    return {name: str(location / name) for name in tools}


def cake_command(tools: dict[str, str], cnf: Path, proof: Path, heap_mb: int) -> list[str]:
    return [tools['cake_lpr'], f'--CML_HEAP_SIZE={heap_mb}', '--CML_STACK_SIZE=4096', str(cnf), str(proof)]


def tool_controls(run: Path, tools: dict[str, str], guard: Safety, heap_mb: int) -> None:
    directory = run / ('controls_' + stamp())
    directory.mkdir()
    unsat, sat, proof = directory / 'unsat.cnf', directory / 'sat.cnf', directory / 'proof.lrat'
    unsat.write_text('p cnf 1 2\n1 0\n-1 0\n')
    sat.write_text('p cnf 1 2\n1 0\n1 0\n')
    solve = guard.execute([tools['cadical'], '--lrat', '--no-binary', str(unsat), str(proof)], directory, 'solver')
    require(solve['exit'] == 20 and proof.exists(), 'Positive-control solver failed')
    lrat = guard.execute([tools['lrat-check'], str(unsat), str(proof)], directory, 'lrat_positive')
    cake = guard.execute(cake_command(tools, unsat, proof, heap_mb), directory, 'cake_positive')
    require(lrat['exit'] == 0, 'Positive LRAT control failed')
    require(cake['exit'] == 0 and marker_present(directory / 'cake_positive.out'), 'Positive Cake control failed')
    lrat_bad = guard.execute([tools['lrat-check'], str(sat), str(proof)], directory, 'lrat_negative')
    cake_bad = guard.execute(cake_command(tools, sat, proof, heap_mb), directory, 'cake_negative')
    require(lrat_bad['exit'] != 0, 'LRAT checker accepted proof against satisfiable control CNF')
    require(not (cake_bad['exit'] == 0 and marker_present(directory / 'cake_negative.out')),
            'Cake accepted proof against satisfiable control CNF')
    save(directory / 'controls.json', {'status': 'PASS', 'wrong_formula_rejected': True,
                                      'positive_marker_required': True, 'proof_sha256': sha(proof)})
    print('TOOLCHAIN_CONTROLS_PASS positive_UNSAT_and_negative_wrong_formula', flush=True)


def read_witness(path: Path) -> dict[int, bool]:
    values = {}
    for line in path.read_text(errors='strict').splitlines():
        words = line.split()
        if not words or words[0] in ('s', 'c'):
            continue
        if words[0] == 'v':
            words = words[1:]
        for word in words:
            number = int(word)
            if number:
                require(abs(number) not in values or values[abs(number)] == (number > 0), 'Contradictory witness')
                values[abs(number)] = number > 0
    return values


def verify_sat(path: Path, units: list[int]) -> list[list[int]]:
    values = read_witness(path)
    require(all(i in values for i in range(1, 993)), 'SAT witness missing primary variables')
    require(all(values[abs(lit)] == (lit > 0) for lit in units), 'SAT witness violates case assumptions')
    p = [[0] * 32 for _ in range(32)]
    p[12][12] = p[13][13] = 2
    for variable, (i, j) in enumerate(itertools.combinations(range(32), 2), 1):
        require(not (values[variable] and values[variable + 496]), 'SAT witness violates S/L disjointness')
        p[i][j] = p[j][i] = int(values[variable]) + 2 * int(values[variable + 496])
    q = [[0] * 35 for _ in range(35)]
    for i in range(3):
        for j in range(3):
            q[i][j] = int(i != j)
        for v in range(4 * i, 4 * i + 4):
            q[i][v + 3], q[v + 3][i] = 3, 1
    for i in range(32):
        q[i + 3][3:] = p[i]
    sizes = [1] * 3 + [3] * 32
    require(all(sum(row) == 14 for row in q), 'SAT quotient row degree failure')
    for i in range(35):
        for j in range(35):
            require(sizes[i] * q[i][j] == sizes[j] * q[j][i], 'SAT quotient balance failure')
            lhs = sum(q[i][k] * q[k][j] for k in range(35)) + q[i][j]
            require(lhs == 12 * (i == j) + 2 * sizes[j], f'SAT quotient equation failure {i},{j}')
    return q


def compress_verified(proof: Path, expected: str, guard: Safety) -> dict[str, Any]:
    target = proof.with_name(proof.name + '.' + stamp() + '.gz')
    temporary = target.with_name(target.name + '.partial')
    digest = hashlib.sha256()
    size = 0
    with proof.open('rb') as source, gzip.open(temporary, 'xb', compresslevel=1) as output:
        for block in iter(lambda: source.read(1 << 20), b''):
            guard.check()
            digest.update(block)
            size += len(block)
            output.write(block)
    require(digest.hexdigest() == expected, 'Proof changed during compression')
    reread = hashlib.sha256()
    with gzip.open(temporary, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            guard.check()
            reread.update(block)
    require(reread.hexdigest() == expected, 'Compressed proof round-trip failed')
    temporary.replace(target)
    # Removal happens only after both checkers and exact compression verification.
    return {'proof_file': str(target.relative_to(guard.run)), 'proof_gz_sha256': sha(target),
            'proof_raw_sha256': expected, 'proof_raw_bytes': size, 'proof_gz_bytes': target.stat().st_size}


def completed_certificate(run: Path, job: Any, manifest_sha: str) -> dict[str, Any] | None:
    certificate = run / 'jobs' / job['id'] / 'certificate.json'
    if not certificate.exists():
        return None
    record = json.loads(certificate.read_text())
    require(record['status'] == 'UNSAT_CERTIFIED' and record['manifest_sha256'] == manifest_sha,
            'Resume certificate identity mismatch')
    require(record['cnf_sha256'] == job['cnf_sha256'], 'Resume certificate CNF mismatch')
    require(record['lrat_exit'] == record['cake_exit'] == 0 and record['cake_positive_marker'] is True,
            'Resume certificate missing positive verdicts')
    proof = run / record['proof_file']
    require(sha(proof) == record['proof_gz_sha256'], 'Archived proof changed on resume')
    for label in ('lrat', 'cake'):
        output = run / record[label + '_stdout']
        require(sha(output) == record[label + '_stdout_sha256'], 'Checker log changed')
    require(marker_present(run / record['cake_stdout']), 'Stored Cake marker absent')
    return record


def run_job(run: Path, job: Any, tools: Any, guard: Safety, checker_lock: threading.Lock,
            checker_waiting: threading.Event, heap_mb: int, manifest_sha: str) -> dict[str, Any]:
    folder = run / 'jobs' / job['id']
    cnf = folder / 'leaf.cnf'
    require(sha(cnf) == job['cnf_sha256'], 'Terminal CNF changed before solve')
    attempt = None
    solved = None
    for previous in sorted(folder.glob('attempt_*'), reverse=True):
        file = previous / 'solve_complete.json'
        if not file.exists():
            continue
        candidate = json.loads(file.read_text())
        raw = previous / 'proof.lrat'
        if candidate.get('exit') == 20 and candidate.get('cnf_sha256') == job['cnf_sha256'] and raw.exists():
            require(sha(raw) == candidate['proof_raw_sha256'], 'Stored unfinished-check proof changed')
            attempt, solved = previous, candidate
            break
    if attempt is None:
        attempt = folder / ('attempt_' + stamp())
        attempt.mkdir()
        proof, witness = attempt / 'proof.lrat', attempt / 'witness.out'
        solved = guard.execute([tools['cadical'], '--lrat', '--no-binary', '-w', str(witness),
                                str(cnf), str(proof)], attempt, 'solver')
        if solved['exit'] == 10:
            quotient = verify_sat(witness, job['units'])
            save(attempt / 'quotient_Q.json', quotient)
            result = {'id': job['id'], 'status': 'SAT_QUOTIENT_VERIFIED',
                      'cnf_sha256': job['cnf_sha256'], 'solver': solved,
                      'scope': 'Verified quotient witness only, not an SRG lift'}
            save(folder / 'sat_result.json', result)
            return result
        require(solved['exit'] == 20, f'{job["id"]}: unexpected solver exit {solved["exit"]}')
        require(proof.is_file(), 'UNSAT proof missing')
        solved.update({'cnf_sha256': job['cnf_sha256'], 'proof_raw_sha256': sha(proof)})
        save(attempt / 'solve_complete.json', solved)
    proof = attempt / 'proof.lrat'
    while not checker_lock.acquire(timeout=1):
        guard.check()
    try:
        checker_waiting.set()
        need = heap_mb / 1024 + 4 + 4
        while memory_available() < need:
            guard.check()
            time.sleep(2)
        checker_waiting.clear()
        check_name = 'check_' + stamp()
        checks = attempt / check_name
        checks.mkdir()
        lrat = guard.execute([tools['lrat-check'], str(cnf), str(proof)], checks, 'lrat')
        require(lrat['exit'] == 0, f'{job["id"]}: LRAT rejection')
        current_heap = heap_mb
        while True:
            cake_name = 'cake_' + str(current_heap)
            cake = guard.execute(cake_command(tools, cnf, proof, current_heap), checks, cake_name)
            marker = marker_present(checks / (cake_name + '.out'))
            if cake['exit'] == 0 and marker:
                break
            error_text = (checks / (cake_name + '.err')).read_text(errors='replace')
            heap_ceiling = max(current_heap, int(memory_total() - 8) * 1024)
            if 'heap space exhausted' not in error_text.lower() or current_heap >= heap_ceiling:
                raise RuntimeError(f'{job["id"]}: Cake failed: exit={cake["exit"]}, marker={marker}; {error_text[-400:]}')
            current_heap = min(heap_ceiling, current_heap + 8192)
            checker_waiting.set()
            need = current_heap / 1024 + 4 + 4
            while memory_available() < need:
                guard.check()
                time.sleep(2)
            checker_waiting.clear()
        require(sha(proof) == solved['proof_raw_sha256'], 'Proof changed after checker passes')
        compressed = compress_verified(proof, solved['proof_raw_sha256'], guard)
        record = {'id': job['id'], 'status': 'UNSAT_CERTIFIED', 'manifest_sha256': manifest_sha,
                  'cnf_sha256': job['cnf_sha256'], 'solver_exit': 20,
                  'lrat_exit': 0, 'cake_exit': 0, 'cake_positive_marker': True,
                  'cake_heap_mb': current_heap, 'lrat_stdout': lrat['stdout'], 'cake_stdout': cake['stdout'],
                  'lrat_stdout_sha256': sha(run / lrat['stdout']),
                  'cake_stdout_sha256': sha(run / cake['stdout']),
                  'solver_wall_seconds': solved['wall_seconds'], **compressed}
        save(folder / 'certificate.json', record)
        proof.unlink()
        print(f'CERTIFIED {job["id"]} proof_raw_GiB={record["proof_raw_bytes"] / GIB:.3f}', flush=True)
        return record
    finally:
        checker_waiting.clear()
        checker_lock.release()


def handoff(run: Path) -> Path:
    archive = run.parent / (run.name + '_handoff_' + stamp() + '.zip')
    excluded_suffixes = {'.cnf', '.lrat', '.gz', '.pyc', '.partial'}
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(run.rglob('*')):
            if not path.is_file() or path.suffix in excluded_suffixes or 'tools' in path.relative_to(run).parts:
                continue
            if path.name.endswith('.lock') or '__pycache__' in path.parts:
                continue
            name = str(path.relative_to(run))
            if path.stat().st_size <= 2 * 1024 * 1024:
                output.write(path, name)
            elif path.suffix in {'.out', '.err', '.log'}:
                with path.open('rb') as stream:
                    stream.seek(-2 * 1024 * 1024, os.SEEK_END)
                    output.writestr(name + '.tail', stream.read())
    downloads = Path('/mnt/c/Users/rb/Downloads')
    if downloads.is_dir():
        target = downloads / archive.name
        with archive.open('rb') as source, target.open('xb') as destination:
            shutil.copyfileobj(source, destination)
        require(sha(target) == sha(archive), 'Windows handoff copy hash mismatch')
        print('HANDOFF_WINDOWS ' + str(target), flush=True)
    print('HANDOFF ' + str(archive), flush=True)
    return archive


def execute_pilot(run: Path, manifest: Any, tools: Any, workers: int = 8, heap_mb: int = 16384,
                  disk_floor: float = 75.0, status_seconds: float = 600.0) -> None:
    require(1 <= workers <= 8, 'Use 1..8 solver lanes for this pilot')
    guard = Safety(run, disk_floor=disk_floor)
    # With 48 GiB WSL, reserve the configured checker budget plus 4 GiB headroom.
    require(memory_available() >= heap_mb / 1024 + 8, 'Insufficient free RAM for configured checker admission')
    guard.check()
    manifest_sha = sha(run / 'manifest.json')
    records = {}
    for job in manifest['jobs']:
        record = completed_certificate(run, job, manifest_sha)
        if record:
            records[job['id']] = record
    queue = [job for job in manifest['jobs'] if job['id'] not in records]
    lock = threading.Lock()
    checker_waiting = threading.Event()
    state = {'status': 'RUNNING', 'case': manifest['case_id'], 'manifest_sha256': manifest_sha,
             'certified': len(records), 'total': 23, 'solver_workers': workers, 'checker_workers': 1,
             'wallclock_timeout': None, 'proof_size_cap': None, 'disk_floor_gib': disk_floor,
             'memory_floor_gib': 2.0, 'started_at': time.time()}
    pool = cf.ThreadPoolExecutor(max_workers=workers)
    futures: dict[Any, Any] = {}
    started = time.monotonic()
    last = started
    original_certified = len(records)
    try:
        tool_controls(run, tools, guard, heap_mb)
        print('K66_PILOT_START 23_cases solver_lanes<=8 checker_lane=1 timeouts=NONE ETA=unknown', flush=True)
        while queue or futures:
            guard.check()
            for future in list(futures):
                if not future.done():
                    continue
                job = futures.pop(future)
                record = future.result()
                if record['status'] == 'SAT_QUOTIENT_VERIFIED':
                    state['status'] = 'SAT_QUOTIENT_VERIFIED'
                    state['sat_job'] = job['id']
                    guard.stop_all('Verified quotient found; preserve witness and stop other work')
                    queue.clear()
                    raise RuntimeError('SAT_QUOTIENT_FOUND: retained quotient needs project review, not an SRG claim')
                records[job['id']] = record
            # Memory admission pauses NEW solvers only; it does not time out active work.
            if queue and len(futures) < workers and not checker_waiting.is_set():
                if memory_available() >= heap_mb / 1024 + 8 and shutil.disk_usage(run).free / GIB > disk_floor + 5:
                    job = queue.pop(0)
                    future = pool.submit(run_job, run, job, tools, guard, lock, checker_waiting, heap_mb, manifest_sha)
                    futures[future] = job
            now = time.monotonic()
            state.update({'certified': len(records), 'active_or_checking': len(futures),
                          'pending': len(queue), 'elapsed_seconds': round(now - started, 1),
                          'mem_available_gib': round(memory_available(), 2),
                          'disk_free_gib': round(shutil.disk_usage(run).free / GIB, 2),
                          'checker_waiting_for_ram': checker_waiting.is_set(),
                          'admission': 'WAIT_CHECKER_RAM' if checker_waiting.is_set() else
                                       ('WAIT_RAM' if memory_available() < heap_mb / 1024 + 8 else
                                        ('WAIT_DISK' if shutil.disk_usage(run).free / GIB <= disk_floor + 5 else 'OPEN')),
                          'certified_ids': sorted(records)})
            save(run / 'state.json', state)
            if now - last >= status_seconds:
                fresh = len(records) - original_certified
                eta = f'{(now - started) * (23 - len(records)) / fresh / 3600:.2f}h_throughput_estimate_not_bound' if fresh else 'unknown'
                print(f'STATUS certified={len(records)}/23 active={len(futures)} pending={len(queue)} '
                      f'RAM_free={state["mem_available_gib"]}GiB disk_free={state["disk_free_gib"]}GiB '
                      f'admission={state["admission"]} checker_RAM_wait={checker_waiting.is_set()} ETA={eta}', flush=True)
                last = now
            time.sleep(1)
        require(len(records) == 23, 'Missing terminal certificates')
        state['status'] = 'ALL_23_UNSAT_CERTIFIED_MIXED_COVERAGE_READY'
        state['scope'] = 'k66 only: 223 arithmetic witnesses plus 23 LRAT/Cake certificates; no monolithic LRAT proof and no global SRG claim'
        print('K66_PILOT_COMPLETE 23/23_UNSAT_CERTIFIED arithmetic=223 mixed_coverage=246/246', flush=True)
    except BaseException as exc:
        if state['status'] != 'SAT_QUOTIENT_VERIFIED':
            state['status'] = 'INTERRUPTED' if isinstance(exc, KeyboardInterrupt) else 'ERROR_OR_RESOURCE_STOP'
        state['error'] = repr(exc)
        guard.stop_all(repr(exc))
        print('K66_PILOT_STOP ' + repr(exc), flush=True)
        raise
    finally:
        if futures:
            guard.stop_all(guard.reason or 'Run finalization')
        pool.shutdown(wait=True, cancel_futures=True)
        state['certified'] = sum((run / 'jobs' / j['id'] / 'certificate.json').exists() for j in manifest['jobs'])
        state['finished_at'] = time.time()
        save(run / 'state.json', state)
        handoff(run)
