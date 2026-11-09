"""C2B1 durable batch transactions; whole-case closure is exclusively external.
A successful subset audit is never a global case exclusion. Linux only.
"""
from pathlib import Path
from contextlib import ExitStack
import ctypes
import fcntl
import gzip
import hashlib
import json
import os
import resource
import signal
import subprocess
import time
import uuid
from resource_sensor import Sensor

BASE = Path(__file__).resolve().parent
NAMES = ('model.txt', 'action.txt', 'batch-engine', 'batch-verify', 'blocks.txt')
GLOBAL_LOCK = BASE.parent / 'C2_BatchRecoveryIncremental_20261107/research.lock'


def require(test, message):
    if not test:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    return sha(Path(path).read_bytes())


def read(path):
    return json.loads(Path(path).read_text())


def durable_new(path, data):
    """Atomically publish without replacing any previous evidence."""
    path = Path(path)
    temp = path.parent / ('.pending-' + uuid.uuid4().hex)
    with temp.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.link(temp, path)
    finally:
        temp.unlink()
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def mkdir_durable(path):
    path = Path(path)
    path.mkdir(exist_ok=False)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def write(path, value):
    durable_new(path, canonical(value))


def safe_root(root):
    root = Path(root).resolve()
    require(BASE in root.parents, 'Research output must stay in isolated workspace')
    return root


def initialise(root, label, total, tasks, sources, binding=None):
    root = safe_root(root)
    require(type(total) is int and total > 0, 'Bad total')
    require(tasks and len(set(tasks)) == len(tasks), 'Empty/duplicate task list')
    require(all(type(i) is int and 0 <= i < total for i in tasks), 'Bad task index')
    mkdir_durable(root)
    mkdir_durable(root / 'receipts')
    mkdir_durable(root / 'attempts')
    for name in NAMES:
        durable_new(root / name, Path(sources[name]).read_bytes())
        if name.startswith('batch-'):
            (root / name).chmod(0o755)
    tokens = iter(map(int,(root/'model.txt').read_text().split()))
    n,c = next(tokens),next(tokens)
    for _ in range(c+2*n*n): next(tokens)
    for _ in range(n):
        for __ in range(next(tokens)): next(tokens)
    count = next(tokens)
    masks = [[next(tokens),next(tokens)] for _ in range(count)]
    require(count == total,'Boundary total mismatch')
    contract = dict(binding=binding or {'case':None,'scope':'SYNTHETIC_OR_BOUNDED_TEST'}, masks=masks, schema='C2B1_DURABLE_BATCH_V1', label=label, total=total,
                    tasks=tasks, files={n: digest(root / n) for n in NAMES},
                    controller_sha256=digest(__file__), sensor_sha256=digest(BASE / 'resource_sensor.py'),
                    scope='BOUNDED_RESEARCH_SUBSET_NOT_GLOBAL_EXCLUSION')
    write(root / 'contract.json', contract)
    return contract


def check_contract(root):
    contract = read(root / 'contract.json')
    require(contract['schema'] == 'C2B1_DURABLE_BATCH_V1', 'Wrong schema')
    require(contract['controller_sha256'] == digest(__file__), 'Controller changed')
    require(contract['sensor_sha256'] == digest(BASE / 'resource_sensor.py'), 'Sensor changed')
    for name in NAMES:
        require(not (root / name).is_symlink(), 'Symlink bundle')
        require(digest(root / name) == contract['files'][name], 'Changed ' + name)
    return contract, sha(canonical(contract))


def payload(raw, index):
    require(len(raw) >= 8 and raw[:4] == b'C2B1', 'Wrong proof format')
    require(int.from_bytes(raw[4:8], 'little') == index, 'Wrong proof index')


