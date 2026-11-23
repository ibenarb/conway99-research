"""Positive and adversarial controls for the standalone S1 evidence auditor."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import os

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('s1_audit', BASE / 'audit_singleton_evidence_v1.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    rows, unary, good, bad = audit.plan()
    positives = [audit.audit_one(BASE / 'jobs' / str(cid), cid, rows[cid], unary['charts'][cid]) for cid in (0, 12, 202)]
    source = BASE / 'jobs/12'
    before = {p.name: audit.sha(p) for p in source.iterdir() if p.is_file()}
    root = BASE / args.output_dir
    root.mkdir(exist_ok=False)
    rejected = []
    cases = ['wrong_chart', 'open', 'omit_orbit_member', 'duplicate_orbit_member',
             'wrong_input_roots', 'missing_root_row', 'missing_final', 'error_stream']
    for case in cases:
        destination = root / case
        destination.mkdir()
        report = audit.load(source / 'result.json')
        setup = audit.load(source / 'setup.txt.json')
        changes = {}
        if case == 'wrong_chart':
            report['chart'] = 13
        elif case == 'open':
            report['status'] = 'OPEN_NOT_EXCLUSION'
        elif case == 'omit_orbit_member':
            setup['orbit_audit']['orbits'][0]['members'].pop()
        elif case == 'duplicate_orbit_member':
            members = setup['orbit_audit']['orbits'][0]['members']
            members[-1] = members[0]
        elif case == 'wrong_input_roots':
            raw = gzip.decompress((source / 'setup.txt.gz').read_bytes())
            lines = raw.decode('ascii').splitlines(keepends=True)
            roots = lines[1].split()
            roots[1] = roots[0]
            lines[1] = ' '.join(roots) + '\n'
            raw = ''.join(lines).encode('ascii')
            changes['setup.txt.gz'] = gzip.compress(raw, mtime=0)
            digest = hashlib.sha256(raw).hexdigest()
            setup['setup_sha256'] = digest
            report['lossless_input_archive'].update(uncompressed_bytes=len(raw), uncompressed_sha256=digest,
                archive_sha256=hashlib.sha256(changes['setup.txt.gz']).hexdigest())
        elif case in ('missing_root_row', 'missing_final'):
            lines = (source / 'solver.stdout').read_text(encoding='ascii').splitlines(keepends=True)
            lines.pop(0 if case == 'missing_root_row' else -1)
            changes['solver.stdout'] = ''.join(lines).encode('ascii')
        elif case == 'error_stream':
            changes['solver.stderr'] = b'ERROR deliberate control\n'
        if case in ('omit_orbit_member', 'duplicate_orbit_member', 'wrong_input_roots'):
            report['setup'] = setup
            changes['setup.txt.json'] = json.dumps(setup, indent=4).encode('utf-8')
        for path in source.iterdir():
            if path.name == 'result.json' or not path.is_file():
                continue
            target = destination / path.name
            if path.name in changes:
                target.write_bytes(changes[path.name])
                report['hashes'][path.name] = audit.sha(target)
            else:
                os.link(path, target)
        (destination / 'result.json').write_text(json.dumps(report, indent=4), encoding='utf-8')
        try:
            audit.audit_one(destination, 12, rows[12], unary['charts'][12])
        except AssertionError as error:
            rejected.append(dict(case=case, rejected=True, diagnostic=str(error),
                                 all_changed_file_hashes_updated=True))
        else:
            raise RuntimeError('Corrupt fixture was accepted: ' + case)
    assert before == {p.name: audit.sha(p) for p in source.iterdir() if p.is_file()}
    result = dict(status='THREE_POSITIVE_EIGHT_NEGATIVE_SINGLETON_AUDITOR_CONTROLS_PASS',
                  positive=positives, negative=rejected, originals_unchanged=True,
                  hardlinked_unchanged_inputs_are_not_independent_backups=True,
                  auditor_sha256=audit.sha(BASE / 'audit_singleton_evidence_v1.py'))
    (root / 'controls_result.json').write_text(json.dumps(result, indent=4), encoding='utf-8')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
