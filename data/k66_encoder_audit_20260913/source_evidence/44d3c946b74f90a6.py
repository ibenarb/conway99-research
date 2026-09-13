"""Pinned, read-only preparation of the 23 residual fixed-K3/k66 CNFs."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import itertools
import json
import math
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import o3_v4_preflight as core
import o3_verify_psd_minors as minor

COMMIT = 'b279cd6de420bc4ad64869c8c7f99d653c73a195'
ROOT_SHA = 'b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0'
CASE_ID = 'k66_s1_t225'
ENCODER_PATH = 'src/reconciliation/o3_fixed_triangle_certify.py'
V3_PATH = 'src/reconciliation/o3_fixed_triangle_structural_v3.py'
BLOBS = {
    ENCODER_PATH: '4dc25c74cc31c04a28344b5d7b067ab0f5afe172',
    V3_PATH: '33304bed06710a0e0da08119e954bc158d2f0224',
    'docs/breadth1/O3_fixed_triangle_internal_model.md': '498546157b3597867c5af78aad6011aa7e5cb94d',
}
INPUT_SHA = 'abd6426cf649a0ad9a1854f31f64d8024e5ec2d3d9c7f6cf33b7fa921a7fdd12'
SOURCE_ZIP_SHA = 'cd67e2f26d14ce1351ccf58b03be77b91e545dbc5d70bf2ed8e1851d3f59c29e'


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path: Path, data: Any) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)


def get_pinned_sources(repo: Path, out: Path) -> dict[str, Any]:
    result = {'repository': str(repo), 'reference_commit': COMMIT, 'files': {}}
    check = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', COMMIT + '^{commit}'], text=True).strip()
    require(check == COMMIT, 'Pinned reference commit missing from local Git object store')
    for relative, expected in BLOBS.items():
        blob = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', f'{COMMIT}:{relative}'], text=True).strip()
        require(blob == expected, 'Reference tree/blob mismatch: ' + relative)
        content = subprocess.check_output(['git', '-C', str(repo), 'cat-file', 'blob', blob])
        actual = hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
        require(actual == expected, 'Downloaded Git object content mismatch: ' + relative)
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        result['files'][relative] = {'blob': blob, 'sha256': sha(destination)}
    return result


def canonical_case(source: Path) -> dict[str, Any]:
    """Evaluate only the pinned V3's pure case-generation definitions."""
    names = {'sha_text', 'edge', 'svar', 'lvar', 'matching_group', 'pair_key',
             'local_types', 'canon_types', 'ord_pair_count', 'build_case_data'}
    tree = ast.parse(source.read_text())
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    require({node.name for node in selected} == names, 'Pinned V3 functions incomplete')
    pairs = list(itertools.combinations(range(32), 2))
    namespace = {
        'itertools': itertools, 'Counter': Counter, 'math': math, 'hashlib': hashlib, 'json': json,
        'N': 32, 'GROUPS': (tuple(range(4)), tuple(range(4, 8)), tuple(range(8, 12))),
        'T': (12, 13), 'ORD': tuple(range(14, 32)), 'PAIRS': pairs,
        'PAIR_INDEX': {pair: index for index, pair in enumerate(pairs)}, 'EXPECTED_ROOT_SHA256': ROOT_SHA,
    }
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(source), 'exec'), namespace)
    cases = namespace['build_case_data']()['cases']
    return next(case for case in cases if case['id'] == CASE_ID)


def independent_t_literals(case: Any) -> list[int]:
    pairs = list(itertools.combinations(range(32), 2))
    variable = {pair: index + 1 for index, pair in enumerate(pairs)}
    values: dict[int, bool] = {}
    d = 6 - case['s']
    c = case['cell_sizes'][0]
    ordinary = list(range(14, 32))
    n0 = set(ordinary[:d])
    n1 = set(ordinary[:c]) | set(ordinary[d:d + d - c])
    for (i, j), var in variable.items():
        if i not in (12, 13) and j not in (12, 13):
            continue
        if (i, j) == (12, 13):
            edge = bool(case['s'])
        else:
            t, other = (i, j) if i in (12, 13) else (j, i)
            edge = bool(case['attached_T_bits'][other][t - 12]) if other < 12 else other in (n0 if t == 12 else n1)
        values[var] = edge
        values[var + 496] = False
    return sorted((v if bit else -v for v, bit in values.items()), key=abs)


