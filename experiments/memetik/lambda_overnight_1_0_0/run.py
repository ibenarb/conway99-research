"""Ryzen CLI. Preflight/controls precede launch; no automatic budget extension."""
import boot
from util import *
from prepare import prepare, verify, package_verify
from clock import HostClock, probe, resources
from coordinator import Coordinator
from evaluate import evaluate
import argparse
import shutil
import tarfile

def monitor_aux(run, host, process_id):
    host.sample()
    usage = {process_id: process(process_id)}
    hazards = resources(run, host.last, usage)["hazards"]
    if hazards:
        raise RuntimeError(str(hazards))

def auxiliary(run, host, ledger, category, action, destination, extra=()):
    ceiling = ledger.remaining(category)
    if ceiling < 10:
        raise RuntimeError("Auxiliary budget unavailable: " + category)
    ledger.begin(category, action, ceiling)
    with (run / "diagnostics" / (action + ".log")).open("ab") as log:
        proc = subprocess.Popen([sys.executable, str(boot.HERE / "aux_worker.py"), action,
                                 str(destination), str(ceiling), *map(str, extra)],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, **THREAD_ENV})
    usage = None
    last_status = -10000
    print("AUX_START " + json.dumps({"action": action, "cpu_ceiling": ceiling}), flush=True)
    try:
        while True:
            pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                proc.returncode = os.waitstatus_to_exitcode(status)
                break
            monitor_aux(run, host, proc.pid)
            if host.last["host_seconds"] - last_status >= 600:
                print("AUX_STATUS " + json.dumps({"action": action, "self_cpu": process(proc.pid)["cpu"],
                                                 "cpu_ceiling": ceiling, "utc": host.last["utc"]}), flush=True)
                last_status = host.last["host_seconds"]
            time.sleep(2)
    except BaseException:
        try:
            os.kill(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        _, status, usage = os.wait4(proc.pid, 0)
        proc.returncode = os.waitstatus_to_exitcode(status)
        ledger.finish(usage.ru_utime + usage.ru_stime, "FAILED")
        raise
    ledger.finish(usage.ru_utime + usage.ru_stime, "FINISHED" if proc.returncode == 0 else "FAILED")
    if proc.returncode or not destination.exists():
        raise RuntimeError("Auxiliary failed; inspect " + action + ".log")
    return read(destination)

def gate(run, filename, expected):
    value = read(run / filename)
    if value["status"] != expected or value.get("fingerprint_sha256") != file_sha(run / "FINGERPRINT.json"):
        raise RuntimeError("Missing or stale gate: " + filename)
    return value

def check(run):
    plan = verify(run)
    ledger = AuxiliaryLedger(run)
    host = None
    try:
        host = HostClock(run)
        if len(os.sched_getaffinity(0)) < 8:
            raise RuntimeError("Fewer than 8 available logical CPUs")
        if not (run / "CLOCK_PASS.json").exists():
            probe(run, host, ledger, lambda: None)
            value = read(run / "CLOCK_PASS.json")
            value["fingerprint_sha256"] = file_sha(run / "FINGERPRINT.json")
            atomic(run / "CLOCK_PASS.json", value)
        else:
            gate(run, "CLOCK_PASS.json", "CLOCK_PASS")
        destination = run / "CONTROLS_PASS.json"
        if not destination.exists():
            result = auxiliary(run, host, ledger, "controls", "controls", destination, (run,))
            if result["status"] != "CONTROLS_PASS":
                raise RuntimeError("Controls did not pass")
            result["fingerprint_sha256"] = file_sha(run / "FINGERPRINT.json")
            atomic(destination, result)
        else:
            gate(run, "CONTROLS_PASS.json", "CONTROLS_PASS")
        result = {"status": "READY_NOT_STARTED", "fingerprint_sha256": file_sha(run / "FINGERPRINT.json"),
                  "clock": gate(run, "CLOCK_PASS.json", "CLOCK_PASS"),
                  "host": host.sample(), "jobs": 8, "search_budget_cpu_hours": 56, "maximum_total_cpu_hours": 57}
        if resources(run, host.last, {})["hazards"]:
            raise RuntimeError("Resource reserve failed")
        atomic(run / "READY.json", result)
        print(json.dumps({k: v for k, v in result.items() if k != "clock"}, indent=2))
    finally:
        host_cpu = host.close() if host else 0
        ledger.charge_infrastructure(own_cpu(), "check", host_cpu)

def do_run(run):
    plan = verify(run)
    if (run / "DIAGNOSIS_REQUIRED.json").exists() or (run / "HOST_START_FAILED.json").exists():
        raise RuntimeError("A recorded technical fault requires diagnosis")
    gate(run, "READY.json", "READY_NOT_STARTED")
    gate(run, "CLOCK_PASS.json", "CLOCK_PASS")
    gate(run, "CONTROLS_PASS.json", "CONTROLS_PASS")
    ledger = AuxiliaryLedger(run)
    if read(ledger.path)["active"] is not None:
        raise RuntimeError("Unresolved auxiliary CPU")
    host = None
    try:
        host = HostClock(run)
        if resources(run, host.sample(), {})["hazards"]:
            raise RuntimeError("Resource reserve failed")
        state = Coordinator(run, plan, host, ledger).execute()
        if state == "COMPLETE":
            report = evaluate(run)
            print("SEARCH_ENDPOINTS_VERIFIED " + json.dumps(report), flush=True)
            print("FRONTIER_VERIFIED " + json.dumps(report), flush=True)
            atomic(run / "COMPLETE.json", {"status": "FRONTIER_VERIFIED", "utc": host.sample()["utc"]})
        else:
            print("VERIFIED_SOLUTION_SAVED", flush=True)
        status = read(run / "status.json")
        status["status"] = state
        atomic(run / "status.json", status)
    except BaseException as error:
        if "USER_REQUESTED_PAUSE" not in str(error):
            atomic(run / "DIAGNOSIS_REQUIRED.json", {"status": "DIAGNOSIS_REQUIRED", "error": str(error)})
        raise
    finally:
        host_cpu = host.close() if host else 0
        ledger.charge_infrastructure(own_cpu(), "controller", host_cpu)

def export(run):
    verify(run)
    if any((run / "runs").glob("*/tasks/*/active.json")):
        raise RuntimeError("Active/unresolved tasks; export refused")
    destination = run.parent / (run.name + "_verified.tar.gz")
    if destination.exists():
        raise FileExistsError(destination)
    if not (run / "COMPLETE.json").exists() and not (run / "SOLUTION.json").exists():
        raise RuntimeError("Use status/diagnose; no verified completion to export")
    if (run / "COMPLETE.json").exists():
        evaluate(run)
    path = destination.with_suffix(destination.suffix + ".partial")
    with tarfile.open(path, "w:gz") as archive:
        archive.add(run, arcname=run.name)
    os.replace(path, destination)
    digest = file_sha(destination)
    Path(str(destination) + ".sha256").write_text(digest + "  " + destination.name + "\n")
    AuxiliaryLedger(run).charge_infrastructure(own_cpu(), "export")
    print(json.dumps({"archive": str(destination), "sha256": digest}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "check", "launch", "run", "status", "evaluate", "export", "pause"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    run = args.directory.expanduser().resolve()
    if args.action == "prepare":
        prepare(None, run)
        return
    if args.action == "status":
        print(json.dumps(read(run / "status.json") if (run / "status.json").exists()
                         else {"prepared": (run / "PREPARED.json").exists(), "ready": (run / "READY.json").exists()}, indent=2))
        return
    # All state-changing actions execute the frozen copy; exec retains process CPU.
    frozen = run / "program" / Path(__file__).resolve().relative_to(boot.ROOT)
    if Path(__file__).resolve() != frozen:
        verify(run)
        os.execv(sys.executable, [sys.executable, str(frozen), *sys.argv[1:]])
    if args.action == "pause":
        value = read(run / "launcher.json")
        live = process(value["pid"])
        if live["start_ticks"] != value["start_ticks"] or live["start_ticks"] is None:
            raise RuntimeError("Owned launcher PID no longer matches")
        os.kill(value["pid"], signal.SIGTERM)
        print("PAUSE_REQUEST_SENT")
        return
    inherited = os.environ.pop("CONWAY_LOCK_FD", None)
    if inherited is not None and args.action == "run":
        fd = int(inherited)
        if os.fstat(fd).st_ino != (run / "controller.lock").stat().st_ino:
            raise RuntimeError("Invalid inherited controller lock")
        owner = os.fdopen(fd, "r+")
        token = os.environ.pop("CONWAY_LAUNCH_TOKEN")
        until = time.monotonic() + 15
        while not (run / "launch_ready.json").exists() or read(run / "launch_ready.json").get("token") != token:
            if time.monotonic() > until:
                raise RuntimeError("Launcher handoff incomplete")
            time.sleep(0.05)
    else:
        owner = lock(run / "controller.lock")
    try:
        if args.action == "check":
            check(run)
        elif args.action == "run":
            do_run(run)
        elif args.action == "launch":
            verify(run)
            if (run / "DIAGNOSIS_REQUIRED.json").exists() or (run / "HOST_START_FAILED.json").exists():
                raise RuntimeError("Recorded fault needs diagnosis before launch")
            gate(run, "READY.json", "READY_NOT_STARTED")
            if any((run / "runs").glob("*/tasks/*/active.json")):
                raise RuntimeError("Unresolved worker receipt")
            import uuid
            token = uuid.uuid4().hex
            with (run / "controller.log").open("ab") as log:
                child = subprocess.Popen([sys.executable, str(frozen), "run", str(run)],
                                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                         start_new_session=True, pass_fds=(owner.fileno(),),
                                         env={**os.environ, "CONWAY_LOCK_FD": str(owner.fileno()), "CONWAY_LAUNCH_TOKEN": token})
            atomic(run / "launcher.json", {"pid": child.pid, "start_ticks": process(child.pid)["start_ticks"]})
            AuxiliaryLedger(run).charge_infrastructure(own_cpu(), "launch")
            atomic(run / "launch_ready.json", {"token": token})
            print(json.dumps({"status": "LAUNCHED_CHECK_LOG", "pid": child.pid, "run": str(run)}))
        elif args.action == "evaluate":
            print(json.dumps(evaluate(run), indent=2))
            AuxiliaryLedger(run).charge_infrastructure(own_cpu(), "evaluate")
        elif args.action == "export":
            export(run)
    finally:
        owner.close()

if __name__ == "__main__":
    main()
