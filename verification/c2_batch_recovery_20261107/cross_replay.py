from pathlib import Path
import json
import batch_recovery as b
from resource_sensor import Sensor
P=Path(__file__).resolve().parent
O=P/'cross_replay'
O.mkdir(exist_ok=False)
checker=P.parent/'C2_Rest55_20261104/case_0078'
contract=b.read(checker/'execution_contract.json')
assert b.digest(checker/'row-verify')==contract['files']['row-verify']
expected=b.digest(checker/'row-verify')
seen=set();results=[];sensor=Sensor(O)
for result in b.read(P/'REAL_RESULTS.json'):
    if result['variant']!='batch':continue
    root=P/'real_pilot'/f"c{result['case']}_{result['pattern']}_batch"
    own,context=b.check_contract(root)
    receipts=b.load_receipts(root,own,context)
    for i in result['tasks']:
        key=(result['case'],i)
        if key in seen:continue
        seen.add(key)
        item=receipts[i]
        proof=root/'attempts'/item['attempt']/'snapshot'/f'boundary_{i}.proof'
        log=O/f'case{key[0]}_boundary{i}.log'
        replay=b.stage([checker/'row-verify',root/'model.txt',i,proof,root/'action.txt'],log,sensor)
        assert replay['returncode']==0,replay
        assert b.digest(proof)==item['proof_sha256']
        assert b.digest(checker/'row-verify')==expected
        results.append(dict(case=key[0],boundary=i,proof_sha256=item['proof_sha256'],
                            replay=replay,verifier_sha256=expected,status='PASS'))
assert len(results)==8
answer=dict(status='PASS',distinct_boundaries=8,independent_single_verifier=expected,
            results=results,scope='Cross replay of every distinct real pilot proof; not global exclusion')
(P/'CROSS_REPLAY.json').write_text(json.dumps(answer,indent=4)+'\n')
print(json.dumps(dict(status='PASS',distinct_boundaries=8)))
