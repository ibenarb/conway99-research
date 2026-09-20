"""Detached bounded calibration and explicitly separate confirmation launch."""
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
import tempfile
import time
import uuid

from common import ROOT, atomic, core, sha, checked
from prepare import jobs
from runtime import HERE, Pool, THREAD_ENV, fingerprint, immutable, read
from resources import snapshot
from search import identity, key
from generate import structure

TRAINING = {"omega": ["B_maple_20260829", "codex_v01_c01"],
            "lambda": ["hog57177", "codex_v01_c07"]}
BASE_CONFIG = {"perturb_cpu": 45, "descent_cpu": 75, "sample_size": 32,
               "neutral_limit": 32, "memory_states": 128, "linf_plus_one_fraction": 0,
               "fresh_fraction": 0, "redistributed_recipe_weights": [4, 3, 2],
               "crossover_fraction": 0, "migration": False, "population": 16,
               "thresholds": {}, "practical_relative_median_gain": 0.005,
               "closing_reserve_cpu": 2.0}


def as_candidate(entry):
    return {"graph6": entry["graph6"], "scores": entry["scores"], "family": entry["family"],
            "line": entry["id"], "parent": None, "state": identity(entry["graph6"]),
            "class": entry["class_sha256"],
            "fixed_source_template_holds": structure(core.decode_g6(entry["graph6"]), entry["family"])}


def pick(pool, arm, exclude):
    unique = {}
    for item in pool:
        if item["line"] not in exclude:
            unique.setdefault(item["class"], item)
    candidates = list(unique.values())
    if len(candidates) < 16:
        raise RuntimeError(f"Only {len(candidates)} distinct {arm} founders after training/holdout split; no cloned filler")
    selected = []
    # Four quality anchors, then representation, then balanced source counts.
    for target in ("W", "L1", "F", "Linf"):
        best = min(candidates, key=lambda p: (key(p["scores"], target), p["line"]))
        if best not in selected:
            selected.append(best)
    for family in sorted({p["family"] for p in candidates}):
        if not any(p["family"] == family for p in selected):
            selected.append(min((p for p in candidates if p["family"] == family),
                                key=lambda p: (p["scores"]["F"], p["line"])))
    while len(selected) < 16:
        counts = Counter(p["family"] for p in selected)
        rest = [p for p in candidates if p not in selected]
        selected.append(min(rest, key=lambda p: (counts[p["family"]], p["scores"]["F"], p["line"])))
    return selected


