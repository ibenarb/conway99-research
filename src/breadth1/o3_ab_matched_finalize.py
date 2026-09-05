#!/usr/bin/env python3
import json
import hashlib
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

RUN = Path.home() / "conway99_workspace/o3_breadth1_runs/ab_matched_main_20260904"
FREEZE = Path.home() / "conway99_workspace/conway99_freezes/O3_BREADTH1_AB_MATCHED_20260905"
REPO = Path.home() / "conway99_workspace/conway99-research"

RUNNER_REL = Path("src/breadth1/o3_ab_matched_scout_runner.py")
PANEL_REL = Path("results/breadth1/O3_smt_panel20.tsv")

EXPECTED_RUNNER_SHA256 = "451ac951efa307cefc2fd258dba9a119cfe78edc352d4e16675531ba3342e29e"
EXPECTED_PANEL_SHA256 = "c7ea3d618c056120dfeea303017e261485952887729c7057f1c989e9c2650839"
EXPECTED_TYPES = 139
EXPECTED_INSTANCES = 278
EXPECTED_STATUS = Counter({"TIMEOUT": 275, "UNSAT_UNCERTIFIED": 3})
EXPECTED_LAYER_STATUS = {
    "A": Counter({"TIMEOUT": 138, "UNSAT_UNCERTIFIED": 1}),
    "B": Counter({"TIMEOUT": 137, "UNSAT_UNCERTIFIED": 2}),
}
CONTROL_3_9 = "tau06_3-3-3-3-3-3-3-3-3"
CONTROL_6_3_7 = "tau06_6-3-3-3-3-3-3-3"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()

