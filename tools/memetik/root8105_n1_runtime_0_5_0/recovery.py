"""Explicit, conservative recovery for runtime 0.2.0.
No automatic adoption, no reconstruction of missing wait4 measurements.
"""
import copy
import fcntl
import json
import math
import os
from pathlib import Path
import resource
import time
import uuid
import runtime as r
import n1_check
import accounting
import guard


def lock_run(root):
    lock = (root / "supervisor.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lock


def validate(root):
    m = r.read(root / "manifest.json")
    for path, digest in (
        (root / "input.cnf", m["input_sha256"]),
        (Path(m["worker"]), m["worker_sha256"]),
        (Path(m["checker"]), m["checker_sha256"]),
        (Path(r.__file__), m["runtime_sha256"]),
        (Path(__file__), m["recovery_sha256"]),
        (Path(__file__).with_name("n1_check.py"), m["n1_check_sha256"]),
        (Path(__file__).with_name("bind_n1.py"), m["binder_sha256"]),
        (Path(__file__).with_name("accounting.py"), m["accounting_sha256"]),
        (Path(__file__).with_name("guard.py"), m["guard_sha256"]),
    ):
        if r.sha(path) != digest:
            raise ValueError("input/tool hash mismatch: " + str(path))
    if m["binding_sha256"] is not None:
        if r.sha(root / "binding.json") != m["binding_sha256"]:
            raise ValueError("binding changed")
        n1_check.validate_binding(n1_check.load(root / "binding.json"), root / "input.cnf")
    return m


def alive(ident):
    if ident["boot"] != Path("/proc/sys/kernel/random/boot_id").read_text().strip():
        return False
    directory = Path("/proc") / str(ident["proc_pid"])
    try:
        fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
        return (fields[19] == ident["birth"] and fields[0] != "Z" and
                os.readlink(directory / "ns/pid") == ident["namespace"])
    except (FileNotFoundError, ProcessLookupError):
        return False


def check_files(directory, hashes):
    for name, digest in hashes.items():
        if Path(name).name != name or name in (".", ".."):
            raise ValueError("invalid artifact path")
        if r.sha(directory / name) != digest:
            raise ValueError("changed artifact: " + str(directory / name))


def phase_receipt(directory, phase, m):
    receipt = r.read(directory / (phase + "_receipt.json"))
    cpu = receipt["cpu_s"]
    if (receipt["attempt_id"] != directory.name or receipt["phase"] != phase or
            receipt["input_sha256"] != m["input_sha256"] or
            type(cpu) not in (int, float) or not math.isfinite(cpu) or cpu < 0):
        raise ValueError("invalid phase receipt")
    check_files(directory, receipt["files"])
    return receipt


def checked_status(directory, receipt):
    lines = (directory / "check.log").read_text().replace("\r", "\n").splitlines()
    valid = (receipt["returncode"] == 0 and "s VERIFIED" in lines and
             not any(x in lines for x in ("s NOT VERIFIED", "s TIMEOUT", "s DERIVATION")))
    return "UNSAT_CERTIFIED" if valid else "UNSAT_UNCERTIFIED"


def validate_sat(root, manifest, directory, persist):
    if not r.cnf_model_ok(root / "input.cnf", directory / "model.txt"):
        raise ValueError("invalid CNF SAT model")
    if manifest["binding_sha256"] is None:
        return None
    binding = n1_check.load(root / "binding.json")
    matrix, check = n1_check.decode_and_check(binding, root / "input.cnf", directory / "model.txt")
    evidence = {"status": "SAT_N1_VERIFIED", "matrix": matrix, "check": check,
                "binding_sha256": manifest["binding_sha256"],
                "model_sha256": r.sha(directory / "model.txt"),
                "cnf_sha256": manifest["input_sha256"]}
    target = directory / "N1_WITNESS.json"
    if target.exists() and r.read(target) != evidence:
        raise ValueError("N1 witness evidence changed")
    if persist:
        r.atomic(target, evidence)
    return evidence


def inventory(root, state, m):
    n1_evidence = {}
    total, gaps, attempts, sources, sat, certified = 0.0, [], [], {}, False, False
    directories = sorted((root / "attempts").iterdir())
    metas = {}
    for d in directories:
        if not d.is_dir():
            raise ValueError("unexpected attempt entry")
        meta = r.read(d / "attempt.json")
        if (meta["id"] != d.name or meta["run_id"] != m["run_id"] or
                meta["input_sha256"] != m["input_sha256"] or
                meta["binding_sha256"] != m["binding_sha256"]):
            raise ValueError("invalid attempt identity")
        metas[d.name] = meta
        if (d / "final.json").exists():
            item = {"id": d.name, "receipt_sha256": r.sha(d / "final.json")}
            final = r.verify_attempt(d, item)
            if final["attempt_id"] != d.name or final["input_sha256"] != m["input_sha256"]:
                raise ValueError("invalid final receipt identity")
            attempts.append(item)
        for phase in ("search", "check"):
            intent, done = d / (phase + "_intent.json"), d / (phase + "_receipt.json")
            if done.exists():
                if not intent.exists():
                    raise ValueError("receipt without launch intent")
                receipt = phase_receipt(d, phase, m)
                total += receipt["cpu_s"]
                if phase == "search" and (d / "worker.json").exists():
                    code = json.loads((d / "worker.json").read_text())["result"]
                    if receipt["returncode"] != code:
                        raise ValueError("solver exit/result mismatch")
                    if code == 20:
                        if "proof.partial" not in receipt["files"]:
                            raise ValueError("unsealed proof")
                        sources[d.name] = receipt["files"]["proof.partial"]
                    elif code == 10:
                        evidence = validate_sat(root, m, d, False)
                        if evidence is not None:
                            n1_evidence[d.name] = evidence
                        sat = True
                    elif code != 0:
                        raise ValueError("invalid solver result")
            elif intent.exists():
                idfile = d / (phase + "_identity.json")
                if not idfile.exists():
                    raise ValueError("launch window without identity; manual reconciliation required")
                if alive(r.read(idfile)):
                    raise ValueError("live orphan: no adoption or duplicate start")
                lower = None
                if state.get("active_attempt") == d.name and state.get("phase") == phase:
                    lower = state.get("live_cpu")
                gaps.append({"attempt": d.name, "phase": phase, "cpu_s": None,
                             "last_measured_lower_bound_s": lower,
                             "reason": "missing wait4 end receipt"})
    for d in directories:
        if (d / "check_receipt.json").exists():
            source = metas[d.name]["proof_source"]
            if source not in sources:
                raise ValueError("checker has no sealed UNSAT search input")
            if metas[d.name]["proof_sha256"] != sources[source]:
                raise ValueError("checker/source proof mismatch")
            receipt = phase_receipt(d, "check", m)
            certified |= checked_status(d, receipt) == "UNSAT_CERTIFIED"
    if sat and certified:
        raise ValueError("contradictory verified results")
    source = None
    if sources:
        source = max(sources, key=lambda key: metas[key]["created_ns"])
    result = ("UNSAT_CERTIFIED" if certified else ("SAT_N1_VERIFIED" if m["binding_sha256"] is not None else "SAT_CNF_VERIFIED") if sat else
              "UNSAT_UNCERTIFIED" if source else
              "READY" if not directories else "STOPPED_UNRESOLVED")
    return {"n1_evidence": n1_evidence, "cpu_confirmed_s": total, "accounting_complete": not gaps,
            "gaps": gaps, "attempts": attempts, "proof_source": source,
            "proof_sha256": sources.get(source), "result_status": result}


def recover(root, apply=False):
    lock = lock_run(root)
    m = validate(root)
    s = r.latest_state(root)
    if s["run_id"] != m["run_id"]:
        raise ValueError("state run identity mismatch")
    guard.validate_state(root, s, m)
    inv = inventory(root, s, m)
    proposed = copy.deepcopy(s)
    proposed.update(cpu_completed=inv["cpu_confirmed_s"], live_cpu=0.0,
                    accounting_complete=inv["accounting_complete"],
                    accounting_gaps=inv["gaps"], attempts=inv["attempts"],
                    proof_source=inv["proof_source"], proof_sha256=inv["proof_sha256"],
                    result_status=inv["result_status"], child=None, supervisor=None,
                    active_attempt=None, phase=None)
    proposed["status"] = inv["result_status"] if inv["accounting_complete"] else "ACCOUNTING_INCOMPLETE"
    # Preserve budget/reply transaction history exactly, including stop and open request.
    if proposed["status"] in ("SAT_CNF_VERIFIED", "SAT_N1_VERIFIED", "UNSAT_CERTIFIED"):
        proposed["request"] = None
    report = {"apply": apply, "from_sequence": s["_seq"], "inventory": inv,
              "proposed_status": proposed["status"]}
    if apply:
        # Preserve the cache bytes, even if stale or corrupted.
        folder = root / "recovery"
        folder.mkdir(exist_ok=True)
        rid = uuid.uuid4().hex
        cache = root / "state.json"
        if cache.exists():
            out = folder / (rid + ".state-before")
            with out.open("xb") as f:
                f.write(cache.read_bytes())
                f.flush()
                os.fsync(f.fileno())
        r.atomic(folder / (rid + ".json"), report)
        r.atomic(root / "state.json", proposed)
    return report


def finish(root, s, m, directory, result, started):
    final = {"status": result, "attempt_id": directory.name,
             "input_sha256": m["input_sha256"], "binding_sha256": m["binding_sha256"], "cpu_completed": s["cpu_completed"],
             "accounting_complete": s["accounting_complete"],
             "accounting_scope": "native_children_cpu_seconds",
             "supervisor_session_cpu_s": time.process_time() - started,
             "files": {p.name: r.sha(p) for p in directory.iterdir() if p.is_file()}}
    r.atomic(directory / "final.json", final)
    r.fault(root, "after_final")
    item = {"id": directory.name, "receipt_sha256": r.sha(directory / "final.json")}
    r.verify_attempt(directory, item)
    s["attempts"].append(item)
    s.update(status=guard.finish(s, result), result_status=result, request=None, active_attempt=None)
    r.atomic(root / "state.json", s)
    return s


def run(root, resume=False):
    lock = lock_run(root)
    m, s = validate(root), r.read(root / "state.json")
    accounting.gate(root, m)
    if resource.getrlimit(resource.RLIMIT_CPU) != (-1, -1):
        raise ValueError("finite inherited CPU limit")
    guard.validate_state(root, s, m)
    inv = inventory(root, s, m)
    if not inv["accounting_complete"] or not s["accounting_complete"]:
        raise ValueError("incomplete accounting; explicit recovery, no automatic restart")
    if abs(inv["cpu_confirmed_s"] - s["cpu_completed"]) > 1e-9:
        raise ValueError("ledger mismatch; explicit recover required")
    if s["status"] in ("SAT_CNF_VERIFIED", "SAT_N1_VERIFIED", "UNSAT_CERTIFIED"):
        if s["status"] != inv["result_status"]:
            raise ValueError("terminal status lacks evidence")
        return s
    if s["status"] not in ("READY", "STOPPED_UNRESOLVED", "UNSAT_UNCERTIFIED", "RESOURCE_STOPPED"):
        raise ValueError("unclosed session; explicit recover required")
    if s["status"] != "READY" and not resume:
        raise ValueError("explicit resume required")
    source = inv["proof_source"] if s["status"] in ("UNSAT_UNCERTIFIED", "RESOURCE_STOPPED") else None
    if s["status"] == "UNSAT_UNCERTIFIED" and source is None:
        raise ValueError("missing sealed proof source")
    s["stop"] = False
    if not guard.activate(root, s, m):
        return s
    s["supervisor"] = r.identity(os.getpid())
    s["status"] = "RUNNING"
    aid = uuid.uuid4().hex
    directory = root / "attempts" / aid
    directory.mkdir()
    meta = {"id": aid, "run_id": m["run_id"], "created_ns": time.time_ns(),
            "input_sha256": m["input_sha256"], "binding_sha256": m["binding_sha256"],
            "proof_source": source, "proof_sha256": inv["proof_sha256"] if source else None,
            "accounting_session": os.environ.get(accounting.ENV)}
    r.atomic(directory / "attempt.json", meta)
    s["active_attempt"] = aid
    r.atomic(root / "state.json", s)
    started = time.process_time()
    result = "STOPPED_UNRESOLVED"
    if source is None:
        search = r.child(root, s, directory, [m["worker"], str(root / "input.cnf")], "search")
        raw = directory / "worker.json"
        if not raw.exists():
            return finish(root, s, m, directory, "CRASHED_UNRESOLVED", started)
        code = json.loads(raw.read_text())["result"]
        if search["returncode"] != code:
            raise ValueError("worker/exit disagreement")
        if code == 10:
            validate_sat(root, m, directory, True)
            status = "SAT_N1_VERIFIED" if m["binding_sha256"] is not None else "SAT_CNF_VERIFIED"
            return finish(root, s, m, directory, status, started)
        if code == 20:
            source = aid
            meta.update(proof_source=aid, proof_sha256=r.sha(directory / "proof.partial"))
            r.atomic(directory / "attempt.json", meta)
            result = "UNSAT_UNCERTIFIED"
        elif code != 0:
            raise ValueError("unexpected solver code")
    else:
        result = "UNSAT_UNCERTIFIED"
    if s.get("guard") is not None:
        guard.MONITORS[str(root)]["last_tick"] = -1e9
        r.service(root, s)
    if source is not None and not s["stop"]:
        # Immutable source has a successful worker return and a sealed phase receipt.
        phase_receipt(root / "attempts" / source, "search", m)
        proof = root / "attempts" / source / "proof.partial"
        if r.sha(proof) != meta["proof_sha256"]:
            raise ValueError("proof changed before checker launch")
        check = r.child(root, s, directory,
                        [m["checker"], str(root / "input.cnf"), str(proof), "-O"], "check")
        result = checked_status(directory, check)
    return finish(root, s, m, directory, result, started)
