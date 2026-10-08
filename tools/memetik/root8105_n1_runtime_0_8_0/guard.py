"""Opt-in aggregate CPU decision points and cooperative resource protection."""
import collections
import math
import os
from pathlib import Path
import time
import uuid
import accounting as a
import runtime as r

SCOPE = 'recorded_cli_aggregate_cpu_lower_bound_seconds'
SCAN_BATCH = 32
RESERVE_BYTES = 1048576
MONITORS = {}


def config(total, rss, disk, available):
    values = (total, rss, disk, available)
    if all(v is None for v in values):
        return None
    if any(v is None for v in values):
        raise ValueError('guard requires total budget, max RSS, free disk and available memory')
    if type(total) not in (int, float) or not math.isfinite(total) or total <= 0:
        raise ValueError('positive finite aggregate CPU budget required')
    if any(type(v) is not int or v <= 0 for v in (rss, disk, available)):
        raise ValueError('positive integer resource thresholds required')
    return dict(scope=SCOPE, original_budget=total, max_rss_bytes=rss,
                min_free_bytes=disk, min_available_bytes=available,
                scan_batch=SCAN_BATCH, emergency_reserve_bytes=RESERVE_BYTES)


def initial(cfg):
    return dict(config=cfg, budget=cfg['original_budget'], request=None, events=[],
                consumed_lower_bound_s=0.0, stop_reason=None, snapshot=None)


def stat(ident):
    if ident['boot'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip():
        return None
    directory = Path('/proc')/str(ident['proc_pid'])
    try:
        fields = (directory/'stat').read_text().rsplit(')', 1)[1].split()
        if fields[19] != ident['birth'] or os.readlink(directory/'ns/pid') != ident['namespace']:
            return None
        return dict(self_cpu_s=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK'),
            waited_cpu_s=(int(fields[13])+int(fields[14]))/os.sysconf('SC_CLK_TCK'),
            rss_bytes=int(fields[21])*os.sysconf('SC_PAGE_SIZE'), parent=int(fields[1]),
            zombie=fields[0] == 'Z')
    except (FileNotFoundError, ProcessLookupError):
        return None


class Scanner:
    """Closed accounts cached once; bounded enumeration and active refresh per tick."""
    def __init__(self, root):
        self.root = root
        self.folder = a.ledger(root)/'sessions'
        self.current = a.session(root).name
        self.iterator = os.scandir(self.folder)
        self.first_pass_done = False
        self.values = {}
        self.closed = set()
        self.active = collections.deque()
        self.active_set = set()
        self.total = 0.0
        self.last_cycle_utc = None
        self.ledger_id = r.read(a.ledger(root)/'manifest.json')['id']

    def sample(self, sid, state):
        directory = self.folder/sid
        intent = r.read(directory/'intent.json')
        a.require(intent['id'] == sid and intent['root'] == str(self.root) and
                  intent['ledger_id'] == self.ledger_id, 'foreign account intent')
        receipt = directory/'receipt.json'
        if receipt.exists():
            value = r.read(receipt)
            a.require(value['session_id'] == sid and value['ledger_id'] == self.ledger_id and
                      value['intent_sha256'] == r.sha(directory/'intent.json'), 'account receipt identity')
            keys = ('inclusive_wait4_cpu_s', 'observer_cpu_lower_bound_s', 'user_s', 'system_s')
            a.require(all(a.number(value[k]) for k in keys), 'invalid account CPU')
            a.require(abs(value['inclusive_wait4_cpu_s']-value['user_s']-value['system_s']) < 1e-9,
                      'account CPU components')
            self.closed.add(sid)
            self.active_set.discard(sid)
            pe = value.get('platform')
            host = 0.0
            if pe is not None:
                a.require(pe['adapter_complete'] and pe['fault'] is None, 'platform account gap')
                host = pe['host']['sampler_cpu_end_s'] + pe['host']['owner_cpu_lower_bound_s']
            return value['inclusive_wait4_cpu_s']+value['observer_cpu_lower_bound_s']+host, 0
        observer = stat(intent['observer'])
        if observer is None or observer['zombie']:
            if receipt.exists():
                return self.sample(sid, state)
            raise ValueError('missing outer end account')
        cpu, rss = observer['self_cpu_s'], observer['rss_bytes']
        idfile = directory/'identity.json'
        if idfile.exists():
            ident = r.read(idfile)
            inner = stat(ident)
            if inner:
                cpu += inner['self_cpu_s']+inner['waited_cpu_s']
                rss += inner['rss_bytes']
                # Parent is sampled BEFORE child; a concurrent reap can undercount
                # briefly but cannot count a child's CPU both live and waited.
                child_id = state.get('child') if sid == self.current else None
                if child_id:
                    child = stat(child_id)
                    if child and child['parent'] == ident['proc_pid']:
                        cpu += child['self_cpu_s']+child['waited_cpu_s']
                        rss += child['rss_bytes']
            else:
                # Parent may have just reaped: prefer its now-sealed end receipt.
                if receipt.exists():
                    return self.sample(sid, state)
                heartbeat = directory/'heartbeat.json'
                if heartbeat.exists():
                    cpu += r.read(heartbeat).get('inner_self_live_s', 0)
        host_path = directory/'platform'/'health.json'
        if host_path.exists():
            cpu += r.read(host_path)['host']['cpu_lower_bound_s']
        if sid not in self.active_set:
            self.active_set.add(sid)
            self.active.append(sid)
        return cpu, rss

    def update(self, sid, state):
        if sid in self.closed:
            return 0
        value, rss = self.sample(sid, state)
        previous = self.values.get(sid, 0.0)
        # Preserve every already observed lower bound, including observer work
        # in the small interval before its final sample becomes visible.
        self.values[sid] = max(previous, value)
        self.total += self.values[sid]-previous
        return rss

    def tick(self, state):
        processed = 0
        with (a.ledger(self.root)/'registry.lock').open('a') as lock:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_SH)
            for _ in range(SCAN_BATCH):
                try:
                    entry = next(self.iterator)
                except StopIteration:
                    self.iterator.close()
                    self.iterator = os.scandir(self.folder)
                    self.first_pass_done = True
                    self.last_cycle_utc = time.time()
                    break
                a.require(entry.is_dir(follow_symlinks=False), 'unexpected account entry')
                self.update(entry.name, state)
                processed += 1
        for _ in range(min(SCAN_BATCH, len(self.active))):
            sid = self.active.popleft()
            if sid in self.active_set:
                self.update(sid, state)
                if sid in self.active_set:
                    self.active.append(sid)
        rss = self.update(self.current, state)
        return dict(cpu_lower_bound_s=self.total, run_rss_bytes=rss,
                    entries_examined=processed, first_pass_done=self.first_pass_done,
                    last_full_cycle_utc=self.last_cycle_utc, known_accounts=len(self.values),
                    sampled_utc=time.time(), scope=SCOPE)