def calibrate(directory, pool):
    intake = read(directory / "intake.json")
    entries = intake["entries"]
    original = {e["id"]: as_candidate(e) for e in entries if not e["control_only"]}
    # Fixed, finite generator batch. No dependence on success to enlarge budget.
    generators = []
    for arm, count, family in (("omega", 8, "F02"), ("lambda", 24, "Z33_lift")):
        for index in range(count):
            generators.append({"id": f"gen-{arm}-{index:02d}", "kind": "generate", "arm": arm,
                               "family": family, "seed": 20260920+index, "worker_cpu_seconds": 60})
    generated = pool.run(generators, 12, "generation")
    all_candidates = {arm: [p for p in original.values()
                           if next(e["arm"] for e in entries if e["id"] == p["line"]) == arm]
                      for arm in ("omega", "lambda")}
    new_candidates = {arm: [] for arm in all_candidates}
    for task, output in zip(generators, generated["results"]):
        if output["candidate"]:
            item = output["candidate"]
            if item["class"] not in {p["class"] for p in all_candidates[task["arm"]]}:
                all_candidates[task["arm"]].append(item)
                new_candidates[task["arm"]].append(item)
    holdout = {}
    for arm in all_candidates:
        if not new_candidates[arm]:
            raise RuntimeError("No unused generated transfer founder: " + arm)
        holdout[arm] = new_candidates[arm][-1]
    census = pool.run([{"id": "B-W2080-descent-census", "kind": "census", "arm": "omega",
                        "parent": original["B_W2080"], "seed": 2026092004,
                        "worker_cpu_seconds": 900}], 1, "b_census")
    b = census["results"][0]["candidate"]
    if b["scores"]["W"] < original["B_W2080"]["scores"]["W"]:
        all_candidates["omega"] = [b if p["line"] == "B_W2080" else p for p in all_candidates["omega"]]
    selected = {arm: pick(all_candidates[arm], arm, TRAINING[arm]+[holdout[arm]["line"]])
                for arm in all_candidates}
    # Split is fixed BEFORE collecting threshold observations.
    immutable(directory / "founder_split.json", {"training": TRAINING, "holdout": holdout, "confirmation": selected})
    training = [{"id": "train-"+ident, "kind": "train", "arm": arm, "seed": 2026092004,
                 "parent": original[ident], "worker_cpu_seconds": 240}
                for arm in TRAINING for ident in TRAINING[arm]]
    trained = pool.run(training, 4, "training")
    thresholds, observations = {}, {}
    for arm in TRAINING:
        thresholds[arm], observations[arm] = {}, {}
        for target in ("W", "L1", "F"):
            values = sorted(v for t, r in zip(training, trained["results"]) if t["arm"] == arm
                            for v in r["positive_deltas"][target])
            if len(values) < 32:
                raise RuntimeError(f"Insufficient positive trade calibration: {arm}/{target}: {len(values)}")
            thresholds[arm][target] = values[math.ceil(0.75*len(values))-1]
            observations[arm][target] = len(values)
    config = dict(BASE_CONFIG, thresholds=thresholds)
    immutable(directory / "trained_config.json", {"config": config, "positive_observations": observations,
                                                  "quantile": "nearest-rank 75 percent", "training": TRAINING})
    transfer = [{"id": f"transfer-{arm}-{target}-{variant}", "kind": "benchmark", "arm": arm,
                 "target": target, "variant": variant, "seed": 2026092005, "parent": holdout[arm],
                 "worker_cpu_seconds": 130, "episode_limit": 1, "config": config}
                for arm in holdout for target in ("W", "L1", "F", "Linf") for variant in ("A0", "A1")]
    pool.run(transfer, 12, "transfer")
    # The transfer outcomes are reported, never used to retune thresholds.
    benchmarks = []
    for workers in (12, 18, 24):
        path = directory / f"throughput_{workers}.json"
        if path.exists():
            benchmarks.append(read(path))
            continue
        tasks = [{"id": f"bench-{workers}-{arm}-{target}-{variant}-{rep}", "kind": "benchmark",
                  "arm": arm, "target": target, "variant": variant, "seed": 2026092010+rep,
                  "parent": original[TRAINING[arm][rep]], "worker_cpu_seconds": 130, "config": config}
                 for rep in range(2) for arm in ("omega", "lambda") for target in ("W", "L1", "F", "Linf")
                 for variant in ("A0", "A1")]
        measured = pool.run(tasks, workers, f"throughput_{workers}")
        if any(r["status"] != "VALID" for r in measured["results"]):
            raise RuntimeError("Interrupted throughput batch; no worker-count decision from partial samples")
        valid = sum(r["valid_completed_episodes"] for r in measured["results"])
        reached = sum(r["minimum_reached"] for r in measured["results"])
        report = {"workers": workers, "valid_completed_episodes": valid, "minimum_reached": reached,
                  "cpu_seconds": measured["cpu_seconds"], "wall_seconds": measured["wall_seconds_this_session"],
                  "valid_episodes_per_wall_second": valid/measured["wall_seconds_this_session"]}
        atomic(path, report)
        benchmarks.append(report)
    winner = max(benchmarks, key=lambda r: r["valid_episodes_per_wall_second"])
    confirmation = jobs()
    for task in confirmation["jobs"]:
        task.update(kind="compare", config=config, founders=selected[task["arm"]])
    confirmation.update(launch_enabled=True, workers=winner["workers"], config=config,
                        fingerprint=read(directory / "fingerprint.json"),
                        decision=dict(confirmation["decision"], practical_relative_median_gain=0.005))
    immutable(directory / "confirmation.json", confirmation)
    summary = {"status": "READY_FOR_CONFIRMATION", "workers": winner["workers"],
               "thresholds": thresholds, "founders": {arm: len(v) for arm, v in selected.items()},
               "families": {arm: dict(Counter(p["family"] for p in v)) for arm, v in selected.items()},
               "confirmation_manifest_sha256": sha((directory / "confirmation.json").read_bytes()),
               "preparation_worker_cpu_hours": sum(r["cpu_seconds"] for r in pool.receipts())/3600,
               "throughput": benchmarks, "comparison_started": False}
    atomic(directory / "calibration_result.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


def controller(directory, phase):
    directory = directory.resolve()
    if read(directory / "fingerprint.json") != fingerprint():
        raise RuntimeError("Code or runtime changed; refuse mixed-version continuation")
    pool = Pool(directory)
    if (directory / "controller_error.json").exists():
        (directory / "controller_error.json").rename(directory / ("controller_error_"+uuid.uuid4().hex+".json"))
    if len(os.sched_getaffinity(0)) < 24:
        raise RuntimeError("Expected calibrated Ryzen affinity of 24 CPUs")
    try:
        if phase == "calibrate":
            calibrate(directory, pool)
        else:
            frozen = read(directory / "confirmation.json")
            frozen_hash = sha((directory / "confirmation.json").read_bytes())
            if frozen_hash != read(directory / "calibration_result.json")["confirmation_manifest_sha256"]:
                raise RuntimeError("Frozen confirmation manifest changed")
            if not frozen["launch_enabled"] or frozen["total_worker_cpu_seconds"] != 518400:
                raise RuntimeError("Invalid comparison budget")
            # Round-robin task ordering has one entry per arm/target before
            # filling the next seed/variant slots; equal total CPU per group.
            tasks = sorted(frozen["jobs"], key=lambda t: (t["replicate"], t["variant"], t["arm"], t["target"]))
            pool.run(tasks, frozen["workers"], "confirmation")
            from evaluate import evaluate
            report = evaluate(directory)
            atomic(directory / "evaluation.json", report)
            print(json.dumps(report, indent=2), flush=True)
    except Exception as error:
        # Context remains on disk; no new budget is assigned on resume.
        pool.emergency_stop_owned()
        atomic(directory / "controller_error.json", {"phase": phase, "error": str(error)})
        raise
    finally:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        atomic(directory / ("controller_cpu_"+uuid.uuid4().hex+".json"),
               {"phase": phase, "cpu_seconds": usage.ru_utime+usage.ru_stime})


def launch(directory, phase):
    # Parent performs the same fail-closed guard before detaching.
    report = snapshot(directory)
    if not report["may_launch"]:
        raise RuntimeError(json.dumps(report))
    with (directory / "console.log").open("ab") as log:
        entry = directory / "bundle/experiments/memetik/ryzen_compare_0_4_0/campaign.py"
        if not entry.is_file():
            raise RuntimeError("Frozen code bundle missing")
        child = subprocess.Popen([sys.executable, str(entry), "controller", str(directory),
                                  "--phase", phase], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                 start_new_session=True, env={**os.environ, **THREAD_ENV})
    print(json.dumps({"status": "LAUNCHED", "phase": phase, "directory": str(directory), "pid": child.pid,
                      "comparison_started": phase == "compare"}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "controller", "resume", "compare", "status", "export"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--phase", choices=("calibrate", "compare"), default="calibrate")
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.action == "prepare":
        intake = read(directory / "founder_registry.json")
        for entry in intake["entries"]:
            rows, scores = checked(entry["graph6"], entry["arm"])
            if scores != entry["scores"] or core.canonical(rows) != entry["class_sha256"]:
                raise ValueError("Intake file changed or canonicalizer differs: " + entry["id"])
        run = Path(tempfile.mkdtemp(prefix="ryzen_compare_041_", dir=Path.home() / "conway99_workspace"))
        atomic(run / "intake.json", intake)
        signature = fingerprint()
        atomic(run / "fingerprint.json", signature)
        for relative, digest in signature["files"].items():
            data = (ROOT / relative).read_bytes()
            if sha(data) != digest:
                raise RuntimeError("Source changed while freezing bundle")
            destination = run / "bundle" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as handle:
                handle.write(data)
        atomic(run / "preparation_source.json", {"directory": str(directory),
                                                 "registry_sha256": sha((directory / "founder_registry.json").read_bytes()),
                                                 "git_head": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()})
        launch(run, "calibrate")
    elif args.action == "controller":
        controller(directory, args.phase)
    elif args.action in ("resume", "compare"):
        launch(directory, "compare" if args.action == "compare" else args.phase)
    elif args.action == "export":
        from evaluate import export
        print(export(directory))
    else:
        name = "status.json"
        if (directory / "evaluation.json").exists():
            name = "evaluation.json"
        elif (directory / "calibration_result.json").exists():
            if not (directory / "status.json").exists() or read(directory / "status.json")["phase"] != "confirmation":
                name = "calibration_result.json"
        print(json.dumps(read(directory / name), indent=2))
        if (directory / "controller_error.json").exists():
            print(json.dumps(read(directory / "controller_error.json"), indent=2))


if __name__ == "__main__":
    main()
