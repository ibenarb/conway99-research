#!/usr/bin/env python3
"""Exact T-skeleton classification and certifiable 27-column Gram model.

Stages:
  156 unlabeled simple graphs B on six vertices
   -> 69 with M=6J+6I-5B-B^2 entrywise nonnegative
   -> 44 with M positive semidefinite (exact principal-minor test)
   -> SAT/UNSAT classification of the exact binary Gram model CC^T=M,
      C in {0,1}^{6x27}, using CNF + CaDiCaL/LRAT/Cake.

The 44->? stage does not trust MILP or floating point. SAT cases are checked by
an independent integer witness verifier; UNSAT cases require LRAT and the
explicit positive Cake verdict marker.
"""
from __future__ import annotations
import argparse, collections, concurrent.futures as cf, hashlib, itertools, json, subprocess, threading, time
from pathlib import Path

N=6
EDGES=[(i,j) for i in range(N) for j in range(i+1,N)]
EIDX={e:k for k,e in enumerate(EDGES)}
MARKER=b"s VERIFIED UNSAT"

def sha256_file(p,block=1<<20):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(block),b""):h.update(b)
    return h.hexdigest()

def permutation_maps():
    out=[]
    for p in itertools.permutations(range(N)):
        mp=[]
        for i,j in EDGES:
            a,b=sorted((p[i],p[j])); mp.append(EIDX[(a,b)])
        out.append(mp)
    return out

def all_canonical_reps():
    size=1<<len(EDGES)
    canon=list(range(size))
    for mp in permutation_maps():
        tr=[0]*size
        for mask in range(1,size):
            lb=mask & -mask; bit=lb.bit_length()-1
            tr[mask]=tr[mask^lb] | (1<<mp[bit])
        for mask in range(size):
            if tr[mask]<canon[mask]:canon[mask]=tr[mask]
    reps=sorted(set(canon))
    assert len(reps)==156
    return reps

def matrix_B(mask):
    B=[[0]*N for _ in range(N)]
    for k,(i,j) in enumerate(EDGES):
        if (mask>>k)&1:B[i][j]=B[j][i]=1
    return B

def matmul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def matrix_M(B):
    B2=matmul(B,B)
    return [[6+(6 if i==j else 0)-5*B[i][j]-B2[i][j] for j in range(N)] for i in range(N)]

def det_bareiss(A):
    A=[row[:] for row in A]; n=len(A)
    if n==0:return 1
    sign=1; prev=1
    for k in range(n-1):
        if A[k][k]==0:
            sw=next((r for r in range(k+1,n) if A[r][k]),None)
            if sw is None:return 0
            A[k],A[sw]=A[sw],A[k]; sign=-sign
        piv=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*piv-A[i][k]*A[k][j])//prev
        prev=piv
        for i in range(k+1,n):A[i][k]=0
    return sign*A[n-1][n-1]

def psd_exact(M):
    for r in range(1,N+1):
        for I in itertools.combinations(range(N),r):
            sub=[[M[i][j] for j in I] for i in I]
            if det_bareiss(sub)<0:return False
    return True

class CNF:
    def __init__(self):self.n=0;self.cl=[]
    def var(self):self.n+=1;return self.n
    def add(self,*xs):self.cl.append(list(xs))
    def atmost(self,lits,k):
        n=len(lits)
        if k<0:self.add();return
        if k>=n:return
        if k==0:
            for a in lits:self.add(-a)
            return
        s=[[self.var() for _ in range(k)] for _ in range(n-1)]
        self.add(-lits[0],s[0][0])
        for j in range(1,k):self.add(-s[0][j])
        for i in range(1,n-1):
            self.add(-lits[i],s[i][0]); self.add(-s[i-1][0],s[i][0])
            for j in range(1,k):
                self.add(-lits[i],-s[i-1][j-1],s[i][j])
                self.add(-s[i-1][j],s[i][j])
            self.add(-lits[i],-s[i-1][k-1])
        self.add(-lits[-1],-s[-1][k-1])
    def exactly(self,lits,k):
        self.atmost(lits,k); self.atmost([-a for a in lits],len(lits)-k)

def pattern_forbid_clause(rowvars,pattern):
    return [(-v if ((pattern>>t)&1) else v) for t,v in enumerate(rowvars)]