def complete_units(t_units: list[int], neighbors: Any) -> list[int]:
    mapping = {pair: k + 1 for k, pair in enumerate(itertools.combinations(range(32), 2))}
    values = {abs(lit): lit > 0 for lit in t_units}
    for i, j in itertools.combinations(range(12), 2):
        values[mapping[i, j]] = j in neighbors[i]
        values[mapping[i, j] + 496] = False
    result = [v if bit else -v for v, bit in sorted(values.items())]
    require(len(result) == 254 and len({abs(v) for v in result}) == 254, 'Unexpected primary assignment count')
    return result


def write_leaf(root: Path, units: list[int], destination: Path) -> str:
    with root.open('rb') as source, destination.open('xb') as target:
        header = source.readline().split()
        require(header[:2] == [b'p', b'cnf'], 'Unexpected root CNF header')
        target.write(f'p cnf {int(header[2])} {int(header[3]) + len(units)}\n'.encode())
        shutil.copyfileobj(source, target, 1 << 20)
        for literal in units:
            target.write(f'{literal} 0\n'.encode())
    return sha(destination)


def verify_leaf(root: Path, leaf: Path, units: list[int]) -> None:
    """Independent byte-prefix/EOF comparison, not just a stored digest."""
    with root.open('rb') as a, leaf.open('rb') as b:
        ra, rb = a.readline().split(), b.readline().split()
        require(ra[:2] == rb[:2] == [b'p', b'cnf'], 'Invalid DIMACS header')
        require(ra[2] == rb[2] and int(rb[3]) == int(ra[3]) + len(units), 'Leaf dimensions mismatch')
        while block := a.read(1 << 20):
            require(b.read(len(block)) == block, 'Root clauses changed in terminal CNF')
        require(b.read() == b''.join(f'{lit} 0\n'.encode() for lit in units), 'Terminal assumptions mismatch')


def prepare(repo: Path, run: Path, payload: Path, root_hint: Path | None = None) -> dict[str, Any]:
    require(sha(payload / 'k66_input.json') == INPUT_SHA, 'Accepted k66 input hash mismatch')
    snapshot = run / 'reference'
    provenance = get_pinned_sources(repo, snapshot)
    original = json.loads((payload / 'k66_input.json').read_text())
    types, lookup = core.local_types()
    case = next(c for c in core.build_cases(types, lookup) if c['id'] == CASE_ID)
    summary, records = core.audit_case(case, types, core.transformation_table(), True, lambda *args: None)
    require(records == original['orbits'], 'Recomputed V4 partition differs from accepted local archive')
    require(summary['V4_orbits'] == 246 and summary['exact_PSD_orbits'] == 23, 'k66 expected counts failed')
    excluded = []
    selected = []
    for record in records:
        code = record[0]
        neighbors = core.neighbors_for(core.TRIPLES[code])
        if record[5]:
            selected.append(code)
        else:
            require(record[6] is not None, 'Unexplained discarded orbit')
            minor.validate(minor.combinatorial_gram(case, neighbors), record[6], rational=True)
            excluded.append({'code': code, 'orbit_size': record[1], 'witness': record[6]})
    require(len(excluded) == 223 and len(selected) == 23, 'Mixed coverage partition incomplete')
    t_units = independent_t_literals(case)
    canonical = canonical_case(snapshot / V3_PATH)
    require(set(t_units) == set(canonical['lits']), 'Independent/canonical V3 literal mismatch')
    source = snapshot / ENCODER_PATH
    root = run / 'root.cnf'
    if root_hint is not None and root_hint.is_file():
        require(sha(root_hint) == ROOT_SHA, 'Existing root CNF differs from pinned SHA256')
        shutil.copyfile(root_hint, root)
        root_origin = str(root_hint)
    else:
        spec = importlib.util.spec_from_file_location('pinned_encoder', source)
        require(spec is not None and spec.loader is not None, 'Encoder import failed')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cnf, _, _, _ = module.build()
        module.write_dimacs(cnf, root)
        del cnf
        root_origin = 'regenerated_from_pinned_encoder'
    require(sha(root) == ROOT_SHA, 'Regenerated root SHA256 differs from canonical root')
    jobs = []
    for code in selected:
        neighbors = core.neighbors_for(core.TRIPLES[code])
        units = complete_units(t_units, neighbors)
        job = run / 'jobs' / f'v4_{code:05d}'
        job.mkdir(parents=True, exist_ok=False)
        leaf = job / 'leaf.cnf'
        digest = write_leaf(root, units, leaf)
        verify_leaf(root, leaf, units)
        jobs.append({'id': job.name, 'code': code, 'units': units, 'cnf_sha256': digest,
                     'matching_permutations': [list(core.PERMS[k]) for k in core.TRIPLES[code]]})
    expected_hashes = json.loads((payload / 'expected_terminal_hashes.json').read_text())
    require({job['id']: job['cnf_sha256'] for job in jobs} == expected_hashes,
            'Terminal CNFs differ from independently generated reference hashes')
    manifest = {
        'format': 'CONWAY99-K66-V4-PILOT-1', 'case_id': CASE_ID, 'provenance': provenance,
        'input_archive_sha256': SOURCE_ZIP_SHA, 'k66_input_sha256': INPUT_SHA,
        'expected_terminal_hashes_sha256': sha(payload / 'expected_terminal_hashes.json'),
        'root_sha256': ROOT_SHA, 'root_origin': root_origin, 'jobs': jobs,
        'V4_orbits_total': 246, 'labelled_crossmatchings': 13824, 'stabilizer_order': 64,
        'arithmetic_exclusions': excluded, 'residual_jobs': 23,
        'coverage_checks': ['Burnside', 'direct_disjoint_orbits', '223_rational_minor_checks',
                            'canonical_V3_literal_equality', 'unchanged_CNF_prefix_and_exact_units'],
        'claim_scope': '223 exact arithmetic exclusions plus 23 pending LRAT/Cake obligations. No global SRG exclusion.',
        'case_summary': summary,
    }
    save(run / 'manifest.json', manifest)
    print(f'K66_PREPARE_PASS V4=246 arithmetic=223 residual=23 root_sha256={ROOT_SHA}', flush=True)
    return manifest


