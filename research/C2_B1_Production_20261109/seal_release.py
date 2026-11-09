import gzip,json,shutil
from pathlib import Path
import production as p
import batch_recovery as b

def seal(root):
    contract,context=p.verify_structure(root)
    for name in p.CONTROLS:assert b.read(p.P/name)['status']=='PASS',name
    files={n:b.digest(p.P/n) for n in sorted(p.seal_files(root))}
    data=dict(schema='C2B1_PRODUCTION_SEAL_V1',case=contract['case'],closure_context=context,files=files,chunk_size=3,scope='Restricted boundary search; global result requires fresh complete closure, byte-verified archive, final review and Git documentation')
    target=root/'SEAL.json'
    if target.exists():
        assert target.read_bytes()==b.canonical(data), 'Existing seal is frozen; create a versioned continuation instead'
    else:b.write(target,data)
    p.check_seal(root)
    return data

def prepare(root):
    contract,context=p.verify_structure(root)
    p.initialise_search(root,'search',list(range(contract['boundary_count'])))
    with gzip.open(root/'closure/boundaries.json.gz','rt') as f:masks=json.load(f)['representatives']
    b.write(root/'BOUNDARIES.json',masks)
    (root/'sources').mkdir()
    for name in p.SOURCES:shutil.copyfile(p.P/name,root/'sources'/name)
    receipts=[b.read(f) for f in (root/'pilot_final/receipts').glob('*.json')]
    raw=max(v['proof_bytes'] for v in receipts);packed=max(v['compressed_bytes'] for v in receipts)
    estimated=(3*raw+5*packed)*contract['boundary_count']
    required=int(estimated*1.5)+24*1024**3
    b.write(root/'STORAGE_PLAN.json',dict(schema='C2B1_STORAGE_PLAN_V1',case=contract['case'],pilot_samples=len(receipts),pilot_max_raw=raw,pilot_max_gzip=packed,boundaries=contract['boundary_count'],raw_copies=3,gzip_copies_including_archive=5,forecast_multiplier=1.5,reserve_bytes=24*1024**3,required_free_before_start=required,available_at_plan=shutil.disk_usage(root).free,limitation='Pilot-based forecast, not a mathematical upper bound. Resource watcher stops before reserve exhaustion; preserves checkpoints. No global count on resource stop.'))
    assert shutil.disk_usage(root).free>=required,'Storage forecast does not fit'

if __name__=='__main__':
    import sys
    root=p.P/'case_1005'
    if sys.argv[1]=='prepare':prepare(root)
    else:print(json.dumps(seal(root)))
