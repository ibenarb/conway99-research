# Own implementation of the local model at a central star (manuscript Section 6): base graph, outside attachments
# with literal capacity checks, unary Schur tests, F_7 pivot data, simplex words.  No code from the reviewed packets.
import itertools, json
from fractions import Fraction as Fr
GEO = json.load(open('geometry_own.json'))
LAY = [list(map(int, s.split())) for s in open('layouts.tsv')]
OUTER = [(j, k, t) for j in range(6) for k in range(j + 1, 6) for t in (0, 1)]          # 30 outside labels
def ax(j, s): return 3 + 2 * j + s
def pos(i): return 15 + i
def neg(i): return 27 + i
def base_adj(P, N):
    A = [0] * 39
    def e(a, b): A[a] |= 1 << b; A[b] |= 1 << a
    e(0, 1); e(0, 2); e(1, 2)
    for j in range(6): e(0, ax(j, 0)); e(0, ax(j, 1)); e(ax(j, 0), ax(j, 1))
    for i in range(12):
        j, t = divmod(i, 2)
        e(1, pos(i)); e(2, neg(i)); e(pos(i), ax(j, t)); e(neg(i), ax(j, 1 - t))
        e(pos(i), pos(P[i])); e(neg(i), neg(P[i])); e(pos(i), neg(N[i])); e(neg(i), pos(N[i]))
    return A
def caps_ok(A):
    n = len(A)
    for a in range(n):
        for b in range(a + 1, n):
            if bin(A[a] & A[b]).count('1') > 2 - ((A[a] >> b) & 1): return False
    return True
def inv_frac(M):
    n = len(M); A = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        d = A[c][c]; A[c] = [x / d for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]; A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [row[n:] for row in A]
