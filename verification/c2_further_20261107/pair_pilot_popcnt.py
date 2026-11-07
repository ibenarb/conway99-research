from pathlib import Path
import sys,json,fcntl
P=Path(__file__).resolve().parent
B=P.parent/'C2_BatchRecoveryIncremental_20261107'
sys.path.insert(0,str(B))
import batch_recovery as b
from resource_sensor import Sensor
O=P/'pair_pilot_popcnt'
O.mkdir(exist_ok=False)
sensor=Sensor(O)
checker=P.parent/'C2_Rest55_20261104/case_0078/row-verify'
action=P.parent/'C2_ProofReplay_20261107/column_action.txt'
results=[]
with (B/'research.lock').open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    compile_result=b.stage(['g++','-O3','-mpopcnt','-std=c++17',P/'pair-engine.cpp','-o',P/'pair-engine-popcnt'],O/'compile.log',sensor)
    assert compile_result['returncode']==0,compile_result
    for case in [20,77]:
        tasks=sorted({i for row in b.read(B/'REAL_RESULTS.json') if row['case']==case for i in row['tasks']})
        model=P.parent/'C2_Rest55_20261104'/f'case_{case:04d}'/'row_input.txt'
        original=b.read(model.parent/'execution_contract.json')
        assert b.digest(model)==original['files']['row_input.txt']
        for i in tasks:
            for variant in (['base','pair'] if i%2==0 else ['pair','base']):
                folder=O/f'c{case}_{i}_{variant}'
                folder.mkdir()
                engine=B/'batch-engine' if variant=='base' else P/'pair-engine-popcnt'
                run=b.stage([engine,model,str(i),folder,'30',action],folder/'search.log',sensor)
                assert run['returncode']==20,run
                report=b.read(folder/f'boundary_{i}.json')
                proof=folder/f'boundary_{i}.proof'
                replay=b.stage([checker,model,str(i),proof,action],folder/'replay.log',sensor)
                assert replay['returncode']==0,replay
                result=dict(case=case,boundary=i,variant=variant,search=run['seconds'],replay=replay['seconds'],report=report,proof_bytes=proof.stat().st_size,proof_sha256=b.digest(proof),engine_sha256=b.digest(engine),checker_sha256=b.digest(checker),input_sha256=b.digest(model))
                results.append(result)
                (P/'PAIR_POPCNT_RESULTS.json').write_text(json.dumps(results,indent=4)+'\n')
                print(json.dumps(result),flush=True)
    totals={v:sum(r['search']+r['replay'] for r in results if r['variant']==v) for v in ['base','pair']}
    summary=dict(status='PASS',distinct_tasks=len(results)//2,totals=totals,speedup=totals['base']/totals['pair'],pair_cuts=sum(r['report'].get('pair_cuts',0) for r in results),scope='Bounded first screen, native search+unchanged replay with resource monitoring; no production or whole-case claim.')
    (P/'PAIR_POPCNT_SUMMARY.json').write_text(json.dumps(summary,indent=4)+'\n')
    print(json.dumps(summary),flush=True)
