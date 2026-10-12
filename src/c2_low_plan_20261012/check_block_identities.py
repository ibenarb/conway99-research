"""Compare proposed interface residuals with direct 99-vertex matrix residuals.
Random matrices are not graph solutions. This checks the derived block identities.
"""
import itertools
import json
from pathlib import Path
import sys
import numpy as np


def matching_matrix(rng):
    order = rng.permutation(12)
    m = np.zeros((12, 12), dtype=np.int64)
    for a, b in order.reshape(-1, 2):
        m[a, b] = m[b, a] = 1
    return m


def main(destination):
    rng = np.random.default_rng(20261012)
    labels = [(c, d) for c, d in itertools.combinations(range(12), 2) if d != (c ^ 1)]
    index = {pair: i for i, pair in enumerate(labels)}
    t = np.zeros((60, 60), dtype=np.int64)
    rz = np.zeros((60, 12), dtype=np.int64)
    p = np.zeros((12, 12), dtype=np.int64)
    for i in range(12):
        p[i, i ^ 1] = 1
    for i, (c, d) in enumerate(labels):
        t[i, index[tuple(sorted((c ^ 1, d ^ 1)))]] = 1
        rz[i, c] = rz[i, d] = 1
    for trial in range(50):
        l, n = matching_matrix(rng), matching_matrix(rng)
        x = rng.integers(0, 2, size=(12, 60), dtype=np.int64)
        h = rng.integers(0, 2, size=(60, 60), dtype=np.int64)
        h = np.maximum(h, h.T)
        h = np.maximum(h, t @ h @ t)
        np.fill_diagonal(h, 0)
        h[t == 1] = 0
        graph = np.zeros((99, 99), dtype=np.int64)
        graph[0, 1:15] = graph[1:15, 0] = 1
        for c in range(14):
            graph[1 + c, 1 + (c ^ 1)] = 1
        for i in range(12):
            for v, anchors in [(15 + i, (1, 3 + i)), (27 + i, (2, 3 + (i ^ 1)))]:
                for a in anchors:
                    graph[v, a] = graph[a, v] = 1
        for i, (c, d) in enumerate(labels):
            for a in (3 + c, 3 + d):
                graph[39 + i, a] = graph[a, 39 + i] = 1
        graph[15:, 15:] = np.block([[l, n, x], [n, l, x @ t], [x.T, t @ x.T, h]])
        residual = graph @ graph + graph - 12 * np.eye(99, dtype=np.int64) - 2
        a = 9 * np.eye(12, dtype=np.int64) + np.ones((12, 12), dtype=np.int64) - l
        k = 2 * np.ones((12, 12), dtype=np.int64) - p - n - l @ n - n @ l
        demands = 2 * np.ones((12, 12), dtype=np.int64) - np.eye(12, dtype=np.int64) - p - l - n @ p
        assert np.array_equal(residual[15:27, 15:27], x @ x.T - a)
        assert np.array_equal(residual[15:27, 27:39], x @ t @ x.T - k)
        assert np.array_equal(residual[15:27, 3:15], x @ rz - demands)
        assert np.array_equal(residual[15:27, 39:], l @ x + n @ x @ t + x @ h + x - (2 - rz.T))
    report = {'status': 'PASS', 'random_seed': 20261012, 'trials': 50,
              'identities_checked': ['XXt', 'XTXt', 'XRz', 'Wa_to_Z'],
              'scope': 'Algebraic residual identity checks against directly assembled matrices, not existence or UNSAT checks.'}
    Path(destination).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main(sys.argv[1])
