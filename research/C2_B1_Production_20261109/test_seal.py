import shutil,json
import production as p
import batch_recovery as b
import seal_release as release
P=p.P;source=P/'case_1005';root=P/'sealed_fixture';root.mkdir()
# A separate real-data fixture: never mutate production inputs.
for name in ['closure','sources']:
    shutil.copytree(source/name,root/name)
(root/'structure/audit').mkdir(parents=True);shutil.copyfile(source/'structure/audit/FINAL_AUDIT.json',root/'structure/audit/FINAL_AUDIT.json')
(root/'search').mkdir()
for name in list(b.NAMES)+['contract.json']:shutil.copyfile(source/'search'/name,root/'search'/name)
for name in ['PILOT_PASS_FINAL.json','BOUNDARIES.json','STORAGE_PLAN.json']:shutil.copyfile(source/name,root/name)
release.seal(root)
p.check_seal(root)
answers=['complete_real_data_seal_accepted']
def update_seal():
    seal=b.read(root/'SEAL.json')
    seal['files']={n:b.digest(P/n) for n in sorted(p.seal_files(root))}
    (root/'SEAL.json').write_bytes(b.canonical(seal))
def reject(needle):
    try:p.check_seal(root)
    except Exception as e:assert needle in str(e),(needle,str(e))
    else:raise AssertionError('Bad seal accepted')
def trial(name,change,needle,paths):
    old={x:x.read_bytes() for x in paths}
    try:
        change();update_seal();reject(needle);answers.append(name)
    finally:
        for x,data in old.items():x.write_bytes(data)
        update_seal();p.check_seal(root)
contract_path=root/'search/contract.json'
def change_model():
    path=root/'search/model.txt';path.write_bytes(path.read_bytes()+b'\n')
    c=b.read(contract_path);c['files']['model.txt']=b.digest(path);contract_path.write_bytes(b.canonical(c))
trial('resealed_search_model_closure_mismatch_rejected',change_model,'Search/closure file mismatch',[contract_path,root/'search/model.txt'])
def change_native():
    path=root/'search/batch-engine';path.write_bytes(b'not the approved engine')
    c=b.read(contract_path);c['files']['batch-engine']=b.digest(path);contract_path.write_bytes(b.canonical(c))
trial('resealed_wrong_native_rejected',change_native,'Wrong native program',[contract_path,root/'search/batch-engine'])
def change_masks():
    c=b.read(contract_path);c['masks'][0]=[0,0];contract_path.write_bytes(b.canonical(c));(root/'BOUNDARIES.json').write_bytes(b.canonical(c['masks']))
trial('self_consistent_but_wrong_masks_rejected',change_masks,'Mask list differs',[contract_path,root/'BOUNDARIES.json'])
def change_pilot():
    c=b.read(root/'PILOT_PASS_FINAL.json');c['source_hashes']['production.py']='0'*64;(root/'PILOT_PASS_FINAL.json').write_bytes(b.canonical(c))
trial('resealed_pilot_other_driver_rejected',change_pilot,'Pilot release mismatch',[root/'PILOT_PASS_FINAL.json'])
def change_sources():
    (root/'sources/production.py').write_bytes(b'wrong archived source')
trial('resealed_wrong_archived_source_rejected',change_sources,'Archived source differs',[root/'sources/production.py'])
def change_case():
    c=b.read(contract_path);c['binding']['case']=78;contract_path.write_bytes(b.canonical(c))
trial('resealed_wrong_case_rejected',change_case,'Transaction closure binding',[contract_path])
result=b.read(P/'PRODUCTION_CONTROLS.json');result['tests']+=answers;result['scope']='Production helpers and real-data seal-binding tests; no global exclusion'
(P/'PRODUCTION_CONTROLS.json').write_bytes(b.canonical(result))
release.seal(source)
print(json.dumps(result))