def load_receipts(root, contract, context, selected=None):
    records = {}
    if selected is None:
        paths = sorted((root / 'receipts').glob('*.json'))
    else:
        require(len(set(selected)) == len(selected), 'Duplicate selected receipts')
        paths = [root / 'receipts' / f'{i:05d}.json' for i in selected]
    for path in paths:
        item = read(path)
        i = item['boundary']
        require(type(i) is int and i in contract['tasks'], 'Unexpected receipt index')
        require(path.name == f'{i:05d}.json' and i not in records, 'Duplicate/misnamed receipt')
        require(item['context'] == context and item['status'] == 'VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT', 'Wrong receipt binding')
        require(item['case'] == contract['binding']['case'] and item['masks'] == contract['masks'][i], 'Wrong case/masks')
        require(item['format'] == 'C2B1', 'Wrong receipt format')
        attempt = item['attempt']
        require(len(attempt) == 32 and all(c in '0123456789abcdef' for c in attempt), 'Bad attempt name')
        folder = root / 'attempts' / attempt
        checked = folder / 'checked.json'
        require(digest(checked) == item['checked_sha256'], 'Changed replay receipt')
        replay = read(checked)
        require(replay['context'] == context and replay['returncode'] == 0, 'Unsuccessful replay')
        require(digest(folder / 'verify.log') == replay['log_sha256'], 'Changed replay log')
        require(replay['proofs'][str(i)] == item['proof_sha256'], 'Proof absent from replay')
        native = folder / 'snapshot' / f'boundary_{i}.verified.json'
        require(digest(native) == replay['native_receipts'][str(i)], 'Changed native replay receipt')
        require(read(native) == dict(boundary=i, status='VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT', format='C2B1'), 'Wrong native decision')
        raw = (folder / 'snapshot' / f'boundary_{i}.proof').read_bytes()
        require(sha(raw) == item['proof_sha256'], 'Changed replay input')
        packed = (root / 'receipts' / f'{i:05d}.proof.gz').read_bytes()
        require(sha(packed) == item['compressed_sha256'], 'Changed compressed proof')
        require(len(raw) == item['proof_bytes'] and len(packed) == item['compressed_bytes'], 'Changed length')
        require(gzip.decompress(packed) == raw, 'Changed raw proof')
        payload(raw, i)
        records[i] = item
    return records


def child_limits(parent):
    # A killed controller cannot leave a long-running producer behind.
    libc = ctypes.CDLL(None)
    require(libc.prctl(1, signal.SIGKILL) == 0, 'Cannot bind child lifetime')
    if os.getppid() != parent:
        os.kill(os.getpid(), signal.SIGKILL)
    os.nice(max(0,15-os.getpriority(os.PRIO_PROCESS,0)))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_FSIZE, (128 * 1024**2, 128 * 1024**2))


def stage(arguments, log, sensor):
    sample, reasons = sensor.resources()
    require(not reasons, 'RESOURCE_HOLD: ' + repr((sample, reasons)))
    parent = os.getpid()
    begin = time.monotonic()
    with log.open('xb') as stream:
        process = subprocess.Popen(list(map(str, arguments)), stdin=subprocess.DEVNULL,
                                   stdout=stream, stderr=subprocess.STDOUT, start_new_session=True,
                                   preexec_fn=lambda: child_limits(parent))
        try:
            while process.poll() is None:
                time.sleep(0.05)
                _, reasons = sensor.resources()
                require(not reasons, 'RESOURCE_HOLD: ' + repr(reasons))
                require(time.monotonic() - begin < 200, 'Stage watchdog')
            code = process.returncode
            stream.flush()
            os.fsync(stream.fileno())
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    return dict(returncode=code, seconds=time.monotonic() - begin, log_sha256=digest(log))


def validate_sat(root, index, witness):
    """Original supplied full matrix contract; not a global C2 witness claim."""
    numbers = iter(map(int, (root / 'model.txt').read_text().split()))
    n, c = next(numbers), next(numbers)
    perm = [next(numbers) for _ in range(c)]
    g = [[next(numbers) for _ in range(n)] for _ in range(n)]
    k = [[next(numbers) for _ in range(n)] for _ in range(n)]
    domains = [[next(numbers) for _ in range(next(numbers))] for _ in range(n)]
    boundaries = [(next(numbers), next(numbers)) for _ in range(next(numbers))]
    require(len(witness) == n and all(type(x) is int for x in witness), 'Bad SAT rows')
    require(tuple(witness[:2]) == boundaries[index], 'Bad SAT boundary')
    require(all(x in domains[r] for r, x in enumerate(witness)), 'SAT outside domains')
    images = [sum(1 << perm[b] for b in range(c) if x >> b & 1) for x in witness]
    require(all((witness[r] & witness[s]).bit_count() == g[r][s] and
                (witness[r] & images[s]).bit_count() == k[r][s]
                for r in range(n) for s in range(n)), 'SAT violates matrices')
    require(all(sum(x >> b & 1 for x in witness) == 2 for b in range(c)), 'SAT violates column sums')


