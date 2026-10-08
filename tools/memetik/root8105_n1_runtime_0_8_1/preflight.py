"""Mandatory launch gate. Reports never grant a reusable production capability."""
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import time
import uuid
import accounting
import guard
import n1_check
import runtime as r

CATALOG_SHA256 = 'bccafba36574c677c65d8f2e744310e2c85ce95cd2494c16a9ef667732f8e8e5'
CATALOG_COMMIT = '9a02918f46b2c7c5af2f36da3445233b7382c6b0'
PROFILES = ('control', 'n1-production')


def require(value, message):
    if not value:
        raise ValueError(message)


def calibration_module():
    path = Path(__file__).with_name('calibration_gate.py')
    require(r.sha(path) == 'ed20323b539872071fde400a620698502436e6deec6cb076200fea8aa0956555', 'calibration gate source changed')
    import calibration_gate
    return calibration_gate


def control_input(cnf, binding=None):
    require(cnf.stat().st_size <= 8*1024*1024, 'control CNF exceeds 8 MiB')
    nv = nc = None
    count, pending = 0, False
    with cnf.open() as stream:
        for line in stream:
            words = line.split()
            if not words or words[0] == 'c':
                continue
            if words[0] == 'p':
                require(nv is None and len(words)==4 and words[1]=='cnf', 'control DIMACS header')
                nv,nc=map(int,words[2:])
                require(0 <= nv <= 1000 and 0 <= nc <= 20000, 'outside small control envelope')
                continue
            require(nv is not None, 'control clause before header')
            for word in words:
                lit=int(word)
                require(abs(lit)<=nv, 'control literal outside header')
                if lit == 0:
                    count+=1
                    pending=False
                else:
                    pending=True
    require(nv is not None and not pending and count==nc, 'control clause count/termination')
    if binding is not None:
        spec=n1_check.load(binding)['spec']
        require(spec['kind']=='control' and spec['m']==2, 'real root cannot use control profile')
    return dict(variables=nv, clauses=nc, bytes=cnf.stat().st_size, production=False)


def catalog_identity(root, manifest):
    require(manifest['binding_sha256'] is not None, 'missing N1 binding')
    require(manifest['catalog_sha256']==CATALOG_SHA256, 'unapproved catalogue receipt hash')
    path=root/'catalog.json'
    require(r.sha(path)==CATALOG_SHA256, 'catalogue receipt changed')
    catalog=n1_check.load(path)
    require(catalog['schema']=='N1_CATALOG_IDENTITY_1' and catalog['status']=='PASS', 'catalogue schema/status')
    binding=n1_check.load(root/'binding.json')
    spec=binding['spec']
    require(spec['kind']=='root-class' and spec['m']==7 and spec['class_id']==0 and
            spec['root_id'] in (210,6682), 'task outside approved catalogue slice')
    rows=[x for x in catalog['results'] if (x['root_id'],x['class_id'])==(spec['root_id'],spec['class_id'])]
    require(len(rows)==1, 'ambiguous catalogue identity')
    row=rows[0]
    require(row['catalog_identity_checked'] is True and row['binding_sha256']==r.sha(root/'binding.json') and
            row['cnf_sha256']==r.sha(root/'input.cnf'), 'catalogue binding/CNF mismatch')
    n1_check.validate_binding(binding,root/'input.cnf')
    return dict(root_id=spec['root_id'],class_id=0,catalog_sha256=CATALOG_SHA256,
                reference_commit=CATALOG_COMMIT,full_coverage_reaudited=False)


def unescape(text):
    return re.sub(r'\\([0-7]{3})',lambda m:chr(int(m.group(1),8)),text)


