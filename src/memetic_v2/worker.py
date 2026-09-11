"""One isolated, seeded task. No task may directly mutate the population."""

from collections import Counter, deque
import argparse
import ctypes
import signal
import json
import os
from pathlib import Path
import random
import resource
import sys
import time
import traceback

# Set before numerical/solver libraries are imported, including transitively.
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"

from core import Budget, BudgetEnd, align, apply_move, canonical, decode_g6, describe, descriptor_distance, distance, encode_g6, metrics, score, validate
from core import objective_key
from models import crossover, lambda_start, omega_start
from operators import MoveSource


def atomic_json(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as handle:
        json.dump(data, handle, separators=(",", ":"))
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def attempt(task):
    cfg = task["config"]
    seed = task["seed"]
    rng = random.Random(seed)
    budget = Budget(cfg["task_cpu_seconds"], cfg["task_evaluations"])
    parent_data = task["parent"]
    parent = decode_g6(parent_data["g6"])
    arm = parent_data["arm"]
    validate(parent, arm)
    objective = parent_data["objective"]
    def rank(rows):
        return objective_key(metrics(rows), objective)
    original_score = rank(parent)
    parent_identity = canonical(parent)
    current = parent
    tabu = deque([parent], maxlen=cfg["tabu_states"])
    inverse = None
    best = None
    best_data = None
    moves_used = Counter()
    outcomes = Counter()
    trace = []
    descent_steps = 0
    perturb_steps = 0
    generation_counts = {"empty_families": Counter()}
    method_information = {}
    phase = "perturb"

    def consider(rows, value, source):
        nonlocal best, best_data
        if value > original_score or (best_data is not None and value > objective_key(best_data, objective)):
            return
        identity = canonical(rows)
        if identity == parent_identity:
            outcomes["return_copy"] += 1
            return
        data = metrics(rows)
        data.update({"g6": encode_g6(rows), "canonical": identity,
                     "arm": arm, "objective": objective, "family": parent_data["family"],
                     "founder": parent_data.get("founder", parent_data["family"]),
                     "seed": seed, "origin": {"task_id": task["id"], "phase": source}})
        # Worker tie-break is a documented proxy. Final population tie-break
        # compares the actual descriptor distance to all other family slots.
        references = task.get("novelty_reference") or [parent_data]
        novelty = min(descriptor_distance(data, item) for item in references)
        previous = min(descriptor_distance(best_data, item) for item in references) if best_data else -1
        if best is None or value < objective_key(best_data, objective) or (value == objective_key(best_data, objective) and novelty > previous):
            best, best_data = rows, data
            trace.append({"objective_key": value, "phase": source, "evaluations": budget.evaluations})

    def choices(rows, count):
        source = MoveSource(rows, arm, rng, budget)
        options = []
        while len(options) < count:
            item = source.next()
            if item is None:
                break
            family, move = item
            if inverse is not None and move == inverse:
                outcomes["inverse_blocked"] += 1
                continue
            child = apply_move(rows, move)
            if child in tabu:
                outcomes["tabu_blocked"] += 1
                continue
            budget.evaluate()
            value = rank(child)
            options.append((family, move, child, value))
        generation_counts["empty_families"].update(source.exhausted)
        return options

    status = "COMPLETED"
    try:
        kind = task["kind"]
        partner = None
        if kind in ("guided", "crossover"):
            if task.get("partner") is None:
                return {"status": "NO_SECOND_PARENT", "candidate": None,
                        "cpu_seconds": time.process_time() - budget.started,
                        "evaluations": 0, "seed": seed, "id": task["id"]}
            partner = decode_g6(task["partner"]["g6"])
            partner = align(parent, partner, arm, rng, budget)
        if kind == "crossover" and arm == "omega":
            mixed, method_information = crossover(parent, partner, rng, seed, budget)
            if mixed is None:
                raise BudgetEnd("NO_CROSSOVER_CHILD")
            budget.evaluate()
            consider(mixed, rank(mixed), "crossover")
            current = mixed
            tabu.append(current)
        else:
            length = rng.randint(*task["length"])
            for _ in range(length):
                options = choices(current, cfg["guided_choices"] if partner is not None else 1)
                if not options:
                    outcomes["empty_allowed_neighborhood"] += 1
                    break
                if partner is not None and rng.random() < cfg["guided_probability"]:
                    chosen = min(options, key=lambda x: (distance(x[2], partner), x[3]))
                else:
                    chosen = rng.choice(options)
                family, move, current, value = chosen
                inverse = (move[1], move[0])
                tabu.append(current)
                moves_used[family] += 1
                perturb_steps += 1
                consider(current, value, phase)
        phase = "descent"
        for _ in range(cfg["descent_accepted_moves"]):
            current_score = rank(current)
            # Best improvement over up to eight generated legal neighbors.
            # Finite candidate sampling is not a local-minimum certificate.
            options = choices(current, cfg["descent_candidates_per_step"])
            improving = [option for option in options if option[3] < current_score]
            if not improving:
                outcomes["sampled_descent_stagnation"] += 1
                break
            family, move, current, value = min(improving, key=lambda x: x[3])
            inverse = (move[1], move[0])
            tabu.append(current)
            moves_used[family] += 1
            descent_steps += 1
            consider(current, value, phase)
    except BudgetEnd as error:
        status = str(error)
    if best_data is not None:
        validate(best, arm)
        best_data["rooted_canonical"] = canonical(best, True) if arm == "omega" else None
        outcomes["strict_improvement" if objective_key(best_data, objective) < original_score else "neutral_new"] += 1
    return {"id": task["id"], "seed": seed, "status": status, "candidate": best_data,
            "cpu_seconds": time.process_time() - budget.started,
            "evaluations": budget.evaluations, "generated_legal_moves": budget.generated,
            "perturb_steps": perturb_steps, "descent_steps": descent_steps,
            "net_distance_from_parent": distance(parent, best) if best is not None else 0,
            "moves_used": dict(moves_used), "outcomes": dict(outcomes),
            "empty_families": dict(generation_counts["empty_families"]),
            "best_trace": trace, "method_information": method_information}


def start_task(task):
    cfg, seed = task["config"], task["seed"]
    rng = random.Random(seed)
    budget = Budget(cfg["task_cpu_seconds"], 10 ** 9)
    arm, method = task["arm"], task["method"]
    report = {}
    try:
        function = omega_start if arm == "omega" else lambda_start
        rows, report = function(method, rng, seed, budget)
        candidate = describe(rows, arm, method, seed, {"method": method, "task_id": task["id"]}) if rows is not None else None
        status = "VALID_START" if candidate is not None else "NO_START_WITHIN_BUDGET"
    except BudgetEnd as error:
        candidate, status = None, str(error)
    if candidate:
        candidate["founder"] = task["id"]
    return {"id": task["id"], "seed": seed, "status": status,
            "candidate": candidate, "cpu_seconds": time.process_time() - budget.started,
            "evaluations": 0, "method_information": report}


def walk_start(task):
    cfg, seed = task["config"], task["seed"]
    budget = Budget(cfg["task_cpu_seconds"], 10 ** 9)
    rng = random.Random(seed)
    parent = task["parent"]
    current = decode_g6(parent["g6"])
    tabu = deque([current], maxlen=cfg["tabu_states"])
    steps = 0
    status = "START_WALK_COMPLETE"
    try:
        for _ in range(rng.randint(32, 128)):
            source = MoveSource(current, parent["arm"], rng, budget)
            moved = False
            while True:
                option = source.next()
                if option is None:
                    break
                _, move = option
                child = apply_move(current, move)
                if child not in tabu:
                    current = child
                    tabu.append(current)
                    steps += 1
                    moved = True
                    break
            if not moved:
                break
    except BudgetEnd as error:
        status = str(error)
    candidate = None
    if steps and canonical(current) != parent["canonical"]:
        candidate = describe(current, parent["arm"], "project", seed,
                             {"method": "valid_start_excursion", "steps": steps, "task_id": task["id"]})
        candidate["founder"] = parent["founder"]
    return {"id": task["id"], "seed": seed, "status": status,
            "candidate": candidate, "cpu_seconds": time.process_time() - budget.started,
            "evaluations": 0, "startup_moves": steps}


def main():
    initial_parent = os.getppid()
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGTERM, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "Cannot install parent-death signal")
    if initial_parent == 1 or os.getppid() != initial_parent:
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    task = json.loads(Path(args.input).read_text())
    # Three workers share a WSL host. Virtual limits are supplementary; the
    # coordinator guards measured RSS and host MemAvailable independently.
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024 ** 2, 1536 * 1024 ** 2))
    os.nice(10)
    started = time.monotonic()
    try:
        function = start_task if task["kind"] == "start" else (walk_start if task["kind"] == "start_walk" else attempt)
        result = function(task)
        result["wall_seconds"] = time.monotonic() - started
        result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result["rng_policy"] = "Task-scoped Python Random(seed); unfinished tasks replay from their stored seed"
        atomic_json(args.output, result)
    except BaseException as error:
        result = {"id": task["id"], "seed": task["seed"], "status": "ERROR",
                  "error": repr(error), "traceback": traceback.format_exc(),
                  "wall_seconds": time.monotonic() - started}
        atomic_json(args.output, result)
        raise


if __name__ == "__main__":
    main()
