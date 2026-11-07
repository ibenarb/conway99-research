from pathlib import Path
from copy import deepcopy
import json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from closure_gate import validate_manifest,snapshot_proof,read_json,canonical,sha,SEMANTICS,run
from mathematical_audit import load_model
R=P/'bundle_20_final';O=P/'controls_final';O.mkdir(exist_ok=False)
contract=read_json(R/'contract.json');context=sha(canonical(contract));manifest=read_json(R/'manifest.json');boundaries=load_model(R/'model.txt')[-1]
passed=[]
assert len(validate_manifest(manifest,contract,context,boundaries,False))==17
passed.append('Real 17-proof subset accepted only as subset')
def reject(label,change):
    bad=deepcopy(manifest);change(bad)
    try:validate_manifest(bad,contract,context,boundaries,False)
    except (ValueError,KeyError,TypeError):passed.append(label)
    else:raise RuntimeError('Accepted '+label)
reject('wrong manifest context',lambda x:x.update(context_sha256='0'*64))
reject('wrong manifest case',lambda x:x.update(case=77))
reject('duplicate boundary',lambda x:x['records'].append(deepcopy(x['records'][0])))
reject('wrong concrete masks',lambda x:x['records'][0].update(masks=[0,1]))
reject('wrong record case',lambda x:x['records'][0].update(case=77))
reject('wrong record context',lambda x:x['records'][0].update(context_sha256='0'*64))
reject('restricted mislabeled unrestricted',lambda x:x['records'][1].update(status='VERIFIED_BOUNDARY_UNSAT'))
reject('unrestricted mislabeled restricted',lambda x:x['records'][0].update(status='VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT'))
reject('unknown format',lambda x:x['records'][0].update(format='C2R1'))
reject('unknown encoding',lambda x:x['records'][0].update(encoding='zip'))
reject('oversize proof',lambda x:x['records'][0].update(proof_bytes=2**40))
reject('boolean index',lambda x:x['records'][0].update(boundary=False))
reject('out of range index',lambda x:x['records'][0].update(boundary=36288))
reject('duplicate proof path',lambda x:x['records'][1].update(path=x['records'][0]['path']))
reject('empty manifest',lambda x:x.update(records=[]))
for label,updates in [('wrong stored hash',{'stored_sha256':'0'*64}),('wrong raw hash',{'proof_sha256':'0'*64}),('path escape',{'path':'../outside'}),('wrong header binding',{'format':'C2B1'})]:
    record=deepcopy(manifest['records'][0]);record.update(updates)
    try:snapshot_proof(R,record,O/(label.replace(' ','_')+'.proof'))
    except (ValueError,FileNotFoundError):passed.append(label)
    else:raise RuntimeError('Accepted '+label)
try:run(R,P/'incomplete_full_audit_final','complete')
except ValueError as error:
    assert 'INCOMPLETE' in str(error)
    assert not (P/'incomplete_full_audit_final/FINAL_AUDIT.json').exists()
    assert read_json(P/'incomplete_full_audit_final/FAILED.json')['case_proved_unsat'] is False
    passed.append('Real incomplete complete-gate invocation rejects before any closure output')
else:raise RuntimeError('Closed incomplete case')
# Complete-index validation unit only; no proof or mathematics claim.
small=deepcopy(manifest);small['records']=small['records'][:3]
small_contract=deepcopy(contract);small_contract['boundary_count']=3
small_boundaries=[r['masks'] for r in small['records']]
for i,r in enumerate(small['records']):r['boundary']=i
assert len(validate_manifest(small,small_contract,context,small_boundaries,True))==3
passed.append('Complete-index helper positive unit: explicitly synthetic, NOT a case audit')
small['records'].pop()
try:validate_manifest(small,small_contract,context,small_boundaries,True)
except ValueError:passed.append('Missing final index rejected by complete-index helper')
else:raise RuntimeError('Missing final index accepted')
result=dict(status='PASS',checks=passed,global_case_closed=False,scope='Manifest/snapshot/preflight controls; no successful complete real-case closure asserted')
(P/'CONTROLS_FINAL.json').write_text(json.dumps(result,indent=4)+'\n',encoding='utf-8');print(json.dumps(result))
