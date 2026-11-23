"""Adversarial bookkeeping controls for the separate S3 result auditor."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import time

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[2] / 'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure


def main():
    while True:
        resource = measure()
        if max(r['system_busy_cpu'] for r in resource['intervals']) + 1 <= 20 and resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35:
            break
        time.sleep(10)
    spec = importlib.util.spec_from_file_location('low_auditor_v2', BASE / 'audit_low_evidence_v2.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    plan, planes = audit.plan()
    hashes = {name:audit.sha(BASE / name) for name in audit.SOURCE_NAMES}
    geometry = audit.load(BASE / 'geometry_own.json')
    source = BASE / 'jobs/306.0'
    before = {p.name:audit.sha(p) for p in source.iterdir() if p.is_file()}
    positive = audit.audit_one(source, plan['306.0'], hashes, geometry, planes)
    root = BASE / 'audit_controls_v2'
    root.mkdir(exist_ok=False)
    cases = []
    for name, changed_file in [('wrong_key', None), ('open', None), ('truncated_stars', 'stars.txt'),
                               ('duplicate_star', 'stars.txt'), ('missing_final', 'solver.stdout'), ('depth_cutoff', None)]:
        directory = root / name
        directory.mkdir()
        report = audit.load(source / 'result.json')
        for p in source.iterdir():
            if not p.is_file() or p.name == 'result.json':
                continue
            destination = directory / p.name
            if p.name == changed_file:
                lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
                if name in ('truncated_stars', 'missing_final'):
                    lines = lines[:-1]
                else:
                    lines[-1] = lines[0]
                destination.write_text(''.join(lines), encoding='utf-8', newline='\n')
                report['evidence_hashes'][p.name] = audit.sha(destination)
            else:
                os.link(p, destination)
        if name == 'wrong_key':
            report['chart'] += 1
        elif name == 'open':
            report['status'] = 'OPEN_NOT_EXCLUSION'
            report['open'] = 1
        elif name == 'depth_cutoff':
            report['depth_cutoff'] = True
            report['full_depth'] = 8
        (directory / 'result.json').write_text(json.dumps(report, indent=4), encoding='utf-8')
        try:
            audit.audit_one(directory, plan['306.0'], hashes, geometry, planes)
        except AssertionError as error:
            cases.append(dict(case=name, rejected=True, diagnostic=str(error),
                              changed_evidence_hash_updated=changed_file is not None))
        else:
            raise RuntimeError('Corrupt control incorrectly accepted: ' + name)
    after = {p.name:audit.sha(p) for p in source.iterdir() if p.is_file()}
    assert before == after
    result = dict(status='ONE_POSITIVE_SIX_NEGATIVE_AUDITOR_CONTROLS_PASS', positive=positive,
                  negative=cases, original_evidence_unchanged=True,
                  hardlinked_control_inputs_are_immutable=True,
                  auditor_sha256=audit.sha(BASE / 'audit_low_evidence_v2.py'), resource=resource)
    with (root / 'controls_result.json').open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=4)
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
