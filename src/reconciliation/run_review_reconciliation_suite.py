#!/usr/bin/env python3
"""Autonomous local reconciliation suite for O3_REVIEW_RECONCILED_20260907."""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

def read_json(p):
    try:return json.loads(Path(p).read_text())
    except Exception:return None

def run(cmd):
    print("EXEC", " ".join(map(str,cmd)), flush=True)
    return subprocess.run(list(map(str,cmd))).returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=str(Path.home()/"conway99_workspace/o3_reconciliation_runs/review_reconciled_20260907"))
    ap.add_argument("--workers",type=int,default=6)
    args=ap.parse_args()
    repo=Path(__file__).resolve().parents[2]
    root=Path(args.root).expanduser(); root.mkdir(parents=True,exist_ok=True)
    statep=root/"suite_state.json"
    state=read_json(statep) or {"format":"CONWAY99-O3-RECONCILIATION-SUITE-1","started_at":time.time(),"phases":{}}
    def save():statep.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print("=== O3 REVIEW RECONCILIATION SUITE ===",flush=True)
    print("Phase 1 tau27 exact regression: expected <1 minute.",flush=True)
    print("Phase 2 T-skeleton certified classification: expected 2-20 min; conservative <2 h.",flush=True)
    print("Phase 3 fixed-K3 quotient certification: optimistic <1 h, working expectation 1-8 h; conservative up to 50 h.",flush=True)
    print("Phase 3 has no wallclock timeout; automatic status every 10 minutes and a 75 GiB disk safety floor.",flush=True)
    print(f"run_root={root}",flush=True)

    p1=root/"tau27"; p1.mkdir(exist_ok=True); r1=read_json(p1/"result.json")
    if not (r1 and r1.get("pass")):
        rc=run([sys.executable,repo/"src/reconciliation/o3_tau27_lift_check.py","--out",p1/"result.json"])
        if rc:raise SystemExit(f"tau27 checker failed rc={rc}")
        r1=read_json(p1/"result.json")
    state["phases"]["tau27"]={"status":"PASS" if r1 and r1.get("pass") else "FAIL","result":str(p1/"result.json")}; save()
    if state["phases"]["tau27"]["status"]!="PASS":raise SystemExit("tau27 phase failed")
    print("PHASE1_PASS",flush=True)

    p2=root/"t_skeleton"; p2.mkdir(exist_ok=True); s2=read_json(p2/"summary.json")
    if not (s2 and s2.get("complete")):
        rc=run([sys.executable,repo/"src/reconciliation/o3_t_skeleton_certify.py","--out",p2,"--run","--run-dir",p2/"jobs","--workers",str(args.workers),"--status-seconds","600"])
        if rc:raise SystemExit(f"T-skeleton phase failed rc={rc}")
        s2=read_json(p2/"summary.json")
    state["phases"]["t_skeleton"]={"status":"PASS" if s2 and s2.get("complete") else "FAIL","summary":s2}; save()
    if state["phases"]["t_skeleton"]["status"]!="PASS":raise SystemExit("T-skeleton phase incomplete")
    print("PHASE2_PASS",json.dumps(s2,sort_keys=True),flush=True)

    p3=root/"fixed_triangle"; p3.mkdir(exist_ok=True); r3=read_json(p3/"result.json"); final={"UNSAT_CERTIFIED","SAT_QUOTIENT_VERIFIED"}
    if not (r3 and r3.get("status") in final):
        du=shutil.disk_usage(root)
        if du.free<100*1024**3:raise SystemExit(f"fixed-triangle phase not admitted: only {du.free/1024**3:.1f} GiB free (<100 GiB)")
        rc=run([sys.executable,repo/"src/reconciliation/o3_fixed_triangle_certify.py","--out",p3,"--run","--run-dir",p3/"job","--status-seconds","600"])
        if rc:raise SystemExit(f"fixed-triangle phase failed rc={rc}")
        r3=read_json(p3/"result.json")
    st=r3.get("status") if r3 else "MISSING"
    state["phases"]["fixed_triangle"]={"status":st,"result":r3}; state["ended_at"]=time.time(); save()
    print("PHASE3_RESULT",json.dumps(r3,sort_keys=True),flush=True)
    if st=="UNSAT_CERTIFIED":print("=== SUITE_PASS: O3 fixed-K3 quotient is certified UNSAT ===",flush=True)
    elif st=="SAT_QUOTIENT_VERIFIED":print("=== SUITE_COMPLETE_WITH_SAT_QUOTIENT: inspect witness; FPF cannot be promoted ===",flush=True)
    else:print(f"=== SUITE_PARTIAL: fixed-triangle status {st} ===",flush=True)

if __name__=="__main__":main()
