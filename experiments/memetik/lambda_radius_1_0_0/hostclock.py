"""Persistent Windows monotonic intervals; no fallback that pretends a host test."""
import boot
from support import *
import base64
import selectors
import shutil


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