def hms(x):
    x = int(round(float(x)))
    h, rem = divmod(x, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def load_states():
    files = sorted((RUN / "types").glob("*.json"))
    if len(files) != EXPECTED_TYPES:
        raise RuntimeError(f"expected {EXPECTED_TYPES} type files, found {len(files)}")
    states = []
    for p in files:
        d = json.loads(p.read_text())
        if not d.get("complete"):
            raise RuntimeError(f"incomplete type: {p.name}")
        inst = d.get("instances", [])
        if len(inst) != 2:
            raise RuntimeError(f"{p.name}: expected 2 instances, got {len(inst)}")
        if [x.get("layer") for x in inst] != ["A", "B"]:
            raise RuntimeError(f"{p.name}: layer order is not A,B")
        a, b = inst
        if a.get("seed") != b.get("seed"):
            raise RuntimeError(f"{p.name}: A/B seed mismatch")
        if a.get("cpu") != b.get("cpu"):
            raise RuntimeError(f"{p.name}: A/B CPU mismatch")
        states.append(d)
    return states

def aggregate(states):
    status = Counter()
    layer_status = defaultdict(Counter)
    layer_tau = defaultdict(Counter)
    metrics = defaultdict(lambda: defaultdict(float))
    unsat = []
    rows = []
    for d in states:
        jid = d["job_id"]
        for x in d["instances"]:
            st, ly, tau = x["status"], x["layer"], x["tau"]
            status[st] += 1
            layer_status[ly][st] += 1
            layer_tau[(ly, tau)][st] += 1
            for k in ("conflicts", "decisions", "propagations"):
                metrics[ly][k] += int(x.get(k, 0))
            for k in ("solve_wall_seconds", "child_cpu_seconds"):
                metrics[ly][k] += float(x.get(k, 0))
            if st == "UNSAT_UNCERTIFIED":
                unsat.append({
                    "job_id": jid, "layer": ly, "tau": tau,
                    "seed": x.get("seed"), "cpu": x.get("cpu"),
                    "solve_wall_seconds": x.get("solve_wall_seconds"),
                    "conflicts": x.get("conflicts"),
                    "decisions": x.get("decisions"),
                    "propagations": x.get("propagations"),
                    "cnf_sha256": x.get("cnf_sha256"),
                    "variables": x.get("variables"), "clauses": x.get("clauses"),
                })
        a, b = d["instances"]
        rows.append({
            "job_id": jid, "tau": d["tau"], "cycle_type": d["cycle_type"],
            "seed": a["seed"], "cpu": a["cpu"],
            "A_status": a["status"], "B_status": b["status"],
            "A_solve_wall_seconds": a["solve_wall_seconds"],
            "B_solve_wall_seconds": b["solve_wall_seconds"],
            "A_conflicts": a.get("conflicts", 0), "B_conflicts": b.get("conflicts", 0),
            "A_decisions": a.get("decisions", 0), "B_decisions": b.get("decisions", 0),
            "A_propagations": a.get("propagations", 0), "B_propagations": b.get("propagations", 0),
            "A_cnf_sha256": a.get("cnf_sha256"), "B_cnf_sha256": b.get("cnf_sha256"),
        })
    return status, layer_status, layer_tau, metrics, unsat, rows

def validate(status, layer_status, unsat):
    if status != EXPECTED_STATUS:
        raise RuntimeError(f"final status mismatch: {dict(status)}")
    for ly, exp in EXPECTED_LAYER_STATUS.items():
        if layer_status[ly] != exp:
            raise RuntimeError(f"{ly} status mismatch: {dict(layer_status[ly])}")
    pairs = {(x["job_id"], x["layer"]) for x in unsat}
    expected = {
        (CONTROL_3_9, "A"),
        (CONTROL_3_9, "B"),
        (CONTROL_6_3_7, "B"),
    }
    if pairs != expected:
        raise RuntimeError(f"unexpected UNSAT pairs: {sorted(pairs)}")

def control_info(states):
    idx = {d["job_id"]: d for d in states}
    a39, b39 = idx[CONTROL_3_9]["instances"]
    a637, b637 = idx[CONTROL_6_3_7]["instances"]
    if a39["cnf_sha256"] != b39["cnf_sha256"]:
        raise RuntimeError("(3^9): A/B CNFs are not identical")
    for k in ("conflicts", "decisions", "propagations"):
        if a39.get(k) != b39.get(k):
            raise RuntimeError(f"(3^9): A/B {k} mismatch")
    if a637["status"] != "TIMEOUT" or b637["status"] != "UNSAT_UNCERTIFIED":
        raise RuntimeError("(6,3^7): unexpected A/B result")
    return {"3^9": {"A": a39, "B": b39}, "6,3^7": {"A": a637, "B": b637}}

def freeze_copy(metadata):
    if FREEZE.exists():
        raise RuntimeError(f"freeze exists; refusing overwrite: {FREEZE}")
    shutil.copytree(RUN, FREEZE, symlinks=True, copy_function=shutil.copy2)
    (FREEZE / "FREEZE_METADATA.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    entries = []
    for p in sorted(FREEZE.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            entries.append((sha256_file(p), str(p.relative_to(FREEZE))))
    checksum = FREEZE / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{h}  {rel}\n" for h, rel in entries))
    return len(entries), sha256_file(checksum)

def write_reports(summary, rows):
    res = REPO / "results/breadth1"
    docs = REPO / "docs/breadth1"
    res.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)

    js = res / "O3_ab_matched_main_20260905_summary.json"
    js.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    tsv = res / "O3_ab_matched_main_20260905_types.tsv"
    cols = ["job_id","tau","cycle_type","seed","cpu","A_status","B_status",
            "A_solve_wall_seconds","B_solve_wall_seconds",
            "A_conflicts","B_conflicts","A_decisions","B_decisions",
            "A_propagations","B_propagations","A_cnf_sha256","B_cnf_sha256"]
    with tsv.open("w", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda x: x["job_id"]):
            vals = []
            for c in cols:
                v = r[c]
                if c == "cycle_type":
                    v = ",".join(map(str, v))
                vals.append(str(v))
            f.write("\t".join(vals) + "\n")

    c39 = summary["controls"]["3^9"]
    c637 = summary["controls"]["6,3^7"]
    ma = summary["layer_metrics"]["A"]
    mb = summary["layer_metrics"]["B"]
    md = docs / "O3_AB_MATCHED_MAIN_20260905.md"
    md.write_text(f"""# O3-BREADTH-1 matched-seed A/B scout — final report

Date: 2026-09-05
Status: **COMPLETE / SCOUT ONLY**
Certification: **no new certified exclusion**

## Provenance

- Raw campaign: `{RUN}`
- Immutable freeze: `{FREEZE}`
- Git branch before final report: `{summary["git"]["branch"]}`
- Git HEAD before final report: `{summary["git"]["head"]}`
- Runner SHA256: `{summary["provenance"]["runner_sha256"]}`
- SMT panel SHA256: `{summary["provenance"]["smt_panel_sha256"]}`
- Workers: **20**
- Timeout: **5760 s**
- Layers: **A, B**
- A/B seed scope: **matched per type**
- A/B execution: **same logical CPU, A then B**

## Final audit

- Types complete: **139/139**
- Instances complete: **278/278**
- A/B seed matches: **139/139**
- A/B CPU matches: **139/139**
- `TIMEOUT`: **275**
- `UNSAT_UNCERTIFIED`: **3**
- Audit errors: **0**

Layer totals:

- A: **138 TIMEOUT + 1 UNSAT_UNCERTIFIED**
- B: **137 TIMEOUT + 2 UNSAT_UNCERTIFIED**

## Main scientific result

The only `UNSAT_UNCERTIFIED` outcomes belong to the two pre-existing control/excluded types:

- `(3^9)`
- `(6,3^7)`

For the **137 remaining open O3 types**:

- A: **137/137 TIMEOUT**
- B: **137/137 TIMEOUT**
- new UNSAT candidates: **0**

`UNSAT_UNCERTIFIED` is a scout-level CaDiCaL outcome, not an LRAT/Cake-certified mathematical exclusion.

## Control `(3^9)`

A and B are byte-identical because B adds no generic `C_m` constraint here.

- CNF SHA256 A/B: `{c39["A"]["cnf_sha256"]}`
- matched seed: `{c39["A"]["seed"]}`
- matched CPU: `{c39["A"]["cpu"]}`
- A solve wall: **{c39["A"]["solve_wall_seconds"]:.3f} s**
- B solve wall: **{c39["B"]["solve_wall_seconds"]:.3f} s**
- conflicts A/B: **{c39["A"]["conflicts"]} / {c39["B"]["conflicts"]}**
- decisions A/B: **{c39["A"]["decisions"]} / {c39["B"]["decisions"]}**
- propagations A/B: **{c39["A"]["propagations"]} / {c39["B"]["propagations"]}**

The logical solver statistics are exactly identical, validating the matched-seed control.

## Control `(6,3^7)`

This type was already fully certified in the earlier FULLCERT milestone (656/656 terminal A obligations certified). The present result is only a performance/control observation.

- matched seed: **{c637["A"]["seed"]}**
- matched CPU: **{c637["A"]["cpu"]}**
- A: **TIMEOUT**, solve wall **{c637["A"]["solve_wall_seconds"]:.3f} s**
- B: **UNSAT_UNCERTIFIED**, solve wall **{c637["B"]["solve_wall_seconds"]:.3f} s**
- conflicts A/B: **{c637["A"]["conflicts"]} / {c637["B"]["conflicts"]}**
- decisions A/B: **{c637["A"]["decisions"]} / {c637["B"]["decisions"]}**
- propagations A/B: **{c637["A"]["propagations"]} / {c637["B"]["propagations"]}**
- B added clauses: **{c637["B"]["encoder_meta"]["added_over_A_clauses"]}**
- B added variables: **{c637["B"]["encoder_meta"]["added_over_A_variables"]}**
- B cycle-local constraints: **{c637["B"]["encoder_meta"]["cycle_local"]["constraints"]}**

B therefore has a real algorithmic effect on this known control, but that effect produced no new solved type among the 137 open cases.

## Aggregate solver work

A:

- conflicts: **{int(ma["conflicts"])}**
- decisions: **{int(ma["decisions"])}**
- propagations: **{int(ma["propagations"])}**
- summed solve wall: **{hms(ma["solve_wall_seconds"])}**

B:

- conflicts: **{int(mb["conflicts"])}**
- decisions: **{int(mb["decisions"])}**
- propagations: **{int(mb["propagations"])}**
- summed solve wall: **{hms(mb["solve_wall_seconds"])}**

## Interpretation

The generic `C_m` B-layer is valid and demonstrably helpful on the known `(6,3^7)` control, but under this matched-seed monolithic budget it did **not** convert any of the 137 open O3 types from TIMEOUT to UNSAT.

The next research phase should therefore prioritize **structured decomposition / cubing**, using Task03 as the successful model, rather than simply extending the same monolithic A/B timeout.

## Integrity

- Freeze files hashed: **{summary["freeze"]["hashed_files"]}**
- `SHA256SUMS.txt` SHA256: `{summary["freeze"]["sha256sums_sha256"]}`

Raw campaign artifacts remain outside Git in the project freeze. Git receives this report, the machine-readable summary, the per-type table, and the exact source used for the campaign.
""")
    return js, tsv, md

def main():
    if not RUN.is_dir():
        raise RuntimeError(f"missing run directory: {RUN}")
    runner = REPO / RUNNER_REL
    panel = REPO / PANEL_REL
    rsha = sha256_file(runner)
    psha = sha256_file(panel)
    if rsha != EXPECTED_RUNNER_SHA256:
        raise RuntimeError(f"runner SHA256 mismatch: {rsha}")
    if psha != EXPECTED_PANEL_SHA256:
        raise RuntimeError(f"panel SHA256 mismatch: {psha}")

    manifest = json.loads((RUN / "manifest.json").read_text())
    if manifest.get("instances") != 278 or manifest.get("workers") != 20 or manifest.get("timeout") != 5760:
        raise RuntimeError("manifest configuration mismatch")
    if manifest.get("layers") != ["A", "B"]:
        raise RuntimeError("manifest A/B layer design mismatch")
    # Matched seeds/CPUs are not stored as dedicated manifest fields in this
    # runner version. They are audited directly and exhaustively from all
    # 139 completed per-type JSON records in load_states().

    states = load_states()
    status, layer_status, layer_tau, metrics, unsat, rows = aggregate(states)
    validate(status, layer_status, unsat)
    controls = control_info(states)

    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")

    metadata = {
        "milestone": "O3_BREADTH1_AB_MATCHED_20260905",
        "created_at": datetime.now().astimezone().isoformat(),
        "source_run": str(RUN),
        "git_head_before_report": head,
        "git_branch": branch,
        "runner_sha256": rsha,
        "smt_panel_sha256": psha,
        "status": dict(status),
        "layer_status": {k: dict(v) for k, v in layer_status.items()},
        "unsat_unverified": unsat,
    }

    print("FINAL_AUDIT PASS")
    print("TYPES 139 INSTANCES 278")
    print("STATUS", dict(status))
    print("A", dict(layer_status["A"]))
    print("B", dict(layer_status["B"]))
    print("UNSAT_JOBS", sorted({x["job_id"] for x in unsat}))
    print("MATCHED_SEEDS 139/139")
    print("MATCHED_CPUS 139/139")
    print("RUNNER_SHA256", rsha)
    print("GIT_HEAD", head)
    print("GIT_BRANCH", branch)

    nfiles, sums_sha = freeze_copy(metadata)

    summary = {
        "schema": 1,
        "milestone": "O3_BREADTH1_AB_MATCHED_20260905",
        "created_at": datetime.now().astimezone().isoformat(),
        "counts": {"types": 139, "instances": 278},
        "status": dict(status),
        "layer_status": {k: dict(v) for k, v in layer_status.items()},
        "layer_tau_status": {f"{ly}/tau{tau}": dict(v) for (ly, tau), v in sorted(layer_tau.items())},
        "layer_metrics": {
            ly: {
                "conflicts": int(v["conflicts"]),
                "decisions": int(v["decisions"]),
                "propagations": int(v["propagations"]),
                "solve_wall_seconds": float(v["solve_wall_seconds"]),
                "child_cpu_seconds": float(v["child_cpu_seconds"]),
            } for ly, v in metrics.items()
        },
        "unsat_unverified": unsat,
        "controls": controls,
        "open_types_result": {
            "count": 137,
            "A": {"TIMEOUT": 137, "UNSAT_UNCERTIFIED": 0},
            "B": {"TIMEOUT": 137, "UNSAT_UNCERTIFIED": 0},
            "new_unsat_candidates": 0,
        },
        "manifest": manifest,
        "provenance": {
            "source_run": str(RUN),
            "runner_sha256": rsha,
            "smt_panel_sha256": psha,
        },
        "git": {"head": head, "branch": branch},
        "freeze": {
            "path": str(FREEZE),
            "hashed_files": nfiles,
            "sha256sums_sha256": sums_sha,
        },
        "certification_note": (
            "UNSAT_UNCERTIFIED is a scout outcome, not a new certified exclusion. "
            "(6,3^7) was already fully certified in the previous FULLCERT milestone."
        ),
    }

    js, tsv, md = write_reports(summary, rows)

    print("FREEZE_OK", FREEZE)
    print("HASHED_FILES", nfiles)
    print("SHA256SUMS_SHA256", sums_sha)
    print("REPORT_JSON", js.relative_to(REPO), sha256_file(js))
    print("REPORT_TSV", tsv.relative_to(REPO), sha256_file(tsv))
    print("REPORT_MD", md.relative_to(REPO), sha256_file(md))
    print("FINALIZE_PREPARED_OK")
    print("NO_GIT_COMMIT_TAG_OR_PUSH_YET")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FINALIZE_FAILED:", e, file=sys.stderr)
        sys.exit(1)
