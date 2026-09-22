"""Host transport, inherited-lock and accounting failure controls."""
import boot
from util import *
import clock
import harvest
import tempfile
from unittest.mock import patch

def main():
    report = {}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        original_popen = subprocess.Popen
        server = """import sys,json,time,os
start=time.monotonic()
for line in sys.stdin:
    print(json.dumps(dict(host_seconds=time.monotonic()-start,utc="FIXTURE",
        windows_cpu_seconds=time.process_time(),windows_pid=os.getpid(),
        distribution="Ubuntu",vhdx="fixture",volume="fixture-volume",
        physical_free_bytes=100*1024**3,physical_total_bytes=200*1024**3)),flush=True)
    if line.strip()=="quit": break
"""
        def fake_powershell(command, **kwargs):
            return original_popen([sys.executable, "-u", "-c", server], **kwargs)
        with patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu"}), patch.object(clock.shutil, "which", return_value="fixture"):
            with patch.object(clock.subprocess, "Popen", side_effect=fake_powershell):
                h = clock.HostClock(root)
                first = h.sample()
                second = h.sample()
                assert second["host_seconds"] >= first["host_seconds"]
                assert h.close() >= 0
                assert h.closed
        report["host_transport"] = "PASS using Python pipe server, not Windows"
        ledger = AuxiliaryLedger(root)
        ledger.begin("harvest", "fixture", 2)
        try:
            ledger.begin("harvest", "overlap", 1)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Overlapping auxiliary accepted")
        ledger.finish(1, "PASS")
        assert ledger.remaining("harvest") == 3599
        ledger.begin("controls", "overrun", 1)
        try:
            ledger.finish(2, "FAILED")
        except RuntimeError:
            pass
        else:
            raise AssertionError("Auxiliary overrun accepted")
        assert ledger.used("controls") == 2
        report["auxiliary_transactions"] = "Overlap and overrun rejected; consumed CPU retained"
        # Real descriptor inheritance, same open file description held by child.
        owner = lock(root / "controller.lock")
        child_code = """import os,sys,time,json,pathlib
fd=int(sys.argv[1]); root=pathlib.Path(sys.argv[2])
assert os.fstat(fd).st_ino==(root/"controller.lock").stat().st_ino
(root/"child_ready").write_text("ready")
until=time.monotonic()+5
while not (root/"release").exists():
    if time.monotonic()>until: raise RuntimeError("handoff timeout")
    time.sleep(.02)
"""
        child = original_popen([sys.executable, "-c", child_code, str(owner.fileno()), str(root)],
                               pass_fds=(owner.fileno(),))
        until = time.monotonic()+5
        while not (root/"child_ready").exists():
            assert time.monotonic()<until
            time.sleep(.02)
        owner.close()
        try:
            bad = lock(root / "controller.lock")
        except BlockingIOError:
            pass
        else:
            bad.close()
            raise AssertionError("Inherited lock lost")
        (root/"release").write_text("release")
        _, status, usage = os.wait4(child.pid,0)
        child.returncode = os.waitstatus_to_exitcode(status)
        assert child.returncode == 0
        free = lock(root / "controller.lock")
        free.close()
        report["lock_handoff"] = "Child retains exclusive lock after parent closes"
        founders = read(boot.FROZEN / "founders.json")
        f=founders[0]
        try:
            harvest.save_solution(root,f["graph6"],{**f["scores"],"F":0},"negative fixture")
        except RuntimeError:
            pass
        else:
            raise AssertionError("False harvest solution accepted")
        rook = [sum(1<<j for j in range(9) if j!=i and (i//3==j//3 or i%3==j%3)) for i in range(9)]
        g6=core.encode_g6(rook)
        with patch.object(harvest,"checked",return_value=(rook,{"F":0})):
            try:
                harvest.save_solution(root,g6,{"F":0},"explicit rook plumbing fixture")
            except harvest.FoundSolution:
                pass
            else:
                raise AssertionError("Harvest did not stop on solution")
        assert read(root/"SOLUTION.json")==read(root/"SOLUTION_BACKUP.json")
        report["harvest_solution"] = "False zero rejected; positive fixture double-saved and stops"
    report.update(status="INFRASTRUCTURE_TESTS_PASS",real_windows_or_ryzen_test=False)
    if len(sys.argv)>1:
        atomic(Path(sys.argv[1]),report)
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
