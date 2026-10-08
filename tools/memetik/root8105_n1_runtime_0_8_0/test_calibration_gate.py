"""Targeted release-delta tests; fixtures are not a second Windows acceptance."""
import copy
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import calibration_gate as g
import preflight
import runtime as r


def require_control(value):
    if value != "CONTROL":
        raise AssertionError(value)


def main():
    results = []
    def test(name, operation, reject=False):
        try:
            operation()
        except (ValueError, BlockingIOError):
            if not reject:
                raise
        else:
            if reject:
                raise AssertionError('Accepted negative case: ' + name)
        results.append(dict(test=name, passed=True))
    cfg = dict(max_rss_bytes=24*g.GIB, min_available_bytes=8*g.GIB, min_free_bytes=100*g.GIB)
    cg = dict(version=2, visible_memory_ceiling_bytes=None, visible_memory_headroom_bytes=None)
    mem = dict(MemTotal=49331856*1024, MemAvailable=48648304*1024)
    def check(c=cfg, cgroup=cg, memory=mem, host=40*g.GIB, disk=830*g.GIB):
        return g.memory_envelope(c, cgroup, memory, host, disk)
    test('measured_Ryzen_unlimited_cgroup_with_finite_guest', check)
    test('low_guest_available', lambda: check(memory=dict(mem, MemAvailable=31*g.GIB)), True)
    test('low_host_available', lambda: check(host=31*g.GIB), True)
    test('low_disk', lambda: check(disk=99*g.GIB), True)
    test('oversized_RSS', lambda: check(c=dict(cfg, max_rss_bytes=25*g.GIB)), True)
    test('reduced_reserve', lambda: check(c=dict(cfg, min_available_bytes=7*g.GIB)), True)
    test('missing_cgroup', lambda: check(cgroup=None), True)
    test('finite_cgroup_too_small', lambda: check(cgroup=dict(cg, visible_memory_ceiling_bytes=31*g.GIB, visible_memory_headroom_bytes=31*g.GIB)), True)
    test('finite_cgroup_sufficient', lambda: check(cgroup=dict(cg, visible_memory_ceiling_bytes=40*g.GIB, visible_memory_headroom_bytes=35*g.GIB)))
    test('accepted_evidence_archive', g.evidence)
    with tempfile.TemporaryDirectory() as temp:
        d = Path(temp)
        (d/'TARGET_ACCEPTANCE.zip').write_bytes(b'changed')
        with patch.object(g, '__file__', str(d/'calibration_gate.py')):
            test('altered_evidence_rejected', g.evidence, True)
        (d/'conway99_workspace').mkdir()
        with patch.object(Path, 'home', return_value=d):
            with g.single_calibration():
                def competing():
                    with g.single_calibration():
                        pass
                test('parallel_calibration_rejected', competing, True)
            test('lock_released_after_return', competing)
    manifest = dict(worker_sha256=g.WORKER_SHA, checker_sha256=g.CHECKER_SHA,
                    worker='/fixture/worker', checker='/fixture/checker', platform_wsl=True)
    manifest.update({'accounting_sha256': '0a0121011af289bd7c7d200fc464435f467862742509ba4e1e0c5540d44e0929', 'binder_sha256': 'd3ebe14be640c519810310164a7aeb3e69cb014d1076f467bd4718c3417e06a3', 'guard_sha256': '0f5851e27a32eec5336d5f4303a3bcc309e70d7100bc15d97c8dc42047439d13', 'host_script_sha256': '49c35d187f6285c36086fbc3e9bd189221ceb2d724b8330a8bd7168ad70e8d40', 'n1_check_sha256': '116c33dcd3bf4b16fb70d20a68cf09995feff31368d10c4a13d3fbd1c5c1c04a', 'platform_adapter_sha256': '8904a4d3ff9515def7ffc49072d46ba02547063151eb37870be2f9957ecaeba2', 'recovery_sha256': '75f8906b1617d514c8d455d8153f36bd20f9834de2d5b6ae52ce1d5123c9a018'})
    with patch.object(g.platform, 'node', return_value='RB-CUBE'), patch.object(g.platform, 'release', return_value='microsoft-fixture'):
        test('accepted_build_binding', lambda: g.target(manifest))
        test('changed_core_rejected', lambda: g.target(dict(manifest, guard_sha256='0'*64)), True)
        test('wrong_binary_rejected', lambda: g.target(dict(manifest, worker_sha256='0'*64)), True)
        test('missing_host_adapter_rejected', lambda: g.target(dict(manifest, platform_wsl=False)), True)
    with patch.object(g.platform, 'node', return_value='other-host'):
        test('wrong_host_rejected', lambda: g.target(manifest), True)
    import recovery
    with tempfile.TemporaryDirectory() as temp:
        d = Path(temp)
        (d/'conway99_workspace').mkdir()
        with patch.object(Path, 'home', return_value=d), patch.object(r, 'read', return_value={'execution_profile':'n1-production'}):
            def inner(root, resume):
                with g.single_calibration():
                    raise AssertionError('runtime did not hold campaign lock')
            with patch.object(recovery, 'run', side_effect=inner):
                test('runtime_dispatch_holds_lock', lambda: r.run(d), True)
        with patch.object(r, 'read', return_value={'execution_profile':'control'}), patch.object(recovery, 'run', return_value='CONTROL'):
            test('control_dispatch_unchanged', lambda: require_control(r.run(d)))
    test('gate_source_binding', preflight.calibration_module)
    with patch.object(preflight.r, 'sha', return_value='changed'):
        test('changed_gate_source_rejected', preflight.calibration_module, True)
    print(json.dumps(dict(status='PASS', tests=results, windows_executed=False, N1_searches=0), indent=2))


if __name__ == '__main__':
    main()
