#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, os, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

from row_build import check, digest, row_alternatives

HERE=Path(__file__).resolve().parent
PROBE=HERE/"probe_target_depth.py"

def atomic(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True))
    os.replace(tmp,path)

def parse_rows(raw):
    return tuple(int(x,16) if isinstance(x,str) else int(x) for x in raw)

def harvest(run_dir,cuts):
    bank={d:{} for d in cuts}
    errors=[]
    for p in sorted(Path(run_dir).rglob("*.json")):
        try:
            data=json.loads(p.read_text())
        except Exception as e:
            errors.append({"file":str(p),"error":f"json:{e}"})
            continue
        for key in ("best","prefix"):
            raw=data.get(key)
            if not raw:
                continue
            try:
                rows=parse_rows(raw); check(rows)
            except Exception as e:
                errors.append({"file":str(p),"key":key,"error":str(e)})
                continue
            for d in cuts:
                if len(rows)<d:
                    continue
                q=rows[:d]; h=digest(q)
                rec=bank[d].setdefault(h,{"rows":q,"sources":[]})
                rec["sources"].append(f"{p.name}:{key}")
    return bank,errors

def base_file(out,d,h,rec):
    p=Path(out)/"bases"/f"d{d:02d}_{h[:16]}.json"
    if not p.exists():
        atomic(p,{"best":[hex(x) for x in rec["rows"]],
                  "depth":d,"sha256":h,"sources":rec["sources"]})
    return p

def boot_id():
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except Exception:
        return None

def run_probe(base,cut,target,cfg,result_path,timeout):
    cmd=[
        sys.executable,str(PROBE),str(base),
        "--base-depth",str(cut),
        "--target-depth",str(target),
        "--node-limit",str(cfg["node_limit"]),
        "--solution-limit",str(cfg["solution_limit"]),
        "--seed",str(cfg["seed"]+cut*1000003+target*104729),
    ]
    t0=time.time()
    try:
        cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        elapsed=time.time()-t0
        if cp.returncode!=0:
            result={"status":"TASK_ERROR","returncode":cp.returncode,
                    "stderr":cp.stderr[-12000:],"elapsed_s":elapsed}
        else:
            lines=[x for x in cp.stdout.splitlines() if x.strip()]
            result=json.loads(lines[-1])
            result["elapsed_s"]=elapsed
    except subprocess.TimeoutExpired as e:
        result={"status":"TASK_TIMEOUT_UNKNOWN","elapsed_s":time.time()-t0,
                "stdout_tail":(e.stdout or "")[-4000:] if isinstance(e.stdout,str) else "",
                "stderr_tail":(e.stderr or "")[-4000:] if isinstance(e.stderr,str) else ""}
    atomic(result_path,result)
    return result

def climb(base,cut,h,cfg,out,deadline):
    target=cfg["target_start"]
    best=cfg["known_best_depth"]
    history=[]
    while target<=84:
        rp=Path(out)/"tasks"/f"d{cut:02d}_{h[:16]}_t{target:02d}.json"
        if rp.exists():
            result=json.loads(rp.read_text())
        else:
            remaining=deadline-time.time()-cfg["shutdown_reserve_seconds"]
            if remaining<=0:
                return {"cut":cut,"sha256":h,"best":best,
                        "status":"CAMPAIGN_TIME_RESERVE","history":history}
            timeout=min(cfg["task_timeout_seconds"],max(1,int(remaining)))
            result=run_probe(base,cut,target,cfg,rp,timeout)
        status=result.get("status","UNKNOWN")
        history.append({"target":target,"status":status,"file":str(rp)})
        if status==f"FOUND_DEPTH{target}":
            best=max(best,target)
            target+=1
            continue
        return {"cut":cut,"sha256":h,"best":best,
                "status":status,"history":history}
    return {"cut":cut,"sha256":h,"best":84,"status":"COMPLETE_SRG","history":history}

def heartbeat(out,phase,best,done,total,unknown):
    atomic(Path(out)/"HEARTBEAT.json",{
        "realtime":time.time(),"monotonic":time.monotonic(),"pid":os.getpid(),
        "boot_id":boot_id(),"phase":phase,"best_depth":best,
        "done":done,"total":total,"unknown":unknown})
    print(f"WALK cut={phase} best={best}/84 done={done}/{total} unk={unknown}"[:79],
          flush=True)

