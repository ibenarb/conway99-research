#!/usr/bin/env python3
"""Internal certified quotient model for an order-3 automorphism fixing K3.

The project derivation in docs/breadth1/O3_fixed_triangle_internal_model.md
proves that any such SRG induces the canonical 35-orbit quotient encoded here.
UNSAT is accepted only after lrat-check exit 0 and Cake's explicit
's VERIFIED UNSAT' verdict. SAT is accepted only after an independent full
35x35 quotient reconstruction check.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, time
from pathlib import Path

N=32
ATTACHED=set(range(12))
GROUPS=[tuple(range(0,4)),tuple(range(4,8)),tuple(range(8,12))]
T={12,13}
MARKER=b"s VERIFIED UNSAT"

def sha256_file(p,block=1<<20):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(block),b""):h.update(b)
    return h.hexdigest()

def pairs(xs):
    xs=list(xs)
    for a in range(len(xs)):
        for b in range(a+1,len(xs)):yield xs[a],xs[b]

def edge(i,j):return (i,j) if i<j else (j,i)

class CNF:
    def __init__(self):self.cl=[];self.n=0
    def var(self):self.n+=1;return self.n
    def add(self,*x):self.cl.append(list(x))
    def clause(self,*x):
        if any(a is True for a in x):return
        self.add(*[a for a in x if a is not False])
    def weighted_eq(self,items,r):
        ws={}
        for v,w in items:
            if isinstance(v,bool):
                if v:r-=w
                continue
            ws[v]=ws.get(v,0)+w
        a=sorted(ws.items()); suffix=[0]*(len(a)+1)
        for i in range(len(a)-1,-1,-1):suffix[i]=suffix[i+1]+a[i][1]
        memo={}
        def neg(v):return (not v) if isinstance(v,bool) else -v
        def node(i,rest):
            if rest<0 or rest>suffix[i]:return False
            if i==len(a):return rest==0
            key=(i,rest)
            if key in memo:return memo[key]
            x,w=a[i]; lo=node(i+1,rest); hi=node(i+1,rest-w)
            if lo is hi:memo[key]=lo;return lo
            v=self.var();memo[key]=v
            self.clause(-v,-x,hi); self.clause(-v,x,lo)
            self.clause(-x,neg(hi),v); self.clause(x,neg(lo),v)
            return v
        self.clause(node(0,r))

def and_var(c,a,b):
    z=c.var(); c.add(-z,a); c.add(-z,b); c.add(z,-a,-b); return z

def build():
    c=CNF(); S={edge(i,j):c.var() for i in range(N) for j in range(i+1,N)}; L={edge(i,j):c.var() for i in range(N) for j in range(i+1,N)}
    for e in S:c.add(-S[e],-L[e])
    for i in range(N):
        sedges=[S[edge(i,j)] for j in range(N) if j!=i]; ledges=[L[edge(i,j)] for j in range(N) if j!=i]
        sd=11 if i in ATTACHED else (12 if i in T else 10); ld=1 if i in ATTACHED else (0 if i in T else 2)
        c.weighted_eq([(v,1) for v in sedges],sd); c.weighted_eq([(v,1) for v in ledges],ld)
    for G in GROUPS:
        for v in range(N):
            items=[]
            for u in G:
                if u==v:continue
                items.append((S[edge(u,v)],1)); items.append((L[edge(u,v)],2))
            c.weighted_eq(items,1 if v in ATTACHED else 2)
    # Safe WLOG: each induced attachment-group matching is relabelled canonically.
    for G in GROUPS:
        a,b,d,e=G; chosen={edge(a,b),edge(d,e)}
        for i,j in pairs(G):
            c.add(S[edge(i,j)] if edge(i,j) in chosen else -S[edge(i,j)])
            c.add(-L[edge(i,j)])
    product_count=0
    for i in range(N):
        for j in range(i+1,N):
            items=[]
            for k in range(N):
                if k==i or k==j:continue
                items.append((and_var(c,S[edge(i,k)],S[edge(k,j)]),1)); product_count+=1
                items.append((and_var(c,S[edge(i,k)],L[edge(k,j)]),2)); product_count+=1
                items.append((and_var(c,L[edge(i,k)],S[edge(k,j)]),2)); product_count+=1
                items.append((and_var(c,L[edge(i,k)],L[edge(k,j)]),4)); product_count+=1
            di=2 if i in T else 0; dj=2 if j in T else 0
            items.append((S[edge(i,j)],1+di+dj)); items.append((L[edge(i,j)],2*(1+di+dj)))
            same_group=(i in ATTACHED and j in ATTACHED and i//4==j//4)
            c.weighted_eq(items,3 if same_group else 6)
    meta={"N_three_orbits":N,"fixed_vertices":3,"tau_triangle_orbits":2,"S_vars":len(S),"L_vars":len(L),"and_products":product_count,"variables":c.n,"clauses":len(c.cl)}
    return c,S,L,meta

def write_dimacs(c,path):
    with open(path,"w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:f.write(" ".join(map(str,cl))+" 0\n")

def parse_witness(path):
    vals={}
    for tok in Path(path).read_text(errors="replace").split():
        try:v=int(tok)
        except ValueError:continue
        if v:vals[abs(v)]=(v>0)
    return vals

def full_Q(vals,S,L):
    q=[[0]*35 for _ in range(35)]
    for f in range(3):
        for g in range(3):
            if f!=g:q[f][g]=1
    for f,G in enumerate(GROUPS):
        for u in G:q[f][3+u]=3;q[3+u][f]=1
    for i in range(N):
        q[3+i][3+i]=2 if i in T else 0
        for j in range(i+1,N):
            w=(1 if vals.get(S[edge(i,j)],False) else 0)+2*(1 if vals.get(L[edge(i,j)],False) else 0)
            q[3+i][3+j]=q[3+j][3+i]=w
    return q

def verify_Q(q):
    sizes=[1,1,1]+[3]*32
    if any(sum(row)!=14 for row in q):return False,"row degree"
    for i in range(35):
        for j in range(35):
            if sizes[i]*q[i][j]!=sizes[j]*q[j][i]:return False,"orbit balance"
    for i in range(35):
        for j in range(35):
            lhs=sum(q[i][k]*q[k][j] for k in range(35))+q[i][j]
            rhs=(12 if i==j else 0)+2*sizes[j]
            if lhs!=rhs:return False,f"quotient equation {i},{j}: {lhs}!={rhs}"
    return True,"PASS"

def run_cmd(cmd,out,err):
    with open(out,"wb") as o,open(err,"wb") as e:return subprocess.run(cmd,stdout=o,stderr=e).returncode

def mem_available_gib():
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            if line.startswith('MemAvailable:'):return int(line.split()[1])/1024**2
    except Exception:pass
    return None

def solve(cnf,S,L,args):
    run=Path(args.run_dir); run.mkdir(parents=True,exist_ok=True)
    wit=run/"witness.out"; proof=run/"proof.lrat"; so=run/"solver.out"; se=run/"solver.err"
    cmd=[args.cadical,"--lrat","--no-binary","-w",str(wit),str(cnf),str(proof)]
    print("SOLVE_START", " ".join(cmd),flush=True); start=time.time(); last=start
    with open(so,"wb") as o,open(se,"wb") as e:
        proc=subprocess.Popen(cmd,stdout=o,stderr=e)
        while proc.poll() is None:
            time.sleep(5); now=time.time()
            if now-last>=args.status_seconds:
                pb=proof.stat().st_size if proof.exists() else 0; du=shutil.disk_usage(run)
                print(f"STATUS phase=SOLVE elapsed={(now-start)/3600:.2f}h proof={pb/1024**3:.2f}GiB disk_free={du.free/1024**3:.1f}GiB ETA=unknown",flush=True); last=now
                if du.free<75*1024**3:
                    proc.terminate(); raise RuntimeError("disk safety floor 75 GiB reached")
        rc=proc.wait()
    rec={"solver_exit":rc,"solver_wall":time.time()-start,"cnf_sha256":sha256_file(cnf)}
    if rc==10:
        vals=parse_witness(wit); q=full_Q(vals,S,L); ok,msg=verify_Q(q)
        rec.update({"status":"SAT_QUOTIENT_VERIFIED" if ok else "SAT_WITNESS_INVALID","verify":msg})
        if ok:(run/"quotient_Q.json").write_text(json.dumps(q,indent=2)+"\n")
        return rec
    if rc!=20:rec["status"]="SOLVER_ERROR"; return rec
    rec["proof_bytes"]=proof.stat().st_size; rec["proof_sha256"]=sha256_file(proof)
    lo,le=run/"lrat.out",run/"lrat.err"; t=time.time(); lrc=run_cmd([args.lrat_check,str(cnf),str(proof)],lo,le)
    rec.update({"lrat_exit":lrc,"lrat_wall":time.time()-t})
    if lrc!=0:rec["status"]="LRAT_FAILED"; return rec
    proof_gib=proof.stat().st_size/1024**3; cake_est=3.0+0.9*proof_gib; avail=mem_available_gib()
    rec.update({"cake_estimated_rss_gib":cake_est,"mem_available_before_cake_gib":avail})
    if cake_est>40 or (avail is not None and cake_est>avail-4):
        rec["status"]="LRAT_CERTIFIED_CAKE_DEFERRED_RESOURCE"; return rec
    co,ce=run/"cake.out",run/"cake.err"; t=time.time(); crc=run_cmd([args.cake,str(cnf),str(proof)],co,ce)
    marker=MARKER in co.read_bytes(); rec.update({"cake_exit":crc,"cake_wall":time.time()-t,"cake_positive_marker":marker})
    rec["status"]="UNSAT_CERTIFIED" if crc==0 and marker else "CAKE_FAILED"; return rec

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); ap.add_argument("--run",action="store_true"); ap.add_argument("--run-dir",default=None)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical")); ap.add_argument("--lrat-check",default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake",default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr")); ap.add_argument("--status-seconds",type=int,default=600)
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    print("BUILD fixed-K3 exact quotient CNF ...",flush=True); c,S,L,meta=build(); cnf=out/"fixed_triangle_o3_quotient.cnf"; write_dimacs(c,cnf)
    meta.update({"cnf":str(cnf),"cnf_sha256":sha256_file(cnf)}); (out/"model_meta.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("BUILD_OK",json.dumps(meta,sort_keys=True),flush=True)
    if args.run:
        if not args.run_dir:args.run_dir=str(out/"run")
        for tool in (args.cadical,args.lrat_check,args.cake):
            if not Path(tool).exists():raise SystemExit(f"missing tool: {tool}")
        rec=solve(cnf,S,L,args); (out/"result.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n"); print("RESULT",json.dumps(rec,sort_keys=True),flush=True)

if __name__=="__main__":main()
