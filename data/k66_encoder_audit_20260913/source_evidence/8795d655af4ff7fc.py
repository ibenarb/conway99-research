from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, os, shutil, signal, subprocess, time, zipfile
from collections import Counter
from pathlib import Path

ROOT_IDS = ["v4_09316","v4_09317","v4_09322","v4_09323","v4_09331","v4_09332","v4_09333"]
ROOT_HASHES = {
    "v4_09316":"c7a44b5aad06611f55c2306bc5ddd2f8e93052d4ac3c8d515dd9118b61f84d19",
    "v4_09317":"b191ca979d0d2b3bec5053c877a973d61349b479fbdac35a470d9bfacf9bce5b",
    "v4_09322":"a8f3b3770f58f7d32d9e198d7d6847561ffaec351c497edc96ca996b1865ef7f",
    "v4_09323":"f771ee35ef44160f58125f88ed7809684ffae291e0d2889b68cd9be07b09221d",
    "v4_09331":"be9ee79a549b8af6fff52723f25a97891eb8942050de11238041a8ca86ad7b82",
    "v4_09332":"06bb87a23f10c01abc42d709d1e79db1954588df0509eb292836bf4c09a5bee1",
    "v4_09333":"8b2f5eeb923bc736d6af9d0ea96a9ed09251bdb3a433e3cbb33f3fb80446b7d9",
}
PRIMARY_COUNTS = {"v4_09316":634,"v4_09317":642,"v4_09322":654,"v4_09323":708,"v4_09331":608,"v4_09332":724,"v4_09333":741}
CADICAL_SHA="d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
LRAT_SHA="49f0bf5b418fec38dad3a199a9ae7eb52a4617269a6d360d49d3f580a9b98dfa"
CAKE_SHA="e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a"
LRAT_MARKER="c VERIFIED"
CAKE_MARKER=b"s VERIFIED UNSAT"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(p,obj):
    t=p.with_suffix(p.suffix+".tmp")
    t.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    os.replace(t,p)

def resources(p):
    du=shutil.disk_usage(p)
    mem=-1.0
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            mem=int(line.split()[1])/1024**2
            break
    return du.free/1024**3,mem

def parse_header(p):
    with open(p) as f:
        for line in f:
            if line.startswith("p cnf "):
                _,_,v,c=line.split(); return int(v),int(c)
    raise RuntimeError("missing DIMACS header")

def split_rank(p,nprimary):
    cnt=[0]*(nprimary+1)
    with open(p) as f:
        for line in f:
            if not line or line[0] in "cp": continue
            for tok in line.split():
                v=abs(int(tok))
                if 1<=v<=nprimary: cnt[v]+=1
    return sorted(range(1,nprimary+1), key=lambda v:(-cnt[v],v))

def write_leaf(root,lits,out):
    nv,nc=parse_header(root)
    out.parent.mkdir(parents=True,exist_ok=True)
    replaced=False
    with open(root,"rb") as src, open(out,"wb") as dst:
        for raw in src:
            if not replaced and raw.startswith(b"p cnf "):
                dst.write(f"p cnf {nv} {nc+len(lits)}\n".encode()); replaced=True
            else:
                dst.write(raw)
        if not replaced: raise RuntimeError("header replacement failed")
        for lit in lits: dst.write(f"{lit} 0\n".encode())

def plain_scout(root,lits,work,cadical,seconds):
    work=Path(work); work.mkdir(parents=True,exist_ok=True)
    cnf=work/"scout.cnf"; write_leaf(Path(root),lits,cnf)
    t=time.time()
    with open(work/"scout.out","wb") as o, open(work/"scout.err","wb") as e:
        try:
            r=subprocess.run([cadical,"--plain",str(cnf)],stdout=o,stderr=e,timeout=seconds)
            rc=r.returncode
        except subprocess.TimeoutExpired:
            rc=124
    return {"exit":rc,"wall":time.time()-t}

def proof_attempt(root,lits,work,cadical,seconds,cap_gib):
    work=Path(work); work.mkdir(parents=True,exist_ok=True)
    cnf=work/"leaf.cnf"; proof=work/"proof.lrat"; wit=work/"witness.out"
    write_leaf(Path(root),lits,cnf)
    for p in (proof,wit):
        if p.exists(): p.unlink()
    t=time.time(); reason=None
    with open(work/"cadical.out","wb") as o, open(work/"cadical.err","wb") as e:
        p=subprocess.Popen([cadical,"--lrat","--no-binary","-w",str(wit),str(cnf),str(proof)],stdout=o,stderr=e)
        while p.poll() is None:
            time.sleep(2)
            wall=time.time()-t
            size=proof.stat().st_size if proof.exists() else 0
            if seconds and wall>=seconds:
                reason="TIME_SPLIT"; p.terminate(); break
            if cap_gib and size>=cap_gib*1024**3:
                reason="PROOF_SPLIT"; p.terminate(); break
        if reason:
            try: p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                p.kill(); p.wait()
        rc=p.returncode
    size=proof.stat().st_size if proof.exists() else 0
    return {"exit":rc,"wall":time.time()-t,"stop_reason":reason,"proof_bytes":size,
            "cnf_sha256":sha(cnf),"proof_sha256":sha(proof) if size else None}

