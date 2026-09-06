"""Hash immutable production CNF/LRAT inputs in a separate process group."""
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path

def file_hash(path):
    h=hashlib.sha256(); size=0
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1<<20),b''):
            size+=len(block); h.update(block)
    return {'path':str(path), 'size':size, 'sha256':h.hexdigest()}

def main():
    if len(sys.argv) != 5 or sys.argv[1] != 'hash-inputs':
        raise SystemExit('usage: proof_worker.py hash-inputs CNF LRAT META')
    cnf, proof, meta = map(Path, sys.argv[2:])
    # Do not parse, filter, copy, or rewrite either production input here.
    value={'cnf':file_hash(cnf), 'lrat':file_hash(proof)}
    tmp=meta.with_suffix('.tmp');tmp.write_text(json.dumps(value, sort_keys=True)+'\n');os.replace(tmp,meta)
if __name__=='__main__':main()
