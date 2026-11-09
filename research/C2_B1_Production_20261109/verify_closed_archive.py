"""Verify a complete closed-case archive; optionally remove only identical loose gzip duplicates."""
from pathlib import Path
import hashlib,json,sys,zipfile,datetime
W=Path(__file__).resolve().parents[2];R=W/'work/C2_Rest55_20261104';case=int(sys.argv[1]);reclaim='--reclaim' in sys.argv[2:]
assert case in (74,75,76,77)
root=(R/f'case_{case:04d}').resolve();assert root.is_relative_to(W.resolve()) and root.name==f'case_{case:04d}'
ledger=json.loads((R/'ledger.json').read_text(encoding='utf-8-sig'));assert case in ledger['closed'] and ledger.get('active_case')!=case
assert json.loads((root/'full_run/status.json').read_text())['state']=='CASE_VERIFIED_UNSAT'
receipt=next(x for x in json.loads((root/'ARCHIVE_RECEIPTS.json').read_text()) if 'Vollstaendig' in x['archive']);assert receipt['status']=='PASS'
archive=(W/'review'/receipt['archive']).resolve();assert archive.is_relative_to((W/'review').resolve()) and archive.stat().st_size==receipt['bytes']
def digest_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
assert digest_file(archive)==receipt['sha256'],'Archive hash changed'
with zipfile.ZipFile(archive) as z:
    manifest=json.loads(z.read('MANIFEST.json'));entries={e['path']:e for e in manifest}
    assert len(z.namelist())==len(entries)+1 and set(z.namelist())==set(entries)|{'MANIFEST.json'}
    for e in manifest:
        h=hashlib.sha256();size=0
        with z.open(e['path']) as f:
            for b in iter(lambda:f.read(1024**2),b''):h.update(b);size+=len(b)
        assert size==e['bytes'] and h.hexdigest()==e['sha256'],e['path']
records=json.loads((root/'full_run/completion.json').read_text())['proof_records'];targets=[]
for r in records:
    p=(root/r['proof_file']).resolve();assert p.is_relative_to(root/'full_run') and p.name=='proof.bin.gz' and not p.is_symlink()
    name=p.relative_to(W).as_posix();e=entries[name]
    assert e['sha256']==r['compressed_sha256'] and e['bytes']==r['compressed_bytes']
    if p.exists():
        assert p.stat().st_size==e['bytes'] and digest_file(p)==e['sha256'],name
        targets.append((p,e))
result=dict(status='ARCHIVE_AND_DUPLICATES_VERIFIED',case=case,archive=str(archive),archive_sha256=receipt['sha256'],archive_entries=len(entries),loose_duplicates=len(targets),bytes=sum(e['bytes'] for _,e in targets),reclaimed=False,time=datetime.datetime.now(datetime.timezone.utc).isoformat())
log=root/'STORAGE_DUPLICATE_AUDIT.json';log.write_text(json.dumps(result,indent=4))
if reclaim:
    # Every destination archive member and every exact source byte was checked above.
    for p,e in targets:
        assert p.resolve().is_relative_to(root/'full_run') and p.stat().st_size==e['bytes']
        p.unlink()
    result['reclaimed']=True;result['status']='ARCHIVED_DUPLICATES_RECLAIMED'
    result['preserved']='Complete verified archive, all loose metadata/checkpoints/logs/contracts; no T20 files touched'
    log.write_text(json.dumps(result,indent=4))
print(json.dumps(result),flush=True)
