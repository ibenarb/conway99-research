
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, os, shutil, subprocess, time, zipfile
from pathlib import Path

CADICAL_SHA = "d24720982bdd81989212ba786e3005b2e6f481101967a250d4bfdd69973d8fad"
LRAT_SHA = "49f0bf5b418fec38dad3a199a9ae7eb52a4617269a6d360d49d3f580a9b98dfa"
CAKE_SHA = "e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a"
CAKE_MARKER = b"s VERIFIED UNSAT"
LRAT_MARKER = "c VERIFIED"

EXPECTED_STAR_NAMES = [
    "profile_1159.cnf","profile_1377.cnf","profile_1425.cnf","profile_1488.cnf",
    "profile_1528.cnf","profile_1756.cnf","profile_1873.cnf","profile_1943.cnf",
    "profile_2194.cnf","profile_2286.cnf","profile_2500.cnf","profile_2557.cnf",
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def mem_available_gib():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1024**2
    return -1.0

def atomic_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)

def solve_one(name, cnf, cert_dir, cadical):
    cert_dir.mkdir(parents=True, exist_ok=True)
    proof = cert_dir / "proof.lrat"
    witness = cert_dir / "witness.out"
    stdout = cert_dir / "cadical.out"
    stderr = cert_dir / "cadical.err"
    for p in (proof, witness, stdout, stderr, cert_dir/"lrat.out", cert_dir/"lrat.err",
              cert_dir/"cake.out", cert_dir/"cake.err"):
        if p.exists():
            p.unlink()
    start = time.time()
    with open(stdout, "wb") as o, open(stderr, "wb") as e:
        rc = subprocess.run(
            [cadical, "--lrat", "--no-binary", "-w", str(witness), str(cnf), str(proof)],
            stdout=o, stderr=e
        ).returncode
    return {
        "name": name,
        "cnf": str(cnf),
        "cert_dir": str(cert_dir),
        "solver_exit": rc,
        "solver_wall": time.time() - start,
        "cnf_sha256": sha256(cnf),
        "proof_bytes": proof.stat().st_size if proof.exists() else 0,
        "proof_sha256": sha256(proof) if proof.exists() else None,
    }

def verify_one(rec, lrat, cake, disk_floor):
    cnf = Path(rec["cnf"])
    cert_dir = Path(rec["cert_dir"])
    proof = cert_dir / "proof.lrat"
    if rec["solver_exit"] != 20:
        rec["status"] = "SOLVER_NOT_UNSAT"
        return rec

    free = shutil.disk_usage(cert_dir).free / 1024**3
    if free < disk_floor:
        rec["status"] = "DISK_FLOOR_BEFORE_CHECK"
        return rec

    lo, le = cert_dir/"lrat.out", cert_dir/"lrat.err"
    start = time.time()
    with open(lo, "wb") as o, open(le, "wb") as e:
        lrc = subprocess.run([lrat, str(cnf), str(proof)], stdout=o, stderr=e).returncode
    ltxt = lo.read_text(errors="replace")
    rec.update({
        "lrat_exit": lrc,
        "lrat_wall": time.time() - start,
        "lrat_positive_marker": LRAT_MARKER in ltxt,
    })
    if lrc != 0 or LRAT_MARKER not in ltxt:
        rec["status"] = "LRAT_FAILED"
        return rec

    avail = mem_available_gib()
    rec["mem_available_before_cake_gib"] = avail
    if avail >= 0 and avail < 8:
        rec["status"] = "CAKE_DEFERRED_LOW_RAM"
        return rec

    co, ce = cert_dir/"cake.out", cert_dir/"cake.err"
    start = time.time()
    with open(co, "wb") as o, open(ce, "wb") as e:
        crc = subprocess.run([cake, str(cnf), str(proof)], stdout=o, stderr=e).returncode
    marker = CAKE_MARKER in co.read_bytes()
    rec.update({
        "cake_exit": crc,
        "cake_wall": time.time() - start,
        "cake_positive_marker": marker,
    })
    rec["status"] = "UNSAT_CERTIFIED_MODEL" if crc == 0 and marker else "CAKE_FAILED"
    return rec

