#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, re, sys
sys.path.insert(0,str(Path(__file__).parent))
from pilot import decode_g6, validate, frame_ok, W
ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default=str(Path.home()/'conway99_workspace')); a=ap.parse_args()
pat=re.compile(r'(B[_-]?maple.*20260829|candidate[_-]?M|kandidat[_-]?M|(^|[/_.-])M([/_.-]|$))',re.I)
hits=[]
for p in Path(a.root).rglob('*'):
    if not p.is_file() or p.stat().st_size>5_000_000: continue
    if not pat.search(str(p)): continue
    rec={'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix.lower() in ('.g6','.graph6'):
        try:
            rows=decode_g6(p.read_text()); validate(rows); rec.update({'graph99':True,'frame_ok':frame_ok(rows),'W':W(rows)})
        except Exception as e: rec.update({'graph99':False,'error':str(e)})
    hits.append(rec)
print(json.dumps({'root':a.root,'hits':hits},indent=2))
