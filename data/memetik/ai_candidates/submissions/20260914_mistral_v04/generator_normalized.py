import numpy as np
import sys
from itertools import combinations

def build_omega_frame():
    """
    Baut den kanonischen Ω-Rahmen:
    - Wurzel: 0
    - Nachbarn: 1-14 (Labels 0-13)
    - Außenknoten: 15-98 (84 Knoten, Paare {a,b} mit a < b, ausgenommen Partnerpaare)
    Returns:
        P (14x84): Inzidenzmatrix
        C (14x14): Partnerkantenmatrix
        outer_pairs: Liste der Außenpaare (als Tupel (a,b))
    """
    # Nachbarn: 1-14 (Labels 0-13)
    neighbors = list(range(1, 15))

    # Partnerpaare: {0,7}, {1,8}, ..., {6,13}
    partners = [(i, (i + 7) % 14) for i in range(7)]

    # Alle Paare {a,b} mit a < b
    all_pairs = list(combinations(range(14), 2))
    # Außenpaare: alle Paare außer Partnerpaaren
    outer_pairs = [p for p in all_pairs if p not in partners]

    # Inzidenzmatrix P (14 x 84)
    P = np.zeros((14, 84), dtype=int)
    for col, (a, b) in enumerate(outer_pairs):
        P[a, col] = 1
        P[b, col] = 1

    # Partnerkantenmatrix C (14 x 14)
    C = np.zeros((14, 14), dtype=int)
    for a, b in partners:
        C[a, b] = 1
        C[b, a] = 1

    return P, C, outer_pairs

def check_omega_conditions(H, P, C, i, j):
    """
    Prüft, ob das Setzen von H[i,j] = 1 die Ω-Bedingungen verletzt.
    Args:
        H: Aktuelle H-Matrix (84x84)
        P: Inzidenzmatrix (14x84)
        C: Partnerkantenmatrix (14x14)
        i, j: Indizes der geänderten Zelle (i < j)
    Returns:
        True, falls keine Bedingung verletzt wird.
    """
    n_outer = H.shape[0]
    J = np.ones((14, 84))
    I = np.eye(14)
    target = 2 * J - (C + I) @ P

    # Aktualisiere die betroffenen Zeilen von PH
    # Nur die Zeilen a, für die P[a,i] oder P[a,j] = 1, sind betroffen
    affected_rows = set()
    for a in range(14):
        if P[a, i] == 1 or P[a, j] == 1:
            affected_rows.add(a)

    # Prüfe für jede betroffene Zeile a und alle Spalten k
    for a in affected_rows:
        for k in range(n_outer):
            # Berechne (PH)[a,k] = sum_l P[a,l] * H[l,k]
            lhs = np.sum(P[a] * H[:, k])
            rhs = target[a, k]
            if lhs != rhs:
                return False
    return True

def backtrack_omega(H, P, C, degrees, step, max_steps):
    """
    Backtracking-Algorithmus für H-Matrix.
    Args:
        H: Aktuelle H-Matrix (84x84)
        P: Inzidenzmatrix (14x84)
        C: Partnerkantenmatrix (14x14)
        degrees: Aktuelle Grade der Außenknoten (84,)
        step: Aktuelle Rekursionstiefe
        max_steps: Maximale Rekursionstiefe
    Returns:
        H (84x84) falls erfolgreich, sonst None.
    """
    if step > max_steps:
        return None

    n_outer = H.shape[0]
    # Finde die erste Zelle (i,j) mit i < j und H[i,j] = 0
    for i in range(n_outer):
        for j in range(i + 1, n_outer):
            if H[i, j] == 0:
                # Option 1: Setze H[i,j] = 1
                if degrees[i] < 12 and degrees[j] < 12:
                    H[i, j] = 1
                    H[j, i] = 1
                    degrees[i] += 1
                    degrees[j] += 1

                    # Prüfe Ω-Bedingungen
                    if check_omega_conditions(H, P, C, i, j):
                        result = backtrack_omega(H, P, C, degrees, step + 1, max_steps)
                        if result is not None:
                            return result

                    # Backtrack
                    H[i, j] = 0
                    H[j, i] = 0
                    degrees[i] -= 1
                    degrees[j] -= 1

                # Option 2: Behalte H[i,j] = 0 (implizit, da bereits 0)
                # Keine Aktion nötig, da H[i,j] bereits 0 ist.
                # Wir versuchen die nächste Zelle.
                return backtrack_omega(H, P, C, degrees, step + 1, max_steps)

    # Alle Zellen gesetzt: Prüfe finale Bedingungen
    if np.all(degrees == 12):
        # Vollständige Prüfung der Ω-Bedingung
        J = np.ones((14, 84))
        I = np.eye(14)
        target = 2 * J - (C + I) @ P
        if np.array_equal(P @ H, target):
            return H.copy()
    return None

