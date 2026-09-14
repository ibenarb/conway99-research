# Executable statements transcribed from chat; comments/docstrings omitted.
# Only copying escape in bits[i\:i+6] normalized to bits[i:i+6].
import numpy as np
import sys

def construct_circular_graph(n: int = 99, differences: list = None) -> np.ndarray:
    if differences is None:
        differences = [1, 2, 4, 8, 16, 32, 64]
    A = np.zeros((n, n), dtype=int)
    for i in range(n):
        for d in differences:
            j1 = (i + d) % n
            j2 = (i - d) % n
            A[i, j1] = 1
            A[i, j2] = 1
    np.fill_diagonal(A, 0)
    return A

def check_lambda_condition(A: np.ndarray) -> bool:
    A2 = A @ A
    n = A.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1 and A2[i, j] != 1:
                return False
    return True

def check_regularity(A: np.ndarray, degree: int = 14) -> bool:
    degrees = np.sum(A, axis=1)
    return np.all(degrees == degree)

def matrix_to_graph6(A: np.ndarray) -> str:
    n = A.shape[0]
    if n <= 62:
        header = chr(63 + n)
    else:
        k = (n - 1) // 6
        r = (n - 1) % 6
        header = chr(63 + k) + chr(63 + r)
    bits = []
    for i in range(n):
        for j in range(i + 1, n):
            bits.append('1' if A[i, j] else '0')
    while len(bits) % 6 != 0:
        bits.append('0')
    graph6 = []
    for i in range(0, len(bits), 6):
        byte = int(''.join(bits[i:i+6]), 2)
        graph6.append(chr(63 + byte))
    return header + ''.join(graph6)

def main():
    n = 99
    D = [1, 2, 4, 8, 16, 32, 64]
    A = construct_circular_graph(n, D)
    assert A.shape == (n, n), f"Falsche Matrixdimension: {A.shape}"
    assert np.array_equal(A, A.T), "Graph ist nicht symmetrisch"
    assert np.all(np.diag(A) == 0), "Graph hat Selbstschleifen"
    assert check_regularity(A, 14), "Graph ist nicht 14-regulär"
    if not check_lambda_condition(A):
        print("NO_CANDIDATE_FOUND")
        sys.exit(1)
    graph6 = matrix_to_graph6(A)
    print(graph6)

if __name__ == "__main__":
    main()
