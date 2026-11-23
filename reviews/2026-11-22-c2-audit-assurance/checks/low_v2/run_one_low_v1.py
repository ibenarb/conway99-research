from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
os.chdir(BASE)
import own_local
import low_setup_v1

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(args, output, error):
    command = ['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec']+args
    with output.open('wb') as out, error.open('wb') as err:
        result = subprocess.run(command, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    return result.returncode

def main(cid, parity):
    key = f'{cid}.{1-parity}'
    directory = BASE/'jobs'/key
    if directory.exists():
        raise RuntimeError('Existing job: inspect evidence and identity, never overwrite or duplicate.')
    resource = measure()
    assert max(row['system_busy_cpu'] for row in resource['intervals'])+1 <= 20
    assert resource['ram_free_gib'] >= 10 and resource['disk_free_gib'] >= 35
    directory.mkdir(parents=True)
    started = time.time()
    report = dict(status='RUNNING', chart=cid, own_parity=parity, packet_parity=1-parity,
                  started=started, identity=identity(os.getpid()), resource_at_admission=resource)
    (directory/'identity.json').write_text(json.dumps(report,indent=4))
    try:
        control = json.loads((BASE/'gram_controls_result.json').read_text())
        assert control['status'] == 'GRAM_CONTROLS_PASS'
        for name in ['residual_gram_v1.cpp','residual_gram_v1_checked']:
            assert sha(BASE/name) == control['hashes'][name]
        chart, setup = low_setup_v1.write_setup(cid,parity,directory/'setup.txt')
        report.update(rank=chart.rank, setup=setup)
        status = run(['./star_dump_checked','layouts.tsv',str(cid),str(parity)],
                     directory/'stars.txt',directory/'stars.stderr')
        assert status == 0
        expected = json.loads((BASE/'star_counts_own.json').read_text())[f'{cid},{parity}']
        seen = set()
        for line in (directory/'stars.txt').read_text().splitlines():
            words = tuple(map(int,line.split()))
            assert len(words) == 24 and words not in seen
            seen.add(words)
            for i in range(12):
                s,g = words[2*i:2*i+2]
                assert s in chart.words_central[i//2] and g >= 0 and g & ~s == 0
                for j in range(i+1):
                    t,h = words[2*j:2*j+2]
                    assert (s&t).bit_count()-2*((g^h)&s&t).bit_count() == chart.HA[i][j]
        assert len(seen) == expected and expected > 0
        if chart.rank == 8:
            reference = {tuple(x for pair in star for x in pair) for star in chart.star_assignments()}
            assert seen == reference
            report['python_cpp_star_sets_equal'] = True
        relative = directory.relative_to(BASE).as_posix()
        report['expected_stars'] = expected
        report['phase'] = 'FULL_SEARCH'
        (directory/'progress.json').write_text(json.dumps(report,indent=4))
        status = run(['./residual_gram_v1_checked',relative+'/setup.txt',relative+'/stars.txt',str(expected)],
                     directory/'solver.stdout',directory/'solver.stderr')
        output = (directory/'solver.stdout').read_text()
        error = (directory/'solver.stderr').read_text()
        match = re.search(r'FINAL stars (\d+) open (\d+) closed (\d+) viable_planes (\d+) closed_planes (\d+)',output)
        assert match and status in (0,3) and 'runtime error:' not in error
        stars,opened,closed,planes,closed_planes = map(int,match.groups())
        assert stars == expected and opened+closed == stars
        if chart.rank == 8:
            expected_plane = {(306,0):2786,(306,1):2786,(620,0):2416,(620,1):2420,
                              (2264,0):27645,(2264,1):27645}[(cid,parity)]
            assert planes == expected_plane
        if not opened:
            assert planes == closed_planes
        report.update(status='SECOND_LOW_SOLVER_CLOSED' if not opened else 'OPEN_NOT_EXCLUSION',
                      stars=stars, open=opened, closed=closed, viable_planes=planes,
                      closed_planes=closed_planes, full_depth=30, depth_cutoff=False)
    except Exception as exc:
        report.update(status='ERROR_NOT_EXCLUSION', error=repr(exc))
    report['elapsed_seconds'] = time.time()-started
    report['source_hashes'] = {p:sha(BASE/p) for p in ['residual_gram_v1.cpp','residual_gram_v1_checked',
                             'low_setup_v1.py','own_setup.py','own_local.py','star_dump_checked',
                             'geometry_own.json','layouts.tsv','run_one_low_v1.py']}
    report['evidence_hashes'] = {p.name:sha(p) for p in directory.iterdir() if p.is_file() and p.name not in ['result.json']}
    (directory/'result.json').write_text(json.dumps(report,indent=4))
    print(json.dumps(report),flush=True)
    return 0 if report['status'] == 'SECOND_LOW_SOLVER_CLOSED' else 1

if __name__ == '__main__':
    raise SystemExit(main(int(sys.argv[1]),int(sys.argv[2])))
