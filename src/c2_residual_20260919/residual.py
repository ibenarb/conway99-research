"""C2 residual stabilizers, prefix lex constraints and four streamed variants, v1.0.0."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, permutations, product
import json
from math import factorial
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src/c2_reference_20260913'))
sys.path.insert(0, str(ROOT / 'src/c2_matching_20260915'))
sys.path.insert(0, str(ROOT / 'src/c2_counter_ab_20260916'))
from c2_reference import CNF, Frame, sha256, write_json
from matching_orbits import canonical_matching, normalized, frame_action
from counter import CounterCNF, encode_variant

if not __debug__:
    raise RuntimeError('Assertions must be enabled; do not use Python -O')

VERSION = '1.0.0'
BASE_SHA = '7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd'
MAP_SHA = 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'
PARTS = [(1,1,1,1,1,1), (1,1,1,1,2), (1,1,1,3), (1,1,2,2),
         (1,1,4), (1,2,3), (1,5), (2,2,2), (2,4), (3,3), (6,)]


def closure(gens, n):
    identity = tuple(range(n))
    seen, pending = {identity}, [identity]
    for current in pending:
        for g in gens:
            image = tuple(g[current[i]] for i in range(n))
            if image not in seen:
                seen.add(image)
                pending.append(image)
    return seen


def stabilizer(parts):
    n = sum(parts)
    matching = canonical_matching(parts)
    elements = []
    for perm in permutations(range(n)):
        for flips in product(range(2), repeat=n):
            p = tuple(2 * perm[a // 2] + ((a % 2) ^ flips[a // 2]) for a in range(2*n))
            if normalized((p[a], p[b]) for a, b in matching) == matching:
                elements.append(p)
    gens, group = [], {tuple(range(2*n))}
    for p in elements:
        if p not in group:
            gens.append(p)
            group = closure(gens, 2*n)
    expected = 1
    for r, m in Counter(parts).items():
        expected *= (2*r)**m * factorial(m)
    assert len(group) == len(elements) == expected and group == set(elements)
    return gens, len(group)


def units_for(frame, parts):
    lookup = {lab: i for i, lab in enumerate(frame.labels)}
    vertices = [lookup[(0, a)] for a in range(2, frame.k)]
    matching = set(canonical_matching(parts))
    return [frame.edge(vertices[a], vertices[b]) * (1 if (a, b) in matching else -1)
            for a, b in combinations(range(len(vertices)), 2)]


def certificate(frame, parts):
    gens, order = stabilizer(parts)
    units = units_for(frame, parts)
    records = []
    for p in gens:
        q = [0, 1] + [a+2 for a in p]
        assert all(q[a ^ 1] == (q[a] ^ 1) for a in range(frame.k))
        vm = frame_action(frame, q)
        assert {vm[abs(u)] * (1 if u > 0 else -1) for u in units} == set(units)
        lookup = {lab: i for i, lab in enumerate(frame.labels)}
        outer = [lookup[tuple(sorted(q[a] for a in lab))] for lab in frame.labels]
        # Checks the data from which E1/E2/E3 are built: full incidence, fixed
        # pairing, forbidden edges, every edge variable and common-label targets.
        for x, y in combinations(range(len(outer)), 2):
            assert len(set(frame.labels[x]) & set(frame.labels[y])) == len(
                set(frame.labels[outer[x]]) & set(frame.labels[outer[y]]))
        records.append({'labels': q, 'outer': outer,
                        'primary_old_to_new': [vm[i] for i in range(1, len(frame.map)+1)]})
    return {'parts': parts, 'order': order, 'units': units, 'generators': records}


def add_lex(cnf, permutation, prefix):
    """Enforce (x_1,...,x_d) <=lex (x_p(1),...,x_p(d)). Fresh prefix gates."""
    if sorted(permutation) != list(range(1, len(permutation)+1)):
        raise ValueError('Invalid primary permutation')
    if not 0 <= prefix <= len(permutation):
        raise ValueError('Prefix outside primary order')
    positions = [(i, permutation[i-1]) for i in range(1, prefix+1) if i != permutation[i-1]]
    equal = True
    for index, (a, b) in enumerate(positions):
        cnf.clause(False if equal is True else -equal, -a, b)
        if index + 1 == len(positions):
            break
        nxt = cnf.variable()
        # nxt <=> equal AND (a <=> b). No unproved equality of orbit bits.
        cnf.clause(-nxt, equal)
        cnf.clause(-nxt, -a, b)
        cnf.clause(-nxt, a, -b)
        cnf.clause(False if equal is True else -equal, a, b, nxt)
        cnf.clause(False if equal is True else -equal, -a, -b, nxt)
        equal = nxt


def triangles(frame):
    clauses = set()
    for x, y, z in combinations(range(len(frame.labels)), 3):
        if not any(set(frame.labels[a]) & set(frame.labels[b]) for a, b in ((x,y),(x,z),(y,z))):
            continue
        edges = [frame.edge(x,y), frame.edge(x,z), frame.edge(y,z)]
        if any(e is False for e in edges):
            continue
        clauses.add(tuple(sorted(set(-e for e in edges))))
    return sorted(clauses)


def export(out):
    out.mkdir(parents=True, exist_ok=False)
    cnf, frame = CNF(), Frame(14)
    frame.allocate(cnf)
    try:
        write_json(out / 'variables.json', frame.mapping())
        assert sha256(out / 'variables.json') == MAP_SHA
        cases = []
        for parts in PARTS:
            row = certificate(frame, parts)
            name = 'matching_' + '_'.join(map(str, parts))
            write_json(out / (name + '.json'), row)
            cases.append({'id': name, 'order': row['order'], 'generators': len(row['generators']),
                          'sha256': sha256(out / (name + '.json'))})
        tri = triangles(frame)
        assert len(tri) == 28980 and all(len(c) == 3 for c in tri)
        write_json(out / 'triangles.json', tri)
        manifest = {'version': VERSION, 'status': 'EXPORTED_NOT_SOLVED', 'cases': cases,
                    'triangle_count': len(tri), 'triangle_sha256': sha256(out / 'triangles.json'),
                    'mapping_sha256': MAP_SHA, 'primary_order': '1..1722, false < true',
                    'action': 'permutation[i-1] is image of primary variable i; lex uses pullback x[p(i)]'}
        write_json(out / 'manifest.json', manifest)
        return manifest
    finally:
        cnf.close()


def prepare(certdir, out, selected, prefix):
    if not 0 <= prefix <= 1722:
        raise ValueError('Invalid prefix')
    manifest = json.loads((certdir / 'manifest.json').read_text())
    if manifest['mapping_sha256'] != MAP_SHA or sha256(certdir / 'variables.json') != MAP_SHA:
        raise ValueError('Mapping mismatch')
    if sha256(certdir / 'triangles.json') != manifest['triangle_sha256']:
        raise ValueError('Triangle certificate mismatch')
    cases = [c for c in manifest['cases'] if not selected or c['id'] in selected]
    if selected and {c['id'] for c in cases} != set(selected):
        raise ValueError('Unknown case')
    out.mkdir(parents=True, exist_ok=False)
    cnf, frame = CounterCNF(), Frame(14)
    frame.allocate(cnf)
    try:
        encode_variant(cnf, frame)
        base = cnf.write(out / 'base.cnf')
        assert base['sha256'] == BASE_SHA
    finally:
        cnf.close()
    shutil.copyfile(certdir / 'variables.json', out / 'variables.json')
    tri = json.loads((certdir / 'triangles.json').read_text())
    jobs = []
    for case in cases:
        file = certdir / (case['id'] + '.json')
        assert sha256(file) == case['sha256']
        cert = json.loads(file.read_text())
        for variant in ('totalizer', 'lex', 'triangles', 'both'):
            extra = CNF()
            extra.variables = base['variables']
            try:
                for unit in cert['units']:
                    extra.clause(unit)
                lex_start = extra.variables + 1
                if variant in ('lex', 'both'):
                    for g in cert['generators']:
                        add_lex(extra, g['primary_old_to_new'], prefix)
                if variant in ('triangles', 'both'):
                    for clause in tri:
                        extra.clause(*clause)
                name = case['id'] + '__' + variant
                path = out / (name + '.cnf')
                with path.open('wb') as target, (out / 'base.cnf').open('rb') as source:
                    source.readline()
                    target.write(f"p cnf {extra.variables} {base['clauses'] + extra.clauses}\n".encode())
                    shutil.copyfileobj(source, target)
                    extra.body.flush()
                    extra.body.seek(0)
                    shutil.copyfileobj(extra.body, target)
                jobs.append({'id': name, 'case': case['id'], 'variant': variant,
                             'variables': extra.variables, 'clauses': base['clauses'] + extra.clauses,
                             'sha256': sha256(path), 'certificate_sha256': case['sha256'],
                             'lex_auxiliary_range': [lex_start, extra.variables] if extra.variables >= lex_start else [],
                             'prefix': prefix if variant in ('lex', 'both') else None})
            finally:
                extra.close()
    report = {'version': VERSION, 'status': 'PREPARED_NOT_SOLVED', 'base': base,
              'mapping_sha256': MAP_SHA, 'jobs': jobs, 'production_solver_runs': 0}
    write_json(out / 'manifest.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    ex = sub.add_parser('export')
    ex.add_argument('--out', type=Path, required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--certificates', type=Path, required=True)
    prep.add_argument('--out', type=Path, required=True)
    prep.add_argument('--case', action='append', default=[])
    prep.add_argument('--prefix', type=int, default=1722)
    args = parser.parse_args()
    if args.command == 'export':
        result = export(args.out)
    else:
        result = prepare(args.certificates, args.out, args.case, args.prefix)
    print(json.dumps({'status': result['status'], 'count': len(result.get('cases', result.get('jobs', [])))}))
