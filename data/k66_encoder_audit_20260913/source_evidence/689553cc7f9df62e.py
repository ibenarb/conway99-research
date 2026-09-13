
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, math, multiprocessing as mp
import os, shutil, subprocess, time
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

OPEN_IDS = [
    "v4_09316","v4_09317","v4_09322",
    "v4_09323","v4_09331","v4_09332","v4_09333",
]
EXPECTED_RAW = {
    "v4_09316":662, "v4_09317":677, "v4_09322":664,
    "v4_09323":720, "v4_09331":632, "v4_09332":734, "v4_09333":747,
}
EXPECTED_PRIOR_ACTIVE = {
    "v4_09316":634, "v4_09317":642, "v4_09322":654,
    "v4_09323":708, "v4_09331":608, "v4_09332":724, "v4_09333":741,
}
EXPECTED_CONFLICTS = {
    "v4_09316":84656, "v4_09317":90742, "v4_09322":86157,
    "v4_09323":102608, "v4_09331":69043, "v4_09332":114614, "v4_09333":106572,
}
ROOT_SHA = "b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0"
CADICAL_SHA = "d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
INT64_SQRT = 3037000499

CASE_DATA = {}
ACTIVE = {}
CADICAL = None
OUTDIR = None
QUICK_SECONDS = 5.0
DEEP_SECONDS = 900.0

def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def mem_available_gib():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1024**2
    return -1.0

def resource_check(path, disk_floor, mem_floor):
    free = shutil.disk_usage(path).free / 1024**3
    mem = mem_available_gib()
    if free < disk_floor:
        raise RuntimeError(f"RESOURCE_DISK {free:.1f}GiB < {disk_floor:.1f}GiB")
    if mem >= 0 and mem < mem_floor:
        raise RuntimeError(f"RESOURCE_RAM {mem:.1f}GiB < {mem_floor:.1f}GiB")
    return free, mem

def atomic_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)

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
            H[4*r+i, 4*r+j] = H[4*r+j, 4*r+i] = 1
    for i, (x, y) in enumerate(summary["attached_T_bits"]):
        H[i, 12] = H[12, i] = x
        H[i, 13] = H[13, i] = y
    H[12, 12] = H[13, 13] = 2
    H[12, 13] = H[13, 12] = summary["s"]
    for (r, t), p in zip(((0,1),(0,2),(1,2)), job["matching_permutations"]):
        for i, j in enumerate(p):
            H[4*r+i, 4*t+j] = H[4*t+j, 4*r+i] = 1
    return H

