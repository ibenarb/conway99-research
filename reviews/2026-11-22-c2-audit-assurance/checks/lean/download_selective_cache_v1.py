"""Download only the 2209 canonical cache files identified by the pinned Lean planner.
No extraction, proof build, CI action or remote write occurs in this stage.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.request
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
probe=json.loads((BASE/'cache_size_probe_result_v1.json').read_text())
assert probe['available']==probe['planned']==2209
assert probe['compressed_bytes']==140592860
started=time.time()
with (BASE/'cache_download_identity_v1.json').open('x') as out:
    json.dump(dict(identity=identity(os.getpid()),started=started),out,indent=4)
while True:
    resource=measure()
    allowed=(max(x['system_busy_cpu'] for x in resource['intervals'])+1<=20
             and resource['ram_free_gib']>=8
             and resource['disk_free_gib']-probe['compressed_bytes']/2**30>=35.5)
    if allowed:
        break
    (BASE/'cache_download_progress_v1.json').write_text(json.dumps(
        dict(status='WAITING_FOR_RESOURCES',resource=resource,updated=time.time()),indent=4))
    time.sleep(10)
destination=BASE/'mathlib_cache'
destination.mkdir(exist_ok=True)
for row in probe['records']:
    assert re.fullmatch(r'[0-9a-f]{16}\.ltar',row['file'])
    assert row['url'] in [f'https://cache.mathlib.org/{c}/f/{row["file"]}' for c in ('mathlib4-master','mathlib4')]
    assert not (destination/row['file']).exists()
def fetch(row):
    result={k:row[k] for k in ('module','file','url','bytes','etag')}
    path=destination/row['file']
    partial=destination/(row['file']+'.download_v1')
    try:
        assert shutil.disk_usage(BASE).free>=int(35.4*2**30)+row['bytes']+64*1024**2
        request=urllib.request.Request(row['url'],headers={'User-Agent':'Conway99-local-assurance/1.0'})
        digest=hashlib.sha256()
        count=0
        with urllib.request.urlopen(request) as response,partial.open('xb') as out:
            assert response.geturl().startswith('https://')
            assert int(response.headers['Content-Length'])==row['bytes']
            if row['etag']:
                assert response.headers.get('ETag')==row['etag']
            while True:
                block=response.read(1024*1024)
                if not block:
                    break
                count+=len(block)
                assert count<=row['bytes']
                digest.update(block)
                out.write(block)
        assert count==row['bytes']
        reread=partial.read_bytes()
        assert hashlib.sha256(reread).hexdigest()==digest.hexdigest()
        assert reread[:4] in (b'LTAR',b'LTR2',b'LTR3')
        assert not path.exists()
        partial.rename(path)
        result.update(status='DOWNLOADED_READBACK_VERIFIED',sha256=digest.hexdigest())
    except Exception as error:
        result.update(status='DOWNLOAD_ERROR_NOT_PROOF_VERDICT',error=repr(error))
    return result
answers=[]
with ThreadPoolExecutor(max_workers=8) as pool:
    futures=[pool.submit(fetch,row) for row in probe['records']]
    for future in as_completed(futures):
        answers.append(future.result())
        if len(answers)%100==0:
            progress=dict(status='DOWNLOADING',completed=len(answers),
                verified=sum(x['status']=='DOWNLOADED_READBACK_VERIFIED' for x in answers),
                elapsed_seconds=time.time()-started,free_disk_gib=shutil.disk_usage(BASE).free/2**30)
            (BASE/'cache_download_progress_v1.json').write_text(json.dumps(progress,indent=4))
            print(json.dumps(progress),flush=True)
answers.sort(key=lambda x:x['module'])
ok=all(x['status']=='DOWNLOADED_READBACK_VERIFIED' for x in answers)
report=dict(status='ALL_SELECTIVE_CACHE_FILES_DOWNLOADED' if ok else 'CACHE_DOWNLOAD_ERRORS',
            planned=2209,verified=sum(x['status']=='DOWNLOADED_READBACK_VERIFIED' for x in answers),
            bytes=probe['compressed_bytes'],records=answers,resource_at_start=resource,
            elapsed_seconds=time.time()-started,extracted=False,fresh_proof_build=False,
            free_disk_gib=shutil.disk_usage(BASE).free/2**30)
(BASE/'cache_download_result_v1.json').write_text(json.dumps(report,indent=4))
print(json.dumps({k:v for k,v in report.items() if k not in ('records','resource_at_start')}),flush=True)
