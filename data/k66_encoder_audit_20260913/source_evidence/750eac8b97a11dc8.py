
from __future__ import annotations
import argparse, concurrent.futures as cf, gzip, hashlib, json, os, shutil, signal, subprocess, sys, threading, time, zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT_IDS = ["v4_09316","v4_09317","v4_09322","v4_09323","v4_09331","v4_09332","v4_09333"]
PRIMARY_COUNTS = {
    "v4_09316":634,"v4_09317":642,"v4_09322":654,"v4_09323":708,
    "v4_09331":608,"v4_09332":724,"v4_09333":741,
}
CADICAL_SHA="d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
LRAT_SHA="49f0bf5b418fec38dad3a199a9ae7eb52a4617269a6d360d49d3f580a9b98dfa"
CAKE_SHA="e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a"
LRAT_MARKER="c VERIFIED"
CAKE_MARKER=b"s VERIFIED UNSAT"

PID_LOCK=threading.Lock()
ACTIVE_PIDS=set()

def register(pid):
    with PID_LOCK: ACTIVE_PIDS.add(pid)

def unregister(pid):
    with PID_LOCK: ACTIVE_PIDS.discard(pid)

def kill_all():
    with PID_LOCK: pids=list(ACTIVE_PIDS)
    for pid in pids:
        try: os.killpg(pid,signal.SIGTERM)
        except ProcessLookupError: pass
    time.sleep(1)
    for pid in pids:
        try: os.killpg(pid,signal.SIGKILL)
        except ProcessLookupError: pass

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(path,obj):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    os.replace(tmp,path)

def mem_gib():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"): return int(line.split()[1])/1024**2
    return -1.0

def resource_snapshot(path):
    du=shutil.disk_usage(path)
    return du.free/1024**3, mem_gib()

def parse_header(path):
    with open(path) as f:
        for line in f:
            if line.startswith("p cnf "):
                _,_,v,c=line.split()
                return int(v),int(c)
    raise RuntimeError(f"missing DIMACS header {path}")

def primary_occurrence_order(path,nprimary):
    counts=[0]*(nprimary+1)
    with open(path) as f:
        for line in f:
            if not line or line[0] in "cp": continue
            for tok in line.split():
                v=abs(int(tok))
                if 1<=v<=nprimary: counts[v]+=1
    return sorted(range(1,nprimary+1),key=lambda v:(-counts[v],v))

def write_leaf(root,lits,path):
    nv,nc=parse_header(root)
    path.parent.mkdir(parents=True,exist_ok=True)
    replaced=False
    with open(root,"rb") as src,open(path,"wb") as out:
        for raw in src:
            if not replaced and raw.startswith(b"p cnf "):
                out.write(f"p cnf {nv} {nc+len(lits)}\n".encode()); replaced=True
            else:
                out.write(raw)
        if not replaced: raise RuntimeError("header replacement failed")
        for lit in lits: out.write(f"{lit} 0\n".encode())

def parse_dimacs(path):
    clauses=[]; cur=[]; nvars=None; nclauses=None
    for raw in path.read_text(errors="strict").splitlines():
        line=raw.strip()
        if not line or line.startswith("c"): continue
        if line.startswith("p "):
            p=line.split()
            if len(p)!=4 or p[1]!="cnf": raise RuntimeError("bad DIMACS header")
            nvars=int(p[2]); nclauses=int(p[3]); continue
        for tok in line.split():
            lit=int(tok)
            if lit==0: clauses.append(tuple(cur)); cur=[]
            else: cur.append(lit)
    if cur: raise RuntimeError("unterminated clause")
    if nvars is None or nclauses is None or len(clauses)!=nclauses:
        raise RuntimeError("DIMACS count mismatch")
    return clauses

def clause_state(clause,assignment):
    unit=None; n=0
    for lit in clause:
        val=assignment.get(abs(lit))
        if val is None:
            unit=lit; n+=1
            if n>1: return "open",None
        elif val==(lit>0): return "sat",None
    if n==0: return "conflict",None
    return "unit",unit