def prepare_case(np, summary, job, common):
    Z, ell, q, caps, cells, products, coords, TARGET = common
    H = build_H(np, summary, job)
    G = TARGET - H @ H - H
    budget = np.array([G[i,j] for i,j in coords], dtype=np.int64)
    mask = np.all(products <= budget, axis=1)
    basis, adj, den = inverse_minor(np, G)
    W = Z[:, basis] @ adj
    lev_all = (W * Z[:,basis]).sum(axis=1)
    mask &= np.all(W @ G[basis,:] == den * Z, axis=1) & (lev_all <= den)
    M = -H - np.eye(14, dtype=np.int64)
    M[:, :4] += 3
    MZ = Z @ M.T
    beta_all = (W * MZ[:,basis]).sum(axis=1)
    mask &= (beta_all >= -3*(den-lev_all)) & (beta_all <= 4*(den-lev_all))
    mask &= np.array([summary["cell_sizes"][c] > 0 for c in cells])

    ids = np.flatnonzero(mask)
    z = Z[ids]
    e = ell[ids]
    qq = q[ids]
    cap = caps[ids].copy()
    cell = cells[ids]
    A = z[:,basis] @ adj
    delta = A @ z[:,basis].T
    eta = A @ MZ[ids][:,basis].T
    require(np.array_equal(eta, eta.T), "eta symmetry failed")
    D = z @ z.T
    lev = lev_all[ids]
    beta = beta_all[ids]
    n = len(ids)
    allowed = np.zeros((n,n), dtype=np.uint8)
    for b in (0,1,2):
        ok = D + b <= 6
        if b == 2:
            ok &= (e[:,None] <= 1) & (e[None,:] <= 1)
        lhs1 = b*den - eta - 4*delta
        r1 = 4*(den-lev) - beta
        lhs2 = eta - b*den - 3*delta
        r2 = 3*(den-lev) + beta
        require(
            max(int(np.max(np.abs(lhs1))), int(np.max(np.abs(lhs2))),
                int(np.max(np.abs(r1))), int(np.max(np.abs(r2)))) <= INT64_SQRT,
            "int64 square bound exceeded",
        )
        ok &= lhs1*lhs1 <= r1[:,None]*r1[None,:]
        ok &= lhs2*lhs2 <= r2[:,None]*r2[None,:]
        if b == 1:
            both = (e[:,None]==0)&(e[None,:]==0)&(qq[:,None]==2)&(qq[None,:]==2)
            ok &= ~(both & ((z[:,:12] @ z[:,:12].T) == 0))
        allowed[ok] |= (1 << b)
    cap[np.diag(allowed)==0] = np.minimum(cap[np.diag(allowed)==0], 1)
    return {
        "H":H, "ids":ids, "z":z, "ell":e, "q":qq, "cap":cap, "cell":cell,
        "budget":budget, "products":products[ids], "allowed":allowed,
        "cell_sizes":np.array(summary["cell_sizes"],dtype=np.int64),
    }

def prior_removed_indices(d, prior_base, cid):
    global_to_local = {int(g): i for i, g in enumerate(d["ids"])}
    removed = set()
    for round_no in (1,2,3):
        p = prior_base / f"star_round_{round_no}" / cid
        if not p.exists():
            continue
        for cnf in p.glob("profile_*.cnf"):
            gid = int(cnf.stem.split("_")[1])
            require(gid in global_to_local, f"prior removed profile {gid} not in current universe for {cid}")
            removed.add(global_to_local[gid])
    return removed

def build_star_cnf(np, cid, idx):
    d = CASE_DATA[cid]
    active = np.array(sorted(ACTIVE[cid]), dtype=np.int64)
    z0 = d["z"][idx]
    rhs = 6*np.ones(14,dtype=np.int64) - (d["H"] + np.eye(14,dtype=np.int64)) @ z0
    dS = int(4 + 2*d["ell"][idx] - d["q"][idx])
    dL = int(2 - d["ell"][idx])

    c = CNF()
    opts = []
    for j in active:
        copies = int(d["cap"][j]) - (1 if j == idx else 0)
        if copies <= 0:
            continue
        allowS = bool(d["allowed"][idx,j] & 2)
        allowL = bool(d["allowed"][idx,j] & 4)
        if not (allowS or allowL):
            continue
        for _ in range(copies):
            sv = c.var() if allowS else False
            lv = c.var() if allowL else False
            if sv is not False and lv is not False:
                c.add(-sv, -lv)
            opts.append((sv, lv, d["z"][j], int(d["cell"][j])))

    c.weighted_eq([(sv,1) for sv,lv,w,cell in opts], dS)
    c.weighted_eq([(lv,1) for sv,lv,w,cell in opts], dL)
    for k in range(14):
        items=[]
        for sv,lv,w,cell in opts:
            wk=int(w[k])
            if wk:
                items.append((sv,wk))
                items.append((lv,2*wk))
        c.weighted_eq(items,int(rhs[k]))
    for cell in range(4):
        limit = int(d["cell_sizes"][cell]) - (1 if int(d["cell"][idx]) == cell else 0)
        vars=[]
        for sv,lv,w,cc in opts:
            if cc == cell:
                if sv is not False: vars.append(sv)
                if lv is not False: vars.append(lv)
        c.cardinality_leq(vars, limit)
    return c

