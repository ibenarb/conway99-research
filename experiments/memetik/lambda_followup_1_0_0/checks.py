"""Finite controls for the new mechanism; never a substitute for WSL preflight."""
import boot
from util import *
from pc_engine import PCEngine
from engine import Engine as FrozenEngine
from worker import initial
from archive import Archive
from kernel import catalogue
import controls as frozen_checks
from search import tuple_state, key
import copy
import random
import tempfile
from unittest.mock import patch

def differential(founders):
    class WithoutCycle(PCEngine):
        def batch(self, current, guard, sample_size=None):
            return FrozenEngine.batch(self, current, guard, sample_size)
    traces, rngs, finals = [], [], []
    with tempfile.TemporaryDirectory() as temp:
        for variant, engine_type in (("P", FrozenEngine), ("PC", WithoutCycle)):
            task = frozen_checks.task_for(founders, variant, 220922)
            task["config"]["perturb_ranges"] = [[2, 2], [2, 2], [2, 2]]
            state = initial(task)
            rng = random.Random(task["seed"])
            archive = Archive(Path(temp) / (variant + ".sqlite"))
            for f in founders:
                archive.put(f)
            observer = frozen_checks.Observation(task, state, archive)
            engine = engine_type(task, state, rng, observer)
            while state["episodes"] < 20:
                engine.step(frozen_checks.Guard())
            traces.append(observer.trace)
            rngs.append(rng.getstate())
            finals.append(([p["state"] for p in state["population"]],
                           [p["state"] for p in state["children"]], state["best"]["state"], state["epoch"]))
            archive.close()
    assert traces[0] == traces[1] and rngs[0] == rngs[1] and finals[0] == finals[1]
    return {"episodes": 20, "same_moves_rng_population_children_best_epoch": True,
            "diagnostic_perturbation_length": 2, "stop_label_difference_intentional": True}

def cycle_control():
    w = read(boot.HERE / "CONTROL_WITNESS.json")
    rows, sc = checked(w["start_graph6"], "lambda")
    for field in ("step1", "step2"):
        move = tuple(tuple(tuple(e) for e in part) for part in w[field]["move"])
        matches = [name for name, m in catalogue(rows, True, frozen_checks.Guard()) if m == move]
        assert matches == [w[field]["operator"]]
        if field == "step2":
            founders = read(boot.FROZEN / "founders.json")
            task = frozen_checks.task_for(founders, "PC")
            state = initial(task)
            with tempfile.TemporaryDirectory() as temp:
                archive = Archive(Path(temp) / "pc-catalogue.sqlite")
                observer = frozen_checks.Observation(task, state, archive)
                engine = PCEngine(task, state, random.Random(task["seed"]), observer)
                item = checked_item(core.encode_g6(rows), "catalogue-control")
                choices = engine.batch(item, frozen_checks.Guard())
                assert any(c["operator"] == "cycle3" and c["move"] == move for c in choices)
                assert engine.variant == "PC"
                archive.close()
        before = rows
        rows = core.apply_move(rows, move)
        checked(core.encode_g6(rows), "lambda")
        assert core.apply_move(rows, move[::-1]) == before
    assert core.encode_g6(rows) == w["graph6"]
    assert checked(w["graph6"], "lambda")[1] == w["scores"]
    bad = list(rows)
    other = next(i for i in range(99) if (bad[0] >> i) & 1)
    bad[0] &= ~(1 << other)
    bad[other] &= ~1
    try:
        checked(core.encode_g6(bad), "lambda")
    except (ValueError, AssertionError):
        pass
    else:
        raise AssertionError("Invalid graph accepted")
    return {"known_pivot_and_cycle_member": True, "W2116_valid": True, "invalid_graph_rejected": True}

def receipt_controls():
    # Tiny authentic worker sessions are exercised separately in integration tests.
    from clock import validate_clock_session
    start = {"host_seconds": 0, "guest_after": {"MONOTONIC": 0}}
    end = {"host_seconds": 180, "guest_after": {"MONOTONIC": 165}}
    good = [{"code": 0, "wait4_cpu": 179, "self_cpu": 179}]
    assert validate_clock_session(start, end, good, 1)["guest_monotonic_drift"]
    try:
        validate_clock_session(start, {**end, "host_seconds": 160}, good, 1)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Inflated CPU/host accepted")
    return {"guest_drift_detected": True, "cpu_host_inflation_rejected": True}

def resume_copy(run):
    plan = read(run / "plan.json")
    spec = next(j for j in plan["jobs"] if j["id"] == "Pext--W-00")
    src = run / spec["directory"]
    before_hashes = hashes(src, ["task.json", "receipt.json", "result.json", "checkpoint.json", "archive.sqlite"])
    with tempfile.TemporaryDirectory(dir=run / "diagnostics") as temp:
        import shutil
        root = Path(temp)
        d = root / "tasks" / "probe"
        d.mkdir(parents=True)
        for name in before_hashes:
            shutil.copyfile(src / name, d / name)
        atomic(root / "budget.json", {"per_job_cpu_seconds": 3720})
        previous = receipt_valid(d)
        old = read(d / "result.json")
        code, usage = timed_child([sys.executable, str(boot.FROZEN / "worker.py"), str(d)], d / "worker.log", 120)
        receipt = make_receipt(d, previous, 3600, 3720, code, usage)
        receipt_valid(d)
        result = read(d / "result.json")
        assert code == 0 and receipt["budget_cpu_seconds"] <= 3720
        assert result["endpoint_cpu_seconds"] == 3720
        assert result["curves"][:len(old["curves"])] == old["curves"]
        for mark in ("600", "1800", "3600"):
            assert result["milestones"][mark] == old["milestones"][mark]
        if read(src / "checkpoint.json")["state"]["batch"] is not None:
            assert result["replayed_moves"] > old["replayed_moves"]
        assert hashes(src, list(before_hashes)) == before_hashes
        report = {"new_cpu_seconds": usage.ru_utime + usage.ru_stime,
                  "closed_reserve_cpu_seconds": receipt["closed_reserve_cpu_seconds"],
                  "old_milestones_preserved": True, "source_unchanged": True}
    return report

def run_checks(run=None):
    started = own_cpu()
    founders = read(boot.FROZEN / "founders.json")
    from prepare import validate_founders
    validate_founders(founders)
    differential_result = differential(founders)
    with patch.object(frozen_checks, "Engine", PCEngine):
        continuations = [frozen_checks.continuation(founders, "PC", point) for point in (False, True)]
    # Preserve original P/TC continuation behavior, including archive/RNG restart paths.
    continuations += [frozen_checks.continuation(founders, v, point)
                      for v in ("P", "TC") for point in (False, True)]
    success = frozen_checks.solution_controls(founders)
    result = {"status": "CONTROLS_PASS", "pc_differential": differential_result,
              "continuations": continuations, "cycle": cycle_control(),
              "clock_decisions": receipt_controls(), "success": success,
              "host_probe": "Not performed by this mathematical suite"}
    if run is not None:
        result["original_copy_resume"] = resume_copy(Path(run))
    result["self_cpu_seconds"] = own_cpu() - started
    return result
