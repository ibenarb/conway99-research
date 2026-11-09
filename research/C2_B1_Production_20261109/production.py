"""Sealed C2B1 production driver: transactions, full fresh closure, verified archive."""
from pathlib import Path
import argparse
import ctypes
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import zipfile
import uuid
import gzip
import batch_recovery as b

P = Path(__file__).resolve().parent
W = P.parents[1]
G = P.parent/'C2_Closure_C2B1_20261107'
SOURCES = ['production.py','batch_recovery.py','resource_sensor.py','batch-engine','batch-engine.cpp','batch-verify','batch-verify.cpp']
CONTROLS = ['CONTROLS.json','HARD_KILL_CONTROLS.json','UNKNOWN_PREFIX_CONTROLS.json','SCALING_CONTROLS.json','BINDING_CONTROLS.json','PRODUCTION_CONTROLS.json','ABA_PASS.json']

def seal_files(root):
    rel=root.relative_to(P).as_posix()
    return set(SOURCES+CONTROLS+[rel+'/'+n for n in ['search/contract.json','closure/contract.json','structure/audit/FINAL_AUDIT.json','PILOT_PASS_FINAL.json','BOUNDARIES.json','STORAGE_PLAN.json']]+[rel+'/sources/'+n for n in SOURCES])

def write_status(root,phase,**extra):
    data=dict(phase=phase,time=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=os.getpid(),case_count_changed=False,**extra)
    temp=root/'STATE.tmp'
    with temp.open('w') as f:
        json.dump(data,f,indent=4);f.flush();os.fsync(f.fileno())
    os.replace(temp,root/'STATE.json')

def bind_parent(parent):
    b.require(ctypes.CDLL(None).prctl(1,signal.SIGKILL)==0,'Parent binding failed')
    if os.getppid()!=parent:os.kill(os.getpid(),signal.SIGKILL)

def verify_structure(root):
    contract=b.read(root/'closure/contract.json')
    report=b.read(root/'structure/audit/FINAL_AUDIT.json')
    context=b.sha(b.canonical(contract))
    b.require(report['status']=='NONCLOSING_STRUCTURE' and report['context_sha256']==context,'Structure audit context')
    b.require(report['mathematical_audit']['case']==contract['case'] and report['mathematical_audit']['boundary_count']==contract['boundary_count'],'Structure case/count')
    for name,h in contract['files'].items():b.require(b.digest(root/'closure'/name)==h,'Closure input changed: '+name)
    for name in ['closure_gate.py','mathematical_audit.py','row_domains_complete.py','resource_sensor.py','run_closure.py']:
        b.require(b.digest(G/name)==contract['files'][name],'Installed closure auditor differs: '+name)
    return contract,context

def check_seal(root):
    seal=b.read(root/'SEAL.json')
    b.require(seal['schema']=='C2B1_PRODUCTION_SEAL_V1','Wrong production seal')
    b.require(set(seal['files'])==seal_files(root),'Incomplete seal file set')
    for name,h in seal['files'].items():
        path=(P/name).resolve()
        b.require(path.is_relative_to(P) and not path.is_symlink() and b.digest(path)==h,'Sealed file changed: '+name)
    contract,context=verify_structure(root)
    b.require(seal['case']==contract['case'] and seal['closure_context']==context,'Wrong seal context')
    trans,tx=b.check_contract(root/'search')
    b.require(trans['tasks']==list(range(contract['boundary_count'])),'Incomplete production task list')
    b.require(trans['binding']==dict(case=contract['case'],closure_context=context,semantics=contract['semantics']),'Transaction closure binding')
    b.require(trans['masks']==b.read(root/'BOUNDARIES.json'),'Transaction masks mismatch')
    for local,closure in [('model.txt','model.txt'),('action.txt','s2_action.txt'),('blocks.txt','block_actions.txt')]:
        b.require(trans['files'][local]==contract['files'][closure],'Search/closure file mismatch: '+local)
    for name in ['batch-engine','batch-verify']:
        b.require(trans['files'][name]==b.digest(P/name),'Wrong native program')
    with gzip.open(root/'closure/boundaries.json.gz','rt') as f: boundaries=json.load(f)['representatives']
    b.require(boundaries==trans['masks'],'Mask list differs from checked coverage')
    for name in SOURCES:b.require(b.digest(P/name)==b.digest(root/'sources'/name),'Archived source differs')
    pilot=b.read(root/'PILOT_PASS_FINAL.json')
    b.require(pilot['status']=='PASS' and pilot['closure_context']==context and pilot['source_hashes']=={n:b.digest(P/n) for n in SOURCES},'Pilot release mismatch')
    for name in CONTROLS:b.require(b.read(P/name)['status']=='PASS','Control not passed')
    return seal,contract,context

