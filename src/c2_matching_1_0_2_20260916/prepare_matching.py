"""Prepare 11 whole-neighborhood matching representatives with unchanged baseline."""
from itertools import combinations
import json
from pathlib import Path
import subprocess
from common import ROOT, VERSION, REF_HASH, CNF_HASH, MAP_HASH, SOLVER_COMMIT, sha, save
from matching_orbits import check_cover
from windows_guard import host_probe

HERE = Path(__file__).resolve().parent


def prepare(reference, out):
    reference, out = Path(reference), Path(out)
    if sha(reference/'baseline.cnf') != CNF_HASH or sha(reference/'variables.json') != MAP_HASH:
        raise ValueError('Pinned reference identity mismatch')
    cover = check_cover()
    mapping = json.loads((reference/'variables.json').read_text())
    label_index = {tuple(label): i for i, label in enumerate(mapping['labels'])}
    variables = {(block, i, j): var for var, block, i, j in mapping['primary_variables']}
    vertices = [label_index[(0, a)] for a in range(2, 14)]
    if any(i >= mapping['pair_count'] for i in vertices):
        raise ValueError('Expected representative-half labels')
    edge_vars = {}
    for a, b in combinations(range(12), 2):
        i, j = sorted((vertices[a], vertices[b]))
        edge_vars[(a, b)] = variables['B', i, j]
    if len(set(edge_vars.values())) != 66:
        raise ValueError('Local primary map not injective')
    header, body = (reference/'baseline.cnf').read_bytes().split(b'\n', 1)
    if header != b'p cnf 570171 1990821' or not body.endswith(b'\n'):
        raise ValueError('Unexpected baseline header')
    out.mkdir(parents=True, exist_ok=False)
    jobs = []
    for orbit in cover['orbits']:
        name = 'matching_' + '_'.join(map(str, orbit['type']))
        matching = {tuple(edge) for edge in orbit['matching']}
        units = [var if edge in matching else -var for edge, var in edge_vars.items()]
        if len(units) != 66 or sum(u > 0 for u in units) != 6:
            raise ValueError('Wrong matching constraint count')
        suffix = ''.join(f'{u} 0\n' for u in units).encode()
        path = out/(name+'.cnf')
        path.write_bytes(b'p cnf 570171 1990887\n'+body+suffix)
        if path.read_bytes().split(b'\n', 1)[1] != body+suffix:
            raise ValueError('Exact prefix/suffix check failed')
        jobs.append({'id': name, 'group': 'matching_orbits', 'orbit_type': orbit['type'],
                     'labelled_count': orbit['labelled_count'], 'seed': 0, 'assumptions': units,
                     'cnf': str(path.resolve()), 'cnf_sha256': sha(path),
                     'outer_matching_labels': [[list(mapping['labels'][vertices[a]]),
                                                list(mapping['labels'][vertices[b]])] for a, b in sorted(matching)]})
    manifest = {'status': 'MATCHING_ORBITS_PREPARED_NOT_SOLVED', 'version': VERSION,
                'baseline_sha256': CNF_HASH, 'mapping_sha256': MAP_HASH,
                'cover': cover, 'jobs': jobs,
                'coverage': 'One representative per orbit under C2 wr S6 fixing frame vertices 0 and 1. Not an exact labelled partition.',
                'scope': 'Necessary local matching types; no extension to a full graph asserted.'}
    save(out/'manifest.json', manifest)
    return manifest


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if sha(HERE/'c2_reference.py') != REF_HASH:
        raise RuntimeError('Reference source changed')
    previous = Path.home()/'conway99_workspace/c2_scout_v2'
    config = json.loads((previous/'setup.json').read_text())
    if config['solver_source_commit'] != SOLVER_COMMIT or config['baseline_sha256'] != CNF_HASH or config['mapping_sha256'] != MAP_HASH:
        raise RuntimeError('Previous installation provenance mismatch')
    solver = config['solver']
    if sha(solver) != config['solver_sha256']:
        raise RuntimeError('Solver binary changed')
    if subprocess.check_output([solver, '--version'], text=True).strip() != '2.2.1':
        raise RuntimeError('Wrong solver version')
    host = host_probe()
    if host['free_bytes'] < 50*1024**3:
        raise RuntimeError('Windows disk reserve')
    parts = ROOT/'partitions'
    # Refuse to reuse a partial/edited manifest silently. Fresh installation is small.
    if parts.exists():
        raise RuntimeError('Matching partitions already exist; inspect setup.json instead of reinstalling')
    manifest = prepare(previous/'reference', parts)
    result = {'status': 'C2_MATCHING_PREPARED_NOT_LAUNCHED', 'version': VERSION,
              'source': str(HERE), 'solver': solver, 'solver_sha256': sha(solver),
              'solver_source_commit': SOLVER_COMMIT, 'baseline_sha256': CNF_HASH,
              'mapping_sha256': MAP_HASH, 'jobs': len(manifest['jobs']),
              'labelled_matchings': manifest['cover']['labelled_matchings'],
              'transports_checked': manifest['cover']['transports_checked'],
              'host_probe': host, 'production_solver_runs': 0}
    save(ROOT/'setup.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
