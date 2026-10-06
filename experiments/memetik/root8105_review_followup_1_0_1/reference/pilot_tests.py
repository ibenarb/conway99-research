"""Regressions for new mirror, clock and deterministic sampling integration."""
import json
import sys
import tempfile
import time
from pathlib import Path
from runtime import atomic, answer, budget_tick, close_requests, connect, get, sync_request
from census import initialise
from clock_diagnostics import ClockDiagnostics


def tests():
    results = []
    with tempfile.TemporaryDirectory(prefix='filter-pilot-tests-') as directory:
        run = Path(directory) / 'run'
        info = initialise(run, 2, 1, test_mode=True)
        con = connect(run)
        budget_tick(con, run, 2)
        rid = json.loads((run / 'time_request.json').read_text())['id']
        assert answer(run, info['run_id'], rid, '10') == 'EXTENDED'
        assert json.loads((run / 'time_request.json').read_text())['state'] == 'EXTENDED'
        assert answer(run, info['run_id'], rid, '10') == 'ALREADY_PROCESSED'
        assert get(con, 'budget_cpu_s') == 11
        for state in ('CLOSED_COMPLETE', 'CLOSED_USER_BUDGET_ZERO'):
            budget_tick(con, run, 20)
            close_requests(con, state)
            assert json.loads((run / 'time_request.json').read_text())['state'] == state
            atomic(run / 'time_request.json', {'state': 'OPEN', 'id': 'obsolete-mirror'})
            sync_request(con)
            assert json.loads((run / 'time_request.json').read_text())['state'] == state
        budget_tick(con, run, 20)
        rid = json.loads((run / 'time_request.json').read_text())['id']
        assert answer(run, info['run_id'], rid, '0') == 'STOP_REQUESTED'
        close_requests(con, 'CLOSED_USER_BUDGET_ZERO')
        assert json.loads((run / 'time_request.json').read_text())['state'] == 'CLOSED_USER_BUDGET_ZERO'
        con.close()
        results.append('mirror after extension, completion, zero, restart; duplicate answer idempotent')
    c = ClockDiagnostics(10, 100, True)
    assert c.observe(10, 100)['reason'] == 'HOST_NOT_YET_AVAILABLE'
    assert c.observe(11, 101, error='test')['reason'] == 'HOST_READ_ERROR'
    assert c.observe(12, 102, {'pid': 1, 'stopwatch_s': 1, 'utc_s': 102})['reason'] == 'ANCHOR_WARMUP'
    d = c.observe(72, 162, {'pid': 1, 'stopwatch_s': 61, 'utc_s': 162})
    assert d['ok'] and d['deviation_s'] == 0
    d = c.observe(142, 222, {'pid': 1, 'stopwatch_s': 121, 'utc_s': 222})
    assert d['reason'] == 'HOST_WSL_DELTA_MISMATCH' and d['deviation_s'] == 10
    assert d['host_anchor']['guest_monotonic_s'] == 12
    assert c.observe(200, 500, {'pid': 1, 'stopwatch_s': 180, 'utc_s': 280})['reason'] == 'HOST_STALE_OR_UTC_MISMATCH'
    assert c.observe(200, 300, {'pid': 2, 'stopwatch_s': 180, 'utc_s': 300})['reason'] == 'HOST_IDENTITY_OR_CLOCK_RESET'
    results.append('clock anchors/deltas/freshness/read error/reset/drift reasons')
    from plan import choose_controls
    cases = [{'root': i, 'type': i % 3, 'target': 2, 'rank': 10,
              'variants': {'F_LD': {'pass': False, 'reason': 'label_disjoint'}}} for i in range(40)]
    groups = choose_controls(list(reversed(cases)))
    assert all(len(g['cases']) == 8 for g in groups)
    assert all([c['root'] for c in g['cases']] == list(range(g['type'], 24, 3)) for g in groups)
    results.append('deterministic first-eight per type/reason independent of result order')
    return {'status': 'PASS', 'checks': results, 'cpu_s': time.process_time()}


if __name__ == '__main__':
    output = Path(sys.argv[1])
    atomic(output, tests())
