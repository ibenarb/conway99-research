from pathlib import Path
import json,fcntl,time
import production as p
import batch_recovery as b
P=p.P;root=P/'case_1005'
with (P.parent/'C2_Rest55_20261104/campaign.lock').open('a+b') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    with __import__('gzip').open(root/'closure/boundaries.json.gz','rt') as f:masks=json.load(f)['representatives']
    a=masks[0][0]
    other=next(i for i,v in enumerate(masks) if v[0]!=a)
    tasks=[0,other,1]
    assert masks[1][0]==a
    timings={}
    for name,chunk in [('aba_batch',3),('aba_single',1)]:
        p.initialise_search(root,name,tasks)
        start=time.monotonic()
        state=b.run(root/name,chunk_size=chunk)
        assert state['state']=='RESEARCH_SUBSET_VERIFIED'
        timings[name]=time.monotonic()-start
    hashes={}
    for i in tasks:
        x=b.read(root/'aba_batch/receipts'/f'{i:05d}.json')
        y=b.read(root/'aba_single/receipts'/f'{i:05d}.json')
        assert x['proof_sha256']==y['proof_sha256']
        hashes[str(i)]=x['proof_sha256']
    result=dict(status='PASS',case=1005,tasks=tasks,masks=[masks[i] for i in tasks],proof_hashes=hashes,seconds=timings,source_hashes={n:b.digest(P/n) for n in p.SOURCES},scope='Real A-B-A native batch versus single tasks, independently replayed byte-identical proof payloads; not a full-case speedup claim')
    b.write(P/'ABA_PASS.json',result)
    print(json.dumps(result))
