
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, math, subprocess, time
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path

INT64_SQRT=3037000499

def req(x,m):
    if not x: raise RuntimeError(m)

class CNF:
    def __init__(self): self.n=0; self.cl=[]
    def var(self): self.n+=1; return self.n
    def add(self,*x): self.cl.append(list(x))
    def clause(self,*x):
        if any(v is True for v in x): return
        self.add(*[v for v in x if v is not False])
    def weighted_eq(self,items,target):
        ws={}
        for v,w in items:
            if isinstance(v,bool):
                if v: target-=w
                continue
            if w: ws[v]=ws.get(v,0)+int(w)
        a=sorted(ws.items()); suf=[0]*(len(a)+1)
        for i in range(len(a)-1,-1,-1): suf[i]=suf[i+1]+a[i][1]
        memo={}
        def neg(v): return (not v) if isinstance(v,bool) else -v
        def node(i,r):
            if r<0 or r>suf[i]: return False
            if i==len(a): return r==0
            k=(i,r)
            if k in memo: return memo[k]
            x,w=a[i]; lo=node(i+1,r); hi=node(i+1,r-w)
            if lo is hi: memo[k]=lo; return lo
            v=self.var(); memo[k]=v
            self.clause(-v,-x,hi); self.clause(-v,x,lo)
            self.clause(-x,neg(hi),v); self.clause(x,neg(lo),v)
            return v
        self.clause(node(0,int(target)))

