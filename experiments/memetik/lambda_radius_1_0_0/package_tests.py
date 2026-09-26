from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import zipfile
repo=Path.cwd()
with tempfile.TemporaryDirectory(prefix='radius-package-') as temp:
    p=Path(temp)
    with zipfile.ZipFile(repo/'releases/memetik/lambda_radius_1_0_0.zip') as z:
        assert z.testzip() is None
        z.extractall(p)
    cli=p/'lambda_radius_1_0_0/experiments/memetik/lambda_radius_1_0_0/run.py'
    run=p/'run'
    env={**os.environ, 'PYTHONNOUSERSITE':'1'}
    env.pop('WSL_DISTRO_NAME',None)
    q=subprocess.run([sys.executable,str(cli),'prepare',str(run)],env=env,capture_output=True,text=True)
    assert q.returncode==0,(q.stdout,q.stderr)
    assert json.loads((run/'ledger.json').read_text())['used']['aux']==10
    q=subprocess.run([sys.executable,str(cli),'prepare',str(run)],env=env,capture_output=True,text=True)
    assert q.returncode!=0 and 'Existing run' in q.stderr
    q=subprocess.run([sys.executable,str(cli),'launch',str(run)],env=env,capture_output=True,text=True)
    assert q.returncode!=0 and 'Production requires Windows host clock' in q.stderr,q.stderr
    assert not (run/'launcher.json').exists()
    kernel=run/'program/experiments/memetik/lambda_compare_0_2_0/kernel.py'
    kernel.write_bytes(kernel.read_bytes()+b'\n')
    q=subprocess.run([sys.executable,str(cli),'launch',str(run)],env=env,capture_output=True,text=True)
    assert q.returncode!=0 and 'SOURCE_HASH_MISMATCH' in q.stderr,q.stderr
out={'status':'PACKAGE_PASS','standalone_prepare':True,'existing_run_refused':True,'no_native_production_fallback':True,'frozen_source_tamper_refused':True,'prepare_cpu_reservation':10}
(repo/'experiments/memetik/lambda_radius_1_0_0/PACKAGE_TEST_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