class Chart:
    def __init__(self, cid, par):
        self.cid, self.par = cid, par
        self.P = P = LAY[cid][1:13]; self.N = N = LAY[cid][13:25]
        self.A = base_adj(P, N); self.physical = caps_ok(self.A)
        I12 = range(12)
        self.FA = [[11 * (a == b) + ((a ^ 1) == b) - 4 * (P[a] == b) + 4 * (N[a] == b) - 1 for b in I12] for a in I12]
        self.HA = [[5 * (a == b) - ((a ^ 1) == b) - 2 * (P[a] == b) - 2 * (N[a] == b) for b in I12] for a in I12]
        # components of the graph M u P u N (kernel of H_A)
        comp = [-1] * 12; nc = 0
        for s in I12:
            if comp[s] < 0:
                st = [s]
                while st:
                    x = st.pop()
                    if comp[x] >= 0: continue
                    comp[x] = nc; st += [P[x], N[x], x ^ 1]
                nc += 1
        self.comp, self.ncomp = comp, nc
        self.Finv = inv_frac([[self.FA[a][b] + 1 for b in I12] for a in I12])
        self.Hinv = inv_frac([[self.HA[a][b] + (comp[a] == comp[b]) for b in I12] for a in I12])
        # F_7 data: pivot columns left to right
        M = [[x % 7 for x in row] for row in self.FA]; piv = []; r = 0; M = [row[:] for row in M]
        for c in range(12):
            k = next((i for i in range(r, 12) if M[i][c]), None)
            if k is None: continue
            M[r], M[k] = M[k], M[r]; iv = pow(M[r][c], -1, 7); M[r] = [(x * iv) % 7 for x in M[r]]
            for i in range(12):
                if i != r and M[i][c]:
                    f = M[i][c]; M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[r])]
            piv.append(c); r += 1
        self.piv, self.rank = piv, r
        assert 11 not in piv
        self.nonpiv = [c for c in range(11) if c not in piv]
        Q = [[self.FA[a][b] % 7 for b in piv] for a in piv]
        self.Qinv = self.inv7(Q); self.detQ = self.det7(Q)
        self.words_central = [GEO[str(par)]['central'][j] for j in range(6)]
        self.words_outer = {(j, k): GEO[str(par)]['outer'][f'{j},{k}'] for j in range(6) for k in range(j + 1, 6)}
        self._dom = None
    @staticmethod
    def det7(M):
        M = [row[:] for row in M]; n = len(M); d = 1
        for c in range(n):
            k = next((i for i in range(c, n) if M[i][c] % 7), None)
            if k is None: return 0
            if k != c: M[c], M[k] = M[k], M[c]; d = -d
            d = d * M[c][c] % 7; iv = pow(M[c][c], -1, 7)
            for i in range(c + 1, n):
                f = M[i][c] * iv % 7; M[i] = [(x - f * y) % 7 for x, y in zip(M[i], M[c])]
        return d % 7
    @staticmethod
    def inv7(M):
        n = len(M); A = [[x % 7 for x in row] + [int(i == j) for j in range(n)] for i, row in enumerate(M)]
        for c in range(n):
            p = next(r for r in range(c, n) if A[r][c]); A[c], A[p] = A[p], A[c]
            iv = pow(A[c][c], -1, 7); A[c] = [(x * iv) % 7 for x in A[c]]
            for r in range(n):
                if r != c and A[r][c]:
                    f = A[r][c]; A[r] = [(x - f * y) % 7 for x, y in zip(A[r], A[c])]
        return [row[n:] for row in A]
    def zdot(self, i, y):
        j, k, t = y; ji, ti = divmod(i, 2)
        return (-1) ** ti * ((ji == j) + (-1) ** t * (ji == k))
    def attachments(self):
        """All physically and unarily admissible attachments of every outside label.
        Returns dom[y] = list of dicts(a,b masks on anchors, mask39, f, u, key, rho, h)."""
        if self._dom is not None: return self._dom
        A = self.A; pairs = list(itertools.combinations(range(12), 2)); dom = {}
        for y in OUTER:
            j, k, t = y; out = []
            for (u1, u2) in pairs:
                for (v1, v2) in pairs:
                    m = (1 << pos(u1)) | (1 << pos(u2)) | (1 << neg(v1)) | (1 << neg(v2)) | (1 << ax(j, 0)) | (1 << ax(k, t))
                    mm = (1 << neg(u1)) | (1 << neg(u2)) | (1 << pos(v1)) | (1 << pos(v2)) | (1 << ax(j, 1)) | (1 << ax(k, 1 - t))
                    # literal 41-vertex graph
                    B = A + [m, mm]
                    for x in range(39):
                        if m >> x & 1: B[x] |= 1 << 39
                        if mm >> x & 1: B[x] |= 1 << 40
                    if not caps_ok(B): continue
                    a = [int(i in (u1, u2)) for i in range(12)]; b = [int(i in (v1, v2)) for i in range(12)]
                    f = [-self.zdot(i, y) - 4 * (a[i] - b[i]) for i in range(12)]
                    u = [1 - abs(self.zdot(i, y)) - 2 * (a[i] + b[i]) for i in range(12)]
                    if sum(f) != 0: continue
                    if any(sum(u[i] for i in range(12) if self.comp[i] == c) != 0 for c in range(self.ncomp)): continue
                    nf = 10 - sum(f[i] * self.Finv[i][l] * f[l] for i in range(12) for l in range(12))
                    nu = 5 - sum(u[i] * self.Hinv[i][l] * u[l] for i in range(12) for l in range(12))
                    if nf < 0 or nu < 0: continue
                    fI = [f[i] % 7 for i in self.piv]
                    mv = [sum(self.Qinv[r][c] * fI[c] for c in range(len(fI))) % 7 for r in range(len(fI))]
                    rho = (10 - sum(fI[r] * mv[r] for r in range(len(fI)))) % 7
                    h = tuple((f[kk] - sum(self.FA[kk][self.piv[r]] * mv[r] for r in range(len(fI)))) % 7 for kk in self.nonpiv)
                    out.append(dict(a=a, b=b, mask=m, twin=mm, f=f, u=u, key=tuple(a[i] + b[i] for i in range(12)), rho=rho, h=h, m=mv, fI=fI, nf=nf))
            dom[y] = out
        self._dom = dom; return dom
    def star_assignments(self):
        """All sign-normalised 12-word assignments realising H_A (first use of a coordinate is +)."""
        res = []; H = self.HA
        def dot(w1, w2):
            c = w1[0] & w2[0]; return bin(c).count('1') - 2 * bin((w1[1] ^ w2[1]) & c).count('1')
        cur = []
        def rec(i, used):
            if i == 12: res.append(list(cur)); return
            for s in self.words_central[i // 2]:
                old = s & used; sub = old
                while True:
                    w = (s, sub)
                    if all(dot(cur[a], w) == H[a][i] for a in range(i)):
                        cur.append(w); rec(i + 1, used | s); cur.pop()
                    if sub == 0: break
                    sub = (sub - 1) & old
        rec(0, 0); return res
    def outer_keys(self, star, y):
        """T-patterns (and words) of the 192 signed words of label y against a star assignment."""
        j, k, t = y; out = {}
        for s in self.words_outer[(j, k)]:
            sub = s
            while True:
                key = []
                for i in range(12):
                    c = star[i][0] & s; d = bin(c).count('1') - 2 * bin((star[i][1] ^ sub) & c).count('1')
                    v = 1 - int((i // 2) in (j, k)) - d
                    if v % 2 or not 0 <= v <= 4: key = None; break
                    key.append(v // 2)
                if key is not None: out.setdefault(tuple(key), []).append((s, sub))
                if sub == 0: break
                sub = (sub - 1) & s
        return out
