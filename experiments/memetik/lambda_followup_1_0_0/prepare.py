"""Build isolated runs; read and lock, but never change the original campaign."""
import boot
from util import *
import copy
import shutil

PLAN = "docs/memetik/lambda_synthesis_20260922/PROPOSED_MANIFEST.json"
BANK = "docs/memetik/lambda_synthesis_20260922/RECORD_BANK.json"

def package_verify():
    info = read(boot.HERE / "PACKAGE.json")
    for relative, expected in info["files"].items():
        p = boot.ROOT / relative
        if not p.is_file() or file_sha(p) != expected:
            raise RuntimeError("Package source changed: " + relative)
    return info

def source_verify(source, specs):
    signature = read(source / "fingerprint.json")
    if env() != signature["environment"]:
        raise RuntimeError("Original Python/pynauty environment differs: " + str(signature["environment"]))
    if file_sha(source / "manifest.json") != signature["manifest_sha256"]:
        raise RuntimeError("Original manifest changed")
    expected = read(boot.HERE / "SOURCE_PINS.json")
    if signature["files"] != expected:
        raise RuntimeError("Original bundle is not the pinned 0.2.0 bundle")
    for path, digest in expected.items():
        if file_sha(source / "bundle" / path) != digest:
            raise RuntimeError("Original source changed: " + path)
    if read(source / "budget.json")["per_job_cpu_seconds"] != 3600:
        raise RuntimeError("Original no longer at the agreed one-hour endpoint")
    if any((source / "tasks").glob("*/active.json")):
        raise RuntimeError("Original has active/unresolved CPU sessions")
    if any(not read(p).get("clean", False) for p in source.glob("*_timing.json")):
        raise RuntimeError("Original controller timing is unresolved")
    for spec in specs:
        if spec["mode"] != "resume_copy":
            continue
        d = source / "tasks" / spec["old_id"]
        r = receipt_valid(d)
        if r != spec["original_receipt"]:
            raise RuntimeError("Original differs from published receipt: " + spec["old_id"])
        if read(d / "result.json")["endpoint_cpu_seconds"] != 3600:
            raise RuntimeError("Wrong original endpoint")
        sqlite_frozen(d / "archive.sqlite")
    return signature

def record_founders(target, founders, banks):
    bank = banks[target]
    new = copy.deepcopy(founders)
    item = checked_item(bank["record"]["graph6"], "record-synthesis-" + target)
    if item["scores"] != bank["record"]["scores"]:
        raise RuntimeError("Record score differs")
    item["parent"] = item["state"]
    new[bank["replace_index"]] = item
    validate_founders(new)
    return new

def validate_founders(founders):
    if len(founders) != 16:
        raise RuntimeError("Expected exactly sixteen founders")
    classes = []
    for f in founders:
        rows, scores = checked(f["graph6"], "lambda")
        certificate = core.canonical(rows)
        if scores != f["scores"] or certificate != f["class"] or sha(f["graph6"].encode()) != f["state"]:
            raise RuntimeError("Invalid founder or canonical certificate")
        classes.append(certificate)
    if len(set(classes)) != 16:
        raise RuntimeError("Duplicate canonical founder")

