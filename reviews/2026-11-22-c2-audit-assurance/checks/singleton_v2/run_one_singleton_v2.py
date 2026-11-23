from pathlib import Path
import gzip
import hashlib
import shutil
import json
import os
import re
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
import singleton_setup_v1

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main(cid):
    resource=measure()
    assert max(row['system_busy_cpu'] for row in resource['intervals'])+1<=20
    assert resource['ram_free_gib']>=10 and resource['disk_free_gib']>=35.2
    control=json.loads((BASE/'controls_result_v1.json').read_text())
    assert control['status']=='SINGLETON_CORE_CONTROLS_PASS'
    for name in ['singleton_exact_v1.cpp','singleton_exact_v1_checked']:
        assert sha(BASE/name)==control['hashes'][name]
    directory=BASE/'jobs'/str(cid)
    directory.mkdir(parents=True,exist_ok=False)
    started=time.time()
    record=dict(status='RUNNING',chart=cid,identity=identity(os.getpid()),started=started,resource=resource)
    (directory/'identity.json').write_text(json.dumps(record,indent=4))
    try:
        singleton_setup_v1.write_setup(cid,directory/'setup.txt')
        record['setup']=json.loads((directory/'setup.txt.json').read_text())
        relative=(directory/'setup.txt').relative_to(BASE).as_posix()
        command=['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),
                 '--exec','./singleton_exact_v1_checked',relative]
        with (directory/'solver.stdout').open('wb') as out,(directory/'solver.stderr').open('wb') as err:
            result=subprocess.run(command,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        output=(directory/'solver.stdout').read_text()
        error=(directory/'solver.stderr').read_text()
        match=re.search(r'FINAL chart (\d+) roots (\d+) planned (\d+) open (\d+)',output)
        assert match and int(match[1])==cid and result.returncode in (0,3)
        done,planned,opened=map(int,match.groups()[1:])
        assert planned==record['setup']['root_representatives'] and 'runtime error:' not in error
        if not opened:
            assert done==planned and result.returncode==0
        record.update(status='SECOND_SINGLETON_SOLVER_CLOSED' if not opened else 'OPEN_NOT_EXCLUSION',
                      roots_completed=done,roots_planned=planned,exit_code=result.returncode,
                      final_line=next(row for row in output.splitlines() if row.startswith('FINAL')))
    except Exception as exc:
        record.update(status='ERROR_NOT_EXCLUSION',error=repr(exc))
        raise
    finally:
        if record.get('status') == 'SECOND_SINGLETON_SOLVER_CLOSED':
            source=directory/'setup.txt'
            digest=sha(source)
            size=source.stat().st_size
            archive=directory/'setup.txt.gz'
            with source.open('rb') as inp,archive.open('xb') as raw:
                with gzip.GzipFile(filename='',mode='wb',compresslevel=6,fileobj=raw,mtime=0) as out:
                    shutil.copyfileobj(inp,out)
            checked=hashlib.sha256()
            reread=0
            with gzip.open(archive,'rb') as stream:
                while True:
                    block=stream.read(1024*1024)
                    if not block:
                        break
                    checked.update(block)
                    reread+=len(block)
            assert reread==size and checked.hexdigest()==digest
            record['lossless_input_archive']=dict(file=archive.name,uncompressed_bytes=size,
                uncompressed_sha256=digest,archive_sha256=sha(archive),full_readback=True)
            assert source.resolve().parent == directory.resolve() and source.name=='setup.txt'
            source.unlink()
        record['elapsed_seconds']=time.time()-started
        record['hashes']={p.name:sha(p) for p in directory.iterdir() if p.is_file() and p.name!='result.json'}
        (directory/'result.json').write_text(json.dumps(record,indent=4))
    print(json.dumps({k:v for k,v in record.items() if k not in ('resource','setup','hashes')}),flush=True)

if __name__=='__main__':
    os.chdir(BASE)
    main(int(sys.argv[1]))