def build_gram_cnf(M):
    c=CNF(); x=[[c.var() for _ in range(N)] for _ in range(27)]; y={}
    for u in range(27):
        for i in range(N):
            for j in range(i+1,N):
                z=c.var(); y[(u,i,j)]=z
                c.add(-z,x[u][i]); c.add(-z,x[u][j]); c.add(z,-x[u][i],-x[u][j])
    for i in range(N):c.exactly([x[u][i] for u in range(27)],M[i][i])
    for i in range(N):
        for j in range(i+1,N):c.exactly([y[(u,i,j)] for u in range(27)],M[i][j])
    # WLOG sort the 27 six-bit columns. The equations depend only on their multiset.
    for u in range(26):
        for a in range(64):
            ca=pattern_forbid_clause(x[u],a)
            for b in range(a):c.add(*(ca+pattern_forbid_clause(x[u+1],b)))
    return c,x

def write_dimacs(c,path):
    with open(path,"w") as f:
        f.write(f"p cnf {c.n} {len(c.cl)}\n")
        for cl in c.cl:f.write(" ".join(map(str,cl))+" 0\n")

def classify_prepare(outdir):
    outdir=Path(outdir); cnfdir=outdir/"cnf"; cnfdir.mkdir(parents=True,exist_ok=True)
    reps=all_canonical_reps(); rows=[]; n69=n44=0
    for mask in reps:
        B=matrix_B(mask); M=matrix_M(B)
        nonneg=all(x>=0 for row in M for x in row); psd=False
        if nonneg:
            n69+=1; psd=psd_exact(M)
            if psd:n44+=1
        rec={"mask":mask,"mask_hex":f"{mask:04x}","edges":sum(map(sum,B))//2,"B":B,"M":M,
             "entrywise_nonnegative":nonneg,"psd_exact":psd}
        if psd:
            c,x=build_gram_cnf(M); cp=cnfdir/f"B_{mask:04x}.cnf"; write_dimacs(c,cp)
            rec.update({"cnf":str(cp),"cnf_sha256":sha256_file(cp),"variables":c.n,"clauses":len(c.cl),"x_vars":x})
        rows.append(rec)
    assert len(rows)==156 and n69==69 and n44==44
    idx={"format":"CONWAY99-O3-T-SKELETON-INDEX-1","counts":{"unlabeled":156,"nonnegative":n69,"psd_exact":n44},"cases":rows}
    (outdir/"index.json").write_text(json.dumps(idx,indent=2,sort_keys=True)+"\n")
    return idx

def parse_witness(path):
    vals={}
    for tok in Path(path).read_text(errors="replace").split():
        try:v=int(tok)
        except ValueError:continue
        if v:vals[abs(v)]=(v>0)
    return vals

def verify_sat(case,witness):
    vals=parse_witness(witness); x=case["x_vars"]; M=case["M"]; rows=[]
    for u in range(27):
        row=[]
        for i in range(N):
            v=x[u][i]
            if v not in vals:raise ValueError(f"missing primary witness var {v}")
            row.append(1 if vals[v] else 0)
        rows.append(row)
    pats=[sum(row[t]<<t for t in range(N)) for row in rows]
    if pats!=sorted(pats):raise ValueError("lex order violated")
    for i in range(N):
        if sum(rows[u][i] for u in range(27))!=M[i][i]:raise ValueError("diagonal moment mismatch")
    for i in range(N):
        for j in range(i+1,N):
            if sum(rows[u][i]*rows[u][j] for u in range(27))!=M[i][j]:raise ValueError("pair moment mismatch")
    return {"patterns":pats,"pattern_counts":{str(p):pats.count(p) for p in sorted(set(pats))}}

def run_cmd(cmd,stdout,stderr):
    with open(stdout,"wb") as o,open(stderr,"wb") as e:return subprocess.run(cmd,stdout=o,stderr=e).returncode

