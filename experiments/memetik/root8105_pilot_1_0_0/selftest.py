"""Independent tiny-graph oracle, projection/canon/proof and real worker tests."""
import itertools
import json
import os
import random
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from core import Geometry, atomic, encode, enumerate_projection, pack, unpack
from proof import certify

BASE = Path(__file__).resolve().parent


def brute_projection(g, rows, target):
    edges = list(itertools.combinations(range(g.n), 2))
    valid = set()
    for mask in range(1 << len(edges)):
        matrix = [[0] * g.n for _ in range(g.n)]
        for k, (u, v) in enumerate(edges):
            matrix[u][v] = matrix[v][u] = (mask >> k) & 1
        if any(any(matrix[u][v] != ((r >> v) & 1) for v in range(g.n)) for u, r in rows.items()):
            continue
        ok = True
        # Direct numerical oracle; no SAT card/encoder helpers.
        a, b = g.labels[target]
        for x in range(g.b):
            expected = 1 if x in {a, b, (a + g.m) % g.b, (b + g.m) % g.b} else 2
            actual = sum(matrix[target][v] for v, pair in enumerate(g.labels) if x in pair)
            ok &= actual == expected
        for u, row in rows.items():
            for v in range(g.n):
                if v in rows or (v != target and not matrix[u][v]):
                    continue
                shared_border = len(set(g.labels[u]).intersection(g.labels[v]))
                common = sum(matrix[u][w] * matrix[v][w] for w in range(g.n))
                ok &= common + shared_border == 2 - matrix[u][v]
        if ok:
            valid.add(sum(matrix[target][v] << v for v in range(g.n)))
    return valid


def check_graph99_independent(g, rows):
    # Assemble original full graph and directly count common neighbors for every
    # resolved pair, including all border vertices. Independent of row verify.
    n = 1 + g.b + g.n
    adj = [set() for _ in range(n)]
    def edge(a, b):
        adj[a].add(b)
        adj[b].add(a)
    for a in range(g.b):
        edge(0, 1 + a)
    for a in range(g.m):
        edge(1 + a, 1 + a + g.m)
    for u, pair in enumerate(g.labels):
        for a in pair:
            edge(1 + a, 1 + g.b + u)
    for u, row in rows.items():
        for v in range(g.n):
            if (row >> v) & 1:
                edge(1 + g.b + u, 1 + g.b + v)
    resolved = list(range(1 + g.b)) + [1 + g.b + u for u in rows]
    for u in resolved:
        assert len(adj[u]) == 2 * g.m
    for u, v in itertools.combinations(resolved, 2):
        assert len(adj[u] & adj[v]) == (1 if v in adj[u] else 2)


