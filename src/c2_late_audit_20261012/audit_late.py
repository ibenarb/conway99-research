"""Bind four historical UNSAT receipts and recompute exact late complements.

No proof bytes read, no solver/checker executed. Python assertions required.
Usage: python3 audit_late.py WORKSPACE
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main(workspace):
    root = Path(workspace).resolve()
    repo = root / 'c2_publication_git'
    source = root / 'c2_late_inputs'
    work = root / 'c2_late_work'
    work.mkdir(exist_ok=True)
    output = repo / 'results/c2_late_audit_20261012'
    vendor = repo / 'vendor/c2_late_audit_20261012'
    module_path = vendor / 'independent_coverage.py'
    spec = importlib.util.spec_from_file_location('independent', module_path)
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    variables = independent.arc_variables(read(root / 'c2_filter_work/variables.json'))
    assert sha(root / 'c2_filter_work/variables.json') == 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'
    pairs = [(a, b) for a in range(7) for b in range(7) if a != b]
    positions = {v: pairs.index(pair) for v, pair in variables.items()}
    base = root / 'c2_filter_work/profile_346.cnf'
    assert sha(base) == '33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030'
    header, body = base.read_bytes().split(b'\n', 1)
    _, _, nvars, nclauses = header.split()
    candidates = read(source / 'continuation/inputs/priority_candidates.json')['candidates']
    sources = [source / 'ryzen/work/case/certificate.json',
               source / 'ab/work/certificates/seed_042_step_44.json',
               source / 'ab/work/certificates/seed_172_step_49.json',
               source / 'c/work/certificates/seed_172_step_47.json']
    certificates = [read(p) for p in sources]
    groups = ['ryzen', 'ab', 'ab', 'c']
    binding = []

    def local(path, group):
        return source / group / path.split('/conway99_workspace/', 1)[1].split('/', 1)[1]

    def receipt(row, group, rc, marker):
        assert row['returncode'] == rc and row['reason'] is None
        if isinstance(row['log'], str):
            path, digest = row['log'], row['log_sha256']
        else:
            path, digest = row['log']['path'], row['log']['sha256']
        log = local(path, group)
        assert sha(log) == digest and marker in log.read_text().splitlines()
        assert read(log.with_name('result.json')) == row
        return digest

    for candidate, item, group, path in zip(candidates, certificates, groups, sources):
        units = item['units']
        assert units == candidate['units'] and item['candidate'] == candidate['id']
        assert item['status'] == 'UNSAT_VERIFIED'
        assert len(units) == len(set(units)) == 9
        assert all(abs(v) in variables and -v not in units for v in units)
        formula_bytes = b'p cnf %d %d\n' % (int(nvars), int(nclauses) + len(units)) + body + ''.join('%d 0\n' % v for v in units).encode()
        digest = hashlib.sha256(formula_bytes).hexdigest()
        assert digest == candidate['formula_sha256']
        solve_hash = receipt(item['solver'], group, 20, 's UNSATISFIABLE')
        if group == 'ryzen':
            assert digest == item['formula_sha256'] and item['profile_sha256'] == sha(base)
            formula, proof = item['solver']['command'][-2:]
            assert item['checker']['command'][1:3] == [formula, proof]
            assert item['proof']['path'] == proof
            checked_proof = item['proof']
            checker_hash = receipt(item['checker'], group, 0, 's VERIFIED')
        else:
            formula = item['formula']
            assert formula['sha256'] == digest and formula['bytes'] == len(formula_bytes)
            assert item['solver']['inputs'] == [formula]
            assert item['solver']['outputs'] == [item['proof']]
            assert item['solver']['command'][-2:] == [formula['path'], item['proof']['path']]
            trim, cake = item['checks']
            assert trim['inputs'] == [formula, item['proof']] and trim['outputs'] == [item['checked_proof']]
            assert cake['inputs'] == [formula, item['checked_proof']]
            assert trim['command'][-3:] == [formula['path'], item['proof']['path'], item['checked_proof']['path']]
            assert cake['command'][-2:] == [formula['path'], item['checked_proof']['path']]
            receipt(trim, group, 20, 's VERIFIED')
            checker_hash = receipt(cake, group, 0, 's VERIFIED UNSAT')
            assert sha(source / group / 'work/toolchain.json') == item['toolchain_sha256']
            checked_proof = item['checked_proof']
        positive = sum(1 << positions[v] for v in units if v > 0)
        negative = sum(1 << positions[-v] for v in units if v < 0)
        binding.append({'id': candidate['id'], 'units': units, 'positive_mask': positive, 'negative_mask': negative,
                        'formula_sha256': digest, 'certificate_sha256': sha(path), 'checked_proof': checked_proof,
                        'solver_log_sha256': solve_hash, 'checker_log_sha256': checker_hash})
    print('FOUR_FORMULA_RECEIPT_BINDINGS_PASS', flush=True)
    source_list = root / 'c2_coverage_inputs/handoff/remaining_234691.tsv'
    assert sha(source_list) == '3c4155233a8969ecbaa8dec288491aced9034b9af6ea606971f5c6c74c0074fb'
    lines, codes = independent.population(source_list)
    references = [source / 'continuation/inputs/remaining_6651.tsv', source / 'ab/work/remaining_after_1.tsv',
                  source / 'ab/work/remaining_after_2.tsv', source / 'c/work/remaining_after_C_218.tsv']
    expected_remaining = [6651, 3360, 406, 218]
    reports = []
    binary = work / 'coverage'
    subprocess.run(['g++', '-O3', '-std=c++17', str(repo / 'vendor/c2_coverage_audit_20261012/coverage.cpp'), '-o', str(binary)], check=True)
    current = source_list
    for row, reference, expected in zip([binding[i] for i in (0, 2, 1, 3)], references, expected_remaining):
        covered = independent.cover(codes, row['units'], variables)
        wanted = lines[0] + b''.join(line for line, code in zip(lines[1:], codes) if code not in covered)
        assert wanted == reference.read_bytes()
        pattern = work / 'pattern.txt'
        pattern.write_text('%d %d\n' % (row['positive_mask'], row['negative_mask']))
        remaining = work / (row['id'] + '_remaining.tsv')
        run = subprocess.run([str(binary), '7', str(pattern), str(current), str(remaining)], check=True, capture_output=True, text=True)
        cpp = json.loads(run.stdout)
        assert remaining.read_bytes() == wanted
        assert cpp['total'] == len(codes) and cpp['covered'] == len(covered) and cpp['remaining'] == expected
        assert cpp['hits'] == [len(covered)]
        reports.append({'id': row['id'], **cpp, 'remaining_sha256': sha(remaining), 'both_algorithms_byte_identical': True})
        current = remaining
        lines, codes = independent.population(current)
        print('EXACT_COMPLEMENT_PASS', row['id'], expected, flush=True)
    assert current.read_bytes() == (repo / 'vendor/c2_completeness_20261012/rest218/inputs/remaining_218.tsv').read_bytes()
    assert references[0].read_bytes() == (source / 'ryzen/work/remaining_after_certificate.tsv').read_bytes()
    assert references[2].read_bytes() == (source / 'c/inputs/remaining_406.tsv').read_bytes()
    assert certificates[3] == read(source / 'installer/payload/evidence/C_certificate.json')
    rest_audit = read(repo / 'results/c2_completeness_20261012/rest218_abschlussaudit.json')
    assert {r['code'] for r in rest_audit['records']} == set(codes)
    assert len(rest_audit['records']) == rest_audit['total'] == rest_audit['covered'] == 218
    assert rest_audit['base_sha256'] == sha(base) and rest_audit['rest_list_sha256'] == sha(current)
    # Independently reconstruct all endpoint formulas before inheriting closure verdicts.
    prefix = hashlib.sha256(b'p cnf %d %d\n' % (int(nvars), int(nclauses) + 42) + body)
    arc_by_bit = {positions[v]: v for v in variables}
    for record in rest_audit['records']:
        digest = prefix.copy()
        digest.update(''.join('%d 0\n' % (arc_by_bit[k] if record['code'] >> k & 1 else -arc_by_bit[k]) for k in range(42)).encode())
        assert digest.hexdigest() == record['formula_sha256']
    report = {'status': 'PASS_WITH_INHERITED_PROOF_VERDICTS', 'bindings': binding, 'coverage': reports,
              'endpoint': {'cases': 218, 'all_formula_hashes_reconstructed': True, 'exact_match_to_existing_closure_audit': True, 'closure_audit_sha256': sha(repo / 'results/c2_completeness_20261012/rest218_abschlussaudit.json')},
              'limits': ['No SAT or proof-checker executions; historical success verdicts inherited.', 'External proof files not read.', 'Rest218 audit retained with its original metadata/formula-reconstruction limits.', 'No exclusion of low degrees 0,1,2.']}
    (output / 'late_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print('LATE_AUDIT_PASS', flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
