"""Atomic semicolon CSV snapshots; one row per objective, arm and founder."""

from collections import defaultdict
import csv
import io
import json
import math
from pathlib import Path
import time

from core import objective_key
from runtime import atomic_bytes, atomic_json


def write_report(directory, state, status):
    directory = Path(directory)
    history = directory / "reports"
    history.mkdir(exist_ok=True)
    groups = defaultdict(list)
    for candidate in state["population"]:
        groups[(candidate["objective"], candidate["arm"], candidate["founder"])].append(candidate)
        groups[(candidate["objective"], candidate["arm"], "ALL")].append(candidate)
    sample_id = str(time.time_ns())
    records = []
    for (objective, arm, founder), population in sorted(groups.items()):
        row = {"sample_id": sample_id, "utc": status["utc"],
               "active_seconds": round(state["pilot_active_seconds"], 3),
               "phase": state["phase"], "generation": state["generation"],
               "objective": objective, "arm": arm, "founder": founder,
               "population_n": len(population),
               "objective_best_graph": min(population, key=lambda p: objective_key(p, objective))["canonical"]}
        for label, key in (("W", "W"), ("L1", "L1"), ("L2_squared", "F"), ("Linf", "Linf")):
            values = [p[key] for p in population]
            row[label + "_best"] = min(values)
            row[label + "_mean"] = round(sum(values) / len(values), 6)
            row[label + "_worst"] = max(values)
        row["L2_best"] = round(math.sqrt(min(p["F"] for p in population)), 6)
        row["L2_mean"] = round(sum(math.sqrt(p["F"]) for p in population) / len(population), 6)
        archive = [p for p in state.get("archive", []) if p["objective"] == objective and p["arm"] == arm and (founder == "ALL" or p["founder"] == founder)]
        for label, key in (("W", "W"), ("L1", "L1"), ("L2_squared", "F"), ("Linf", "Linf")):
            row[label + "_best_ever"] = min(p[key] for p in archive or population)
        row["best_definition"] = "independent_minimum_per_metric"
        total = state.get("variant_work", {}).get(objective, {})
        row["variant_completed_tasks"] = total.get("tasks", 0)
        row["variant_cpu_seconds"] = round(total.get("cpu_seconds", 0), 3)
        records.append(row)
    atomic_json(history / (sample_id + ".json"), records)
    # Rebuild from atomic snapshots: no torn row or duplicate append after a crash.
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(records[0]), delimiter=";", lineterminator="\n")
    writer.writeheader()
    for path in sorted(history.glob("*.json")):
        writer.writerows(json.loads(path.read_text()))
    atomic_bytes(directory / "convergence.csv", output.getvalue().encode("utf-8-sig"))
    print("CSV_STATUS utc;generation;objective;arm;founder;n;W_best;W_mean;L1_best;L1_mean;L2_squared_best;L2_squared_mean;Linf_best;Linf_mean", flush=True)
    for r in records:
        keys = ("utc", "generation", "objective", "arm", "founder", "population_n", "W_best", "W_mean", "L1_best", "L1_mean", "L2_squared_best", "L2_squared_mean", "Linf_best", "Linf_mean")
        print(";".join(str(r[k]) for k in keys), flush=True)
