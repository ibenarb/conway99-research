"""Reconstruct C4/Profile46 formulas; audit all receipts and restricted census.

No SAT solver and no proof checker is executed. Inputs: extracted historical
Profile46 final export, original installer, previous Profile346 dependency file.
Python assertions must be active. The two C++ programs perform finite enumeration.
"""
import argparse
import collections
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import zipfile


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--installer', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parents[2]
    original = repo / 'vendor/c2_completeness_20261012'
    dependency = json.loads((original / 'profile346/profile46_dependency.json').read_text())
    assert sha(args.archive) == dependency['export_sha256']
    for name, expected in dependency['files'].items():
        assert sha(source / name) == expected, name
    source_hashes = {}
    for name in ('model.py', 'counter.py', 'c2_reference.py', 'anchor_profile.py'):
        assert (source / name).read_bytes() == (original / 'rest218/legacy' / name).read_bytes()
        source_hashes[name] = sha(source / name)
    sys.path.insert(0, str(source))
    import model
    import anchor_profile as ap
    model.build_base(work)
    ap.build(work / 'base.cnf', work / 'profile_46.cnf', profile=[4, 6])
    ap.build(work / 'base.cnf', work / 'profile_346.cnf', profile=[3, 4, 6])
    assert sha(work / 'profile_46.cnf') == '5b251b4832904a3bd2ce7d804508e380794444f19c70ba8b26903cb1b4b02859'
    assert sha(work / 'profile_346.cnf') == '33fc424d5e0ce00179a5abbde52c56b40e4e1fcbc272c36d595ef29354e3b030'
    # Derive primary arc numbers independently from the emitted mapping.
    mapping = json.loads((work / 'variables.json').read_text())
    labels = {tuple(x): i for i, x in enumerate(mapping['labels'])}
    primaries = {(b, i, j): v for v, b, i, j in mapping['primary_variables']}
    arcs = {}
    for p, q in itertools.permutations(range(7), 2):
        x = labels[tuple(sorted((2 * p, 2 * q)))]
        y = labels[tuple(sorted((2 * p, 2 * q + 1)))]
        i, j = sorted((x % 42, y % 42))
        arcs[p, q] = primaries['B' if x // 42 == y // 42 else 'C', i, j]
    assert len(set(arcs.values())) == 42 and arcs == ap.arcs(ap.frame(14))
    truth_checks = 0
    for allowed in ({4, 6}, {3, 4, 6}):
        for p in range(7):
            variables = [arcs[p, q] for q in range(7) if q != p]
            clauses = ap.profile_clauses(sorted(variables), allowed)
            for mask in range(64):
                values = {v: bool(mask & (1 << i)) for i, v in enumerate(variables)}
                holds = all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)
                assert holds == (mask.bit_count() in allowed)
                truth_checks += 1
    base_cycle = {(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3)}
    units = [[arcs[e]] for e in sorted(base_cycle)]
    c4_hash = model.augment(work / 'base.cnf', work / 'bi_c4.cnf', model.header_variables(work / 'base.cnf'), units)
    c4 = json.loads((source / 'work/c4_certificate.json').read_text())
    assert c4_hash == c4['formula_sha256'] and units == c4['units']
    transformed = {tuple(sorted(-arcs[g[a], g[b]] for a, b in base_cycle)) for g in itertools.permutations(range(7))}
    coverage = json.loads((source / 'work/coverage.json').read_text())
    supplied = coverage['c4_transport']
    assert len(transformed) == len(supplied) == 105
    assert transformed == {tuple(w['clause']) for w in supplied}
    for witness in supplied:
        g = witness['class_permutation']
        assert sorted(g) == list(range(7))
        assert tuple(sorted(-arcs[g[a], g[b]] for a, b in base_cycle)) == tuple(witness['clause'])

    def receipt(row, expected_id, expected_rc, verdict):
        assert row['id'] == expected_id and row['returncode'] == expected_rc and row['reason'] is None
        relative = row['log'].split('/Conway99_C2_Profile46Cert_1.0.0/', 1)[1]
        log = source / relative
        assert sha(log) == row['log_sha256']
        assert verdict in log.read_text().splitlines()
        assert json.loads(log.with_name('result.json').read_text()) == row
        return row['log_sha256']

    receipt(c4['checker'], 'c4_lemma_check', 0, 's VERIFIED')
    assert c4['checker']['command'][1:] == [
        '/home/rb/conway99_workspace/Conway99_C2_Profile46Cert_1.0.0/work/bi_c4.cnf',
        '/home/rb/conway99_workspace/Conway99_C2_Profile46Cert_1.0.0/work/bi_c4.drat']
    with zipfile.ZipFile(args.installer) as archive:
        packed = archive.read('bi_c4_seed0.drat.gz')
        assert hashlib.sha256(packed).hexdigest() == c4['proof_archive']['gzip_sha256']
        import io
        raw_hash = hashlib.sha256()
        raw_bytes = 0
        with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
            for block in iter(lambda: stream.read(1048576), b''):
                raw_hash.update(block)
                raw_bytes += len(block)
        assert raw_hash.hexdigest() == c4['proof_archive']['uncompressed_sha256']
    print('C4_FORMULA_TRANSPORT_AND_PROOF_HASH_PASS', flush=True)
    reps = json.loads((source / 'profile46_orbits.json').read_text())
    cubes = [[int(x) for x in line.split()] for line in (source / 'cubes46.txt').read_text().splitlines()]
    state = json.loads((source / 'work/round.json').read_text())
    assert len(reps) == len(cubes) == len(state['cubes']) == 2170
    assert set(state['cubes']) == {str(i) for i in range(2170)}
    assert state['counts'] == {'UNSAT_VERIFIED': 2170} and state['status'] == 'PROFILE46_UNSAT_VERIFIED'
    assert state['identity']['cube_list_sha256'] == sha(source / 'cubes46.txt')
    assert state['identity']['manifest_sha256'] == sha(source / 'MANIFEST.json')
    with (work / 'profile_46.cnf').open('rb') as stream:
        header = stream.readline().decode().split()
        prefix = hashlib.sha256(f'p cnf {header[2]} {int(header[3]) + 42}\n'.encode())
        for block in iter(lambda: stream.read(1048576), b''):
            prefix.update(block)
    directed_pairs = list(itertools.permutations(range(7), 2))
    record_lines = ['code\taut\tmutual_edges\tdegrees\tstratum\n']
    case_lines = ['index\tcode\tformula_sha256\tproof_sha256\tproof_gzip_sha256\tchecker_log_sha256\n']
    seen = set()
    for index, (rep, cube) in enumerate(zip(reps, cubes)):
        edges = {(i, j) for i in range(7) for j in rep['out'][str(i)]}
        assert all(sum(a == i for a, b in edges) in (4, 6) for i in range(7))
        assert all(a != b and a in range(7) and b in range(7) for a, b in edges)
        code = sum(1 << k for k, e in enumerate(directed_pairs) if e in edges)
        assert code == rep['code'] and code not in seen
        seen.add(code)
        expected_units = [arcs[e] if e in edges else -arcs[e] for e in directed_pairs]
        assert cube == expected_units + [0]
        # Every transported forbidden C4 clause must hold on these signed units.
        positives = {v for v in expected_units if v > 0}
        assert all(any(-lit not in positives for lit in clause) for clause in transformed)
        description = json.loads((source / f'work/certificates/cube_{index:04d}/formula.json').read_text())
        h = prefix.copy()
        h.update(''.join(f'{v} 0\n' for v in expected_units).encode())
        digest = h.hexdigest()
        item = state['cubes'][str(index)]
        assert description == {'index': index, 'base_sha256': sha(work / 'profile_46.cnf') if index == 0 else profile_sha, 'units': expected_units, 'formula_sha256': digest}
        profile_sha = description['base_sha256']
        assert item['index'] == index and item['units'] == expected_units and item['formula_sha256'] == digest
        assert item['status'] == 'UNSAT_VERIFIED'
        receipt(item['solve'], f'cube_{index:04d}_solve', 20, 's UNSATISFIABLE')
        checker_hash = receipt(item['checker'], f'cube_{index:04d}_check', 0, 's VERIFIED')
        folder = f'/home/rb/conway99_workspace/Conway99_C2_Profile46Cert_1.0.0/work/certificates/cube_{index:04d}'
        assert item['checker']['command'][1:] == [folder + '/formula.cnf', folder + '/proof.drat']
        assert item['solve']['command'][2:] == [folder + '/formula.cnf', folder + '/proof.drat']
        assert item['solve']['outputs'] == {folder + '/proof.drat': item['proof_sha256']}
        assert item['proof_archive']['uncompressed_sha256'] == item['proof_sha256']
        assert item['proof_archive']['file'] == folder + '/proof.drat.gz'
        case_lines.append(f'{index}\t{code}\t{digest}\t{item["proof_sha256"]}\t{item["proof_archive"]["gzip_sha256"]}\t{checker_hash}\n')
        record_lines.append(f'{code}\t{rep["aut"]}\t0\tprofile46\tprofile46\n')
    case_path = args.output.with_name('profile46_case_bindings.tsv')
    case_path.write_text(''.join(case_lines))
    input_tsv = work / 'profile46_for_iso.tsv'
    input_tsv.write_text(''.join(record_lines))
    print('ALL_2170_FORMULAS_AND_CHECKER_RECEIPTS_PASS', flush=True)
    src = Path(__file__).resolve().parent
    cpp_sources = [repo / 'src/c2_completeness_20261012/audit_isomorphism.cpp', src / 'count46_independent.cpp']
    binaries = [work / 'iso', work / 'count46']
    for cpp, binary in zip(cpp_sources, binaries):
        subprocess.run(['g++', '-O3', '-std=c++17', str(cpp), '-o', str(binary)], check=True, capture_output=True)
    iso = subprocess.run([str(binaries[0]), str(input_tsv)], check=True, capture_output=True, text=True)
    iso_result = json.loads(iso.stdout)
    assert iso_result['records'] == 2170 and iso_result['labelled_orbit_sum'] == 10690440
    counts = subprocess.run([str(binaries[1])], check=True, capture_output=True, text=True)
    profile_counts = {}
    for line in counts.stdout.splitlines():
        row = line.split('\t')
        if row[0] == 'PROFILE46':
            profile_counts[int(row[1])] = int(row[4])
        else:
            assert row[0] == 'TOTAL46' and int(row[1]) == 10690440
    assert profile_counts == {0: 10448730, 1: 241710, **{i: 0 for i in range(2, 8)}}
    args.output.with_suffix('.log').write_text(iso.stderr + iso.stdout + counts.stdout)
    report = {
        'status': 'PASS', 'checked_at': datetime.now(ZoneInfo('Europe/Berlin')).isoformat(),
        'scope': 'Exact C4 formula on unrestricted base, semantic transport, Profile46 restricted census completeness, and all 2170 formula/receipt bindings.',
        'source_archive_sha256': sha(args.archive), 'installer_sha256': sha(args.installer),
        'profile346_dependency_hashes_all_match': True, 'encoder_files_identical_to_rest218': source_hashes,
        'formula_hashes': {name: sha(work / name) for name in ['base.cnf', 'variables.json', 'profile_46.cnf', 'profile_346.cnf', 'bi_c4.cnf']},
        'base_metadata': json.loads((work / 'base.json').read_text()),
        'profile_truth_table_checks': truth_checks,
        'c4': {'uses_unrestricted_base': True, 'units': units, 'transported_clauses': len(transformed), 'proof_gzip_and_raw_hash_verified': True, 'raw_proof_bytes': raw_bytes, 'checker_log_hash_verified': True, 'checker_replayed': False},
        'profile46': {'cases': 2170, 'all_cnf_hashes_reconstructed': True, 'all_solver_and_checker_logs_hashed_and_matched': True, 'all_operation_receipts_matched': True, 'proof_archive_metadata_bound': True, 'original_cube_proofs_read': False, 'checker_replays': 0, 'independent_isomorphism_audit': iso_result, 'independent_labelled_count': sum(profile_counts.values()), 'counts_by_number_d6': profile_counts, 'case_binding_sha256': sha(case_path)},
        'sources': {str(p.relative_to(repo)): sha(p) for p in [*cpp_sources, repo / 'src/c2_completeness_20261012/count_labelled.cpp', Path(__file__).resolve()]},
        'compiler': subprocess.run(['g++', '--version'], check=True, capture_output=True, text=True).stdout.splitlines()[0],
        'compiler_flags': ['-O3', '-std=c++17'],
        'limits': ['No SAT solver or proof checker was run.', 'Historical UNSAT checks remain inherited; all supplied receipt links and formula hashes were freshly audited.', 'The 2170 compressed case proofs remain external and were not read.', 'Encoder correctness requires the separately documented mathematical argument.', 'No exclusion of degrees 0, 1, or 2 and no general C2 exclusion.']
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('C4_PROFILE46_AUDIT_PASS', flush=True)


if __name__ == '__main__':
    main()
