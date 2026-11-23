from pathlib import Path
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from math import lcm

BASE = Path(__file__).resolve().parent
os.chdir(BASE)
import own_local
import own_setup


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, output, error):
    command = ['wsl.exe', '--distribution', 'Ubuntu-24.04', '--cd', str(BASE), '--exec'] + args
    with output.open('wb') as fo, error.open('wb') as fe:
        completed = subprocess.run(command, stdout=fo, stderr=fe, creationflags=subprocess.CREATE_NO_WINDOW)
    if completed.returncode:
        raise RuntimeError({'command': args, 'exit_code': completed.returncode})


def archive(path):
    original_hash = sha(path)
    zipped = Path(str(path) + '.gz')
    with path.open('rb') as fi, gzip.open(zipped, 'wb', compresslevel=6) as fo:
        while chunk := fi.read(1024 * 1024):
            fo.write(chunk)
    h = hashlib.sha256()
    with gzip.open(zipped, 'rb') as fi:
        while chunk := fi.read(1024 * 1024):
            h.update(chunk)
    assert h.hexdigest() == original_hash
    record = {'uncompressed_sha256': original_hash, 'compressed_sha256': sha(zipped), 'compressed_bytes': zipped.stat().st_size}
    path.unlink()
    return record


def main(job_id):
    manifest = json.loads((BASE / 'jobs_manifest.json').read_text())
    job = next(j for j in manifest['jobs'] if j['id'] == job_id)
    work = BASE / 'jobs' / job_id
    work.mkdir(parents=True, exist_ok=False)
    start = time.time()
    result = {'job': job, 'started': start, 'pid': os.getpid(), 'status': 'RUNNING'}
    (work / 'identity.json').write_text(json.dumps(result, indent=4))
    try:
        cid, par, mode = job['chart'], job['own_parity'], job['mode']
        C = own_local.Chart(cid, par)
        bounds = {}
        for label, matrix, bound in [('signed', C.Finv, 3600), ('unsigned', C.Hinv, 2304)]:
            denominator = lcm(*(x.denominator for row in matrix for x in row))
            maximum = max(abs(int(x*denominator)) for row in matrix for x in row)
            assert maximum*bound < 2**63 and 10*denominator < 2**63
            bounds[label] = dict(denominator=denominator, int64_conservative_bound=maximum*bound)
        result['numpy_arithmetic_bounds'] = bounds
        C = own_setup.write_setup(cid, par, work / 'setup.txt')
        assert C and C.rank in (10, 11)
        raw = work / 'stars.txt'
        if job['kind'] == 'strong':
            orbit = json.loads((BASE / 'orbits_result.json').read_text())
            assert orbit['status'] == 'ALL_98_ORBIT_REGENERATIONS_PASS'
            source = BASE / 'reps' / f'{cid}.{par}.txt'
            assert sha(source) == orbit['reps_sha256'][f'{cid}.{par}.txt']
            raw.write_bytes(source.read_bytes())
            expected = orbit['counts'][f'{cid},{par}']['orbits']
        else:
            run(['./star_dump_checked', 'layouts.tsv', str(cid), str(par)], raw, work / 'star.stderr')
            expected = json.loads((BASE / 'star_counts_own.json').read_text())[f'{cid},{par}']
        assert expected > 0
        seen = set()
        with raw.open() as fi:
            for line in fi:
                words = tuple(map(int, line.split()))
                assert len(words) == 24 and words not in seen
                seen.add(words)
                for i in range(12):
                    s, g = words[2*i:2*i+2]
                    assert s in C.words_central[i//2] and 0 <= g and g & ~s == 0
                    for j in range(i+1):
                        t, h = words[2*j:2*j+2]
                        assert (s&t).bit_count()-2*((g^h)&s&t).bit_count() == C.HA[i][j]
        assert len(seen) == expected
        del seen
        rel = work.relative_to(BASE).as_posix()
        run(['./own_pair2_checked', rel+'/setup.txt', rel+'/stars.txt', str(mode), '30', '1'], work/'solver.stdout', work/'solver.stderr')
        out = (work/'solver.stdout').read_text()
        err = (work/'solver.stderr').read_text()
        m = re.search(r'stars (\d+) open (\d+) closed (\d+)', out)
        assert m, 'Missing exhaustion summary'
        stars, opened, closed = map(int, m.groups())
        assert stars == expected and closed+opened == stars
        assert 'runtime error:' not in err
        result.update(status='SECOND_SOLVER_CLOSED' if opened == 0 else 'OPEN_NOT_EXCLUSION', stars=stars, open=opened, closed=closed, elapsed_seconds=time.time()-start, depth_limit=30, source_hashes={p:sha(BASE/p) for p in ['own_pair2.cpp','own_pair2_checked','star_dump.cpp','star_dump_checked','own_local.py','own_setup.py','layouts.tsv','jobs_manifest.json']})
        result['input_archives'] = {p:archive(work/p) for p in ['setup.txt','stars.txt']}
        result['output_hashes'] = {p:sha(work/p) for p in ['solver.stdout','solver.stderr']}
    except Exception as exc:
        result.update(status='ERROR_NOT_EXCLUSION', error=repr(exc), elapsed_seconds=time.time()-start)
    (work/'result.json').write_text(json.dumps(result, indent=4))
    print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'SECOND_SOLVER_CLOSED' else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
