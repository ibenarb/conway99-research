#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generator.py  --  Startkandidaten fuer srg(99,14,1,2)  (Conway-99-Problem)

Erzeugt drei Kandidaten:

  A : Omega-Suchraum, H invariant unter der Translation a -> a+1 auf Z_14
  B : Omega-Suchraum, ohne auferlegte Symmetrie (LNS-Drift aus A, F-Optimierung)
  C : lambda-Suchraum, randomisierte Dreieckszerlegung mit exakter lambda=1-Invariante

Zusaetzlich: erschoepfende Pruefung, dass kein Cayley-Graph ueber einer Gruppe
der Ordnung 99 im lambda-Suchraum liegt  (Stufe "cayley").

Aufruf:
    python3 generator.py            # alle Stufen nacheinander (ca. 5-6 min)
    python3 generator.py A          # nur Stufe A
    python3 generator.py B          # nur Stufe B (benoetigt cand_A.json)
    python3 generator.py C          # nur Stufe C
    python3 generator.py cayley     # nur die Nichtexistenz-Pruefung
    python3 generator.py final      # Verifikation + Bewertung + .g6-Dateien

Abhaengigkeiten: nur die Python-Standardbibliothek (getestet mit CPython 3.12).
Alle Zufallsentscheidungen laufen ueber random.Random(<fester Seed>); es werden
nirgends Mengen von Tupeln iteriert, daher ist der Lauf unabhaengig von
PYTHONHASHSEED reproduzierbar.
"""

import itertools
import json
import os
import random
import sys
import time

# ======================================================================
# 0.  Omega-Rahmen:  99 = 1 + 14 + 84
# ======================================================================
# Knoten 0        : unendlich
# Knoten 1..14    : Labels 0..13   (Nachbarn von unendlich)
# Knoten 15..98   : die 84 Aussenknoten = ungeordnete Paare {a,b}, a<b,
#                   ohne die sieben Partnerpaare {a,a+7}, lexikographisch.

def partner(a):
    return (a + 7) % 14

OUTER = sorted((a, b) for a in range(14) for b in range(a + 1, 14)
               if b != partner(a))
assert len(OUTER) == 84
IDX = {p: i for i, p in enumerate(OUTER)}
LAB = [list(p) for p in OUTER]

# Sollwerte:  C[x][l] = Anzahl der H-Nachbarn von x, die das Label l tragen.
TC = [[2] * 14 for _ in range(84)]
for _x, (_a, _b) in enumerate(OUTER):
    for _l in (_a, _b, partner(_a), partner(_b)):
        TC[_x][_l] = 1

CONT = [[x for x in range(84) if l in OUTER[x]] for l in range(14)]

def pairidx(u, v):
    """Index des Aussenknotens {u,v}, oder None falls kein zulaessiges Paar."""
    u %= 14
    v %= 14
    if u == v or v == partner(u):
        return None
    return IDX[(min(u, v), max(u, v))]


# ======================================================================
# 1.  Stufe A:  Z_14-symmetrische Loesung des Omega-Systems
# ======================================================================
# Parametrisierung der Aussenknoten:  (a,d) <-> {a, a+d},  d in 1..6, a in Z_14.
# H sei invariant unter a -> a+1.  Dann ist H durch Verbindungsmengen
#   S[d][e] subset Z_14 ,  (a,d) ~ (a+s,e)  <=>  s in S[d][e]
# beschrieben, mit S[e][d] = -S[d][e] und 0 not in S[d][d].
#
# Bedingung (Label-Zaehlung fuer x = {0,d}):
#   N(d,l) = sum_e ( [l in S[d][e]] + [l-e in S[d][e]] )  =  REQ[d][l]
# mit REQ[d][l] = 1 fuer l in {0,d,7,d+7} und sonst 2.

DRANGE = range(1, 7)

REQ = [[0] * 14 for _ in range(7)]
for _d in DRANGE:
    for _l in range(14):
        REQ[_d][_l] = 1 if _l in (0, _d, 7, (_d + 7) % 14) else 2

VARS = []
for _d in DRANGE:
    for _e in DRANGE:
        if _d < _e:
            for _s in range(14):
                VARS.append((_d, _e, _s))
        elif _d == _e:
            for _s in range(1, 8):
                VARS.append((_d, _d, _s))
VARSET = set(VARS)


def sym_counts(S):
    N = [[0] * 14 for _ in range(7)]
    for d in DRANGE:
        row = N[d]
        for e in DRANGE:
            Sde = S[d][e]
            for s in range(14):
                if Sde[s]:
                    row[s] += 1
                    row[(s + e) % 14] += 1
    return N


def sym_energy(N):
    return sum((N[d][l] - REQ[d][l]) ** 2 for d in DRANGE for l in range(14))


def sym_apply(S, v):
    d, e, s = v
    if d < e:
        S[d][e][s] ^= 1
        S[e][d][(-s) % 14] ^= 1
    else:
        S[d][d][s] ^= 1
        if (-s) % 14 != s:
            S[d][d][(-s) % 14] ^= 1


def solve_symmetric(seed, maxsteps=20000):
    """Lokale Suche im Z_14-symmetrischen Teilraum. Gibt S oder None zurueck."""
    rnd = random.Random(seed)
    S = [[[0] * 14 for _ in range(7)] for _ in range(7)]
    for v in VARS:
        if rnd.random() < 0.43:
            sym_apply(S, v)
    N = sym_counts(S)
    E = sym_energy(N)
    for step in range(maxsteps):
        if E == 0:
            return S, step
        viol = [(d, l) for d in DRANGE for l in range(14)
                if N[d][l] != REQ[d][l]]
        d0, l0 = rnd.choice(viol)
        cands = []
        for e in DRANGE:
            for s in (l0, (l0 - e) % 14):
                if d0 < e:
                    cands.append((d0, e, s))
                elif d0 > e:
                    cands.append((e, d0, (-s) % 14))
                elif s != 0:
                    cands.append((d0, d0, s if 1 <= s <= 7 else (-s) % 14))
        cands = [c for c in cands if c in VARSET]
        rnd.shuffle(cands)
        best = None
        bestE = None
        for v in cands:
            sym_apply(S, v)
            E2 = sym_energy(sym_counts(S))
            sym_apply(S, v)
            if bestE is None or E2 < bestE:
                bestE, best = E2, v
        if bestE < E or rnd.random() < 0.25:
            sym_apply(S, best)
            N = sym_counts(S)
            E = sym_energy(N)
    return None, E


def pd_pair(a, d):
    x, y = a % 14, (a + d) % 14
    return (min(x, y), max(x, y))


def H_from_S(S):
    """Baut die Adjazenzlisten des 84-Knoten-Graphen H aus den Mengen S."""
    adj = [set() for _ in range(84)]
    for d in DRANGE:
        for a in range(14):
            i = IDX[pd_pair(a, d)]
            for e in DRANGE:
                for s in range(14):
                    if S[d][e][s]:
                        adj[i].add(IDX[pd_pair(a + s, e)])
    for x in range(84):
        for y in adj[x]:
            assert x in adj[y], "H nicht symmetrisch"
        assert x not in adj[x]
    return adj


# ======================================================================
# 2.  Zustand + Reparatur fuer das volle (unsymmetrische) Omega-System
# ======================================================================
# Energie  E = sum_{x,l} ( n[x][l] - TC[x][l] )^2 ,  E = 0  <=>  Omega exakt.
# Verletzungen werden als ganze Zahl x*14+l gespeichert (kein Set von Tupeln),
# damit die Iterationsreihenfolge nicht von PYTHONHASHSEED abhaengt.

class OmegaState(object):

    def __init__(self, adj):
        self.adj = [set(a) for a in adj]
        self.n = [[0] * 14 for _ in range(84)]
        for x in range(84):
            for y in self.adj[x]:
                for l in LAB[y]:
                    self.n[x][l] += 1
        self.E = sum((self.n[x][l] - TC[x][l]) ** 2
                     for x in range(84) for l in range(14))
        self.V = set(x * 14 + l for x in range(84) for l in range(14)
                     if self.n[x][l] != TC[x][l])

    def flip(self, x, y, add):
        n, V = self.n, self.V
        s = 1 if add else -1
        d = 0
        for l in LAB[y]:
            v = n[x][l] - TC[x][l]
            d += 2 * s * v + 1
            n[x][l] += s
            if n[x][l] != TC[x][l]:
                V.add(x * 14 + l)
            else:
                V.discard(x * 14 + l)
        for l in LAB[x]:
            v = n[y][l] - TC[y][l]
            d += 2 * s * v + 1
            n[y][l] += s
            if n[y][l] != TC[y][l]:
                V.add(y * 14 + l)
            else:
                V.discard(y * 14 + l)
        if add:
            self.adj[x].add(y)
            self.adj[y].add(x)
        else:
            self.adj[x].discard(y)
            self.adj[y].discard(x)
        self.E += d


def omega_repair(st, rnd, maxsteps, noise=0.08):
    """Min-Conflicts mit zusammengesetzten Tauschzuegen. True bei E = 0."""
    Vl = list(st.V)
    for step in range(maxsteps):
        if not st.V:
            return True
        if step % 16 == 0 or not Vl:
            Vl = list(st.V)
        code = Vl[rnd.randrange(len(Vl))]
        x, l = divmod(code, 14)
        if st.n[x][l] == TC[x][l]:
            continue
        cands = []
        if st.n[x][l] > TC[x][l]:
            for y in sorted(st.adj[x]):
                if l in LAB[y]:
                    cands.append([(x, y, False)])
                    m = LAB[y][0] if LAB[y][1] == l else LAB[y][1]
                    for lp in range(14):
                        if st.n[x][lp] < TC[x][lp]:
                            yp = pairidx(lp, m)
                            if yp is not None and yp != x and yp not in st.adj[x]:
                                cands.append([(x, y, False), (x, yp, True)])
        else:
            for yp in CONT[l]:
                if yp != x and yp not in st.adj[x]:
                    cands.append([(x, yp, True)])
                    m = LAB[yp][0] if LAB[yp][1] == l else LAB[yp][1]
                    for lo in range(14):
                        if st.n[x][lo] > TC[x][lo]:
                            y = pairidx(lo, m)
                            if y is not None and y in st.adj[x]:
                                cands.append([(x, yp, True), (x, y, False)])
        if not cands:
            continue
        if rnd.random() < noise:
            for f in rnd.choice(cands):
                st.flip(*f)
        else:
            rnd.shuffle(cands)
            bd = None
            bm = None
            for mv in cands:
                e0 = st.E
                for f in mv:
                    st.flip(*f)
                d = st.E - e0
                for (a_, b_, c_) in reversed(mv):
                    st.flip(a_, b_, not c_)
                if bd is None or d < bd:
                    bd, bm = d, mv
            for f in bm:
                st.flip(*f)
    return not st.V


# ---- Guetemass F nur auf dem Aussen-Aussen-Block (dort sitzen alle Fehler) ---

PMAT = [[0] * 84 for _ in range(14)]
for _j, (_a, _b) in enumerate(OUTER):
    PMAT[_a][_j] = 1
    PMAT[_b][_j] = 1

LABMASK = [0] * 84
for _x, (_a, _b) in enumerate(OUTER):
    LABMASK[_x] = (1 << _a) | (1 << _b)


def outer_scores(adj):
    """(F, W, L1, Linf) des Gesamtgraphen -- Fehler treten nur aussen auf."""
    bit = [0] * 84
    for x in range(84):
        m = 0
        for y in adj[x]:
            m |= 1 << y
        bit[x] = m
    F = W = L1 = Li = 0
    for x in range(84):
        bx, lx = bit[x], LABMASK[x]
        for y in range(x + 1, 84):
            c = bin(bx & bit[y]).count("1") + bin(lx & LABMASK[y]).count("1")
            r = c + (1 if (bit[y] >> x) & 1 else 0) - 2
            if r:
                W += 1
                a = abs(r)
                L1 += a
                F += r * r
                if a > Li:
                    Li = a
    return F, W, L1, Li


def lns_optimize(adj_start, seed, rounds, repair_steps=150000):
    """Destroy-and-repair innerhalb des exakt zulaessigen Omega-Bereichs.
    Zerstoert alle H-Kanten an k zufaelligen Aussenknoten und repariert exakt;
    akzeptiert nur nicht-verschlechternde Loesungen (mit kleiner Toleranz)."""
    rnd = random.Random(seed)
    cur = OmegaState(adj_start)
    assert cur.E == 0
    curF = outer_scores(cur.adj)
    best = [set(a) for a in cur.adj]
    bestF = curF
    acc = 0
    for _ in range(rounds):
        trial = OmegaState(cur.adj)
        k = rnd.choice([12, 16, 20])
        for x in rnd.sample(range(84), k):
            for y in sorted(trial.adj[x]):
                trial.flip(x, y, False)
        if omega_repair(trial, rnd, repair_steps, 0.08):
            f = outer_scores(trial.adj)
            if f[0] <= curF[0] + (2 if rnd.random() < 0.3 else 0):
                cur = trial
                curF = f
                acc += 1
                if f[0] < bestF[0]:
                    bestF = f
                    best = [set(a) for a in trial.adj]
    return best, bestF, acc


# ======================================================================
# 3.  Stufe C:  lambda-Suchraum, beschraenkte Dreieckszerlegung
# ======================================================================
# 231 Tripel auf 99 Punkten, jeder Punkt in 7 Tripeln, je zwei Punkte in
# hoechstens einem.  Ein Tripel {u,v,w} darf nur eingefuegt werden, wenn die
# drei Paare vorher keinen gemeinsamen Nachbarn haben; das ist genau die
# Bedingung dafuer, dass kein transversales Dreieck entsteht, haelt also
# (A^2)_ij <= 1 auf allen Kanten invariant.

def triangle_packing(seed, maxiter=300000, n=99, K=14):
    rnd = random.Random(seed)
    N = [set() for _ in range(n)]
    triples = []
    where = [set() for _ in range(n)]

    def addt(t):
        triples.append(t)
        for p, q in itertools.combinations(t, 2):
            N[p].add(q)
            N[q].add(p)
        for p in t:
            where[p].add(len(triples) - 1)

    def remove_at(i):
        t = triples[i]
        last = len(triples) - 1
        for p, q in itertools.combinations(t, 2):
            N[p].discard(q)
            N[q].discard(p)
        for p in t:
            where[p].discard(i)
        if i != last:
            tl = triples[last]
            for p in tl:
                where[p].discard(last)
                where[p].add(i)
            triples[i] = tl
        triples.pop()

    for _ in range(maxiter):
        if len(triples) == 231:
            return triples
        cand = [v for v in range(n) if len(N[v]) < K]
        m = min(len(N[v]) for v in cand)
        u = rnd.choice([v for v in cand if len(N[v]) == m])
        Nu = N[u]
        ok = [x for x in cand if x != u and x not in Nu and not (N[x] & Nu)]
        rnd.shuffle(ok)
        placed = False
        for a in range(len(ok)):
            v = ok[a]
            Nv = N[v]
            for b in range(a + 1, len(ok)):
                w = ok[b]
                if w in Nv or (N[w] & Nv):
                    continue
                addt((u, v, w))
                placed = True
                break
            if placed:
                break
        if not placed:
            pool = set()
            for y in Nu:
                pool |= where[y]
                for z in N[y]:
                    pool |= where[z]
            pool = sorted(pool) if pool else list(range(len(triples)))
            for _ in range(rnd.randint(1, 3)):
                if not triples:
                    break
                remove_at(rnd.choice(pool))
                pool = [i for i in pool if i < len(triples)]
                if not pool:
                    break
    return None


# ======================================================================
# 4.  Nichtexistenz von Cayley-Graphen im lambda-Suchraum
# ======================================================================
# |G| = 99 = 3^2 * 11.  n_11 = 1 und n_3 = 1 (11 = 2 mod 3), also ist G das
# direkte Produkt seiner Sylow-Gruppen und damit abelsch:
#     G = Z_99   oder   G = Z_3 x Z_3 x Z_11.
# In einem Cayley-Graphen mit lambda = 1 zerfaellt die Dreiecksmenge in
# Translationsbahnen der Laenge 99 (voll) oder 33 (kurz, Nebenklassen einer
# Untergruppe der Ordnung 3).  Jeder Punkt liegt in 7 Dreiecken, also
# 7 = 3*m + k mit m vollen und k kurzen Bahnen.  k = 4 (nur in Z_3xZ_3xZ_11
# moeglich) erzwingt K_9 auf jeder E_9-Nebenklasse und ist mit lambda = 1
# unvereinbar (jede innere Kante haette sieben gemeinsame Nachbarn);
# k = 7 ist unmoeglich, da es hoechstens 4 Untergruppen der Ordnung 3 gibt.
# Bleibt k = 1, m = 2 -- und dieser Fall wird hier erschoepfend durchsucht.

def _cayley_search(add, neg, order3, n=99):
    def diffs(x, y):
        D = {x, neg[x], y, neg[y]}
        d = add[y][neg[x]]
        D.add(d)
        D.add(neg[d])
        return D

    HS = set(order3)
    blocks = []
    seen = set()
    for x in range(1, n):
        for y in range(1, n):
            if y == x:
                continue
            B = (0, x, y)
            canon = min(tuple(sorted(add[b][t] for b in B)) for t in range(n))
            if canon in seen:
                continue
            seen.add(canon)
            D = diffs(x, y)
            if len(D) != 6 or (D & HS):
                continue
            blocks.append((B, D))

    def common_le1(S, s):
        c = 0
        for v in S:
            if add[v][neg[s]] in S:
                c += 1
                if c > 1:
                    return False
        return c == 1

    for i in range(len(blocks)):
        B1, D1 = blocks[i]
        for j in range(i + 1, len(blocks)):
            B2, D2 = blocks[j]
            if D1 & D2:
                continue
            S = set(order3) | D1 | D2
            if len(S) != 14:
                continue
            if all(common_le1(S, s) for s in sorted(S)):
                return (B1, B2), len(blocks)
    return None, len(blocks)


def cayley_check():
    res = {}
    # ---- G = Z_99 ----
    n = 99
    add = [[(i + j) % n for j in range(n)] for i in range(n)]
    neg = [(-i) % n for i in range(n)]
    hit, nb = _cayley_search(add, neg, [33, 66])
    res["Z99"] = {"basisbloecke": nb, "loesung": hit}
    # ---- G = Z_3 x Z_3 x Z_11 ----
    def enc(u, v, w):
        return (u % 3) * 33 + (v % 3) * 11 + (w % 11)
    dec = [(i // 33, (i // 11) % 3, i % 11) for i in range(99)]
    add = [[enc(dec[i][0] + dec[j][0], dec[i][1] + dec[j][1],
                dec[i][2] + dec[j][2]) for j in range(99)] for i in range(99)]
    neg = [enc(-dec[i][0], -dec[i][1], -dec[i][2]) for i in range(99)]
    hit, nb = _cayley_search(add, neg, [enc(1, 0, 0), enc(2, 0, 0)])
    res["Z3xZ3xZ11"] = {"basisbloecke": nb, "loesung": hit}
    return res


# ======================================================================
# 5.  Zusammenbau, Verifikation, Bewertung, graph6
# ======================================================================

def assemble_omega(adjH):
    """99 Knoten: 0 = unendlich, 1..14 = Labels, 15..98 = OUTER."""
    A = [[0] * 99 for _ in range(99)]

    def e(i, j):
        A[i][j] = 1
        A[j][i] = 1

    for a in range(14):
        e(0, 1 + a)
    for a in range(14):
        e(1 + a, 1 + partner(a))
    for j, (a, b) in enumerate(OUTER):
        e(1 + a, 15 + j)
        e(1 + b, 15 + j)
    for x in range(84):
        for y in adjH[x]:
            if x < y:
                e(15 + x, 15 + y)
    return A


def assemble_lambda(triples):
    A = [[0] * 99 for _ in range(99)]
    for t in triples:
        for i, j in itertools.combinations(t, 2):
            assert A[i][j] == 0, "zwei Tripel teilen ein Paar"
            A[i][j] = 1
            A[j][i] = 1
    return A


def check_omega_equation(adjH):
    """Prueft PH = 2J - (C+I)P elementweise. True/False."""
    for a in range(14):
        for x in range(84):
            lhs = 0
            for y in adjH[x]:
                if a in OUTER[y]:
                    lhs += 1
            rhs = 2 - PMAT[a][x] - PMAT[partner(a)][x]
            if lhs != rhs:
                return False
    return True


def evaluate(A):
    n = len(A)
    bits = [0] * n
    for i in range(n):
        m = 0
        for j in range(n):
            if A[i][j]:
                m |= 1 << j
        bits[i] = m
    deg = sorted(set(bin(b).count("1") for b in bits))
    W = L1 = F = Li = 0
    lam = set()
    mu = {}
    for i in range(n):
        for j in range(i + 1, n):
            c = bin(bits[i] & bits[j]).count("1")
            if A[i][j]:
                lam.add(c)
            else:
                mu[c] = mu.get(c, 0) + 1
            r = c + A[i][j] - 2
            if r:
                W += 1
                a = abs(r)
                L1 += a
                F += r * r
                if a > Li:
                    Li = a
    sym = all(A[i][j] == A[j][i] for i in range(n) for j in range(n))
    diag = sum(A[i][i] for i in range(n))
    return {"symmetrisch": sym, "diagonale": diag, "grade": deg,
            "lambda_werte": sorted(lam), "mu_verteilung": dict(sorted(mu.items())),
            "W": W, "L1": L1, "F": F, "Linf": Li,
            "kanten": sum(bin(b).count("1") for b in bits) // 2}


def graph6(A):
    n = len(A)
    out = []
    if n <= 62:
        out.append(n + 63)
    else:
        out.append(126)
        out.append(((n >> 12) & 63) + 63)
        out.append(((n >> 6) & 63) + 63)
        out.append((n & 63) + 63)
    bitsv = []
    for j in range(1, n):
        for i in range(j):
            bitsv.append(A[i][j])
    while len(bitsv) % 6:
        bitsv.append(0)
    for k in range(0, len(bitsv), 6):
        v = 0
        for b in bitsv[k:k + 6]:
            v = (v << 1) | b
        out.append(v + 63)
    return "".join(chr(c) for c in out)


def z14_translation():
    """Die Permutation der 99 Knoten zur Translation a -> a+1 auf Z_14."""
    pi = [0] * 99
    pi[0] = 0
    for a in range(14):
        pi[1 + a] = 1 + (a + 1) % 14
    for j, (a, b) in enumerate(OUTER):
        pi[15 + j] = 15 + pairidx(a + 1, b + 1)
    return pi


def is_invariant(A, pi):
    n = len(A)
    return all(A[i][j] == A[pi[i]][pi[j]] for i in range(n) for j in range(n))


# ======================================================================
# 6.  Stufen
# ======================================================================

SEED_A = 1
SEED_B = 11
ROUNDS_B = 100
SEED_C = 4


def stage_A():
    t = time.time()
    S, steps = solve_symmetric(SEED_A)
    assert S is not None, "Stufe A: keine Loesung gefunden"
    adjH = H_from_S(S)
    assert all(len(a) == 12 for a in adjH)
    assert check_omega_equation(adjH)
    json.dump([sorted(a) for a in adjH], open("cand_A.json", "w"))
    print("Stufe A: Loesung nach %d Schritten, %.1fs" % (steps, time.time() - t))
    print("         Omega-Gleichung exakt erfuellt:", check_omega_equation(adjH))
    return adjH


def stage_B():
    adjA = [set(a) for a in json.load(open("cand_A.json"))]
    t = time.time()
    best, bestF, acc = lns_optimize(adjA, SEED_B, ROUNDS_B)
    assert check_omega_equation(best)
    json.dump([sorted(a) for a in best], open("cand_B.json", "w"))
    ham = sum(len(best[x] ^ adjA[x]) for x in range(84)) // 2
    print("Stufe B: %d Runden, %d akzeptiert, %.0fs" % (ROUNDS_B, acc, time.time() - t))
    print("         (F,W,L1,Linf) =", bestF, " Hamming-Abstand zu A:", ham)
    return best


def stage_C():
    t = time.time()
    for s in range(SEED_C + 1):
        tr = triangle_packing(s)
        if tr:
            break
    assert tr is not None, "Stufe C: keine Zerlegung gefunden"
    json.dump([list(x) for x in tr], open("cand_C.json", "w"))
    print("Stufe C: 231 Tripel mit Seed %d, %.0fs" % (s, time.time() - t))
    return tr


def stage_cayley():
    t = time.time()
    res = cayley_check()
    json.dump(res, open("cayley.json", "w"))
    for g, r in res.items():
        print("Cayley %-12s: %4d Basisblock-Bahnen geprueft, Loesung: %s"
              % (g, r["basisbloecke"], r["loesung"]))
    print("         %.0fs" % (time.time() - t))
    return res


def stage_final():
    pi = z14_translation()
    adjA = [set(a) for a in json.load(open("cand_A.json"))]
    adjB = [set(a) for a in json.load(open("cand_B.json"))]
    tr = [tuple(x) for x in json.load(open("cand_C.json"))]
    gA = assemble_omega(adjA)
    gB = assemble_omega(adjB)
    gC = assemble_lambda(tr)
    report = {}
    for name, g, adjH in (("A", gA, adjA), ("B", gB, adjB), ("C", gC, None)):
        r = evaluate(g)
        if adjH is not None:
            r["omega_gleichung"] = check_omega_equation(adjH)
        r["z14_invariant"] = is_invariant(g, pi)
        report[name] = r
        print("Kandidat %s: %s" % (name, json.dumps(r, ensure_ascii=False)))
    ham = sum(len(adjA[x] ^ adjB[x]) for x in range(84)) // 2
    report["hamming_A_B"] = ham
    print("Hamming-Abstand H(A) gegen H(B):", ham, "von 504 Kanten")
    for name, g in (("01", gA), ("02", gB), ("03", gC)):
        with open("kandidat_%s.g6" % name, "w") as f:
            f.write(graph6(g) + "\n")
    json.dump(report, open("bewertung.json", "w"), ensure_ascii=False, indent=1)
    return report


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "alles"
    if what in ("A", "alles"):
        stage_A()
    if what in ("C", "alles"):
        stage_C()
    if what in ("cayley", "alles"):
        stage_cayley()
    if what in ("B", "alles"):
        stage_B()
    if what in ("final", "alles"):
        stage_final()


if __name__ == "__main__":
    main()
