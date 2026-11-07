"""C2B1 full closure gate. Fresh mathematical audit and fresh proof replay.
No controller logs or previous PASS declarations are trusted. Research release.
"""
from pathlib import Path
import argparse
import ctypes
import signal
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from mathematical_audit import load_model, require, validate

SEMANTICS = dict(schema='C2B1_GLOBAL_MINIMUM_V1',rows=[2,3],composition='g_col_after_sigma_col',sigma=[2,3,0,1,4,5,6,7,8,9,10,11],comparison='unsigned_60_bit_integer',relation='image_greater_or_equal_boundary_a',equality_allowed=True,old_format_implication='C2S2_UNSAT_implies_C2B1_restricted_UNSAT')
TRUSTED = {
    'representatives.json': 'edc2abec0357bdd5b70a493d741d86b8d9adddb5ca64370f1e4be9999ecbb581',
    'c2s2-verify': 'c93325925676d22f68672bf9f2f7dadf41edc751824079e9de22bfe249662c46',
    'c2s2-verify.cpp': 'c8747b95f84cdeb3d5169c7e4512d77074ec11205ecf720e06b03d7b44c8e693',
    'c2b1-verify': '094e0cc4eb51f9b420125d5b549f60ac57b04bba087cf6b17d0a88c786ade1e7',
    'c2b1-verify.cpp': 'a005e9f2bed767ef89b3ef7f63210f75e7732abfdfd5fd862e670ecb78d5ae23',
}
LOCAL = ['closure_gate.py','mathematical_audit.py','row_domains_complete.py','run_closure.py','resource_sensor.py']
REQUIRED = set(TRUSTED) | set(LOCAL) | {'record.json','model.txt','boundaries.json.gz','block_actions.txt','s2_action.txt'}
MAX_PROOF = 128 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(',',':')).encode()