def cgroup_probe(membership=None, mounts=None):
    membership=Path('/proc/self/cgroup').read_text() if membership is None else membership
    mounts=Path('/proc/self/mountinfo').read_text() if mounts is None else mounts
    paths=[x[3:] for x in membership.splitlines() if x.startswith('0::')]
    require(len(paths)==1, 'no unique cgroup-v2 membership')
    member=PurePosixPath(paths[0])
    require(member.is_absolute() and '..' not in member.parts, 'invalid cgroup membership path')
    candidates=[]
    for line in mounts.splitlines():
        fields=line.split()
        if '-' not in fields:
            continue
        sep=fields.index('-')
        if fields[sep+1]!='cgroup2':
            continue
        base=PurePosixPath(unescape(fields[3]))
        try:
            relative=member.relative_to(base)
        except ValueError:
            continue
        mount=Path(unescape(fields[4])).resolve(strict=True)
        directory=(mount/str(relative)).resolve(strict=True)
        require(directory.is_relative_to(mount), 'cgroup mount traversal')
        candidates.append((len(base.parts),mount,directory,fields[5]))
    require(bool(candidates), 'membership not mapped to visible cgroup mount')
    _,mount,directory,options=max(candidates,key=lambda x:x[0])
    rows=[]
    current=directory
    while True:
        row=dict(path=str(current))
        for name in ('memory.max','memory.high','memory.current','cpu.max','memory.events'):
            p=current/name
            row[name]=p.read_text().strip() if p.exists() else None
        for name in ('memory.max','memory.high','memory.current'):
            value=row[name]
            if value not in (None,'max'):
                require(value.isdecimal(), 'invalid cgroup memory value')
                row[name]=int(value)
        rows.append(row)
        if current==mount:
            break
        current=current.parent
    leaf=rows[0]
    require(type(leaf['memory.current']) is int and leaf['memory.max'] is not None,
            'required leaf memory counters unavailable')
    finite=[x['memory.max'] for x in rows if type(x['memory.max']) is int]
    remaining=[max(0,x['memory.max']-x['memory.current']) for x in rows
               if type(x['memory.max']) is int and type(x['memory.current']) is int]
    return dict(version=2,membership=str(member),mount=str(mount),directory=str(directory),
        mount_read_only='ro' in options.split(','),visible_ancestors=rows,
        visible_memory_ceiling_bytes=min(finite) if finite else None,
        visible_memory_headroom_bytes=min(remaining) if remaining else None,
        hidden_ancestors_not_verified=True,limits_modified=False)


def host_probe():
    release=platform.release()
    result=dict(kernel_release=release,system=platform.system(),wsl='microsoft' in release.lower(),
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                guest_monotonic_ns=time.monotonic_ns(),guest_utc_ns=time.time_ns(),
                windows_host_clock=None,host_cpu_end_account=None)
    try:
        result['cgroup']=cgroup_probe()
    except (OSError,ValueError) as exc:
        result['cgroup']=None
        result['cgroup_error']=type(exc).__name__+': '+str(exc)
    return result


