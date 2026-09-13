
from __future__ import annotations
import argparse, json, math, time
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
            rows.append(sum((q[0] for q in z),[])); ls.append(ell)
    require(len(rows)==936,"profile universe mismatch")
    return np.array(rows,dtype=np.int64),np.array(ls,dtype=np.int64)

def inverse_minor(np,K):
    A=[[F(int(v)) for v in row] for row in K]; basis=[]
    for k in range(len(A)):
        if A[k][k]==0: continue
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
            if i==k: continue
            d=C[i][k]; C[i]=[x-d*y for x,y in zip(C[i],C[k])]
    inv=[r[n:] for r in C]
    den=math.lcm(*(x.denominator for r in inv for x in r))
    adj=np.array([[int(x*den) for x in r] for r in inv],dtype=np.int64)
    require(np.array_equal(K[np.ix_(basis,basis)]@adj,den*np.eye(n,dtype=np.int64)),
            "inverse check failed")
    return basis,adj,den

def build_H(np,summary,job):
    H=np.zeros((14,14),dtype=np.int64)
    for r in range(3):
        for i,j in ((0,1),(2,3)):
            H[4*r+i,4*r+j]=H[4*r+j,4*r+i]=1
    for i,(x,y) in enumerate(summary["attached_T_bits"]):
        H[i,12]=H[12,i]=x; H[i,13]=H[13,i]=y
    H[12,12]=H[13,13]=2; H[12,13]=H[13,12]=summary["s"]
    for (r,t),p in zip(((0,1),(0,2),(1,2)),job["matching_permutations"]):
        for i,j in enumerate(p):
            H[4*r+i,4*t+j]=H[4*t+j,4*r+i]=1
    return H

def filtered_profiles(np,summary,job,Z,ell,q,caps,cells,products,coords,TARGET):
    H=build_H(np,summary,job); G=TARGET-H@H-H
    budget=np.array([G[i,j] for i,j in coords],dtype=np.int64)
    mask=np.all(products<=budget,axis=1)
    basis,adj,den=inverse_minor(np,G)
    W=Z[:,basis]@adj
    kernel=np.all(W@G[basis,:]==den*Z,axis=1)
    lev=(W*Z[:,basis]).sum(axis=1)
    mask &= kernel & (lev<=den)
    M=-H-np.eye(14,dtype=np.int64); M[:,:4]+=3
    MZ=Z@M.T
    beta=(W*MZ[:,basis]).sum(axis=1)
    mask &= (beta>=-3*(den-lev))&(beta<=4*(den-lev))
    mask &= np.array([summary["cell_sizes"][c]>0 for c in cells])
    ids=np.flatnonzero(mask)
    return H,G,M,MZ,basis,adj,den,lev[ids],beta[ids],ids

