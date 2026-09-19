"""Sequential UP diagnostics on three cases; fixed cubes shared by all variants."""
import argparse
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import tempfile
from residual import sha256, write_json


def propagate(binary, path, cube):
    return json.loads(subprocess.check_output([str(binary), str(path), *map(str, cube)], text=True))


def python_up(clauses, cube):
    work = [tuple(c) for c in clauses] + [(x,) for x in cube]
    fixed = set()
    while True:
        if any(not c for c in work):
            return True, fixed
        unit = next((c[0] for c in work if len(c) == 1), None)
        if unit is None:
            return False, fixed
        fixed.add(unit)
        work = [tuple(x for x in c if x != -unit) for c in work if unit not in c]


def check_engine(binary):
    rng = random.Random(20260919)
    count = 0
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / 'tiny.cnf'
        for trial in range(100):
            n = 6
            clauses = [tuple(rng.choice((-1,1))*v for v in rng.sample(range(1,n+1), rng.randrange(4)))
                       for _ in range(rng.randrange(20))]
            path.write_text(f'p cnf {n} {len(clauses)}\n' + ''.join(' '.join(map(str,c))+' 0\n' for c in clauses))
            for cube in ([], [1], [-1], [2,-3]):
                expected, fixed = python_up(clauses, cube)
                actual = propagate(binary, path, cube)
                assert actual['conflict'] == expected
                if not expected:
                    assert set(actual['primary_literals']) == fixed
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--variants', type=Path, required=True)
    parser.add_argument('--certificates', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.binary = args.binary.resolve()
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    controls = check_engine(args.binary)
    manifest = json.loads((args.variants / 'manifest.json').read_text())
    tri = json.loads((args.certificates / 'triangles.json').read_text())
    plan, roots = {}, {}
    for case in sorted({j['case'] for j in manifest['jobs']}):
        root = propagate(args.binary, args.variants / (case + '__totalizer.cnf'), [])
        assert not root['conflict']
        roots[case] = root
        fixed = {abs(v) for v in root['primary_literals']}
        split = next(v for v in range(1,1723) if v not in fixed)
        t = next(c for c in tri if all(abs(v) not in fixed for v in c))
        plan[case] = [[], [split], [-split], [-t[0], -t[1]], [-t[1], -t[2]]]
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out / 'cubes.json', plan)
    records = []
    for job in manifest['jobs']:
        path = args.variants / (job['id'] + '.cnf')
        assert sha256(path) == job['sha256']
        for index, cube in enumerate(plan[job['case']]):
            result = roots[job['case']] if job['variant'] == 'totalizer' and index == 0 else propagate(args.binary, path, cube)
            records.append({'job': job['id'], 'case': job['case'], 'variant': job['variant'],
                            'cube': index, 'assumptions': cube, **result})
        print(job['id'] + ' UP done', flush=True)
    for case in plan:
        for i in range(len(plan[case])):
            rows = {r['variant']: r for r in records if r['case'] == case and r['cube'] == i}
            for weak, strong in [('totalizer','lex'), ('totalizer','triangles'), ('lex','both'), ('triangles','both')]:
                a, b = rows[weak], rows[strong]
                if a['conflict']:
                    assert b['conflict']
                elif not b['conflict']:
                    assert set(a['primary_literals']) <= set(b['primary_literals'])
    report = {'status': 'C2_STRUCTURED_UP_PASS', 'engine_controls': controls,
              'engine_source_sha256': sha256(Path(__file__).with_name('up.cpp')),
              'engine_binary_sha256': sha256(args.binary), 'cube_sha256': sha256(args.out / 'cubes.json'),
              'variant_manifest_sha256': sha256(args.variants / 'manifest.json'),
              'records': records, 'scope': 'Propagation only; no search, no progress percentage; conflict trails are partial.'}
    write_json(args.out / 'report.json', report)
    print(json.dumps({'status': report['status'], 'queries': len(records), 'engine_controls': controls}))


if __name__ == '__main__':
    main()