def make_root_up_lrat(cnf,proof):
    clauses=parse_dimacs(cnf); assign={}; hints=[]
    while True:
        progress=False
        for cid,cl in enumerate(clauses,1):
            st,lit=clause_state(cl,assign)
            if st=="conflict":
                hints.append(cid)
                lemma=len(clauses)+1
                proof.write_text(f"{lemma} 0 "+" ".join(map(str,hints))+" 0\n")
                return len(hints)
            if st=="unit":
                v=abs(lit); val=lit>0
                if v in assign:
                    if assign[v]!=val:
                        hints.append(cid)
                        lemma=len(clauses)+1
                        proof.write_text(f"{lemma} 0 "+" ".join(map(str,hints))+" 0\n")
                        return len(hints)
                    continue
                hints.append(cid); assign[v]=val; progress=True; break
        if not progress:
            raise RuntimeError("zero-byte CaDiCaL proof but CNF is not root-UP refutable")

def compress_proof(path):
    gz=path.with_suffix(path.suffix+".gz")
    tmp=gz.with_suffix(gz.suffix+".tmp")
    with open(path,"rb") as src,gzip.open(tmp,"wb",compresslevel=3) as dst:
        shutil.copyfileobj(src,dst,length=4<<20)
    os.replace(tmp,gz)
    raw_sha=sha(path); gz_sha=sha(gz); raw_bytes=path.stat().st_size; gz_bytes=gz.stat().st_size
    path.unlink()
    return {"proof_raw_sha256":raw_sha,"proof_raw_bytes":raw_bytes,
            "proof_gz_sha256":gz_sha,"proof_gz_bytes":gz_bytes,"proof_gz":str(gz)}

def solver_attempt(root,lits,work,cadical,proof_cap_gib):
    work=Path(work); work.mkdir(parents=True,exist_ok=True)
    cnf=work/"leaf.cnf"; proof=work/"proof.lrat"; wit=work/"witness.out"
    so,se=work/"cadical.out",work/"cadical.err"
    for p in (cnf,proof,wit,so,se,work/"lrat.out",work/"lrat.err",work/"cake.out",work/"cake.err"):
        if p.exists(): p.unlink()
    write_leaf(Path(root),lits,cnf)
    start=time.time()
    with open(so,"wb") as o,open(se,"wb") as e:
        proc=subprocess.Popen([cadical,"--lrat","--no-binary","-w",str(wit),str(cnf),str(proof)],
                              stdout=o,stderr=e,start_new_session=True)
        register(proc.pid)
        capped=False
        try:
            while proc.poll() is None:
                time.sleep(5)
                if proof.exists() and proof.stat().st_size>=proof_cap_gib*1024**3:
                    capped=True
                    os.killpg(proc.pid,signal.SIGTERM)
                    try: proc.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid,signal.SIGKILL); proc.wait()
                    break
            rc=proc.wait()
        finally:
            unregister(proc.pid)
    wall=time.time()-start
    size=proof.stat().st_size if proof.exists() else 0
    if capped:
        if proof.exists(): proof.unlink()
        return {"status":"CAP_SPLIT","exit":rc,"wall":wall,"proof_bytes":size,
                "leaf_cnf_sha256":sha(cnf)}
    if rc==20 and size==0:
        hints=make_root_up_lrat(cnf,proof); size=proof.stat().st_size
        rootup=True
    else:
        hints=None; rootup=False
    return {"status":"UNSAT_READY" if rc==20 else ("SAT" if rc==10 else f"ERROR_{rc}"),
            "exit":rc,"wall":wall,"proof_bytes":size,"proof_sha256":sha(proof) if size else None,
            "leaf_cnf_sha256":sha(cnf),"root_up_generated":rootup,"root_up_hints":hints}

def checker_attempt(work,lrat,cake):
    work=Path(work); cnf=work/"leaf.cnf"; proof=work/"proof.lrat"
    lo,le=work/"lrat.out",work/"lrat.err"; co,ce=work/"cake.out",work/"cake.err"
    t=time.time()
    with open(lo,"wb") as o,open(le,"wb") as e:
        p=subprocess.Popen([lrat,str(cnf),str(proof)],stdout=o,stderr=e,start_new_session=True)
        register(p.pid)
        try: lrc=p.wait()
        finally: unregister(p.pid)
    lmark=LRAT_MARKER in lo.read_text(errors="replace"); lw=time.time()-t
    if lrc!=0 or not lmark:
        return {"status":"LRAT_FAILED","lrat_exit":lrc,"lrat_marker":lmark,"lrat_wall":lw}
    t=time.time()
    with open(co,"wb") as o,open(ce,"wb") as e:
        p=subprocess.Popen([cake,str(cnf),str(proof)],stdout=o,stderr=e,start_new_session=True)
        register(p.pid)
        try: crc=p.wait()
        finally: unregister(p.pid)
    cmark=CAKE_MARKER in co.read_bytes(); cw=time.time()-t
    if crc!=0 or not cmark:
        return {"status":"CAKE_FAILED","lrat_exit":lrc,"lrat_marker":lmark,"lrat_wall":lw,
                "cake_exit":crc,"cake_marker":cmark,"cake_wall":cw}
    comp=compress_proof(proof)
    return {"status":"CERTIFIED","lrat_exit":lrc,"lrat_marker":lmark,"lrat_wall":lw,
            "cake_exit":crc,"cake_marker":cmark,"cake_wall":cw,**comp}