def matrix_to_graph6(A):
    """
    Konvertiert eine Adjazenzmatrix (99x99) in graph6-Format.
    Korrektur: Header für n=99 ist '~?@b'.
    """
    n = A.shape[0]
    if n == 99:
        header = '~?@b'
    else:
        if n <= 62:
            header = chr(63 + n)
        else:
            k = (n - 1) // 6
            r = (n - 1) % 6
            header = chr(63 + k) + chr(63 + r)

    # Lexikographische Paarreihenfolge: (0,1),(0,2),(1,2),(0,3),...
    bits = []
    for i in range(n):
        for j in range(i + 1, n):
            bits.append('1' if A[i, j] else '0')
    # Pad to multiple of 6
    while len(bits) % 6 != 0:
        bits.append('0')
    # Konvertiere zu graph6-Zeichen (MSB first)
    graph6 = []
    for i in range(0, len(bits), 6):
        byte = int(''.join(bits[i:i+6]), 2)
        graph6.append(chr(63 + byte))
    return header + ''.join(graph6)

def build_full_adjacency(H, P, outer_pairs, neighbors):
    """
    Baut die vollständige Adjazenzmatrix A (99x99) aus H, P und dem Rahmen.
    Args:
        H: H-Matrix (84x84)
        P: Inzidenzmatrix (14x84)
        outer_pairs: Liste der Außenpaare
        neighbors: Liste der Nachbar-Knoten (1-14)
    Returns:
        A: Adjazenzmatrix (99x99)
    """
    n = 99
    root = 0
    outer = list(range(15, 99))  # 15-98
    A = np.zeros((n, n), dtype=int)

    # 1. Wurzel mit Nachbarn verbinden
    for neighbor in neighbors:
        A[root, neighbor] = 1
        A[neighbor, root] = 1

    # 2. Nachbarn untereinander (C: Partnerkanten)
    partners = [(i, (i + 7) % 14) for i in range(7)]
    for a, b in partners:
        A[neighbors[a], neighbors[b]] = 1
        A[neighbors[b], neighbors[a]] = 1

    # 3. Nachbarn mit Außenknoten (P)
    for i in range(14):
        for j in range(84):
            if P[i, j]:
                A[neighbors[i], outer[j]] = 1
                A[outer[j], neighbors[i]] = 1

    # 4. Außenknoten untereinander (H)
    for i in range(84):
        for j in range(84):
            if H[i, j]:
                A[outer[i], outer[j]] = 1

    return A

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    max_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000

    np.random.seed(seed)

    # Baue Ω-Rahmen
    P, C, outer_pairs = build_omega_frame()
    n_outer = 84

    # Initialisiere H und Grade
    H = np.zeros((n_outer, n_outer), dtype=int)
    degrees = np.zeros(n_outer, dtype=int)

    # Backtracking
    result_H = backtrack_omega(H, P, C, degrees, 0, max_steps)

    if result_H is None:
        print("NO_CANDIDATE_FOUND")
        sys.exit(1)

    # Baue vollständige Adjazenzmatrix
    neighbors = list(range(1, 15))
    A = build_full_adjacency(result_H, P, outer_pairs, neighbors)

    # Prüfung der Aufnahmebedingungen
    # 1. Einfach und ungerichtet
    assert np.array_equal(A, A.T), "Graph ist nicht symmetrisch"
    assert np.all(np.diag(A) == 0), "Graph hat Selbstschleifen"

    # 2. 14-Regularität
    degrees_full = np.sum(A, axis=1)
    assert np.all(degrees_full == 14), f"Grade: {degrees_full} (erwartet 14)"

    # 3. Ω-Rahmenbedingung
    J = np.ones((14, 84))
    I = np.eye(14)
    target = 2 * J - (C + I) @ P
    assert np.array_equal(P @ result_H, target), "Ω-Rahmenbedingung nicht erfüllt"

    # 4. graph6-Kodierung
    graph6 = matrix_to_graph6(A)
    print(graph6)

if __name__ == "__main__":
    main()
