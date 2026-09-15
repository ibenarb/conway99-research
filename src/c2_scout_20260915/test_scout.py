"""Targeted safety/partition controls; no production proof or SAT claim."""
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
from common import sha, save, LOG_LIMIT, CNF_HASH, MAP_HASH
from prepare import prepare
from worker import classify


def run(solver):
    root=Path(tempfile.mkdtemp(prefix='c2-scout-tests-'))
    assert classify(20,['s UNSATISFIABLE'])=='UNSAT_UNCERTIFIED'
    assert classify(0,['s UNSATISFIABLE'])=='SOLVER_ERROR'
    assert classify(20,[])=='SOLVER_ERROR'
    assert classify(0,['s UNKNOWN'])=='OPEN_BUDGET'
    assert classify(10,['s SATISFIABLE','s UNSATISFIABLE'])=='SOLVER_ERROR'
    def limit():
        resource.setrlimit(resource.RLIMIT_FSIZE,(4096,4096))
    oversized=root/'oversized'
    with oversized.open('wb') as log:
        p=subprocess.run([sys.executable,'-c','import os; os.write(1,b"x"*8192); os.write(1,b"y")'],stdout=log,stderr=subprocess.DEVNULL,preexec_fn=limit)
    assert p.returncode!=0 and oversized.stat().st_size==4096
    # The worker must reject altered inputs before a solver starts.
    bad=root/'bad';bad.mkdir();inp=bad/'in.cnf';inp.write_text('p cnf 1 1\n1 0\n')
    save(bad/'job.json',{'cnf':str(inp),'cnf_sha256':'0'*64,'seed':0})
    p=subprocess.run([sys.executable,str(Path(__file__).with_name('worker.py')),str(bad/'job.json'),solver,'3',str(bad),str(os.getpid())],stderr=subprocess.DEVNULL)
    assert p.returncode!=0 and not (bad/'solver.log').exists()
    # Verify child death binding with a sleeping fake solver, without touching any campaign.
    fake=root/'fake';fake.write_text('#!/usr/bin/env python3\nimport os,time\nopen('+repr(str(root/'solver.pid'))+',"w").write(str(os.getpid()))\ntime.sleep(60)\n');fake.chmod(0o755)
    death=root/'death';death.mkdir();save(death/'job.json',{'cnf':str(inp),'cnf_sha256':sha(inp),'seed':0})
    worker=subprocess.Popen([sys.executable,str(Path(__file__).with_name('worker.py')),str(death/'job.json'),str(fake),'30',str(death),str(os.getpid())])
    try:
        for _ in range(100):
            if (root/'solver.pid').exists():break
            time.sleep(.05)
        pid=int((root/'solver.pid').read_text())
        worker.kill();worker.wait()
        for _ in range(100):
            stat=Path(f'/proc/{pid}/stat')
            if not stat.exists() or stat.read_text().split()[2]=='Z':break
            time.sleep(.05)
        else:raise AssertionError('Solver survived worker death')
    finally:
        if worker.poll() is None:worker.kill();worker.wait()
    base=root/'reference'
    subprocess.run([sys.executable,str(Path(__file__).with_name('c2_reference.py')),'--out',str(base)],check=True,stdout=subprocess.DEVNULL)
    manifest=prepare(base,root/'partitions')
    assert len(manifest['jobs'])==27 and manifest['coverage_checks']==24
    assert sha(base/'baseline.cnf')==CNF_HASH and sha(base/'variables.json')==MAP_HASH
    report={'status':'SCOUT_SAFETY_AND_PARTITION_CONTROLS_PASS','status_mismatch_controls':5,
            'file_size_limit_control':True,'changed_input_rejected':True,'worker_death_kills_solver':True,
            'reference_hashes_match':True,'coverage_checks':24,'jobs_prepared':27,
            'production_solver_runs':0,'windows_guard':'Requires real WSL/Windows setup check; not executed in Linux build environment.'}
    print(json.dumps(report));return report

if __name__=='__main__':
    run(sys.argv[1])