def make_handoff(outdir, summary):
    stamp = time.strftime("%Y%m%d_%H%M%S")
    zip_path = outdir / f"k66_09232_neighborstar_cert13_handoff_{stamp}.zip"
    manifest = outdir / "cert13_manifest.json"
    atomic_json(manifest, summary)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(manifest, "cert13_manifest.json")
        for rec in summary["records"]:
            cert = Path(rec["cert_dir"])
            prefix = rec["name"].replace(".cnf", "")
            for fn in ("cadical.out","cadical.err","lrat.out","lrat.err","cake.out","cake.err"):
                p = cert/fn
                if p.exists():
                    z.write(p, f"{prefix}/{fn}")
    windows = Path("/mnt/c/Users/rb/Downloads") / zip_path.name
    shutil.copy2(zip_path, windows)
    return manifest, zip_path, windows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--disk-floor-gib", type=float, default=75)
    ap.add_argument("--cadical", default=str(Path.home()/".local/bin/cadical"))
    ap.add_argument("--lrat-check", default=str(Path.home()/".local/bin/lrat-check"))
    ap.add_argument("--cake", default=str(Path.home()/"conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr"))
    a = ap.parse_args()

    run = Path(a.run_dir)
    base = run/"neighbor_star_preflight_20260909"
    star_dir = base/"star_round_1"/"v4_09232"
    global_cnf = base/"global_rescout"/"v4_09232"/"model.cnf"
    outdir = base/"certify_v4_09232"
    outdir.mkdir(exist_ok=True)

    tools = [
        (Path(a.cadical), CADICAL_SHA, "cadical"),
        (Path(a.lrat_check), LRAT_SHA, "lrat-check"),
        (Path(a.cake), CAKE_SHA, "cake_lpr"),
    ]
    for p, expected, name in tools:
        if not p.exists():
            raise SystemExit(f"missing {name}: {p}")
        got = sha256(p)
        if got != expected:
            raise SystemExit(f"{name} hash mismatch: {got}")

    found = sorted(p.name for p in star_dir.glob("profile_*.cnf"))
    if found != EXPECTED_STAR_NAMES:
        raise SystemExit(f"star CNF inventory mismatch: {found}")
    if not global_cnf.exists():
        raise SystemExit(f"missing global CNF: {global_cnf}")

    free = shutil.disk_usage(outdir).free / 1024**3
    if free < 100:
        raise SystemExit(f"admission refused: disk free {free:.1f} GiB")

    print("K66_09232_CERT13_START stars=12 global=1 timeouts=NONE", flush=True)
    print(f"disk_free={free:.1f}GiB mem_available={mem_available_gib():.1f}GiB", flush=True)

    workers = max(1, min(int(a.workers), 12))
    star_records = []
    print(f"STAR_SOLVE_PHASE workers={workers}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        for name in EXPECTED_STAR_NAMES:
            cnf = star_dir/name
            cert = outdir/"stars"/name.replace(".cnf","")
            futs[ex.submit(solve_one, name, cnf, cert, a.cadical)] = name
        for f in cf.as_completed(futs):
            rec = f.result()
            star_records.append(rec)
            print(
                f"STAR_SOLVER_DONE {rec['name']} exit={rec['solver_exit']} "
                f"wall={rec['solver_wall']:.2f}s proof={rec['proof_bytes']/1024**2:.1f}MiB",
                flush=True
            )

    star_records.sort(key=lambda r: r["name"])
    if any(r["solver_exit"] != 20 for r in star_records):
        raise SystemExit("not all star CNFs solved UNSAT; no checker phase started")

    print("STAR_CHECKER_PHASE serial", flush=True)
    for i, rec in enumerate(star_records):
        star_records[i] = verify_one(rec, a.lrat_check, a.cake, a.disk_floor_gib)
        r = star_records[i]
        print(
            f"STAR_CHECK_DONE {r['name']} status={r['status']} "
            f"lrat={r.get('lrat_exit')} cake={r.get('cake_exit')} "
            f"marker={r.get('cake_positive_marker')}",
            flush=True
        )
    if any(r["status"] != "UNSAT_CERTIFIED_MODEL" for r in star_records):
        raise SystemExit("star certification incomplete; global certification not started")

    print("GLOBAL_CERT_START v4_09232", flush=True)
    global_rec = solve_one(
        "global_v4_09232.cnf",
        global_cnf,
        outdir/"global_v4_09232",
        a.cadical
    )
    print(
        f"GLOBAL_SOLVER_DONE exit={global_rec['solver_exit']} "
        f"wall={global_rec['solver_wall']:.2f}s "
        f"proof={global_rec['proof_bytes']/1024**3:.2f}GiB",
        flush=True
    )
    global_rec = verify_one(global_rec, a.lrat_check, a.cake, a.disk_floor_gib)
    print(
        f"GLOBAL_CHECK_DONE status={global_rec['status']} "
        f"lrat={global_rec.get('lrat_exit')} cake={global_rec.get('cake_exit')} "
        f"marker={global_rec.get('cake_positive_marker')}",
        flush=True
    )

    records = star_records + [global_rec]
    certified = sum(r["status"] == "UNSAT_CERTIFIED_MODEL" for r in records)
    summary = {
        "format": "CONWAY99-K66-V4-09232-NEIGHBORSTAR-CERT13-1",
        "claim_scope": (
            "12 local neighbor-star CNFs and the reduced global profile-conflict CNF "
            "are LRAT+Cake certified UNSAT. Promotion to exclusion of v4_09232 also "
            "requires the necessity/encoder audit linking the certified star eliminations "
            "to the reduced global model."
        ),
        "tool_hashes": {
            "cadical": CADICAL_SHA,
            "lrat-check": LRAT_SHA,
            "cake_lpr": CAKE_SHA,
        },
        "certified_count": certified,
        "star_certified_count": sum(r["status"] == "UNSAT_CERTIFIED_MODEL" for r in star_records),
        "global_certified": global_rec["status"] == "UNSAT_CERTIFIED_MODEL",
        "records": records,
    }
    manifest, handoff, windows = make_handoff(outdir, summary)
    print(f"K66_09232_CERT13_DONE certified={certified}/13", flush=True)
    print("MANIFEST_SHA256", sha256(manifest), flush=True)
    print("HANDOFF_SHA256", sha256(handoff), flush=True)
    print("HANDOFF_WINDOWS", windows, flush=True)

if __name__ == "__main__":
    main()
