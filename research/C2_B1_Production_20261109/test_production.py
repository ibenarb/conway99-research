from pathlib import Path
import json,shutil
import production as p
import batch_recovery as b
P=p.P;root=P/'case_1005';out=P/'production_controls';out.mkdir()
answers=[]
def reject(fn,needle):
    try:fn()
    except Exception as e:
        assert needle in str(e),(needle,str(e))
    else:raise AssertionError('Accepted invalid data: '+needle)
# Closure copy recovery preserves evidence and refuses conflicting existing bytes.
x=out/'proof.gz';p.copy_once(x,b'abc');p.copy_once(x,b'abc');assert x.read_bytes()==b'abc'
reject(lambda:p.copy_once(x,b'xyz'),'Conflicting preserved')
assert x.read_bytes()==b'abc';answers.append('idempotent_partial_closure_copy_conflict_rejected')
link=out/'link';link.symlink_to(x)
reject(lambda:p.copy_once(link,b'abc'),'Conflicting preserved');answers.append('closure_symlink_rejected')
# Exact mandatory seal set: an empty hash dictionary is never sufficient.
f=P/'seal_empty_fixture';f.mkdir();b.write(f/'SEAL.json',dict(schema='C2B1_PRODUCTION_SEAL_V1',files={}))
reject(lambda:p.check_seal(f),'Incomplete seal file set');answers.append('empty_seal_rejected')
# Running root is explicitly confined; wrong destination cannot acquire a campaign.
reject(lambda:p.run(out/'not_a_direct_case','production'),'direct child');answers.append('wrong_production_root_rejected')
# Direct final-audit admission guard rejects a merely structural audit.
final=out/'incomplete_final';(final/'audit').mkdir(parents=True)
b.write(final/'audit/FINAL_AUDIT.json',dict(status='NONCLOSING_STRUCTURE',case_proved_unsat=False,remaining=9072))
reject(lambda:p.archive(out,final),'No full case proof');answers.append('archive_rejects_nonclosing_structure')
result=dict(status='PASS',tests=answers,source_hashes={n:b.digest(P/n) for n in p.SOURCES},scope='Production helper controls; full sealed-context controls are added after pilot and seal construction')
b.write(P/'PRODUCTION_CONTROLS.json',result)
print(json.dumps(result))
