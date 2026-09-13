
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, math, multiprocessing as mp
import os, shutil, subprocess, tempfile, time
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

OPEN_IDS = [
    "v4_09232","v4_09316","v4_09317","v4_09322",
    "v4_09323","v4_09331","v4_09332","v4_09333",
]
EXPECTED_PROFILES = {
    "v4_09232":350, "v4_09316":662, "v4_09317":677, "v4_09322":664,
    "v4_09323":720, "v4_09331":632, "v4_09332":734, "v4_09333":747,
}
EXPECTED_CONFLICTS = {
    "v4_09232":19547, "v4_09316":84656, "v4_09317":90742, "v4_09322":86157,
    "v4_09323":102608, "v4_09331":69043, "v4_09332":114614, "v4_09333":106572,
}
ROOT_SHA = "b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0"
CADICAL_SHA = "d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
INT64_SQRT = 3037000499

CASE_DATA = {}
ACTIVE = {}
ROUND_DIR = None
CADICAL = None
STAR_SECONDS = None

def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []
    def var(self):
        self.n += 1
        return self.n
    def add(self, *xs):
        self.cl.append(list(xs))
    def clause(self, *xs):
        if any(x is True for x in xs):
            return
        self.add(*[x for x in xs if x is not False])
    def weighted_eq(self, items, target):
        weights = {}
        for v, w in items:
            if isinstance(v, bool):
                if v:
                    target -= w
                continue
            if w:
                weights[v] = weights.get(v, 0) + int(w)
        a = sorted(weights.items())
        suffix = [0] * (len(a) + 1)
        for i in range(len(a) - 1, -1, -1):
            suffix[i] = suffix[i + 1] + a[i][1]
        memo = {}
        def neg(v):
            return (not v) if isinstance(v, bool) else -v
        def node(i, rest):
            if rest < 0 or rest > suffix[i]:
                return False
            if i == len(a):
                return rest == 0
            key = (i, rest)
            if key in memo:
                return memo[key]
            x, w = a[i]
            lo = node(i + 1, rest)
            hi = node(i + 1, rest - w)
            if lo is hi:
                memo[key] = lo
                return lo
            v = self.var()
            memo[key] = v
            self.clause(-v, -x, hi)
            self.clause(-v, x, lo)
            self.clause(-x, neg(hi), v)
            self.clause(x, neg(lo), v)
            return v
        self.clause(node(0, int(target)))
    def cardinality_leq(self, variables, limit):
        variables = [v for v in variables if v is not False]
        if limit < 0:
            self.add()
            return
        if len(variables) <= limit:
            return
        slack = [self.var() for _ in range(limit)]
        self.weighted_eq([(v, 1) for v in variables + slack], limit)