def certify(root, source, indices, context, sensor, hook):
    """Snapshot only after producer exit; full successful replay before any commit."""
    if not indices:
        return
    attempt = uuid.uuid4().hex
    folder = root / 'attempts' / attempt
    mkdir_durable(folder)
    snapshot = folder / 'snapshot'
    mkdir_durable(snapshot)
    hashes = {}
    for i in indices:
        raw = (source / f'boundary_{i}.proof').read_bytes()
        payload(raw, i)
        durable_new(snapshot / f'boundary_{i}.proof', raw)
        hashes[str(i)] = sha(raw)
    write(folder / 'replay_intent.json', dict(context=context, tasks=indices, proofs=hashes))
    hook('snapshot', None)
    result = stage([root / 'batch-verify', root / 'model.txt', ','.join(map(str, indices)),
                    snapshot, root / 'action.txt', root / 'blocks.txt'], folder / 'verify.log', sensor)
    require(result['returncode'] == 0, 'Independent replay rejected batch; no new receipts')
    for i in indices:
        require(digest(snapshot / f'boundary_{i}.proof') == hashes[str(i)], 'Replay input changed')
    # Recheck executable/model/action/controller binding before committing results.
    _, current = check_contract(root)
    require(current == context, 'Context changed during replay')
    native_hashes = {}
    for i in indices:
        native = snapshot / f'boundary_{i}.verified.json'
        require(read(native) == dict(boundary=i, status='VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT', format='C2B1'), 'Missing native decision')
        native_hashes[str(i)] = digest(native)
    result.update(context=context, tasks=indices, proofs=hashes, native_receipts=native_hashes)
    write(folder / 'checked.json', result)
    hook('checked', None)
    for i in indices:
        raw = (snapshot / f'boundary_{i}.proof').read_bytes()
        require(sha(raw) == hashes[str(i)], 'Proof changed before commit')
        packed = gzip.compress(raw, compresslevel=1, mtime=0)
        require(gzip.decompress(packed) == raw, 'Compression mismatch')
        destination = root / 'receipts' / f'{i:05d}.proof.gz'
        if destination.exists():
            require(destination.read_bytes() == packed, 'Conflicting orphan proof')
        else:
            durable_new(destination, packed)
        hook('packed', i)
        contract,_ = check_contract(root)
        record = dict(case=contract['binding']['case'],masks=contract['masks'][i],format='C2B1',boundary=i, status='VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT', context=context,
                      attempt=attempt, checked_sha256=digest(folder / 'checked.json'),
                      proof_sha256=sha(raw), compressed_sha256=sha(packed),
                      proof_bytes=len(raw), compressed_bytes=len(packed))
        write(root / 'receipts' / f'{i:05d}.json', record)
        hook('committed', i)


