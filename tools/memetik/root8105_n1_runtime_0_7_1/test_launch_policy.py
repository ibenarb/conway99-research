"""Exact launch contract with mocked Windows transport, not Windows acceptance."""
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
from unittest.mock import patch
import platform_adapter as pa


def main():
    with tempfile.TemporaryDirectory() as directory:
        observer = pa.Observer.__new__(pa.Observer)
        observer.folder = Path(directory)
        observer.session = "policy-regression"
        observer.started = time.monotonic()
        observer.log = io.BytesIO()
        observer.fault = None
        observer.tick = lambda: None
        calls = []
        windows_paths = iter(["C:\\fixture\\host_clock.ps1", "C:\\fixture\\output"])

        def launch(argv, **kwargs):
            calls.append((argv, kwargs))
            (observer.folder / "heartbeat.json").write_text("{}")
            return object()

        with patch.object(pa.platform, "release", return_value="microsoft-test"), \
                patch.object(pa.shutil, "which", side_effect=lambda name: name), \
                patch.object(pa.subprocess, "check_output", side_effect=lambda *a, **k: next(windows_paths)), \
                patch.object(pa.subprocess, "Popen", side_effect=launch):
            observer.start()
        assert len(calls) == 1
        argv, kwargs = calls[0]
        assert argv == ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
                        "-ExecutionPolicy", "Bypass", "-File", "C:\\fixture\\host_clock.ps1",
                        "-Directory", "C:\\fixture\\output", "-Session", "policy-regression"]
        assert kwargs == dict(stdin=subprocess.DEVNULL, stdout=observer.log, stderr=subprocess.STDOUT)
    print(json.dumps(dict(test="process_scoped_policy_launch", status="PASS", windows_executed=False)))


if __name__ == "__main__":
    main()
