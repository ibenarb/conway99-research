#!/usr/bin/env python3
import argparse, hashlib, json, os, re, signal, statistics, subprocess, time
from pathlib import Path

CPU10=[0,2,4,6,8,10,12,14,16,18]
CPU20=list(range(20))
SEQUENCE=[("10a",10),("20a",20),("20b",20),("10b",10)]

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(8<<20),b""):
            h.update(b)
    return h.hexdigest()

def parse_stats(path):
    out={"conflicts":0,"decisions":0,"propagations":0}
    pats={k:re.compile(r"^c %s:\s*([0-9][0-9,]*)\b"%k,re.I) for k in out}
    text=Path(path).read_text(errors="replace") if Path(path).exists() else ""
    for line in text.splitlines():
        for k,p in pats.items():
            m=p.match(line)
            if m:
                out[k]=int(m.group(1).replace(",",""))
    status="UNKNOWN"
    if re.search(r"^s\s+UNSATISFIABLE\b",text,re.M): status="UNSAT"
    elif re.search(r"^s\s+SATISFIABLE\b",text,re.M): status="SAT"
    return out,status

def validate_topology():
    pairs=[]
    for c in range(0,24,2):
        ids=[]
        for cpu in (c,c+1):
            p=Path(f"/sys/devices/system/cpu/cpu{cpu}/topology/core_id")
            if not p.exists(): raise RuntimeError(f"missing topology for cpu {cpu}")
            ids.append(p.read_text().strip())
        if ids[0]!=ids[1]:
            raise RuntimeError(f"expected SMT siblings {c},{c+1}, got {ids}")
        pairs.append((c,c+1,ids[0]))
    if len({x[2] for x in pairs})!=12:
        raise RuntimeError("expected 12 distinct physical cores")
    return pairs

def kill_proc(p):
    if p.poll() is not None: return
    try: os.killpg(p.pid,signal.SIGTERM)
    except ProcessLookupError: return
    try: p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        p.wait()

def run_wave(label,wave_no,jobs,cpus,solver,timeout,watchdog,outdir):
    started=time.time(); running=[]
    for rec,cpu in zip(jobs,cpus):
        log=outdir/f"{rec['rank']:02d}_{rec['job_id']}.log"
        cmd=["taskset","-c",str(cpu),solver,"-t",str(timeout),f"--seed={rec['seed']}","--stats",rec["path"]]
        f=open(log,"w")
        p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        running.append({"rec":rec,"cpu":cpu,"log":log,"file":f,"proc":p,"start":time.time()})
    last=-60
    while True:
        alive=[x for x in running if x["proc"].poll() is None]
        elapsed=time.time()-started
        if elapsed-last>=60 or not alive:
            print(f"[{now_iso()}] {label} wave={wave_no} elapsed={elapsed:.1f}s alive={len(alive)}/{len(running)}",flush=True)
            last=elapsed
        for x in alive:
            if time.time()-x["start"]>watchdog: kill_proc(x["proc"])
        if not alive: break
        time.sleep(1)
    results=[]
    for x in running:
        x["file"].close()
        st,status=parse_stats(x["log"])
        results.append({"rank":x["rec"]["rank"],"job_id":x["rec"]["job_id"],"seed":x["rec"]["seed"],
                        "cpu":x["cpu"],"cnf_sha256":x["rec"]["cnf_sha256"],"returncode":x["proc"].returncode,
                        "status":status,"elapsed_seconds":time.time()-x["start"],**st})
    return results,time.time()-started

def run_mode(label,width,panel,solver,timeout,watchdog,root):
    outdir=root/label; outdir.mkdir(parents=True,exist_ok=False)
    t0=time.time(); allr=[]; wavewalls=[]
    waves=[panel[:10],panel[10:]] if width==10 else [panel]
    cpus=CPU10 if width==10 else CPU20
    for i,jobs in enumerate(waves,1):
        r,w=run_wave(label,i,jobs,cpus[:len(jobs)],solver,timeout,watchdog,outdir)
        allr.extend(r); wavewalls.append(w)
    wall=time.time()-t0
    totals={k:sum(x[k] for x in allr) for k in ("conflicts","decisions","propagations")}
    statuses={}
    for x in allr: statuses[x["status"]]=statuses.get(x["status"],0)+1
    summary={"label":label,"width":width,"wall_seconds":wall,"wave_wall_seconds":wavewalls,
             "results":allr,"totals":totals,"statuses":statuses}
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(f"MODE_DONE {label} width={width} wall={wall:.2f}s totals={totals} statuses={statuses}",flush=True)
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--solver",default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--timeout",type=int,default=300)
    ap.add_argument("--watchdog",type=int,default=330)
    args=ap.parse_args()
    manifest=Path(args.manifest).resolve(); root=Path(args.out_dir).resolve()
    solver=str(Path(args.solver).resolve())
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"refusing non-empty output dir: {root}")
    root.mkdir(parents=True,exist_ok=True)
    pairs=validate_topology()
    panel=json.loads(manifest.read_text())
    if len(panel)!=20: raise RuntimeError(f"expected 20 jobs, got {len(panel)}")
    for rec in panel:
        got=sha256_file(rec["path"])
        if got!=rec["cnf_sha256"]:
            raise RuntimeError(f"CNF hash mismatch {rec['job_id']}: {got} != {rec['cnf_sha256']}")
    meta={"created_at":now_iso(),"manifest":str(manifest),"manifest_sha256":sha256_file(manifest),
          "solver":solver,"solver_sha256":sha256_file(solver),"timeout":args.timeout,"watchdog":args.watchdog,
          "cpu10":CPU10,"cpu20":CPU20,"reserved_cpus":[20,21,22,23],"topology_pairs":pairs,"sequence":SEQUENCE}
    (root/"benchmark_meta.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    print("SMT_PREFLIGHT_PASS",flush=True)
    print("SEQUENCE",SEQUENCE,flush=True)
    print("CPU10",CPU10,"CPU20",CPU20,"RESERVED",[20,21,22,23],flush=True)
    print("MANIFEST_SHA256",meta["manifest_sha256"],flush=True)
    summaries=[run_mode(label,width,panel,solver,args.timeout,args.watchdog,root) for label,width in SEQUENCE]
    report={"runs":[]}
    for s in summaries:
        t=s["totals"]; wall=s["wall_seconds"]
        report["runs"].append({"label":s["label"],"width":s["width"],"wall_seconds":wall,
                               "conflicts":t["conflicts"],"decisions":t["decisions"],"propagations":t["propagations"],
                               "conflicts_per_wall_s":t["conflicts"]/wall,
                               "decisions_per_wall_s":t["decisions"]/wall,
                               "propagations_per_wall_s":t["propagations"]/wall,
                               "statuses":s["statuses"]})
    def mean_metric(width,key):
        return statistics.mean(r[key] for r in report["runs"] if r["width"]==width)
    report["throughput_gain_20_over_10"]={key:mean_metric(20,key)/mean_metric(10,key)-1
        for key in ("conflicts_per_wall_s","decisions_per_wall_s","propagations_per_wall_s")}
    (root/"FINAL_REPORT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SMT_BENCHMARK_COMPLETE",flush=True)
    print(json.dumps(report["throughput_gain_20_over_10"],sort_keys=True),flush=True)
    print("FINAL_REPORT",root/"FINAL_REPORT.json",flush=True)

if __name__=="__main__":
    main()
