"""Validate linear receipt-file reads and lock cleanup on synthetic small models."""
from pathlib import Path
import json
import batch_recovery as b
import test_recovery as t

P=Path(__file__).resolve().parent
O=P/'scale_controls'
O.mkdir(exist_ok=False)
g=[[2,0,1,1],[0,2,1,1],[1,1,2,0],[1,1,0,2]]
model=O/'model.txt'
count=96
t.model(model,4,g,[[3,12],[3,12],[3],[3]],[(3,12)]*count)
action=O/'action.txt';action.write_text('1 0 2 3')
sources=dict(zip(b.NAMES,[model,action,P/'batch-engine',P/'batch-verify',model.with_suffix('.blocks')]))
root=O/'run'
b.initialise(root,'96-boundary-small-fixture',count,list(range(count)),sources)
original=b.load_receipts
calls=[]

def traced(root,contract,context,selected=None):
    result=original(root,contract,context,selected)
    calls.append(dict(kind='full' if selected is None else 'incremental',records=len(result)))
    return result

b.load_receipts=traced
state=b.run(root,chunk_size=8,sensor=t.FixtureSensor())
assert state['state']=='RESEARCH_SUBSET_VERIFIED'
first=list(calls)
assert sum(x['records'] for x in first)==2*count,first
assert [x['records'] for x in first if x['kind']=='full']==[0,count]
assert len([x for x in first if x['kind']=='incremental'])==12
calls.clear()
assert b.run(root,sensor=t.FixtureSensor())['tasks']==list(range(count))
assert sum(x['records'] for x in calls)==2*count,calls
assert not [x for x in calls if x['kind']=='incremental' and x['records']]
# An exception opening the per-bundle lock must release the global lock.
bad=O/'bad_lock'
b.initialise(bad,'lock-fixture',count,[0],sources)
(bad/'controller.lock').mkdir()
t.rejected(lambda:b.run(bad,sensor=t.FixtureSensor()))
assert b.run(root,sensor=t.FixtureSensor())['state']=='RESEARCH_SUBSET_VERIFIED'
answer=dict(status='PASS',boundaries=count,chunk_size=8,first_run_receipt_validations=192,
            startup_full_records=0,closure_full_records=96,incremental_records=96,
            restart_receipt_validations=192,lock_open_failure_releases_global_lock=True,
            scope='Linear receipt-file validation work; not an asymptotic claim for all bookkeeping or a runtime benchmark')
(P/'SCALING_CONTROLS.json').write_text(json.dumps(answer,indent=4)+'\n')
print(json.dumps(answer,indent=4))
