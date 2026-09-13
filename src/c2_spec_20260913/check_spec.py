"""Exact integer controls for the C2 specification; no Conway99 search."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


def eq(a, b):
    return bool(np.array_equal(a, b))


def frame(k):
    labels = [p for p in itertools.combinations(range(k), 2) if p[1] != (p[0] ^ 1)]
    tau = {p: tuple(sorted(a ^ 1 for a in p)) for p in labels}
    reps = sorted(p for p in labels if p < tau[p])
    order = reps + [tau[p] for p in reps]
    r = np.array([[int(a in p) for a in range(k)] for p in order], dtype=np.int64)
    w = r[:len(reps), 0::2] + r[:len(reps), 1::2]
    v = r[:len(reps), 0::2] - r[:len(reps), 1::2]
    km = np.eye(k, dtype=np.int64)[:, np.arange(k) ^ 1]
    return order, r, w, v, km


def graph(r, km, m):
    k, n = len(km), len(m)
    a = np.zeros((1 + k + n, 1 + k + n), dtype=np.int64)
    a[0, 1:1+k] = a[1:1+k, 0] = 1
    a[1:1+k, 1:1+k] = km
    a[1+k:, 1:1+k], a[1:1+k, 1+k:] = r, r.T
    a[1+k:, 1+k:] = m
    return a


def outer_ok(k, r, km, m):
    n = len(m)
    return all((eq(m.sum(axis=1), np.full(n, k - 2)),
                eq(m @ r, np.full((n, k), 2) - r @ (km + np.eye(k, dtype=np.int64))),
                eq(m @ m + m, (k - 2) * np.eye(n, dtype=np.int64) + 2 - r @ r.T)))


def full_ok(k, a):
    return eq(a @ a + a, (k - 2) * np.eye(len(a), dtype=np.int64) + 2)


def split_ok(k, w, v, b, c):
    q, d = b + c, b - c
    n, h = w.shape
    return all((eq(q.sum(axis=1), np.full(n, k - 2)),
                eq(q @ w, np.full((n, h), 4) - 2 * w),
                eq(d @ v, np.zeros((n, h), dtype=np.int64)),
                eq(q @ q + q, (k - 2) * np.eye(n, dtype=np.int64) + 4 - w @ w.T),
                eq(d @ d + d, (k - 2) * np.eye(n, dtype=np.int64) - v @ v.T)))


def residual_control(k, r, w, v, km, b, c):
    n = len(b)
    m = np.block([[b, c], [c, b]])
    q, d = b + c, b - c
    e = m @ m + m - ((k - 2) * np.eye(2*n, dtype=np.int64) + 2 - r @ r.T)
    ep = q @ q + q - ((k - 2) * np.eye(n, dtype=np.int64) + 4 - w @ w.T)
    em = d @ d + d - ((k - 2) * np.eye(n, dtype=np.int64) - v @ v.T)
    assert eq(e[:n, :n] + e[:n, n:], ep)
    assert eq(e[:n, :n] - e[:n, n:], em)
    z = m @ r - (2 - r @ (km + np.eye(k, dtype=np.int64)))
    assert eq(z[:n, 0::2] + z[:n, 1::2], q @ w - (4 - 2*w))
    assert eq(z[:n, 0::2] - z[:n, 1::2], d @ v)
    a = graph(r, km, m)
    ea = a @ a + a - ((k - 2) * np.eye(len(a), dtype=np.int64) + 2)
    assert eq(ea[1+k:, 1+k:], e)
    assert eq(ea[1+k:, 1:1+k], z)
    assert outer_ok(k, r, km, m) == full_ok(k, a)
    assert split_ok(k, w, v, b, c) == full_ok(k, a)


def main():
    labels, r, w, v, km = frame(14)
    n = len(w)
    assert n == 42 and eq(v.T @ v, 12 * np.eye(7, dtype=np.int64))
    assert eq(w.T @ w, 10 * np.eye(7, dtype=np.int64) + 2)
    assert eq((v*v).sum(axis=1), np.full(n, 2))
    rng = np.random.default_rng(20260913)
    for _ in range(32):
        matrices = []
        for j in range(2):
            z = np.triu(rng.integers(0, 2, size=(n, n), dtype=np.int64), 1)
            matrices.append(z + z.T)
        residual_control(14, r, w, v, km, *matrices)
    small, sr, sw, sv, sk = frame(4)
    edges = list(itertools.combinations(range(4), 2))
    solutions = []
    for bits in itertools.product((0, 1), repeat=len(edges)):
        m = np.zeros((4, 4), dtype=np.int64)
        for (i, j), bit in zip(edges, bits):
            m[i, j] = m[j, i] = bit
        a = graph(sr, sk, m)
        assert outer_ok(4, sr, sk, m) == full_ok(4, a)
        if full_ok(4, a):
            solutions.append(m)
    assert len(solutions) == 1
    m = solutions[0]
    assert eq(m[:2, :2], m[2:, 2:]) and eq(m[:2, 2:], m[2:, :2])
    b, c = m[:2, :2], m[:2, 2:]
    assert split_ok(4, sw, sv, b, c)
    assert eq(b + c, np.array([[0, 2], [2, 0]])) and not np.any(b - c)
    for bits in itertools.product((0, 1), repeat=2):
        b, c = [np.array([[0, z], [z, 0]], dtype=np.int64) for z in bits]
        residual_control(4, sr, sw, sv, sk, b, c)
    # Independent explicit rook graph, then identify it by fixed-frame labels.
    vertices = list(itertools.product(range(3), repeat=2))
    rook = np.array([[int(x != y and (x[0] == y[0] or x[1] == y[1]))
                      for y in vertices] for x in vertices], dtype=np.int64)
    root = (2, 2)
    inner = [(2, 0), (2, 1), (0, 2), (1, 2)]
    outer = [next(x for x in vertices if x != root and x not in inner
                  and tuple(i for i, y in enumerate(inner)
                            if rook[vertices.index(x), vertices.index(y)]) == p) for p in small]
    idx = [vertices.index(x) for x in [root] + inner + outer]
    assert eq(rook[np.ix_(idx, idx)], graph(sr, sk, m))
    report = {
        'status': 'C2_SPEC_CONTROLS_PASS', 'version': '1.0.0',
        'k14_outer_vertices': 84, 'outer_pairs': n, 'primary_bits': n*(n-1),
        'fixed_frame_integer_gram_checks': True, 'random_residual_controls': 32,
        'rook_all_outer_graphs_checked': 64, 'rook_solutions': len(solutions),
        'rook_invariant_assignments_checked': 4, 'independent_rook_match': True,
        'necessary_C2_structure': {'double_edge_matching_size': 21,
                                 'signed_support_degree': 10,
                                 'signed_spectrum': {'0': 7, '3': 20, '-4': 15}},
        'scope': 'Finite controls support the written general algebraic proof; no 99-vertex solution or UNSAT proof.',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    target = Path(__file__).resolve().parents[2] / 'results/c2_spec_20260913/controls.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