def children_map(cubes):
    d=defaultdict(list)
    for c in cubes.values():
        if c.get("parent") is not None: d[c["parent"]].append(c["id"])
    return d

def old_cut(old_cubes,root_id,depth):
    kids=children_map(old_cubes); selected=[]; included=set()
    stack=[root_id]
    while stack:
        cid=stack.pop(); c=old_cubes[cid]; included.add(cid)
        ck=kids.get(cid,[])
        if c["depth"]>=depth or len(ck)!=2:
            selected.append(cid)
        else:
            stack.extend(sorted(ck))
    return selected,included

def exact_children_from_old(old_cubes,cid):
    kids=children_map(old_cubes).get(cid,[])
    if len(kids)!=2: return None
    c=old_cubes[cid]
    got=[old_cubes[k] for k in sorted(kids)]
    # infer variable and validate complementary extension
    if len(got[0]["lits"])!=len(c["lits"])+1 or len(got[1]["lits"])!=len(c["lits"])+1:
        return None
    a=got[0]["lits"][-1]; b=got[1]["lits"][-1]
    if a!=-b or got[0]["lits"][:-1]!=c["lits"] or got[1]["lits"][:-1]!=c["lits"]:
        return None
    return got

def choose_fresh_split(c,rank):
    used={abs(x) for x in c["lits"]}
    return next((v for v in rank if v not in used),None)

def coverage_audit(cubes,root_id):
    kids=children_map(cubes); seen=set(); stack=[root_id]
    while stack:
        cid=stack.pop()
        if cid in seen: raise RuntimeError("cycle")
        seen.add(cid); c=cubes[cid]
        if c["status"]=="SPLIT":
            ck=kids.get(cid,[])
            if len(ck)!=2: raise RuntimeError(f"incomplete split {cid}")
            a,b=(cubes[x] for x in ck)
            if a["lits"][:-1]!=c["lits"] or b["lits"][:-1]!=c["lits"] or a["lits"][-1]!=-b["lits"][-1]:
                raise RuntimeError(f"bad children {cid}")
            stack.extend(ck)
        elif c["status"]!="CERTIFIED":
            raise RuntimeError(f"uncovered leaf {cid}: {c['status']}")
    return len(seen)

