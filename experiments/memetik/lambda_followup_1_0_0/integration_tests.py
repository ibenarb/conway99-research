"""Real short workers; WSL host calls replaced only inside this local test harness."""
import boot
from util import *
from coordinator import Coordinator
import coordinator
import copy
import tempfile
from unittest.mock import patch

class FixtureHost:
    def __init__(self):
        self.last = {}
        self.sample()
    def sample(self):
        self.last = {"host_seconds": time.monotonic(), "utc": "TEST_FIXTURE",
                     "windows_cpu_seconds": 0, "physical_free_bytes": 100 * GIB}
        return self.last

def fixture_resources(*args):
    return {"hazards": []}

def task(variant, ceiling, founders):
    cfg = read(boot.FROZEN / "config.json")
    cfg["milestones_cpu_seconds"] = [1, 2, ceiling]
    cfg["checkpoint_wall_seconds"] = 1
    return {"id": "test-" + variant, "kind": "compare", "arm": "lambda", "variant": variant,
            "target": "W", "seed": 22, "replicate": 0, "worker_cpu_seconds": ceiling,
            "founders": founders, "config": cfg}

class PauseCoordinator(Coordinator):
    def monitor(self):
        host, usage = super().monitor()
        if any(v["cpu"] >= 0.8 for v in usage.values()):
            self.stop_reason = "TEST_REQUESTED_PAUSE"
        return host, usage

def execute(run, plan, cls=Coordinator):
    with patch.object(coordinator, "resources", fixture_resources):
        return cls(run, plan, FixtureHost(), AuxiliaryLedger(run)).execute()

def main():
    started = own_cpu()
    founders = read(boot.FROZEN / "founders.json")
    report = {}
    with tempfile.TemporaryDirectory() as temp:
        run = Path(temp)
        jobs = []
        for variant in ("P", "PC"):
            d = run / "runs" / "comparison" / "tasks" / ("test-" + variant)
            d.mkdir(parents=True)
            atomic(d / "task.json", task(variant, 12, founders))
            jobs.append({"id": "test-" + variant, "directory": str(d.relative_to(run)),
                         "variant": variant, "target": "W", "group": "method", "initial_actual_cpu": 0,
                         "cumulative_budget_seconds": 12, "additional_cpu_seconds": 12})
        atomic(run / "runs/comparison/budget.json", {"per_job_cpu_seconds": 12})
        plan = {"jobs": jobs, "queue": [j["id"] for j in jobs], "workers": 2}
        try:
            execute(run, plan, PauseCoordinator)
        except RuntimeError as error:
            assert "PAUSED" in str(error)
        else:
            raise AssertionError("Pause did not occur")
        for job in jobs:
            r = receipt_valid(run / job["directory"])
            assert r["status"] == "PAUSED" and len(r["sessions"]) == 1
        assert execute(run, plan) == "COMPLETE"
        old = {}
        for job in jobs:
            d = run / job["directory"]
            r = receipt_valid(d)
            assert r["status"] == "COMPLETE" and len(r["sessions"]) == 2
            assert r["budget_cpu_seconds"] <= 12
            old[job["id"]] = read(d / "result.json")
        assert execute(run, plan) == "COMPLETE"
        assert all(len(receipt_valid(run / j["directory"])["sessions"]) == 2 for j in jobs)
        atomic(run / "runs/comparison/budget.json", {"per_job_cpu_seconds": 22})
        for job in jobs:
            job["cumulative_budget_seconds"] = 22
        assert execute(run, plan) == "COMPLETE"
        for job in jobs:
            d = run / job["directory"]
            r = receipt_valid(d)
            result = read(d / "result.json")
            assert len(r["sessions"]) == 3 and r["budget_cpu_seconds"] <= 22
            assert r["closed_reserve_cpu_seconds"] > 0
            assert result["curves"][:len(old[job["id"]]["curves"])] == old[job["id"]]["curves"]
            for mark in ("1", "2", "12"):
                assert result["milestones"][mark] == old[job["id"]]["milestones"][mark]
        report["real_workers"] = {"variants": ["P", "PC"], "pause_resume_extend": True,
                                  "completed_jobs_skipped": True, "closed_reserves_retained": True,
                                  "old_curves_milestones_unchanged": True}
        d = run / jobs[0]["directory"]
        for name in ("task.json", "result.json", "checkpoint.json", "archive.sqlite"):
            before = (d / name).read_bytes()
            (d / name).write_bytes(before + b" ")
            try:
                receipt_valid(d)
            except (RuntimeError, json.JSONDecodeError):
                pass
            else:
                raise AssertionError("Tampering accepted: " + name)
            (d / name).write_bytes(before)
        report["tamper_rejections"] = ["task", "result", "checkpoint", "archive"]
        atomic(d / "active.json", {"pid": 99999999})
        try:
            execute(run, plan)
        except RuntimeError as error:
            assert "Unresolved" in str(error)
        else:
            raise AssertionError("Unresolved CPU allowed")
        (d / "active.json").unlink()
        report["unresolved_cpu_rejected"] = True
        # Both roots participate in solution handling; wrong-order graph is a negative control.
        from common import verifier
        rook = [sum(1 << j for j in range(9) if j != i and (i // 3 == j // 3 or i % 3 == j % 3)) for i in range(9)]
        g6 = core.encode_g6(rook)
        assert verifier.check_graph(g6, "lambda", expected_n=9, expected_degree=4)["is_solution"]
        root = run / "runs" / "records"
        root.mkdir(parents=True)
        marker = {"candidate": {"graph6": g6, "scores": {"F": 0}}}
        atomic(root / "SOLUTION.json", marker)
        c = Coordinator(run, plan, FixtureHost(), AuxiliaryLedger(run))
        try:
            try:
                c.check_solution()
            except ValueError:
                pass
            else:
                raise AssertionError("Wrong order accepted in production")
            with patch.object(coordinator, "checked", return_value=(rook, {"F": 0})):
                c.check_solution()
            assert c.stop_reason == "VERIFIED_SOLUTION"
            assert read(run / "SOLUTION.json") == marker == read(run / "SOLUTION_BACKUP.json")
        finally:
            for sig, handler in c.owned_signals.items():
                signal.signal(sig, handler)
        report["global_solution"] = {"both_roots": True, "double_saved": True,
                                    "wrong_order_rejected": True, "positive_plumbing": "real rook graph with explicit fixture injection"}
        from clock import resources
        with patch("clock.memory", return_value={"MemAvailable": 47 * GIB}), patch("clock.shutil.disk_usage", return_value=type("D", (), {"free": 100 * GIB})()):
            hazards = resources(run, {"physical_free_bytes": 49 * GIB}, {})["hazards"]
            assert hazards == ["WINDOWS_VHDX_RESERVE"]
        report["host_disk_guard_fixture"] = True
    report.update(status="INTEGRATION_PASS", real_wsl_host_test=False, own_cpu=own_cpu()-started,
                  waited_child_cpu=child_cpu())
    if len(sys.argv) > 1:
        atomic(Path(sys.argv[1]), report)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