def star_task(task):
    cid, idx, seconds, phase_tag = task
    import numpy as np
    c = build_star_cnf(np, cid, idx)
    phase_dir = Path(OUTDIR) / phase_tag / cid
    phase_dir.mkdir(parents=True, exist_ok=True)
    gid = int(CASE_DATA[cid]["ids"][idx])
    tmp = phase_dir / f"profile_{gid:04d}_{os.getpid()}.cnf"
    write_dimacs(c, tmp)
    start=time.time()
    try:
        with open(os.devnull,"wb") as devnull:
            res=subprocess.run([CADICAL,"--plain",str(tmp)],stdout=devnull,stderr=devnull,timeout=seconds)
        rc=res.returncode
    except subprocess.TimeoutExpired:
        rc=124
    wall=time.time()-start
    if rc == 20:
        keep = phase_dir / f"profile_{gid:04d}.cnf"
        os.replace(tmp, keep)
        status="UNSAT_UNCERTIFIED"
        cpath=str(keep); chash=sha256(keep)
    else:
        if tmp.exists(): tmp.unlink()
        status="SAT" if rc==10 else ("TIMEOUT" if rc==124 else f"OTHER_{rc}")
        cpath=None; chash=None
    return {
        "case":cid,"local_index":int(idx),"global_profile_id":gid,
        "status":status,"exit":int(rc),"wall_seconds":round(wall,3),
        "cnf_path":cpath,"cnf_sha256":chash,
    }

def run_star_phase(tasks, workers, status_seconds, label, disk_floor, mem_floor):
    if not tasks:
        return []
    results=[]
    start=time.time(); last=start
    with cf.ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork")) as ex:
        futs=[ex.submit(star_task,t) for t in tasks]
        for f in cf.as_completed(futs):
            r=f.result(); results.append(r)
            now=time.time()
            if now-last >= status_seconds:
                done=len(results); uns=sum(x["status"]=="UNSAT_UNCERTIFIED" for x in results)
                sat=sum(x["status"]=="SAT" for x in results)
                to=sum(x["status"]=="TIMEOUT" for x in results)
                elapsed=now-start
                rate=done/elapsed if elapsed>0 else 0
                eta=(len(tasks)-done)/rate if rate>0 else None
                free,mem=resource_check(Path(OUTDIR),disk_floor,mem_floor)
                print(
                    f"STATUS phase={label} done={done}/{len(tasks)} unsat={uns} sat={sat} timeout={to} "
                    f"elapsed={elapsed/60:.1f}min ETA={'unknown' if eta is None else f'{eta/60:.1f}min'} "
                    f"RAM={mem:.1f}GiB disk_free={free:.1f}GiB",
                    flush=True
                )
                last=now
    return results

def encode_global(np,d,active):
    active=np.array(sorted(active),dtype=np.int64)
    c=CNF(); n=len(active); caps=d["cap"][active]
    y=[c.var() for _ in range(n)]; extra=[0]*n
    for i,cap in enumerate(caps):
        if int(cap)==2:
            extra[i]=c.var(); c.add(-extra[i],y[i])
    def items(coeff):
        out=[]
        for i,w in enumerate(coeff):
            w=int(w)
            if w:
                out.append((y[i],w))
                if extra[i]: out.append((extra[i],w))
        return out
    P=d["products"][active]
    for k,target in enumerate(d["budget"]):
        c.weighted_eq(items(P[:,k]),int(target))
    cell=d["cell"][active]
    for cc,target in enumerate(d["cell_sizes"]):
        c.weighted_eq(items((cell==cc).astype(np.int64)),int(target))
    allow=d["allowed"][np.ix_(active,active)]
    ii,jj=np.triu_indices(n,1); bad=allow[ii,jj]==0
    for i,j in zip(ii[bad],jj[bad]):
        c.add(-y[int(i)],-y[int(j)])
    return c,active,y,extra

