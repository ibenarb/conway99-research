
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

IDS = ["v4_09220","v4_09221","v4_09226","v4_09227","v4_09233","v4_09234","v4_09235",
       "v4_09236","v4_09238","v4_09239","v4_09274","v4_09284","v4_09285"]
CADICAL_SHA="d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
LRAT_SHA="49f0bf5b418fec38dad3a199a9ae7eb52a4617269a6d360d49d3f580a9b98dfa"
CAKE_SHA="e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a"
MARK=b"s VERIFIED UNSAT"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def memgib():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"): return int(line.split()[1])/1024**2
    return -1.0

def solve(cid, root, cadical):
    d=root/cid; c=d/"certification_batch13"; c.mkdir(exist_ok=True)
    proof=c/"proof.lrat"; wit=c/"witness.out"
    for p in (proof,wit,c/"cadical.out",c/"cadical.err",c/"lrat.out",c/"lrat.err",c/"cake.out",c/"cake.err"):
        if p.exists(): p.unlink()
    t=time.time()
    with open(c/"cadical.out","wb") as o, open(c/"cadical.err","wb") as e:
        rc=subprocess.run([cadical,"--lrat","--no-binary","-w",str(wit),str(d/"model.cnf"),str(proof)],
                          stdout=o,stderr=e).returncode
    return {"id":cid,"solver_exit":rc,"solver_wall":time.time()-t,
            "cnf_sha256":sha(d/"model.cnf"),
            "proof_bytes":proof.stat().st_size if proof.exists() else 0,
            "proof_sha256":sha(proof) if proof.exists() else None}

def check(rec,root,lrat,cake):
    cid=rec["id"]; d=root/cid; c=d/"certification_batch13"; proof=c/"proof.lrat"; cnf=d/"model.cnf"
    if rec["solver_exit"]!=20:
        rec["status"]="SOLVER_NOT_UNSAT"; return rec
    t=time.time()
    with open(c/"lrat.out","wb") as o, open(c/"lrat.err","wb") as e:
        rc=subprocess.run([lrat,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    txt=(c/"lrat.out").read_text(errors="replace")
    rec.update({"lrat_exit":rc,"lrat_wall":time.time()-t,"lrat_marker":"c VERIFIED" in txt})
    if rc!=0 or "c VERIFIED" not in txt:
        rec["status"]="LRAT_FAILED"; return rec
    t=time.time()
    with open(c/"cake.out","wb") as o, open(c/"cake.err","wb") as e:
        crc=subprocess.run([cake,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    marker=MARK in (c/"cake.out").read_bytes()
    rec.update({"cake_exit":crc,"cake_wall":time.time()-t,"cake_marker":marker})
    rec["status"]="UNSAT_CERTIFIED_MODEL" if crc==0 and marker else "CAKE_FAILED"
    return rec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scout-dir",required=True)
    ap.add_argument("--workers",type=int,default=12)
    ap.add_argument("--status-seconds",type=int,default=600)
    ap.add_argument("--disk-floor-gib",type=float,default=75)
    ap.add_argument("--cadical",default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--lrat-check",default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake",default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr"))
    a=ap.parse_args(); root=Path(a.scout_dir)

    tools=[(a.cadical,CADICAL_SHA,"cadical"),(a.lrat_check,LRAT_SHA,"lrat-check"),(a.cake,CAKE_SHA,"cake")]
    for p,h,n in tools:
        p=Path(p)
        if not p.exists(): raise SystemExit(f"missing {n}: {p}")
        if sha(p)!=h: raise SystemExit(f"{n} hash mismatch")
    for cid in IDS:
        if not (root/cid/"model.cnf").exists(): raise SystemExit(f"missing {cid}/model.cnf")
    free=shutil.disk_usage(root).free/1024**3
    if free<100: raise SystemExit(f"disk admission refused: {free:.1f} GiB")

    workers=max(1,min(a.workers,12))
    print(f"K66_CERT13_START cases=13 solver_workers={workers} timeouts=NONE checker_phase=SERIAL",flush=True)
    print(f"disk_free={free:.1f}GiB mem_available={memgib():.1f}GiB",flush=True)

    records={}; start=time.time(); last=start
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs={ex.submit(solve,cid,root,a.cadical):cid for cid in IDS}
        while futs:
            done=[f for f in list(futs) if f.done()]
            for f in done:
                cid=futs.pop(f)
                try: rec=f.result()
                except Exception as e: rec={"id":cid,"status":"ERROR","error":repr(e)}
                records[cid]=rec
                if "solver_exit" in rec:
                    print(f"SOLVER_DONE {cid} exit={rec['solver_exit']} wall={rec['solver_wall']:.1f}s proof={rec['proof_bytes']/1024**3:.2f}GiB",flush=True)
                else:
                    print("SOLVER_ERROR",json.dumps(rec),flush=True)
            free=shutil.disk_usage(root).free/1024**3
            if free<a.disk_floor_gib:
                subprocess.run(["pkill","-TERM","-f",str(Path(a.cadical))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                raise RuntimeError(f"disk floor reached: {free:.1f} GiB")
            now=time.time()
            if now-last>=a.status_seconds:
                total=sum(r.get("proof_bytes",0) for r in records.values())/1024**3
                print(f"STATUS phase=SOLVE elapsed={(now-start)/60:.1f}min done={len(records)}/13 active={len(futs)} proof_done={total:.2f}GiB disk_free={free:.1f}GiB ETA=unknown",flush=True)
                last=now
            if futs and not done: time.sleep(1)

    print("CHECKER_PHASE_START serial",flush=True)
    for cid in IDS:
        records[cid]=check(records[cid],root,a.lrat_check,a.cake)
        r=records[cid]
        print(f"CHECK_DONE {cid} status={r['status']} lrat={r.get('lrat_exit')} cake={r.get('cake_exit')} marker={r.get('cake_marker')}",flush=True)

    certified=[cid for cid in IDS if records[cid].get("status")=="UNSAT_CERTIFIED_MODEL"]
    summary={"format":"CONWAY99-K66-PROFILE-CONFLICT-CERT13-1",
             "claim_scope":"LRAT+Cake UNSAT certification of the necessary profile-frequency plus pair-conflict CNFs. Exclusion of an H additionally requires the model-necessity/encoder audit.",
             "certified_model_unsat":certified,"certified_count":len(certified),
             "records":[records[c] for c in IDS]}
    (root/"cert13_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")

    stamp=time.strftime("%Y%m%d_%H%M%S")
    handoff=root/f"profile_conflict_cert13_handoff_{stamp}.zip"
    with zipfile.ZipFile(handoff,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(root/"cert13_summary.json","cert13_summary.json")
        for cid in IDS:
            c=root/cid/"certification_batch13"
            for name in ("cadical.out","cadical.err","lrat.out","lrat.err","cake.out","cake.err"):
                p=c/name
                if p.exists(): z.write(p,f"{cid}/{name}")
    win=Path("/mnt/c/Users/rb/Downloads")/handoff.name
    try:
        shutil.copy2(handoff,win)
        print("HANDOFF_WINDOWS",win,flush=True)
    except Exception as e:
        print("HANDOFF_WINDOWS_FAILED",repr(e),flush=True)
    print(f"K66_CERT13_DONE certified_model_unsat={len(certified)}/13",flush=True)
    print("HANDOFF",handoff,flush=True)

if __name__=="__main__":
    main()