def verify_prepared(run: Path) -> dict[str, Any]:
    manifest = json.loads((run / 'manifest.json').read_text())
    require(manifest['format'] == 'CONWAY99-K66-V4-PILOT-1', 'Unknown manifest format')
    require(manifest['root_sha256'] == ROOT_SHA and sha(run / 'root.cnf') == ROOT_SHA, 'Resume root mismatch')
    for relative, expected in BLOBS.items():
        content = (run / 'reference' / relative).read_bytes()
        blob = hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
        require(blob == expected, 'Reference snapshot changed: ' + relative)
    types, lookup = core.local_types()
    case = next(c for c in core.build_cases(types, lookup) if c['id'] == CASE_ID)
    _, records = core.audit_case(case, types, core.transformation_table(), True, lambda *args: None)
    selected = {r[0] for r in records if r[5]}
    expected_excluded = [{'code': r[0], 'orbit_size': r[1], 'witness': r[6]} for r in records if not r[5]]
    require(manifest['arithmetic_exclusions'] == expected_excluded, 'Resume arithmetic coverage changed')
    for record in expected_excluded:
        neighbors = core.neighbors_for(core.TRIPLES[record['code']])
        minor.validate(minor.combinatorial_gram(case, neighbors), record['witness'], rational=True)
    require(len(manifest['jobs']) == 23 and {j['code'] for j in manifest['jobs']} == selected, 'Resume selection incomplete')
    require(len({j['id'] for j in manifest['jobs']}) == 23, 'Resume duplicate job IDs')
    t_units = independent_t_literals(case)
    require(set(t_units) == set(canonical_case(run / 'reference' / V3_PATH)['lits']), 'Resume V3 mismatch')
    for job in manifest['jobs']:
        require(job['id'] == f"v4_{job['code']:05d}", 'Unexpected job path')
        expected_units = complete_units(t_units, core.neighbors_for(core.TRIPLES[job['code']]))
        require(job['units'] == expected_units, 'Resume primary assignments changed')
        leaf = run / 'jobs' / job['id'] / 'leaf.cnf'
        require(sha(leaf) == job['cnf_sha256'], 'Resume CNF changed: ' + job['id'])
        verify_leaf(run / 'root.cnf', leaf, job['units'])
    return manifest