def dimacs(c,p):
    with open(p,"w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl: f.write(" ".join(map(str,cl))+" 0\n")

def profiles(np):
    modes=[]
    for pair in combinations(range(4),2):
        p=[0]*4
        for i in pair: p[i]=1
        modes.append((p,0))
    for i in range(4):
        p=[0]*4; p[i]=2; modes.append((p,1))
    rows=[]; ls=[]
    for z in product(modes,repeat=3):
        e=sum(q[1] for q in z)
        if e<=2:
            rows.append(sum((q[0] for q in z),[])); ls.append(e)
    req(len(rows)==936,"profile count")
    return np.array(rows,dtype=np.int64),np.array(ls,dtype=np.int64)

def invminor(np,K):
    A=[[F(int(v)) for v in r] for r in K]; basis=[]
    for k in range(len(A)):
        if A[k][k]==0: continue
        req(A[k][k]>0,"negative PSD pivot")
        basis.append(k); d=A[k][k]
        for i in range(k+1,len(A)):
            for j in range(i,len(A)):
                A[j][i]=A[i][j]=A[i][j]-A[i][k]*A[k][j]/d
    n=len(basis)
    C=[[F(int(K[i,j])) for j in basis]+[F(int(k==q)) for q in range(n)] for k,i in enumerate(basis)]
    for k in range(n):
        d=C[k][k]; req(d!=0,"singular minor"); C[k]=[v/d for v in C[k]]
        for i in range(n):
            if i==k: continue
            d=C[i][k]; C[i]=[x-d*y for x,y in zip(C[i],C[k])]
    inv=[r[n:] for r in C]; den=math.lcm(*(x.denominator for r in inv for x in r))
    adj=np.array([[int(x*den) for x in r] for r in inv],dtype=np.int64)
    req(np.array_equal(K[np.ix_(basis,basis)]@adj,den*np.eye(n,dtype=np.int64)),"inverse")
    return basis,adj,den

def buildH(np,s,j):
    H=np.zeros((14,14),dtype=np.int64)
    for r in range(3):
        for a,b in ((0,1),(2,3)): H[4*r+a,4*r+b]=H[4*r+b,4*r+a]=1
    for i,(x,y) in enumerate(s["attached_T_bits"]):
        H[i,12]=H[12,i]=x; H[i,13]=H[13,i]=y
    H[12,12]=H[13,13]=2; H[12,13]=H[13,12]=s["s"]
    for (r,t),p in zip(((0,1),(0,2),(1,2)),j["matching_permutations"]):
        for i,k in enumerate(p): H[4*r+i,4*t+k]=H[4*t+k,4*r+i]=1
    return H

def prepare(np,s,j,common):
    Z,ell,q,caps,cells,prods,coords,T=common
    H=buildH(np,s,j); G=T-H@H-H
    budget=np.array([G[i,k] for i,k in coords],dtype=np.int64)
    mask=np.all(prods<=budget,axis=1)
    basis,adj,den=invminor(np,G)
    W=Z[:,basis]@adj; lev=(W*Z[:,basis]).sum(axis=1)
    mask &= np.all(W@G[basis,:]==den*Z,axis=1) & (lev<=den)
    M=-H-np.eye(14,dtype=np.int64); M[:,:4]+=3; MZ=Z@M.T
    beta=(W*MZ[:,basis]).sum(axis=1)
    mask &= (beta>=-3*(den-lev))&(beta<=4*(den-lev))
    mask &= np.array([s["cell_sizes"][c]>0 for c in cells])
    ids=np.flatnonzero(mask); z=Z[ids]; e=ell[ids]; qq=q[ids]; cap=caps[ids].copy(); cell=cells[ids]
    A=z[:,basis]@adj; delta=A@z[:,basis].T; eta=A@MZ[ids][:,basis].T
    req(np.array_equal(eta,eta.T),"eta")
    D=z@z.T; lv=lev[ids]; bt=beta[ids]; n=len(ids); allowed=np.zeros((n,n),dtype=np.uint8)
    for b in (0,1,2):
        ok=D+b<=6
        if b==2: ok &= (e[:,None]<=1)&(e[None,:]<=1)
        l1=b*den-eta-4*delta; r1=4*(den-lv)-bt
        l2=eta-b*den-3*delta; r2=3*(den-lv)+bt
        req(max(int(np.max(np.abs(l1))),int(np.max(np.abs(l2))),int(np.max(np.abs(r1))),int(np.max(np.abs(r2))))<=INT64_SQRT,"int64")
        ok &= l1*l1<=r1[:,None]*r1[None,:]
        ok &= l2*l2<=r2[:,None]*r2[None,:]
        if b==1:
            both=(e[:,None]==0)&(e[None,:]==0)&(qq[:,None]==2)&(qq[None,:]==2)
            ok &= ~(both&((z[:,:12]@z[:,:12].T)==0))
        allowed[ok]|=(1<<b)
    cap[np.diag(allowed)==0]=np.minimum(cap[np.diag(allowed)==0],1)
    return dict(ids=ids,cap=cap,cell=cell,budget=budget,prods=prods[ids],allowed=allowed,cell_sizes=np.array(s["cell_sizes"],dtype=np.int64))

def encode(np,d):
    c=CNF(); n=len(d["ids"]); y=[c.var() for _ in range(n)]; extra=[0]*n
    for i,cap in enumerate(d["cap"]):
        if int(cap)==2:
            extra[i]=c.var(); c.add(-extra[i],y[i])
    def items(coeff):
        a=[]
        for i,w in enumerate(coeff):
            w=int(w)
            if w:
                a.append((y[i],w))
                if extra[i]: a.append((extra[i],w))
        return a
    for k,t in enumerate(d["budget"]): c.weighted_eq(items(d["prods"][:,k]),int(t))
    for cell,t in enumerate(d["cell_sizes"]): c.weighted_eq(items((d["cell"]==cell).astype(np.int64)),int(t))
    ii,jj=np.triu_indices(n,1); bad=d["allowed"][ii,jj]==0
    for i,j in zip(ii[bad],jj[bad]): c.add(-y[int(i)],-y[int(j)])
    return c,{"y":y,"extra":extra,"profiles":n,"conflicts":int(bad.sum())}

def modelvals(p):
    vals={}
    if not p.exists(): return vals
    for tok in p.read_text(errors="replace").split():
        try: v=int(tok)
        except: continue
        if v: vals[abs(v)]=v>0
    return vals

def verify(np,vals,m,d):
    x=np.array([1 if vals.get(v,False) else 0 for v in m["y"]],dtype=np.int64)
    for i,v in enumerate(m["extra"]):
        if v and vals.get(v,False): x[i]+=1
    sel=x>0; ii,jj=np.triu_indices(len(x),1); bad=d["allowed"][ii,jj]==0
    ok=np.array_equal(d["prods"].T@x,d["budget"])
    ok &= all(int(x[d["cell"]==c].sum())==int(d["cell_sizes"][c]) for c in range(4))
    ok &= bool(np.all(x>=0)&np.all(x<=d["cap"]))
    ok &= not bool(np.any(sel[ii[bad]]&sel[jj[bad]]))
    return bool(ok),int(sel.sum())

def solve(job,cnf,cadical,seconds):
    out=cnf.parent; model=out/"model.out"
    with open(out/"solver.out","wb") as o,open(out/"solver.err","wb") as e:
        t=time.time(); rc=subprocess.run([cadical,"--plain","-t",str(int(seconds)),"-w",str(model),str(cnf)],stdout=o,stderr=e).returncode
    return job["id"],rc,time.time()-t,model

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True); ap.add_argument("--workers",type=int,default=8)
    ap.add_argument("--case-seconds",type=int,default=1800); ap.add_argument("--status-seconds",type=int,default=600)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    a=ap.parse_args(); run=Path(a.run_dir); mf=json.loads((run/"manifest.json").read_text()); st=json.loads((run/"state.json").read_text())
    req(mf.get("case_id")=="k66_s1_t225","case"); req(mf.get("residual_jobs")==23,"jobs"); req(st.get("certified")==0,"certified"); req(Path(a.cadical).exists(),"cadical")
    import numpy as np
    raw,e0=profiles(np); cellspec=[(1,1),(1,0),(0,1),(0,0)]
    Z=np.concatenate([np.column_stack((raw,np.tile(c,(936,1)))) for c in cellspec])
    ell=np.tile(e0,4); q=Z[:,12:].sum(axis=1); caps=np.where((ell+q)>0,1,2); cells=np.repeat(np.arange(4),936)
    coords=list(zip(*np.triu_indices(14))); prods=np.array([Z[:,i]*Z[:,j] for i,j in coords]).T
    T=12*np.eye(14,dtype=np.int64)+6*np.ones((14,14),dtype=np.int64)
    for r in range(3): T[4*r:4*r+4,4*r:4*r+4]-=3
    common=(Z,ell,q,caps,cells,prods,coords,T)
    outdir=run/"profile_conflict_cnf_scout_20260909_r2"; outdir.mkdir(exist_ok=True)
    data={}; meta={}; jobs=[]
    print("K66_PROFILE_CONFLICT_CNF_SCOUT_START",flush=True)
    print("Exact CNF of necessary profile-frequency + pair-conflict model. No LRAT/Cake.",flush=True)
    for j in mf["jobs"]:
        d=prepare(np,mf["case_summary"],j,common); c,m=encode(np,d); cd=outdir/j["id"]; cd.mkdir(exist_ok=True); cnf=cd/"model.cnf"; dimacs(c,cnf)
        data[j["id"]]=d; meta[j["id"]]=m; jobs.append((j,cnf))
        print(f"BUILD {j['id']} profiles={m['profiles']} conflicts={m['conflicts']} vars={c.n} clauses={len(c.cl)} size={cnf.stat().st_size/1024**2:.2f}MiB",flush=True)
    workers=max(1,min(a.workers,20)); start=time.time(); last=start; results=[]
    print(f"SCOUT_START cases=23 workers={workers} per_case={a.case_seconds}s",flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(solve,j,cnf,a.cadical,a.case_seconds):j["id"] for j,cnf in jobs}
        while futs:
            done=[f for f in list(futs) if f.done()]
            for f in done:
                cid=futs.pop(f)
                try:
                    cid,rc,wall,model=f.result()
                    if rc==10:
                        ok,supp=verify(np,modelvals(model),meta[cid],data[cid]); status="SAT_EXACT_WITNESS" if ok else "SAT_INVALID_WITNESS"
                    elif rc==20: status="UNSAT_UNCERTIFIED"; supp=None
                    else: status="TIMEOUT_OR_OTHER"; supp=None
                    r={"id":cid,"status":status,"exit":rc,"wall_seconds":round(wall,3),"support":supp}
                except Exception as e: r={"id":cid,"status":"ERROR","error":repr(e)}
                results.append(r); print("SCOUT_RESULT",json.dumps(r,sort_keys=True),flush=True)
            now=time.time()
            if now-last>=a.status_seconds:
                from collections import Counter
                co=Counter(r["status"] for r in results)
                print(f"STATUS elapsed={(now-start)/60:.1f}min finished={len(results)}/23 counts={dict(co)} ETA=bounded_by_case_limit",flush=True); last=now
            if futs: time.sleep(1)
    from collections import Counter
    results.sort(key=lambda r:r["id"]); counts=Counter(r["status"] for r in results)
    (outdir/"summary.json").write_text(json.dumps({"format":"CONWAY99-K66-PROFILE-CONFLICT-CNF-SCOUT-1","counts":dict(counts),"results":results,"claim_scope":"Scout only; UNSAT needs LRAT+Cake."},indent=2,sort_keys=True)+"\n")
    print("K66_PROFILE_CONFLICT_CNF_SCOUT_DONE",json.dumps(dict(counts),sort_keys=True),flush=True)
    print("RESULT",outdir/"summary.json",flush=True)

if __name__=="__main__": main()
