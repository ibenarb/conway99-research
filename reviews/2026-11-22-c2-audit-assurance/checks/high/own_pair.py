# Independent pairwise search for a high-rank central chart (own implementation, own data structures).
# For one sign-normalised star assignment it decides whether there is a choice, for ALL 30 outside labels, of
# (signed circuit word, physical attachment, residual F_7 vector) that is pairwise consistent:
#   T from the word product in {0,1,2}; L = 0 for even T, L = +-1 for T = 1 (both tried);
#   residual product = -4L - z.z - f[I]^T Q^{-1} f'[I]  (mod 7) in the common complement;
#   exact real Cauchy inequality for the residuals off the star;  literal capacities in the 43-vertex graph.
# "closed" = no such choice (searched to full depth with forward checking).  Rank 11, or rank 10 with a mode.
import sys, time, itertools, json
from math import lcm
import numpy as np
from own_local import *

def literal_caps(base, x, y, like, opp):
    A = np.zeros((43, 43), dtype=np.int64); A[:39, :39] = base
    for idx, m in ((39, x['mask']), (40, x['twin']), (41, y['mask']), (42, y['twin'])):
        for v in range(39):
            if m >> v & 1: A[idx, v] = A[v, idx] = 1
    if like: A[39, 41] = A[41, 39] = A[40, 42] = A[42, 40] = 1
    if opp: A[39, 42] = A[42, 39] = A[40, 41] = A[41, 40] = 1
    C = A @ A; np.fill_diagonal(C, 0)
    return bool((C <= 2 - A).all())

