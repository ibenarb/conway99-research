"""Validate 39 jobs and report primary pairs separately from record hunting."""
import boot
from util import *
from search import key
from prepare import verify

def evaluate(run):
    plan = verify(run)
    results = {}
    total_new = 0
    for job in plan["jobs"]:
        d = run / job["directory"]
        r = receipt_valid(d)
        result = read(d / "result.json")
        if r["status"] != "COMPLETE" or result["endpoint_cpu_seconds"] != job["cumulative_budget_seconds"]:
            raise RuntimeError("Missing clean endpoint: " + job["id"])
        if not job["cumulative_budget_seconds"] - 5.1 <= r["budget_cpu_seconds"] <= job["cumulative_budget_seconds"]:
            raise RuntimeError("Unexpected job CPU consumption")
        for item in [result["best"], result["current"]] + result["curves"] + result["final_population"] + list(result["observed_best"].values()):
            if checked(item["graph6"], "lambda")[1] != item["scores"]:
                raise RuntimeError("Invalid endpoint graph/score")
        curves = result["curves"]
        if not all(a["cpu"] <= b["cpu"] and key(a["scores"], job["target"]) > key(b["scores"], job["target"])
                   for a, b in zip(curves, curves[1:])):
            raise RuntimeError("Invalid improvement curve")
        if any(not 0 <= p["cpu"] <= job["cumulative_budget_seconds"] for p in curves):
            raise RuntimeError("Curve outside budget")
        initial = run / "initial" / job["id"] / "result.json"
        if initial.exists():
            old = read(initial)
            if curves[:len(old["curves"])] != old["curves"]:
                raise RuntimeError("Old curve changed")
            for m in ("600", "1800", "3600"):
                if result["milestones"][m] != old["milestones"][m]:
                    raise RuntimeError("Old milestone changed")
        marks = [600, 1800, 3600, 7200] if job["group"] == "record" else [600, 1800, 3600, 7200, 10800, 14400]
        milestones = {}
        for mark in marks:
            point = next(p for p in reversed(curves) if p["cpu"] <= mark)
            stored = result["milestones"].get(str(mark))
            if stored and (stored["scores"] != point["scores"] or stored["graph6"] != point["graph6"]):
                raise RuntimeError("Milestone/curve mismatch")
            milestones[str(mark)] = point
        new_cpu = r["cpu_seconds"] - job["initial_actual_cpu"]
        if new_cpu > job["additional_cpu_seconds"] + 0.01:
            raise RuntimeError("Additional CPU exceeded")
        total_new += new_cpu
        results[job["id"]] = {"best": result["best"], "observed_best": result["observed_best"],
                             "milestones": milestones, "curves": curves,
                             "new_cpu_seconds": new_cpu, "replayed_moves": result["replayed_moves"],
                             "closed_reserve_cpu_seconds": r["closed_reserve_cpu_seconds"],
                             "restarts": result["restarts"], "episodes": result["episodes"],
                             "iterations": result["iterations"], "histogram": result["histogram"]}
    comparisons = []
    for mark in (3600, 7200, 10800, 14400):
        pairs = [[results[f"{v}--W-{i:02d}"]["milestones"][str(mark)]["scores"]
                  for v in ("Pext", "PC")] for i in range(12)]
        wins = sum(key(b, "W") < key(a, "W") for a, b in pairs)
        losses = sum(key(b, "W") > key(a, "W") for a, b in pairs)
        comparisons.append({"mark": mark, "PC_wins": wins, "ties": 12-wins-losses,
                            "PC_losses": losses, "paired_scores": pairs})
    ledger = read(run / "auxiliary_ledger.json")
    aux = {category: sum(e["cpu_seconds"] for e in ledger["entries"] if e["category"] == category)
           for category in AUX_LIMITS}
    result = {"status": "FOLLOWUP_VERIFIED", "jobs": results, "primary_PC_vs_Pext": comparisons,
              "new_search_cpu_hours": total_new / 3600, "auxiliary_cpu_seconds_at_evaluation": aux,
              "TCx_below_W2141": sum(results[f"TCx--W-{i:02d}"]["best"]["scores"]["W"] < 2141 for i in range(3)),
              "record_results": {k: v for k, v in results.items() if k.startswith("R-")},
              "scope": "Exploratory paired follow-up, reused seeds; record track separate",
              "automatic_extension": False}
    atomic(run / "EVALUATION.json", result)
    return {k: v for k, v in result.items() if k not in ("jobs", "record_results")}