def run(cfgfile,out,run_dir):
    cfg=json.loads(Path(cfgfile).read_text())
    cuts=list(cfg["cut_depths"])
    if cuts!=sorted(set(cuts),reverse=True) or min(cuts)<1 or max(cuts)>84:
        raise ValueError("cut_depths must be unique descending depths")
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    bank,errors=harvest(run_dir,cuts)
    manifest={
        "version":cfg["version"],"config":cfg,"source_run_dir":str(Path(run_dir).resolve()),
        "rules":["GC-08","GC-15","GC-16","GC-17"],
        "harvest_counts":{str(d):len(bank[d]) for d in cuts},
        "harvest_errors":errors,
        "started_realtime":time.time(),"boot_id":boot_id(),
    }
    atomic(out/"MANIFEST.json",manifest)
    for d in cuts:
        for h,rec in bank[d].items():
            base_file(out,d,h,rec)

    deadline=time.time()+cfg["campaign_wall_seconds"]
    best=cfg["known_best_depth"]; all_results=[]
    for cut in cuts:
        if time.time()+cfg["shutdown_reserve_seconds"]>=deadline:
            break
        items=list(bank[cut].items())
        if not items:
            continue
        jobs=[]
        with ThreadPoolExecutor(max_workers=cfg["workers"]) as ex:
            for h,rec in items:
                bf=base_file(out,cut,h,rec)
                jobs.append(ex.submit(climb,bf,cut,h,cfg,out,deadline))
            pending=set(jobs); done_n=0; unknown=0; last=0
            while pending:
                finished,pending=wait(
                    pending,timeout=min(cfg["status_seconds"],30),
                    return_when=FIRST_COMPLETED)
                for f in finished:
                    r=f.result(); all_results.append(r); done_n+=1
                    best=max(best,r["best"])
                    unknown+=int(r["status"] in (
                        "TASK_TIMEOUT_UNKNOWN","LIMIT_UNRESOLVED",
                        "TASK_ERROR","CAMPAIGN_TIME_RESERVE"))
                    if r["best"]>cfg["known_best_depth"]:
                        atomic(out/"BEST.json",r)
                if time.time()-last>=cfg["status_seconds"]:
                    heartbeat(out,cut,best,done_n,len(jobs),unknown); last=time.time()
        atomic(out/"PROGRESS.json",{"best_depth":best,"results":all_results,
                                    "last_completed_cut":cut})
    status="TIME_BUDGET" if time.time()+cfg["shutdown_reserve_seconds"]>=deadline else "DONE"
    atomic(out/"SUMMARY.json",{
        "status":status,"best_depth":best,"results":all_results,
        "harvest_counts":manifest["harvest_counts"],"finished_realtime":time.time()})
    heartbeat(out,"end",best,len(all_results),len(all_results),
              sum(r["status"] in ("TASK_TIMEOUT_UNKNOWN","LIMIT_UNRESOLVED","TASK_ERROR")
                  for r in all_results))

def selftest():
    cfg0={"alternatives_per_node":16,"node_limit_initial":250000,
          "node_limit_max":1000000,"solution_scan_initial":512,
          "solution_scan_max":4096,"adaptive_rounds":3,"adaptive_factor":4}
    p=()
    for i in range(3):
        aa,_=row_alternatives(p,12345+i,cfg0,"random")
        if not aa: raise SystemExit("selftest construction failed")
        p=p+(aa[0],)
    check(p)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); run_dir=root/"run"; out=root/"out"
        run_dir.mkdir()
        atomic(run_dir/"checkpoint_00.json",
               {"best":[hex(x) for x in p],"prefix":[hex(x) for x in p]})
        bank,errors=harvest(run_dir,[2])
        if errors or len(bank[2])!=1:
            raise SystemExit("selftest harvest failed")
        h,rec=next(iter(bank[2].items())); bf=base_file(out,2,h,rec)
        cfg={"node_limit":2000000,"solution_limit":4096,"seed":99}
        r=run_probe(bf,2,3,cfg,out/"result.json",60)
        if r.get("status")!="FOUND_DEPTH3":
            raise SystemExit(f"selftest probe failed: {r}")
    print(json.dumps({"status":"PASS","depth":3,"sha256":digest(p)}))

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("selftest")
    r=sp.add_parser("run"); r.add_argument("config"); r.add_argument("outdir"); r.add_argument("source_run_dir")
    a=ap.parse_args()
    selftest() if a.cmd=="selftest" else run(a.config,a.outdir,a.source_run_dir)

if __name__=="__main__":
    main()
