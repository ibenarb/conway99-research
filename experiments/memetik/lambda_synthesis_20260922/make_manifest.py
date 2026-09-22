"""Build a reviewable, non-launching manifest and deterministic slot schedule."""
from pathlib import Path
import hashlib
import heapq
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/memetik/lambda_synthesis_20260922"
FROZEN = ROOT / "experiments/memetik/lambda_compare_0_2_0"
sys.path.insert(0, str(FROZEN))
import bootstrap
from common import core

def load(path):
    return json.loads(path.read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def key(s, target):
    return tuple(s[k] for k in {"W": ("W", "L1"), "L1": ("L1",),
                               "Linf": ("Linf", "Nmax", "L1")}[target])

def main():
    source = load(ROOT / "docs/memetik/lambda_plan_codex_20260922/SOURCE_CHECK.json")
    assert all(digest(ROOT / p) == h for p, h in source["sha256"].items())
    founders = load(FROZEN / "founders.json")
    witness = load(OUT / "WITNESS_CHECK.json")
    old_descents = load(ROOT / "docs/memetik/lambda_plan_codex_20260922/POSTRUN_DESCENTS.json")
    census = load(ROOT / "docs/memetik/lambda_results_20260922/RECORD_CENSUS.json")
    records = {
        "W": {"graph6": witness["descended_graph6"], "scores": witness["descended_scores"],
              "origin": "Reviewer W2116 followed by one verified pivot in this synthesis"},
        "Linf": {"graph6": old_descents["Linf"]["graph6"], "scores": old_descents["Linf"]["scores"],
                 "origin": "Codex post-run Linf witness c91fbdf"},
        "L1": {"graph6": census["observed_L1"]["graph6"], "scores": census["observed_L1"]["scores"],
               "origin": "Historical observed L1 record at 84c46aa"}
    }
    starters = {}
    for target, record in records.items():
        record["state_sha256"] = hashlib.sha256(record["graph6"].encode()).hexdigest()
        worst = max(range(len(founders)),
                    key=lambda i: (key(founders[i]["scores"], target), founders[i]["state"]))
        assert key(record["scores"], target) < min(key(f["scores"], target) for f in founders)
        starters[target] = dict(replace_index=worst, replaced_founder=founders[worst],
                                record=record, preserve_other_founders_and_order=True,
                                canonical_check="Required on Ryzen with pinned pynauty before launch")
    receipts = load(ROOT / "docs/memetik/lambda_results_20260922/RECEIPTS.json")
    jobs = []
    for i in range(12):
        seed = core.derive_seed(2026092104, ["lambda-compare", i])
        old = f"P--lambda-W-{i:02d}"
        jobs.append(dict(id=f"Pext--W-{i:02d}", group="method", variant="P", target="W",
                         replicate=i, seed=seed, old_id=old, mode="resume_copy",
                         original_receipt=receipts[old],
                         old_budget_seconds=3600, cumulative_budget_seconds=14400,
                         additional_cpu_seconds=10800, rng="restore checkpoint",
                         population="unchanged original state", engine="frozen-0.2.0"))
        jobs.append(dict(id=f"PC--W-{i:02d}", group="method", variant="PC", target="W",
                         replicate=i, seed=seed, mode="fresh",
                         old_budget_seconds=0, cumulative_budget_seconds=14400,
                         additional_cpu_seconds=14400, population="original 16 founders",
                         engine="new version, only P catalogue expanded to APC"))
    for i in range(3):
        old = f"TC--lambda-W-{i:02d}"
        jobs.append(dict(id=f"TCx--W-{i:02d}", group="discriminator", variant="TC", target="W",
                         replicate=i, seed=core.derive_seed(2026092104, ["lambda-compare", i]),
                         old_id=old, mode="resume_copy", original_receipt=receipts[old],
                         old_budget_seconds=3600, cumulative_budget_seconds=14400,
                         additional_cpu_seconds=10800, rng="restore checkpoint",
                         population="unchanged original path", engine="frozen-0.2.0"))
    record_jobs = []
    for target, reps, variants in (("W", 3, ("P", "PC")), ("Linf", 4, ("P",)), ("L1", 2, ("P",))):
        for i in range(reps):
            seed = core.derive_seed(2026092202, ["lambda-record-synthesis", target, i])
            for variant in variants:
                job = dict(id=f"R-{variant}--{target}-{i:02d}", group="record",
                           variant=variant, target=target, replicate=i, seed=seed, mode="fresh",
                           old_budget_seconds=0, cumulative_budget_seconds=7200,
                           additional_cpu_seconds=7200, population=f"record_bank:{target}",
                           engine="frozen P decision rules or new PC catalogue")
                record_jobs.append(job)
                jobs.append(job)
    ids = {j["id"]: j for j in jobs}
    main_order = []
    for i in range(12):
        pair = [f"Pext--W-{i:02d}", f"PC--W-{i:02d}"]
        main_order.extend(pair if i % 2 == 0 else pair[::-1])
    r_ids = [j["id"] for j in record_jobs]
    queue = main_order + r_ids[:3] + [f"TCx--W-{i:02d}" for i in range(3)] + r_ids[3:]
    slots = [(0, i) for i in range(18)]
    heapq.heapify(slots)
    schedule = []
    for job_id in queue:
        start, slot = heapq.heappop(slots)
        end = start + ids[job_id]["additional_cpu_seconds"]
        schedule.append(dict(id=job_id, slot=slot, ideal_start_seconds=start, ideal_end_seconds=end))
        heapq.heappush(slots, (end, slot))
    total = sum(j["additional_cpu_seconds"] for j in jobs)
    assert len(jobs) == 39 and total == 117 * 3600
    makespan = max(s["ideal_end_seconds"] for s in schedule)
    manifest = dict(version="synthesis-proposal-1.0.0", date="2026-09-22",
                    authorized_to_launch=False, software_implemented=False, workers_max=18,
                    code_commit="b659cb8743dd6036d91dafb466b2d12cb21a29b0",
                    results_commit="84c46aac2b39d718c44daee2a7b994c29930e6c5",
                    original_source_files_rechecked=len(source["sha256"]),
                    founders_sha256=digest(FROZEN / "founders.json"),
                    primary="paired active (W,L1) PC vs Pext at cumulative 14400 budget CPU seconds",
                    claim_scope="Exploratory extension on reused seeds and founders, not new independent confirmation",
                    comparison_milestones=[600,1800,3600,7200,10800,14400],
                    record_milestones=[600,1800,3600,7200], jobs=jobs, queue=queue,
                    auxiliary_cpu_seconds={
                        "clocks_one_and_eighteen_workers": 3420,
                        "resume_and_PC_controls": 3780,
                        "readonly_observed_harvest": 3600,
                        "controller_hash_export_host_helpers": 3600
                    },
                    search_cpu_hours=117, auxiliary_cpu_hours=4, proposed_total_cpu_hours=121,
                    automatic_extensions=False, early_plateau_stops=False,
                    harvest_rule="Read OBSERVED records, deduplicate before validation; no silent replacement of frozen starters",
                    harvest_incomplete="Report coverage and remaining work; never claim exhaustive completion",
                    cpu_basis="Runtime self CPU, wait4 finalized accounting; no assumed post-hoc scaling",
                    eta_basis="Validated monotonic Windows host interval and measured throughput")
    (OUT / "PROPOSED_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")
    (OUT / "RECORD_BANK.json").write_text(json.dumps(starters, indent=2)+"\n")
    (OUT / "SCHEDULE.json").write_text(json.dumps(dict(assumption="One budget CPU second per occupied slot per real second; ideal model only",
        schedule=schedule, makespan_seconds=makespan, utilization=total/(18*makespan)), indent=2)+"\n")
    fields = ("id", "group", "variant", "target", "replicate", "seed", "mode",
              "old_budget_seconds", "cumulative_budget_seconds", "additional_cpu_seconds")
    (OUT / "PROPOSED_JOBS.tsv").write_text("\t".join(fields)+"\n"+"".join(
        "\t".join(str(j[f]) for f in fields)+"\n" for j in jobs))
    print(json.dumps(dict(jobs=len(jobs), search_hours=total/3600, auxiliary_hours=4,
                         total_hours=121, ideal_makespan_hours=makespan/3600,
                         replacements={t:x["replace_index"] for t,x in starters.items()},
                         source_files_rechecked=len(source["sha256"])), indent=2))

if __name__ == "__main__":
    main()
