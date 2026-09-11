"""Office coordinator: bounded starts, calibration, then 24 active pilot hours."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time
import traceback

from core import VERSION, canonical, decode_g6, derive_seed, describe, descriptor_distance
from runtime import DEFAULTS, Checkpoints, Journal, RunLock, atomic_json, canonical_json, digest, fingerprint, make_status, print_status, resources
from verify import check_graph

REPOSITORY = Path(__file__).resolve().parents[2]
REFERENCE = REPOSITORY / "data/memetic/reference"


def assert_candidate(candidate):
    report = check_graph(candidate["g6"], candidate["arm"], candidate)
    if not report["hard_valid"]:
        raise RuntimeError("Independent candidate verification failed: " + json.dumps(report))
    identity = canonical(decode_g6(candidate["g6"]))
    if identity != candidate["canonical"]:
        raise RuntimeError("Candidate canonical identity mismatch")
    return report


def reference_candidates():
    manifest = json.loads((REFERENCE / "provenance.json").read_text())
    result = []
    for item in manifest:
        path = REFERENCE / item["file"]
        if digest(path.read_bytes()) != item["sha256"]:
            raise RuntimeError("Reference file checksum mismatch: " + path.name)
        arm = "lambda" if path.name.startswith("hog") else "omega"
        founder = "hog57338" if arm == "lambda" else path.stem
        candidate = describe(decode_g6(path.read_text()), arm, "project", 0,
                             {"reference_file": path.name, "sha256": item["sha256"]})
        candidate["founder"] = founder
        assert_candidate(candidate)
        result.append(candidate)
    return result


def update_archive(state, candidate, config):
    archive = state.setdefault("archive", [])
    if any(c["canonical"] == candidate["canonical"] and c["arm"] == candidate["arm"] for c in archive):
        return
    cell = (candidate["arm"], candidate["F"] // config["archive_f_bin"], candidate["max_defect_degree"])
    for i, old in enumerate(archive):
        old_cell = (old["arm"], old["F"] // config["archive_f_bin"], old["max_defect_degree"])
        if old_cell == cell:
            if (candidate["F"], candidate["W"]) < (old["F"], old["W"]):
                archive[i] = candidate
            return
    archive.append(candidate)
    if len(archive) > config["archive_cells"]:
        # Always protect the global best of each arm. Remove a redundant
        # high-F representative from an overrepresented arm/cell region.
        protected = set()
        for arm in ("omega", "lambda"):
            indices = [i for i, p in enumerate(archive) if p["arm"] == arm]
            if indices:
                protected.add(min(indices, key=lambda i: archive[i]["F"]))
        removable = [i for i in range(len(archive)) if i not in protected]
        counts = Counter(p["arm"] for p in archive)
        index = max(removable, key=lambda i: (counts[archive[i]["arm"]], archive[i]["F"]))
        del archive[index]


def choose_initial(pool, config):
    selected, identities = [], set()
    for arm in ("omega", "lambda"):
        for family in ("exact", "repair", "algebraic", "project"):
            candidates = sorted((p for p in pool if p["arm"] == arm and p["family"] == family), key=lambda p: (p["F"], p["canonical"]))
            limit = config["family_target"]
            group = []
            while candidates and len(group) < limit:
                candidates = [p for p in candidates if p["canonical"] not in identities]
                candidates = [p for p in candidates if p.get("founder") != "hog57338" or sum(q.get("founder") == "hog57338" for q in selected + group) < config["hog_family_max"]]
                if not candidates:
                    break
                if len(group) < limit // 2 or not selected + group:
                    choice = min(candidates, key=lambda p: (p["F"], p["canonical"]))
                else:
                    choice = max(candidates, key=lambda p: (min(descriptor_distance(p, q) for q in selected + group), -p["F"], p["canonical"]))
                group.append(dict(choice))
                identities.add(choice["canonical"])
                candidates.remove(choice)
            selected.extend(group)
    for i, candidate in enumerate(selected):
        candidate["line_id"] = f"line-{i:03d}"
        candidate["stagnant_generations"] = 0
    return selected


def build_start_jobs(config, references):
    jobs = []
    for arm in ("omega", "lambda"):
        for method in ("exact", "repair", "algebraic"):
            for ordinal in range(config["starter_attempts_per_method_arm"]):
                identity = f"start-{arm}-{method}-{ordinal:03d}"
                jobs.append({"id": identity, "kind": "start", "arm": arm, "method": method,
                             "seed": derive_seed(config["master_seed"], identity), "config": config})
    for reference in references:
        for ordinal in range(config["starter_walk_attempts_per_reference"]):
            identity = f"startwalk-{reference['founder']}-{ordinal:03d}"
            jobs.append({"id": identity, "kind": "start_walk", "parent": reference,
                         "seed": derive_seed(config["master_seed"], identity), "config": config})
    # Interleave arms/methods so a finite preparation budget treats them fairly.
    random.Random(derive_seed(config["master_seed"], "startup-order")).shuffle(jobs)
    return jobs


def build_generation_jobs(state, config, calibration=False):
    population = state["population"]
    if calibration:
        population = [p for arm in ("omega", "lambda") for p in [q for q in population if q["arm"] == arm][:1]]
    generation = state.get("generation", 0)
    jobs = []
    for parent in population:
        adaptive = generation >= config["warmup_generations"] and parent["stagnant_generations"] >= config["stagnation_generations"]
        lengths = [(2, 4)] * (2 if adaptive else 3) + [(5, 12)] * 2 + [(13, 64 if adaptive else 32)] * (2 if adaptive else 1)
        specifications = [("random", length) for length in lengths]
        specifications += [("guided", (8, 16)), ("crossover" if parent["arm"] == "omega" else "guided", (8, 16))]
        for ordinal, (kind, length) in enumerate(specifications):
            prefix = "cal" if calibration else f"g{generation:06d}"
            identity = f"{prefix}-{parent['line_id']}-{ordinal}"
            seed = derive_seed(config["master_seed"], identity)
            partners = [p for p in population if p["arm"] == parent["arm"] and p["canonical"] != parent["canonical"]]
            other_families = [p for p in partners if p["family"] != parent["family"]]
            partner = random.Random(seed).choice(other_families or partners) if partners else None
            jobs.append({"id": identity, "seed": seed, "kind": kind, "length": length,
                         "parent": parent, "partner": partner, "config": config,
                         "novelty_reference": [{"defect_degrees": q["defect_degrees"], "residual_histogram": q["residual_histogram"]} for q in population if q["line_id"] != parent["line_id"]]})
    return jobs


def select_generation(state, config):
    population = state["population"]
    results = state["results"]
    grouped = defaultdict(list)
    for task in state["jobs"]:
        result = results.get(task["id"], {})
        if result.get("candidate"):
            grouped[task["parent"]["line_id"]].append(result["candidate"])
    # Stable order. No completion-order-dependent replacement policy.
    for position, parent in enumerate(list(population)):
        others = [p for i, p in enumerate(population) if i != position]
        identities = {p["canonical"] for p in others}
        acceptable = [p for p in grouped[parent["line_id"]] if p["F"] <= parent["F"] and p["canonical"] != parent["canonical"] and p["canonical"] not in identities]
        if acceptable:
            best_score = min(p["F"] for p in acceptable)
            ties = [p for p in acceptable if p["F"] == best_score]
            child = dict(max(ties, key=lambda p: (min((descriptor_distance(p, q) for q in others), default=0), p["canonical"])))
            child["line_id"] = parent["line_id"]
            child["family"] = parent["family"]
            child["founder"] = parent["founder"]
            child["stagnant_generations"] = 0 if child["F"] < parent["F"] else parent["stagnant_generations"] + 1
            population[position] = child
        else:
            parent["stagnant_generations"] += 1
    state["generation"] += 1
    return {"generation": state["generation"], "population": len(population),
            "canonical_classes": len({p["canonical"] for p in population}),
            "families": dict(Counter(p["arm"] + ":" + p["family"] for p in population)),
            "minimum_F": {arm: min((p["F"] for p in population if p["arm"] == arm), default=None) for arm in ("omega", "lambda")}}


class Coordinator:
    def __init__(self, directory, config):
        self.directory = Path(directory).resolve()
        if self.directory == REPOSITORY or REPOSITORY in self.directory.parents:
            raise ValueError("Run data must be outside the repository")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = RunLock(self.directory)
        for name in ("spool", "logs", "findings"):
            (self.directory / name).mkdir(exist_ok=True)
        self.config = config
        self.checkpoints = Checkpoints(self.directory, config["checkpoint_slots"])
        self.journal = Journal(self.directory / "logs", config)
        self.active = {}
        self.stopping = None
        self.last_tick = time.monotonic()
        self.last_checkpoint = self.last_tick
        self.last_status = 0
        current_fingerprint = fingerprint(REPOSITORY, config)
        self.state, damaged = self.checkpoints.load()
        if self.state is None:
            references = reference_candidates()
            self.state = {"phase": "STARTERS", "generation": 0, "config": config,
                          "fingerprint": current_fingerprint, "population": [],
                          "pool": references, "archive": [], "results": {},
                          "jobs": build_start_jobs(config, references), "completed_tasks": 0,
                          "startup_active_seconds": 0.0, "pilot_active_seconds": 0.0,
                          "recent_task_wall": [], "cumulative_cpu_seconds": 0.0,
                          "created_utc": datetime.now(timezone.utc).isoformat()}
            for candidate in references:
                update_archive(self.state, candidate, config)
            atomic_json(self.directory / "config.resolved.json", config)
            atomic_json(self.directory / "provenance.json", current_fingerprint)
            self.checkpoints.save(self.state)
        else:
            old = self.state["fingerprint"]
            if old["config_sha256"] != current_fingerprint["config_sha256"] or old["code_and_inputs_sha256"] != current_fingerprint["code_and_inputs_sha256"]:
                raise RuntimeError("Resume refused: changed config, code or reference inputs")
            if old["runtime_signature_sha256"] != current_fingerprint["runtime_signature_sha256"]:
                raise RuntimeError("Resume refused: changed Python or numerical/canonicalization packages")
            for candidate in self.state.get("population", []) + self.state.get("archive", []):
                assert_candidate(candidate)
            self.journal.append("events", {"event": "RESUME", "damaged_slots": damaged, "sequence": self.state["checkpoint_sequence"]})
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, lambda signum, frame: setattr(self, "stopping", "INTERRUPTED"))

    def tick(self):
        now = time.monotonic()
        elapsed = now - self.last_tick
        self.last_tick = now
        if self.state["phase"] in ("STARTERS", "CALIBRATION"):
            self.state["startup_active_seconds"] += elapsed
        elif self.state["phase"] == "PILOT":
            self.state["pilot_active_seconds"] += elapsed

    def launch(self, task):
        path = self.directory / "spool" / task["id"]
        input_path = path.with_suffix(".input.json")
        output_path = path.with_suffix(".result.json")
        atomic_json(input_path, task)
        # A completed file from a pre-checkpoint interruption is replayed into
        # the coordinator rather than recalculated when its ID/seed match.
        if output_path.exists():
            result = json.loads(output_path.read_text())
            self.accept_result(task, result)
            return
        err = path.with_suffix(".stderr.txt").open("wb")
        env = dict(os.environ)
        env.update({name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
        process = subprocess.Popen([sys.executable, str(REPOSITORY / "src/memetic/worker.py"), "--input", str(input_path), "--output", str(output_path)],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=err,
                                   start_new_session=True, env=env)
        self.active[task["id"]] = {"process": process, "task": task, "output": output_path,
                                    "stderr": err, "launched": time.monotonic()}

    def accept_result(self, task, result):
        if result.get("id") != task["id"] or result.get("seed") != task["seed"]:
            raise RuntimeError("Worker result ID/seed mismatch")
        if result.get("status") == "ERROR":
            self.journal.append("errors", result)
            raise RuntimeError("Worker error: " + result.get("error", "unknown"))
        candidate = result.get("candidate")
        if candidate:
            verification = assert_candidate(candidate)
            result["independent_verification"] = {k: verification[k] for k in ("hard_valid", "is_solution", "F", "W")}
            update_archive(self.state, candidate, self.config)
            if self.state["phase"] == "STARTERS":
                if not any(p["canonical"] == candidate["canonical"] for p in self.state["pool"]):
                    self.state["pool"].append(candidate)
            if verification["is_solution"]:
                atomic_json(self.directory / "findings" / f"solution-{candidate['canonical']}.json", {"candidate": candidate, "verification": verification})
                self.stopping = "VERIFIED_SOLUTION"
        with (self.directory / "task_seeds.tsv").open("a") as seed_log:
            seed_log.write(f"{task['id']}\t{task['seed']}\t{result['status']}\n")
            seed_log.flush()
            os.fsync(seed_log.fileno())
        self.state["results"][task["id"]] = result
        self.state["completed_tasks"] += 1
        self.state["cumulative_cpu_seconds"] += result.get("cpu_seconds", 0)
        self.state["recent_task_wall"] = (self.state["recent_task_wall"] + [result.get("wall_seconds", 0)])[-128:]
        self.journal.append("attempts", {"task": {k: v for k, v in task.items() if k not in ("parent", "partner", "config", "novelty_reference")}, "result": result})
        self.tick()
        self.checkpoints.save(self.state)
        # The checkpoint is durable before transient input/result removal.
        for path in (self.directory / "spool").glob(task["id"] + ".*"):
            path.unlink(missing_ok=True)

    def harvest(self):
        for identity, active in list(self.active.items()):
            process = active["process"]
            if process.poll() is None:
                continue
            active["stderr"].close()
            del self.active[identity]
            if not active["output"].exists():
                raise RuntimeError(f"Worker {identity} exited {process.returncode} without an atomic result")
            self.accept_result(active["task"], json.loads(active["output"].read_text()))

    def terminate_workers(self):
        for active in self.active.values():
            try:
                os.killpg(active["process"].pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 3
        for active in self.active.values():
            process = active["process"]
            try:
                process.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            active["stderr"].close()
        self.active.clear()

    def transition(self):
        phase = self.state["phase"]
        self.journal.append("batches", {"phase": phase, "generation": self.state["generation"], "done": len(self.state["results"]), "planned": len(self.state["jobs"])})
        if phase == "STARTERS":
            self.state["population"] = choose_initial(self.state["pool"], self.config)
            for arm in ("omega", "lambda"):
                if not any(p["arm"] == arm for p in self.state["population"]):
                    raise RuntimeError("No valid initial representative for arm " + arm)
            atomic_json(self.directory / "starter_report.json", {"target_per_arm": self.config["population_per_arm"],
                        "actual_population": self.state["population"],
                        "completed_attempts": len(self.state["results"]),
                        "statuses": dict(Counter(v["status"] for v in self.state["results"].values())),
                        "scope": "A smaller population is explicit; no padding with relabelings"})
            self.state["pool"] = []
            self.state["phase"] = "CALIBRATION"
            self.state["jobs"] = build_generation_jobs(self.state, self.config, calibration=True)
        elif phase == "CALIBRATION":
            atomic_json(self.directory / "calibration.json", {"results": self.state["results"],
                        "scope": "Finite calibration tasks from the initial population; no changes to pilot parameters"})
            self.state["phase"] = "PILOT"
            self.state["jobs"] = build_generation_jobs(self.state, self.config)
        else:
            report = select_generation(self.state, self.config)
            self.journal.append("generations", report)
            atomic_json(self.directory / "population.json", {"generation": self.state["generation"], "candidates": self.state["population"]})
            self.state["jobs"] = build_generation_jobs(self.state, self.config)
        self.state["results"] = {}
        self.checkpoints.save(self.state)

    def run(self):
        try:
            while not self.stopping:
                self.tick()
                if self.state["phase"] == "COMPLETE":
                    self.stopping = "ALREADY_COMPLETE"
                    break
                self.harvest()
                resource_report = resources(self.directory, [a["process"].pid for a in self.active.values()], self.config)
                if resource_report["hazards"]:
                    self.stopping = ",".join(resource_report["hazards"])
                    break
                for identity, active in self.active.items():
                    if time.monotonic() - active["launched"] > self.config["worker_watchdog_seconds"]:
                        raise RuntimeError("Worker watchdog: " + identity)
                if self.state["phase"] == "PILOT" and self.state["pilot_active_seconds"] >= self.config["pilot_active_seconds"]:
                    self.state["phase"] = "COMPLETE"
                    self.stopping = "PILOT_BUDGET_COMPLETE"
                    break
                pending = [j for j in self.state["jobs"] if j["id"] not in self.state["results"] and j["id"] not in self.active]
                startup_expired = self.state["phase"] == "STARTERS" and self.state["startup_active_seconds"] >= self.config["startup_active_seconds"]
                if (not pending or startup_expired) and not self.active:
                    self.transition()
                    continue
                if resource_report["may_launch"] and not startup_expired:
                    for task in pending[:max(0, self.config["workers"] - len(self.active))]:
                        self.launch(task)
                now = time.monotonic()
                if now - self.last_status >= self.config["status_seconds"]:
                    report = make_status(self.state, self.config, resource_report, len(self.active))
                    print_status(report)
                    atomic_json(self.directory / "status.json", report)
                    self.journal.append("status", report)
                    self.last_status = now
                if now - self.last_checkpoint >= self.config["checkpoint_seconds"]:
                    self.checkpoints.save(self.state)
                    self.last_checkpoint = now
                time.sleep(0.25)
        except BaseException as error:
            self.stopping = "ERROR"
            self.journal.append("errors", {"error": repr(error), "traceback": traceback.format_exc()})
            print("RUNNER_ERROR", repr(error), flush=True)
        finally:
            self.terminate_workers()
            self.tick()
            self.state["last_stop_reason"] = self.stopping
            self.checkpoints.save(self.state)
            atomic_json(self.directory / "best_archive.json", {"candidates": self.state["archive"]})
            atomic_json(self.directory / "population.json", {"generation": self.state["generation"], "candidates": self.state["population"]})
            final_resources = resources(self.directory, [], self.config)
            final_status = make_status(self.state, self.config, final_resources, 0)
            final_status["stop_reason"] = self.stopping
            atomic_json(self.directory / "status.json", final_status)
            print("RUNNER_STOP", self.stopping, "RESUME_DIR", self.directory, flush=True)
            self.lock.close()
        return 2 if self.stopping == "ERROR" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(REPOSITORY / "configs/memetic/office-0.1.0.json"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if set(config) != set(DEFAULTS) or config["version"] != VERSION:
        raise ValueError("Unsupported or incomplete configuration")
    if not 1 <= config["workers"] <= 4 or config["task_cpu_seconds"] <= 0:
        raise ValueError("Invalid Office worker/budget configuration")
    if args.status:
        path = Path(args.run_dir) / "status.json"
        print(path.read_text() if path.exists() else "No status yet")
        return
    os.nice(5)
    coordinator = Coordinator(args.run_dir, config)
    sys.exit(coordinator.run())


if __name__ == "__main__":
    main()
