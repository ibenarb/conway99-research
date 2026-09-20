"""Read-only source intake and one-time, bounded Ryzen preparation manifest."""
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile

from common import ROOT, BASE, VERSION, atomic, checked, core, cpu, sha
from resources import snapshot, GIB, HOST_RESERVE, LINUX_RESERVE


def read(path):
    return json.loads((ROOT / path).read_text())


def sources():
    for item in read("data/memetic_v2/reference/provenance.json"):
        name = item["founder"]
        family = ("HoG" if name.lower().startswith("hog") else
                  "Z14" if "Z14" in name else
                  "Z2_template" if "Z2" in name else
                  "B_Maple" if name.startswith("B_") else "A_legacy")
        yield dict(id=name, arm=item["arm"], family=family,
                   source="data/memetic_v2/reference/" + item["file"],
                   expected_sha256=item["sha256"], parents=[], metadata=item["source"],
                   control_only=family == "A_legacy")
    intake = "data/memetik/ai_candidates/"
    codex = {x["candidate_id"]: x for x in read(intake + "submissions/20260915_codex_v01/submission.json")["candidates"]}
    for item in read(intake + "registry.json")["accepted_candidates"]:
        meta = read(intake + item["metadata_path"])
        ident = item["id"]
        family = ("F02" if meta.get("source_family_id") == "F02" else
                  "Z33_lift" if meta.get("source_family_id") in ("F03", "F04") else
                  "free_Omega_CSP" if ident.startswith("gemini") else
                  "triangle_packing" if ident == "claude_v01_c" else "Z14")
        original = codex.get(meta.get("source_candidate_id"), {})
        yield dict(id=ident, arm=item["arm"], family=family,
                   source=intake + item["path"], expected_sha256=item["sha256"],
                   seed=original.get("seed", meta.get("seed")),
                   generator_args=meta.get("generator_args"),
                   generation_cost=original.get("runtime"),
                   parents=meta.get("parents", []), metadata_path=intake + item["metadata_path"],
                   source_archive_commit=item["source_archive_commit"], control_only=False)
    base = "results/memetik/office_pilot_001_20260912/"
    for stem in ("B_descendant_L1", "B_descendant_L2", "B_descendant_Linf", "lambda_Linf2_00"):
        is_b = stem.startswith("B_")
        yield dict(id=stem, arm="omega" if is_b else "lambda", family="B_Maple" if is_b else "HoG",
                   source=base + stem + ".g6", parents=["B_maple_20260829" if is_b else "hog57338"],
                   metadata_path=base + stem + ".json", control_only=False)
    path = "results/memetik/minimax_20260919/B_escape_W2082__bfs_W.json"
    witness = read(path)["witness"]["path"][-1]
    yield dict(id="B_W2080", arm="omega", family="B_Maple", source=path,
               graph6=witness["graph6"], parents=["B_escape_W2082"], control_only=False,
               preparation_required="bounded descent/census; not a proven local minimum")
    anchor_path = "experiments/memetik/ryzen_compare_0_4_0/quality_anchor.json"
    yield dict(read(anchor_path), source=anchor_path)


def registry():
    entries = []
    first_class = {}
    for item in sources():
        data = (ROOT / item["source"]).read_bytes()
        if item.get("expected_sha256") and sha(data) != item["expected_sha256"]:
            raise ValueError("Source SHA256 mismatch: " + item["source"])
        text = item.get("graph6", data.decode().strip())
        started = cpu()
        rows, scores = checked(text, item["arm"])
        checked_cpu = cpu() - started
        started = cpu()
        # Exact certificate retained, hash for indexing. Never use uncolored
        # identity to quotient labelled Omega search states.
        import pynauty
        graph = pynauty.Graph(99, adjacency_dict={i: list(core.vertices(r)) for i, r in enumerate(rows)})
        certificate = pynauty.certificate(graph).hex()
        canonical_cpu = cpu() - started
        identity = (item["arm"], certificate)
        duplicate = first_class.get(identity)
        first_class.setdefault(identity, item["id"])
        entries.append(dict(item, graph6=text, source_file_sha256=sha(data),
                            graph6_lf_sha256=sha((text + "\n").encode()), scores=scores,
                            exact_nauty_certificate_hex=certificate,
                            class_sha256=sha(bytes.fromhex(certificate)), duplicate_of=duplicate,
                            independent_validation_cpu=checked_cpu, canonical_cpu=canonical_cpu,
                            omega_frame={"root": 0, "canonical_to_graph6": list(range(99)),
                                         "outer_pairs": core.OUTER} if item["arm"] == "omega" else None,
                            basin_novelty="not established"))
    counts = {arm: len({e["exact_nauty_certificate_hex"] for e in entries
                       if e["arm"] == arm and not e["control_only"]}) for arm in ("omega", "lambda")}
    return {"version": VERSION, "base_commit": BASE, "entries": entries,
            "unique_eligible_by_arm": counts, "selection_frozen": False,
            "generation_cost_note": "null means unknown; no inferred zero generation cost",
            "families": {arm: dict(Counter(e["family"] for e in entries
                         if e["arm"] == arm and not e["duplicate_of"] and not e["control_only"]))
                         for arm in counts}}


