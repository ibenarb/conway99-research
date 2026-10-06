"""Recovery rejection tests: immutable identities and accounts, no production work."""
import json
import math
from pathlib import Path
import tempfile

from census import audit_start, checked_payload, initialise, reconcile_crash
from runtime import atomic, connect, put


def snapshot(run):
    con = connect(run, readonly=True)
    value = '\n'.join(con.iterdump())
    con.close()
    return value


def rejected_unchanged(run, expected):
    before = snapshot(run)
    for apply in (False, True):
        try:
            reconcile_crash(run, apply=apply)
        except ValueError as exc:
            assert expected in str(exc), str(exc)
        else:
            raise AssertionError('invalid recovery accepted')
        assert snapshot(run) == before, 'rejected recovery changed database'


def main(out):
    root = Path(tempfile.mkdtemp(prefix='root8105-recovery-tests-'))
    tests = []
    for name in ('orphan', 'manifest', 'fingerprint', 'root-identity', 'negative-cpu'):
        run = root / name
        initialise(run, 1, 300, test_mode=True, test_roots=1)
        con = connect(run)
        with con:
            if name == 'orphan':
                con.execute("UPDATE roots SET state='RUNNING'")
                expected = 'NEW_RUN_REQUIRED'
            elif name == 'manifest':
                put(con, 'run_id', 'foreign-run')
                expected = 'manifest mismatch'
            elif name == 'fingerprint':
                manifest = json.loads((run / 'manifest.json').read_text())
                manifest['fingerprint']['code_hash'] = 'foreign-code'
                put(con, 'fingerprint', manifest['fingerprint'])
                atomic(run / 'manifest.json', manifest)
                expected = 'fingerprint changed'
            elif name == 'root-identity':
                row = json.loads(con.execute('SELECT spec FROM roots').fetchone()[0])
                row['row'] = '0'
                con.execute('UPDATE roots SET spec=?', (json.dumps(row),))
                expected = 'ROOT_IDENTITY_MISMATCH'
            else:
                put(con, 'auxiliary_cpu_s', -1)
                expected = 'ACCOUNT_CPU_INVALID'
        con.close()
        rejected_unchanged(run, expected)
        tests.append(name + '_dry_run_and_apply_rejected_without_account_changes')
    # Invalid process CPU is never promoted to a recovered receipt.
    spec = {'attempt': 'a', 'model': 'test', 'code_hash': 'c', 'root_hash': 'r',
            'model_hash': 'm', 'root_row_hash': 'rr', 'root': {'id': 1}, 'partial': {}}
    path = root / 'payload.json'
    for value in (-1, math.inf, math.nan, True, '1'):
        payload = dict(spec, root=1, counts={}, worker_cpu_s=value)
        atomic(path, payload)
        try:
            checked_payload(path, spec)
        except ValueError as exc:
            assert 'invalid worker CPU' in str(exc)
        else:
            raise AssertionError('invalid worker CPU accepted')
    tests.append('five_invalid_worker_cpu_values_rejected')
    # Clean no-op, including apply, leaves all logical data intact and releases the lock.
    run = root / 'clean'
    initialise(run, 1, 300, test_mode=True, test_roots=1)
    before = snapshot(run)
    for apply in (False, True, False):
        result = reconcile_crash(run, apply=apply)
        assert not result['sessions'] and not result['attempts'] and 'applied' not in result
        assert snapshot(run) == before
    con = connect(run, readonly=True)
    audit_start(con)
    con.close()
    tests.append('clean_recovery_noop_and_lock_release')
    atomic(out, {'status': 'PASS', 'tests': tests, 'artifacts': str(root),
                 'scope': 'synthetic corrupt copies; no mathematical census'})
    print(json.dumps({'status': 'PASS', 'tests': tests}), flush=True)


if __name__ == '__main__':
    import sys
    main(Path(sys.argv[1]))