def prepare(source, run):
    if run.exists():
        raise FileExistsError("Run directory already exists; it will not be overwritten")
    if source == run or source in run.parents or run in source.parents:
        raise RuntimeError("Source and destination must be separate sibling trees")
    info = package_verify()
    proposal = read(boot.ROOT / PLAN)
    if len(proposal["jobs"]) != 39 or proposal["proposed_total_cpu_hours"] != 121:
        raise RuntimeError("Unexpected proposal")
    source_lock = lock(source / "controller.lock", create=False)
    run.mkdir(parents=True)
    ledger = AuxiliaryLedger(run)
    host_cpu = 0
    try:
        ledger.begin("infrastructure", "prepare", min(1800, ledger.remaining("infrastructure")))
        from clock import HostClock, resources
        host = HostClock(run)
        try:
            snap = resources(run.parent, host.sample(), {})
            if snap["hazards"] or len(os.sched_getaffinity(0)) < 18:
                raise RuntimeError("Ryzen preflight failed: " + str(snap))
            signature = source_verify(source, proposal["jobs"])
            copy_size = sum((source / "tasks" / j["old_id"] / n).stat().st_size
                            for j in proposal["jobs"] if j["mode"] == "resume_copy"
                            for n in ("task.json", "checkpoint.json", "result.json", "receipt.json", "archive.sqlite"))
            if snap["linux_free_bytes"] - copy_size < 20 * GIB or host.last["physical_free_bytes"] - copy_size < 50 * GIB:
                raise RuntimeError("Snapshot copies would consume the required disk reserve")
            program = run / "program"
            files = list(info["files"]) + [str((boot.HERE / "PACKAGE.json").relative_to(boot.ROOT))]
            for relative in files:
                p = program / relative
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(boot.ROOT / relative, p)
            founders = read(boot.FROZEN / "founders.json")
            validate_founders(founders)
            banks = read(boot.ROOT / BANK)
            populations = {t: record_founders(t, founders, banks) for t in ("W", "Linf", "L1")}
            config = read(boot.FROZEN / "config.json")
            entries = []
            for spec in proposal["jobs"]:
                part = "records" if spec["group"] == "record" else "comparison"
                d = run / "runs" / part / "tasks" / spec["id"]
                d.mkdir(parents=True)
                root = d.parent.parent
                if not (root / "budget.json").exists():
                    atomic(root / "budget.json", {"per_job_cpu_seconds": 7200 if part == "records" else 14400})
                if spec["mode"] == "resume_copy":
                    original = source / "tasks" / spec["old_id"]
                    for name in ("task.json", "checkpoint.json", "result.json", "receipt.json", "archive.sqlite"):
                        shutil.copyfile(original / name, d / name)
                    receipt_valid(d)
                    initial_actual = spec["original_receipt"]["cpu_seconds"]
                    history = read(d / "result.json")
                else:
                    cfg = copy.deepcopy(config)
                    cfg["milestones_cpu_seconds"] = proposal["record_milestones"] if part == "records" else proposal["comparison_milestones"]
                    cfg["version"] = "lambda-followup-1.0.0"
                    task = {"id": spec["id"], "kind": "compare" if part == "comparison" else "record",
                            "arm": "lambda", "target": spec["target"], "variant": spec["variant"],
                            "seed": spec["seed"], "replicate": spec["replicate"],
                            "worker_cpu_seconds": spec["cumulative_budget_seconds"],
                            "founders": populations[spec["target"]] if part == "records" else founders, "config": cfg}
                    atomic(d / "task.json", task)
                    initial_actual, history = 0, None
                initial = run / "initial" / spec["id"]
                initial.mkdir(parents=True)
                if history:
                    shutil.copyfile(d / "result.json", initial / "result.json")
                    shutil.copyfile(d / "receipt.json", initial / "receipt.json")
                entries.append({**spec, "directory": str(d.relative_to(run)), "initial_actual_cpu": initial_actual,
                                "task_sha256": file_sha(d / "task.json"),
                                "original_result_sha256": file_sha(initial / "result.json") if history else None})
            (run / "diagnostics").mkdir()
            plan = {"version": "lambda-followup-1.0.0", "authorized_cpu_hours": 121, "workers": 18,
                    "source": str(source), "source_manifest_sha256": signature["manifest_sha256"],
                    "jobs": entries, "queue": proposal["queue"], "auxiliary_limits": AUX_LIMITS,
                    "search_additional_cpu_seconds": 117 * 3600,
                    "automatic_extension": False, "record_bank": banks}
            atomic(run / "plan.json", plan)
            immutable_files = {str(p.relative_to(run)): file_sha(p) for p in program.rglob("*") if p.is_file()}
            immutable_files["plan.json"] = file_sha(run / "plan.json")
            for p in (run / "initial").rglob("*"):
                if p.is_file():
                    immutable_files[str(p.relative_to(run))] = file_sha(p)
            for part in ("comparison", "records"):
                rel = "runs/" + part + "/budget.json"
                immutable_files[rel] = file_sha(run / rel)
            atomic(run / "FINGERPRINT.json", {"files": immutable_files, "environment": env()})
            snap = resources(run, host.sample(), {})
            if snap["hazards"]:
                raise RuntimeError("Post-copy resource reserve failed")
            atomic(run / "PREPARED.json", {"status": "PREPARED_NOT_STARTED", "jobs": 39,
                                          "copy_bytes": copy_size, "host": host.last})
        finally:
            host_cpu = host.close()
        ledger.finish(own_cpu() + host_cpu, "PREPARED")
    except BaseException:
        current = read(ledger.path)
        if current["active"] is not None:
            ledger.finish(own_cpu() + host_cpu, "PREPARE_FAILED")
        atomic(run / "PREPARE_FAILED.json", {"status": "DIAGNOSIS_REQUIRED"})
        raise
    finally:
        source_lock.close()
    print(json.dumps({"status": "PREPARED_NOT_STARTED", "run": str(run), "jobs": 39, "new_cpu_hours": 121}, indent=2))

def verify(run):
    signature = read(run / "FINGERPRINT.json")
    if signature["environment"] != env():
        raise RuntimeError("Prepared environment changed")
    for relative, expected in signature["files"].items():
        if file_sha(run / relative) != expected:
            raise RuntimeError("Frozen run file changed: " + relative)
    plan = read(run / "plan.json")
    if (len(plan["jobs"]) != 39 or len(set(plan["queue"])) != 39
            or set(plan["queue"]) != {j["id"] for j in plan["jobs"]}
            or plan["workers"] != 18
            or sum(j["additional_cpu_seconds"] for j in plan["jobs"]) != 117 * 3600):
        raise RuntimeError("Invalid selected jobs or budget")
    for job in plan["jobs"]:
        if file_sha(run / job["directory"] / "task.json") != job["task_sha256"]:
            raise RuntimeError("Task changed: " + job["id"])
    return plan
