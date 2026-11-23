"""Fetch only the nine pinned public Lean dependencies, sequentially, with local resource gates."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/C2_K4_Methodenpilot_20261117'))
from c2_shared_measurement_20261118_v1 import measure
from c2_serial_admission_core_20261118_v1 import identity

def main():
    started = time.time()
    marker = BASE/'dependencies_started_v1.json'
    with marker.open('x') as out:
        json.dump(dict(identity=identity(os.getpid()),time=started),out,indent=4)
    project = BASE/'c3formal'
    manifest_bytes = (project/'lake-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    report = dict(status='RUNNING',manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                  no_cloud_compute=True,packages=[])
    for package in manifest['packages']:
        resource = measure()
        while (max(row['system_busy_cpu'] for row in resource['intervals'])+1 > 20
               or resource['ram_free_gib'] < 10 or resource['disk_free_gib'] < 36):
            report.update(status='RESOURCE_WAIT',resource=resource)
            (BASE/'dependencies_progress_v1.json').write_text(json.dumps(report,indent=4))
            time.sleep(15)
            resource = measure()
        target = project/'.lake/packages'/package['name']
        assert not target.exists(), f'Existing dependency {target}: inspect before resuming'
        target.mkdir(parents=True)
        commands = [
            ['git','init','--quiet',str(target)],
            ['git','-C',str(target),'remote','add','origin',package['url']],
            ['git','-c','pack.threads=1','-C',str(target),'fetch','--depth=1','origin',package['rev']],
            ['git','-C',str(target),'checkout','--quiet','--detach','FETCH_HEAD']
        ]
        with (BASE/f'dependency_{package["name"]}.log').open('wb') as log:
            for command in commands:
                result = subprocess.run(command,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode:
                    raise RuntimeError(dict(package=package['name'],command=command[:3],code=result.returncode))
        result = subprocess.run(['git','-C',str(target),'rev-parse','HEAD'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode == 0 and result.stdout.strip() == package['rev']
        tree = subprocess.run(['git','-C',str(target),'rev-parse','HEAD^{tree}'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        size = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
        report['packages'].append(dict(name=package['name'],url=package['url'],revision=package['rev'],
                                      tree=tree.stdout.strip(),bytes=size,resource_before=resource))
        report['status'] = 'RUNNING'
        (BASE/'dependencies_progress_v1.json').write_text(json.dumps(report,indent=4))
    assert (project/'lake-manifest.json').read_bytes() == manifest_bytes
    report.update(status='ALL_NINE_PINNED_DEPENDENCIES_READY',elapsed_seconds=time.time()-started)
    (BASE/'dependencies_result_v1.json').write_text(json.dumps(report,indent=4))
    print(json.dumps(report),flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        (BASE/'dependencies_error_v1.json').write_text(json.dumps(dict(status='SETUP_ERROR_NO_PROOF_VERDICT',error=repr(exc),time=time.time()),indent=4))
        raise
