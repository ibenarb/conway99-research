"""Single-thread worker. Parent wait4 receipts are authoritative CPU totals."""
import argparse
import json
import math
import os
from pathlib import Path
import random
import resource
import signal
import time

from common import atomic, core, cpu, checked, sha
from search import (Guard, candidate, episode, fresh_costs, identity, key,
                    parent_choice, sampled, select, tuple_state)
from generate import cover, lift, structure
from moves import omega_moves

STOP = False
PARENT = os.getppid()


def stop_requested():
    return STOP or os.getppid() != PARENT


def stopping(signum, frame):
    global STOP
    STOP = True


def read(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    directory = Path(args.directory)
    task = read(directory / "task.json")
    signal.signal(signal.SIGTERM, stopping)
    signal.signal(signal.SIGINT, stopping)
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    base = read(directory / "receipt.json")["cpu_seconds"] if (directory / "receipt.json").exists() else 0.0
    limit = task["worker_cpu_seconds"]
    # This signal is only an emergency ceiling. Cooperative checks enforce the
    # normal endpoint; no solver grandchildren exist in this worker design.
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(limit-base)+5), max(2, math.ceil(limit-base)+6)))
    deadline = max(0, limit-base)
    costs = fresh_costs()
    if task["kind"] == "census":
        parent = task["parent"]
        rows = core.decode_g6(parent["graph6"])
        best_value = parent["scores"]["W"]
        guard = Guard(deadline, stop_requested)
        censuses, complete = [], False
        try:
            for step in range(16):
                counts = {}
                best_child = None
                for family in ("4x4", "4x6", "6x6"):
                    counts[family] = 0
                    for move in omega_moves(rows, family, random.Random(task["seed"]+step), guard):
                        guard.check()
                        child = core.apply_move(rows, move)
                        score = core.metrics(child)
                        counts[family] += 1
                        if score["W"] < best_value:
                            best_value, best_child = score["W"], child
                censuses.append(counts)
                if best_child is None:
                    complete = True
                    break
                checked(core.encode_g6(best_child), "omega")
                rows = best_child
        except core.BudgetEnd:
            pass
        result = candidate(rows, "omega", parent["family"], parent["line"], parent["state"], costs)
        atomic(directory / "result.json", {"status": "LOCAL_MINIMUM_IN_CATALOG" if complete else "BOUNDED_CENSUS",
                                          "candidate": result, "completed_censuses": censuses,
                                          "catalog": ["4x4", "4x6", "6x6"]})
        return
    if task["kind"] == "generate":
        function = cover if task["arm"] == "omega" else lift
        rows, info = function(task["seed"], max(0.01, deadline-cpu()-1))
        value = candidate(rows, task["arm"], task["family"], task["id"], None, costs) if rows else None
        atomic(directory / "result.json", {"candidate": value, "details": info, "cpu_seconds": cpu(),
                                          "status": "VALID" if value else "NO_CANDIDATE"})
        return
    if task["kind"] == "train":
        parent = task["parent"]
        rows = core.decode_g6(parent["graph6"])
        rng = random.Random(task["seed"])
        deltas = {"F": [], "L1": []}
        guard = Guard(deadline, stop_requested)
        examined, escaped_template = 0, False
        try:
            for child, scores, name in sampled(rows, task["arm"], rng, guard, costs, 4096):
                examined += 1
                for target in deltas:
                    delta = scores[target] - parent["scores"][target]
                    if delta > 0:
                        deltas[target].append(delta)
                if examined <= 128 and structure(rows, parent["family"]) is True:
                    escaped_template |= structure(child, parent["family"]) is False
                if min(map(len, deltas.values())) >= 128:
                    break
        except core.BudgetEnd:
            pass
        atomic(directory / "result.json", {"positive_deltas": deltas, "examined": examined,
                                          "fixed_template_exit_observed": escaped_template,
                                          "costs": costs, "status": "TRAINED"})
        return
    if task["kind"] == "benchmark":
        rng = random.Random(task["seed"])
        parent = task["parent"]
        records = []
        if base and (directory / "result.json").exists():
            prior = read(directory / "result.json")
            records = prior["records"]
            rng.setstate(tuple_state(prior["rng"]))
        result = parent
        while cpu() < deadline and not stop_requested():
            result, record, memory = episode(parent, task["arm"], task["target"], task["variant"], rng,
                                             task["config"], [], 0, deadline, stop_requested)
            records.append(record)
            if task.get("episode_limit") and len(records) >= task["episode_limit"]:
                break
        atomic(directory / "result.json", {"status": "PAUSED" if stop_requested() and cpu() < deadline else "VALID", "records": records,
                                          "rng": rng.getstate(),
                                          "valid_completed_episodes": sum(r["eligible_before_endpoint"] and r["status"] != "PAUSED" for r in records),
                                          "minimum_reached": sum(r["minimum_reached"] for r in records),
                                          "candidate": result, "cpu_seconds": cpu()})
        return
    if task["kind"] != "compare":
        raise ValueError("Unknown task kind")
    config = task["config"]
    # Identical closing reserve INSIDE the assigned one-hour CPU ceiling.
    # Unused reserve is reported, never reassigned or counted as computation.
    closing_reserve = min(config["closing_reserve_cpu"], limit*0.01)
    deadline = max(0, limit-base-closing_reserve)
    target, arm = task["target"], task["arm"]
    checkpoint = directory / "checkpoint.json"
    if checkpoint.exists():
        wrapper = read(checkpoint)
        state = wrapper["state"]
        if sha(json.dumps(state, sort_keys=True).encode()) != wrapper["sha256"]:
            raise ValueError("Checkpoint digest mismatch; no silent restart")
        if state["task_sha256"] != sha((directory / "task.json").read_bytes()):
            raise ValueError("Changed task")
        rng = random.Random()
        rng.setstate(tuple_state(state["rng"]))
    else:
        rng = random.Random(task["seed"])
        population = task["founders"]
        state = {"population": population, "children": [], "epoch": 0, "episodes": 0,
                 "best": min(population, key=lambda p: key(p["scores"], target)),
                 "curves": [], "memory": {}, "failures": {}, "class_hashes": [],
                 "histogram": {}, "costs": fresh_costs(), "best_validation_cpu": 0.0,
                 "task_sha256": sha((directory / "task.json").read_bytes())}
        state["curves"].append({"cpu": 0.0, "scores": state["best"]["scores"]})
    last_save = 0.0
    seen_classes = set(state["class_hashes"])
    state["status"] = "RUNNING"

    def save():
        state["rng"] = rng.getstate()
        state["class_hashes"] = sorted(seen_classes)
        state["checkpoint_cpu_seconds"] = base + cpu()
        payload = json.loads(json.dumps(state))
        atomic(checkpoint, {"state": payload, "sha256": sha(json.dumps(payload, sort_keys=True).encode())})

    def best(rows, scores):
        if key(scores, target) >= key(state["best"]["scores"], target):
            return
        start = cpu()
        item = candidate(rows, arm, parent["family"], parent["line"], parent["state"], costs)
        state["best_validation_cpu"] += cpu()-start
        if cpu() <= deadline:
            state["best"] = item
            state["curves"].append({"cpu": base+cpu(), "scores": item["scores"]})

    while not stop_requested() and cpu() < deadline:
        parent = parent_choice(state["population"], target, rng)
        line = parent["line"]
        result, record, memory = episode(parent, arm, target, task["variant"], rng, config,
                                         state["memory"].get(line, []), state["failures"].get(line, 0),
                                         deadline, stop_requested, best)
        state["episodes"] += 1
        state["memory"][line] = memory if task["variant"] == "A1" else []
        state["failures"][line] = 0 if record["target_improved"] else state["failures"].get(line, 0)+1
        for k, v in record["costs"].items():
            state["costs"][k] += v
        for name, value in (("perturb_length", record["perturb_trades"]),
                            ("descent_length", record["descent_trades"]),
                            ("neutral_length", record["neutral_trades"]),
                            ("escape_length", record["escape_trades"]),
                            ("minimum_reached", record["minimum_reached"]),
                            ("returned", record["returned_to_parent"]),
                            ("target_improved", record["target_improved"]),
                            ("new_class_vs_parent", record["new_class_vs_parent"]),
                            ("stop", record["status"])):
            bucket = state["histogram"].setdefault(name, {})
            bucket[str(value)] = bucket.get(str(value), 0)+1
        if record["eligible_before_endpoint"]:
            seen_classes.add(result["class"])
            state["children"].append(result)
            if len(state["children"]) >= 16:
                families = sorted({p["family"] for p in task["founders"]})
                state["population"] = select(state["population"], state["children"], arm, target,
                                               rng, state["epoch"], families)
                state["children"] = []
                state["epoch"] += 1
        if time.monotonic()-last_save >= 30:
            save()
            last_save = time.monotonic()
    state["status"] = "PAUSED" if stop_requested() and cpu() < deadline else "COMPLETE"
    search_stop_cpu = base+cpu()
    save()
    atomic(directory / "result.json", {"status": state["status"], "best": state["best"],
                                      "curves": state["curves"], "episodes": state["episodes"],
                                      "histogram": state["histogram"], "costs": state["costs"],
                                      "classes": len(seen_classes),
                                      "families": sorted({p["family"] for p in state["population"]}),
                                      "endpoint_cpu_seconds": limit,
                                      "closing_reserve_cpu_seconds": closing_reserve,
                                      "search_stop_cpu_seconds": search_stop_cpu,
                                      "checkpoint_cpu_seconds": base+cpu()})


if __name__ == "__main__":
    main()
