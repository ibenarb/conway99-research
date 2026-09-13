
from __future__ import annotations
import argparse, json, math, os, time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

INT64_SQRT = 3037000499

def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)

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
    rows=[]; ls=[]
    for z in product(modes,repeat=3):
        ell=sum(q[1] for q in z)
        if ell<=2:
            rows.append(sum((q[0] for q in z),[]))
            ls.append(ell)
    require(len(rows)==936,"profile universe mismatch")
    return np.array(rows,dtype=np.int64),np.array(ls,dtype=np.int64)

def inverse_minor(np,K):
    A=[[F(int(v)) for v in row] for row in K]; basis=[]
    for k in range(len(A)):
        if A[k][k]==0:
            continue
        require(A[k][k]>0,"negative PSD pivot")
        basis.append(k); d=A[k][k]
        for i in range(k+1,len(A)):
            for j in range(i,len(A)):
                A[j][i]=A[i][j]=A[i][j]-A[i][k]*A[k][j]/d
    n=len(basis)
    C=[[F(int(K[i,j])) for j in basis]+[F(int(k==ell)) for ell in range(n)]
       for k,i in enumerate(basis)]
    for k in range(n):
        d=C[k][k]; require(d!=0,"singular selected minor")
        C[k]=[v/d for v in C[k]]
        for i in range(n):
            if i==k:
                continue
            d=C[i][k]
            C[i]=[x-d*y for x,y in zip(C[i],C[k])]
    inv=[r[n:] for r in C]
    den=math.lcm(*(x.denominator for r in inv for x in r))
    adj=np.array([[int(x*den) for x in r] for r in inv],dtype=np.int64)
    require(np.array_equal(K[np.ix_(basis,basis)]@adj,
                           den*np.eye(n,dtype=np.int64)),"inverse check failed")
    return basis,adj,den

def build_H(np,summary,job):
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

def case_model_payload(np,summary,job,common):
    Z,ell,q,caps,cells,products,coords,TARGET=common
    H=build_H(np,summary,job)
    G=TARGET-H@H-H
    budget=np.array([G[i,j] for i,j in coords],dtype=np.int64)

    mask=np.all(products<=budget,axis=1)
    basis,adj,den=inverse_minor(np,G)
    W=Z[:,basis]@adj
    kernel=np.all(W@G[basis,:]==den*Z,axis=1)
    lev_all=(W*Z[:,basis]).sum(axis=1)
    mask &= kernel & (lev_all<=den)

    M=-H-np.eye(14,dtype=np.int64)
    M[:,:4]+=3
    MZ=Z@M.T
    beta_all=(W*MZ[:,basis]).sum(axis=1)
    mask &= (beta_all>=-3*(den-lev_all))&(beta_all<=4*(den-lev_all))
    mask &= np.array([summary["cell_sizes"][c]>0 for c in cells])

    ids=np.flatnonzero(mask)
    z=Z[ids]
    e=ell[ids]
    qq=q[ids]
    cap=caps[ids].copy()
    cell=cells[ids]
    zb=z[:,basis]
    A=zb@adj
    delta=A@zb.T
    eta=A@(MZ[ids][:,basis].T)
    require(np.array_equal(eta,eta.T),"eta symmetry failed")
    D=z@z.T
    lev=lev_all[ids]
    beta=beta_all[ids]
    n=len(ids)
    allowed=np.zeros((n,n),dtype=np.uint8)

    for b in (0,1,2):
        ok=(D+b<=6)
        if b==2:
            ok &= (e[:,None]<=1)&(e[None,:]<=1)
        lhs1=b*den-eta-4*delta
        r1=4*(den-lev)-beta
        lhs2=eta-b*den-3*delta
        r2=3*(den-lev)+beta
        require(max(int(np.max(np.abs(lhs1))),int(np.max(np.abs(lhs2))),
                    int(np.max(np.abs(r1))),int(np.max(np.abs(r2))))<=INT64_SQRT,
                "int64 square bound exceeded")
        ok &= lhs1*lhs1<=r1[:,None]*r1[None,:]
        ok &= lhs2*lhs2<=r2[:,None]*r2[None,:]
        if b==1:
            both=(e[:,None]==0)&(e[None,:]==0)&(qq[:,None]==2)&(qq[None,:]==2)
            datt=z[:,:12]@z[:,:12].T
            ok &= ~(both&(datt==0))
        allowed[ok] |= (1<<b)

    # If two copies of the same profile cannot have any B color, multiplicity <= 1.
    cap[np.diag(allowed)==0]=np.minimum(cap[np.diag(allowed)==0],1)

    ii,jj=np.triu_indices(n,1)
    conflict=(allowed[ii,jj]==0)
    ci=ii[conflict].astype(np.int32)
    cj=jj[conflict].astype(np.int32)

    return {
        "id":job["id"],
        "code":job["code"],
        "products":products[ids].astype(np.int16),
        "budget":budget.astype(np.int16),
        "caps":cap.astype(np.int8),
        "cells":cell.astype(np.int8),
        "cell_sizes":np.array(summary["cell_sizes"],dtype=np.int8),
        "conflict_i":ci,
        "conflict_j":cj,
        "profiles":n,
        "conflicts":len(ci),
    }