def inspect(root, manifest=None, state=None):
    import recovery
    m=manifest or r.read(root/'manifest.json')
    s=state or r.read(root/'state.json')
    checks=[]
    def check(name, operation):
        try:
            detail=operation()
            checks.append(dict(name=name,passed=True,detail=detail))
        except (OSError,ValueError,KeyError,TypeError,OverflowError) as exc:
            checks.append(dict(name=name,passed=False,detail=type(exc).__name__+': '+str(exc)))
    def identity():
        recovery.validate(root)
        require(s['run_id']==m['run_id'],'state/manifest run mismatch')
        require(m['execution_profile'] in PROFILES,'unknown execution profile')
        return m['execution_profile']
    check('immutable_inputs_and_sources',identity)
    check('no_inherited_CPU_timeout',lambda: require(resource.getrlimit(resource.RLIMIT_CPU)==(-1,-1),'finite CPU limit'))
    def native_accounts():
        inv=recovery.inventory(root,s,m)
        require(inv['accounting_complete'] and s['accounting_complete'],'native account gap')
        require(abs(inv['cpu_confirmed_s']-s['cpu_completed'])<1e-9,'native ledger mismatch')
        require(s['status'] in ('READY','STOPPED_UNRESOLVED','UNSAT_UNCERTIFIED','RESOURCE_STOPPED',
                'SAT_CNF_VERIFIED','SAT_N1_VERIFIED','UNSAT_CERTIFIED'),'run state requires recovery or is active')
        return dict(confirmed_cpu_s=inv['cpu_confirmed_s'],result_status=inv['result_status'])
    check('native_accounts_and_restart_state',native_accounts)
    import platform_adapter
    if m.get('platform_wsl'):
        def live_platform():
            require(platform_adapter.current() is not None, 'platform observer absent')
            return platform_adapter.health()
        check('live_windows_and_continuous_cgroup_adapter', live_platform)
    profile=m.get('execution_profile')
    environment=host_probe()
    if profile=='control':
        check('bounded_control_input',lambda: control_input(root/'input.cnf',
            root/'binding.json' if m['binding_sha256'] else None))
    elif profile=='n1-production':
        check('catalogue_binding',lambda: catalog_identity(root,m))
        def protected():
            cfg=m['guard']
            require(cfg is not None,'mandatory guard absent')
            require(guard.config(cfg['original_budget'],cfg['max_rss_bytes'],cfg['min_free_bytes'],
                                cfg['min_available_bytes'])==cfg,'invalid guard configuration')
            guard.validate_state(root,s,m)
            return cfg
        check('mandatory_guard_and_budget_history',protected)
        def cli_history():
            require(m['accounting_ledger_id'] is not None,'unwrapped initialization')
            current=accounting.session(root)
            report=accounting.audit(root,current.name if current else None)
            require(report['ledger_id']==m['accounting_ledger_id'] and not report['gaps'] and
                    report['history_includes_wrapped_init'],'CLI history incomplete')
            return dict(ledger_id=report['ledger_id'],host_accounting_complete=False)
        check('bound_CLI_account_history',cli_history)
        check('unlimited_proof_file_size',lambda: require(resource.getrlimit(resource.RLIMIT_FSIZE)==(-1,-1),'finite file-size limit'))
        check('observed_WSL_and_cgroup_memory_envelope',
              lambda: calibration_module().memory(root,m,environment))
        check('WSL_target',lambda: require(environment['wsl'],'not observed on WSL target'))
        # These are missing executable capabilities, not user-editable booleans.
        for name in ('windows_host_clock_adapter','host_end_accounting_adapter',
                     'continuous_cgroup_guard_integration'):
            checks.append(dict(name=name,passed=bool(m.get('platform_wsl')) and
                any(c['name']=='live_windows_and_continuous_cgroup_adapter' and c['passed'] for c in checks),
                detail='IMPLEMENTED_AND_RYZEN_0_7_2_ACCEPTED'))
        check('target_hardware_acceptance',lambda: calibration_module().target(m))
    else:
        checks.append(dict(name='execution_profile',passed=False,detail='unknown profile'))
    blocked=[x['name'] for x in checks if not x['passed']]
    return dict(schema='N1_PREFLIGHT_1',run_id=m['run_id'],profile=profile,
        allowed=not blocked,status=('CALIBRATION_READY' if profile=='n1-production' else 'CONTROL_READY') if not blocked else 'BLOCKED',
        blockers=blocked,checks=checks,environment=environment,created_utc=time.time(),
        manifest_sha256=r.sha(root/'manifest.json'),state_sequence=s['_seq'],
        production_launch_authorized=not blocked and profile=='n1-production',scientific_result=None,report_is_not_a_start_token=True)


def enforce(root, manifest, state):
    report=inspect(root,manifest,state)
    folder=root/'preflights'
    folder.mkdir(exist_ok=True)
    path=folder/(uuid.uuid4().hex+'.json')
    r.raw_atomic(path,report)
    if not report['allowed']:
        raise ValueError('PREFLIGHT_BLOCKED: '+', '.join(report['blockers']))
    return report