def parse_json(raw):
    def unique(pairs):
        result = {}
        for key,value in pairs:
            require(key not in result,'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw,object_pairs_hook=unique)


def read_json(path):
    return parse_json(path.read_bytes())


def contained(root, name):
    path = Path(name)
    require(not path.is_absolute() and name and '..' not in path.parts,'Unsafe relative path')
    candidate = root / path
    require(candidate.resolve().is_relative_to(root.resolve()),'Path escapes bundle')
    require(all(not part.is_symlink() for part in [candidate,*candidate.parents] if part != root.parent),'Symlink input')
    return candidate


def snapshot_contract(root, out):
    contract = read_json(root / 'contract.json')
    require(contract['schema'] == 'C2B1_CLOSURE_CONTRACT_V1' and contract['semantics'] == SEMANTICS,'Wrong closure semantics')
    require(type(contract['case']) is int and type(contract['boundary_count']) is int and contract['boundary_count'] > 0,'Invalid case/count')
    require(set(contract['files']) == REQUIRED,'Incomplete/unexpected contract files')
    context = sha(canonical(contract))
    inputs = out / 'inputs'
    inputs.mkdir()
    for name,expected in contract['files'].items():
        source = contained(root,name)
        require(digest(source) == expected,'Contract hash mismatch: ' + name)
        if name in TRUSTED:
            require(expected == TRUSTED[name],'Untrusted checker/catalog: ' + name)
        if name in LOCAL:
            require(expected == digest(Path(__file__).parent / name),'Auditor source mismatch: ' + name)
        shutil.copyfile(source,inputs / name)
        require(digest(inputs / name) == expected,'Snapshot mismatch: ' + name)
    (out / 'contract.json').write_bytes(canonical(contract))
    for name in ['c2s2-verify','c2b1-verify']:
        (inputs / name).chmod(0o755)
    return contract,context,inputs


def validate_manifest(manifest,contract,context,boundaries,complete):
    require(manifest['schema'] == 'C2B1_PROOF_MANIFEST_V1' and manifest['context_sha256'] == context,'Manifest context')
    require(manifest['case'] == contract['case'] and type(manifest['case']) is int,'Manifest case')
    require(len(boundaries) == contract['boundary_count'],'Contract boundary count')
    records = manifest['records']
    require(type(records) is list and records,'Empty proof manifest')
    indices = []
    paths = set()
    for record in records:
        i = record['boundary']
        require(type(i) is int and 0 <= i < len(boundaries),'Invalid boundary index')
        require(record['case'] == contract['case'] and type(record['case']) is int,'Receipt case')
        require(record['context_sha256'] == context,'Receipt context')
        require(record['masks'] == boundaries[i] and all(type(x) is int for x in record['masks']),'Concrete boundary mismatch')
        fmt = record['format']
        require(fmt in ['C2S2','C2B1'],'Unknown proof semantics')
        status = 'VERIFIED_BOUNDARY_UNSAT' if fmt == 'C2S2' else 'VERIFIED_CANONICALLY_RESTRICTED_BOUNDARY_UNSAT'
        require(record['status'] == status,'Wrong restricted/unrestricted status')
        require(record['encoding'] in ['raw','gzip'],'Unsupported proof encoding')
        require(type(record['proof_bytes']) is int and 8 <= record['proof_bytes'] <= MAX_PROOF,'Proof size')
        require(record['path'] not in paths,'Duplicate proof path')
        paths.add(record['path'])
        indices.append(i)
    require(len(indices) == len(set(indices)),'Duplicate boundary index')
    if complete:
        require(set(indices) == set(range(len(boundaries))),'INCOMPLETE: full original boundary coverage required')
    return sorted(records,key=lambda r:r['boundary'])


def snapshot_proof(root,record,target):
    source = contained(root,record['path'])
    with source.open('rb') as stream:
        stored = stream.read(MAX_PROOF + 1024 * 1024 + 1)
    require(len(stored) <= MAX_PROOF + 1024 * 1024 and sha(stored) == record['stored_sha256'],'Stored proof hash/size')
    with target.with_suffix('.stored').open('xb') as stream:
        stream.write(stored)
    if record['encoding'] == 'gzip':
        with gzip.GzipFile(fileobj=io.BytesIO(stored),mode='rb') as stream:
            raw = stream.read(MAX_PROOF + 1)
    else:
        raw = stored
    require(len(raw) == record['proof_bytes'] and sha(raw) == record['proof_sha256'],'Raw proof size/hash')
    require(raw[:4] == record['format'].encode() and int.from_bytes(raw[4:8],'little') == record['boundary'],'Proof header/index')
    with target.open('xb') as stream:
        stream.write(raw)
    require(digest(target) == record['proof_sha256'],'Proof snapshot hash')


def child_limits(parent):
    require(ctypes.CDLL(None).prctl(1,signal.SIGKILL) == 0,'Cannot bind verifier lifetime')
    if os.getppid() != parent:
        os.kill(os.getpid(),signal.SIGKILL)
    import resource
    current_nice = os.getpriority(os.PRIO_PROCESS,0)
    if current_nice < 15:
        os.nice(15-current_nice)
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(180,180))
    resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_PROOF,MAX_PROOF))


