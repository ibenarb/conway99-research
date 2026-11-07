from pathlib import Path
import sys,json,fcntl
P=Path(__file__).resolve().parent
B=P.parent/'C2_BatchRecoveryIncremental_20261107'
sys.path.insert(0,str(B))
import batch_recovery as b
from resource_sensor import Sensor
O=P/'profile_pilot';O.mkdir(exist_ok=False)
sensor=Sensor(O);results=[]
checker=P.parent/'C2_Rest55_20261104/case_0078/row-verify'
action=P.parent/'C2_ProofReplay_20261107/column_action.txt'
with (B/'research.lock').open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    compile_result=b.stage(['g++','-O3','-std=c++17',P/'profile-engine.cpp','-o',P/'profile-engine'],O/'compile.log',sensor)
    assert compile_result['returncode']==0,compile_result
    for case in [20,77]:
        tasks=sorted({i for row in b.read(B/'REAL_RESULTS.json') if row['case']==case for i in row['tasks']})
        model=P.parent/'C2_Rest55_20261104'/f'case_{case:04d}'/'row_input.txt'
        assert b.digest(model)==b.read(model.parent/'execution_contract.json')['files']['row_input.txt']
        folder=O/f'c{case}';folder.mkdir()
        search=b.stage([P/'profile-engine',model,','.join(map(str,tasks)),folder,'30',action],folder/'search.log',sensor)
        assert search['returncode']==20,search
        for i in tasks:
            proof=folder/f'boundary_{i}.proof'
            baseline=P/'pair_pilot'/f'c{case}_{i}_base'/f'boundary_{i}.proof'
            assert proof.read_bytes()==baseline.read_bytes(),'Diagnostic changed proof'
            replay=b.stage([checker,model,str(i),proof,action],folder/f'replay_{i}.log',sensor)
            assert replay['returncode']==0,replay
            result=dict(case=case,boundary=i,report=b.read(folder/f'boundary_{i}.json'),proof_sha256=b.digest(proof),baseline_byte_identical=True,replay=replay)
            results.append(result)
            print(json.dumps(result),flush=True)
        (P/'PROFILE_RESULTS.json').write_text(json.dumps(results,indent=4)+'\n')
    summary=dict(status='PASS',distinct_tasks=len(results),case_final_counters=[r for r in results if r['boundary']==max(x['boundary'] for x in results if x['case']==r['case'])],scope='Exact completed UNSAT states only; bounded diagnostics, no reuse; fixed model/action per process; incomplete children never inserted; hash collisions checked by full string equality; skipped keys and capacity limits mean no global absence claim.')
    (P/'PROFILE_SUMMARY.json').write_text(json.dumps(summary,indent=4)+'\n')
