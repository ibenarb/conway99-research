
from __future__ import annotations
import argparse, json, math, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def sha256_file(path):
    h = __import__("hashlib").sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def make_profiles(np):
    modes=[]
    for pair in combinations(range(4),2):
        p=[0]*4
        for i in pair:
            p[i]=1
        modes.append((p,0))
    for i in range(4):
        p=[0]*4
        p[i]=2
        modes.append((p,1))
    rows=[]
    ls=[]
    for z in product(modes, repeat=3):
        ell=sum(q[1] for q in z)
        if ell <= 2:
            rows.append(sum((q[0] for q in z), []))
            ls.append(ell)
    require(len(rows)==936, "profile universe mismatch")
    return np.array(rows,dtype=np.int64), np.array(ls,dtype=np.int64)

def inverse_nonsingular_minor(K):
    import numpy as np
    A=[[F(int(v)) for v in row] for row in K]
    basis=[]
    for k in range(len(A)):
        if A[k][k] == 0:
            continue
        require(A[k][k] > 0, "non-PSD pivot in PSD survivor")
        basis.append(k)
        d=A[k][k]
        for i in range(k+1,len(A)):
            for j in range(i,len(A)):
                A[j][i]=A[i][j]=A[i][j]-A[i][k]*A[k][j]/d
    n=len(basis)
    C=[[F(int(K[i,j])) for j in basis]+[F(int(k==ell)) for ell in range(n)]
       for k,i in enumerate(basis)]
    for k in range(n):
        d=C[k][k]
        require(d != 0, "singular chosen minor")
        C[k]=[v/d for v in C[k]]
        for i in range(n):
            if i == k:
                continue
            d=C[i][k]
            C[i]=[x-d*y for x,y in zip(C[i],C[k])]
    inv=[row[n:] for row in C]
    den=math.lcm(*(x.denominator for row in inv for x in row))
    adj=np.array([[int(x*den) for x in row] for row in inv],dtype=np.int64)
    require(np.array_equal(K[np.ix_(basis,basis)]@adj,
                           den*np.eye(n,dtype=np.int64)), "inverse check failed")
    return basis,adj,den

def build_H(np, summary, job):
    H=np.zeros((14,14),dtype=np.int64)
    for r in range(3):
        for i,j in ((0,1),(2,3)):
            H[4*r+i,4*r+j]=H[4*r+j,4*r+i]=1
    for i,(x,y) in enumerate(summary["attached_T_bits"]):
        H[i,12]=H[12,i]=x
        H[i,13]=H[13,i]=y
    H[12,12]=H[13,13]=2
    H[12,13]=H[13,12]=summary["s"]
    for (r,t),p in zip(((0,1),(0,2),(1,2)),job["matching_permutations"]):
        for i,j in enumerate(p):
            H[4*r+i,4*t+j]=H[4*t+j,4*r+i]=1
    return H

def prepare_case_data(manifest):
    import numpy as np
    summary=manifest["case_summary"]
    require(summary["id"]=="k66_s1_t225","wrong case")
    require(summary["cell_sizes"]==[0,5,5,8],"unexpected k66 cell sizes")
    raw,ell=make_profiles(np)
    cells=[(1,1),(1,0),(0,1),(0,0)]
    Z=np.concatenate([np.column_stack((raw,np.tile(cell,(936,1)))) for cell in cells])
    li=np.tile(ell,4)
    qi=Z[:,12:].sum(axis=1)
    caps=np.where((li+qi)>0,1,2)
    cell_id=np.repeat(np.arange(4),936)
    coords=list(zip(*np.triu_indices(14)))
    products=np.array([Z[:,i]*Z[:,j] for i,j in coords]).T
    TARGET=12*np.eye(14,dtype=np.int64)+6*np.ones((14,14),dtype=np.int64)
    for r in range(3):
        TARGET[4*r:4*r+4,4*r:4*r+4]-=3
    return summary,Z,li,qi,caps,cell_id,coords,products,TARGET