def solve_case(case,rundir,cadical,lrat,cake):
    mask=case["mask"]; job=Path(rundir)/f"B_{mask:04x}"; job.mkdir(parents=True,exist_ok=True)
    cnf=Path(case["cnf"]); wit=job/"witness.out"; proof=job/"proof.lrat"; sout=job/"solver.out"; serr=job/"solver.err"
    t=time.time(); rc=run_cmd([cadical,"--lrat","--no-binary","-w",str(wit),str(cnf),str(proof)],sout,serr)
    rec={"mask":mask,"mask_hex":f"{mask:04x}","solver_exit":rc,"solver_wall":time.time()-t,"cnf_sha256":sha256_file(cnf)}
    if rc==10:
        rec["status"]="SAT_WITNESS_VERIFIED"; rec["witness"]=verify_sat(case,wit); return rec
    if rc!=20:rec["status"]="SOLVER_ERROR"; return rec
    rec["proof_sha256"]=sha256_file(proof); rec["proof_bytes"]=proof.stat().st_size
    lo,le=job/"lrat.out",job/"lrat.err"; t=time.time(); lrc=run_cmd([lrat,str(cnf),str(proof)],lo,le)
    rec.update({"lrat_exit":lrc,"lrat_wall":time.time()-t})
    if lrc!=0:rec["status"]="LRAT_FAILED"; return rec
    co,ce=job/"cake.out",job/"cake.err"; t=time.time(); crc=run_cmd([cake,str(cnf),str(proof)],co,ce)
    marker=MARKER in co.read_bytes(); rec.update({"cake_exit":crc,"cake_wall":time.time()-t,"cake_positive_marker":marker})
    rec["status"]="UNSAT_CERTIFIED" if crc==0 and marker else "CAKE_FAILED"
    return rec

def solve_all(index,outdir,rundir,workers,cadical,lrat,cake,status_seconds):
    cases=[x for x in index["cases"] if x.get("psd_exact")]; result_path=Path(outdir)/"classification.json"; results={}
    if result_path.exists():
        old=json.loads(result_path.read_text())
        results={r["mask_hex"]:r for r in old.get("results",[]) if r.get("status") in ("SAT_WITNESS_VERIFIED","UNSAT_CERTIFIED")}
    start=time.time(); last=start; todo=[c for c in cases if c["mask_hex"] not in results]
    def save():
        obj={"format":"CONWAY99-O3-T-SKELETON-CLASSIFICATION-1","results":sorted(results.values(),key=lambda r:r["mask"])}
        obj["counts"]=dict(collections.Counter(r["status"] for r in results.values()))
        result_path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print(f"RUN cases={len(cases)} already={len(results)} todo={len(todo)} workers={workers}",flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(solve_case,c,rundir,cadical,lrat,cake):c for c in todo}
        while futs:
            done,_=cf.wait(futs,timeout=1,return_when=cf.FIRST_COMPLETED)
            for f in done:
                c=futs.pop(f); r=f.result(); results[c["mask_hex"]]=r; save()
                print(f"DONE B_{c['mask_hex']} {r['status']} wall={r.get('solver_wall',0):.2f}s",flush=True)
            now=time.time()
            if now-last>=status_seconds:
                cnt=collections.Counter(r["status"] for r in results.values())
                print(f"STATUS elapsed={(now-start)/60:.1f}m finished={len(results)}/{len(cases)} pending={len(futs)} counts={dict(cnt)} ETA=unknown",flush=True); last=now
    save(); cnt=collections.Counter(r["status"] for r in results.values())
    complete=len(results)==44 and set(cnt)<= {"SAT_WITNESS_VERIFIED","UNSAT_CERTIFIED"}
    summary={"counts":dict(cnt),"complete":complete,"total":len(results),"expected_input_cases":44}
    (Path(outdir)/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("SUMMARY",json.dumps(summary,sort_keys=True),flush=True); return summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); ap.add_argument("--run",action="store_true"); ap.add_argument("--run-dir",default=None)
    ap.add_argument("--workers",type=int,default=6); ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--lrat-check",default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake",default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr"))
    ap.add_argument("--status-seconds",type=int,default=600); args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    print("PREPARE exact unlabeled/PSD/CNF classification ...",flush=True); idx=classify_prepare(out); print("PREPARE_OK",idx["counts"],flush=True)
    if args.run:
        rundir=Path(args.run_dir or (out/"run")); rundir.mkdir(parents=True,exist_ok=True)
        for tool in (args.cadical,args.lrat_check,args.cake):
            if not Path(tool).exists():raise SystemExit(f"missing tool: {tool}")
        solve_all(idx,out,rundir,args.workers,args.cadical,args.lrat_check,args.cake,args.status_seconds)

if __name__=="__main__":main()