def initialise_search(root,name,tasks):
    contract,context=verify_structure(root)
    sources={'model.txt':root/'closure/model.txt','action.txt':root/'closure/s2_action.txt','blocks.txt':root/'closure/block_actions.txt','batch-engine':P/'batch-engine','batch-verify':P/'batch-verify'}
    return b.initialise(root/name,'case'+str(contract['case']),contract['boundary_count'],tasks,sources,binding=dict(case=contract['case'],closure_context=context,semantics=contract['semantics']))

def prepare_manifest(root):
    seal,contract,context=check_seal(root)
    tx,txhash=b.check_contract(root/'search')
    records=b.load_receipts(root/'search',tx,txhash)
    b.require(set(records)==set(range(contract['boundary_count'])),'Not all boundaries verified')
    bundle=root/'closure'
    folder=bundle/'proofs'
    folder.mkdir(exist_ok=True)
    manifest=[]
    sensor=b.Sensor(root)
    for i,item in sorted(records.items()):
        _,reasons=sensor.resources();b.require(not reasons,'RESOURCE_HOLD: '+repr(reasons))
        packed=(root/'search/receipts'/f'{i:05d}.proof.gz').read_bytes()
        b.require(b.sha(packed)==item['compressed_sha256'],'Changed stored proof')
        rel=f'proofs/{i:05d}.proof.gz'
        copy_once(bundle/rel,packed)
        manifest.append(dict(case=contract['case'],boundary=i,masks=tx['masks'][i],context_sha256=context,format='C2B1',status='VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT',encoding='gzip',path=rel,stored_sha256=item['compressed_sha256'],proof_sha256=item['proof_sha256'],proof_bytes=item['proof_bytes']))
    copy_once(bundle/'manifest.json',b.canonical(dict(schema='C2B1_PROOF_MANIFEST_V1',case=contract['case'],context_sha256=context,records=manifest)))

def copy_once(path,data):
    if path.exists():
        b.require(not path.is_symlink() and path.read_bytes()==data,'Conflicting preserved closure file')
    else:b.durable_new(path,data)

def archive(root,final):
    report=b.read(final/'audit/FINAL_AUDIT.json')
    b.require(report['status']=='PASS' and report['case_proved_unsat'] and report['remaining']==0,'No full case proof')
    case=report['case'];total=report['mathematical_audit']['boundary_count']
    files=sorted(f for f in root.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.suffix not in ('.proof','.stored','.lock','.tmp') and f.name not in ('STATE.json','driver.log','driver.stderr.log','ARCHIVE_RECEIPT.json','STOP.json'))
    b.require(len(list((root/'closure/proofs').glob('*.gz')))==total,'Incomplete archive corpus')
    b.require(shutil.disk_usage(root).free>22*1024**3+sum(f.stat().st_size for f in files),'Archive reserve insufficient')
    path=W/'review'/f'C2B1_case_{case}_complete_{uuid.uuid4().hex}.zip'
    sensor=b.Sensor(root)
    entries=[]
    with zipfile.ZipFile(path,'x',allowZip64=True) as z:
        for i,f in enumerate(files):
            if i%100==0:
                _,reasons=sensor.resources();b.require(not reasons,'RESOURCE_HOLD: '+repr(reasons))
            entry=dict(path=f.relative_to(root).as_posix(),bytes=f.stat().st_size,sha256=b.digest(f))
            z.write(f,entry['path'],compress_type=zipfile.ZIP_STORED if f.suffix=='.gz' else zipfile.ZIP_DEFLATED)
            entries.append(entry)
        z.writestr('ARCHIVE_MANIFEST.json',json.dumps(entries))
    with path.open('rb') as f:os.fsync(f.fileno())
    with zipfile.ZipFile(path) as z:
        b.require(len(z.namelist())==len(entries)+1,'Archive member count')
        for i,e in enumerate(entries):
            if i%100==0:
                _,reasons=sensor.resources();b.require(not reasons,'RESOURCE_HOLD: '+repr(reasons))
            raw=z.read(e['path'])
            b.require(len(raw)==e['bytes'] and b.sha(raw)==e['sha256'] and b.digest(root/e['path'])==e['sha256'],'Archive byte mismatch')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    b.write(root/('ARCHIVE_RECEIPT_'+uuid.uuid4().hex+'.json'),dict(status='PASS',case=case,complete_proofs=total,files=len(entries),bytes=path.stat().st_size,sha256=h.hexdigest(),archive=str(path),case_count_changed=False))

