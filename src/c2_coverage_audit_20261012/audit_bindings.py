"""Audit historical formula/receipt bindings. No proof replay. Run without -O."""
import hashlib
import itertools
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.file_digest(Path(path).open('rb'), 'sha256').hexdigest()


def main(root):
    root = Path(root).resolve()
    inputs = root / 'c2_coverage_inputs'
    mapping = json.loads((root / 'c2_filter_work/variables.json').read_text())
    labels = {tuple(x): i for i, x in enumerate(mapping['labels'])}
    primary = {(b, i, j): v for v, b, i, j in mapping['primary_variables']}
    arcs = []
    for p, q in itertools.permutations(range(7), 2):
        x = labels[tuple(sorted((2 * p, 2 * q)))]
        y = labels[tuple(sorted((2 * p, 2 * q + 1)))]
        i, j = sorted((x % 42, y % 42))
        arcs.append(primary['B' if x // 42 == y // 42 else 'C', i, j])
    positions = {v: k for k, v in enumerate(arcs)}
    base = root / 'c2_filter_work/profile_346.cnf'
    assert sha(base) == '33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030'
    header, body = base.read_bytes().split(b'\n', 1)
    _, _, variables, clauses = header.split()
    prefixes = {}
    records = []

    def locate(path):
        suffix = path.split('/conway99_workspace/', 1)[1]
        project, relative = suffix.split('/', 1)
        if project.startswith('Conway99_C2_Profile346Pilot_'):
            return inputs / 'pilot' / relative
        if project.startswith('Conway99_C2_Generalize_'):
            return inputs / 'generalize' / relative
        if project.startswith('Conway99_C2_One3Cert_'):
            return inputs / 'one3' / relative
        tag = 'g2' if project.startswith('Conway99_C2_Generalize2_') else 'two3'
        assert project.startswith(('Conway99_C2_Generalize2_', 'Conway99_C2_Two3Cert_')), project
        return inputs / 'handoff' / (tag + '__' + relative.replace('/', '__'))

    def check(ident, item):
        units = item['units']
        assert len(set(units)) == len(units)
        assert all(abs(v) in positions and -v not in units for v in units)
        if len(units) not in prefixes:
            prefixes[len(units)] = hashlib.sha256(b'p cnf %d %d\n' % (int(variables), int(clauses) + len(units)) + body)
        digest = prefixes[len(units)].copy()
        digest.update(''.join('%d 0\n' % v for v in units).encode())
        assert digest.hexdigest() == item['formula_sha256'], ident
        assert item['status'] in ('CERTIFIED', 'UNSAT_VERIFIED'), ident
        for key, rc, marker in [('solve', 20, 's UNSATISFIABLE'), ('checker', 0, 's VERIFIED')]:
            row = item[key]
            assert row['returncode'] == rc and row['reason'] is None
            log = locate(row['log'])
            assert sha(log) == row['log_sha256'], str(log)
            assert marker in log.read_text().splitlines()
            result = log.with_name(log.name.replace('output.log', 'result.json'))
            assert json.loads(result.read_text()) == row
        assert item['solve']['command'][-2:] == item['checker']['command'][-2:]
        formula, proof = item['checker']['command'][-2:]
        assert item['solve']['outputs'] == {proof: item['proof_sha256']}
        assert item['proof_archive']['uncompressed_sha256'] == item['proof_sha256']
        assert item['proof_archive']['file'] == proof + '.gz'
        pos = sum(1 << positions[v] for v in units if v > 0)
        neg = sum(1 << positions[-v] for v in units if v < 0)
        if 'code' in item:
            assert len(units) == 42 and pos == item['code'] and neg == ((1 << 42) - 1) ^ pos
        records.append({'id': ident, 'positive_mask': pos, 'negative_mask': neg,
                        'formula_sha256': item['formula_sha256'], 'proof_sha256': item['proof_sha256'],
                        'proof_archive': item['proof_archive'], 'checker_log_sha256': item['checker']['log_sha256']})

    groups = {}
    for name, path in [('one3', inputs / 'one3/work/certify/certificates.json'),
                       ('two3', inputs / 'handoff/two3__work__certify__certificates.json')]:
        cases = json.loads(path.read_text())['cases']
        for ident, item in cases.items():
            check(name + '/' + ident, item)
        groups[name] = len(cases)
    states = {name: json.loads(path.read_text())['trials'] for name, path in [
        ('generalize', inputs / 'generalize/work/search/state.json'),
        ('generalize2', inputs / 'handoff/g2__work__search__state.json')]}
    for name, trials in states.items():
        before = len(records)
        for ident, item in trials.items():
            if item['status'] == 'CERTIFIED':
                check(name + '/' + ident, item)
        groups[name] = len(records) - before
    pilot = json.loads((inputs / 'pilot/work/pilot/pilot.json').read_text())['cases']
    before = len(records)
    for ident, item in pilot.items():
        if item['status'] == 'UNSAT_VERIFIED':
            check('pilot/' + ident, item)
    groups['pilot'] = len(records) - before
    bound = {(r['positive_mask'], r['negative_mask']) for r in records}
    patterns = {}
    for name, path in [('generalize', inputs / 'generalize/work/coverage/lemmas.json'),
                       ('generalize2', inputs / 'handoff/g2__work__coverage__lemmas.json')]:
        rows = json.loads(path.read_text())
        pattern_file = path.with_name(path.name.replace('lemmas.json', 'patterns.txt'))
        assert [tuple(map(int, line.split())) for line in pattern_file.read_text().splitlines()] == [(row['positive_mask'], row['negative_mask']) for row in rows]
        unbound = []
        for row in rows:
            pos = sum(1 << positions[v] for v in row['units'] if v > 0)
            neg = sum(1 << positions[-v] for v in row['units'] if v < 0)
            assert (pos, neg) == (row['positive_mask'], row['negative_mask'])
            assert row['clause'] == [-v for v in row['units']]
            if (pos, neg) not in bound:
                unbound.append(row['id'])
        patterns[name] = {'total': len(rows), 'unbound_here': unbound}
    assert all(not row['unbound_here'] for row in patterns.values())
    out = root / 'c2_publication_git/results/c2_coverage_audit_20261012'
    (out / 'certificate_bindings.json').write_text(json.dumps(records, indent=2) + '\n')
    report = {'status': 'PASS_WITH_EXPLICIT_LIMITS', 'groups': groups, 'patterns': patterns,
              'base_sha256': sha(base), 'bindings_sha256': sha(out / 'certificate_bindings.json'),
              'limits': ['No proof bytes read and no checker replay.', 'Historical UNSAT verdicts are inherited; formula and receipt bindings freshly checked.']}
    (out / 'binding_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