class Solver:
    def __init__(self, cid, par, mode=0):
        self.C = C = Chart(cid, par); assert C.physical and C.rank in (10, 11)
        self.mode = mode; self.dom = C.attachments()
        self.base = np.array([[(C.A[a] >> b) & 1 for b in range(39)] for a in range(39)], dtype=np.int64)
        self.d = 1 if C.detQ in (1, 2, 4) else 3
        self.nd = 13 - C.rank
        if self.nd == 2:
            assert mode == 0
            self.vecs = [(a, b) for a in range(7) for b in range(7)]
            self.ip = lambda v, w: (v[0] * w[0] + self.d * v[1] * w[1]) % 7
            self.null = None
        else:
            self.vecs = [(a, b, c) for a in range(7) for b in range(7) for c in range(7)]
            self.ip = lambda v, w: (v[0] * w[0] + v[1] * w[1] + self.d * v[2] * w[2]) % 7
            self.null = next(v for v in self.vecs if any(v) and self.ip(v, v) == 0) if mode else (0, 0, 0)
        # residual vectors by (norm, pairing with the residual anchor)
        self.R = {}
        for v in self.vecs:
            key = (self.ip(v, v), self.ip(v, self.null) if self.nd == 3 else 0)
            self.R.setdefault(key, []).append(v)
        self.ipt = {}
        den = 1
        for row in C.Finv:
            for x in row: den = lcm(den, x.denominator)
        self.den = den
        Fi = np.array([[int(x * den) for x in row] for row in C.Finv], dtype=object)
        self.att = []; self.att_of = {y: [] for y in OUTER}
        for y in OUTER:
            for a in self.dom[y]:
                cond = a['h'][0] if self.nd == 3 else 0
                if (a['rho'], cond) not in self.R: continue          # no residual vector with the required norm and pairing
                f = np.array(a['f'], dtype=object)
                a = dict(a); a['y'] = y; a['G'] = Fi.dot(f); a['n'] = int(den * 10 - f.dot(a['G'])); a['fnp'] = f; a['rk'] = (a['rho'], cond)
                assert a['n'] >= 0
                self.att_of[y].append(len(self.att)); self.att.append(a)
        self.capcache = {}; self.stats = dict(arcs=0, cauchy_fail=0, caps=0, nodes=0, maxdepth=0)
    def zz(self, y1, y2):
        (j, k, t), (j2, k2, t2) = y1, y2
        v1 = {j: 1, k: (-1) ** t}; v2 = {j2: 1, k2: (-1) ** t2}
        return sum(v1[a] * v2.get(a, 0) for a in v1)
    def axcommon(self, y1, y2): return len({y1[0], y1[1]} & {y2[0], y2[1]})
    def arc(self, c1, v1, c2, rem):
        """c = (attachment index, word); returns the subset of residual vectors of c2 (from rem) compatible with (c1,v1)."""
        self.stats['arcs'] += 1
        a1 = self.att[c1[0]]; a2 = self.att[c2[0]]; y1, y2 = a1['y'], a2['y']
        w1, w2 = c1[1], c2[1]; cm = w1[0] & w2[0]
        dot = bin(cm).count('1') - 2 * bin((w1[1] ^ w2[1]) & cm).count('1')
        t = 1 - self.axcommon(y1, y2) - dot
        if t % 2 or not 0 <= t <= 4: return []
        t //= 2; zz = self.zz(y1, y2)
        base7 = (-zz - sum(m * f for m, f in zip(a1['m'], a2['fI']))) % 7
        out = []
        for L in ((0,) if t != 1 else (1, -1)):
            target = (base7 - 4 * L) % 7
            cand = [v for v in rem if self.ip(v1, v) == target]
            if not cand: continue
            cross = self.den * (-4 * L - zz) - int(a2['fnp'].dot(a1['G']))
            if cross * cross > a1['n'] * a2['n']: self.stats['cauchy_fail'] += 1; continue
            key = (c1[0], c2[0], t, L)
            if key not in self.capcache:
                self.stats['caps'] += 1
                self.capcache[key] = literal_caps(self.base, a1, a2, like=(t == 2 or L == 1), opp=(t == 2 or L == -1))
            if self.capcache[key]: out += cand
        return out
    def solve(self, star, maxdepth=30):
        C = self.C; ds = []
        for y in OUTER:
            keys = C.outer_keys(star, y); cl = []
            for ai in self.att_of[y]:
                a = self.att[ai]
                for w in keys.get(a['key'], ()):
                    cl.append(((ai, w), list(self.R[a['rk']])))
            if not cl: return 'closed', 0
            ds.append(cl)
        def size(d): return sum(len(r) for _, r in d)
        def dfs(ds, depth):
            self.stats['nodes'] += 1; self.stats['maxdepth'] = max(self.stats['maxdepth'], depth)
            if depth >= maxdepth or not ds: return True
            i = min(range(len(ds)), key=lambda i: size(ds[i])); ds = ds[:]; ds[0], ds[i] = ds[i], ds[0]
            for c1, rem1 in ds[0]:
                for v1 in rem1:
                    nxt = []; ok = True
                    for d in ds[1:]:
                        nd = []
                        for c2, rem2 in d:
                            r = self.arc(c1, v1, c2, rem2)
                            if r: nd.append((c2, r))
                        if not nd: ok = False; break
                        nxt.append(nd)
                    if ok and dfs(nxt, depth + 1): return True
            return False
        return ('open' if dfs(ds, 0) else 'closed'), self.stats['maxdepth']

if __name__ == '__main__':
    cid, par = int(sys.argv[1]), int(sys.argv[2]); mode = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    maxdepth = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    t0 = time.time(); S = Solver(cid, par, mode)
    reps = [list(map(int, s.split())) for s in open(f'reps/{cid}.{par}.txt')]
    print(f'chart {cid} own-parity {par} mode {mode}: rank {S.C.rank}, det Q {S.C.detQ}, attachments {len(S.att)}, orbit representatives {len(reps)}, setup {round(time.time()-t0)} s', flush=True)
    res = {'open': 0, 'closed': 0}; depths = []
    for k, r in enumerate(reps):
        star = [(r[2 * i], r[2 * i + 1]) for i in range(12)]
        S.stats['maxdepth'] = 0
        verdict, md = S.solve(star, maxdepth); res[verdict] += 1; depths.append(md)
        if verdict == 'open': print('  OPEN at representative', k, flush=True)
    from collections import Counter
    print(f'  result: {res}; deepest level reached per representative: {dict(sorted(Counter(depths).items()))}; nodes {S.stats["nodes"]}, arc tests {S.stats["arcs"]}, exact Cauchy rejections {S.stats["cauchy_fail"]}, literal 43-vertex checks {S.stats["caps"]}; time {round(time.time()-t0)} s', flush=True)
