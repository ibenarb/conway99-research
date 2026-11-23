"""Read-only size/availability probe of the canonical, content-keyed Mathlib cache."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity
resource=measure()
assert max(x['system_busy_cpu'] for x in resource['intervals'])+1<=20
assert resource['ram_free_gib']>=8 and resource['disk_free_gib']>=35.4
plan=(BASE/'cache_plan_v1.stdout').read_text()
assert json.loads((BASE/'cache_plan_result_v1.json').read_text())['status']=='PLAN_READY'
rows=[]
for line in plan.splitlines():
    if line.startswith('MODULE '):
        _,module,name=line.split()
        assert re.fullmatch(r'[0-9a-f]{16}\.ltar',name)
        rows.append((module,name))
assert len(rows)==2209 and len({x[0] for x in rows})==2209
started=time.time()
with (BASE/'cache_size_probe_started_v1.json').open('x') as out:
    json.dump(dict(started=started,identity=identity(os.getpid()),resource=resource,
                   plan_sha256=hashlib.sha256(plan.encode()).hexdigest()),out,indent=4)
def probe(item):
    module,name=item
    for container in ('mathlib4-master','mathlib4'):
        url=f'https://cache.mathlib.org/{container}/f/{name}'
        try:
            request=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Conway99-local-assurance/1.0'})
            with urllib.request.urlopen(request) as response:
                assert response.geturl().startswith('https://')
                length=int(response.headers['Content-Length'])
                assert length>0
                return dict(module=module,file=name,url=url,final_url=response.geturl(),bytes=length,
                            etag=response.headers.get('ETag'),status='AVAILABLE')
        except urllib.error.HTTPError as error:
            if error.code==404:
                continue
            return dict(module=module,file=name,status='HTTP_ERROR',error=str(error))
        except Exception as error:
            return dict(module=module,file=name,status='PROBE_ERROR',error=repr(error))
    return dict(module=module,file=name,status='MISSING_FROM_CANONICAL_CACHE')
answers=[]
with ThreadPoolExecutor(max_workers=8) as pool:
    futures=[pool.submit(probe,item) for item in rows]
    for future in as_completed(futures):
        answers.append(future.result())
        if len(answers)%100==0:
            print(json.dumps(dict(completed=len(answers),available=sum(x['status']=='AVAILABLE' for x in answers),
                                 elapsed=time.time()-started)),flush=True)
answers.sort(key=lambda x:x['module'])
result=dict(status='CACHE_SIZE_PROBE_COMPLETE',planned=2209,
            available=sum(x['status']=='AVAILABLE' for x in answers),
            compressed_bytes=sum(x.get('bytes',0) for x in answers),elapsed_seconds=time.time()-started,
            records=answers,downloads_performed=False)
(BASE/'cache_size_probe_result_v1.json').write_text(json.dumps(result,indent=4))
print(json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)
