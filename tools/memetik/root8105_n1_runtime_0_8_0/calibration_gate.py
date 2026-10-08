"""Evidence-bound release for the two fixed Ryzen N1 calibration cases."""
import contextlib
import fcntl
import hashlib
import io
import json
from pathlib import Path
import platform
import zipfile

GIB = 1024**3
EVIDENCE_SHA = "0a9293787b48cc5f739f42df573b37c3051fefa33516a8a94b7b28c779f04d4c"
WORKER_SHA = "5f307e871ca9e09cf10d8985cce19a5f527ccc383ee19b6252fce5a1811d121c"
CHECKER_SHA = "2d49f6abe7756fe27d895bff73a3da4b83f13a938b594af45097649fa1f15af7"


def require(value, message):
    if not value:
        raise ValueError(message)


def sealed(raw):
    value = json.loads(raw)
    data = json.dumps(value['data'], sort_keys=True, allow_nan=False).encode()
    require(hashlib.sha256(data).hexdigest() == value['sha256'], 'damaged acceptance envelope')
    return value['data']


def evidence():
    raw = Path(__file__).with_name('TARGET_ACCEPTANCE.zip').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EVIDENCE_SHA, 'unapproved target evidence archive')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        probe = sealed(z.read('ROOT8105_N1_probe_20261008_03/RESULT.json'))
        controls = sealed(z.read('ROOT8105_N1_controls_20261008_01/RESULT.json'))
        require(probe['status'] == controls['status'] == 'PASS', 'target tests not passed')
        require(probe['windows_executed'] and controls['windows_executed'], 'synthetic target evidence')
        require(len({s['host']['sequence'] for s in probe['measurements']}) == 6, 'missing host progress')
        require(probe['end_account']['adapter_complete'] and probe['end_account']['fault'] is None,
                'incomplete target host account')
        require(controls['N1_class_searches'] == 0 and len(controls['tests']) == 3 and
                all(t['passed'] for t in controls['tests']), 'incomplete target controls')
        build = json.loads(z.read('ROOT8105_N1_native_072/BUILD.json'))
        require(build['binaries'] == {'n1-worker': WORKER_SHA, 'drat-trim': CHECKER_SHA}, 'target binary identities')
    return dict(archive_sha256=EVIDENCE_SHA, audit_commit='d28d8f88cd95119737a58089b963f8e5fbb94b96',
                acceptance_runtime='0.7.2', release_runtime='0.8.0', scope='two fixed class-zero calibrations')


def target(manifest):
    require(platform.node() == 'RB-CUBE' and 'microsoft' in platform.release().lower(), 'wrong calibration host')
    require(manifest['worker_sha256'] == WORKER_SHA and manifest['checker_sha256'] == CHECKER_SHA,
            'binaries differ from accepted Ryzen build')
    require(manifest['platform_wsl'] is True, 'live Windows observation required')
    accepted_sources = {'accounting_sha256': '0a0121011af289bd7c7d200fc464435f467862742509ba4e1e0c5540d44e0929', 'binder_sha256': 'd3ebe14be640c519810310164a7aeb3e69cb014d1076f467bd4718c3417e06a3', 'guard_sha256': '0f5851e27a32eec5336d5f4303a3bcc309e70d7100bc15d97c8dc42047439d13', 'host_script_sha256': '49c35d187f6285c36086fbc3e9bd189221ceb2d724b8330a8bd7168ad70e8d40', 'n1_check_sha256': '116c33dcd3bf4b16fb70d20a68cf09995feff31368d10c4a13d3fbd1c5c1c04a', 'platform_adapter_sha256': '8904a4d3ff9515def7ffc49072d46ba02547063151eb37870be2f9957ecaeba2', 'recovery_sha256': '75f8906b1617d514c8d455d8153f36bd20f9834de2d5b6ae52ce1d5123c9a018'}
    require(all(manifest.get(key) == value for key, value in accepted_sources.items()),
            "core sources differ from accepted runtime")
    require(not Path(manifest['worker']).is_symlink() and not Path(manifest['checker']).is_symlink(),
            'native binaries must be fixed regular files')
    return evidence()


def memory_envelope(cfg, cgroup, memory, host_available, disk_free):
    require(cgroup is not None and cgroup['version'] == 2, 'cgroup observations required')
    require(cfg['max_rss_bytes'] <= 24*GIB and cfg['min_available_bytes'] >= 8*GIB and
            cfg['min_free_bytes'] >= 100*GIB, 'outside calibration resource envelope')
    total, available = memory['MemTotal'], memory['MemAvailable']
    require(type(total) is int and type(available) is int and 0 < available <= total <= 48*GIB,
            'invalid or changed WSL guest memory envelope')
    needed = cfg['max_rss_bytes'] + cfg['min_available_bytes']
    require(total >= needed and available >= needed, 'insufficient WSL startup headroom')
    require(host_available >= needed, 'insufficient Windows startup headroom')
    require(disk_free >= cfg['min_free_bytes'], 'insufficient disk reserve')
    ceiling, headroom = cgroup['visible_memory_ceiling_bytes'], cgroup['visible_memory_headroom_bytes']
    if ceiling is not None:
        require(headroom is not None and ceiling >= needed and headroom >= needed,
                'finite cgroup limit/headroom too small')
    return dict(kind='WSL_guest_RAM_with_continuous_reserve_observation', guest_total_bytes=total,
                guest_available_bytes=available, host_available_bytes=host_available,
                cgroup_ceiling_bytes=ceiling, swap_counted_as_RAM=False,
                hard_per_process_limit=False, os_limits_modified=False)


def memory(root, manifest, environment):
    import guard
    import platform_adapter
    health = platform_adapter.health()
    values = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        name, rest = line.split(':', 1)
        if name in ('MemTotal', 'MemAvailable'):
            words = rest.split()
            require(len(words) == 2 and words[1] == 'kB', 'unexpected memory units')
            values[name] = int(words[0])*1024
    sensors = guard.sensors(root, 0)
    require(sensors['synthetic'] is False, 'synthetic resource sample forbidden')
    return memory_envelope(manifest['guard'], environment['cgroup'], values,
                           health['host']['available_physical_bytes'], sensors['free_bytes'])


@contextlib.contextmanager
def single_calibration():
    path = Path.home() / 'conway99_workspace' / 'ROOT8105_N1_calibration.lock'
    with path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another N1 calibration is already active') from None
        yield
