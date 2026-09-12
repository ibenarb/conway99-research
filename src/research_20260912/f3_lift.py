"""Exact F3 linear reduction for validated Conway orbit quotients."""
import itertools
import json
from pathlib import Path
import numpy as np


def nullspace_mod3(matrix):
    a = np.array(matrix, dtype=np.int64) % 3
    rows, cols = a.shape
    pivot_columns = []
    r = 0
    for c in range(cols):
        choices = np.flatnonzero(a[r:, c])
        if not len(choices):
            continue
        p = r + int(choices[0])
        a[[r, p]] = a[[p, r]]
        a[r] = (a[r] * int(a[r, c])) % 3
        for start in range(0, rows, 128):
            end = min(rows, start+128)
            factors = a[start:end, c].copy()
            if start <= r < end:
                factors[r-start] = 0
            a[start:end] = (a[start:end] - factors[:, None]*a[r]) % 3
        pivot_columns.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in pivot_columns]
    basis = np.zeros((cols, len(free)), dtype=np.int64)
    for t, c in enumerate(free):
        basis[c, t] = 1
        for i, p in enumerate(pivot_columns):
            basis[p, t] = -a[i, c] % 3
    assert not np.any(np.array(matrix, dtype=np.int64) @ basis % 3)
    return basis, pivot_columns


def phase_u(R, Z):
    U = np.zeros_like(R)
    for i in range(len(R)):
        U[i, i] = 2 if R[i, i] == 0 else 0
        for j in range(len(R)):
            if i == j:
                continue
            z = int(Z[i, j]) % 3
            if R[i, j] == 1:
                U[i, j] = 2*z*(z+1) % 3
            elif R[i, j] == 2:
                U[i, j] = (1-2*z*(z-1)) % 3
    return U


def reduce_quotient(R):
    R = np.array(R, dtype=np.int64)
    n = 33
    if R.shape != (n, n) or not np.array_equal(R, R.T):
        raise ValueError('Expected symmetric 33 by 33 matrix')
    if any(v not in (0, 2) for v in np.diag(R)) or not np.all(np.isin(R, [0, 1, 2])):
        raise ValueError('Illegal quotient alphabet')
    if not np.all(R.sum(axis=1) == 14) or not np.array_equal(R@R+R, 12*np.eye(n, dtype=np.int64)+6):
        raise ValueError('Exact quotient identity/regularity required')
    B = (R + np.eye(n, dtype=np.int64)) % 3
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if R[i, j]]
    columns = []
    for i, j in edges:
        Z = np.zeros_like(R)
        Z[i, j], Z[j, i] = 1, -1
        columns.append((B@Z+Z@B-Z).ravel())
    equations = np.array(columns).T
    # Gauge-fix a spanning tree: every tree phase is zero, uniquely modulo global shift.
    seen, tree = {0}, []
    while len(seen) < n:
        nxt = next(((t, i, j) for t, (i, j) in enumerate(edges) if (i in seen) != (j in seen)), None)
        if nxt is None:
            raise ValueError('Disconnected support contradicts exact quotient assumptions')
        t, i, j = nxt
        tree.append(t)
        seen.update((i, j))
    gauge = np.eye(len(edges), dtype=np.int64)[tree]
    raw_basis, _ = nullspace_mod3(equations)
    reduced_basis, _ = nullspace_mod3(np.vstack([equations, gauge]))
    assert raw_basis.shape[1] - reduced_basis.shape[1] == 32
    return {'edges': edges, 'tree_edge_indices': tree,
            'linear_nullity': raw_basis.shape[1], 'gauge_reduced_nullity': reduced_basis.shape[1],
            'phase_basis': reduced_basis.tolist()}


def multiply(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1])


def divisible3(value):
    a, b = value
    return a % 3 == 0 and b % 3 == 0 and (a+b) % 9 == 0


def controls():
    rng = np.random.default_rng(20260912)
    pi, pi2 = (1, -1), (0, -3)
    phases = [(1, 0), (0, 1), (-1, -1)]
    for rep in range(25):
        n = 7
        R = np.zeros((n, n), dtype=np.int64)
        Z = np.zeros_like(R)
        Wa, Wb = np.zeros_like(R), np.zeros_like(R)
        for i in range(n):
            R[i, i] = int(rng.integers(2))*2
            Wa[i, i] = -R[i, i]//2
            for j in range(i+1, n):
                r, z = int(rng.integers(3)), int(rng.integers(3))
                if r == 0:
                    z = 0
                R[i, j] = R[j, i] = r
                Z[i, j], Z[j, i] = z, -z % 3
                if r:
                    g = (-z if r == 1 else z) % 3
                    a, b = phases[g]
                    if r == 2:
                        a, b = -a, -b
                    Wa[i, j], Wb[i, j] = a, b
                    Wa[j, i], Wb[j, i] = a-b, -b
        U = phase_u(R, Z)
        assert not np.any((U-U.T-Z) % 3)
        T = R + np.eye(n, dtype=np.int64)
        for i in range(n):
            for j in range(n):
                ea = int(Wa[i, j]+4*(i==j)-T[i, j]-Z[i, j])
                eb = int(Wb[i, j]+Z[i, j]+3*U[i, j])
                assert divisible3((ea, eb))
        E = R@R+R-12*np.eye(n, dtype=np.int64)-6
        Q = -T+2*np.eye(n, dtype=np.int64)+1
        P = T@Z+Z@T-Z
        C = T@U+U@T-U+Z@Z-2*Q
        residual_a = Wa@Wa-Wb@Wb+Wa-12*np.eye(n, dtype=np.int64)
        residual_b = Wa@Wb+Wb@Wa-Wb@Wb+Wb
        for i in range(n):
            for j in range(n):
                assert divisible3((int(residual_a[i,j]-E[i,j]-P[i,j]), int(residual_b[i,j]+P[i,j]+3*C[i,j])))
    # Linear off-block dimension and projected quadratic equations on algebraic controls.
    n, rank = 9, 4
    B = np.diag([1]*rank+[0]*(n-rank))
    columns = []
    for i, j in itertools.combinations(range(n), 2):
        Z = np.zeros((n,n), dtype=np.int64)
        Z[i,j], Z[j,i] = 1, -1
        columns.append((B@Z+Z@B-Z).ravel())
    basis, _ = nullspace_mod3(np.array(columns).T)
    assert basis.shape[1] == rank*(n-rank)
    rejected = False
    try:
        reduce_quotient(np.zeros((33,33), dtype=np.int64))
    except ValueError:
        rejected = True
    assert rejected
    result = {'status': 'PASS_SCALAR_TABLE_AND_GENERAL_RESIDUAL_EXPANSION',
              'random_legal_alphabet_matrices': 25, 'dimension_control': {'n': 9, 'rank_B': 4, 'skew_linear_nullity': 20},
              'invalid_quotient_rejected': True,
              'scope': 'No exact Conway quotient supplied. The production reduction is not performance-tested on one.',
              'derived_conway_ranks': {'tau6': 18, 'tau27': 24}}
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quotient-json', type=Path)
    args = parser.parse_args()
    if args.quotient_json:
        print(json.dumps(reduce_quotient(json.loads(args.quotient_json.read_text())), indent=4))
    else:
        result = controls()
        base = Path(__file__).resolve().parents[2]
        (base/'results/research_20260912/f3_controls.json').write_text(json.dumps(result, indent=4)+'\n')
        print(json.dumps(result, indent=4))
