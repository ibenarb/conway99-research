import sys
import numpy as np
import networkx as nx
from ortools.sat.python import cp_model

def build_C():
    """Erzeugt die 14x14 Matrix C (perfektes Matching mit Partner a <-> a+7 mod 14)."""
    C = np.zeros((14, 14), dtype=int)
    for i in range(14):
        C[i, (i + 7) % 14] = 1
    return C

def build_P_and_labels():
    """Erzeugt die 14x84 Matrix P und die lexikographisch sortierten Labels."""
    labels = []
    for a in range(14):
        for b in range(a + 1, 14):
            if b != (a + 7) % 14 and a != (b + 7) % 14:
                labels.append((a, b))
    
    # Lexikographische Sortierung sicherstellen
    labels.sort()
    
    P = np.zeros((14, 84), dtype=int)
    for j, (a, b) in enumerate(labels):
        P[a, j] = 1
        P[b, j] = 1
        
    return P, labels

def evaluate_graph(A):
    """
    Evaluiert die Adjazenzmatrix A bezüglich srg(99,14,1,2).
    Berechnet die Fehlerkoeffizienten r_ij = (A^2)_ij + A_ij - 2.
    """
    A2 = A @ A
    
    W = 0
    L1 = 0
    F = 0
    Linf = 0
    
    # Auswertung nur für Knotenpaare u < v
    for u in range(99):
        for v in range(u + 1, 99):
            r = A2[u, v] + A[u, v] - 2
            if r != 0:
                W += 1
            L1 += abs(r)
            F += r * r
            Linf = max(Linf, abs(r))
            
    return W, L1, F, Linf

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(f"Starte Ω-Suchraum Generator mit Seed {seed}...")
    
    C = build_C()
    P, labels = build_P_and_labels()
    
    I = np.eye(14, dtype=int)
    J = np.ones((14, 84), dtype=int)
    
    # Zielmatrix T für die Gleichung PH = T
    T = 2 * J - (C + I) @ P
    
    model = cp_model.CpModel()
    
    # H Variablen anlegen (symmetrisch, Nulldiagonale)
    H_vars = {}
    for i in range(84):
        for j in range(i, 84):
            if i == j:
                H_vars[i, j] = model.NewConstant(0)
            else:
                var = model.NewBoolVar(f'H_{i}_{j}')
                H_vars[i, j] = var
                H_vars[j, i] = var
                
    # Constraint 1: Zeilensumme = 12
    for i in range(84):
        model.Add(sum(H_vars[i, j] for j in range(84)) == 12)
        
    # Constraint 2: PH = 2J - (C+I)P = T
    for k in range(14):
        for j in range(84):
            # T[k, j] ist aus {0, 1, 2}, CP-SAT verlangt explizite Python ints
            target_val = int(T[k, j])
            # Skalarprodukt der Zeile k von P mit Spalte j von H
            model.Add(
                sum(int(P[k, i]) * H_vars[i, j] for i in range(84)) == target_val
            )
            
    # Solver Konfiguration
    solver = cp_model.CpSolver()
    solver.parameters.randomize_search = True
    solver.parameters.random_seed = seed
    # Zeitlimit setzen, falls die Suche auf bestimmten Architekturen hängt
    solver.parameters.max_time_in_seconds = 3600.0 
    
    print("Modell erstellt. Beginne Lösungssuche (CSP)...")
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("Lösung im Ω-Suchraum gefunden!")
        
        # H Matrix extrahieren
        H = np.zeros((84, 84), dtype=int)
        for i in range(84):
            for j in range(84):
                H[i, j] = solver.Value(H_vars[i, j])
                
        # Vollständige 99x99 Adjazenzmatrix A konstruieren
        A = np.zeros((99, 99), dtype=int)
        
        # Block 1: Spitze zu C (1..14)
        A[0, 1:15] = 1
        A[1:15, 0] = 1
        
        # Block 2: C (1..14)
        A[1:15, 1:15] = C
        
        # Block 3: P (1..14 zu 15..98)
        A[1:15, 15:99] = P
        A[15:99, 1:15] = P.T
        
        # Block 4: H (15..98)
        A[15:99, 15:99] = H
        
        # Evaluierung
        W, L1, F, Linf = evaluate_graph(A)
        print("\n--- BEWERTUNG ---")
        print(f"W (Anzahl Abweichungen) = {W}")
        print(f"L1 (Absolute Abweichung) = {L1}")
        print(f"F (Quadratische Abw.)  = {F}")
        print(f"Linf (Maximale Abw.)   = {Linf}")
        
        # Graph6 Export
        G = nx.from_numpy_array(A)
        filename = f"kandidat_{seed:02d}.g6"
        # NetworkX schreibt per Default ein newline. Header (>>graph6<<) standardmäßig weggelassen bei dieser Methode.
        nx.write_graph6(G, filename, header=False)
        print(f"\nGraph exportiert nach: {filename}")
        
    else:
        print("Keine Lösung mit diesem Seed im Zeitlimit gefunden.")

if __name__ == "__main__":
    main()