def run(root, chunk_size=3, seconds=60, hook=lambda phase, index: None, sensor=None, batch_limit=None):
    root = safe_root(root)
    require(type(chunk_size) is int and 1 <= chunk_size <= 8, 'Chunk must be bounded')
    require(not any(x.is_symlink() for x in root.rglob('*')), 'Symlink in output bundle')
    require(not (GLOBAL_LOCK).is_symlink(), 'Symlink global lock')
    require(type(seconds) in (int, float) and 0 <= seconds <= 60, 'Invalid task budget')
    require(batch_limit is None or type(batch_limit) is int and batch_limit > 0, 'Invalid batch limit')
    locks = ExitStack()
    try:
        global_lock = locks.enter_context((GLOBAL_LOCK).open('a+b'))
        fcntl.flock(global_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock = locks.enter_context((root / 'controller.lock').open('a+b'))
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        contract, context = check_contract(root)
        records = load_receipts(root, contract, context)
        sensor = sensor or Sensor(root)
        stop = root / 'STOP.json'
        if stop.exists():
            return dict(state='STOPPED', verified=sorted(records), stop=read(stop))
        # Reuse only closed search attempts with durable return records. Never trust
        # partial output from a crashed or still-running producer.
        for previous in sorted((root / 'attempts').iterdir()):
            ready = previous / 'search_closed.json'
            if not ready.exists():
                require(not (previous / 'search_intent.json').exists(), 'UNRESOLVED_SEARCH: inspect failed producer before further search')
                continue
            old = read(ready)
            require(old['context'] == context, 'Foreign recovery attempt')
            intent = read(previous / 'search_intent.json')
            require(intent['context'] == context, 'Foreign search intent')
            require(old['candidates'] == intent['tasks'][:len(old['candidates'])], 'Candidates not ordered prefix')
            require(len(set(old['candidates'])) == len(old['candidates']), 'Duplicate candidates')
            require(old['result']['returncode'] in (0, 10, 20), 'Unsuccessful recovery search')
            require(digest(previous / 'search.log') == old['result']['log_sha256'], 'Changed search log')
            indices = [i for i in old['candidates'] if i not in records]
            for i in indices:
                require(i in contract['tasks'], 'Recovery index outside contract')
                require(digest(previous / f'boundary_{i}.proof') == old['proofs'][str(i)], 'Recovery proof changed')
            certify(root, previous, indices, context, sensor, hook)
            records.update(load_receipts(root, contract, context, indices))
            if old['stop']:
                write(stop, old['stop'])
                return dict(state='STOPPED', verified=sorted(records), stop=old['stop'])
        pending = [i for i in contract['tasks'] if i not in records]
        completed_batches = 0
        while pending:
            tasks = pending[:chunk_size]
            folder = root / 'attempts' / uuid.uuid4().hex
            mkdir_durable(folder)
            write(folder / 'search_intent.json', dict(context=context, tasks=tasks))
            result = stage([root / 'batch-engine', root / 'model.txt', ','.join(map(str, tasks)),
                            folder, seconds, root / 'action.txt', root / 'blocks.txt'], folder / 'search.log', sensor)
            hook('search_exit', None)
            require(result['returncode'] in (0, 10, 20), 'Search process failed; preserve attempt')
            candidates, stop_reason = [], None
            for i in tasks:
                report = read(folder / f'boundary_{i}.json')
                require(type(report['boundary']) is int and report['boundary'] == i, 'Report index mismatch')
                if report['status'] == 'CANONICALLY_RESTRICTED_UNSAT_CANDIDATE':
                    candidates.append(i)
                elif report['status'] == 'SAT_CANDIDATE':
                    require(result['returncode'] == 10, 'SAT/exit mismatch')
                    validate_sat(root, i, report['rows'])
                    stop_reason = dict(boundary=i, reason='SAT_VALIDATED_AGAINST_SUPPLIED_MATRIX',
                                       report_sha256=digest(folder / f'boundary_{i}.json'),
                                       attempt=folder.name, context=context, global_C2_witness=False)
                    break
                elif report['status'] == 'UNKNOWN':
                    require(result['returncode'] == 0, 'UNKNOWN/exit mismatch')
                    stop_reason = dict(boundary=i, reason='UNKNOWN', attempt=folder.name, context=context)
                    break
                else:
                    raise RuntimeError('Invalid search status')
            require((result['returncode'] == 20) == (stop_reason is None), 'Incomplete successful batch')
            write(folder / 'search_closed.json', dict(context=context, candidates=candidates,
                  proofs={str(i): digest(folder / f'boundary_{i}.proof') for i in candidates},
                  stop=stop_reason, result=result))
            hook('search_closed', None)
            certify(root, folder, candidates, context, sensor, hook)
            records.update(load_receipts(root, contract, context, candidates))
            if stop_reason:
                write(stop, stop_reason)
                return dict(state='STOPPED', verified=sorted(records), stop=stop_reason)
            pending = [i for i in contract['tasks'] if i not in records]
            completed_batches += 1
            if batch_limit is not None and completed_batches >= batch_limit and pending:
                return dict(state='INCOMPLETE_CHECKPOINT',verified=sorted(records),global_exclusion=False)
            print('Verified restricted boundaries: '+str(len(records))+'/'+str(len(contract['tasks'])),flush=True)
        # Full closure scan is performed once, not after every chunk.
        require(not any(x.is_symlink() for x in root.rglob('*')), 'Symlink before closure')
        records = load_receipts(root, contract, context)
        require(set(records) == set(contract['tasks']), 'Incomplete subset')
        complete = dict(state='RESEARCH_SUBSET_VERIFIED', context=context, tasks=sorted(records),
                        scope=contract['scope'], global_exclusion=False)
        destination = root / 'COMPLETE.json'
        if destination.exists():
            require(read(destination) == complete, 'Conflicting completion')
        else:
            write(destination, complete)
        return complete
    finally:
        locks.close()
