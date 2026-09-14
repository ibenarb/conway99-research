"""Prepare eight exhaustive C2 cubes; no solver is run."""
import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

CNF_HASH = 'f9d6011c5e6eb8a0fab971fa324d159e94b8bc4526b7b17dc31ee55aee1c25ba'
MAP_HASH = 'cd78938cc0fd6c4b2239ddd2b67054e1ea754b41be4dc6eeaef6849b97e0bc0e'
SPLIT = (22, 36, 685)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(base, out):
    raw = (base / 'baseline.cnf').read_bytes()
    mapping_raw = (base / 'variables.json').read_bytes()
    if sha(raw) != CNF_HASH or sha(mapping_raw) != MAP_HASH:
        raise ValueError('Pinned input integrity failure')
    mapping = json.loads(mapping_raw)
    rows = {row[0]: row for row in mapping['primary_variables']}
    assert [rows[v] for v in SPLIT] == [[22, 'B', 0, 22], [36, 'B', 0, 36], [685, 'B', 22, 36]]
    assert [mapping['labels'][i] for i in (0, 22, 36)] == [[0, 2], [4, 6], [8, 10]]
    header, body = raw.split(b'\n', 1)
    assert header.split() == [b'p', b'cnf', b'570171', b'1990821']
    assert body.endswith(b'\n')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'baseline.cnf').write_bytes(raw)
    (out / 'variables.json').write_bytes(mapping_raw)
    cases = []
    for bits in itertools.product((0, 1), repeat=3):
        literals = [v if bit else -v for v, bit in zip(SPLIT, bits)]
        name = 'cube_' + ''.join(map(str, bits))
        suffix = ''.join(str(v) + ' 0\n' for v in literals).encode()
        data = b'p cnf 570171 1990824\n' + body + suffix
        path = out / (name + '.cnf')
        path.write_bytes(data)
        checked = path.read_bytes()
        assert checked == data
        assert checked.split(b'\n', 1)[1] == body + suffix
        cases.append({'id': name, 'assumptions': literals, 'sha256': sha(checked), 'bytes': len(checked)})
    for bits in itertools.product((0, 1), repeat=3):
        assignment = dict(zip(SPLIT, bits))
        assert sum(all(assignment[abs(v)] == (v > 0) for v in c['assumptions']) for c in cases) == 1
    report = {'status': 'EXHAUSTIVE_PARTITION_PREPARED_NOT_SOLVED', 'version': '1.0.0',
              'cnf_sha256': CNF_HASH, 'mapping_sha256': MAP_HASH,
              'source_sha256': sha(Path(__file__).read_bytes()), 'split_variables': list(SPLIT),
              'cases': cases, 'coverage_assignments_checked': 8, 'solver_runs': 0,
              'scope': 'Every baseline assignment belongs to exactly one cube; no symmetry reduction or exclusion.',
              'next_benchmark': 'Eight cubes with seed 0 plus three baseline controls, matched search budgets and LRAT settings.',
              'output': str(out)}
    (out / 'partition.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path.home() / 'conway99_workspace/c2_reference_v1'
    parser.add_argument('--base', type=Path, default=root / 'prepare_20260913_160812_780017/k14')
    parser.add_argument('--out', type=Path, default=root / ('partition_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')))
    args = parser.parse_args()
    result = prepare(args.base, args.out)
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}), flush=True)