def check_proof(work,lrat,cake):
    work=Path(work); cnf=work/"leaf.cnf"; proof=work/"proof.lrat"
    with open(work/"lrat.out","wb") as o, open(work/"lrat.err","wb") as e:
        lrc=subprocess.run([lrat,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    lmark=LRAT_MARKER in (work/"lrat.out").read_text(errors="replace")
    if lrc!=0 or not lmark:
        return {"status":"LRAT_FAILED","lrat_exit":lrc,"lrat_marker":lmark}
    with open(work/"cake.out","wb") as o, open(work/"cake.err","wb") as e:
        crc=subprocess.run([cake,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    cmark=CAKE_MARKER in (work/"cake.out").read_bytes()
    return {"status":"CERTIFIED" if crc==0 and cmark else "CAKE_FAILED",
            "lrat_exit":lrc,"lrat_marker":lmark,"cake_exit":crc,"cake_marker":cmark}

def coverage(cubes,root):
    children={}
    for c in cubes.values():
        if c.get("parent"): children.setdefault(c["parent"],[]).append(c["id"])
    stack=[root]; seen=set()
    while stack:
        cid=stack.pop()
        if cid in seen: raise RuntimeError("cycle")
        seen.add(cid); c=cubes[cid]
        if c["status"]=="SPLIT":
            ks=children.get(cid,[])
            if len(ks)!=2: raise RuntimeError(f"incomplete split {cid}")
            v=c["split_var"]
            exp={tuple(c["lits"]+[-v]),tuple(c["lits"]+[v])}
            got={tuple(cubes[k]["lits"]) for k in ks}
            if got!=exp: raise RuntimeError(f"bad children {cid}")
            stack.extend(ks)
        elif c["status"]!="CERTIFIED":
            raise RuntimeError(f"uncovered leaf {cid}: {c['status']}")
    return len(seen)

def handoff(run,st):
    stamp=time.strftime("%Y%m%d_%H%M%S")
    zpath=run/f"k66_deep7_adaptive_cert_handoff_{stamp}.zip"
    with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(run/"state.json","state.json"); z.write(run/"manifest.json","manifest.json"); z.write(run/"summary.json","summary.json")
        for c in st["cubes"].values():
            if c["status"]=="CERTIFIED":
                w=Path(c["work"]); pref=c["id"]
                for n in ("cadical.out","cadical.err","lrat.out","lrat.err","cake.out","cake.err"):
                    p=w/n
                    if p.exists(): z.write(p,f"{pref}/{n}")
    win=Path("/mnt/c/Users/rb/Downloads")/zpath.name
    try: shutil.copy2(zpath,win)
    except Exception: win=None
    return zpath,win

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-run",required=True)
    ap.add_argument("--run-dir",default=None)
    ap.add_argument("--scout-workers",type=int,default=20)
    ap.add_argument("--cert-workers",type=int,default=12)
    ap.add_argument("--scout-seconds",type=float,default=180)
    ap.add_argument("--cert-seconds",type=float,default=900)
    ap.add_argument("--proof-cap-gib",type=float,default=3.0)
    ap.add_argument("--status-seconds",type=float,default=600)
    ap.add_argument("--disk-floor-gib",type=float,default=75)
    ap.add_argument("--mem-floor-gib",type=float,default=4)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--lrat-check",default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake",default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr"))
    a=ap.parse_args()
    source=Path(a.source_run); gdir=source/"neighbor_star_deep7_autonomous_20260909"/"global"
    run=Path(a.run_dir) if a.run_dir else source.parent/f"k66_deep7_adaptive_cert_{time.strftime('%Y%m%d_%H%M%S')}"
    run.mkdir(parents=True,exist_ok=True); jobs=run/"jobs"; jobs.mkdir(exist_ok=True)
    for p,h,n in ((Path(a.cadical),CADICAL_SHA,"cadical"),(Path(a.lrat_check),LRAT_SHA,"lrat"),(Path(a.cake),CAKE_SHA,"cake")):
        if not p.exists(): raise SystemExit(f"missing {n}: {p}")
        if sha(p)!=h: raise SystemExit(f"{n} hash mismatch")
    roots={}; ranks={}
    for rid in ROOT_IDS:
        p=gdir/rid/"model.cnf"
        if not p.exists(): raise SystemExit(f"missing root {p}")
        if sha(p)!=ROOT_HASHES[rid]: raise SystemExit(f"root hash mismatch {rid}")
        roots[rid]=str(p); ranks[rid]=split_rank(p,PRIMARY_COUNTS[rid])
    manifest={"format":"CONWAY99-K66-DEEP7-ADAPTIVE-CERT-1","roots":roots,"root_hashes":ROOT_HASHES,"primary_counts":PRIMARY_COUNTS,
              "tool_hashes":{"cadical":CADICAL_SHA,"lrat":LRAT_SHA,"cake":CAKE_SHA},
              "policy":{"scout_seconds":a.scout_seconds,"cert_seconds":a.cert_seconds,"proof_cap_gib":a.proof_cap_gib,
                        "scout_workers":a.scout_workers,"cert_workers":a.cert_workers,"disk_floor_gib":a.disk_floor_gib,"mem_floor_gib":a.mem_floor_gib}}
    mp=run/"manifest.json"
    if mp.exists():
        if json.loads(mp.read_text())!=manifest: raise SystemExit("resume manifest mismatch")
    else: atomic_json(mp,manifest)
    sp=run/"state.json"
    if sp.exists():
        st=json.loads(sp.read_text())
        for c in st["cubes"].values():
            if c["status"] in ("SCOUT_ACTIVE","CERT_ACTIVE","CHECK_ACTIVE"): c["status"]="PENDING"
    else:
        st={"format":"CONWAY99-K66-DEEP7-ADAPTIVE-CERT-STATE-1","started_at":time.time(),"splits":0,
            "cubes":{rid:{"id":rid,"root_id":rid,"lits":[],"depth":0,"parent":None,"status":"PENDING"} for rid in ROOT_IDS}}
        atomic_json(sp,st)
    def save(): atomic_json(sp,st)
    def split(c,reason):
        used={abs(x) for x in c["lits"]}; v=next((x for x in ranks[c["root_id"]] if x not in used),None)
        if v is None: raise RuntimeError(f"no split variable {c['id']}")
        c["status"]="SPLIT"; c["split_var"]=v; c["split_reason"]=reason
        for bit,lit in (("0",-v),("1",v)):
            cid=c["id"]+bit
            if cid not in st["cubes"]:
                st["cubes"][cid]={"id":cid,"root_id":c["root_id"],"lits":c["lits"]+[lit],"depth":c["depth"]+1,"parent":c["id"],"status":"PENDING"}
        st["splits"]+=1
    print("K66_DEEP7_ADAPTIVE_CERT_START",flush=True); print(f"run={run}",flush=True)
    print("Exact x/!x coverage; thresholds only split, never discard obligations.",flush=True)
    print(f"scout={a.scout_workers}x{a.scout_seconds}s cert={a.cert_workers}x{a.cert_seconds}s proof_cap={a.proof_cap_gib}GiB",flush=True)
    last=time.time()
    while True:
        # Scout all PENDING leaves until they either solve quickly or split.
        while True:
            pend=[c for c in st["cubes"].values() if c["status"]=="PENDING"]
            if not pend: break
            batch=pend[:max(1,a.scout_workers)]
            with cf.ThreadPoolExecutor(max_workers=max(1,a.scout_workers)) as ex:
                futs={}
                for c in batch:
                    c["status"]="SCOUT_ACTIVE"; w=jobs/c["id"]/"scout"
                    futs[ex.submit(plain_scout,roots[c["root_id"]],c["lits"],str(w),a.cadical,a.scout_seconds)]=c["id"]
                save()
                for f in cf.as_completed(futs):
                    cid=futs[f]; c=st["cubes"][cid]; r=f.result(); c["scout_exit"]=r["exit"]; c["scout_wall"]=r["wall"]
                    if r["exit"]==20: c["status"]="CERT_PENDING"
                    elif r["exit"]==124: split(c,"SCOUT_TIMEOUT")
                    elif r["exit"]==10: raise RuntimeError(f"SAT scout {cid}")
                    else: raise RuntimeError(f"scout error {cid} exit={r['exit']}")
                    save()
            free,mem=resources(run)
            if free<a.disk_floor_gib or (mem>=0 and mem<a.mem_floor_gib): raise RuntimeError(f"resource danger disk={free:.1f} RAM={mem:.1f}")
            if time.time()-last>=a.status_seconds:
                co=Counter(c["status"] for c in st["cubes"].values())
                print(f"STATUS phase=SCOUT cubes={len(st['cubes'])} splits={st['splits']} counts={dict(co)} disk_free={free:.1f}GiB RAM={mem:.1f}GiB ETA=unknown",flush=True); last=time.time()
        # Run certification attempts on ready leaves.
        certp=[c for c in st["cubes"].values() if c["status"]=="CERT_PENDING"]
        if certp:
            batch=certp[:max(1,a.cert_workers)]
            with cf.ThreadPoolExecutor(max_workers=max(1,a.cert_workers)) as ex:
                futs={}
                for c in batch:
                    c["status"]="CERT_ACTIVE"; w=jobs/c["id"]/"cert"; c["work"]=str(w)
                    futs[ex.submit(proof_attempt,roots[c["root_id"]],c["lits"],str(w),a.cadical,a.cert_seconds,a.proof_cap_gib)]=c["id"]
                save()
                for f in cf.as_completed(futs):
                    cid=futs[f]; c=st["cubes"][cid]; r=f.result(); c.update(r)
                    if r["stop_reason"]:
                        p=Path(c["work"])/"proof.lrat"
                        if p.exists(): p.unlink()
                        split(c,r["stop_reason"])
                    elif r["exit"]==20: c["status"]="CHECK_PENDING"
                    elif r["exit"]==10: raise RuntimeError(f"SAT proof leaf {cid}")
                    else: raise RuntimeError(f"proof solver error {cid} exit={r['exit']}")
                    save()
        # Serial checker lane.
        checkp=[c for c in st["cubes"].values() if c["status"]=="CHECK_PENDING"]
        for c in checkp:
            free,mem=resources(run)
            if free<a.disk_floor_gib: raise RuntimeError("disk floor before checker")
            if mem>=0 and mem<8:
                print(f"CHECK_WAIT_RAM {c['id']} RAM={mem:.1f}GiB",flush=True); time.sleep(60); break
            c["status"]="CHECK_ACTIVE"; save(); r=check_proof(c["work"],a.lrat_check,a.cake); c["check"]=r
            if r["status"]!="CERTIFIED": raise RuntimeError(f"checker failed {c['id']}: {r}")
            c["status"]="CERTIFIED"; save(); print(f"CERTIFIED {c['id']} root={c['root_id']} depth={c['depth']} proof={c.get('proof_bytes',0)/1024**3:.2f}GiB",flush=True)
        remaining=[c for c in st["cubes"].values() if c["status"] not in ("SPLIT","CERTIFIED")]
        free,mem=resources(run)
        if time.time()-last>=a.status_seconds:
            co=Counter(c["status"] for c in st["cubes"].values()); cert=sum(c["status"]=="CERTIFIED" for c in st["cubes"].values())
            proof=sum(c.get("proof_bytes",0) for c in st["cubes"].values() if c["status"]=="CERTIFIED")/1024**3
            print(f"STATUS phase=CERTIFY cubes={len(st['cubes'])} splits={st['splits']} certified={cert} counts={dict(co)} proof_cert={proof:.2f}GiB disk_free={free:.1f}GiB RAM={mem:.1f}GiB ETA=unknown",flush=True); last=time.time()
        if free<a.disk_floor_gib or (mem>=0 and mem<a.mem_floor_gib): raise RuntimeError(f"resource danger disk={free:.1f} RAM={mem:.1f}")
        if not remaining: break
    cov={rid:coverage(st["cubes"],rid) for rid in ROOT_IDS}
    totalproof=sum(c.get("proof_bytes",0) for c in st["cubes"].values() if c["status"]=="CERTIFIED")
    summary={"format":"CONWAY99-K66-DEEP7-ADAPTIVE-CERT-SUMMARY-1","roots":ROOT_IDS,"root_hashes":ROOT_HASHES,
             "coverage_audit":cov,"splits":st["splits"],"certified_leaves":sum(c["status"]=="CERTIFIED" for c in st["cubes"].values()),
             "total_proof_bytes":totalproof,"claim_scope":"All seven reduced necessary profile-conflict root CNFs are covered by exact binary split trees whose terminal CNFs are individually LRAT+Cake certified UNSAT."}
    atomic_json(run/"summary.json",summary); st["status"]="COMPLETE"; st["coverage_audit"]=cov; save(); z,win=handoff(run,st)
    print("K66_DEEP7_ADAPTIVE_CERT_DONE",json.dumps(summary,sort_keys=True),flush=True); print("HANDOFF",z,flush=True)
    if win: print("HANDOFF_WINDOWS",win,flush=True)
    print("HANDOFF_SHA256",sha(z),flush=True)

if __name__=="__main__": main()
