"""Audit completion-report inventory against the pinned plan; no proof replay."""
import json,hashlib,re,statistics,sys
from pathlib import Path
base=Path(__file__).resolve().parents[2]
path=Path(sys.argv[1]);raw=path.read_bytes();r=json.loads(raw)
p=json.loads((base/'results/research_20260912/k66/v4_09333_plan.json').read_text())
assert r['status']=='MODULAR_REDUCED_ROOT_UNSAT_VERIFIED' and r['root']==p['root']
assert r['base_cnf_sha256']==p['base_cnf_sha256']
assert set(r['leaves'])=={x['id'] for x in p['leaves']}
assert set(r['dependencies']['bridges'])=={x['id'] for x in p['bridges']}
c=r['dependencies']['composition'];assert c['coverage_clauses_match'] is True
assert c['leaf_obligations']==3076 and c['bridge_obligations']==112
assert r['dependencies']['coverage']['proof_sha256']==p['coverage_proof_sha256']
for record in list(r['leaves'].values())+list(r['dependencies']['bridges'].values())+[r['dependencies']['coverage']]:
    for field in ('cnf_sha256','proof_sha256'):assert re.fullmatch('[0-9a-f]{64}',record[field])
leaves=list(r['leaves'].values());new=[x for x in leaves if not x['reused_prior_leaf']]
times=[x['job_wall_including_storage'] for x in new]
assert all(isinstance(t,(int,float)) and t>=0 for t in times)
out={'status':'PASS_REPORT_INVENTORY_AND_PLAN_MATCH','reported_status':r['status'],'root':r['root'],'input_sha256':hashlib.sha256(raw).hexdigest(),'input_bytes':len(raw),'base_cnf_sha256':r['base_cnf_sha256'],'coverage_proof_sha256':r['dependencies']['coverage']['proof_sha256'],'leaf_count':len(leaves),'bridge_count':len(r['dependencies']['bridges']),'new_leaves':len(new),'reused_leaves':len(leaves)-len(new),'sum_job_wall_hours':sum(times)/3600,'median_job_wall_seconds':statistics.median(times),'max_job_wall_seconds':max(times),'uncompressed_leaf_proof_GiB':sum(x['proof_bytes'] for x in leaves)/2**30,'scope':'Report inventory, IDs and recorded hashes matched against earlier plan. Proof files and checker logs were not uploaded and were not rechecked here. Sum of recorded job durations is not measured end-to-end runtime.'}
(base/'results/k66_completion_20260913/audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