def jobs():
    result = []
    for replicate in range(9):
        seed = core.derive_seed(2026092004, ["confirmation", replicate])
        for arm in ("omega", "lambda"):
            for target in ("W", "L1", "F", "Linf"):
                for variant in ("A0", "A1"):
                    result.append(dict(id=f"{arm}-{target}-{replicate:02d}-{variant}",
                                       replicate=replicate, seed=seed, arm=arm, target=target,
                                       variant=variant, worker_cpu_seconds=3600))
    return {"version": VERSION, "jobs": result,
            "total_worker_cpu_seconds": sum(j["worker_cpu_seconds"] for j in result),
            "independent_unit": "complete paired run seed", "launch_enabled": False,
            "decision": {"primary": "best active objective at CPU endpoint; W/L1 and Linf/Nmax/L1 lexicographic",
                         "test": "one-sided exact sign test; ties excluded and reported",
                         "multiplicity": "Holm over eight arm/target tests", "alpha": 0.05,
                         "unclear_default": "A0"}}


def main():
    started = cpu()
    workspace = Path.home() / "conway99_workspace"
    workspace.mkdir(exist_ok=True)
    report = snapshot(workspace)
    report.update(distribution=os.environ.get("WSL_DISTRO_NAME"), hostname=platform.node(),
                  affinity=sorted(os.sched_getaffinity(0)), load_average=os.getloadavg(),
                  utc=datetime.now(timezone.utc).isoformat(), version=VERSION,
                  host_reserve_gib=HOST_RESERVE//GIB, linux_reserve_gib=LINUX_RESERVE//GIB)
    # A host probe failure stops before candidate preparation. No silent fallback
    # to Linux free space, no attempt to start research jobs.
    if not report["may_launch"]:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        raise SystemExit("PREPARATION_BLOCKED")
    output = Path(tempfile.mkdtemp(prefix="ryzen_compare_prepare_", dir=workspace))
    report["git_head"] = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    report["lscpu"] = subprocess.check_output(["lscpu", "-J"], text=True)
    report["processes"] = subprocess.check_output(["ps", "-eo", "pid,comm,pcpu,pmem,rss", "--sort=-pcpu"], text=True).splitlines()[:21]
    atomic(output / "host.json", report)
    candidates = registry()
    atomic(output / "founder_registry.json", candidates)
    matrix = jobs()
    atomic(output / "job_manifest.json", matrix)
    atomic(output / "preparation.json", {"status": "INTAKE_AND_HOST_PASS", "cpu_seconds": cpu()-started,
                                          "comparison_started": False, "configuration_frozen": False})
    print(json.dumps({"status": "INTAKE_AND_HOST_PASS", "directory": str(output),
                      "host_drive": report["host"]["drive_letter"],
                      "host_free_gib": round(report["host"]["physical_free_bytes"]/GIB, 2),
                      "linux_free_gib": round(report["linux_free_bytes"]/GIB, 2),
                      "affinity_cpus": len(report["affinity"]),
                      "unique_eligible_by_arm": candidates["unique_eligible_by_arm"],
                      "families": candidates["families"], "jobs": len(matrix["jobs"]),
                      "comparison_cpu_hours": matrix["total_worker_cpu_seconds"]/3600,
                      "comparison_started": False}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
