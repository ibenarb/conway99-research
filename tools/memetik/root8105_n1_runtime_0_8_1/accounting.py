"""Linux CLI accounting. Inclusive wait4 totals are never added to child totals.
The observer's own CPU is a lower bound, not a falsely exact end measurement.
"""
import fcntl
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import uuid
import runtime as r

ENV = 'N1_ACCOUNTING_SESSION'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def ledger(root):
    return root.with_name(root.name + '.accounts')


def session(root):
    sid = os.environ.get(ENV)
    if sid is None:
        return None
    require(len(sid) == 32 and all(c in '0123456789abcdef' for c in sid), 'session id')
    return ledger(root)/'sessions'/sid


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ensure(root):
    folder = ledger(root)
    folder.mkdir(exist_ok=True)
    sync_directory(folder.parent)
    with (folder/'registry.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = folder/'manifest.json'
        if not path.exists():
            require(not (folder/'sessions').exists(), 'ledger manifest missing')
            r.raw_atomic(path, dict(id=uuid.uuid4().hex, root=str(root),
                schema='N1_CLI_ACCOUNTING_1', runtime_sha256=r.sha(r.__file__),
                accounting_sha256=r.sha(__file__)))
            (folder/'sessions').mkdir()
            sync_directory(folder)
        value = r.read(path)
        require(value['root'] == str(root) and value['runtime_sha256'] == r.sha(r.__file__)
                and value['accounting_sha256'] == r.sha(__file__), 'ledger identity')
    return value


def inner_check(root):
    directory = session(root)
    require(directory is not None, 'missing outer accounting observer')
    intent = r.read(directory/'intent.json')
    require(intent['root'] == str(root) and intent['id'] == directory.name,
            'inner account identity')
    require(intent['observer']['pid'] == os.getppid(), 'observer parent mismatch')
    from recovery import alive
    require(alive(intent['observer']), 'accounting observer missing')
    return directory


def inner_final(root):
    directory = inner_check(root)
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    r.raw_atomic(directory/'inner_usage.json', dict(session_id=directory.name,
        self_cpu_before_exit_s=own.ru_utime+own.ru_stime,
        reaped_children_cpu_s=children.ru_utime+children.ru_stime))


def audit(root, exclude=None):
    # Registration and inventory cannot observe half-created account intents.
    with (ledger(root)/'registry.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        return inventory(root, exclude)


def inventory(root, exclude=None):
    folder = ledger(root)
    meta = r.read(folder/'manifest.json')
    require(meta['root'] == str(root), 'ledger root mismatch')
    rows, gaps, active = [], [], []
    inclusive = observers = search = check = supervisor = 0.0
    partition_complete = True
    from recovery import alive
    for directory in sorted((folder/'sessions').iterdir()):
        require(directory.is_dir(), 'unexpected account entry')
        intent = r.read(directory/'intent.json')
        require(intent['id'] == directory.name and intent['ledger_id'] == meta['id']
                and intent['root'] == str(root), 'account intent identity')
        if directory.name == exclude:
            continue
        end = directory/'receipt.json'
        if not end.exists():
            data = dict(session_id=directory.name, cpu_s=None)
            if alive(intent['observer']):
                active.append(data)
            else:
                heartbeat = directory/'heartbeat.json'
                if heartbeat.exists():
                    data['last_heartbeat'] = r.read(heartbeat)
                gaps.append(data)
            partition_complete = False
            continue
        value = r.read(end)
        require(value['session_id'] == directory.name and value['ledger_id'] == meta['id']
                and value['intent_sha256'] == r.sha(directory/'intent.json'), 'receipt identity')
        for key in ('inclusive_wait4_cpu_s', 'observer_cpu_lower_bound_s', 'user_s', 'system_s'):
            require(number(value[key]), 'invalid CPU value')
        require(abs(value['inclusive_wait4_cpu_s']-value['user_s']-value['system_s']) < 1e-9,
                'wait4 components disagree')
        for name, digest in value['files'].items():
            require(Path(name).name == name and r.sha(directory/name) == digest, 'account artifact changed')
        pe = value.get('platform')
        if pe is not None:
            require(r.sha(directory / "platform" / "final.json") == value["platform_final_sha256"] and
                    r.read(directory / "platform" / "final.json") == pe, "changed platform end receipt")
        import platform_adapter
        if not platform_adapter.platform_account_complete(directory, value):
            gaps.append(dict(session_id=directory.name, cpu_s=None, reason='platform end/account fault'))
        inclusive += value['inclusive_wait4_cpu_s']
        observers += value['observer_cpu_lower_bound_s']
        amounts = dict(search=0.0, check=0.0)
        phase_gaps = []
        if (root/'attempts').exists():
            for attempt in (root/'attempts').iterdir():
                am = r.read(attempt/'attempt.json')
                if am.get('accounting_session') != directory.name:
                    continue
                for phase in amounts:
                    launch = attempt/(phase+'_intent.json')
                    final = attempt/(phase+'_receipt.json')
                    if launch.exists() and not final.exists():
                        phase_gaps.append(str(launch.relative_to(root)))
                    if final.exists():
                        receipt = r.read(final)
                        require(receipt['attempt_id'] == attempt.name and receipt['phase'] == phase
                                and number(receipt['cpu_s']), 'invalid phase account')
                        amounts[phase] += receipt['cpu_s']
        native = sum(amounts.values())
        usage_path = directory/'inner_usage.json'
        split = usage_path.name in value['files'] and not phase_gaps
        if split:
            usage = r.read(usage_path)
            require(usage['session_id'] == directory.name and number(usage['reaped_children_cpu_s'])
                    and number(usage['self_cpu_before_exit_s']), 'inner usage identity')
            require(abs(usage['reaped_children_cpu_s']-native) <= 0.000010, 'unclassified reaped child CPU')
            remainder = value['inclusive_wait4_cpu_s'] - native
            require(remainder >= 0 and remainder+1e-6 >= usage['self_cpu_before_exit_s'],
                    'inclusive wait4 does not cover recorded CPU')
            supervisor += remainder
        else:
            partition_complete = False
        search += amounts['search']
        check += amounts['check']
        rows.append(dict(session_id=directory.name, action=intent['action'],
            inclusive_wait4_cpu_s=value['inclusive_wait4_cpu_s'], native_cpu_s=amounts,
            supervisor_cpu_s=remainder if split else None, partition_complete=split,
            platform=value.get('platform'), child_aggregation_rounding_s=usage['reaped_children_cpu_s']-native if split else None,
            phase_gaps=phase_gaps, returncode=value['returncode']))
    host_confirmed = sum(x["platform"]["host"]["sampler_cpu_end_s"] + x["platform"]["host"]["owner_cpu_lower_bound_s"]
        for x in rows if x["platform"] is not None and x["platform"]["adapter_complete"])
    return dict(schema='N1_CLI_ACCOUNTING_REPORT_1', ledger_id=meta['id'], sessions=rows,
        inclusive_wait4_confirmed_s=inclusive, native_search_confirmed_s=search,
        native_check_confirmed_s=check, supervisor_confirmed_s=supervisor,
        observer_cpu_lower_bound_s=observers, accounted_lower_bound_s=inclusive+observers+host_confirmed,
        resource_stops=[dict(session_id=x['session_id'], fault=x['platform']['fault'])
                        for x in rows if x['platform'] is not None and x['platform']['fault'] is not None
                        and x['platform']['fault'].get('reason') == 'ValueError: HOST_MEMORY_RESERVE'],
        observed_commands_complete=not gaps and not active and partition_complete,
        partition_complete=partition_complete, gaps=gaps, active=active,
        all_system_cpu_complete=False, host_cpu_s=None,
        host_sampler_end_confirmed_s=sum(x['platform']['host']['sampler_cpu_end_s'] for x in rows
            if x['platform'] is not None and x['platform']['adapter_complete']),
        host_observer_lower_bound_s=sum(x['platform']['host']['owner_cpu_lower_bound_s'] for x in rows
            if x['platform'] is not None and x['platform']['adapter_complete']),
        history_includes_wrapped_init=any(x['action'] == 'init' and x['returncode'] == 0 for x in rows),
        current_inspection_session_excluded=exclude, child_rounding_tolerance_s=0.000010,
        exclusions=['observer work after its last sample', 'unwrapped API calls',
                    'external host services and commands outside this CLI'],
        budget_scope='native_children_cpu_seconds_unchanged')


def gate(root, manifest):
    if not manifest.get('accounting_ledger_id'):
        return  # Explicitly unwrapped test API; never a complete CLI history.
    inner_check(root)
    report = audit(root, session(root).name)
    require(report['ledger_id'] == manifest['accounting_ledger_id'], 'replaced account ledger')
    require(not report['gaps'], 'missing observer end receipt; accounting reconciliation required')


def launch(root, action, argv, platform_config=None):
    meta = ensure(root)
    sid = uuid.uuid4().hex
    directory = ledger(root)/'sessions'/sid
    intent = dict(id=sid, ledger_id=meta['id'], root=str(root), action=action,
                  observer=r.identity(os.getpid()), created_ns=time.time_ns())
    with (ledger(root)/'registry.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        directory.mkdir()
        r.raw_atomic(directory/'intent.json', intent)
        sync_directory(directory.parent)
    adapter = None
    if platform_config is not None:
        import platform_adapter
        adapter = platform_adapter.Observer(root, directory, platform_config)
        try:
            adapter.start()
        except BaseException:
            adapter.finish()
            raise
    command = [sys.executable, str(Path(r.__file__).resolve())] + argv
    env = dict(os.environ, **{ENV: sid})
    if adapter is not None:
        env[platform_adapter.ENV] = str(adapter.folder)
    try:
        child = subprocess.Popen(command, env=env)
    except BaseException:
        if adapter is not None:
            adapter.finish()
        raise
    ident = r.identity(child.pid)
    if adapter is not None:
        adapter.inner = ident
    r.raw_atomic(directory/'identity.json', ident)
    while True:
        pid, status, usage = os.wait4(child.pid, os.WNOHANG)
        if pid:
            child.returncode = os.waitstatus_to_exitcode(status)
            break
        r.raw_atomic(directory/'heartbeat.json', dict(session_id=sid, utc=time.time(),
            observer_cpu_lower_bound_s=time.process_time(), inner_self_live_s=r.live_cpu(ident)))
        if adapter is not None:
            adapter.tick()
        time.sleep(0.1)
    platform_end = adapter.finish() if adapter is not None else None
    r.fault(root, 'observer_after_wait4')
    value = dict(session_id=sid, ledger_id=meta['id'], intent_sha256=r.sha(directory/'intent.json'),
        platform=platform_end, platform_final_sha256=r.sha(adapter.folder / "final.json") if adapter is not None else None, returncode=child.returncode, user_s=usage.ru_utime, system_s=usage.ru_stime,
        inclusive_wait4_cpu_s=usage.ru_utime+usage.ru_stime,
        observer_cpu_lower_bound_s=time.process_time(),
        peak_child_rss_kib=usage.ru_maxrss,
        files={p.name: r.sha(p) for p in directory.iterdir() if p.name in ('identity.json', 'inner_usage.json')})
    r.raw_atomic(directory/'receipt.json', value)
    r.fault(root, 'observer_after_receipt')
    # Reports are derived snapshots; receipts, not this cache, are authoritative.
    r.raw_atomic(ledger(root)/('report-'+sid+'.json'), audit(root))
    if platform_end is not None and (not platform_end["adapter_complete"] or platform_end["fault"] is not None):
        return 78
    return child.returncode if child.returncode >= 0 else 128-child.returncode
