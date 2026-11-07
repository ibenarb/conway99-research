from pathlib import Path
import sys,json,fcntl
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import run_closure as runner
from closure_gate import parse_json
O=P/'launcher_controls';O.mkdir(exist_ok=False)
checks=[]
try:parse_json(b'{"x":1,"x":2}')
except ValueError:checks.append('Duplicate JSON keys rejected')
else:raise RuntimeError('Duplicate JSON accepted')
try:runner.run(P/'bundle_20_final',O,'complete')
except RuntimeError:checks.append('Existing output rejected')
else:raise RuntimeError('Existing output accepted')
lockfile=P.parent/'C2_BatchRecoveryIncremental_20261107/research.lock'
with lockfile.open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:runner.run(P/'bundle_20_final',O/'locked','subset')
    except BlockingIOError:checks.append('Concurrent research lock rejected before output/process')
    else:raise RuntimeError('Second lock accepted')
    assert not (O/'locked').exists()
original_sensor=runner.Sensor;original_popen=runner.subprocess.Popen
class Hold:
    def __init__(self,*args):pass
    def resources(self):return {'control':'simulated resource hold'},['insufficient resources']
def forbidden(*args,**kwargs):raise AssertionError('Process must not start during resource hold')
runner.Sensor=Hold;runner.subprocess.Popen=forbidden
try:
    try:runner.run(P/'bundle_20_final',O/'hold','complete')
    except RuntimeError as error:
        assert 'RESOURCE_HOLD' in str(error)
        assert json.loads((O/'hold/RUN_FAILED.json').read_text())['case_proved_unsat'] is False
        assert not (O/'hold/audit').exists()
        checks.append('Simulated resource hold prevents launch and records no closure')
    else:raise RuntimeError('Resource hold ignored')
finally:runner.Sensor=original_sensor;runner.subprocess.Popen=original_popen
try:runner.run(P/'bundle_20_final',O/'incomplete','complete')
except RuntimeError as error:
    assert 'Audit failed' in str(error)
    assert not (O/'incomplete/audit/FINAL_AUDIT.json').exists()
    assert 'INCOMPLETE' in (O/'incomplete/audit.log').read_text()
    checks.append('Actual supervised complete mode rejects genuine partial manifest')
else:raise RuntimeError('Incomplete case accepted')
result=dict(status='PASS',checks=checks,scope='Launcher/preflight controls; resource hold alone simulated; no mathematical full-case PASS')
(P/'LAUNCHER_CONTROLS.json').write_text(json.dumps(result,indent=4)+'\n');print(json.dumps(result))
