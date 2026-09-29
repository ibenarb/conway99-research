"""Deterministic K1 PYZ from frozen source and validation documents."""
import hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DOCS=ROOT/'docs/memetik/lambda_k1_20260929'
WRAPPER='''from pathlib import Path
import runpy,sys,tempfile,zipfile
with tempfile.TemporaryDirectory(prefix="conway99_k1_100_") as temporary:
    with zipfile.ZipFile(sys.argv[0]) as archive: archive.extractall(temporary)
    sys.path.insert(0,temporary)
    runpy.run_path(str(Path(temporary)/"start.py"),run_name="__main__")
'''

def main():
    content={p.name:p.read_bytes() for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='PACKAGE.json'}
    for name in ('PLAN.md','VALIDATION.json'):
        content['validation/'+name]=(DOCS/name).read_bytes()
    for name,path in [('EXPERIMENT_RULES.md',ROOT/'docs/EXPERIMENT_RULES.md'),('GLOBAL_CONCLUSIONS.md',ROOT/'docs/operations/GLOBAL_CONCLUSIONS.md')]:
        content['validation/'+name]=path.read_bytes()
    package={'version':'K1-1.0.0','files':{n:hashlib.sha256(b).hexdigest() for n,b in content.items()}}
    # Materialize validation files too: source prepare() and PYZ use identical hashes.
    for n,b in content.items():
        if '/' in n:(HERE/n).parent.mkdir(parents=True,exist_ok=True);(HERE/n).write_bytes(b)
    (HERE/'PACKAGE.json').write_text(json.dumps(package,sort_keys=True,indent=2)+'\n')
    content['PACKAGE.json']=(HERE/'PACKAGE.json').read_bytes();content['__main__.py']=WRAPPER.encode()
    out=ROOT/'releases/memetik/Conway99_Lambda_K1_1.0.0.pyz';out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(content.items()):
            i=zipfile.ZipInfo(n,(2026,9,29,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,b)
    sha=hashlib.sha256(out.read_bytes()).hexdigest();Path(str(out)+'.sha256').write_text(sha+'  '+out.name+'\n')
    report={'version':'K1-1.0.0','sha256':sha,'bytes':out.stat().st_size,'path':str(out.relative_to(ROOT)),'target_host_gate':'NOT_YET_RUN'}
    (DOCS/'RELEASE.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
