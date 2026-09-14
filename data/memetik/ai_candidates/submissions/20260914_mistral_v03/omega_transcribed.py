# Executable statements transcribed from chat; comments/docstrings omitted.
# Identical supplied graph6 routine imported from lambda_transcribed.
import numpy as np
import sys
from itertools import combinations
from lambda_transcribed import matrix_to_graph6

def generate_omega_candidate() -> str:
    root = 0
    neighbors = list(range(1, 15))
    outer = list(range(15, 99))
    partners = [(i, (i + 7) % 14) for i in range(7)]
    all_pairs = list(combinations(range(14), 2))
    outer_pairs = [p for p in all_pairs if p not in partners]
    P = np.zeros((14, 84), dtype=int)
    for col, (a, b) in enumerate(outer_pairs):
        P[a, col] = 1
        P[b, col] = 1
    C = np.zeros((14, 14), dtype=int)
    for a, b in partners:
        C[a, b] = 1
        C[b, a] = 1
    H = np.zeros((84, 84), dtype=int)
    for i, (a, b) in enumerate(outer_pairs):
        for j, (c, d) in enumerate(outer_pairs):
            if i >= j:
                continue
            if len({a, b} & {c, d}) == 1:
                H[i, j] = 1
                H[j, i] = 1
    A = np.zeros((99, 99), dtype=int)
    for neighbor in neighbors:
        A[root, neighbor] = 1
        A[neighbor, root] = 1
    for i in range(14):
        for j in range(14):
            if C[i, j]:
                A[neighbors[i], neighbors[j]] = 1
    for i in range(14):
        for j in range(84):
            if P[i, j]:
                A[neighbors[i], outer[j]] = 1
                A[outer[j], neighbors[i]] = 1
    for i in range(84):
        for j in range(84):
            if H[i, j]:
                A[outer[i], outer[j]] = 1
    assert np.array_equal(A, A.T), "Graph ist nicht symmetrisch"
    assert np.all(np.diag(A) == 0), "Graph hat Selbstschleifen"
    degrees = np.sum(A, axis=1)
    assert np.all(degrees == 14), f"Grade: {degrees} (erwartet 14)"
    J = np.ones((14, 84))
    I = np.eye(14)
    lhs = P @ H
    rhs = 2 * J - (C + I) @ P
    assert np.array_equal(lhs, rhs), "Ω-Rahmenbedingung nicht erfüllt"
    return matrix_to_graph6(A)

def main():
    try:
        graph6 = generate_omega_candidate()
        print(graph6)
    except AssertionError as e:
        print(f"NO_CANDIDATE_FOUND: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
