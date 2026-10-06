import json,sqlite3,hashlib,shutil,tarfile,sys
from pathlib import Path
base=Path('/workspace/scratch/17a703e7ce35');source=base/'repo/experiments/memetik/root8105_review_followup_1_0_0';dest=base/'repo/docs/augmentation/root8105_review_followup_20261006'
sys.path.insert(0,str(source))
from runtime import digest
from census import checked_payload
from tree_probe import summarize
records=[]
for name in ['review_lemma_run','review_tree_calibration']:
 p=base/name;con=sqlite3.connect('file:'+str(p/'run.sqlite')+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
 summary=json.loads((p/'summary.json').read_text());manifest=json.loads((p/'manifest.json').read_text())
 rows=con.execute('select root,payload,digest from results').fetchall()
 for r in rows:
  parsed=json.loads(r['payload']);assert digest(parsed)==r['digest'];assert parsed['state']=='COMPLETE'
 if name=='review_lemma_run':
  assert all(r['state']=='DONE' for r in con.execute('select state from roots'))
  files=list((p/'attempts').glob('*.predictions.*.json'));assert len(files)==48
  predictions={}
  for f in files:
   d=json.loads(f.read_text());predictions[d['root'],d['target']]=d['states']
  for r in rows:
   if r['root']==0:continue
   for key,t in json.loads(r['payload'])['counts'].items():
    pred=predictions[r['root'],int(key)];assert t['prediction_digest']==digest(pred)
    for c,e in zip(t['cases'],pred):
     assert c['row']==e['row'] and c['rank']==e['rank'];assert all(v['pass']==e['prediction'][n] for n,v in c['variants'].items())
  assert summary['states']==3072
  status='PASS_CLOSED_LEDGER'
  count=len(rows)
 else:
  # Preserve stale SQLite verbatim. Reconstruct an ANALYSIS EXPORT, never a resumable ledger.
  verified=[]
  accepted={r['root']:json.loads(r['payload']) for r in rows}
  staging=base/'verified_tree_staging';staging.mkdir(exist_ok=True)
  for f in sorted((p/'attempts').glob('*.input.json')):
   spec=json.loads(f.read_text());output=f.with_name(f.name.replace('.input.json','.output.json'))
   if spec['root']['id'] in accepted:
    output=staging/(str(spec['root']['id'])+'.json')
    output.write_text(json.dumps(accepted[spec['root']['id']]))
   result=checked_payload(output,spec)
   assert result['state']=='COMPLETE' and result['code_hash']==manifest['fingerprint']['code_hash']
   verified.append(result)
  assert len(verified)==96 and {r['root'] for r in verified}==set(range(1,97))
  memory=sqlite3.connect(':memory:');memory.execute('create table results(payload text)')
  memory.executemany('insert into results values(?)',[(json.dumps(v),) for v in verified])
  recovered=summarize(memory)
  for key in ['cells','comparison','status']: assert recovered[key]==summary[key]
  recovered['accounting']={'terminal_export_reported':summary['accounts'],'persisted_sqlite_results':len(rows),
    'ledger_integrity':'FINAL_TRANSACTION_MISSING_IN_PERSISTED_SQLITE',
    'result_sources':'95 controller-accepted SQLite results plus completed root96 worker file; two older worker output files are stale' ,'resume_allowed':False,
    'independently_closed_ledger':False,'cpu_is_not_assumed_zero':True}
  (dest/'TREE_CALIBRATION.json').write_text(json.dumps(recovered,indent=2)+'\n')
  (dest/'TREE_VERIFIED_RESULTS.json').write_text(json.dumps(verified,separators=(',',':'))+'\n')
  status='MATHEMATICAL_EXPORT_VERIFIED_DATABASE_FINALIZATION_INCONSISTENT';count=96
 records.append({'run':name,'run_id':manifest['run_id'],'code_hash':manifest['fingerprint']['code_hash'],'verified_completed_jobs':count,
    'status':status,'reported_aggregate_cpu_s':summary['accounts']['aggregate_cpu_s']})
 con.close()
 with tarfile.open(dest/(name+'.tar.gz'),'w:gz') as tar:tar.add(p,arcname=name)
(dest/'AUDIT.json').write_text(json.dumps({'status':'MATH_PASS_WITH_TREE_LEDGER_EXCEPTION','scope':'result digests, identities, committed predictions, decisions; no mathematical reruns; no silent database repair','runs':records},indent=2)+'\n')
for src in ['lemma_run.log','lemma_preflight.log','tree_calibration.log','tree_preflight.log']:
 shutil.copy2(base/src,dest/src)
print(json.dumps(records,indent=2))