def replay(root,inputs,out,records):
    require(os.name == 'posix','Native fresh replay requires Linux')
    evidence = []
    batch = 0
    for fmt in ['C2S2','C2B1']:
        selected = [r for r in records if r['format'] == fmt]
        for start in range(0,len(selected),3):
            chunk = selected[start:start+3]
            folder = out / ('replay_%06d' % batch)
            folder.mkdir()
            for record in chunk:
                snapshot_proof(root,record,folder / ('boundary_%d.proof' % record['boundary']))
            arguments = [inputs / ('c2s2-verify' if fmt == 'C2S2' else 'c2b1-verify'),inputs / 'model.txt',','.join(str(r['boundary']) for r in chunk),folder,inputs / 's2_action.txt']
            if fmt == 'C2B1':
                arguments.append(inputs / 'block_actions.txt')
            parent = os.getpid()
            with (folder / 'replay.log').open('xb') as stream:
                result = subprocess.run(list(map(str,arguments)),stdout=stream,stderr=subprocess.STDOUT,timeout=200,preexec_fn=lambda:child_limits(parent))
            require(result.returncode == 0,'Fresh proof replay rejected batch ' + str(batch))
            for record in chunk:
                i = record['boundary']
                receipt = folder / ('boundary_%d.verified.json' % i)
                require(read_json(receipt) == dict(boundary=i,status=record['status'],format=fmt),'Native receipt mismatch')
                require(digest(folder / ('boundary_%d.proof' % i)) == record['proof_sha256'],'Proof changed during replay')
                evidence.append(dict(boundary=i,masks=record['masks'],format=fmt,proof_sha256=record['proof_sha256'],receipt_sha256=digest(receipt),log_sha256=digest(folder / 'replay.log')))
            batch += 1
            print('Fresh replay batch completed: ' + str(batch),flush=True)
    require(len(evidence) == len(records),'Missing fresh replay')
    return evidence


def run(root,out,mode):
    require(mode in ['complete','subset','structure'],'Invalid mode')
    root,out = root.resolve(),out.resolve()
    require(not out.exists() and not out.is_relative_to(root) and not root.is_relative_to(out),'Output must be new and separate from evidence bundle')
    out.mkdir(parents=True)
    try:
        contract,context,inputs = snapshot_contract(root,out)
        manifest = None
        records = []
        manifest_hash = None
        if mode != 'structure':
            manifest_bytes = (root / 'manifest.json').read_bytes()
            manifest_hash = sha(manifest_bytes)
            manifest = parse_json(manifest_bytes)
            _,_,_,_,boundaries = load_model(inputs / 'model.txt')
            records = validate_manifest(manifest,contract,context,boundaries,mode == 'complete')
            (out / 'manifest.json').write_bytes(manifest_bytes)
        math = validate(inputs,lambda s:print(s,flush=True))
        require(math['case'] == contract['case'] and math['boundary_count'] == contract['boundary_count'],'Mathematical contract mismatch')
        math.pop('boundaries')
        evidence = replay(root,inputs,out,records) if records else []
        require(read_json(root / 'contract.json') == contract,'Contract changed during audit')
        for name,expected in contract['files'].items():
            require(digest(contained(root,name)) == expected and digest(inputs / name) == expected,'Input changed during audit')
        if manifest is not None:
            require(digest(root / 'manifest.json') == manifest_hash,'Manifest changed during audit')
            for record in records:
                require(digest(contained(root,record['path'])) == record['stored_sha256'],'Source proof changed during audit')
                print('Final source hash checked: ' + str(record['boundary']),flush=True)
        report = dict(status='PASS' if mode == 'complete' else 'NONCLOSING_' + mode.upper(),case=contract['case'],case_proved_unsat=mode == 'complete',global_count_authorized=False,L62_closed=False,C2_closed=False,context_sha256=context,manifest_sha256=manifest_hash,mathematical_audit=math,fresh_replays=evidence,remaining=max(0,contract['boundary_count']-len(records)),requires_before_count=['bytechecked_complete_archive','Git_documentation','independent_release_review'])
        with (out / 'FINAL_AUDIT.json').open('xb') as stream:
            stream.write(canonical(report))
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({k:v for k,v in report.items() if k != 'fresh_replays'}),flush=True)
        return report
    except BaseException as error:
        (out / 'FAILED.json').write_bytes(canonical(dict(status='FAIL',case_proved_unsat=False,error=repr(error))))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--mode',choices=['complete','subset','structure'],default='complete')
    args = parser.parse_args()
    run(args.bundle,args.output,args.mode)
