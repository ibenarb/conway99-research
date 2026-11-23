# Setup files for the C++ port of my independent pairwise search: attachments with all exact derived data.
import sys, json, itertools
from math import lcm
import numpy as np
import own_local
from own_local import *
# faster literal 41-vertex capacity check (same test, numpy)
def attachments_fast(C):
    """Same admissibility tests as own_local.Chart.attachments (literal 41-vertex capacities, both Schur tests),
    reorganised for speed: capacities by the three literal conditions for a new orbit, Schur tests in exact integers."""
    A = C.A
    slack = [[2 - ((A[a] >> b) & 1) - bin(A[a] & A[b]).count('1') for b in range(39)] for a in range(39)]
    den = 1
    for row in C.Finv:
        for x in row: den = lcm(den, x.denominator)
    denH = 1
    for row in C.Hinv:
        for x in row: denH = lcm(denH, x.denominator)
    Fi = np.array([[int(x * den) for x in row] for row in C.Finv], dtype=np.int64)
    Hi = np.array([[int(x * denH) for x in row] for row in C.Hinv], dtype=np.int64)
    compM = np.array([[int(C.comp[i] == c) for i in range(12)] for c in range(C.ncomp)], dtype=np.int64)
    pairs = list(itertools.combinations(range(12), 2)); dom = {}
    def ok41(m, mm):
        if bin(m & mm).count('1') > 2: return False
        for M_ in (m, mm):
            for v in range(39):
                if bin(A[v] & M_).count('1') > 2 - ((M_ >> v) & 1): return False
        vs = [v for v in range(39) if (m | mm) >> v & 1]
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                a, b = vs[i], vs[j]
                gain = ((m >> a) & (m >> b) & 1) + ((mm >> a) & (mm >> b) & 1)
                if gain > slack[a][b]: return False
        return True
    for y in OUTER:
        j, k, t = y; cand = []
        zd = np.array([C.zdot(i, y) for i in range(12)], dtype=np.int64)
        for (u1, u2) in pairs:
            for (v1, v2) in pairs:
                m = (1 << pos(u1)) | (1 << pos(u2)) | (1 << neg(v1)) | (1 << neg(v2)) | (1 << ax(j, 0)) | (1 << ax(k, t))
                mm = (1 << neg(u1)) | (1 << neg(u2)) | (1 << pos(v1)) | (1 << pos(v2)) | (1 << ax(j, 1)) | (1 << ax(k, 1 - t))
                if ok41(m, mm): cand.append((m, mm, u1, u2, v1, v2))
        if not cand: dom[y] = []; continue
        a = np.zeros((len(cand), 12), dtype=np.int64); b = np.zeros((len(cand), 12), dtype=np.int64)
        for r, (_, _, u1, u2, v1, v2) in enumerate(cand): a[r, u1] = a[r, u2] = 1; b[r, v1] = b[r, v2] = 1
        f = -zd[None, :] - 4 * (a - b); u = 1 - np.abs(zd)[None, :] - 2 * (a + b)
        G = f @ Fi.T; nf = 10 * den - (f * G).sum(axis=1)
        nu = 5 * denH - (u * (u @ Hi.T)).sum(axis=1)
        good = (f.sum(axis=1) == 0) & ((u @ compM.T) == 0).all(axis=1) & (nf >= 0) & (nu >= 0)
        out = []
        for r in np.flatnonzero(good):
            fl = [int(x) for x in f[r]]
            fI = [fl[i] % 7 for i in C.piv]
            mv = [sum(C.Qinv[q][c] * fI[c] for c in range(len(fI))) % 7 for q in range(len(fI))]
            rho = (10 - sum(fI[q] * mv[q] for q in range(len(fI)))) % 7
            h = tuple((fl[kk] - sum(C.FA[kk][C.piv[q]] * mv[q] for q in range(len(fI)))) % 7 for kk in C.nonpiv)
            out.append(dict(mask=cand[r][0], twin=cand[r][1], f=fl, key=tuple(int(x) for x in (a[r] + b[r])), rho=rho, h=h, m=mv, fI=fI))
        dom[y] = out
    return dom
def write_setup(cid, par, path):
    C = Chart(cid, par)
    if not C.physical or C.rank not in (10, 11): return None
    dom = attachments_fast(C)
    den = 1
    for row in C.Finv:
        for x in row: den = lcm(den, x.denominator)
    Fi = [[int(x * den) for x in row] for row in C.Finv]
    d = 1 if C.detQ in (1, 2, 4) else 3
    with open(path, 'w') as fo:
        fo.write(f'{C.rank} {d} {den}\n')
        for j in range(6): fo.write(' '.join(map(str, C.words_central[j])) + '\n')
        for j in range(6):
            for k in range(j + 1, 6): fo.write(' '.join(map(str, C.words_outer[(j, k)])) + '\n')
        n = sum(len(v) for v in dom.values()); fo.write(f'{n}\n')
        for yi, y in enumerate(OUTER):
            for a in dom[y]:
                G = [sum(Fi[i][l] * a['f'][l] for l in range(12)) for i in range(12)]
                nn = 10 * den - sum(a['f'][i] * G[i] for i in range(12)); assert nn >= 0
                cond = a['h'][0] if C.rank == 10 else 0
                fo.write(' '.join(map(str, [yi, a['mask'], a['twin'], a['rho'], cond, nn] + list(a['key']) + a['fI'] + a['m'] + a['f'] + G)) + '\n')
        fo.write(' '.join(str(x) for x in C.A) + '\n')
    return C
if __name__ == '__main__':
    import os
    os.makedirs('setup', exist_ok=True)
    for arg in sys.argv[1:]:
        cid, par = map(int, arg.split('.'))
        C = write_setup(cid, par, f'setup/{cid}.{par}.txt'); print(arg, 'rank', C.rank if C else None, flush=True)
