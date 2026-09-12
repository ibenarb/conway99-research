"""Supplement the pinned upstream verifier with all six initial Gram regenerations."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,tempfile
parser=argparse.ArgumentParser();parser.add_argument('repository',type=Path);parser.add_argument('drat_trim',type=Path);args=parser.parse_args()
repo=args.repository.resolve(); tool=args.drat_trim.resolve()
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()=='e8f4d629cdf03b4bb14ebed01e4ebe7e8dbf3f8b'
sys.path.insert(0,str(repo/'verification'))
from f27_binary_gram_cnf import build
bundle=repo/'artifacts/f27_binary_gram_certificates/canonical'
with tempfile.TemporaryDirectory() as temp:
    files=sorted(bundle.glob('mask*.cnf.gz'));assert len(files)==6
    for file in files:
        metadata=json.loads(file.with_suffix('').with_suffix('.json').read_text())
        cnf,_,_=build(tuple(metadata['partition']),metadata['u_mask'])
        out=Path(temp)/'model.cnf';cnf.to_file(str(out))
        assert out.read_bytes()==gzip.decompress(file.read_bytes())
        assert hashlib.sha256(out.read_bytes()).hexdigest()==metadata['cnf_sha256']
        print('PASS_REGENERATED_INITIAL_GRAM',metadata['u_mask'],flush=True)
subprocess.run([sys.executable,str(repo/'verification/verify_f27_certificate_bundle.py'),'--fresh-proofs','--drat-trim',str(tool)],check=True,cwd=repo)