def make_handoff(run,state):
    stamp=time.strftime("%Y%m%d_%H%M%S")
    zp=run/f"k66_deep7_coarsecert_handoff_{stamp}.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(run/"manifest.json","manifest.json"); z.write(run/"state.json","state.json")
        if (run/"policy_changes.json").exists(): z.write(run/"policy_changes.json","policy_changes.json")
        if (run/"harvest_manifest.json").exists(): z.write(run/"harvest_manifest.json","harvest_manifest.json")
        if (run/"summary.json").exists(): z.write(run/"summary.json","summary.json")
        for c in state["cubes"].values():
            if c["status"]=="CERTIFIED":
                w=Path(c["work"]); pref=c["id"].replace("/","_")
                for n in ("cadical.out","cadical.err","lrat.out","lrat.err","cake.out","cake.err"):
                    p=w/n
                    if p.exists(): z.write(p,f"{pref}/{n}")
    win=Path("/mnt/c/Users/rb/Downloads")/zp.name
    try: shutil.copy2(zp,win)
    except Exception: win=None
    return zp,win

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-run",required=True)
    ap.add_argument("--old-scout-run",required=True)
    ap.add_argument("--run-dir",default=None)
    ap.add_argument("--cut-depth",type=int,default=2)
    ap.add_argument("--harvest-cut-depth",type=int,default=None)
    ap.add_argument("--workers",type=int,default=20)
    ap.add_argument("--proof-cap-gib",type=float,default=16)
    ap.add_argument("--status-seconds",type=float,default=600)
    ap.add_argument("--disk-floor-gib",type=float,default=75)
    ap.add_argument("--mem-floor-gib",type=float,default=4)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--lrat-check",default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake",default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr"))
    a=ap.parse_args()

    source=Path(a.source_run)
    oldrun=Path(a.old_scout_run)
    oldstate=json.loads((oldrun/"state.json").read_text())
    oldcubes=oldstate["cubes"]
    roots_dir=source/"neighbor_star_deep7_autonomous_20260909"/"global"

    for p,h,n in ((Path(a.cadical),CADICAL_SHA,"cadical"),(Path(a.lrat_check),LRAT_SHA,"lrat-check"),(Path(a.cake),CAKE_SHA,"cake")):
        if not p.exists(): raise SystemExit(f"missing {n}: {p}")
        if sha(p)!=h: raise SystemExit(f"{n} hash mismatch")

    roots={}; root_hashes={}; ranks={}
    for rid in ROOT_IDS:
        p=roots_dir/rid/"model.cnf"
        if not p.exists(): raise SystemExit(f"missing root {p}")
        if rid not in oldcubes: raise SystemExit(f"old tree missing root {rid}")
        if oldcubes[rid].get("root_id") != rid or oldcubes[rid].get("lits") != []:
            raise SystemExit(f"old tree root identity mismatch {rid}")
        roots[rid]=str(p)
        root_hashes[rid]=sha(p)
        ranks[rid]=primary_occurrence_order(p,PRIMARY_COUNTS[rid])

    if a.run_dir:
        run=Path(a.run_dir)
    else:
        run=source.parent/f"k66_deep7_coarsecert_{time.strftime('%Y%m%d_%H%M%S')}"
    run.mkdir(parents=True,exist_ok=True); (run/"jobs").mkdir(exist_ok=True)

    manifest={"format":"CONWAY99-K66-DEEP7-COARSECERT-1","roots":roots,"old_tree_state_sha256":sha(oldrun/"state.json"),"cut_depth":a.cut_depth,
              "root_hashes":root_hashes,
              "policy":{"workers":a.workers,"proof_cap_gib":a.proof_cap_gib,
                        "status_seconds":a.status_seconds,"disk_floor_gib":a.disk_floor_gib,
                        "mem_floor_gib":a.mem_floor_gib},
              "tool_hashes":{"cadical":CADICAL_SHA,"lrat-check":LRAT_SHA,"cake":CAKE_SHA}}
    mp=run/"manifest.json"
    policy_log=run/"policy_changes.json"
    if mp.exists():
        base_manifest=json.loads(mp.read_text())
        # The immutable base manifest may differ from this resume request ONLY
        # in policy.proof_cap_gib. All mathematical inputs, tools, cut depth,
        # worker count, status cadence and safety floors must remain identical.
        base_cmp=json.loads(json.dumps(base_manifest))
        req_cmp=json.loads(json.dumps(manifest))
        try:
            base_cap=float(base_cmp["policy"]["proof_cap_gib"])
            req_cap=float(req_cmp["policy"]["proof_cap_gib"])
        except Exception as e:
            raise SystemExit(f"malformed manifest policy: {e}")
        base_cmp["policy"]["proof_cap_gib"]="__CAP__"
        req_cmp["policy"]["proof_cap_gib"]="__CAP__"
        if base_cmp!=req_cmp:
            raise SystemExit("resume manifest mismatch outside proof_cap_gib")
        if policy_log.exists():
            pl=json.loads(policy_log.read_text())
            if pl.get("format")!="CONWAY99-K66-DEEP7-POLICY-CHANGES-1":
                raise SystemExit("bad policy_changes format")
            if pl.get("base_manifest_sha256")!=sha(mp):
                raise SystemExit("policy_changes base manifest hash mismatch")
            events=pl.get("events",[])
            effective_cap=float(events[-1]["to"]) if events else base_cap
        else:
            pl={"format":"CONWAY99-K66-DEEP7-POLICY-CHANGES-1",
                "base_manifest_sha256":sha(mp),"events":[]}
            effective_cap=base_cap
        if effective_cap!=req_cap:
            event={"at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                   "field":"proof_cap_gib","from":effective_cap,"to":req_cap,
                   "runner_sha256":sha(Path(sys.argv[0])),
                   "reason":"operator-directed resume policy change; exact x/!x coverage and all prior certificates remain unchanged"}
            pl["events"].append(event)
            atomic_json(policy_log,pl)
            print(f"POLICY_CHANGE proof_cap_gib {effective_cap:g} -> {req_cap:g} audit={policy_log}",flush=True)
        manifest=base_manifest
    else:
        atomic_json(mp,manifest)

    sp=run/"state.json"
    if sp.exists():
        st=json.loads(sp.read_text())
        for c in st["cubes"].values():
            if c["status"]=="SOLVER_ACTIVE": c["status"]="PENDING"
            elif c["status"]=="CHECK_ACTIVE": c["status"]="CHECK_PENDING"
    else:
        newcubes={}; frontier=[]
        for rid in ROOT_IDS:
            selected,included=old_cut(oldcubes,rid,a.cut_depth)
            frontier.extend(selected)
            for cid in included:
                oc=oldcubes[cid]
                newcubes[cid]={"id":cid,"root_id":oc["root_id"],"lits":list(oc["lits"]),
                               "depth":oc["depth"],"parent":oc.get("parent"),
                               "status":"PENDING" if cid in selected else "SPLIT"}
                if cid not in selected:
                    oldkids=exact_children_from_old(oldcubes,cid)
                    if oldkids:
                        newcubes[cid]["split_var"]=abs(oldkids[0]["lits"][-1])
                        newcubes[cid]["split_source"]="OLD_SCOUT_TREE"
        st={"format":"CONWAY99-K66-DEEP7-COARSECERT-STATE-1","started_at":time.time(),
            "cubes":newcubes,"splits":sum(c["status"]=="SPLIT" for c in newcubes.values()),
            "initial_frontier":sorted(frontier)}
        atomic_json(sp,st)

    def save(): atomic_json(sp,st)
    def do_split(c):
        cid=c["id"]; oldkids=exact_children_from_old(oldcubes,cid) if cid in oldcubes else None
        if oldkids:
            children=oldkids; source_tag="OLD_SCOUT_TREE"; v=abs(children[0]["lits"][-1])
        else:
            v=choose_fresh_split(c,ranks[c["root_id"]])
            if v is None: raise RuntimeError(f"no split variable {cid}")
            children=[
                {"id":cid+"0","root_id":c["root_id"],"lits":c["lits"]+[-v],"depth":c["depth"]+1,"parent":cid},
                {"id":cid+"1","root_id":c["root_id"],"lits":c["lits"]+[v],"depth":c["depth"]+1,"parent":cid},
            ]; source_tag="FRESH_OCCURRENCE_RANK"
        c["status"]="SPLIT"; c["split_var"]=v; c["split_source"]=source_tag
        for ch in children:
            if ch["id"] not in st["cubes"]:
                rec={"id":ch["id"],"root_id":ch["root_id"],"lits":list(ch["lits"]),
                     "depth":ch["depth"],"parent":cid,"status":"PENDING"}
                if ch["id"] in oldcubes:
                    rec["old_scout_status"]=oldcubes[ch["id"]].get("status")
                st["cubes"][ch["id"]]=rec
        st["splits"]+=1

    # Optional one-time harvest: replace the currently open coarse leaves by
    # the exact precomputed split forest from the old scout, down to a target
    # depth. Old scout statuses are only scheduling hints; every terminal leaf
    # is re-proved with LRAT and checked with lrat-check + Cake.
    harvest_path=run/"harvest_manifest.json"
    if a.harvest_cut_depth is not None:
        target=int(a.harvest_cut_depth)
        if target<=a.cut_depth:
            raise SystemExit("harvest-cut-depth must exceed base cut-depth")
        if harvest_path.exists():
            hm=json.loads(harvest_path.read_text())
            if hm.get("format")!="CONWAY99-K66-DEEP7-HARVEST-1":
                raise SystemExit("bad harvest manifest format")
            if int(hm.get("target_depth",-1))!=target:
                raise SystemExit("harvest target mismatch")
            if hm.get("old_tree_state_sha256")!=sha(oldrun/"state.json"):
                raise SystemExit("harvest old-tree hash mismatch")
        else:
            # Preserve the exact pre-harvest state on disk for audit/recovery.
            backup=run/f"state_pre_harvest_cut{target}.json"
            if not backup.exists():
                shutil.copy2(sp,backup)
            pre_hash=sha(backup)

            # Any interrupted coarse solver proof on a leaf that we are about
            # to replace by exact old-tree splits is disposable. Delete only
            # transient proof/witness files; keep logs and leaf CNF.
            deleted_bytes=0
            deleted_files=[]
            open_ids=[c["id"] for c in st["cubes"].values()
                      if c["status"] not in ("SPLIT","CERTIFIED")]
            if not open_ids:
                raise SystemExit("harvest requested but no open coarse leaves")

            oldkids_map=children_map(oldcubes)
            queue=list(sorted(open_ids))
            frontier=[]
            expanded=0
            reused_existing=0

            def old_children_fast(cid):
                kids=oldkids_map.get(cid,[])
                if len(kids)!=2 or cid not in oldcubes:
                    return None
                c0=oldcubes[cid]
                got=[oldcubes[k] for k in sorted(kids)]
                if any(len(g["lits"])!=len(c0["lits"])+1 for g in got):
                    return None
                a0=got[0]["lits"][-1]; b0=got[1]["lits"][-1]
                if a0!=-b0 or got[0]["lits"][:-1]!=c0["lits"] or got[1]["lits"][:-1]!=c0["lits"]:
                    return None
                return got

            while queue:
                cid=queue.pop()
                c=st["cubes"][cid]
                if c["status"]=="CERTIFIED":
                    continue
                if c["depth"]>=target:
                    c["status"]="PENDING"
                    if cid in oldcubes:
                        c["old_scout_status"]=oldcubes[cid].get("status")
                    frontier.append(cid)
                    continue
                kids=old_children_fast(cid)
                if not kids:
                    c["status"]="PENDING"
                    if cid in oldcubes:
                        c["old_scout_status"]=oldcubes[cid].get("status")
                    frontier.append(cid)
                    continue

                # Clean stale transient proof from an interrupted solver on
                # this parent before it becomes an internal split node.
                w=c.get("work")
                if w:
                    for name in ("proof.lrat","witness.out"):
                        p=Path(w)/name
                        if p.exists():
                            sz=p.stat().st_size
                            p.unlink()
                            deleted_bytes+=sz
                            deleted_files.append({"path":str(p),"bytes":sz})

                c["status"]="SPLIT"
                c["split_var"]=abs(kids[0]["lits"][-1])
                c["split_source"]="OLD_SCOUT_HARVEST"
                # Drop incomplete-attempt metadata, but retain work/log path.
                c.pop("solver",None)
                c.pop("checker",None)

                for ch in kids:
                    if ch["id"] in st["cubes"]:
                        rec=st["cubes"][ch["id"]]
                        reused_existing+=1
                    else:
                        rec={"id":ch["id"],"root_id":ch["root_id"],"lits":list(ch["lits"]),
                             "depth":ch["depth"],"parent":cid,"status":"PENDING"}
                        st["cubes"][ch["id"]]=rec
                    rec["old_scout_status"]=oldcubes[ch["id"]].get("status")
                    queue.append(ch["id"])
                st["splits"]+=1
                expanded+=1

            # Deduplicate frontier in case pre-existing nodes were encountered.
            frontier=sorted(set(frontier))
            by_root=Counter(st["cubes"][cid]["root_id"] for cid in frontier)
            by_old=Counter(st["cubes"][cid].get("old_scout_status","UNKNOWN") for cid in frontier)
            by_depth=Counter(st["cubes"][cid]["depth"] for cid in frontier)
            save()
            hm={"format":"CONWAY99-K66-DEEP7-HARVEST-1",
                "created_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                "runner_sha256":sha(Path(sys.argv[0])),
                "target_depth":target,
                "base_state_backup":str(backup),
                "base_state_sha256":pre_hash,
                "old_tree_state_sha256":sha(oldrun/"state.json"),
                "open_roots_before":sorted(open_ids),
                "expanded_internal_nodes":expanded,
                "reused_existing_nodes":reused_existing,
                "frontier_count":len(frontier),
                "frontier_by_root":dict(sorted(by_root.items())),
                "frontier_by_old_scout_status":dict(sorted(by_old.items())),
                "frontier_by_depth":dict(sorted((str(k),v) for k,v in by_depth.items())),
                "deleted_transient_bytes":deleted_bytes,
                "deleted_transient_files":deleted_files,
                "semantics":"Old scout split structure is reused only as an exact x/!x partition. Old scout UNSAT/CERT_PENDING labels are scheduling hints only; every terminal obligation must be freshly LRAT+Cake certified."}
            atomic_json(harvest_path,hm)
            print(f"HARVEST_PREPARED cut={target} frontier={len(frontier)} old_status={dict(by_old)} deleted_transient={deleted_bytes/1024**3:.2f}GiB audit={harvest_path}",flush=True)

    workers=max(1,min(a.workers,20))
    free,mem=resource_snapshot(run)
    print("K66_DEEP7_COARSECERT_START",flush=True)
    print(f"run={run}",flush=True)
    print(f"initial_frontier={len(st.get('initial_frontier',[]))} cut_depth={a.cut_depth} harvest_cut={a.harvest_cut_depth} workers={workers}",flush=True)
    print(f"wallclock_timeouts=NONE proof_cap={a.proof_cap_gib}GiB -> exact split only",flush=True)
    print("checker=serial lrat-check+Cake; certified proofs gzip-compressed after verification",flush=True)
    print(f"disk_free={free:.1f}GiB RAM={mem:.1f}GiB",flush=True)

    solver_pool=cf.ThreadPoolExecutor(max_workers=workers)
    checker_pool=cf.ThreadPoolExecutor(max_workers=1)
    solver_futs={}; checker_fut=None; checker_cid=None
    last=time.time(); start=st.get("started_at",time.time())
    try:
        while True:
            # Collect completed solver attempts.
            done=[f for f in list(solver_futs) if f.done()]
            for f in done:
                cid=solver_futs.pop(f); c=st["cubes"][cid]
                r=f.result(); c["solver"]=r
                if r["status"]=="UNSAT_READY":
                    c["status"]="CHECK_PENDING"
                    print(f"SOLVER_DONE {cid} root={c['root_id']} depth={c['depth']} wall={r['wall']/60:.1f}min proof={r['proof_bytes']/1024**3:.2f}GiB rootUP={r.get('root_up_generated')}",flush=True)
                elif r["status"]=="CAP_SPLIT":
                    print(f"PROOF_CAP_SPLIT {cid} root={c['root_id']} depth={c['depth']} wall={r['wall']/60:.1f}min partial={r['proof_bytes']/1024**3:.2f}GiB",flush=True)
                    do_split(c)
                elif r["status"]=="SAT":
                    raise RuntimeError(f"SAT leaf contradicts root UNSAT: {cid}")
                else:
                    raise RuntimeError(f"solver failure {cid}: {r}")
                save()

            # Collect checker.
            if checker_fut is not None and checker_fut.done():
                r=checker_fut.result(); c=st["cubes"][checker_cid]; c["checker"]=r
                if r["status"]!="CERTIFIED": raise RuntimeError(f"checker failure {checker_cid}: {r}")
                c["status"]="CERTIFIED"; save()
                print(f"CERTIFIED {checker_cid} root={c['root_id']} depth={c['depth']} gz={r['proof_gz_bytes']/1024**3:.2f}GiB",flush=True)
                checker_fut=None; checker_cid=None

            # Start serial checker if idle.
            if checker_fut is None:
                cps=[c for c in st["cubes"].values() if c["status"]=="CHECK_PENDING"]
                if cps:
                    free,mem=resource_snapshot(run)
                    if mem>=8 and free>=a.disk_floor_gib:
                        c=sorted(cps,key=lambda x:(x["depth"],x["id"]))[0]
                        c["status"]="CHECK_ACTIVE"; checker_cid=c["id"]
                        checker_fut=checker_pool.submit(checker_attempt,c["work"],a.lrat_check,a.cake)
                        save()

            # Admission: keep solver lanes full unless near hard resource floor.
            free,mem=resource_snapshot(run)
            if free<a.disk_floor_gib or (mem>=0 and mem<a.mem_floor_gib):
                raise RuntimeError(f"RESOURCE_DANGER disk={free:.1f}GiB RAM={mem:.1f}GiB")
            pending=sorted(
                (c for c in st["cubes"].values() if c["status"]=="PENDING"),
                key=lambda c:(0 if c.get("old_scout_status")=="CERT_PENDING" else 1,
                              c["depth"],c["root_id"],c["id"]))
            # Admit solver lanes one at a time. Reserve one full proof-cap for
            # every solver that would be active after the next admission,
            # rather than pessimistically reserving cap*all configured workers.
            # This preserves the disk floor while allowing small frontiers
            # (e.g. the four remaining spines) to use large proof caps safely.
            while (pending and len(solver_futs)<workers
                   and free>=max(a.disk_floor_gib+(len(solver_futs)+1)*a.proof_cap_gib,150)):
                c=pending.pop(0); c["status"]="SOLVER_ACTIVE"
                work=run/"jobs"/c["id"]/"cert"; c["work"]=str(work)
                fut=solver_pool.submit(solver_attempt,roots[c["root_id"]],c["lits"],str(work),a.cadical,a.proof_cap_gib)
                solver_futs[fut]=c["id"]; save()

            nonterm=[c for c in st["cubes"].values() if c["status"] not in ("SPLIT","CERTIFIED")]
            if not nonterm and not solver_futs and checker_fut is None: break

            now=time.time()
            if now-last>=a.status_seconds:
                co=Counter(c["status"] for c in st["cubes"].values())
                leaves=sum(c["status"]!="SPLIT" for c in st["cubes"].values())
                cert=sum(c["status"]=="CERTIFIED" for c in st["cubes"].values())
                elapsed=now-start
                rate=cert/elapsed if cert and elapsed>0 else 0
                remain=sum(c["status"] not in ("SPLIT","CERTIFIED") for c in st["cubes"].values())
                eta="unknown" if rate==0 else f"{remain/rate/3600:.1f}h(current frontier)"
                active_ids=list(solver_futs.values())
                active_raw=sum((Path(st["cubes"][cid]["work"])/"proof.lrat").stat().st_size
                               for cid in active_ids
                               if (Path(st["cubes"][cid]["work"])/"proof.lrat").exists())/1024**3
                compressed=sum(c.get("checker",{}).get("proof_gz_bytes",0)
                               for c in st["cubes"].values() if c["status"]=="CERTIFIED")/1024**3
                print(f"STATUS cubes={len(st['cubes'])} splits={st['splits']} leaves={leaves} counts={dict(co)} active_solvers={len(solver_futs)} checker={checker_cid} active_proof={active_raw:.1f}GiB cert_gz={compressed:.1f}GiB disk_free={free:.1f}GiB RAM={mem:.1f}GiB ETA={eta}",flush=True)
                last=now
            time.sleep(1)

        coverage={rid:coverage_audit(st["cubes"],rid) for rid in ROOT_IDS}
        st["coverage_audit"]=coverage; st["completed_at"]=time.time(); st["status"]="COMPLETE"; save()
        summary={"format":"CONWAY99-K66-DEEP7-COARSECERT-SUMMARY-1","roots":ROOT_IDS,
                 "coverage_audit":coverage,"splits":st["splits"],
                 "certified_leaves":sum(c["status"]=="CERTIFIED" for c in st["cubes"].values()),
                 "claim_scope":"Seven reduced profile-conflict root CNFs are fully covered by exact binary split trees; every terminal leaf is LRAT+Cake certified UNSAT. Proofs are stored losslessly gzip-compressed after verification. IMPORTANT: this run does not certify the prior neighbor-star profile removals used to construct the reduced roots; those are separate proof obligations required before claiming full k66 closure."}
        atomic_json(run/"summary.json",summary)
        hp,win=make_handoff(run,st)
        print("K66_DEEP7_COARSECERT_DONE",json.dumps(summary,sort_keys=True),flush=True)
        print("METADATA_HANDOFF",hp,flush=True)
        if win: print("METADATA_HANDOFF_WINDOWS",win,flush=True)
        print("METADATA_HANDOFF_SHA256",sha(hp),flush=True)
    except KeyboardInterrupt:
        print("K66_DEEP7_COARSECERT_STOP KeyboardInterrupt",flush=True); kill_all(); save(); raise
    except BaseException:
        kill_all(); save(); raise
    finally:
        solver_pool.shutdown(wait=True,cancel_futures=True)
        checker_pool.shutdown(wait=True,cancel_futures=True)

if __name__=="__main__":
    main()
