"""Audit the completed Office 0.2.0 pilot, without modifying the run.
Usage: python3 src/memetik/audit_office_pilot.py ARCHIVE.tar.gz
Uses the standard library. Canonical certificates are imported provenance,
not independently recomputed (pynauty is not required).
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path, PurePosixPath
import copy
import csv
import gzip
import hashlib
import json
import math
import statistics
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/memetik/office_pilot_001_20260912"
EXPECTED = "00116bcbea8fb5013338d0a53327254e4651ae594b24844be1841101e6b94dc3"
OUTER = [(a, b) for a, b in combinations(range(14), 2) if b - a != 7]


def normalized(value):
    return json.dumps(json.loads(json.dumps(value, allow_nan=False)),
                      sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(text):
    values = [ord(c) - 63 for c in text.strip()]
    assert all(0 <= v < 64 for v in values)
    assert values[0] == 63 and values[1] < 63
    n = (values[1] << 12) + (values[2] << 6) + values[3]
    assert n == 99 and len(values) == 4 + (4851 + 5) // 6
    assert values[-1] & 7 == 0
    rows = [set() for _ in range(n)]
    k = 0
    for j in range(1, n):
        for i in range(j):
            if (values[4 + k // 6] >> (5 - k % 6)) & 1:
                rows[i].add(j)
                rows[j].add(i)
            k += 1
    return rows


CACHE = {}


def independent(candidate):
    key = (candidate["g6"], candidate["arm"])
    if key not in CACHE:
        rows = decode(candidate["g6"])
        assert all(len(row) == 14 and i not in row for i, row in enumerate(rows))
        hist = Counter()
        degrees = [0] * 99
        triangles3 = c4twice = bad = 0
        for i, j in combinations(range(99), 2):
            c = len(rows[i] & rows[j])
            edge = int(j in rows[i])
            r = c + edge - 2
            hist[r] += 1
            triangles3 += c * edge
            c4twice += c * (c - 1) // 2
            bad += bool(edge and r)
            if r:
                degrees[i] += 1
                degrees[j] += 1
        if candidate["arm"] == "lambda":
            assert bad == 0
        else:
            assert candidate["arm"] == "omega"
            assert rows[0] == set(range(1, 15))
            for a in range(14):
                assert rows[a + 1] == {0, (a + 7) % 14 + 1} | {
                    j + 15 for j, p in enumerate(OUTER) if a in p}
            for j, pair in enumerate(OUTER):
                assert rows[j + 15] & set(range(15)) == {a + 1 for a in pair}
                for a in range(14):
                    target = 1 if a in pair or (a + 7) % 14 in pair else 2
                    assert sum(i + 15 in rows[j + 15] for i, p in enumerate(OUTER) if a in p) == target
        linf = max(map(abs, hist))
        assert sum(r * c for r, c in hist.items()) == 0
        CACHE[key] = {"F": sum(r * r * c for r, c in hist.items()),
                      "W": sum(c for r, c in hist.items() if r),
                      "L1": sum(abs(r) * c for r, c in hist.items()),
                      "Linf": linf, "Nmax": sum(c for r, c in hist.items() if abs(r) == linf),
                      "lambda_bad": bad, "triangles": triangles3 // 3, "C4": c4twice // 2,
                      "residual_histogram": {str(r): c for r, c in hist.items()},
                      "defect_degrees": sorted(degrees), "max_defect_degree": max(degrees)}
    computed = CACHE[key]
    for name, value in computed.items():
        if name in candidate:
            assert candidate[name] == value, (name, candidate.get("line_id"))
    return computed


def rank(c, obj):
    if obj == "L1":
        return (c["L1"],)
    if obj == "L2":
        return (c["F"],)
    return (c["Linf"], c["Nmax"], c["L1"])


def distance(a, b):
    keys = set(a["residual_histogram"]) | set(b["residual_histogram"])
    return sum(abs(x - y) for x, y in zip(a["defect_degrees"], b["defect_degrees"])) + sum(
        abs(a["residual_histogram"].get(k, 0) - b["residual_histogram"].get(k, 0)) for k in keys)


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=4, sort_keys=True) + "\n")


def main(archive):
    data = Path(archive).read_bytes()
    assert sha(data) == EXPECTED
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
            assert all(not PurePosixPath(m.name).is_absolute() and ".." not in PurePosixPath(m.name).parts
                       and (m.isfile() or m.isdir()) for m in members)
            tar.extractall(temporary, filter="data")
        p = Path(temporary) / "pilot-001"
        status = json.loads((p / "status.json").read_text())
        assert status["phase"] == "COMPLETE" and status["stop_reason"] == "PILOT_BUDGET_COMPLETE"
        provenance = json.loads((p / "provenance.json").read_text())
        for filename, digest in provenance["files"].items():
            assert sha((ROOT / filename).read_bytes()) == digest, filename
        assert sha(normalized(provenance["files"])) == provenance["code_and_inputs_sha256"]
        config = json.loads((p / "config.resolved.json").read_text())
        assert sha(normalized(config)) == provenance["config_sha256"]
        checkpoints = []
        for path in (p / "checkpoints").glob("*.gz"):
            wrapper = json.load(gzip.open(path, "rt"))
            assert sha(normalized(wrapper["payload"])) == wrapper["sha256"]
            checkpoints.append(wrapper["payload"])
        state = max(checkpoints, key=lambda s: s["checkpoint_sequence"])
        population = json.loads((p / "population.json").read_text())["candidates"]
        archive_cs = json.loads((p / "best_archive.json").read_text())["candidates"]
        assert population == state["population"]
        assert archive_cs == state["archive"]
        entries = [json.loads(s) for s in (p / "logs/attempts.jsonl").read_text().splitlines()]
        assert len(entries) == status["completed_tasks"] == state["completed_tasks"]
        assert len({e["task"]["id"] for e in entries}) == len(entries)
        for e in entries:
            assert e["task"]["id"] == e["result"]["id"]
            assert e["task"]["seed"] == e["result"]["seed"]
        by_task = {e["task"]["id"]: e for e in entries}
        for task_id, result in state["results"].items():
            assert by_task[task_id]["result"] == result
        returned = [e["result"]["candidate"] for e in entries if e["result"].get("candidate")]
        starters = json.loads((ROOT / "data/memetic_v2/reference/population64.json").read_text())["candidates"]
        for c in starters:
            c.update(independent(c))
        for c in population + archive_cs + returned:
            independent(c)
        initial = []
        for obj in config["objectives"]:
            for original in starters:
                c = copy.deepcopy(original)
                c.update(objective=obj, line_id=obj + "-" + original["line_id"], stagnant_generations=0)
                initial.append(c)
        by_line = {c["line_id"]: c for c in initial}
        grouped_attempts = defaultdict(list)
        for e in entries:
            line = e["task"]["id"].split("-", 1)[1].rsplit("-", 1)[0]
            c = by_line[line]
            e["_objective"] = c["objective"]
            e["_arm"] = c["arm"]
            e["_founder"] = c["founder"]
            e["_line"] = line
            grouped_attempts[(c["objective"], c["arm"], e["task"]["kind"],
                              tuple(e["task"]["length"]))].append(e)
        cpu = sum(e["result"].get("cpu_seconds", 0) for e in entries)
        assert abs(cpu - state["cumulative_cpu_seconds"]) < 0.001
        records = []
        for group, es in sorted(grouped_attempts.items()):
            rs = [e["result"] for e in es]
            outcomes = Counter()
            for r in rs:
                outcomes.update(r.get("outcomes", {}))
            records.append(dict(objective=group[0], arm=group[1], method=group[2], length=list(group[3]),
                                tasks=len(es), cpu_seconds=sum(r.get("cpu_seconds", 0) for r in rs),
                                statuses=dict(Counter(r["status"] for r in rs)), outcomes=dict(outcomes),
                                returned=sum(r.get("candidate") is not None for r in rs),
                                evaluations=sum(r.get("evaluations", 0) for r in rs),
                                median_evaluations=statistics.median(r.get("evaluations", 0) for r in rs),
                                perturb_steps=sum(r.get("perturb_steps", 0) for r in rs),
                                median_perturb_steps=statistics.median(r.get("perturb_steps", 0) for r in rs),
                                below_requested_min=sum(e["result"].get("perturb_steps", 0) < e["task"]["length"][0] for e in es),
                                no_accepted_descent=sum(r.get("descent_steps", 0) == 0 for r in rs)))
        write_json("attempt_summary.json", records)

        # Independent reconstruction of the deterministic population selection.
        replay = copy.deepcopy(initial)
        selections = []
        snapshots = [copy.deepcopy(replay)]
        for generation in range(status["generation"]):
            relevant = [e for e in entries if e["task"]["id"].startswith(f"g{generation:06d}-")]
            assert len(relevant) == 1536
            line_results = defaultdict(list)
            for e in relevant:
                if e["result"].get("candidate"):
                    line_results[e["_line"]].append(e["result"]["candidate"])
            chosen = Counter()
            for position, parent in enumerate(list(replay)):
                others = [c for i, c in enumerate(replay) if i != position and c["objective"] == parent["objective"]]
                ids = {c["canonical"] for c in others}
                acceptable = [c for c in line_results[parent["line_id"]]
                              if rank(c, parent["objective"]) <= rank(parent, parent["objective"])
                              and c["canonical"] != parent["canonical"] and c["canonical"] not in ids]
                if acceptable:
                    best_rank = min(rank(c, parent["objective"]) for c in acceptable)
                    ties = [c for c in acceptable if rank(c, parent["objective"]) == best_rank]
                    child = copy.deepcopy(max(ties, key=lambda c: (
                        min((distance(c, q) for q in others), default=0), c["canonical"])))
                    strict = rank(child, parent["objective"]) < rank(parent, parent["objective"])
                    child.update(line_id=parent["line_id"], family=parent["family"], founder=parent["founder"],
                                 stagnant_generations=0 if strict else parent["stagnant_generations"] + 1)
                    replay[position] = child
                    chosen[(parent["objective"], parent["arm"], "strict" if strict else "neutral")] += 1
                else:
                    parent["stagnant_generations"] += 1
            selections.append({"generation": generation + 1,
                               "accepted": {"|".join(k): v for k, v in chosen.items()}})
            snapshots.append(copy.deepcopy(replay))
        for a, b in zip(replay, population):
            for name in ("g6", "canonical", "line_id", "founder", "stagnant_generations"):
                assert a[name] == b[name], (name, a["line_id"])
        write_json("selection_replay.json", {"status": "PASS", "generations": selections,
                    "canonical_scope": "Recorded certificates; not newly recomputed"})

        rows = list(csv.DictReader((p / "convergence.csv").open(encoding="utf-8-sig"), delimiter=";"))
        samples = defaultdict(list)
        for row in rows:
            samples[row["sample_id"]].append(row)
        assert len(samples) == 146 and all(len(rs) == 36 for rs in samples.values())
        reports = {}
        for path in (p / "reports").glob("*.json"):
            for r in json.loads(path.read_text()):
                reports[(r["sample_id"], r["objective"], r["arm"], r["founder"])] = r
        for row in rows:
            rr = reports[(row["sample_id"], row["objective"], row["arm"], row["founder"])]
            assert all(str(rr[k]) == v for k, v in row.items())
            pop = [c for c in snapshots[int(row["generation"])] if c["objective"] == row["objective"]
                   and c["arm"] == row["arm"] and (row["founder"] == "ALL" or c["founder"] == row["founder"])]
            assert len(pop) == int(row["population_n"])
            for label, key in (("W", "W"), ("L1", "L1"), ("L2_squared", "F"), ("Linf", "Linf")):
                assert min(c[key] for c in pop) == int(row[label + "_best"])
                assert max(c[key] for c in pop) == int(row[label + "_worst"])
                assert abs(sum(c[key] for c in pop) / len(pop) - float(row[label + "_mean"])) <= 0.000001
        group_rows = []
        for obj in config["objectives"]:
            for arm in ("omega", "lambda"):
                for founder in ["ALL"] + sorted({c["founder"] for c in initial if c["arm"] == arm}):
                    a = [c for c in initial if c["objective"] == obj and c["arm"] == arm and (founder == "ALL" or c["founder"] == founder)]
                    b = [c for c in population if c["objective"] == obj and c["arm"] == arm and (founder == "ALL" or c["founder"] == founder)]
                    all_seen = a + [c for c in returned if c["objective"] == obj and c["arm"] == arm and (founder == "ALL" or c["founder"] == founder)]
                    record = {"objective": obj, "arm": arm, "founder": founder, "n": len(a),
                              "strictly_improved_lines": sum(rank(y, obj) < rank(x, obj) for x, y in zip(a, b)),
                              "changed_lines": sum(x["canonical"] != y["canonical"] for x, y in zip(a, b)),
                              "start_objective_best": list(min(rank(c, obj) for c in a)),
                              "end_objective_best": list(min(rank(c, obj) for c in b)),
                              "returned_objective_best": list(min(rank(c, obj) for c in all_seen))}
                    for key in ("W", "L1", "F", "Linf"):
                        record.update({key + "_start_best": min(c[key] for c in a),
                                       key + "_end_best": min(c[key] for c in b),
                                       key + "_ever_returned_best": min(c[key] for c in all_seen),
                                       key + "_start_mean": statistics.mean(c[key] for c in a),
                                       key + "_end_mean": statistics.mean(c[key] for c in b)})
                    group_rows.append(record)
        write_json("founder_summary.json", group_rows)
        with (OUT / "founder_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(group_rows[0]), delimiter=";")
            writer.writeheader()
            writer.writerows(group_rows)
        witnesses = [c for c in population if c["Linf"] == 2]
        assert witnesses
        for i, c in enumerate(witnesses):
            (OUT / f"lambda_Linf2_{i:02d}.g6").write_text(c["g6"] + "\n")
            write_json(f"lambda_Linf2_{i:02d}.json", c)
        for obj in config["objectives"]:
            cs = [c for c in population if c["objective"] == obj and c["founder"] == "B_maple_20260829"]
            best = min(cs, key=lambda c: rank(c, obj))
            (OUT / f"B_descendant_{obj}.g6").write_text(best["g6"] + "\n")
            write_json(f"B_descendant_{obj}.json", best)
        first_linf2 = next(e for e in entries if e["result"].get("candidate") and e["result"]["candidate"]["Linf"] == 2)
        summary = {"status": "PASS", "archive_sha256": EXPECTED, "archive_bytes": len(data),
                   "provenance_files_verified": len(provenance["files"]), "checkpoint_hashes_verified": len(checkpoints),
                   "phase": status["phase"], "stop_reason": status["stop_reason"],
                   "completed_tasks": len(entries), "calibration_tasks": sum(e["task"]["id"].startswith("cal-") for e in entries),
                   "full_generations": status["generation"], "last_batch_done": status["batch_done"],
                   "last_batch_total": status["batch_total"], "worker_cpu_hours": cpu / 3600,
                   "pilot_active_hours": state["pilot_active_seconds"] / 3600,
                   "calibration_active_seconds": state["startup_active_seconds"],
                   "variant_work": state["variant_work"], "attempt_statuses": dict(Counter(e["result"]["status"] for e in entries)),
                   "candidate_returns": len(returned), "independently_verified_distinct_labeled_graph_arm_pairs": len(CACHE),
                   "population_n": len(population), "archive_n": len(archive_cs),
                   "recorded_initial_canonical_classes": len({c["canonical"] for c in initial}),
                   "recorded_final_canonical_classes": len({c["canonical"] for c in population}),
                   "recorded_final_classes_per_objective": {o: len({c["canonical"] for c in population if c["objective"] == o}) for o in config["objectives"]},
                   "canonical_limit": "Certificates inherited from original run; no fresh nauty execution",
                   "report_samples": len(samples), "csv_rows": len(rows),
                   "csv_population_reconciliation": "PASS all samples via reconstructed generations",
                   "first_Linf2_task": first_linf2["task"],
                   "first_Linf2_metrics": {k: first_linf2["result"]["candidate"][k] for k in ("W", "L1", "F", "Linf", "Nmax", "founder")},
                   "solutions": sum(c["F"] == 0 for c in population + returned),
                   "incomplete_final_generation_selection_applied": False}
        write_json("audit_summary.json", summary)
        print(json.dumps(summary, indent=2))
        print("GROUPS", json.dumps([r for r in group_rows if r["founder"] in ("ALL", "B_maple_20260829")], indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