def exact_profile_filter(manifest):
    import numpy as np
    summary,Z,li,qi,caps,cell_id,coords,products,TARGET=prepare_case_data(manifest)
    rows=[]
    payloads=[]
    for job in manifest["jobs"]:
        H=build_H(np,summary,job)
        K=TARGET-H@H-H
        budget=np.array([K[i,j] for i,j in coords])
        mask=np.all(products<=budget,axis=1)
        basis,adj,den=inverse_nonsingular_minor(K)
        W=Z[:,basis]@adj
        kernel=np.all(W@K[basis,:]==den*Z,axis=1)
        lev=(W*Z[:,basis]).sum(axis=1)
        mask &= kernel & (lev<=den)
        before_diag=int(mask.sum())
        M=-H-np.eye(14,dtype=np.int64)
        M[:,:4]+=3
        MZ=Z@M.T
        beta=(W*MZ[:,basis]).sum(axis=1)
        diag=(beta>=-3*(den-lev))&(beta<=4*(den-lev))
        mask &= diag
        after_diag=int(mask.sum())
        mask &= np.array([summary["cell_sizes"][c]>0 for c in cell_id])
        ids=np.flatnonzero(mask)
        cell_counts=[int(((cell_id[ids])==j).sum()) for j in range(4)]
        cell_capacity=[int(caps[ids][cell_id[ids]==j].sum()) for j in range(4)]
        row=dict(
            id=job["id"], code=job["code"], rank=len(basis),
            profile_candidates_before_B_diagonal=before_diag,
            profile_candidates_after_B_diagonal=after_diag,
            removed_by_B_diagonal=before_diag-after_diag,
            cell_profile_counts=cell_counts,
            cell_capacity=cell_capacity,
        )
        rows.append(row)
        payloads.append(dict(
            id=job["id"], code=job["code"], ids=ids.tolist(),
            budget=budget.tolist(),
            products=products[ids].tolist(),
            caps=caps[ids].tolist(),
            cells=cell_id[ids].tolist(),
            cell_sizes=summary["cell_sizes"],
        ))
    return rows,payloads