def pair_domains(np,summary,job,common):
    Z,ell,q,caps,cells,products,coords,TARGET=common
    H,G,M,MZ,basis,adj,den,lev,beta,ids=filtered_profiles(
        np,summary,job,Z,ell,q,caps,cells,products,coords,TARGET)
    z=Z[ids]; e=ell[ids]; qq=q[ids]; cap=caps[ids]; cell=cells[ids]
    zb=z[:,basis]; A=zb@adj
    delta=A@zb.T
    eta=A@(MZ[ids][:,basis].T)
    require(np.array_equal(eta,eta.T),"eta symmetry failed")
    D=z@z.T
    n=len(ids); allowed=np.zeros((n,n),dtype=np.uint8)

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

    tri=np.triu_indices(n,1); dom=allowed[tri]
    total=len(dom); empty=int((dom==0).sum())
    forced={str(b):int((dom==(1<<b)).sum()) for b in (0,1,2)}

    active=np.ones(n,dtype=bool); rounds=[]
    while True:
        drop=[]
        active_ids=np.flatnonzero(active)
        for i in active_ids:
            s_mask=(allowed[i,active_ids]&2)!=0
            l_mask=(allowed[i,active_ids]&4)!=0
            s_cap=int(cap[active_ids][s_mask].sum())
            l_cap=int(cap[active_ids][l_mask].sum())
            if allowed[i,i]&2: s_cap-=1
            if allowed[i,i]&4: l_cap-=1
            dS=int(4+2*e[i]-qq[i]); dL=int(2-e[i])
            if s_cap<dS or l_cap<dL:
                drop.append(i)
        if not drop: break
        active[drop]=False; rounds.append(len(drop))

    cell_counts=[int((cell[active]==c).sum()) for c in range(4)]
    cell_capacity=[int(cap[active][cell[active]==c].sum()) for c in range(4)]
    h_survives=all(cell_capacity[c]>=summary["cell_sizes"][c] for c in range(4))
    return {
        "id":job["id"],"code":job["code"],"rank":len(basis),"denominator":den,
        "profiles_after_B_diagonal":n,
        "unordered_profile_pairs":total,
        "empty_pair_domains":empty,
        "empty_pair_fraction":empty/total if total else 0,
        "forced_pair_colors":forced,
        "multi_or_zero_color_pairs":total-sum(forced.values()),
        "support_pruning_rounds":rounds,
        "profiles_after_support_pruning":int(active.sum()),
        "cell_profile_counts_after_support":cell_counts,
        "cell_capacity_after_support":cell_capacity,
        "H_survives_pair_support":bool(h_survives),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    args=ap.parse_args()
    run=Path(args.run_dir)
    manifest=json.loads((run/"manifest.json").read_text())
    state=json.loads((run/"state.json").read_text())
    require(manifest.get("case_id")=="k66_s1_t225","wrong case")
    require(manifest.get("residual_jobs")==23,"expected 23 residual jobs")
    require(state.get("status")=="INTERRUPTED","expected interrupted source run")
    require(state.get("certified")==0,"unexpected certified result")
    require(manifest.get("root_sha256")=="b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0",
            "root hash mismatch")

    import numpy as np
    raw,e0=make_profiles(np)
    cellspec=[(1,1),(1,0),(0,1),(0,0)]
    Z=np.concatenate([np.column_stack((raw,np.tile(c,(936,1)))) for c in cellspec])
    ell=np.tile(e0,4); q=Z[:,12:].sum(axis=1)
    caps=np.where((ell+q)>0,1,2)
    cells=np.repeat(np.arange(4),936)
    coords=list(zip(*np.triu_indices(14)))
    products=np.array([Z[:,i]*Z[:,j] for i,j in coords]).T
    TARGET=12*np.eye(14,dtype=np.int64)+6*np.ones((14,14),dtype=np.int64)
    for r in range(3): TARGET[4*r:4*r+4,4*r:4*r+4]-=3
    common=(Z,ell,q,caps,cells,products,coords,TARGET)

    print("K66_PAIR_PROJECTOR_PREFLIGHT_START",flush=True)
    print("Exact integer evaluation of Astra inequalities (19)-(20); no SAT/LRAT/Cake.",flush=True)
    start=time.time(); results=[]
    for job in manifest["jobs"]:
        r=pair_domains(np,manifest["case_summary"],job,common)
        results.append(r)
        print("PAIR_RESULT",json.dumps(r,sort_keys=True),flush=True)

    outdir=run/"pair_projector_preflight_20260909"; outdir.mkdir(exist_ok=True)
    summary={
        "format":"CONWAY99-K66-PAIR-PROJECTOR-PREFLIGHT-1",
        "source_case":"k66_s1_t225",
        "source_root_sha256":manifest["root_sha256"],
        "H_total":23,
        "H_survivors":sum(r["H_survives_pair_support"] for r in results),
        "profile_candidates_before_pair_support":sum(r["profiles_after_B_diagonal"] for r in results),
        "profile_candidates_after_pair_support":sum(r["profiles_after_support_pruning"] for r in results),
        "empty_pair_domains_total":sum(r["empty_pair_domains"] for r in results),
        "unordered_profile_pairs_total":sum(r["unordered_profile_pairs"] for r in results),
        "wall_seconds":time.time()-start,
        "claim_scope":"Necessary exact pair/projector and support-capacity filters only; not a B realization.",
        "results":results,
    }
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("K66_PAIR_PROJECTOR_PREFLIGHT_DONE",json.dumps({
        "H_survivors":summary["H_survivors"],
        "profiles":f'{summary["profile_candidates_before_pair_support"]}->{summary["profile_candidates_after_pair_support"]}',
        "empty_pair_domains":summary["empty_pair_domains_total"],
        "pairs":summary["unordered_profile_pairs_total"],
        "wall_seconds":round(summary["wall_seconds"],2),
    },sort_keys=True),flush=True)
    print("RESULT",outdir/"summary.json",flush=True)

if __name__=="__main__":
    main()
