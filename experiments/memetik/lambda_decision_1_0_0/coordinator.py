"""One owner for 14 jobs, two budget roots, receipts, solutions and safeguards."""
import boot
import statistics
from util import *
from clock import HostClock, resources
from prepare import verify
from search import key

class Coordinator:
    def __init__(self, run, plan, host, ledger):
        self.run, self.plan, self.host, self.ledger = Path(run), plan, host, ledger
        self.active = {}
        self.stop_reason = None
        self.started = host.sample()["host_seconds"]
        self.last_status = -10000
        self.session_cpu = 0.0
        self.last_sample = host.last
        self.counter_before = {}
        self.worker_efficiency = None
        self.error = None
        self.owned_signals = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGINT)}
        for s in self.owned_signals:
            signal.signal(s, self.stop)

    def stop(self, *args):
        self.stop_reason = self.stop_reason or "USER_REQUESTED_PAUSE"

    def directory(self, job):
        return self.run / job["directory"]

    def worker(self, job):
        return boot.HERE / "worker.py"

    def pending(self):
        by_id = {j["id"]: j for j in self.plan["jobs"]}
        pending = []
        for jid in self.plan["queue"]:
            job = by_id[jid]
            d = self.directory(job)
            if (d / "active.json").exists():
                raise RuntimeError("Unresolved CPU session: " + jid)
            r = receipt_valid(d) if (d / "receipt.json").exists() else None
            if r:
                result = read(d / "result.json")
                if r["status"] == "SOLUTION":
                    self.stop_reason = "VERIFIED_SOLUTION_PENDING_CHECK"
                    continue
                if r["status"] == "COMPLETE" and result["endpoint_cpu_seconds"] == job["cumulative_budget_seconds"]:
                    continue
                base = r["budget_cpu_seconds"]
                if r["status"] == "COMPLETE":
                    base = max(base, result["endpoint_cpu_seconds"])
            else:
                if any((d / f).exists() for f in ("checkpoint.json", "result.json", "archive.sqlite")):
                    raise RuntimeError("State without receipt: " + jid)
                base = 0.0
            if base >= job["cumulative_budget_seconds"]:
                raise RuntimeError("Exhausted budget without endpoint: " + jid)
            pending.append((job, base, r or {}))
        return pending

    def check_solution(self):
        for part in ("comparison", "records"):
            marker = self.run / "runs" / part / "SOLUTION.json"
            if marker.exists():
                value = read(marker)
                _, scores = checked(value["candidate"]["graph6"], "lambda")
                if scores["F"] != 0:
                    raise RuntimeError("False solution marker")
                atomic(self.run / "SOLUTION.json", value)
                atomic(self.run / "SOLUTION_BACKUP.json", value)
                self.stop_reason = "VERIFIED_SOLUTION"

    def monitor(self):
        host = self.host.sample()
        active = {pid: process(pid) for pid in self.active}
        report = resources(self.run, host, active)
        if report["hazards"]:
            self.stop_reason = str(report["hazards"])
        # Each single-thread worker cannot gain > host seconds of CPU.
        delta = host["host_seconds"] - self.last_sample["host_seconds"]
        if delta > 0:
            ratios = [(value["cpu"] - self.counter_before[pid]) / delta for pid, value in active.items() if pid in self.counter_before]
            if ratios:
                self.worker_efficiency = min(1.0, statistics.median(ratios))
            for pid, value in active.items():
                if pid in self.counter_before and value["cpu"] - self.counter_before[pid] > 1.02 * delta + 0.15:
                    self.stop_reason = "CPU_HOST_INCONSISTENCY"
        self.counter_before = {pid: value["cpu"] for pid, value in active.items()}
        self.last_sample = host
        with (self.run / "clock_samples.jsonl").open("a") as stream:
            stream.write(json.dumps({"host": host, "active_cpu": self.counter_before}) + "\n")
        if self.ledger.remaining("infrastructure") - own_cpu() - host["windows_cpu_seconds"] < 120:
            self.stop_reason = "INFRASTRUCTURE_RESERVE"
        self.check_solution()
        return host, active

    def status(self, pending, active, force=False):
        now = self.host.last["host_seconds"]
        if not force and now - self.last_status < 600:
            return
        used = 0.0
        best = {}
        for job in self.plan["jobs"]:
            d = self.directory(job)
            if (d / "receipt.json").exists():
                used += max(0, read(d / "receipt.json")["cpu_seconds"] - job["initial_actual_cpu"])
            path = d / "checkpoint.json"
            if path.exists():
                state = read(path)["state"]
                group = job["group"] + "/" + job["variant"] + "/" + job["target"]
                sc = state["best"]["scores"]
                if group not in best or key(sc, job["target"]) < key(best[group], job["target"]):
                    best[group] = sc
        live = sum(v["cpu"] for v in active.values())
        elapsed = now - self.started
        rate = (self.session_cpu + live) / elapsed if elapsed else 0
        remain = sum(job["cumulative_budget_seconds"] - base for job, base, _ in pending)
        remain += sum(max(0, e["job"]["cumulative_budget_seconds"] - e["base"] - active.get(pid, {}).get("cpu", 0))
                      for pid, e in self.active.items())
        value = {"status": "RUNNING" if not self.stop_reason else "PAUSING", "utc": self.host.last["utc"],
                 "active_workers": len(self.active), "pending_jobs": len(pending),
                 "new_search_cpu_hours": (used + live) / 3600, "best_by_group": best,
                 "session_host_seconds": elapsed, "observed_cpu_per_host_second": rate,
                 "budget_eta_seconds": (max([max(0, e["job"]["cumulative_budget_seconds"] - e["base"] - active.get(pid, {}).get("cpu", 0)) for pid, e in self.active.items()] + [job["cumulative_budget_seconds"] - base for job, base, _ in pending] + [0]) / self.worker_efficiency) if self.worker_efficiency and self.worker_efficiency > 0 and elapsed >= 60 else None,
                 "eta_scope": "longest remaining job / recent median per-worker host efficiency; not solution time",
                 "stop_reason": self.stop_reason}
        atomic(self.run / "status.json", value)
        print("STATUS " + json.dumps(value), flush=True)
        self.last_status = now

    def signal_owned(self):
        for pid, entry in self.active.items():
            if not entry.get("stop_sent"):
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                entry["stop_sent"] = True

    def reap(self, blocking=False):
        for pid in list(self.active):
            waited, status, usage = os.wait4(pid, 0 if blocking else os.WNOHANG)
            if not waited:
                continue
            e = self.active.pop(pid)
            e["proc"].returncode = os.waitstatus_to_exitcode(status)
            self.session_cpu += usage.ru_utime + usage.ru_stime
            # A failed write deliberately leaves active.json as an unresolved receipt.
            r = make_receipt(e["d"], e["previous"], e["base"], e["job"]["cumulative_budget_seconds"],
                             e["proc"].returncode, usage, e["host_start"], self.host.last["host_seconds"])
            (e["d"] / "active.json").unlink()
            if r["exit_code"] or r["budget_cpu_seconds"] > e["job"]["cumulative_budget_seconds"]:
                self.stop_reason = "WORKER_FAILED_OR_OVERRUN:" + e["job"]["id"]

    def execute(self):
        try:
            pending = self.pending()
            while pending or self.active:
                host, active = self.monitor()
                if self.stop_reason:
                    self.signal_owned()
                while pending and len(self.active) < self.plan["workers"] and not self.stop_reason:
                    job, base, previous = pending.pop(0)
                    d = self.directory(job)
                    with (d / "worker.log").open("ab") as log:
                        proc = subprocess.Popen([sys.executable, str(self.worker(job)), str(d)],
                                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                                env={**os.environ, **THREAD_ENV})
                    self.active[proc.pid] = {"proc": proc, "job": job, "base": base, "previous": previous,
                                              "d": d, "host_start": host["host_seconds"]}
                    atomic(d / "active.json", {"pid": proc.pid, "start_ticks": process(proc.pid)["start_ticks"],
                                               "base_cpu_seconds": base, "external_id": job["id"]})
                self.reap()
                active = {pid: process(pid) for pid in self.active}
                self.status(pending, active)
                if self.stop_reason and not self.active:
                    break
                if pending or self.active:
                    time.sleep(2)
            self.check_solution()
            self.status(pending, {}, force=True)
            if self.stop_reason and self.stop_reason != "VERIFIED_SOLUTION":
                raise RuntimeError("PAUSED: " + self.stop_reason)
        except BaseException:
            self.signal_owned()
            self.reap(blocking=True)
            raise
        finally:
            for sig, handler in self.owned_signals.items():
                signal.signal(sig, handler)
        return "SOLUTION" if self.stop_reason == "VERIFIED_SOLUTION" else "COMPLETE"