def verify_model(np,path,d,active,y,extra):
    vals={}
    for tok in path.read_text(errors="replace").split():
        try: v=int(tok)
        except ValueError: continue
        if v: vals[abs(v)]=v>0
    x=np.array([1 if vals.get(v,False) else 0 for v in y],dtype=np.int64)
    for i,v in enumerate(extra):
        if v and vals.get(v,False): x[i]+=1
    P=d["products"][active]; cell=d["cell"][active]
    sel=x>0; allow=d["allowed"][np.ix_(active,active)]
    ii,jj=np.triu_indices(len(active),1); bad=allow[ii,jj]==0
    ok=np.array_equal(P.T@x,d["budget"])
    ok &= all(int(x[cell==cc].sum())==int(d["cell_sizes"][cc]) for cc in range(4))
    ok &= bool(np.all(x>=0)&np.all(x<=d["cap"][active]))
    ok &= not bool(np.any(sel[ii[bad]]&sel[jj[bad]]))
    return bool(ok),int(sel.sum())

def global_one(cid, global_dir):
    import numpy as np
    d=CASE_DATA[cid]
    c,active,y,extra=encode_global(np,d,ACTIVE[cid])
    case_dir=Path(global_dir)/cid
    case_dir.mkdir(parents=True,exist_ok=True)
    cnf=case_dir/"model.cnf"; model=case_dir/"model.out"
    write_dimacs(c,cnf)
    start=time.time()
    with open(case_dir/"solver.out","wb") as o,open(case_dir/"solver.err","wb") as e:
        rc=subprocess.run([CADICAL,"--plain","-w",str(model),str(cnf)],stdout=o,stderr=e).returncode
    wall=time.time()-start
    if rc==10:
        ok,support=verify_model(np,model,d,active,y,extra)
        status="SAT_EXACT_WITNESS" if ok else "SAT_INVALID_WITNESS"
    elif rc==20:
        status="UNSAT_UNCERTIFIED"; support=None
    else:
        status=f"OTHER_{rc}"; support=None
    return {
        "id":cid,"status":status,"exit":int(rc),"support":support,
        "wall_seconds":round(wall,3),"profiles":len(active),
        "vars":c.n,"clauses":len(c.cl),"cnf_sha256":sha256(cnf),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    ap.add_argument("--workers",type=int,default=20)
    ap.add_argument("--quick-seconds",type=float,default=5)
    ap.add_argument("--deep-seconds",type=float,default=900)
    ap.add_argument("--status-seconds",type=float,default=600)
    ap.add_argument("--disk-floor-gib",type=float,default=75)
    ap.add_argument("--mem-floor-gib",type=float,default=4)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    a=ap.parse_args()

    run=Path(a.run_dir)
    prior=run/"neighbor_star_preflight_20260909"
    manifest=json.loads((run/"manifest.json").read_text())
    require(manifest.get("case_id")=="k66_s1_t225","wrong case")
    require(manifest.get("root_sha256")==ROOT_SHA,"root hash mismatch")
    require(Path(a.cadical).exists(),"CaDiCaL missing")
    require(sha256(Path(a.cadical))==CADICAL_SHA,"CaDiCaL hash mismatch")
    require(prior.exists(),"prior neighbor-star run missing")

    import numpy as np
    raw,e0=make_profiles(np); cellspec=[(1,1),(1,0),(0,1),(0,0)]
    Z=np.concatenate([np.column_stack((raw,np.tile(c,(936,1)))) for c in cellspec])
    ell=np.tile(e0,4); q=Z[:,12:].sum(axis=1)
    caps=np.where((ell+q)>0,1,2); cells=np.repeat(np.arange(4),936)
    coords=list(zip(*np.triu_indices(14)))
    products=np.array([Z[:,i]*Z[:,j] for i,j in coords]).T
    TARGET=12*np.eye(14,dtype=np.int64)+6*np.ones((14,14),dtype=np.int64)
    for r in range(3): TARGET[4*r:4*r+4,4*r:4*r+4]-=3
    common=(Z,ell,q,caps,cells,products,coords,TARGET)
    jobs={j["id"]:j for j in manifest["jobs"]}

    global CASE_DATA,ACTIVE,CADICAL,OUTDIR,QUICK_SECONDS,DEEP_SECONDS
    CASE_DATA={}; ACTIVE={}
    for cid in OPEN_IDS:
        require(cid in jobs,f"missing job {cid}")
        d=prepare_case(np,manifest["case_summary"],jobs[cid],common)
        require(len(d["ids"])==EXPECTED_RAW[cid],f"raw profile mismatch {cid}")
        ii,jj=np.triu_indices(len(d["ids"]),1)
        require(int((d["allowed"][ii,jj]==0).sum())==EXPECTED_CONFLICTS[cid],f"conflict mismatch {cid}")
        removed=prior_removed_indices(d,prior,cid)
        active=set(range(len(d["ids"])))-removed
        require(len(active)==EXPECTED_PRIOR_ACTIVE[cid],f"prior active mismatch {cid}: {len(active)}")
        CASE_DATA[cid]=d; ACTIVE[cid]=active

    OUTDIR=str(run/"neighbor_star_deep7_autonomous_20260909")
    outdir=Path(OUTDIR); outdir.mkdir(exist_ok=True)
    CADICAL=a.cadical; QUICK_SECONDS=a.quick_seconds; DEEP_SECONDS=a.deep_seconds
    workers=max(1,min(a.workers,20))
    free,mem=resource_check(outdir,a.disk_floor_gib,a.mem_floor_gib)

    print("K66_DEEP7_AUTONOMOUS_START",flush=True)
    print(f"cases=7 workers={workers} quick={a.quick_seconds}s deep={a.deep_seconds}s global_timeouts=NONE",flush=True)
    print("Prior 125 star-UNSAT profiles imported from the earlier exact scout.",flush=True)
    print(f"disk_free={free:.1f}GiB RAM={mem:.1f}GiB",flush=True)

    history=[]
    round_no=0
    while True:
        round_no+=1
        print(f"STAR_ITERATION_START round={round_no} active_total={sum(len(ACTIVE[c]) for c in OPEN_IDS)}",flush=True)

        # Cheap reproducibility pass: classify all currently active stars at the old 5s boundary.
        quick_tasks=[(cid,idx,float(a.quick_seconds),f"round_{round_no}_quick")
                     for cid in OPEN_IDS for idx in sorted(ACTIVE[cid])]
        quick=run_star_phase(quick_tasks,workers,a.status_seconds,f"STAR_QUICK_R{round_no}",a.disk_floor_gib,a.mem_floor_gib)
        quick_uns=[r for r in quick if r["status"]=="UNSAT_UNCERTIFIED"]
        quick_to=[r for r in quick if r["status"]=="TIMEOUT"]
        for r in quick_uns:
            ACTIVE[r["case"]].discard(r["local_index"])
        print(f"STAR_QUICK_DONE round={round_no} unsat={len(quick_uns)} timeouts={len(quick_to)} sat={sum(r['status']=='SAT' for r in quick)}",flush=True)

        # Only the quick timeouts get the expensive 900s treatment, on the updated active sets.
        # Rebuild their CNFs after quick removals, because star feasibility depends on the active profile pool.
        deep_tasks=[(r["case"],r["local_index"],float(a.deep_seconds),f"round_{round_no}_deep")
                    for r in quick_to if r["local_index"] in ACTIVE[r["case"]]]
        deep=run_star_phase(deep_tasks,workers,a.status_seconds,f"STAR_DEEP_R{round_no}",a.disk_floor_gib,a.mem_floor_gib)
        deep_uns=[r for r in deep if r["status"]=="UNSAT_UNCERTIFIED"]
        deep_to=[r for r in deep if r["status"]=="TIMEOUT"]
        for r in deep_uns:
            ACTIVE[r["case"]].discard(r["local_index"])

        rec={
            "round":round_no,
            "quick":{"tasks":len(quick),"unsat":len(quick_uns),"timeouts":len(quick_to),"sat":sum(r["status"]=="SAT" for r in quick)},
            "deep":{"tasks":len(deep),"unsat":len(deep_uns),"timeouts":len(deep_to),"sat":sum(r["status"]=="SAT" for r in deep)},
            "active_counts":{cid:len(ACTIVE[cid]) for cid in OPEN_IDS},
            "hard_star_timeouts":[{"case":r["case"],"profile":r["global_profile_id"]} for r in deep_to],
        }
        history.append(rec)
        atomic_json(outdir/"star_history.json",history)
        print(f"STAR_DEEP_DONE round={round_no} unsat={len(deep_uns)} timeouts={len(deep_to)} sat={sum(r['status']=='SAT' for r in deep)}",flush=True)
        for cid in OPEN_IDS:
            d=CASE_DATA[cid]; act=np.array(sorted(ACTIVE[cid]),dtype=np.int64)
            caps_by=[int(d["cap"][act][d["cell"][act]==cc].sum()) if len(act) else 0 for cc in range(4)]
            survives=all(caps_by[cc]>=int(d["cell_sizes"][cc]) for cc in range(4))
            print(f"STAR_CASE round={round_no} {cid} active={len(act)} cell_caps={caps_by} survives={survives}",flush=True)

        # Fixed point when no new UNSAT profile was found in either quick or deep phase.
        if len(quick_uns)+len(deep_uns)==0:
            print(f"STAR_FIXED_POINT round={round_no} hard_timeouts={len(deep_to)}",flush=True)
            break
        if round_no >= 20:
            raise RuntimeError("unexpected >20 star iterations")

    free,mem=resource_check(outdir,a.disk_floor_gib,a.mem_floor_gib)
    print("GLOBAL_PHASE_START cases=7 workers=7 timeouts=NONE",flush=True)
    global_dir=outdir/"global"
    global_dir.mkdir(exist_ok=True)
    results=[]
    start=time.time(); last=start
    with cf.ProcessPoolExecutor(max_workers=7,mp_context=mp.get_context("fork")) as ex:
        futs={ex.submit(global_one,cid,str(global_dir)):cid for cid in OPEN_IDS}
        while futs:
            done=[f for f in list(futs) if f.done()]
            for f in done:
                cid=futs.pop(f)
                r=f.result(); results.append(r)
                print("GLOBAL_RESULT",json.dumps(r,sort_keys=True),flush=True)
            now=time.time()
            if now-last>=a.status_seconds:
                free,mem=resource_check(outdir,a.disk_floor_gib,a.mem_floor_gib)
                elapsed=now-start
                completed=len(results)
                eta="unknown"
                if completed:
                    rate=completed/elapsed
                    eta=f"{(7-completed)/rate/60:.1f}min"
                counts={}
                for r in results: counts[r["status"]]=counts.get(r["status"],0)+1
                print(f"STATUS phase=GLOBAL elapsed={elapsed/60:.1f}min done={completed}/7 active={len(futs)} counts={counts} ETA={eta} RAM={mem:.1f}GiB disk_free={free:.1f}GiB",flush=True)
                last=now
            if futs and not done: time.sleep(1)

    results.sort(key=lambda r:r["id"])
    final={
        "format":"CONWAY99-K66-NEIGHBOR-STAR-DEEP7-AUTONOMOUS-1",
        "claim_scope":"Exact local star scouts under Astra (8)-(9), followed by no-timeout global profile-conflict scouts. UNSAT remains uncertified until LRAT+Cake and necessity/encoder audit.",
        "prior_removed_profiles":125,
        "star_history":history,
        "final_active_counts":{cid:len(ACTIVE[cid]) for cid in OPEN_IDS},
        "global_results":results,
    }
    atomic_json(outdir/"summary.json",final)
    print("K66_DEEP7_AUTONOMOUS_DONE",json.dumps({r["id"]:r["status"] for r in results},sort_keys=True),flush=True)
    print("RESULT",outdir/"summary.json",flush=True)

if __name__=="__main__":
    main()
