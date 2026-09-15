"""Build a pinned solver and prepare/verify inputs; never launch research jobs."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from common import ROOT, SOLVER_COMMIT, REF_HASH, CNF_HASH, MAP_HASH, save, sha, VERSION
from prepare import prepare
from windows_guard import host_probe, Guard
HERE=Path(__file__).resolve().parent


def controls(solver, directory):
    from worker import classify
    for text, code, status in [('p cnf 1 1\n1 0\n',10,'SAT_PENDING_GRAPH_CHECK'),
                                ('p cnf 1 2\n1 0\n-1 0\n',20,'UNSAT_UNCERTIFIED')]:
        cnf=directory/f'{code}.cnf'
        cnf.write_text(text)
        result=subprocess.run([str(solver),'-t','10',str(cnf)],capture_output=True,timeout=20)
        assert result.returncode==code and classify(code,result.stdout.decode().splitlines())==status
    small=directory/'small'
    subprocess.run([sys.executable,str(HERE/'c2_reference.py'),'--k','4','--out',str(small)],check=True,stdout=subprocess.DEVNULL)
    job={'id':'small_graph_control','group':'control','seed':0,'cnf':str(small/'baseline.cnf'),
         'cnf_sha256':sha(small/'baseline.cnf'),'k':4,'assumptions':[]}
    save(directory/'job.json',job)
    subprocess.run([sys.executable,str(HERE/'worker.py'),str(directory/'job.json'),str(solver),'10',str(directory),str(os.getpid())],check=True,timeout=25)
    assert json.loads((directory/'result.json').read_text())['status']=='GRAPH_VERIFIED'
    assert not list(directory.rglob('*.lrat')) and not list(directory.rglob('*.drat'))
    result={'status':'SOLVER_AND_SMALL_GRAPH_CONTROLS_PASS','tiny_sat':True,'tiny_unsat':True,
            'nine_vertex_graph_reconstructed':True,'production_solver_runs':0,'proof_files_created':0}
    save(directory/'controls.json',result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    args=parser.parse_args()
    ROOT.mkdir(parents=True,exist_ok=True)
    if sha(HERE/'c2_reference.py')!=REF_HASH:
        raise RuntimeError('Reference encoder hash mismatch')
    host=host_probe()
    if host['free_bytes']<50*1024**3 or shutil.disk_usage(ROOT).free<25*1024**3:
        raise RuntimeError('Insufficient initial disk reserve')
    guard=Guard(ROOT)
    try:
        guard.beat()
        guard.read()
    finally:
        guard.close()
    print('SETUP 1/3: pinned CaDiCaL build (usually a few minutes)',flush=True)
    src=ROOT/'cadical_source'
    log=ROOT/'build.log'
    with log.open('ab') as stream:
        if not src.exists():
            subprocess.run(['git','clone','--depth','1','--branch','rel-2.2.1',
                            'https://github.com/arminbiere/cadical.git',str(src)],check=True,stdout=stream,stderr=subprocess.STDOUT)
        commit=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
        if commit!=SOLVER_COMMIT or subprocess.check_output(['git','-C',str(src),'status','--porcelain','--untracked-files=no'],text=True).strip():
            raise RuntimeError('Solver source identity/cleanliness mismatch')
        subprocess.run(['./configure'],cwd=src,check=True,stdout=stream,stderr=subprocess.STDOUT)
        subprocess.run(['make','-j4'],cwd=src,check=True,stdout=stream,stderr=subprocess.STDOUT)
    solver=src/'build/cadical'
    version=subprocess.check_output([str(solver),'--version'],text=True).strip()
    if version!='2.2.1':
        raise RuntimeError('Unexpected solver version')
    print('SETUP 2/3: tiny solver and reconstructed graph controls',flush=True)
    control_dir=Path(tempfile.mkdtemp(prefix='controls_',dir=ROOT))
    checked=controls(solver,control_dir)
    print('SETUP 3/3: reference CNF and three exhaustive partitions',flush=True)
    base=ROOT/'reference'
    if not base.exists():
        subprocess.run([sys.executable,str(HERE/'c2_reference.py'),'--k','14','--out',str(base)],check=True,stdout=subprocess.DEVNULL)
    if sha(base/'baseline.cnf')!=CNF_HASH or sha(base/'variables.json')!=MAP_HASH:
        raise RuntimeError('Reference reproduction failed')
    # This known duplicate adds no information; retain only the baseline bytes.
    duplicate=base/'matching.cnf'
    if duplicate.exists() and sha(duplicate)==CNF_HASH:
        duplicate.unlink()
    parts=ROOT/'partitions'
    if not parts.exists():
        manifest=prepare(base,parts)
    else:
        manifest=json.loads((parts/'manifest.json').read_text())
        if manifest['baseline_sha256']!=CNF_HASH or len(manifest['jobs'])!=27:
            raise RuntimeError('Existing partition manifest mismatch')
        for job in manifest['jobs']:
            if sha(job['cnf'])!=job['cnf_sha256']:
                raise RuntimeError('Existing partition CNF mismatch')
    result={'status':'C2_SCOUT_PREPARED_NOT_LAUNCHED','version':VERSION,'source':str(HERE),
       'solver':str(solver),'solver_sha256':sha(solver),'solver_source_commit':SOLVER_COMMIT,
       'solver_version':version,'baseline_sha256':CNF_HASH,'mapping_sha256':MAP_HASH,
       'controls':checked,'jobs':27,'coverage_checks':24,'production_solver_runs':0,
       'host_probe':host,'next_command':f'python3 {HERE}/scout.py'}
    save(ROOT/'setup.json',result)
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    main()
