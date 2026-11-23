"""Unpack each pinned cache archive into existing tmpfs, hash/count bytes, remove only scratch copies.
The original compressed archives and this complete inventory are retained on disk.
No proof build or check is performed.
"""
from pathlib import Path
import hashlib
import json
import os
import resource
import shutil
import subprocess
import time

BASE=Path(__file__).resolve().parent
download=json.loads((BASE/'cache_download_result_v1.json').read_text())
assert download['status']=='ALL_SELECTIVE_CACHE_FILES_DOWNLOADED'
ram=Path('/dev/shm')
assert ram.is_dir() and shutil.disk_usage(ram).free>2*2**30
scratch=ram/f'conway99_cache_preflight_{os.getpid()}'
scratch.mkdir()
root=scratch.resolve()
assert root.parent==ram.resolve() and root.name.startswith('conway99_cache_preflight_')
binary=BASE/'toolchain/lean-4.35.0-rc2-linux/bin/leantar'
started=time.time()
def cap_memory():
    resource.setrlimit(resource.RLIMIT_AS,(2*2**30,2*2**30))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        while True:
            block=stream.read(1024*1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()
records=[]
try:
    for item in download['records']:
        source=BASE/'mathlib_cache'/item['file']
        assert sha(source)==item['sha256']
        current=scratch/source.stem
        current.mkdir()
        assert current.resolve().parent==root
        result=subprocess.run([str(binary),'--jobs','1','-C',str(current),'-x',str(source)],
                              capture_output=True,text=True,preexec_fn=cap_memory)
        if result.returncode!=0:
            raise RuntimeError(dict(file=item['file'],exit_code=result.returncode,stderr=result.stderr))
        files=[]
        for path in sorted(current.rglob('*')):
            if path.is_file():
                resolved=path.resolve()
                assert not path.is_symlink() and resolved.is_relative_to(current.resolve())
                files.append(dict(path=path.relative_to(current).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
        total=sum(x['bytes'] for x in files)
        assert 0<total<2**30
        records.append(dict(module=item['module'],archive=item['file'],archive_sha256=item['sha256'],
                            expanded_bytes=total,files=files))
        assert current.resolve().parent==root
        shutil.rmtree(current)
        if len(records)%100==0:
            progress=dict(status='PREFLIGHT_RUNNING',completed=len(records),
                          expanded_bytes=sum(x['expanded_bytes'] for x in records),
                          elapsed_seconds=time.time()-started,scratch=str(scratch))
            (BASE/'cache_expansion_progress_v1.json').write_text(json.dumps(progress,indent=4))
            print(json.dumps(progress),flush=True)
    report=dict(status='ALL_ARCHIVES_EXPANDED_AND_HASHED_IN_RAM',planned=2209,completed=len(records),
                expanded_bytes=sum(x['expanded_bytes'] for x in records),
                largest_archive_expansion=max(x['expanded_bytes'] for x in records),
                records=records,elapsed_seconds=time.time()-started,proof_build=False,
                build_tree_modified=False,source_archives_preserved=True)
    (BASE/'cache_expansion_result_v1.json').write_text(json.dumps(report,indent=4))
    assert scratch.resolve()==root and not any(scratch.iterdir())
    scratch.rmdir()
    print(json.dumps({k:v for k,v in report.items() if k!='records'}),flush=True)
except Exception as error:
    (BASE/'cache_expansion_error_v1.json').write_text(json.dumps(
        dict(status='PREFLIGHT_ERROR_NOT_PROOF_VERDICT',error=repr(error),completed=len(records),
             scratch=str(scratch),records=records),indent=4))
    raise