def milp_one(payload, time_limit):
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    os.environ["OMP_NUM_THREADS"]="1"
    os.environ["OPENBLAS_NUM_THREADS"]="1"
    os.environ["MKL_NUM_THREADS"]="1"
    t=time.time()
    products=np.asarray(payload["products"],dtype=np.int64)
    budget=np.asarray(payload["budget"],dtype=np.int64)
    caps=np.asarray(payload["caps"],dtype=np.int64)
    cells=np.asarray(payload["cells"],dtype=np.int64)
    cell_sizes=np.asarray(payload["cell_sizes"],dtype=np.int64)
    n=len(caps)
    Agram=products.T.astype(float)
    Acell=np.zeros((4,n),dtype=float)
    for j in range(4):
        Acell[j]=(cells==j)
    A=np.vstack([Agram,Acell])
    b=np.concatenate([budget.astype(float),cell_sizes.astype(float)])
    result=milp(
        np.zeros(n),
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n),caps.astype(float)),
        constraints=LinearConstraint(A,b,b),
        options={"time_limit":float(time_limit),"mip_rel_gap":0.0,"presolve":True},
    )
    names={0:"FEASIBLE",1:"TIME_LIMIT",2:"INFEASIBLE_UNCERTIFIED",3:"UNBOUNDED",4:"OTHER"}
    status=names.get(int(result.status),f"STATUS_{result.status}")
    witness=None
    if result.x is not None:
        x=np.rint(result.x).astype(np.int64)
        exact_gram=np.array_equal(products.T@x,budget)
        exact_cells=all(int(x[cells==j].sum())==int(cell_sizes[j]) for j in range(4))
        exact_bounds=bool(np.all(x>=0) and np.all(x<=caps))
        exact=bool(exact_gram and exact_cells and exact_bounds)
        if exact:
            status="FEASIBLE_EXACT_WITNESS"
        witness=dict(exact_check=exact,support=int((x>0).sum()))
    return dict(
        id=payload["id"], code=payload["code"], variables=n,
        status=status, scipy_status=int(result.status),
        message=str(result.message), witness=witness,
        wall_seconds=round(time.time()-t,3),
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    ap.add_argument("--workers",type=int,default=6)
    ap.add_argument("--case-seconds",type=int,default=180)
    ap.add_argument("--status-seconds",type=int,default=600)
    args=ap.parse_args()

    run=Path(args.run_dir)
    manifest_path=run/"manifest.json"
    state_path=run/"state.json"
    require(manifest_path.exists(),"manifest.json missing")
    require(state_path.exists(),"state.json missing")
    manifest=json.loads(manifest_path.read_text())
    state=json.loads(state_path.read_text())
    require(manifest.get("case_id")=="k66_s1_t225","wrong manifest case")
    require(manifest.get("residual_jobs")==23,"expected 23 residual jobs")
    require(state.get("status")=="INTERRUPTED","expected interrupted monolithic pilot")
    require(state.get("certified")==0,"unexpected certified research result")
    require(manifest.get("root_sha256")=="b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0",
            "root hash mismatch")

    try:
        import numpy as np
        import scipy
        from scipy.optimize import milp as _milp
    except Exception as e:
        raise RuntimeError("This preflight needs NumPy and SciPy with scipy.optimize.milp: "+repr(e))

    print("K66_PROFILE_PREFLIGHT_START",flush=True)
    print(f"source_run={run}",flush=True)
    print(f"numpy={np.__version__} scipy={scipy.__version__}",flush=True)
    print("No SAT, no LRAT, no Cake, no repository modifications.",flush=True)

    rows,payloads=exact_profile_filter(manifest)
    before=sum(r["profile_candidates_before_B_diagonal"] for r in rows)
    after=sum(r["profile_candidates_after_B_diagonal"] for r in rows)
    print(f"B_DIAGONAL_PASS H=23 profile_pairs={before}->{after} removed={before-after}",flush=True)
    for r in rows:
        print(f"PROFILE {r['id']} {r['profile_candidates_before_B_diagonal']}->{r['profile_candidates_after_B_diagonal']} "
              f"cells={r['cell_profile_counts']} caps={r['cell_capacity']}",flush=True)

    outdir=run/"profile_multiplicity_preflight_20260909"
    outdir.mkdir(exist_ok=True)
    (outdir/"individual_profile_filter.json").write_text(json.dumps(rows,indent=2)+"\n")

    results=[]
    start=time.time()
    last=start
    workers=max(1,min(args.workers,8))
    print(f"MULTIPLICITY_MILP_START cases=23 workers={workers} per_case_limit={args.case_seconds}s",flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(milp_one,p,args.case_seconds):p["id"] for p in payloads}
        while futs:
            done=[f for f in list(futs) if f.done()]
            for f in done:
                cid=futs.pop(f)
                try:
                    r=f.result()
                except Exception as e:
                    r={"id":cid,"status":"ERROR","error":repr(e)}
                results.append(r)
                print("MILP_RESULT",json.dumps(r,sort_keys=True),flush=True)
            now=time.time()
            if now-last>=args.status_seconds:
                from collections import Counter
                c=Counter(r["status"] for r in results)
                print(f"STATUS elapsed={(now-start)/60:.1f}min finished={len(results)}/23 "
                      f"counts={dict(c)} ETA={'unknown' if not results else 'bounded by per-case limits'}",flush=True)
                last=now
            if futs:
                time.sleep(1)

    results.sort(key=lambda x:x["id"])
    from collections import Counter
    counts=Counter(r["status"] for r in results)
    summary={
        "format":"CONWAY99-K66-PROFILE-MULTIPLICITY-PREFLIGHT-1",
        "source_manifest_sha256":sha256_file(manifest_path),
        "source_state_status":state["status"],
        "root_sha256":manifest["root_sha256"],
        "individual_profile_totals":{"before_B_diagonal":before,"after_B_diagonal":after},
        "milp_status_counts":dict(counts),
        "note":"INFEASIBLE_UNCERTIFIED is a numerical MILP preflight result, not a proof. "
               "FEASIBLE_EXACT_WITNESS has its integer witness rechecked exactly against Gram and cell equations.",
        "results":results,
    }
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("K66_PROFILE_PREFLIGHT_DONE",json.dumps(dict(counts),sort_keys=True),flush=True)
    print("RESULT",outdir/"summary.json",flush=True)

if __name__=="__main__":
    main()