def write_dimacs(c, path):
    with open(path, "w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:
            f.write(" ".join(map(str, cl)) + " 0\n")

def make_profiles(np):
    modes = []
    for pair in combinations(range(4), 2):
        p = [0] * 4
        for i in pair:
            p[i] = 1
        modes.append((p, 0))
    for i in range(4):
        p = [0] * 4
        p[i] = 2
        modes.append((p, 1))
    rows, ell = [], []
    for z in product(modes, repeat=3):
        e = sum(q[1] for q in z)
        if e <= 2:
            rows.append(sum((q[0] for q in z), []))
            ell.append(e)
    require(len(rows) == 936, "profile universe mismatch")
    return np.array(rows, dtype=np.int64), np.array(ell, dtype=np.int64)

def inverse_minor(np, K):
    A = [[F(int(v)) for v in row] for row in K]
    basis = []
    for k in range(len(A)):
        if A[k][k] == 0:
            continue
        require(A[k][k] > 0, "negative PSD pivot")
        basis.append(k)
        d = A[k][k]
        for i in range(k + 1, len(A)):
            for j in range(i, len(A)):
                A[j][i] = A[i][j] = A[i][j] - A[i][k] * A[k][j] / d
    n = len(basis)
    C = [
        [F(int(K[i, j])) for j in basis] + [F(int(k == q)) for q in range(n)]
        for k, i in enumerate(basis)
    ]
    for k in range(n):
        d = C[k][k]
        require(d != 0, "singular selected minor")
        C[k] = [v / d for v in C[k]]
        for i in range(n):
            if i == k:
                continue
            d = C[i][k]
            C[i] = [x - d * y for x, y in zip(C[i], C[k])]
    inv = [r[n:] for r in C]
    den = math.lcm(*(x.denominator for r in inv for x in r))
    adj = np.array([[int(x * den) for x in r] for r in inv], dtype=np.int64)
    require(
        np.array_equal(K[np.ix_(basis, basis)] @ adj, den * np.eye(n, dtype=np.int64)),
        "inverse check failed",
    )
    return basis, adj, den

def build_H(np, summary, job):
    H = np.zeros((14, 14), dtype=np.int64)
    for r in range(3):
        for i, j in ((0, 1), (2, 3)):
            H[4 * r + i, 4 * r + j] = H[4 * r + j, 4 * r + i] = 1
    for i, (x, y) in enumerate(summary["attached_T_bits"]):
        H[i, 12] = H[12, i] = x
        H[i, 13] = H[13, i] = y
    H[12, 12] = H[13, 13] = 2
    H[12, 13] = H[13, 12] = summary["s"]
    for (r, t), p in zip(((0, 1), (0, 2), (1, 2)), job["matching_permutations"]):
        for i, j in enumerate(p):
            H[4 * r + i, 4 * t + j] = H[4 * t + j, 4 * r + i] = 1
    return H

def prepare_case(np, summary, job, common):
    Z, ell, q, caps, cells, products, coords, TARGET = common
    H = build_H(np, summary, job)
    G = TARGET - H @ H - H
    budget = np.array([G[i, j] for i, j in coords], dtype=np.int64)
    mask = np.all(products <= budget, axis=1)
    basis, adj, den = inverse_minor(np, G)
    W = Z[:, basis] @ adj
    lev_all = (W * Z[:, basis]).sum(axis=1)
    mask &= np.all(W @ G[basis, :] == den * Z, axis=1) & (lev_all <= den)
    M = -H - np.eye(14, dtype=np.int64)
    M[:, :4] += 3
    MZ = Z @ M.T
    beta_all = (W * MZ[:, basis]).sum(axis=1)
    mask &= (beta_all >= -3 * (den - lev_all)) & (beta_all <= 4 * (den - lev_all))
    mask &= np.array([summary["cell_sizes"][c] > 0 for c in cells])

    ids = np.flatnonzero(mask)
    z = Z[ids]
    e = ell[ids]
    qq = q[ids]
    cap = caps[ids].copy()
    cell = cells[ids]
    A = z[:, basis] @ adj
    delta = A @ z[:, basis].T
    eta = A @ MZ[ids][:, basis].T
    require(np.array_equal(eta, eta.T), "eta symmetry failed")
    D = z @ z.T
    lev = lev_all[ids]
    beta = beta_all[ids]
    n = len(ids)
    allowed = np.zeros((n, n), dtype=np.uint8)
    for b in (0, 1, 2):
        ok = D + b <= 6
        if b == 2:
            ok &= (e[:, None] <= 1) & (e[None, :] <= 1)
        lhs1 = b * den - eta - 4 * delta
        r1 = 4 * (den - lev) - beta
        lhs2 = eta - b * den - 3 * delta
        r2 = 3 * (den - lev) + beta
        require(
            max(
                int(np.max(np.abs(lhs1))), int(np.max(np.abs(lhs2))),
                int(np.max(np.abs(r1))), int(np.max(np.abs(r2))),
            ) <= INT64_SQRT,
            "int64 square bound exceeded",
        )
        ok &= lhs1 * lhs1 <= r1[:, None] * r1[None, :]
        ok &= lhs2 * lhs2 <= r2[:, None] * r2[None, :]
        if b == 1:
            both = (e[:, None] == 0) & (e[None, :] == 0) & (qq[:, None] == 2) & (qq[None, :] == 2)
            ok &= ~(both & ((z[:, :12] @ z[:, :12].T) == 0))
        allowed[ok] |= (1 << b)
    cap[np.diag(allowed) == 0] = np.minimum(cap[np.diag(allowed) == 0], 1)
    return {
        "H": H, "ids": ids, "z": z, "ell": e, "q": qq, "cap": cap, "cell": cell,
        "budget": budget, "products": products[ids], "allowed": allowed,
        "cell_sizes": np.array(summary["cell_sizes"], dtype=np.int64),
    }

def build_star_cnf(np, cid, idx):
    d = CASE_DATA[cid]
    active = np.array(sorted(ACTIVE[cid]), dtype=np.int64)
    z0 = d["z"][idx]
    rhs = 6 * np.ones(14, dtype=np.int64) - (d["H"] + np.eye(14, dtype=np.int64)) @ z0
    dS = int(4 + 2 * d["ell"][idx] - d["q"][idx])
    dL = int(2 - d["ell"][idx])

    c = CNF()
    options = []
    for j in active:
        copies = int(d["cap"][j]) - (1 if j == idx else 0)
        if copies <= 0:
            continue
        allowS = bool(d["allowed"][idx, j] & 2)
        allowL = bool(d["allowed"][idx, j] & 4)
        if not (allowS or allowL):
            continue
        for _ in range(copies):
            sv = c.var() if allowS else False
            lv = c.var() if allowL else False
            if sv is not False and lv is not False:
                c.add(-sv, -lv)
            options.append((sv, lv, d["z"][j], int(d["cell"][j])))

    c.weighted_eq([(sv, 1) for sv, lv, w, cell in options], dS)
    c.weighted_eq([(lv, 1) for sv, lv, w, cell in options], dL)
    for k in range(14):
        items = []
        for sv, lv, w, cell in options:
            if int(w[k]):
                items.append((sv, int(w[k])))
                items.append((lv, 2 * int(w[k])))
        c.weighted_eq(items, int(rhs[k]))

    # At most the number of actual vertices available in each T-cell.
    for cell in range(4):
        limit = int(d["cell_sizes"][cell]) - (1 if int(d["cell"][idx]) == cell else 0)
        variables = []
        for sv, lv, w, ccell in options:
            if ccell == cell:
                if sv is not False:
                    variables.append(sv)
                if lv is not False:
                    variables.append(lv)
        c.cardinality_leq(variables, limit)
    return c

def star_task(task):
    cid, idx, round_no = task
    c = build_star_cnf(__import__("numpy"), cid, idx)
    case_dir = Path(ROUND_DIR) / cid
    case_dir.mkdir(parents=True, exist_ok=True)
    tmp = case_dir / f"profile_{int(CASE_DATA[cid]['ids'][idx]):04d}_{os.getpid()}.cnf"
    write_dimacs(c, tmp)
    start = time.time()
    try:
        with open(os.devnull, "wb") as devnull:
            res = subprocess.run(
                [CADICAL, "--plain", str(tmp)],
                stdout=devnull, stderr=devnull, timeout=STAR_SECONDS,
            )
        rc = res.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    wall = time.time() - start
    global_id = int(CASE_DATA[cid]["ids"][idx])
    keep = None
    if rc == 20:
        keep = case_dir / f"profile_{global_id:04d}.cnf"
        os.replace(tmp, keep)
        status = "UNSAT_UNCERTIFIED"
    else:
        if tmp.exists():
            tmp.unlink()
        status = "SAT_KEEP" if rc == 10 else ("TIMEOUT_KEEP" if rc == 124 else f"OTHER_{rc}_KEEP")
    return {
        "case": cid, "local_index": int(idx), "global_profile_id": global_id,
        "status": status, "exit": int(rc), "wall_seconds": round(wall, 3),
        "cnf_sha256": sha256(keep) if keep is not None else None,
        "cnf_path": str(keep) if keep is not None else None,
    }

def encode_global(np, d, active):
    active = np.array(sorted(active), dtype=np.int64)
    c = CNF()
    n = len(active)
    caps = d["cap"][active]
    y = [c.var() for _ in range(n)]
    extra = [0] * n
    for i, cap in enumerate(caps):
        if int(cap) == 2:
            extra[i] = c.var()
            c.add(-extra[i], y[i])
    def items(coeff):
        out = []
        for i, w in enumerate(coeff):
            w = int(w)
            if w:
                out.append((y[i], w))
                if extra[i]:
                    out.append((extra[i], w))
        return out
    P = d["products"][active]
    for k, target in enumerate(d["budget"]):
        c.weighted_eq(items(P[:, k]), int(target))
    cell = d["cell"][active]
    for cc, target in enumerate(d["cell_sizes"]):
        c.weighted_eq(items((cell == cc).astype(np.int64)), int(target))
    allow = d["allowed"][np.ix_(active, active)]
    ii, jj = np.triu_indices(n, 1)
    bad = allow[ii, jj] == 0
    for i, j in zip(ii[bad], jj[bad]):
        c.add(-y[int(i)], -y[int(j)])
    return c, active, y, extra

def verify_global_model(np, model_path, d, active, y, extra):
    vals = {}
    for tok in model_path.read_text(errors="replace").split():
        try:
            v = int(tok)
        except ValueError:
            continue
        if v:
            vals[abs(v)] = v > 0
    x = np.array([1 if vals.get(v, False) else 0 for v in y], dtype=np.int64)
    for i, v in enumerate(extra):
        if v and vals.get(v, False):
            x[i] += 1
    P = d["products"][active]
    cell = d["cell"][active]
    selected = x > 0
    allow = d["allowed"][np.ix_(active, active)]
    ii, jj = np.triu_indices(len(active), 1)
    bad = allow[ii, jj] == 0
    ok = np.array_equal(P.T @ x, d["budget"])
    ok &= all(int(x[cell == cc].sum()) == int(d["cell_sizes"][cc]) for cc in range(4))
    ok &= bool(np.all(x >= 0) and np.all(x <= d["cap"][active]))
    ok &= not bool(np.any(selected[ii[bad]] & selected[jj[bad]]))
    return bool(ok), int(selected.sum())

def global_task(args):
    import numpy as np
    cid, outdir, seconds = args
    d = CASE_DATA[cid]
    c, active, y, extra = encode_global(np, d, ACTIVE[cid])
    case_dir = Path(outdir) / cid
    case_dir.mkdir(parents=True, exist_ok=True)
    cnf = case_dir / "model.cnf"
    model = case_dir / "model.out"
    write_dimacs(c, cnf)
    start = time.time()
    try:
        with open(case_dir / "solver.out", "wb") as o, open(case_dir / "solver.err", "wb") as e:
            res = subprocess.run(
                [CADICAL, "--plain", "-w", str(model), str(cnf)],
                stdout=o, stderr=e, timeout=seconds,
            )
        rc = res.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    wall = time.time() - start
    if rc == 10:
        ok, support = verify_global_model(np, model, d, active, y, extra)
        status = "SAT_EXACT_WITNESS" if ok else "SAT_INVALID_WITNESS"
    elif rc == 20:
        support = None
        status = "UNSAT_UNCERTIFIED"
    elif rc == 124:
        support = None
        status = "TIMEOUT"
    else:
        support = None
        status = f"OTHER_{rc}"
    return {
        "id": cid, "status": status, "exit": int(rc), "support": support,
        "wall_seconds": round(wall, 3), "profiles": len(active),
        "vars": c.n, "clauses": len(c.cl), "cnf_sha256": sha256(cnf),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--star-seconds", type=float, default=5)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--global-seconds", type=float, default=1800)
    ap.add_argument("--status-seconds", type=float, default=600)
    ap.add_argument("--cadical", default=str(Path.home() / ".local/bin/cadical"))
    a = ap.parse_args()

    run = Path(a.run_dir)
    manifest = json.loads((run / "manifest.json").read_text())
    state = json.loads((run / "state.json").read_text())
    require(manifest.get("case_id") == "k66_s1_t225", "wrong source case")
    require(manifest.get("residual_jobs") == 23, "expected 23 residual V4 jobs")
    require(manifest.get("root_sha256") == ROOT_SHA, "root hash mismatch")
    require(state.get("certified") == 0, "unexpected old root-CNF certification")
    require(Path(a.cadical).exists(), "CaDiCaL missing")
    require(sha256(Path(a.cadical)) == CADICAL_SHA, "CaDiCaL hash mismatch")

    import numpy as np
    raw, e0 = make_profiles(np)
    cellspec = [(1,1),(1,0),(0,1),(0,0)]
    Z = np.concatenate([np.column_stack((raw, np.tile(c, (936,1)))) for c in cellspec])
    ell = np.tile(e0, 4)
    q = Z[:,12:].sum(axis=1)
    caps = np.where((ell + q) > 0, 1, 2)
    cells = np.repeat(np.arange(4), 936)
    coords = list(zip(*np.triu_indices(14)))
    products = np.array([Z[:,i] * Z[:,j] for i,j in coords]).T
    TARGET = 12*np.eye(14,dtype=np.int64) + 6*np.ones((14,14),dtype=np.int64)
    for r in range(3):
        TARGET[4*r:4*r+4,4*r:4*r+4] -= 3
    common = (Z,ell,q,caps,cells,products,coords,TARGET)
    jobs = {j["id"]: j for j in manifest["jobs"]}

    global CASE_DATA, ACTIVE, ROUND_DIR, CADICAL, STAR_SECONDS
    CASE_DATA = {}
    ACTIVE = {}
    for cid in OPEN_IDS:
        require(cid in jobs, f"missing V4 job {cid}")
        d = prepare_case(np, manifest["case_summary"], jobs[cid], common)
        require(len(d["ids"]) == EXPECTED_PROFILES[cid], f"profile count mismatch {cid}")
        ii,jj = np.triu_indices(len(d["ids"]),1)
        conflicts = int((d["allowed"][ii,jj] == 0).sum())
        require(conflicts == EXPECTED_CONFLICTS[cid], f"pair conflict mismatch {cid}")
        CASE_DATA[cid] = d
        ACTIVE[cid] = set(range(len(d["ids"])))

    CADICAL = a.cadical
    STAR_SECONDS = float(a.star_seconds)
    outdir = run / "neighbor_star_preflight_20260909"
    outdir.mkdir(exist_ok=True)
    print("K66_NEIGHBOR_STAR_PREFLIGHT_START", flush=True)
    print("Open H cases=8. Exact local star CNF scout for Astra (8)-(9), then global profile-conflict re-scout.", flush=True)
    print(f"workers={min(max(a.workers,1),20)} star_timeout={STAR_SECONDS}s rounds<={a.rounds} global_timeout={a.global_seconds}s", flush=True)
    print("No LRAT/Cake in this phase; star/global UNSAT are candidates for later certification.", flush=True)

    all_star_results = []
    workers = min(max(a.workers,1),20)
    ctx = mp.get_context("fork")
    for round_no in range(1, int(a.rounds)+1):
        ROUND_DIR = str(outdir / f"star_round_{round_no}")
        Path(ROUND_DIR).mkdir(exist_ok=True)
        tasks = [(cid, idx, round_no) for cid in OPEN_IDS for idx in sorted(ACTIVE[cid])]
        print(f"STAR_ROUND_START round={round_no} tasks={len(tasks)}", flush=True)
        start = time.time()
        done_count = 0
        removed = {cid: [] for cid in OPEN_IDS}
        last = start
        with cf.ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as ex:
            futs = [ex.submit(star_task, t) for t in tasks]
            for f in cf.as_completed(futs):
                r = f.result()
                all_star_results.append(r)
                done_count += 1
                if r["status"] == "UNSAT_UNCERTIFIED":
                    removed[r["case"]].append(r["local_index"])
                now = time.time()
                if now-last >= a.status_seconds:
                    uns = sum(len(v) for v in removed.values())
                    print(f"STATUS phase=STAR round={round_no} done={done_count}/{len(tasks)} star_unsat={uns} elapsed={(now-start)/60:.1f}min ETA=unknown", flush=True)
                    last = now
        total_removed = 0
        for cid in OPEN_IDS:
            for idx in removed[cid]:
                ACTIVE[cid].discard(idx)
            total_removed += len(removed[cid])
        round_summary = {}
        for cid in OPEN_IDS:
            d = CASE_DATA[cid]
            active = np.array(sorted(ACTIVE[cid]),dtype=np.int64)
            caps_by_cell = [
                int(d["cap"][active][d["cell"][active] == cc].sum()) if len(active) else 0
                for cc in range(4)
            ]
            round_summary[cid] = {
                "active_profiles": len(active),
                "removed_this_round": len(removed[cid]),
                "cell_capacity": caps_by_cell,
                "H_capacity_survives": all(caps_by_cell[cc] >= int(d["cell_sizes"][cc]) for cc in range(4)),
            }
            print(f"STAR_CASE round={round_no} {cid} active={len(active)} removed={len(removed[cid])} cell_caps={caps_by_cell} survives={round_summary[cid]['H_capacity_survives']}", flush=True)
        (outdir / f"star_round_{round_no}_summary.json").write_text(json.dumps(round_summary,indent=2,sort_keys=True)+"\n")
        print(f"STAR_ROUND_DONE round={round_no} removed={total_removed}", flush=True)
        if total_removed == 0:
            break

    # Global re-scout with star-UNSAT profiles removed.
    global_dir = outdir / "global_rescout"
    global_dir.mkdir(exist_ok=True)
    print("GLOBAL_RESCOUT_START cases=8", flush=True)
    with cf.ProcessPoolExecutor(max_workers=8, mp_context=ctx) as ex:
        futs = [ex.submit(global_task, (cid, str(global_dir), float(a.global_seconds))) for cid in OPEN_IDS]
        global_results = [f.result() for f in cf.as_completed(futs)]
    global_results.sort(key=lambda x: x["id"])
    for r in global_results:
        print("GLOBAL_RESULT", json.dumps(r,sort_keys=True), flush=True)

    final = {
        "format":"CONWAY99-K66-NEIGHBOR-STAR-PREFLIGHT-1",
        "claim_scope":"Necessary local neighbor-star support from Astra (8)-(9), followed by necessary profile-frequency+pair-conflict global re-scout. No UNSAT promoted without LRAT+Cake and encoder/necessity audit.",
        "open_ids":OPEN_IDS,
        "active_profile_counts":{cid:len(ACTIVE[cid]) for cid in OPEN_IDS},
        "star_unsat_count":sum(1 for r in all_star_results if r["status"]=="UNSAT_UNCERTIFIED"),
        "star_timeout_count":sum(1 for r in all_star_results if r["status"]=="TIMEOUT_KEEP"),
        "global_results":global_results,
    }
    (outdir / "summary.json").write_text(json.dumps(final,indent=2,sort_keys=True)+"\n")
    print("K66_NEIGHBOR_STAR_PREFLIGHT_DONE", json.dumps({
        "star_unsat":final["star_unsat_count"],
        "star_timeouts":final["star_timeout_count"],
        "global_counts":{s:sum(r["status"]==s for r in global_results) for s in sorted({r["status"] for r in global_results})},
    },sort_keys=True), flush=True)
    print("RESULT", outdir / "summary.json", flush=True)

if __name__ == "__main__":
    main()