def solve_one(payload,time_limit):
    os.environ["OMP_NUM_THREADS"]="1"
    os.environ["OPENBLAS_NUM_THREADS"]="1"
    os.environ["MKL_NUM_THREADS"]="1"
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import coo_matrix, csr_matrix, hstack, vstack

    t=time.time()
    P=np.asarray(payload["products"],dtype=np.int64)
    budget=np.asarray(payload["budget"],dtype=np.int64)
    cap=np.asarray(payload["caps"],dtype=np.int64)
    cell=np.asarray(payload["cells"],dtype=np.int64)
    cell_sizes=np.asarray(payload["cell_sizes"],dtype=np.int64)
    ci=np.asarray(payload["conflict_i"],dtype=np.int64)
    cj=np.asarray(payload["conflict_j"],dtype=np.int64)
    n=len(cap)

    # Variables: integer multiplicities x_i and binary support indicators y_i.
    Agram=csr_matrix(P.T.astype(float))
    Acell=csr_matrix(np.vstack([(cell==c).astype(float) for c in range(4)]))
    Ax=vstack([Agram,Acell],format="csr")
    Aeq=hstack([Ax,csr_matrix((Ax.shape[0],n))],format="csr")
    beq=np.concatenate([budget.astype(float),cell_sizes.astype(float)])

    # Link x_i>0 <=> y_i=1:
    # x_i - cap_i*y_i <= 0; y_i - x_i <= 0.
    rows=[]; cols=[]; vals=[]; ub=[]
    r=0
    for i,c in enumerate(cap):
        rows.extend((r,r)); cols.extend((i,n+i)); vals.extend((1.0,-float(c))); ub.append(0.0); r+=1
        rows.extend((r,r)); cols.extend((i,n+i)); vals.extend((-1.0,1.0)); ub.append(0.0); r+=1

    # Empty pair domain => the two profile types cannot both be selected.
    for i,j in zip(ci,cj):
        rows.extend((r,r)); cols.extend((n+int(i),n+int(j))); vals.extend((1.0,1.0)); ub.append(1.0); r+=1

    Aineq=coo_matrix((vals,(rows,cols)),shape=(r,2*n)).tocsr()
    constraints=[
        LinearConstraint(Aeq,beq,beq),
        LinearConstraint(Aineq,-np.inf*np.ones(r),np.array(ub,dtype=float)),
    ]
    bounds=Bounds(np.zeros(2*n),np.concatenate([cap.astype(float),np.ones(n)]))
    integrality=np.ones(2*n,dtype=np.int8)

    res=milp(np.zeros(2*n),integrality=integrality,bounds=bounds,constraints=constraints,
             options={"time_limit":float(time_limit),"mip_rel_gap":0.0,"presolve":True})

    exact=False
    support=None
    if res.x is not None:
        x=np.rint(res.x[:n]).astype(np.int64)
        selected=x>0
        exact=(
            np.array_equal(P.T@x,budget)
            and all(int(x[cell==c].sum())==int(cell_sizes[c]) for c in range(4))
            and bool(np.all(x>=0) and np.all(x<=cap))
            and not bool(np.any(selected[ci]&selected[cj]))
        )
        if exact:
            support=int(selected.sum())

    if exact:
        status="FEASIBLE_EXACT_WITNESS"
    elif int(res.status)==1:
        status="TIME_LIMIT"
    elif int(res.status)==2:
        status="INFEASIBLE_UNCERTIFIED"
    else:
        status=f"SCIPY_STATUS_{res.status}"

    return {
        "id":payload["id"],"code":payload["code"],"profiles":n,"conflicts":len(ci),
        "status":status,"scipy_status":int(res.status),"message":str(res.message),
        "exact_witness_support":support,"wall_seconds":round(time.time()-t,3),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--case-seconds",type=int,default=300)
    ap.add_argument("--status-seconds",type=int,default=600)
    args=ap.parse_args()

    run=Path(args.run_dir)
    manifest=json.loads((run/"manifest.json").read_text())
    state=json.loads((run/"state.json").read_text())
    require(manifest.get("case_id")=="k66_s1_t225","wrong case")
    require(manifest.get("residual_jobs")==23,"expected 23 residual jobs")
    require(state.get("status")=="INTERRUPTED","expected interrupted monolithic source run")
    require(state.get("certified")==0,"unexpected certified result")
    require(manifest.get("root_sha256")=="b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0",
            "root hash mismatch")

    import numpy as np
    import scipy
    from scipy.optimize import milp as _milp
    raw,e0=make_profiles(np)
    cellspec=[(1,1),(1,0),(0,1),(0,0)]
    Z=np.concatenate([np.column_stack((raw,np.tile(c,(936,1)))) for c in cellspec])
    ell=np.tile(e0,4)
    q=Z[:,12:].sum(axis=1)
    caps=np.where((ell+q)>0,1,2)
    cells=np.repeat(np.arange(4),936)
    coords=list(zip(*np.triu_indices(14)))
    products=np.array([Z[:,i]*Z[:,j] for i,j in coords]).T
    TARGET=12*np.eye(14,dtype=np.int64)+6*np.ones((14,14),dtype=np.int64)
    for r in range(3):
        TARGET[4*r:4*r+4,4*r:4*r+4]-=3
    common=(Z,ell,q,caps,cells,products,coords,TARGET)

    print("K66_CONFLICT_MULTIPLICITY_PREFLIGHT_START",flush=True)
    print(f"numpy={np.__version__} scipy={scipy.__version__}",flush=True)
    print("Necessary model: Gram+cells+profile capacities+empty pair-domain conflicts.",flush=True)
    print("No SAT/LRAT/Cake; INFEASIBLE is numerical preflight only.",flush=True)

    payloads=[]
    for job in manifest["jobs"]:
        p=case_model_payload(np,manifest["case_summary"],job,common)
        payloads.append(p)
        print(f"MODEL {p['id']} profiles={p['profiles']} conflicts={p['conflicts']}",flush=True)

    workers=max(1,min(int(args.workers),6))
    start=time.time()
    last=start
    results=[]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(solve_one,p,args.case_seconds):p["id"] for p in payloads}
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
                print(f"STATUS elapsed={(now-start)/60:.1f}min finished={len(results)}/23 counts={dict(c)} ETA=bounded_by_case_limits",flush=True)
                last=now
            if futs:
                time.sleep(1)

    results.sort(key=lambda x:x["id"])
    from collections import Counter
    counts=Counter(r["status"] for r in results)
    outdir=run/"conflict_multiplicity_preflight_20260909"
    outdir.mkdir(exist_ok=True)
    summary={
        "format":"CONWAY99-K66-CONFLICT-MULTIPLICITY-PREFLIGHT-1",
        "root_sha256":manifest["root_sha256"],
        "source_state_status":state["status"],
        "status_counts":dict(counts),
        "claim_scope":"Necessary profile-frequency feasibility with exact pair incompatibilities. Numerical HiGHS infeasibility is not a proof.",
        "results":results,
    }
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("K66_CONFLICT_MULTIPLICITY_PREFLIGHT_DONE",json.dumps(dict(counts),sort_keys=True),flush=True)
    print("RESULT",outdir/"summary.json",flush=True)

if __name__=="__main__":
    main()
