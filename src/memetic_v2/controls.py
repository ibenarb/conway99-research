"""Three focused gates: graph mathematics, persistence, and installed integration.

--core runs without optional runtime packages. --full additionally requires
actual pynauty and OR-Tools, solves a known crossover obstruction and a
constructive crossover control, then interrupts and resumes a real coordinator.
"""

from itertools import combinations, product
import argparse
import copy
import importlib.metadata
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import tempfile
import time

from core import Budget, OUTER, apply_move, canonical, decode_g6, encode_g6, from_edges, metrics, random_frame, relabel, score, validate
from operators import apex_moves, omega_moves, rotation_moves, signed_vectors
from runtime import DEFAULTS, Checkpoints, RunLock, atomic_json
from verify import check_graph

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "data/memetic_v2/reference"


def bvls_control():
    # Ternary Golay [11,6,5], generator x^5+x^4-x^3+x^2-1.
    g = [2, 0, 1, 2, 1, 1]
    matrix = [[0] * 11 for _ in range(6)]
    for i in range(6):
        matrix[i][i:i + 6] = g
    pivots = []
    row = 0
    for column in range(11):
        pivot = next((i for i in range(row, 6) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        inverse = pow(matrix[row][column], -1, 3)
        matrix[row] = [(x * inverse) % 3 for x in matrix[row]]
        for i in range(6):
            if i != row:
                factor = matrix[i][column]
                matrix[i] = [(a - factor * b) % 3 for a, b in zip(matrix[i], matrix[row])]
        pivots.append(column)
        row += 1
    basis = []
    for column in range(11):
        if column not in pivots:
            vector = [0] * 11
            vector[column] = 1
            for i, pivot in enumerate(pivots):
                vector[pivot] = -matrix[i][column] % 3
            basis.append(vector)
    generators = {tuple(sign * basis[i][column] % 3 for i in range(5)) for column in range(11) for sign in (1, 2)}
    labels = list(product(range(3), repeat=5))
    lookup = {v: i for i, v in enumerate(labels)}
    rows = tuple(sum(1 << lookup[tuple((a + b) % 3 for a, b in zip(vertex, generator))] for generator in generators) for vertex in labels)
    return rows


def mathematics():
    report = {"reference_graphs": {}}
    expected = {"hog57338.g6": (2836, 2182), "H_minus_Z2_template_A99.g6": (4980, 2341),
                "H_plus_Z2_template_A99.g6": (5016, 2331), "H_Z14_invariant_A99.g6": (4312, 2310)}
    states = {}
    for filename, expected_values in expected.items():
        text = (REFERENCE / filename).read_text()
        rows = decode_g6(text)
        states[filename] = rows
        arm = "lambda" if filename.startswith("hog") else "omega"
        validate(rows, arm)
        values = metrics(rows)
        assert (values["F"], values["W"]) == expected_values
        oracle = check_graph(encode_g6(rows), arm, values)
        assert oracle["hard_valid"] and not oracle["is_solution"]
        assert decode_g6(encode_g6(rows)) == rows
        forged = dict(values, F=0)
        assert not check_graph(encode_g6(rows), arm, forged)["hard_valid"]
        report["reference_graphs"][filename] = {"F": values["F"], "W": values["W"], "independent": True}
    hog = states["hog57338.g6"]
    moves = list(apex_moves(hog))
    assert len(moves) == 46
    values = []
    for move in moves:
        child = apply_move(hog, move)
        validate(child, "lambda")
        oracle = check_graph(encode_g6(child), "lambda")
        assert oracle["hard_valid"]
        assert apply_move(child, (move[1], move[0])) == hog
        assert oracle["F"] == score(child)
        values.append(oracle["F"])
    assert min(values) == 2856
    report["hog_apex"] = {"count": len(moves), "minimum_F": min(values), "all_independently_valid": True}
    minus = states["H_minus_Z2_template_A99.g6"]
    plus = states["H_plus_Z2_template_A99.g6"]
    products = list(omega_moves(minus, "4x4"))
    assert len(products) == 3
    assert plus in [apply_move(minus, move) for move in products]
    for move in products:
        child = apply_move(minus, move)
        validate(child, "omega")
        assert check_graph(encode_g6(child), "omega")["hard_valid"]
        assert len(move[0]) == len(move[1]) == 8
        assert len({v for part in move for pair in part for v in pair}) == 8
    vector_counts = {}
    for size in (4, 6):
        count = 0
        for vector in signed_vectors(size, random.Random(4)):
            totals = [0] * 14
            assert len({u for u, sign in vector}) == size
            for u, sign in vector:
                a, b = OUTER[u]
                totals[a] += sign
                totals[b] += sign
            assert totals == [0] * 14
            count += 1
        vector_counts[str(size)] = count
    assert vector_counts["6"] * 2 == 250600
    report["omega"] = {"minus_4x4_neighbors": len(products), "kernel_vectors_modulo_sign": vector_counts}
    rook = from_edges(9, [(i, j) for i, j in combinations(range(9), 2) if i // 3 == j // 3 or i % 3 == j % 3])
    assert check_graph(encode_g6(rook), expected_n=9, expected_degree=4)["is_solution"]
    bvls = bvls_control()
    assert check_graph(encode_g6(bvls), expected_n=243, expected_degree=22)["is_solution"]
    apex = next(apex_moves(bvls))
    rotated = next(rotation_moves(bvls))
    for move, expected_f in ((apex, 288), (rotated, 432)):
        child = apply_move(bvls, move)
        oracle = check_graph(encode_g6(child), "lambda", expected_n=243, expected_degree=22)
        assert oracle["hard_valid"] and oracle["F"] == expected_f and oracle["W"] == expected_f
    report["positive_controls"] = {"rook9": "SRG", "bvls243": "SRG", "apex_F_W": 288, "rotation_F_W": 432}
    return report


def persistence():
    with tempfile.TemporaryDirectory(prefix="conway99-persistence-") as temp:
        checkpoints = Checkpoints(temp)
        state = {"phase": "PILOT", "value": 1, "population": [
            {"residual_histogram": {-2: 1, -1: 2, 0: 3, 1: 4, 2: 5, 10: 6}}]}
        checkpoints.save(state)
        state["value"] = 2
        checkpoints.save(state)
        recovered, damaged = checkpoints.load()
        assert recovered["value"] == 2 and not damaged
        assert recovered == json.loads(json.dumps(state))
        # A partial temporary file must be ignored; a corrupt newest slot
        # must recover the prior complete generation of the checkpoint.
        directory = Path(temp) / "checkpoints"
        (directory / "checkpoint.0.json.gz.tmp").write_bytes(b"interrupted write")
        recovered, _ = checkpoints.load()
        assert recovered["value"] == 2
        newest = directory / f"checkpoint.{state['checkpoint_sequence'] % 3}.json.gz"
        newest.write_bytes(b"corrupted checkpoint")
        recovered, damaged = checkpoints.load()
        assert recovered["value"] == 1 and len(damaged) == 1
        lock = RunLock(temp)
        try:
            rejected = False
            try:
                second = RunLock(temp)
                second.close()
            except RuntimeError:
                rejected = True
            assert rejected
        finally:
            lock.close()
    return {"numeric_histogram_keys_roundtrip": True, "atomic_temp_ignored": True, "corrupt_latest_fallback": True, "exclusive_run_lock": True}


def installed_algorithms():
    from models import crossover
    versions = {name: importlib.metadata.version(name) for name in ("ortools", "pynauty", "numpy")}
    minus = decode_g6((REFERENCE / "H_minus_Z2_template_A99.g6").read_text())
    plus = decode_g6((REFERENCE / "H_plus_Z2_template_A99.g6").read_text())
    assert canonical(minus) == canonical(relabel(minus, random_frame(random.Random(22))))
    assert canonical(minus, True) == canonical(relabel(minus, random_frame(random.Random(23))), True)
    hog = decode_g6((REFERENCE / "hog57338.g6").read_text())
    permutation = list(range(99))
    random.Random(24).shuffle(permutation)
    assert canonical(hog) == canonical(relabel(hog, permutation))
    child, report = crossover(minus, plus, random.Random(1), 1, Budget(10, 256))
    assert child is None and report["status"] == "INFEASIBLE"
    positive = None
    first_moves = list(omega_moves(minus, "4x4"))
    for first in first_moves:
        middle = apply_move(minus, first)
        changed = set(first[0] + first[1])
        for second in omega_moves(middle, "4x4"):
            if changed.isdisjoint(second[0] + second[1]):
                endpoint = apply_move(middle, second)
                if canonical(middle) not in (canonical(minus), canonical(endpoint)):
                    positive = endpoint
                    break
        if positive:
            break
    if positive is None:
        raise RuntimeError("Positive crossover control could not be constructed")
    child, positive_report = crossover(minus, positive, random.Random(2), 2, Budget(10, 256))
    assert child is not None and check_graph(encode_g6(child), "omega")["hard_valid"]
    return {"versions": versions, "canonical_relabelings": "PASS",
            "known_crossover_obstruction": report["status"], "positive_crossover": positive_report["status"]}


def resume_integration():
    cfg = dict(DEFAULTS)
    cfg.update({"starter_attempts_per_method_arm": 0, "starter_walk_attempts_per_reference": 0,
                "task_cpu_seconds": 0.1, "pilot_active_seconds": 8,
                "status_seconds": 0.2, "checkpoint_seconds": 0.2,
                "free_disk_floor_gib": 0.001})
    with tempfile.TemporaryDirectory(prefix="conway99-resume-") as temp:
        directory = Path(temp)
        config_path = directory / "control.json"
        atomic_json(config_path, cfg)
        run = directory / "run"
        command = [sys.executable, str(ROOT / "src/memetic_v2/runner.py"), "--config", str(config_path), "--run-dir", str(run)]
        log = (directory / "console.txt").open("w")
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 60
        while process.poll() is None and time.monotonic() < deadline:
            status_path = run / "status.json"
            if status_path.exists() and json.loads(status_path.read_text())["phase"] == "PILOT":
                break
            time.sleep(0.1)
        if process.poll() is not None:
            log.close()
            raise RuntimeError("Integration exited early: " + (directory / "console.txt").read_text())
        process.send_signal(signal.SIGKILL)
        process.wait(timeout=10)
        before, _ = Checkpoints(run).load()
        assert before["phase"] == "PILOT"
        resumed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=40)
        log.close()
        if resumed.returncode != 0:
            raise RuntimeError((directory / "console.txt").read_text())
        after, _ = Checkpoints(run).load()
        assert after["phase"] == "COMPLETE"
        assert after["pilot_active_seconds"] >= before["pilot_active_seconds"]
        assert after["fingerprint"] == before["fingerprint"]
        # Full candidate verification after process interruption and resume.
        for candidate in after["population"] + after["archive"]:
            assert check_graph(candidate["g6"], candidate["arm"], candidate)["hard_valid"]
        return {"interruption": "SIGKILL (no final checkpoint)", "interrupted_phase": before["phase"], "resumed_phase": after["phase"],
                "completed_tasks": after["completed_tasks"], "seed_configuration_preserved": True,
                "checkpoint_bytes": max(p.stat().st_size for p in (run / "checkpoints").glob("*.gz")),
                "last_measured_resources": json.loads((run / "status.json").read_text())["resources"]}


def multinorm_controls():
    from core import objective_key
    from runner import reference_candidates, build_generation_jobs, select_generation
    from reporting import write_report
    import copy
    import csv
    originals = reference_candidates()
    assert len(originals) == 64 and len({p["canonical"] for p in originals}) == 64
    rows_by_identity = {}
    for p in originals:
        origin = p["origin"]
        if origin.get("construction") == "verified_legal_trade":
            parent = rows_by_identity[origin["parent"]]
            assert encode_g6(apply_move(parent, tuple(tuple(tuple(edge) for edge in part) for part in origin["move"]))) == p["g6"]
        rows_by_identity[p["canonical"]] = decode_g6(p["g6"])
    a = next(p for p in originals if p["founder"] == "A_legacy_best_hard")
    b = next(p for p in originals if p["founder"] == "B_maple_20260829")
    assert (a["W"],a["L1"],a["F"],a["Linf"]) == (2175,2718,3926,4)
    assert (b["W"],b["L1"],b["F"],b["Linf"]) == (2110,3512,9716,10)
    # Opposing L1 and L2 rankings: sum-zero integer residual examples.
    x = {"L1":4,"F":8,"Linf":2,"Nmax":2}
    y = {"L1":6,"F":6,"Linf":1,"Nmax":6}
    assert objective_key(x,"L1") < objective_key(y,"L1")
    assert objective_key(x,"L2") > objective_key(y,"L2")
    assert objective_key(x,"Linf") > objective_key(y,"Linf")
    population = []
    for objective in DEFAULTS["objectives"]:
        for original in originals:
            candidate = dict(original, objective=objective, line_id=objective+"-"+original["line_id"])
            population.append(candidate)
    state = {"population":population,"archive":population,"phase":"PILOT","generation":0,"pilot_active_seconds":0}
    jobs = build_generation_jobs(state,DEFAULTS)
    assert len(jobs)==1536
    for i in range(0,len(jobs),3):
        assert [j["parent"]["objective"] for j in jobs[i:i+3]] == DEFAULTS["objectives"]
    assert all(j["partner"] is None or j["partner"]["objective"] == j["parent"]["objective"] for j in jobs)
    assert len({j["seed"] for j in jobs}) == len(jobs)
    # Existing copies in OTHER objectives do not reject a valid improving child.
    # Use two valid distinct graphs; selection logic is independent of the operator.
    state["jobs"]=[];state["results"]={}
    selected_parent = next(p for p in population if p["objective"]=="L2" and p["founder"]=="B_maple_20260829")
    child = dict(a,objective="L2")
    population[:] = [p for p in population if not (p["objective"]=="L2" and p["canonical"]==child["canonical"])]
    state["jobs"]=[{"id":"selection-control","parent":selected_parent}]
    state["results"]={"selection-control":{"candidate":child}}
    select_generation(state,DEFAULTS)
    accepted=next(p for p in population if p["line_id"]==selected_parent["line_id"])
    assert accepted["canonical"]==child["canonical"] and accepted["founder"]==selected_parent["founder"]
    with tempfile.TemporaryDirectory() as temporary:
        write_report(Path(temporary),state,{"utc":"2026-09-11T00:00:00Z"})
        with (Path(temporary)/"convergence.csv").open(encoding="utf-8-sig",newline="") as f:
            records=list(csv.DictReader(f,delimiter=";"))
        assert len(records)==36
        assert all(float(r["L1_best"])<=float(r["L1_mean"])<=float(r["L1_worst"]) for r in records)
    return {"unique_starters":64,"norm_copies":192,"jobs_per_generation":1536,
            "historical_A_B":"PASS","genealogies_replayed":"PASS",
            "cross_objective_isolation":"PASS","csv_rows_per_sample":36}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = {"scope": "FULL" if args.full else "CORE_ONLY", "status": "RUNNING"}
    try:
        result["mathematics"] = mathematics()
        result["persistence"] = persistence()
        if args.full:
            result["installed_algorithms"] = installed_algorithms()
            result["multinorm"] = multinorm_controls()
            result["resume_integration"] = resume_integration()
        else:
            result["not_run"] = ["pynauty canonicalization", "OR-Tools subproblems", "live coordinator interruption/resume"]
        result["status"] = "PASS"
    except BaseException as error:
        result["status"] = "FAIL"
        result["error"] = repr(error)
        raise
    finally:
        result["wall_seconds"] = time.monotonic() - started
        atomic_json(Path(args.output), result)
        print(json.dumps({k: result[k] for k in ("scope", "status", "wall_seconds")}), flush=True)


if __name__ == "__main__":
    main()