def sensors(root, rss):
    fake = os.environ.get('N1_TEST_RESOURCES')
    if fake and (root/'ALLOW_TEST_FAULTS').exists():
        data = r.read(root/'TEST_RESOURCES.json')
        return dict(data, synthetic=True)
    fs = os.statvfs(root)
    lines = Path('/proc/meminfo').read_text().splitlines()
    available = int(next(x.split()[1] for x in lines if x.startswith('MemAvailable:')))*1024
    return dict(free_bytes=fs.f_bavail*fs.f_frsize, available_bytes=available,
                rss_bytes=rss, synthetic=False)


def reserve(root):
    path = root/'emergency.reserve'
    if path.exists():
        a.require(path.stat().st_size == RESERVE_BYTES, 'invalid emergency reserve')
        return
    with path.open('xb') as stream:
        os.posix_fallocate(stream.fileno(), 0, RESERVE_BYTES)
        os.fsync(stream.fileno())
    a.sync_directory(root)


def stop(root, state, reason, detail):
    g = state['guard']
    if g['stop_reason'] is None:
        event = dict(reason=reason, detail=detail, utc=time.time(),
                     scope='this_run_only', cpu_lower_bound_s=g['consumed_lower_bound_s'])
        g['stop_reason'] = event
        g['events'].append(event)
        print('RESOURCE_STOP '+reason+' run='+state['run_id'], flush=True)
    state['stop'] = True
    # Release only our own preallocated reserve, never results/proofs/checkpoints.
    path = root/'emergency.reserve'
    if path.exists():
        path.unlink()
        a.sync_directory(root)


