from pathlib import Path
import json,shutil,sys
import batch_recovery as b
import test_recovery as t
P=Path(__file__).resolve().parent;O=P/'binding_controls';O.mkdir()
answers=[]
for kind in ['case','masks','format','blocks']:
    r=O/kind;shutil.copytree(t.OUT/'normal',r)
    if kind=='blocks':
        with (r/'blocks.txt').open('ab') as f:f.write(b'X')
    else:
        p=r/'receipts/00000.json';v=b.read(p)
        v[kind]=1005 if kind=='case' else [0,0] if kind=='masks' else 'C2S2'
        p.write_text(json.dumps(v))
    t.rejected(lambda:b.run(r,sensor=t.FixtureSensor()))
    answers.append('reject_'+kind)
# A genuine first native decision cannot make a crashed verifier batch committable.
wrapper=O/'prefix-checker'
wrapper.write_text('#!/usr/bin/python3\nimport subprocess,sys\nargs=sys.argv[1:]\nargs[1]=args[1].split(",")[0]\nsubprocess.run(['+repr(str(P/'batch-verify'))+']+args,check=True)\nsys.exit(9)\n')
wrapper.chmod(0o755)
r=O/'verifier_partial'
sources=dict(zip(b.NAMES,[t.OUT/'unsat.txt',t.OUT/'unsat.action',P/'batch-engine',wrapper,t.OUT/'unsat.blocks']))
b.initialise(r,'partial-checker',3,[0,1,2],sources)
t.rejected(lambda:b.run(r,sensor=t.FixtureSensor()),'replay rejected')
assert list(r.glob('attempts/*/snapshot/boundary_0.verified.json'))
assert not list((r/'receipts').glob('*.json'))
answers.append('first_native_receipt_then_verifier_failure_commits_nothing')
# Stop at a committed regular batch, then resume the same immutable contract.
r=O/'regular_resume'
sources['batch-verify']=P/'batch-verify'
b.initialise(r,'regular-checkpoint',3,[0,1,2],sources)
first=b.run(r,chunk_size=1,batch_limit=1,sensor=t.FixtureSensor())
assert first['state']=='INCOMPLETE_CHECKPOINT' and first['verified']==[0]
prior=(r/'receipts/00000.json').read_bytes()
assert not (r/'COMPLETE.json').exists()
assert b.run(r,chunk_size=1,sensor=t.FixtureSensor())['tasks']==[0,1,2]
assert (r/'receipts/00000.json').read_bytes()==prior
answers.append('regular_checkpoint_resume_preserves_first_receipt')
result=dict(status='PASS',tests=answers,controller_sha256=b.digest(P/'batch_recovery.py'),scope='Synthetic binding and native partial replay controls')
(P/'BINDING_CONTROLS.json').write_text(json.dumps(result,indent=4)+'\n');print(json.dumps(result))
