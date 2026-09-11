"""Self-contained Office delivery entrypoint (also used as the zipapp main).

Installs only the required binary Python packages, validates the complete
implementation, checks/stages the reviewed new paths, commits and pushes the
separate branch, then starts or resumes the autonomous pilot. A failed gate
prevents all subsequent stages. No certified historical file is overwritten.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

BASE = "d53ce5b373641868404d9200b43a083c8f632d64"
BRANCH = "memetic/office-v0.2.0-multinorm-20260911"
VERSION = "0.2.0"
REQUIREMENTS = ("ortools==9.15.6755", "pynauty==2.8.8.1")
GENERATED = ("results/memetic_v2/office_validation_0.2.0.json", "manifests/memetic_v2/office_environment_0.2.0.json")
PREFIXES = ("src/memetic_v2/", "configs/memetic_v2/", "docs/memetic_v2/", "data/memetic_v2/", "results/memetic_v2/", "manifests/memetic_v2/")


def execute(arguments, cwd=None, logfile=None, capture=False):
    if capture:
        return subprocess.run(arguments, cwd=cwd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=True).stdout.rstrip("\n")
    if logfile:
        with Path(logfile).open("a") as log:
            log.write("COMMAND " + repr(arguments) + "\n")
            log.flush()
            result = subprocess.run(arguments, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(f"Command failed with code {result.returncode}; see {logfile}")
        return ""
    subprocess.run(arguments, cwd=cwd, check=True)
    return ""


def git(repository, *arguments, logfile=None):
    return execute(["git", "-C", str(repository), *arguments], capture=logfile is None, logfile=logfile)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as handle:
        json.dump(value, handle, indent=4)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_payload(archive):
    with zipfile.ZipFile(archive) as bundle:
        manifest = json.loads(bundle.read("package_manifest.json"))
        if manifest["version"] != VERSION or manifest["base_commit"] != BASE or manifest["branch"] != BRANCH:
            raise RuntimeError("Wrong deployment manifest")
        payload = {}
        for name, expected in manifest["files"].items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts or not name.startswith(PREFIXES):
                raise RuntimeError("Unexpected package path: " + name)
            content = bundle.read("payload/" + name)
            if sha(content) != expected:
                raise RuntimeError("Package checksum mismatch: " + name)
            payload[name] = content
    return manifest, payload


def install_payload(repository, payload, accepted_previous=None):
    accepted_previous = accepted_previous or {}
    branch = git(repository, "branch", "--show-current")
    status = git(repository, "status", "--porcelain", "--untracked-files=all")
    if branch != BRANCH:
        if status:
            raise RuntimeError("Repository contains unrelated changes; installation stopped")
        if git(repository, "rev-parse", "HEAD") != BASE:
            raise RuntimeError("Repository is not at the agreed base commit")
        existing = git(repository, "branch", "--list", BRANCH)
        if existing:
            git(repository, "switch", BRANCH)
        else:
            git(repository, "switch", "-c", BRANCH, BASE)
    status = git(repository, "status", "--porcelain", "--untracked-files=all")
    for line in status.splitlines():
        path = line[3:]
        if path not in payload and path not in GENERATED:
            raise RuntimeError("Unrelated pending change: " + path)
    replacing = []
    for name, content in payload.items():
        target = repository / name
        if target.exists() and target.read_bytes() != content:
            if sha(target.read_bytes()) != accepted_previous.get(name):
                raise RuntimeError("Existing file differs from this release: " + name)
            replacing.append(name)
    if replacing:
        run_root = repository.parent / "conway99_memetic_office_0.2.0/runs"
        if any(run_root.glob("*/checkpoints/checkpoint.*.json.gz")):
            raise RuntimeError("Existing pilot checkpoints require explicit version migration")
        print("Ersetze exakt erkannte Dateien der fehlgeschlagenen Erstversion:", len(replacing), flush=True)
    for name, content in payload.items():
        target = repository / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    historical = git(repository, "diff", "--name-only", BASE, "--")
    if any(name and name not in payload and name not in GENERATED for name in historical.splitlines()):
        raise RuntimeError("Branch contains changes outside the reviewed new files")


def make_environment(experiment, logfile):
    environment = experiment.parent / "conway99_memetic_office_0.1.0/environment"
    python = environment / "bin/python"
    complete_environment = python.exists()
    if not complete_environment:
        raise RuntimeError("Expected the previously validated Office Python environment")
    if complete_environment:
        check = subprocess.run([str(python), "-m", "pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        complete_environment = check.returncode == 0
    if not complete_environment:
        command = [sys.executable, "-m", "venv", str(environment)]
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if completed.returncode:
            if "ensurepip" not in completed.stdout and "venv" not in completed.stdout:
                raise RuntimeError(completed.stdout)
            print("Python-Venv-Paket fehlt; es wird ausschließlich python3-venv benötigt.", flush=True)
            execute(["sudo", "apt-get", "install", "-y", "python3-venv"])
            execute(command, logfile=logfile)
    probe = "import importlib.metadata as m,json; print(json.dumps({n:m.version(n) for n in ['ortools','pynauty']}))"
    ready = False
    try:
        installed = json.loads(execute([str(python), "-c", probe], capture=True))
        ready = installed == {"ortools": "9.15.6755", "pynauty": "2.8.8.1"}
    except subprocess.CalledProcessError:
        pass
    if not ready:
        raise RuntimeError("Existing Python dependency versions differ; historical environment will not be modified")
    freeze = execute([str(python), "-m", "pip", "freeze", "--all"], capture=True)
    (experiment / "audits/dependencies.freeze.txt").write_text(freeze + "\n")
    return python, sha(freeze.encode())


def validate_and_publish(repository, experiment, python, manifest, dependencies, logfile, publish):
    identity = sha(json.dumps(manifest, sort_keys=True).encode() + dependencies.encode())
    stamp = experiment / "audits/validated_release.json"
    report_path = experiment / "audits/full_validation.json"
    verified = False
    if stamp.exists() and report_path.exists():
        previous = json.loads(stamp.read_text())
        report = json.loads(report_path.read_text())
        verified = previous.get("identity") == identity and report.get("scope") == "FULL" and report.get("status") == "PASS"
    if not verified:
        print("Prüfe Mathematik, Isomorphie, Crossover und echte Unterbrechung/Wiederaufnahme.", flush=True)
        execute([str(python), str(repository / "src/memetic_v2/controls.py"), "--full", "--output", str(report_path)], logfile=logfile)
        report = json.loads(report_path.read_text())
        if report.get("scope") != "FULL" or report.get("status") != "PASS":
            raise RuntimeError("Full validation did not pass")
        atomic_json(stamp, {"identity": identity, "version": VERSION,
                           "report_sha256": sha(report_path.read_bytes()), "validated_at": time.time()})
    else:
        print("Unveränderte Version: vorhandene vollständige Validierung wird wiederverwendet.", flush=True)
    audit_target = repository / GENERATED[0]
    audit_target.parent.mkdir(parents=True, exist_ok=True)
    audit_target.write_bytes(report_path.read_bytes())
    environment_target = repository / GENERATED[1]
    environment_target.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(environment_target, {"version": VERSION, "base_commit": BASE, "package_identity": identity,
                "dependency_freeze": (experiment / "audits/dependencies.freeze.txt").read_text(),
                "full_validation_sha256": sha(report_path.read_bytes())})
    # Status and the complete staged diff are retained for the local audit.
    changed = git(repository, "status", "--porcelain", "--untracked-files=all")
    allowed = set(manifest["files"]) | set(GENERATED)
    if any(line[3:] not in allowed for line in changed.splitlines()):
        raise RuntimeError("Unexpected repository changes before commit")
    if changed:
        git(repository, "add", "--", *sorted(allowed))
        git(repository, "diff", "--cached", "--check")
        staged = git(repository, "diff", "--cached", "--name-only")
        if any(path not in allowed for path in staged.splitlines()):
            raise RuntimeError("Staged changes outside release scope")
        status = git(repository, "status", "--short")
        diff = git(repository, "diff", "--cached", "--no-ext-diff")
        (experiment / "audits/precommit_status.txt").write_text(status + "\n")
        (experiment / "audits/precommit_diff.txt").write_text(diff + "\n")
        if diff:
            print("Vollständige lokale Validierung bestanden; committe den separaten Branch.", flush=True)
            git(repository, "commit", "-m", "Add validated Office memetic pilot v0.2.0", logfile=logfile)
    if git(repository, "status", "--porcelain"):
        raise RuntimeError("Working tree is not clean after commit")
    commit = git(repository, "rev-parse", "HEAD")
    if publish:
        git(repository, "push", "-u", "origin", BRANCH, logfile=logfile)
    atomic_json(experiment / "audits/deployment.json", {"commit": commit, "branch": BRANCH,
                "base_commit": BASE, "full_validation": str(report_path), "pushed": publish})
    return commit


def launch(repository, experiment, python):
    run = experiment / "runs/pilot-001"
    run.mkdir(parents=True, exist_ok=True)
    # flock is the final authority. The launcher probes the same file so
    # repeating the command cannot create an additional coordinator.
    import fcntl
    with (run / "run.lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("RUNNING", run, flush=True)
            return
        fcntl.flock(lock, fcntl.LOCK_UN)
    console = run / "console.log"
    with console.open("ab") as output:
        process = subprocess.Popen([str(python), str(repository / "src/memetic_v2/runner.py"),
                                    "--run-dir", str(run)], stdin=subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True, cwd=repository)
    time.sleep(1)
    if process.poll() is not None and process.returncode != 0:
        raise RuntimeError("Runner start failed; see " + str(console))
    print("PILOT_STARTED_OR_RESUMED", "PID", process.pid, flush=True)
    print("RUN_DIRECTORY", run, flush=True)
    print("STATUS_FILE", run / "status.json", flush=True)
    print("CONSOLE_LOG", console, flush=True)
    print("Status alle zehn Minuten; nach Windows-Neustart denselben Aufruf wiederholen.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true", help="Install/validate, but do not start pilot")
    parser.add_argument("--no-push", action="store_true", help="Keep validated commit local")
    parser.add_argument("--no-follow", action="store_true", help="Start without keeping the status display open")
    args = parser.parse_args()
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"
    workspace = Path.home() / "conway99_workspace"
    repository = workspace / "conway99-research"
    experiment = workspace / "conway99_memetic_office_0.2.0"
    if not (repository / ".git").exists():
        raise RuntimeError("Expected prepared repository at " + str(repository))
    manifest, payload = load_payload(Path(sys.argv[0]).resolve())
    experiment.mkdir(exist_ok=True)
    (experiment / "audits").mkdir(exist_ok=True)
    logfile = experiment / "audits/setup.log"
    print("RELEASE", VERSION, "BRANCH", BRANCH, flush=True)
    install_payload(repository, payload, manifest.get("accepted_previous_sha256"))
    python, dependencies = make_environment(experiment, logfile)
    commit = validate_and_publish(repository, experiment, python, manifest, dependencies, logfile, not args.no_push)
    print("FULL_VALIDATION_PASS", "COMMIT", commit, flush=True)
    if not args.prepare_only:
        launch(repository, experiment, python)
        if not args.no_follow:
            print("Statusanzeige geöffnet. Strg+C beendet nur die Anzeige; der Runner bleibt aktiv.", flush=True)
            try:
                subprocess.run(["tail", "-n", "40", "-F", str(experiment / "runs/pilot-001/console.log")])
            except KeyboardInterrupt:
                print("Anzeige beendet; Suchlauf bleibt aktiv.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("DEPLOYMENT_STOPPED", repr(error), file=sys.stderr, flush=True)
        print("Kein Überspringen einer fehlgeschlagenen Kontrolle. Vollständiges Protokoll: ~/conway99_workspace/conway99_memetic_office_0.2.0/audits/setup.log", file=sys.stderr, flush=True)
        sys.exit(2)