def tick(root, state):
    if state.get('guard') is None:
        return
    g = state['guard']
    monitor = MONITORS[str(root)]
    if time.monotonic()-monitor.get('last_tick', -1e9) < 0.25:
        return
    monitor['last_tick'] = time.monotonic()
    try:
        snap = monitor['scanner'].tick(state)
        measurements = sensors(root, snap['run_rss_bytes'])
        for key in ('free_bytes', 'available_bytes', 'rss_bytes'):
            a.require(type(measurements[key]) is int and measurements[key] >= 0, 'invalid resource sensor')
        g['snapshot'] = dict(snap, resources=measurements)
        g['consumed_lower_bound_s'] = max(g['consumed_lower_bound_s'], snap['cpu_lower_bound_s'])
        cfg = g['config']
        for bad, reason in (
            (measurements['free_bytes'] < cfg['min_free_bytes'], 'DISK_RESERVE'),
            (measurements['available_bytes'] < cfg['min_available_bytes'], 'MEMORY_AVAILABLE'),
            (measurements['rss_bytes'] > cfg['max_rss_bytes'], 'RUN_RSS')):
            if bad:
                stop(root, state, reason, measurements)
                break
        if not state['stop'] and g['consumed_lower_bound_s'] >= g['budget'] and g['request'] is None:
            g['request'] = dict(id=uuid.uuid4().hex, scope=SCOPE, budget=g['budget'],
                consumed_at_request=g['consumed_lower_bound_s'], created_utc=time.time(),
                message='time limit reached. ETA unknown. Extend [seconds] ?')
            print('run='+state['run_id']+' scope='+SCOPE+' used='+str(g['consumed_lower_bound_s'])+
                  ' budget='+str(g['budget'])+' CPU seconds request='+g['request']['id'], flush=True)
            print(g['request']['message'], flush=True)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        stop(root, state, 'MONITOR_ERROR', type(exc).__name__+': '+str(exc))


def validate_state(root, state, manifest):
    cfg = manifest.get('guard')
    if cfg is None:
        return
    g = state.get('guard')
    a.require(g is not None and g['config'] == cfg, 'guard config mismatch')
    a.require(a.number(g['consumed_lower_bound_s']), 'invalid guard CPU')
    budgets = dict(native=manifest['original_budget'], total=cfg['original_budget'])
    seen = set()
    for event in state.get('reply_events', []):
        aid, scope = event['answer_id'], event['scope']
        answer = r.read(root/'answers'/(aid+'.json'))
        a.require(aid not in seen and scope in budgets and
                  state['replies'].get(aid) == 'ACCEPTED' and answer['answer_id'] == aid and
                  answer['scope'] == scope and answer['run_id'] == state['run_id'] and
                  answer['request_id'] == event['request']['id'] and
                  type(answer['seconds']) is int and answer['seconds'] >= 0 and
                  answer['seconds'] == event['seconds'] and
                  event['budget_before'] == budgets[scope], 'invalid budget history')
        budgets[scope] += answer['seconds']
        a.require(a.number(budgets[scope]) and event['budget_after'] == budgets[scope], 'budget extension mismatch')
        seen.add(aid)
    a.require(seen == {k for k,v in state['replies'].items() if v == 'ACCEPTED'}, 'missing reply history')
    a.require(state['budget'] == budgets['native'] and g['budget'] == budgets['total'], 'unexplained budget change')


def activate(root, state, manifest):
    if manifest.get('guard') is None:
        return True
    a.require(state.get('guard') is not None and state['guard']['config'] == manifest['guard'],
              'guard config mismatch')
    a.inner_check(root)
    state['guard']['stop_reason'] = None
    import platform_adapter
    try:
        platform_adapter.before_native()
    except (OSError, ValueError) as exc:
        stop(root, state, "PLATFORM_FAULT", str(exc))
        state["status"] = "RESOURCE_STOPPED"
        r.atomic(root / "state.json", state)
        return False
    reserve(root)
    MONITORS[str(root)] = dict(scanner=Scanner(root))
    # Initial history validation occurs before any new native child is started.
    while True:
        MONITORS[str(root)]['last_tick'] = -1e9
        tick(root, state)
        if state['stop'] or MONITORS[str(root)]['scanner'].first_pass_done:
            break
    r.atomic(root/'state.json', state)
    if state['stop']:
        state['status'] = 'RESOURCE_STOPPED'
        r.atomic(root/'state.json', state)
        return False
    return True


def finish(state, result):
    g = state.get('guard')
    if g is None:
        return result
    if g['request'] is not None:
        g['events'].append(dict(reason='REQUEST_CLOSED_ON_TASK_END', request=g['request'], utc=time.time()))
        g['request'] = None
    if g['stop_reason'] and result not in ('SAT_CNF_VERIFIED', 'SAT_N1_VERIFIED', 'UNSAT_CERTIFIED'):
        return 'RESOURCE_STOPPED'
    return result
