
from __future__ import annotations
import argparse, hashlib, json, shutil, time, zipfile
from pathlib import Path

STAR_IDS = ["1159","1377","1425","1488","1528","1756","1873","1943","2194","2286","2500","2557"]
NORMAL = {"1159","2286"}
LRAT_MARKER = "c VERIFIED"
CAKE_MARKER = "s VERIFIED UNSAT"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def record_star(base,pid):
    cnf=base/"star_round_1"/"v4_09232"/f"profile_{pid}.cnf"
    cert=base/"certify_v4_09232"/"stars"/f"profile_{pid}"
    if pid in NORMAL:
        proof=cert/"proof.lrat"; lo=cert/"lrat.out"; co=cert/"cake.out"
        mode="cadical_lrat"
    else:
        proof=cert/"proof_rootup.lrat"; lo=cert/"lrat_rootup.out"; co=cert/"cake_rootup.out"
        mode="root_up_lrat"
    for p in (cnf,proof,lo,co):
        if not p.exists(): raise RuntimeError(f"missing {p}")
    if LRAT_MARKER not in lo.read_text(errors="replace"):
        raise RuntimeError(f"LRAT marker missing for {pid}")
    if CAKE_MARKER not in co.read_text(errors="replace"):
        raise RuntimeError(f"Cake marker missing for {pid}")
    return {
        "kind":"star","profile_id":int(pid),"mode":mode,
        "cnf_sha256":sha(cnf),"cnf_bytes":cnf.stat().st_size,
        "proof_sha256":sha(proof),"proof_bytes":proof.stat().st_size,
        "lrat_verified":True,"cake_verified":True,
        "cnf_path":str(cnf),"proof_path":str(proof),
        "log_dir":str(cert),
    }

def record_global(base):
    cnf=base/"global_rescout"/"v4_09232"/"model.cnf"
    cert=base/"certify_v4_09232"/"global_v4_09232"
    proof=cert/"proof.lrat"; lo=cert/"lrat.out"; co=cert/"cake.out"
    for p in (cnf,proof,lo,co):
        if not p.exists(): raise RuntimeError(f"missing {p}")
    if LRAT_MARKER not in lo.read_text(errors="replace"):
        raise RuntimeError("global LRAT marker missing")
    if CAKE_MARKER not in co.read_text(errors="replace"):
        raise RuntimeError("global Cake marker missing")
    return {
        "kind":"global","id":"v4_09232",
        "cnf_sha256":sha(cnf),"cnf_bytes":cnf.stat().st_size,
        "proof_sha256":sha(proof),"proof_bytes":proof.stat().st_size,
        "lrat_verified":True,"cake_verified":True,
        "cnf_path":str(cnf),"proof_path":str(proof),
        "log_dir":str(cert),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    args=ap.parse_args()
    run=Path(args.run_dir)
    base=run/"neighbor_star_preflight_20260909"
    records=[record_star(base,p) for p in STAR_IDS]+[record_global(base)]
    assert len(records)==13 and all(r["lrat_verified"] and r["cake_verified"] for r in records)

    manifest={
        "format":"CONWAY99-K66-V4-09232-NEIGHBORSTAR-HANDOFF-1",
        "case":"v4_09232",
        "certified_obligations":13,
        "star_obligations":12,
        "global_obligations":1,
        "claim_scope":"Twelve locally impossible profiles and the resulting reduced global profile-conflict model are LRAT+Cake certified UNSAT. Promotion to V4 exclusion requires the necessity/encoder audit for the star and global models.",
        "total_proof_bytes":sum(r["proof_bytes"] for r in records),
        "records":records,
    }
    outdir=base/"certify_v4_09232"
    mp=outdir/"handoff_manifest.json"
    mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    stamp=time.strftime("%Y%m%d_%H%M%S")
    zp=outdir/f"k66_v4_09232_neighborstar_handoff_{stamp}.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(mp,"handoff_manifest.json")
        for r in records:
            logdir=Path(r["log_dir"])
            prefix=("star_"+str(r["profile_id"])) if r["kind"]=="star" else "global_v4_09232"
            names=["cadical.out","cadical.err","lrat.out","lrat.err","cake.out","cake.err",
                   "lrat_rootup.out","lrat_rootup.err","cake_rootup.out","cake_rootup.err"]
            for n in names:
                p=logdir/n
                if p.exists(): z.write(p,f"{prefix}/{n}")
    win=Path("/mnt/c/Users/rb/Downloads")/zp.name
    shutil.copy2(zp,win)
    print("K66_09232_HANDOFF_OK",win)
    print("MANIFEST_SHA256",sha(mp))
    print("ZIP_SHA256",sha(zp))
    print("TOTAL_PROOF_GIB",f"{manifest['total_proof_bytes']/1024**3:.3f}")

if __name__=="__main__":
    main()