def run_tests(directory=None, operational=True):
    if directory is None:
        directory = tempfile.mkdtemp(prefix='root8105_controls_')
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    g = Geometry(2)
    full = {0: 6, 1: 9, 2: 9, 3: 6}
    checks = 0
    for size in range(1, 4):
        for ids in itertools.combinations(range(1, 4), size - 1):
            rows = {u: full[u] for u in (0,) + ids}
            for target in set(range(4)) - rows.keys():
                cnf, variables = encode(g, rows, target)
                sample, meta = enumerate_projection(g, rows, target, cnf, variables, 5, 15, 1000, 1000, 1)
                assert meta['status'] == 'PROJECTED_ENUMERATION_COMPLETE'
                assert set(sample) == brute_projection(g, rows, target)
                checks += 1
    # Test canonical equivalence under every border matching permutation fixing u.
    actual = Geometry()
    from core import load_roots
    root = load_roots(BASE / 'roots.tsv')[0]
    state = {0: int(root['row'], 16)}
    c, v = encode(actual, state, 1)
    samples, meta = enumerate_projection(actual, state, 1, c, v, 5, 15, 100, 100, 42)
    assert samples and meta['status'] == 'LIMIT_UNRESOLVED'
    state[1] = samples[0]
    check_graph99_independent(actual, state)
    for repeat in range(30):
        rng = random.Random(repeat)
        rest = list(range(2, 7))
        rng.shuffle(rest)
        sigma = [0, 1] + rest
        if repeat % 2:
            sigma[0], sigma[1] = 1, 0
        flips = [0, 0] + [rng.randrange(2) for _ in range(5)]
        perm = [sigma[a % 7] + 7 * ((a // 7) ^ flips[a % 7]) for a in range(14)]
        hp = [actual.index[tuple(sorted(perm[a] for a in pair))] for pair in actual.labels]
        moved = {hp[u]: sum(1 << hp[w] for w in range(84) if (row >> w) & 1) for u, row in state.items()}
        actual.verify(moved)
        assert actual.key(state) == actual.key(moved)
    c, v = encode(g, {0: full[0]}, 1)
    artifact = out / 'valid_proof'
    samples, meta = enumerate_projection(g, {0: full[0]}, 1, c, v, 5, 15, 100, 100, 1, artifact)
    proof = certify(artifact, BASE / 'bin' / 'drat-trim', 5)
    assert proof['certified']
    fixture = json.loads((BASE / 'fixtures' / 'trivial_unsat_state.json').read_text())
    fixture_rows = unpack(fixture['rows'])
    fcnf, fvars = encode(actual, fixture_rows, fixture['target'])
    _, fmeta = enumerate_projection(actual, fixture_rows, fixture['target'], fcnf, fvars,
                                    5, 15, 100, 100, 1, out / 'trivial_proof')
    assert fmeta['count'] == 0 and fmeta['status'] == 'PROJECTED_ENUMERATION_COMPLETE'
    trivial = certify(out / 'trivial_proof', BASE / 'bin' / 'drat-trim', 5)
    assert trivial['certified'] and trivial['trivial_unsat_exit_bug_independently_checked']
    # Corrupting stored enumeration must be caught BEFORE certificate generation.
    original = (artifact / 'rows.txt').read_bytes()
    (artifact / 'rows.txt').write_bytes(original + b'0x0\n')
    try:
        certify(artifact, BASE / 'bin' / 'drat-trim', 5)
        raise AssertionError('corrupt enumeration accepted')
    except ValueError:
        pass
    (artifact / 'rows.txt').write_bytes(original)
    # False proof of a satisfiable formula is rejected by independent checker.
    (out / 'sat.cnf').write_text('p cnf 1 1\n1 0\n')
    (out / 'false.drat').write_text('0\n')
    bad = subprocess.run([str(BASE / 'bin' / 'drat-trim'), str(out / 'sat.cnf'), str(out / 'false.drat')],
                         capture_output=True)
    assert bad.returncode != 0 or b'VERIFIED' not in bad.stdout
    # Tiny limit must not produce exhaustion, even if it happens to see all rows.
    _, limited = enumerate_projection(g, {0: full[0]}, 1, c, v, 5, 15, 1, 1, 1)
    assert limited['status'] == 'LIMIT_UNRESOLVED'
    # Actual native solve interrupt; conservative UNKNOWN, not contradiction.
    cglobal, vglobal = encode(actual, {0: int(root['row'], 16)})
    _, interrupted = enumerate_projection(actual, {0: int(root['row'], 16)}, 1,
                                          cglobal, vglobal, 0.02, 1, 100, 1, 1)
    assert interrupted['status'] == 'LIMIT_UNRESOLVED'
    check_graph99_independent(g, full)
    result = {'status': 'PASS', 'independent_tiny_projection_comparisons': checks,
              'canonical_relabel_tests': 30, 'independent_full_adjacency_check': 'PASS',
              'drat_positive': 'PASS', 'trivial_unsat_exit_bug_control': 'PASS', 'drat_false_proof_rejected': 'PASS',
              'corrupt_enumeration_rejected': 'PASS', 'tiny_limit_unknown': 'PASS',
              'native_interrupt_unknown': 'PASS', 'operational': 'NOT_RUN'}
    if operational:
        cfg = json.loads((BASE / 'config.json').read_text())
        cfg.update({'workers': 2, 'job_cpu_s': 1.0, 'node_cpu_s': 0.3, 'projection_cap': 256,
                    'beam_width': 4, 'row_reservoir': 4, 'target_depth': 4,
                    'proofs_per_job': 0, 'free_disk_reserve_gib': 0.01,
                    'available_memory_reserve_gib': 0.1, 'emergency_available_gib': 0.01,
                    'report_s': 600})
        campaign = out / 'mini_campaign'
        (campaign / 'jobs').mkdir(parents=True)
        names = ['normal', 'local_error']
        atomic(campaign / 'manifest.json', {'jobs': names, 'config': cfg})
        for name in names:
            atomic(campaign / 'jobs' / (name + '.json'), {
                'root_id': root['id'], 'row': root['row'] if name == 'normal' else '0x0',
                'arm': 'dynamic', 'seed': 81, 'config': cfg})
        (campaign / 'jobs' / 'local_error.json').write_text('{malformed-json')
        checked = subprocess.run([sys.executable, str(BASE / 'campaign.py'), str(campaign), '--test'],
                                 capture_output=True, timeout=60)
        (out / 'operational.log').write_bytes(checked.stdout + checked.stderr)
        assert checked.returncode == 0, checked.stderr.decode()
        receipts = json.loads((campaign / 'receipts.json').read_text())
        assert len(receipts) == 2 and sum(r['cpu_s'] for r in receipts) > 0
        assert not (campaign / 'session_open.json').exists()
        # Independent isolated exception test: malformed input is visible and
        # does not become a completed proof. It intentionally triggers integrity stop.
        assert any(r['exit'] != 0 for r in receipts)
        assert any(r['job'] == 'normal' and r['exit'] == 0 and r['status'] != 'PAUSED' for r in receipts)
        result['operational'] = 'PASS_REAL_PROCESSES_WAIT4_AND_LOCAL_ERROR_ISOLATION'
    atomic(out / 'controls.json', result)
    return result


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--out')
    a = p.parse_args()
    print(json.dumps(run_tests(a.out)), flush=True)
