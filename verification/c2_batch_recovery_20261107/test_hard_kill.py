"""Real SIGKILL and interrupted SAT-stop tests; synthetic fixtures only."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time
import batch_recovery as b
import test_recovery as t

P=Path(__file__).resolve().parent
O=P/'hard_controls'


def worker(root, phase):
    def hook(where,index):
        if where==phase:
            os.kill(os.getpid(),signal.SIGKILL)
    b.run(root,sensor=t.FixtureSensor(),hook=hook)


def main():
    O.mkdir(exist_ok=False)
    # Keep the fixtures separate; use already generated complete fixture files.
    fixtures=t.OUT
    results=[]
    for phase in ('search_closed','committed'):
        root=O/('mixed_'+phase)
        sources=dict(zip(b.NAMES,[fixtures/'mixed.txt',fixtures/'mixed.action',P/'batch-engine',P/'batch-verify']))
        b.initialise(root,'hard-kill-mixed-fixture',3,[0,1,2],sources)
        process=subprocess.run([sys.executable,__file__,'worker',str(root),phase],timeout=20)
        assert process.returncode==-signal.SIGKILL,process.returncode
        state=b.run(root,sensor=t.FixtureSensor())
        assert state['state']=='STOPPED' and state['verified']==[0],state
        assert state['stop']['reason']=='SAT_VALIDATED_AGAINST_SUPPLIED_MATRIX'
        assert not list((root/'attempts').glob('*/boundary_2.proof'))
        assert len(list((root/'attempts').glob('*/search_intent.json')))==1
        results.append('SIGKILL_mixed_'+phase)
    # Actual live native-child lifetime test, using a deliberately sleeping fixture producer.
    sleeper=O/'sleep-engine'
    sleeper.write_text('#!/usr/bin/python3\nimport os,sys,time\nfrom pathlib import Path\nPath(sys.argv[3],"child.pid").write_text(str(os.getpid()))\ntime.sleep(60)\n')
    sleeper.chmod(0o755)
    root=O/'live_child'
    sources=dict(zip(b.NAMES,[fixtures/'unsat.txt',fixtures/'unsat.action',sleeper,P/'batch-verify']))
    b.initialise(root,'live-child-fixture',3,[0,1,2],sources)
    process=subprocess.Popen([sys.executable,__file__,'worker',str(root),'never'])
    deadline=time.monotonic()+10
    pidfiles=[]
    while time.monotonic()<deadline:
        pidfiles=list((root/'attempts').glob('*/child.pid'))
        if pidfiles:
            break
        time.sleep(0.02)
    assert pidfiles,'Child did not start'
    child=int(pidfiles[0].read_text())
    os.kill(process.pid,signal.SIGKILL)
    assert process.wait(timeout=5)==-signal.SIGKILL
    deadline=time.monotonic()+5
    terminated=False
    while time.monotonic()<deadline:
        stat=Path(f'/proc/{child}/stat')
        if not stat.exists() or stat.read_text().split(') ')[1].split()[0]=='Z':
            terminated=True
            break
        time.sleep(0.02)
    assert terminated,'Orphan producer remains running'
    t.rejected(lambda:b.run(root,sensor=t.FixtureSensor()),'UNRESOLVED_SEARCH')
    assert not list((root/'receipts').glob('*.json'))
    results.append('SIGKILL_parent_terminates_live_child_and_blocks_restart')
    answer=dict(status='PASS',tests=results,child_pid=child,child_running_after_parent_kill=False,
                scope='Actual process kills, not hardware power-loss simulation; fixture sensor only')
    (P/'HARD_KILL_CONTROLS.json').write_text(json.dumps(answer,indent=4)+'\n')
    print(json.dumps(answer,indent=4))


if __name__=='__main__':
    if len(sys.argv)>1:
        worker(Path(sys.argv[2]),sys.argv[3])
    else:
        main()
