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
sys.path.insert(0,str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
os.chdir(BASE)
resource=measure()
assert max(r['system_busy_cpu'] for r in resource['intervals'])+1 <= 20
assert resource['ram_free_gib'] >= 12 and resource['disk_free_gib'] >= 35
with (BASE/'orbit_identity.json').open('x') as f:
    json.dump({'pid':os.getpid(),'started':time.time(),'resource':resource},f,indent=4)
with (BASE/'orbits.stdout').open('wb') as fo,(BASE/'orbits.stderr').open('wb') as fe:
    r=subprocess.run(['wsl.exe','--distribution','Ubuntu-24.04','--cd',str(BASE),'--exec','./orbit_reps_checked','layouts.tsv'],stdout=fo,stderr=fe,creationflags=subprocess.CREATE_NO_WINDOW)
assert r.returncode==0
expected=json.loads((BASE/'star_counts_own.json').read_text())
rows={}
refs=ROOT/'work/C2_Referee_20261122/evidence_original/own/reps'
hashes={}
for line in (BASE/'orbits.stdout').read_text().splitlines():
    m=re.fullmatch(r'(\d+) (\d+) raw (\d+) group (\d+) orbits (\d+) images_outside_raw (\d+)',line)
    assert m
    cid,par,raw,group,count,bad=map(int,m.groups())
    assert raw==expected[f'{cid},{par}'] and bad==0 and group>0 and count>0
    name=f'{cid}.{par}.txt'
    data=(BASE/'reps'/name).read_bytes()
    assert data==(refs/name).read_bytes()
    assert len(data.splitlines())==count
    rows[f'{cid},{par}']={'raw':raw,'group':group,'orbits':count,'images_outside_raw':bad}
    hashes[name]=hashlib.sha256(data).hexdigest()
assert len(rows)==98
assert 'runtime error:' not in (BASE/'orbits.stderr').read_text()
(BASE/'orbits_result.json').write_text(json.dumps({'status':'ALL_98_ORBIT_REGENERATIONS_PASS','counts':rows,'reps_sha256':hashes,'scope':'Referee implementation replay; all raw stars regenerated and union-find representatives regenerated using the supplied previously audited group generators.'},indent=4))
print('ALL_98_ORBIT_REGENERATIONS_PASS',flush=True)
