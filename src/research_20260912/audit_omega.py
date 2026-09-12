"""Exact Omega identities on all saved starters; floating spectra diagnostic only."""
from pathlib import Path
import json
import sys
import numpy as np

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'src/memetic_v2'))
from core import decode_g6, validate, OUTER

P = np.array([[int(i in pair) for pair in OUTER] for i in range(14)], dtype=np.int64)
M = np.array([[int(j == (i+7) % 14) for j in range(14)] for i in range(14)], dtype=np.int64)
I14 = np.eye(14, dtype=np.int64)
J14 = np.ones((14, 14), dtype=np.int64)
K = J14 - I14 - M
Ginv240 = 22*I14 + 2*M - J14
assert np.array_equal((P @ P.T) @ Ginv240, 240*I14)
projector240 = 240*np.eye(84, dtype=np.int64) - P.T @ Ginv240 @ P
assert np.array_equal(projector240 @ projector240, 240*projector240)
assert np.trace(projector240) == 240*70
candidates = json.loads((BASE / 'data/memetic_v2/reference/population64.json').read_text())['candidates']
results = []
for item in candidates:
    rows = decode_g6(item['g6'])
    validate(rows, item['arm'])
    A = np.array([[(r >> j) & 1 for j in range(99)] for r in rows], dtype=np.int64)
    E = A @ A + A - 12*np.eye(99, dtype=np.int64) - 2
    assert not np.any(E.sum(axis=1))
    if item['arm'] != 'omega':
        continue
    H = A[15:, 15:]
    assert np.array_equal(H @ P.T, P.T @ K)
    assert not np.any(E[:15]) and not np.any(E[:, :15])
    EH = E[15:, 15:]
    assert not np.any(EH @ P.T)
    assert np.array_equal(projector240 @ EH, 240*EH)
    freeH240 = projector240 @ H
    assert np.trace(freeH240) == 0
    assert np.trace(freeH240 @ freeH240) == 840*240**2
    assert np.array_equal(H @ EH, EH @ H)
    # A fixed orthonormal basis for ker(P), for diagnostic eigenvalues only.
    _, _, vh = np.linalg.svd(P.astype(float), full_matrices=True)
    N = vh[14:].T
    eig = np.linalg.eigvalsh(N.T @ H @ N)
    target = np.array([-4]*30 + [3]*40)
    bound = float(np.sum((eig-target)**2)/2)
    results.append({'founder': item.get('founder'), 'F': int(np.sum(E*E)//2),
                    'spectral_edge_distance_lower_bound_float': bound})
output = {'status': 'PASS_EXACT_INTEGER_IDENTITIES', 'omega_candidates': len(results),
          'P_rank': 14, 'kernel_dimension': 70, 'fixed_A_spectrum': {'14': 1, '3': 14, '-4': 14},
          'required_free_spectrum': {'3': 40, '-4': 30}, 'free_trace': 0, 'free_square_trace': 840,
          'scope': 'Spectral distance numbers use floating point and are diagnostic, not certified pruning bounds.',
          'candidates': results}
(BASE / 'results/research_20260912/omega_algebra.json').write_text(json.dumps(output, indent=4)+'\n')
print(json.dumps({k: v for k, v in output.items() if k != 'candidates'}, indent=4))
