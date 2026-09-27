"""Resume the qualified profile snapshot in a separate directory; preserve original."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DEFAULT = Path.home() / 'conway99_workspace/ryzen_lambda_profile_100_20260927'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_files(root, entries):
    for name, expected in entries.items():
        if sha(root / name) != expected:
            raise RuntimeError('Recovery hash mismatch: ' + name)


def check_bundle():
    verify_files(HERE, json.loads((HERE / 'MANIFEST.json').read_text()))


def cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def prepare(source, destination):
    from audit import audit
    entries = json.loads((HERE / 'INPUTS.json').read_text())
    verify_files(source, entries)
    report, _ = audit(source)
    if destination.exists():
        raise FileExistsError('Recovery directory already exists: ' + str(destination))
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns('__pycache__', 'controller.lock'))
    verify_files(destination, entries)
    code = destination / 'recovery'
    shutil.copytree(HERE, code, ignore=shutil.ignore_patterns('__pycache__'))
    (destination / 'RESULT.json').rename(destination / 'PRE_RECOVERY_RESULT.json')
    ledger = json.loads((destination / 'ledger.json').read_text())
    # Reserve setup/launch CPU, retaining every previous charge and wall second.
    ledger['used']['aux'] += 30
    ledger['cli_reservations'].append({'action': 'recovery_prepare_launch', 'reserved_cpu': 30,
                                       'measured_before_spawn': cpu()})
    if cpu() > 29 or ledger['used']['aux'] >= 7170:
        raise RuntimeError('Recovery setup budget exceeded; do not launch')
    (destination / 'ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
    (destination / 'RECOVERY.json').write_text(json.dumps({'source': str(source),
        'input_archive_sha256': '8a95e0a04416dd15acf620b7f54e5ea4389434ce0031fe2b266c700bd8b0d7fb',
        'qualified_snapshot': report, 'version': '1.0.1', 'original_program_unchanged': True,
        'recovery_manifest_sha256': sha(code / 'MANIFEST.json')}, indent=2) + '\n')
    (destination / 'status.json').write_text('{"status":"RECOVERY_PREPARED"}\n')
    verify_files(source, entries)
    return code


def main():
    check_bundle()
    if len(sys.argv) == 3 and sys.argv[1] == '--run':
        destination = Path(sys.argv[2]).resolve()
        if HERE != destination / 'recovery':
            raise RuntimeError('Recovery must run from its frozen copy')
        stream = (destination / 'controller.lock').open('a+')
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.path.insert(0, str(destination / 'program/experiments/memetik/lambda_profile_1_0_0'))
        import run as original
        original.verify_run(destination)
        import campaign_fixed
        campaign_fixed.campaign(destination)
        return
    if len(sys.argv) != 1:
        raise SystemExit('Run without arguments in Ryzen WSL')
    if 'WSL_DISTRO_NAME' not in os.environ or not shutil.which('powershell.exe'):
        raise RuntimeError('Ryzen WSL with Windows host clock required')
    source = DEFAULT.resolve()
    stream = (source / 'controller.lock').open('a+')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    sys.path.insert(0, str(source / 'program/experiments/memetik/lambda_profile_1_0_0'))
    import run as original
    original.verify_run(source)
    destination = source.with_name(source.name + '_recovery_101')
    code = prepare(source, destination)
    with (destination / 'controller.log').open('ab') as log:
        proc = subprocess.Popen([sys.executable, str(code / 'start.py'), '--run', str(destination)],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True, env={**os.environ, 'PYTHONNOUSERSITE': '1'})
    from runtime import process
    (destination / 'launcher.json').write_text(json.dumps({'pid': proc.pid,
        'start_ticks': process(proc.pid)['start_ticks']}) + '\n')
    print('PROFILE_RECOVERY_LAUNCHED ' + json.dumps({'directory': str(destination), 'pid': proc.pid,
        'log': str(destination / 'controller.log'), 'retained_episodes': 5099,
        'budgets': 'unchanged; previous CPU and host wall time retained'}), flush=True)


if __name__ == '__main__':
    main()
