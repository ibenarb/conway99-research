"""Prepare pinned reference versus E3 totalizer; no solver launch."""
import fcntl
import json
from pathlib import Path
import shutil
import subprocess
import time
from common import ROOT, VERSION, CNF_HASH, MAP_HASH, REF_HASH, sha, save
from c2_reference import CNF, Frame, encode_base, write_json
from counter import CounterCNF, encode_variant
from check_counter import check
from windows_guard import host_probe

HERE = Path(__file__).resolve().parent
OLD = Path.home() / 'conway99_workspace/c2_matching_v1'
SCOUT = Path.home() / 'conway99_workspace/c2_scout_v2'
SOLVER_HASH = '51e256422129042b730eff10a5c0e91e70c69ddc878c65ed332dd56902a57e3c'


def main():
    lock = (OLD / 'campaign.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (ROOT / 'setup.json').exists() or (ROOT / 'partitions').exists():
        raise RuntimeError('Prepared/partial installation already exists; refusing overwrite')
    old = json.loads((OLD / 'setup.json').read_text())
    if sha(old['solver']) != SOLVER_HASH or sha(HERE / 'c2_reference.py') != REF_HASH:
        raise RuntimeError('Pinned solver/reference source identity mismatch')
    if sha(SCOUT / 'reference/baseline.cnf') != CNF_HASH or sha(SCOUT / 'reference/variables.json') != MAP_HASH:
        raise RuntimeError('Pinned baseline/mapping identity mismatch')
    host = host_probe()
    if host['free_bytes'] < 55 * 1024**3 or shutil.disk_usage(ROOT).free < 30 * 1024**3:
        raise RuntimeError('Insufficient host/Linux preparation reserve')
    print('PREPARE 1/3: independent projection controls', flush=True)
    controls = check()
    print(json.dumps(controls), flush=True)
    parts = ROOT / 'partitions'
    parts.mkdir()
    old_manifest = json.loads((OLD / 'partitions/manifest.json').read_text())
    previous = old_manifest['jobs']
    if len(previous) != 11 or len({j['id'] for j in previous}) != 11:
        raise RuntimeError('Expected eleven matching representatives')
    reference_header, reference_body = (SCOUT / 'reference/baseline.cnf').read_bytes().split(b'\n', 1)
    jobs = []
    for j in previous:
        if sha(j['cnf']) != j['cnf_sha256']:
            raise RuntimeError('Previous matching input modified')
        suffix = ''.join(f'{v} 0\n' for v in j['assumptions']).encode()
        if Path(j['cnf']).read_bytes() != b'p cnf 570171 1990887\n' + reference_body + suffix:
            raise RuntimeError('Reference case prefix or assumptions mismatch')
        jobs.append(dict(j, id='reference__' + j['id'], group='reference'))
    print('PREPARE 2/3: E3 totalizer CNF and exact matching suffixes', flush=True)
    cnf, frame = CounterCNF(), Frame(14)
    frame.allocate(cnf)
    write_json(parts / 'variables.json', frame.mapping())
    if sha(parts / 'variables.json') != MAP_HASH:
        raise RuntimeError('Primary mapping changed')
    phases = encode_variant(cnf, frame)
    info = cnf.write(parts / 'totalizer.cnf')
    cnf.close()
    expected = json.loads((HERE / 'GENERATION.json').read_text())['variant']
    if info != expected:
        raise RuntimeError('Variant generation identity mismatch')
    header, body = (parts / 'totalizer.cnf').read_bytes().split(b'\n', 1)
    for j in previous:
        suffix = ''.join(f'{v} 0\n' for v in j['assumptions']).encode()
        path = parts / ('totalizer__' + j['id'] + '.cnf')
        path.write_bytes(f'p cnf {info["variables"]} {info["clauses"] + 66}\n'.encode() + body + suffix)
        if path.read_bytes().split(b'\n', 1)[1] != body + suffix:
            raise RuntimeError('Variant suffix mismatch')
        jobs.append(dict(j, id='totalizer__' + j['id'], group='totalizer',
                         cnf=str(path), cnf_sha256=sha(path)))
    print('PREPARE 3/3: finite solver integration controls', flush=True)
    for encoder, encode, label in ((CNF, encode_base, 'reference'), (CounterCNF, encode_variant, 'totalizer')):
        c, f = encoder(), Frame(4)
        f.allocate(c)
        encode(c, f)
        sat_path = parts / (label + '_small_sat.cnf')
        c.write(sat_path)
        c.clause(False)
        unsat_path = parts / (label + '_small_unsat.cnf')
        c.write(unsat_path)
        c.close()
        for path, expected in ((sat_path, 10), (unsat_path, 20)):
            r = subprocess.run([old['solver'], str(path)], capture_output=True, timeout=15)
            (path.with_suffix('.log')).write_bytes(r.stdout + r.stderr)
            if r.returncode != expected:
                raise RuntimeError('Solver integration control failed: ' + str(path))
    manifest = dict(version=VERSION, cover=old_manifest['cover'], jobs=jobs, variant=info,
                    phases=phases, controls=controls, reference_sha256=CNF_HASH,
                    mapping_sha256=MAP_HASH, source_sha256=sha(HERE / 'counter.py'),
                    schedule='Reference eleven first, then totalizer eleven; barrier between waves',
                    production_solver_runs=0, proof_files_created=0)
    save(parts / 'manifest.json', manifest)
    save(ROOT / 'setup.json', dict(old, version=VERSION, source=str(HERE), jobs=22))
    print(json.dumps(dict(status='COUNTER_AB_PREPARED_NOT_LAUNCHED', version=VERSION,
                          variant=info, jobs=22, controls=controls, output=str(ROOT),
                          production_solver_runs=0, proof_files_created=0)), flush=True)


if __name__ == '__main__':
    main()