def run(root,mode):
    root=root.resolve()
    b.require(root.parent==P,'Case must be direct child of production root')
    with (P.parent/'C2_Rest55_20261104/campaign.lock').open('a+b') as campaign, (root/'driver.lock').open('a+b') as lock:
        fcntl.flock(campaign,fcntl.LOCK_EX|fcntl.LOCK_NB)
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if mode=='pilot':
            contract,context=verify_structure(root)
            total=contract['boundary_count']
            tasks=sorted(set(min(i,total-1) for i in [0,1,2,100,1000,total-1]))
            initialise_search(root,'pilot_final',tasks)
            state=b.run(root/'pilot_final',chunk_size=3)
            b.require(state['state']=='RESEARCH_SUBSET_VERIFIED','Pilot did not pass')
            b.write(root/'PILOT_PASS_FINAL.json',dict(status='PASS',tasks=tasks,closure_context=context,source_hashes={n:b.digest(P/n) for n in SOURCES}))
            return
        seal,contract,context=check_seal(root)
        _,reasons=b.Sensor(root).resources();b.require(not reasons,'RESOURCE_HOLD: '+repr(reasons))
        b.require(mode=='finish' or not (root/'STOP.json').exists(),'Existing STOP requires explicit diagnosis')
        if mode=='production':
            plan=b.read(root/'STORAGE_PLAN.json')
            b.require(shutil.disk_usage(root).free>=plan['required_free_before_start'],'Planned storage reserve not met')
            regular=b.read(root/'REGULAR_PASS.json')
            b.require(regular['status']=='PASS' and regular['controller_sha256']==b.digest(P/'batch_recovery.py'),'Missing regular checkpoint gate')
        write_status(root,'SEARCHING_RESTRICTED_BOUNDARIES',case=contract['case'])
        if mode=='finish':
            tx,txhash=b.check_contract(root/'search')
            rec=b.load_receipts(root/'search',tx,txhash)
            b.require(set(rec)==set(range(contract['boundary_count'])),'Finish requires all search receipts')
            state=dict(state='RESEARCH_SUBSET_VERIFIED')
        else:state=b.run(root/'search',chunk_size=3,batch_limit=1 if mode=='regular' else None)
        if mode=='regular':
            b.require(state['state'] in ('INCOMPLETE_CHECKPOINT','RESEARCH_SUBSET_VERIFIED'),'Regular checkpoint failure')
            b.write(root/'REGULAR_PASS.json',dict(status='PASS',state=state,controller_sha256=b.digest(P/'batch_recovery.py')))
            write_status(root,'REGULAR_CHECKPOINT_READY',case=contract['case'])
            return
        b.require(state['state']=='RESEARCH_SUBSET_VERIFIED','Search stopped: '+repr(state))
        check_seal(root)
        write_status(root,'PREPARING_FULL_CLOSURE',case=contract['case'])
        prepare_manifest(root)
        write_status(root,'FRESH_FULL_REPLAY',case=contract['case'])
        parent=os.getpid()
        final=root/'final_runs'/uuid.uuid4().hex
        final.parent.mkdir(exist_ok=True)
        subprocess.run([sys.executable,str(G/'run_closure.py'),str(root/'closure'),str(final),'--mode','complete'],check=True,preexec_fn=lambda:bind_parent(parent))
        check_seal(root)
        write_status(root,'ARCHIVING',case=contract['case'])
        with b.GLOBAL_LOCK.open('a+b') as research_lock:
            fcntl.flock(research_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            archive(root,final)
        write_status(root,'AUDIT_ARCHIVE_PASS_PENDING_REVIEW_GIT',case=contract['case'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('mode',choices=['pilot','regular','production','finish']);args=parser.parse_args()
    try:run(args.root,args.mode)
    except BaseException as error:
        write_status(args.root,'STOPPED',error=repr(error))
        if not (args.root/'STOP.json').exists():b.write(args.root/'STOP.json',dict(error=repr(error),case_count_changed=False))
        raise
