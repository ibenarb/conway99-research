"""Persistent Windows monotonic intervals; no fallback that pretends a host test."""
import boot
from util import *
import base64
import selectors
import shutil
from resources import memory, GROUP_LIMIT, RAM_RESERVE, LINUX_RESERVE, HOST_RESERVE

def guest():
    return {name: time.clock_gettime(getattr(time, "CLOCK_" + name))
            for name in ("REALTIME", "MONOTONIC", "MONOTONIC_RAW", "BOOTTIME")
            if hasattr(time, "CLOCK_" + name)}

class HostClock:
    def __init__(self, logdir):
        distro = os.environ.get("WSL_DISTRO_NAME", "")
        if not distro or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. " for c in distro):
            raise RuntimeError("This launch requires a named WSL distribution on Ryzen")
        exe = shutil.which("powershell.exe")
        if not exe:
            raise RuntimeError("Windows PowerShell interop unavailable")
        self.logdir = Path(logdir)
        self.error = (self.logdir / "host_stderr.log").open("ab")
        script = (boot.HERE / "host.ps1").read_text()
        # WSLENV propagation is not assumed: encode an explicit validated distro.
        script = "$env:CONWAY_WSL_DISTRO = '" + distro + "'\n" + script
        encoded = base64.b64encode(script.encode("utf-16-le")).decode()
        self.proc = subprocess.Popen([exe, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.error)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.buffer = b""
        self.last = None
        self.helper_linux_cpu = 0.0
        self.closed = False
        try:
            self.first = self.sample(timeout=40)
        except BaseException:
            self.proc.stdin.close()
            try:
                os.kill(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            _, status, usage = os.wait4(self.proc.pid, 0)
            self.proc.returncode = os.waitstatus_to_exitcode(status)
            self.error.close()
            self.selector.close()
            atomic(self.logdir / "HOST_START_FAILED.json", {
                "linux_helper_cpu": usage.ru_utime + usage.ru_stime,
                "windows_cpu": "UNRESOLVED", "status": "DIAGNOSIS_REQUIRED"})
            raise

    def sample(self, command="sample", timeout=15):
        before = guest()
        self.proc.stdin.write((command + "\n").encode())
        self.proc.stdin.flush()
        until = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            left = until - time.monotonic()
            if left <= 0 or not self.selector.select(left):
                raise RuntimeError("Windows host clock timeout")
            data = os.read(self.proc.stdout.fileno(), 65536)
            if not data:
                raise RuntimeError("Windows host clock exited; inspect host_stderr.log")
            self.buffer += data
        raw, self.buffer = self.buffer.split(b"\n", 1)
        value = json.loads(raw.decode("utf-8-sig"))
        value["guest_before"], value["guest_after"] = before, guest()
        if value["distribution"] != os.environ["WSL_DISTRO_NAME"] or not value["volume"]:
            raise RuntimeError("Wrong WSL/VHDX volume")
        if not 0 <= value["physical_free_bytes"] <= value["physical_total_bytes"]:
            raise RuntimeError("Invalid host storage result")
        if self.last and (value["host_seconds"] < self.last["host_seconds"]
                          or value["windows_cpu_seconds"] < self.last["windows_cpu_seconds"]
                          or value["volume"] != self.last["volume"]):
            raise RuntimeError("Host monotonic/CPU/volume changed")
        self.last = value
        return value

    def close(self):
        if self.closed:
            return self.last["windows_cpu_seconds"] + self.helper_linux_cpu
        try:
            self.sample("quit")
        except Exception:
            try:
                os.kill(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        self.proc.stdin.close()
        _, status, usage = os.wait4(self.proc.pid, 0)
        self.proc.returncode = os.waitstatus_to_exitcode(status)
        self.helper_linux_cpu = usage.ru_utime + usage.ru_stime
        self.error.close()
        self.selector.close()
        self.closed = True
        return (self.last["windows_cpu_seconds"] if self.last else 0) + self.helper_linux_cpu

def resources(run, host, active):
    hazards = []
    mem = memory()
    linux_free = shutil.disk_usage(run).free
    if linux_free < LINUX_RESERVE:
        hazards.append("LINUX_DISK_RESERVE")
    if host["physical_free_bytes"] < HOST_RESERVE:
        hazards.append("WINDOWS_VHDX_RESERVE")
    if mem["MemAvailable"] < RAM_RESERVE:
        hazards.append("RAM_RESERVE")
    if sum(v["rss"] for v in active.values()) + process(os.getpid())["rss"] > GROUP_LIMIT:
        hazards.append("GROUP_RAM_LIMIT")
    if any(v["rss"] > GIB for v in active.values()):
        hazards.append("WORKER_RAM_LIMIT")
    return {"hazards": hazards, "memory": mem, "linux_free_bytes": linux_free,
            "windows_free_bytes": host["physical_free_bytes"]}

def validate_clock_session(start, end, rows, workers):
    elapsed = end["host_seconds"] - start["host_seconds"]
    if elapsed <= 0:
        raise RuntimeError("Invalid host interval")
    total = 0.0
    for row in rows:
        cpu = row["wait4_cpu"]
        total += cpu
        if row["code"] or cpu > 180.01:
            raise RuntimeError("Clock worker failed or exceeded allocation")
        if abs(cpu - row["self_cpu"]) > max(0.1, 0.005 * cpu):
            raise RuntimeError("Self/wait4 mismatch")
        if cpu > elapsed * 1.02 + 0.1:
            raise RuntimeError("CPU exceeds independent host duration")
    if total > workers * elapsed * 1.02 + 0.1:
        raise RuntimeError("Group CPU exceeds host capacity")
    mono = end["guest_after"]["MONOTONIC"] - start["guest_after"]["MONOTONIC"]
    return {"host_elapsed": elapsed, "guest_monotonic_elapsed": mono,
            "guest_monotonic_drift": abs(mono - elapsed) > max(0.5, elapsed * 0.005),
            "total_wait4_cpu": total, "status": "CPU_HOST_PASS",
            "eta_basis": "persistent Windows monotonic host"}

def probe(run, host, ledger, monitor):
    results = []
    out = Path(run) / "diagnostics"
    for count in (1, 18):
        label = "clock-" + str(count)
        remaining = ledger.remaining("clocks")
        maximum = count * 60
        ledger.begin("clocks", label, maximum)
        children = {}
        rows = []
        start = host.sample()
        print("CLOCK_PROBE_START " + json.dumps({"workers": count, "new_cpu_ceiling": maximum}), flush=True)
        try:
            for i in range(count):
                path = out / (label + "-" + str(i) + ".json")
                log = (out / (label + "-" + str(i) + ".log")).open("ab")
                proc = subprocess.Popen([sys.executable, str(boot.HERE / "aux_worker.py"), "spin", str(path), "60"],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                        env={**os.environ, **THREAD_ENV})
                log.close()
                children[proc.pid] = (proc, path)
            while children:
                now = host.sample()
                hazards = resources(run, now, {p: process(p) for p in children})["hazards"]
                if hazards:
                    raise RuntimeError(str(hazards))
                monitor()
                for pid in list(children):
                    waited, status, usage = os.wait4(pid, os.WNOHANG)
                    if not waited:
                        continue
                    proc, path = children.pop(pid)
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    value = read(path) if path.exists() else {}
                    rows.append({"code": proc.returncode, "wait4_cpu": usage.ru_utime + usage.ru_stime,
                                 "self_cpu": value.get("self_cpu", -1)})
                if children:
                    time.sleep(2)
        except BaseException:
            for pid in children:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            for pid, (proc, path) in children.items():
                _, status, usage = os.wait4(pid, 0)
                proc.returncode = os.waitstatus_to_exitcode(status)
                rows.append({"code": proc.returncode, "wait4_cpu": usage.ru_utime + usage.ru_stime,
                             "self_cpu": -1})
            ledger.finish(sum(r["wait4_cpu"] for r in rows), "FAILED")
            raise
        end = host.sample()
        ledger.finish(sum(r["wait4_cpu"] for r in rows), "FINISHED", rows)
        verdict = validate_clock_session(start, end, rows, count)
        results.append({"workers": count, **verdict})
        print("CLOCK_PROBE_FINISHED " + json.dumps(results[-1]), flush=True)
    atomic(Path(run) / "CLOCK_PASS.json", {"status": "CLOCK_PASS", "sessions": results})
    return results
