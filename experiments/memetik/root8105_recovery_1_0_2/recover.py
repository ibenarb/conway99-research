"""ROOT8105 1.0.1 recovery: immutable old sources, explicit fixed budget extension."""
import argparse
import fcntl
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(package, directory):
    checksums = json.loads((HERE / 'SHA256.json').read_text())
    for name, expected in checksums.items():
        if sha(HERE / name) != expected:
            raise ValueError('Recovery package hash mismatch: ' + name)
    baseline = json.loads((HERE / 'baseline.json').read_text())
    for name in ('manifest.json', 'preflight.json'):
        if sha(directory / name) != baseline['sha256'][name]:
            raise ValueError('Original input/gate changed: ' + name)
    if (directory / 'session_open.json').exists():
        raise ValueError('Unclosed session: do not remove marker; audit required')
    with (directory / 'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    sys.path.insert(0, str(package))
    campaign = importlib.import_module('recovery_campaign')
    campaign.BASE = package
    if campaign.code_fingerprint() != baseline['old_code_fingerprint']:
        raise ValueError('Original 1.0.1 sources changed')
    manifest = json.loads((directory / 'manifest.json').read_text())
    for name, expected in manifest['job_sha256'].items():
        if sha(directory / 'jobs' / (name + '.json')) != expected:
            raise ValueError('Original job changed: ' + name)
    receipts = json.loads((directory / 'receipts.json').read_text())
    if hashlib.sha256(json.dumps(receipts[:251], sort_keys=True, separators=(',', ':')).encode()).hexdigest() != baseline['receipt_prefix_sha256']:
        raise ValueError('Original receipts differ from audited diagnosis')
    auxiliary = json.loads((directory / 'aux_ledger.json').read_text())['cpu_s']
    if not math.isfinite(auxiliary) or auxiliary < baseline['aux_cpu_s']:
        raise ValueError('Auxiliary accounting regressed')
    allowed = set(manifest['jobs']) | {n + '_proof' + str(i) for n in manifest['jobs'] for i in range(2)}
    for receipt in receipts:
        if receipt['job'] not in allowed or not math.isfinite(receipt['cpu_s']) or receipt['cpu_s'] < 0:
            raise ValueError('Invalid receipt')
    candidates = 0
    for receipt in receipts[:251]:
        name = receipt['job']
        state = json.loads((directory / 'work' / name / 'checkpoint.json').read_text())
        result = json.loads((directory / 'work' / name / 'worker_result.json').read_text())
        if result['status'] != 'CPU_LIMIT_UNKNOWN' or state['max_depth'] != receipt['max_depth']:
            raise ValueError('Checkpoint/result mismatch: ' + name)
        for artifact in state.get('proof_candidates', []):
            path = Path(artifact).resolve()
            if not path.is_relative_to((directory / 'work' / name / 'enumerations').resolve()):
                raise ValueError('Proof artifact outside its job')
            for filename in ('enumeration.json', 'rows.txt', 'state.json'):
                if not (path / filename).is_file():
                    raise ValueError('Missing proof input: ' + str(path / filename))
            candidates += 1
    used = sum(r['cpu_s'] for r in receipts) + auxiliary
    summary = {'status': 'RECOVERY_CHECK_PASS', 'original_receipts_preserved': 251,
               'all_receipts': len(receipts), 'original_missing_jobs': baseline['missing_jobs'],
               'old_cpu_accounting_s': used, 'original_proof_candidates': candidates,
               'proposed_additional_cpu_h': 16, 'proposed_total_cpu_h': 286,
               'remaining_under_proposed_cap_s': baseline['new_campaign_cpu_s'] - used,
               'search_and_proof_sources': 'original verified 1.0.1, unchanged'}
    return campaign, baseline, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--package', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--run', action='store_true')
    parser.add_argument('--authorize-additional-cpu-hours', type=int)
    args = parser.parse_args()
    directory, package = args.directory.resolve(), args.package.resolve()
    campaign, baseline, summary = check(package, directory)
    print(json.dumps(summary, indent=2), flush=True)
    if args.check:
        return
    if args.authorize_additional_cpu_hours != 16:
        raise ValueError('Explicit --authorize-additional-cpu-hours 16 required; no work started')
    # Keep the authorization fixed across pauses/resumes; never add another 16 hours.
    authorization = directory / 'recovery_102_authorization.json'
    record = {'version': '1.0.2', 'original_campaign_cpu_s': baseline['old_campaign_cpu_s'],
              'additional_cpu_s': baseline['additional_cpu_s'], 'total_campaign_cpu_s': baseline['new_campaign_cpu_s'],
              'recovery_checksums_sha256': sha(HERE / 'SHA256.json'),
              'original_manifest_sha256': baseline['sha256']['manifest.json']}
    if authorization.exists() and json.loads(authorization.read_text()) != record:
        raise ValueError('Existing recovery authorization differs')
    # Exclusive controller lock also protects initial evidence backup/authorization.
    with (directory / 'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        backup = directory / 'before_recovery_102'
        backup.mkdir(exist_ok=True)
        for name in ('manifest.json', 'preflight.json', 'receipts.json', 'aux_ledger.json', 'status.json'):
            target = backup / name
            if not target.exists():
                with target.open('xb') as stream:
                    stream.write((directory / name).read_bytes())
        campaign.atomic(authorization, record)
    campaign.run(directory, additional_cpu_s=baseline['additional_cpu_s'])


if __name__ == '__main__':
    main()
