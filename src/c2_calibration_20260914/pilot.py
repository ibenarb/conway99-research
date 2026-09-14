"""C2 portfolio 1.1.0: eleven seeds, resource limits, timed observation points."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from c2_reference import CNF, Frame, read_primary_model, reconstruct, verify_graph

CNF_HASH = "f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba"
CAKE_HASH = "e63d772e463265d26ace5f52125506024126b36c4a34901e2ed61c4378742d0a"
REF_HASH = "3a88f356831a4f955c79639bfe86aac5eea2a80febdd676cbd1009e86f1e9b29"
DEFAULT_INPUT = "/home/rb/conway99_workspace/c2_reference_v1/prepare_20260913_160812_780017/k14/baseline.cnf"
DEFAULT_CAKE = "/home/rb/conway99_workspace/o3_reconciliation_runs/k66_v4_cert_20260908_231256_132359/tools/cake_lpr"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for b in iter(lambda: stream.read(1024**2), b""):
            h.update(b)
    return h.hexdigest()


def save(path, value):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def memory_gib():
    fields = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
    return int(fields["MemAvailable"].split()[0]) / 1024**2


def resource_reason(out, floor=75):
    if shutil.disk_usage(out).free / 1024**3 < floor:
        return "DISK_FREE_BELOW_75_GIB"
    if memory_gib() < 2:
        return "MEM_AVAILABLE_BELOW_2_GIB"
    return None


def tail(path, size=16384):
    with Path(path).open("rb") as f:
        f.seek(max(0, f.seek(0, 2) - size))
        return f.read().decode(errors="replace")


def stop(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def accepted(code, stdout, stderr):
    return code == 0 and stdout.strip() == "s VERIFIED UNSAT" and not stderr.strip()


def classify(code, log):
    lines = set(log.splitlines())
    if code == 20 and "s UNSATISFIABLE" in lines:
        return "UNSAT_PENDING_CHECK"
    if code == 10 and "s SATISFIABLE" in lines:
        return "SAT_PENDING_CHECK"
    if code == 0 and "s SATISFIABLE" not in lines and "s UNSATISFIABLE" not in lines:
        return "TIMEOUT_OPEN"
    return "SOLVER_ERROR"


def command(solver, cnf, proof, seconds, seed):
    budget = ["-t", str(seconds)] if seconds else []
    return [str(solver), "--lrat", "--no-binary", "--seed=" + str(seed)] + budget + [str(cnf), str(proof)]


def controls(solver, cake, out):
    folder = out / "controls"
    folder.mkdir()
    cnf, sat_cnf, proof = folder / "unsat.cnf", folder / "sat.cnf", folder / "proof.lrat"
    cnf.write_text("p cnf 1 2\n1 0\n-1 0\n")
    sat_cnf.write_text("p cnf 1 1\n1 0\n")
    cmd = command(solver, cnf, proof, 30, 0)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    (folder / "solver.log").write_text(r.stdout + r.stderr)
    if r.returncode != 20 or not proof.exists() or not proof.stat().st_size:
        raise RuntimeError("CaDiCaL LRAT control failed")
    good = subprocess.run([str(cake), str(cnf), str(proof)], capture_output=True, text=True, timeout=60)
    bad = subprocess.run([str(cake), str(sat_cnf), str(proof)], capture_output=True, text=True, timeout=60)
    record = {"solver_command": cmd, "solver_exit": r.returncode,
              "positive": {"exit": good.returncode, "stdout": good.stdout, "stderr": good.stderr},
              "negative": {"exit": bad.returncode, "stdout": bad.stdout, "stderr": bad.stderr}}
    save(folder / "result.json", record)
    if not accepted(good.returncode, good.stdout, good.stderr):
        raise RuntimeError("Cake positive control failed")
    if accepted(bad.returncode, bad.stdout, bad.stderr):
        raise RuntimeError("Cake incorrectly accepted UNSAT for satisfiable control")


def check_proof(cake, cnf, proof, folder, out):
    before = sha(proof)
    if sha(cnf) != CNF_HASH:
        raise RuntimeError("CNF changed before verification")
    start, last = time.monotonic(), 0.0
    with (folder / "cake.stdout").open("w") as stdout, (folder / "cake.stderr").open("w") as stderr:
        proc = subprocess.Popen([str(cake), str(cnf), str(proof)], stdout=stdout, stderr=stderr)
        try:
            while proc.poll() is None:
                reason = resource_reason(out)
                if reason:
                    stop(proc)
                    return {"status": "CHECK_RESOURCE_STOP", "reason": reason, "proof_sha256": before}
                now = time.monotonic()
                if now - last >= 600:
                    status = {"phase": "CAKE_CHECK", "elapsed_seconds": round(now-start),
                              "ETA": "unknown; no checker wall-time limit", "job": folder.name}
                    save(out / "status.json", status)
                    print("STATUS " + json.dumps(status), flush=True)
                    last = now
                time.sleep(2)
        finally:
            stop(proc)
    stdout = (folder / "cake.stdout").read_text()
    stderr = (folder / "cake.stderr").read_text()
    unchanged = sha(proof) == before and sha(cnf) == CNF_HASH
    ok = unchanged and accepted(proc.returncode, stdout, stderr)
    return {"status": "UNSAT_CERTIFIED" if ok else "CHECK_FAILED", "exit": proc.returncode,
            "stdout": stdout, "stderr": stderr, "proof_sha256": before,
            "proof_bytes": proof.stat().st_size, "cnf_sha256": CNF_HASH,
            "input_unchanged": unchanged, "seconds": round(time.monotonic()-start, 2)}


def run(args):
    out = args.out.resolve()
    solver, cake, source = Path(args.solver).resolve(), Path(args.cake).resolve(), Path(args.cnf).resolve()
    if sha(source) != CNF_HASH or sha(cake) != CAKE_HASH:
        raise RuntimeError("Pinned CNF or Cake hash mismatch")
    if sha(Path(__file__).with_name("c2_reference.py")) != REF_HASH:
        raise RuntimeError("Reference checker hash mismatch")
    if resource_reason(out):
        raise RuntimeError("Insufficient current resources: " + str(resource_reason(out)))
    version = subprocess.check_output([str(solver), "--version"], text=True, timeout=15).strip()
    if version != "2.2.1":
        raise RuntimeError("Unexpected CaDiCaL version: " + version)
    cnf = out / "baseline.cnf"
    shutil.copyfile(source, cnf)
    if sha(cnf) != CNF_HASH:
        raise RuntimeError("CNF copy mismatch")
    save(out / "inputs.json", {"cnf_sha256": CNF_HASH, "source": str(source),
         "solver": str(solver), "solver_sha256": sha(solver), "solver_version": version,
         "cake": str(cake), "cake_sha256": CAKE_HASH, "controller_sha256": sha(__file__),
         "reference_sha256": REF_HASH, "seconds_per_seed": args.seconds,
         "seeds": list(range(getattr(args, "workers", 4))), "workers": getattr(args, "workers", 4), "scope": "Distinct seeds on the same complete CNF; no case partition"})
    controls(solver, cake, out)
    records, active = [], []
    checkpoints = set()
    start, last = time.monotonic(), 0.0
    stop_reason = None
    try:
        for seed in range(getattr(args, "workers", 4)):
            folder = out / ("seed_" + str(seed))
            folder.mkdir()
            logfile = (folder / "solver.log").open("w")
            cmd = command(solver, cnf, folder / "proof.lrat", args.seconds, seed)
            proc = subprocess.Popen(cmd, stdout=logfile, stderr=subprocess.STDOUT)
            record = {"seed": seed, "status": "RUNNING", "command": cmd, "pid": proc.pid}
            records.append(record)
            active.append((proc, logfile, folder, record, time.monotonic()))
        save(out / "jobs.json", records)
        while active:
            now = time.monotonic()
            stop_reason = resource_reason(out)
            if stop_reason:
                break
            terminal = False
            for item in active[:]:
                proc, logfile, folder, record, begun = item
                if args.seconds and proc.poll() is None and now - begun > args.seconds + 60:
                    stop(proc)
                    record["status"] = "WATCHDOG_TIMEOUT_OPEN"
                if proc.poll() is not None:
                    logfile.close()
                    if record["status"] == "RUNNING":
                        with (folder / "solver.log").open() as log_input:
                            verdict = "".join(line for line in log_input if line.startswith("s "))
                        record["status"] = classify(proc.returncode, verdict)
                    record.update(exit=proc.returncode, seconds=round(now-begun, 2),
                                  solver_statistics_tail=tail(folder / "solver.log"))
                    active.remove(item)
                    save(folder / "result.json", record)
                    if record["status"] in ("UNSAT_PENDING_CHECK", "SAT_PENDING_CHECK", "SOLVER_ERROR"):
                        terminal = True
            status = {"phase": "SEARCH", "elapsed_seconds": round(now-start),
                      "ETA_search_seconds": max(0, round(args.seconds-(now-start))) if args.seconds else None,
                      "ETA_note": "no fixed search limit; 1h and 2h observation points",
                      "states": {str(r["seed"]): r["status"] for r in records},
                      "free_disk_GiB": round(shutil.disk_usage(out).free/1024**3, 1),
                      "available_RAM_GiB": round(memory_gib(), 1),
                      "proof_GiB": {str(r["seed"]): round((out/("seed_"+str(r["seed"]))/"proof.lrat").stat().st_size/1024**3, 3)
                                    for r in records if (out/("seed_"+str(r["seed"]))/"proof.lrat").exists()}}
            save(out / "status.json", status)
            for checkpoint in (3600, 7200):
                if now - start >= checkpoint and checkpoint not in checkpoints:
                    save(out / ("checkpoint_" + str(checkpoint) + ".json"), status)
                    print("C2_OBSERVATION_POINT " + json.dumps(status), flush=True)
                    checkpoints.add(checkpoint)
            if now - last >= 600 or terminal or not active:
                print("STATUS " + json.dumps(status), flush=True)
                last = now
            if terminal:
                stop_reason = "RESULT_OR_ERROR_REQUIRES_REVIEW"
                break
            time.sleep(2)
    finally:
        for proc, logfile, folder, record, begun in active:
            stop(proc)
            logfile.close()
            record.update(status="STOPPED_OPEN", reason=stop_reason or "CONTROLLER_INTERRUPTED",
                          exit=proc.returncode, seconds=round(time.monotonic()-begun, 2))
            save(folder / "result.json", record)
        save(out / "jobs.json", records)
    for record in records:
        folder = out / ("seed_" + str(record["seed"]))
        if record["status"] == "UNSAT_PENDING_CHECK":
            checked = check_proof(cake, cnf, folder / "proof.lrat", folder, out)
            record["verification"] = checked
            record["status"] = checked["status"]
        elif record["status"] == "SAT_PENDING_CHECK":
            c, f = CNF(), Frame(14)
            try:
                f.allocate(c)
                values = read_primary_model(folder / "solver.log", len(f.map))
                graph = reconstruct(f, values)
                valid = verify_graph(graph, 14)
                record["status"] = "GRAPH_VERIFIED" if valid else "INVALID_SAT_MODEL"
                if valid:
                    save(folder / "graph.json", graph)
            finally:
                c.close()
        proof = folder / "proof.lrat"
        if proof.exists():
            record["proof_bytes"] = proof.stat().st_size
        save(folder / "result.json", record)
    states = {r["status"] for r in records}
    result = "C2_UNSAT_CERTIFIED" if "UNSAT_CERTIFIED" in states else "C2_GRAPH_FOUND" if "GRAPH_VERIFIED" in states else "PILOT_OPEN"
    if result == "PILOT_OPEN" and states & {"SOLVER_ERROR", "CHECK_FAILED", "INVALID_SAT_MODEL"}:
        result = "PILOT_ERROR"
    report = {"status": result, "stop_reason": stop_reason, "jobs": records,
              "wall_seconds": round(time.monotonic()-start, 2), "cnf_sha256": CNF_HASH,
              "scope": "Certificate proves only this CNF; the C2 conclusion also uses the documented encoder and fixed-point theorem."}
    save(out / "summary.json", report)
    save(out / "status.json", report)
    print("C2_PILOT_RESULT " + json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cnf", default=DEFAULT_INPUT)
    parser.add_argument("--cake", default=DEFAULT_CAKE)
    parser.add_argument("--solver", default=str(Path.home()/".local/bin/cadical"))
    parser.add_argument("--seconds", type=int, default=0)
    parser.add_argument("--workers", type=int, default=11)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.seconds < 0 or not 1 <= args.workers <= 24:
        parser.error("seconds must be nonnegative; workers must be 1..24")
    if not args.run:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        args.out = args.out or Path.home()/"conway99_workspace/c2_reference_v1"/("pilot_"+stamp)
        args.out = args.out.resolve()
        args.out.mkdir(parents=True, exist_ok=False)
        command_line = [sys.executable, str(Path(__file__).resolve()), "--run", "--out", str(args.out),
                        "--cnf", args.cnf, "--cake", args.cake, "--solver", args.solver,
                        "--seconds", str(args.seconds), "--workers", str(args.workers)]
        with (args.out/"driver.log").open("w") as log:
            proc = subprocess.Popen(command_line, stdin=subprocess.DEVNULL, stdout=log,
                                    stderr=subprocess.STDOUT, start_new_session=True)
        save(args.out/"launch.json", {"pid": proc.pid, "command": command_line})
        print("C2_PILOT_LAUNCHED " + json.dumps({"pid": proc.pid, "output": str(args.out),
              "log": str(args.out/"driver.log"), "search_budget_seconds": args.seconds or None, "workers": args.workers,
              "observation_points_seconds": [3600, 7200],
              "note": "detached; startup and proof status are recorded in driver.log/status.json"}), flush=True)
        return
    if args.out is None:
        parser.error("--run requires --out")
    def interrupted(signum, frame):
        raise KeyboardInterrupt("Controller signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        run(args)
    except BaseException as error:
        save(args.out/"status.json", {"status": "CONTROLLER_FAILED", "error": repr(error)})
        print("C2_PILOT_FAILED " + repr(error), flush=True)
        raise


if __name__ == "__main__":
    main()
