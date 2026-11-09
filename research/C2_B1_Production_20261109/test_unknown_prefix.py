"""UNSAT/UNKNOWN/open, including interrupted publication; synthetic inputs."""
from pathlib import Path
import json
import signal
import subprocess
import sys
import batch_recovery as b
import test_recovery as t
P=Path(__file__).resolve().parent
O=P/'unknown_prefix_controls_v2';O.mkdir(exist_ok=False)
wrapper=O/'prefix-engine'
wrapper.write_text('''#!/usr/bin/python3
from pathlib import Path
import subprocess,sys
engine=Path(__file__).resolve().parents[2]/'batch-engine'
model,tasks,out,seconds,action,blocks=sys.argv[1:]
ids=tasks.split(',')
a=subprocess.run([str(engine),model,ids[0],out,'5',action,blocks])
if a.returncode!=20:sys.exit(1)
b=subprocess.run([str(engine),model,ids[1],out,'0',action,blocks])
sys.exit(b.returncode)
''')
wrapper.chmod(0o755)
results=[]
for phase in ['normal','search_closed','committed']:
    root=O/phase
    sources=dict(zip(b.NAMES,[t.OUT/'unsat.txt',t.OUT/'unsat.action',wrapper,P/'batch-verify',t.OUT/'unsat.blocks']))
    b.initialise(root,'UNSAT_UNKNOWN_open_fixture',3,[0,1,2],sources)
    if phase!='normal':
        r=subprocess.run([sys.executable,str(P/'test_hard_kill.py'),'worker',str(root),phase],timeout=20)
        assert r.returncode==-signal.SIGKILL,r.returncode
    state=b.run(root,sensor=t.FixtureSensor())
    assert state['state']=='STOPPED' and state['verified']==[0],state
    assert state['stop']['reason']=='UNKNOWN' and state['stop']['boundary']==1
    assert not list((root/'attempts').glob('*/boundary_2.proof'))
    assert b.run(root,sensor=t.FixtureSensor())['verified']==[0]
    assert len(list((root/'attempts').glob('*/search_intent.json')))==1
    results.append(phase)
answer=dict(status='PASS',UNSAT_UNKNOWN_open=results,verified_boundary=0,unknown_boundary=1,unstarted_boundary=2,scope='Synthetic wrapper invokes real searcher with a zero budget for second task')
(P/'UNKNOWN_PREFIX_CONTROLS.json').write_text(json.dumps(answer,indent=4)+'\n')
print(json.dumps(answer,indent=4))
