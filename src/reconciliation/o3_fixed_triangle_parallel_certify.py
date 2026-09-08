#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures as cf, gzip, hashlib, json, os, shutil, signal, subprocess, time
from fractions import Fraction
from pathlib import Path

MARKER=b's VERIFIED UNSAT'
PRIMARY_MAX=992

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def save(p,x):
    q=Path(str(p)+'.tmp'); q.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n'); os.replace(q,p)

def header(root):
    z=root.open().readline().split(); return int(z[2]),int(z[3])

def leaf_cnf(root,lits,out):
    nv,nc=header(root)
    with root.open('rb') as s,out.open('wb') as d:
        s.readline(); d.write(f'p cnf {nv} {nc+len(lits)}\n'.encode()); shutil.copyfileobj(s,d,8<<20)
        for x in lits:d.write(f'{x} 0\n'.encode())

def split_order(root,limit):
    cnt=[0]*(PRIMARY_MAX+1); fixed=set()
    with root.open() as f:
        for line in f:
            if not line or line[0] in 'pc%': continue
            a=[int(x) for x in line.split() if x!='0']
            if len(a)==1 and abs(a[0])<=PRIMARY_MAX: fixed.add(abs(a[0]))
            for x in a:
                if abs(x)<=PRIMARY_MAX: cnt[abs(x)]+=1
    v=[i for i in range(1,PRIMARY_MAX+1) if i not in fixed]
    v.sort(key=lambda x:(-cnt[x],x))
    return v[:limit],sorted(fixed)

def parse_witness(p):
    r={}
    for t in p.read_text(errors='replace').split():
        try:x=int(t)
        except:continue
        if x:r[abs(x)]=x>0
    return r

def maps():
    S={};L={};n=0
    for i in range(32):
        for j in range(i+1,32):n+=1;S[i,j]=n
    for i in range(32):
        for j in range(i+1,32):n+=1;L[i,j]=n
    return S,L

def verify(vals):
    S,L=maps(); groups=[range(0,4),range(4,8),range(8,12)];T={12,13}
    q=[[0]*35 for _ in range(35)]
    for i in range(3):
        for j in range(3):
            if i!=j:q[i][j]=1
    for f,G in enumerate(groups):
        for u in G:q[f][3+u]=3;q[3+u][f]=1
    for i in range(32):
        q[3+i][3+i]=2 if i in T else 0
        for j in range(i+1,32):
            w=int(vals.get(S[i,j],0))+2*int(vals.get(L[i,j],0));q[3+i][3+j]=q[3+j][3+i]=w
    sizes=[1,1,1]+[3]*32
    if any(sum(r)!=14 for r in q):return False,'row-degree',None
    for i in range(35):
        for j in range(35):
            if sizes[i]*q[i][j]!=sizes[j]*q[j][i]:return False,f'balance-{i}-{j}',None
            lhs=sum(q[i][k]*q[k][j] for k in range(35))+q[i][j];rhs=(12 if i==j else 0)+2*sizes[j]
            if lhs!=rhs:return False,f'eq-{i}-{j}',None
    return True,'PASS',q

def solve_one(root,c,job,cadical,secs,floor):
    job.mkdir(parents=True,exist_ok=True)
    cnf=job/'leaf.cnf';proof=job/'proof.lrat';wit=job/'witness.out';so=job/'solver.out';se=job/'solver.err'
    for p in (cnf,proof,wit,so,se):p.unlink(missing_ok=True)
    leaf_cnf(root,c['lits'],cnf); ch=sha(cnf);start=time.time();timed=False;resource=False
    with so.open('wb') as o,se.open('wb') as e:
        p=subprocess.Popen([cadical,'--lrat','--no-binary','-w',str(wit),str(cnf),str(proof)],stdout=o,stderr=e,start_new_session=True)
        while p.poll() is None:
            time.sleep(2)
            if shutil.disk_usage(job).free<floor*1024**3:resource=True;os.killpg(p.pid,signal.SIGINT);break
            if time.time()-start>=secs:timed=True;os.killpg(p.pid,signal.SIGINT);break
        if timed or resource:
            try:p.wait(30)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
        rc=p.wait()
    rec={'id':c['id'],'exit':rc,'wall':time.time()-start,'proof_bytes':proof.stat().st_size if proof.exists() else 0,'leaf_cnf_sha256':ch}
    if resource:rec['kind']='RESOURCE'
    elif timed:rec['kind']='TIMEOUT'
    elif rc==20:rec['kind']='UNSAT'
    elif rc==10:
        ok,msg,q=verify(parse_witness(wit));rec['kind']='SAT' if ok else 'SAT_INVALID';rec['verify']=msg
        if ok:(job/'quotient_Q.json').write_text(json.dumps(q,indent=2)+'\n')
    else:rec['kind']='ERROR'
    save(job/'solve.json',rec);return rec

def certify(job,c,lrat,cake):
    cnf=job/'leaf.cnf';proof=job/'proof.lrat';lo=job/'lrat.out';le=job/'lrat.err';co=job/'cake.out';ce=job/'cake.err';start=time.time()
    with lo.open('wb') as o,le.open('wb') as e:lrc=subprocess.run([lrat,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    if lrc:return {'ok':False,'stage':'lrat','exit':lrc}
    with co.open('wb') as o,ce.open('wb') as e:crc=subprocess.run([cake,str(cnf),str(proof)],stdout=o,stderr=e).returncode
    marker=MARKER in co.read_bytes()
    if crc or not marker:return {'ok':False,'stage':'cake','exit':crc,'marker':marker}
    rawh=sha(proof);rawb=proof.stat().st_size;gz=Path(str(proof)+'.gz')
    with proof.open('rb') as s,gzip.open(gz,'wb',compresslevel=1) as d:shutil.copyfileobj(s,d,8<<20)
    proof.unlink();rec={'ok':True,'id':c['id'],'depth':c['depth'],'lits':c['lits'],'leaf_cnf_sha256':sha(cnf),'proof_raw_sha256':rawh,'proof_raw_bytes':rawb,'proof_gz_sha256':sha(gz),'proof_gz_bytes':gz.stat().st_size,'lrat_exit':0,'cake_exit':0,'cake_positive_marker':True,'wall':time.time()-start};save(job/'certificate.json',rec);cnf.unlink();wit=job/'witness.out';wit.unlink(missing_ok=True);return rec

def cleanup(job):
    for n in ('leaf.cnf','proof.lrat','witness.out'):(job/n).unlink(missing_ok=True)

def weight(c):return Fraction(1,1<<c['depth'])

def main():
    ap=argparse.ArgumentParser();home=Path.home();
    ap.add_argument('--root-cnf',default=str(home/'conway99_workspace/o3_reconciliation_runs/review_reconciled_20260907/fixed_triangle/fixed_triangle_o3_quotient.cnf'))
    ap.add_argument('--run-dir',default=str(home/'conway99_workspace/o3_reconciliation_runs/fixed_triangle_parallel_20260908'))
    ap.add_argument('--workers',type=int,default=21);ap.add_argument('--initial-depth',type=int,default=8);ap.add_argument('--leaf-seconds',type=int,default=180);ap.add_argument('--proof-max-gib',type=float,default=1.0);ap.add_argument('--split-limit',type=int,default=128);ap.add_argument('--status-seconds',type=int,default=600);ap.add_argument('--disk-floor-gib',type=float,default=75)
    ap.add_argument('--cadical',default=str(home/'.local/bin/cadical'));ap.add_argument('--lrat-check',default=str(home/'.local/bin/lrat-check'));ap.add_argument('--cake',default=str(home/'conway99_workspace/conway99_o3_qsat_preflight_0.1.12/dependencies/bin/cake_lpr'))
    a=ap.parse_args();
    if not 1<=a.workers<=21:raise SystemExit('workers must be 1..21 (one checker lane keeps total <=22)')
    root=Path(a.root_cnf);run=Path(a.run_dir);jobs=run/'jobs';run.mkdir(parents=True,exist_ok=True);jobs.mkdir(exist_ok=True)
    for p in (root,Path(a.cadical),Path(a.lrat_check),Path(a.cake)):
        if not p.exists():raise SystemExit(f'missing: {p}')
    rh=sha(root);sp=run/'split_vars.json';statep=run/'state.json'
    print('=== FIXED-K3 PARALLEL CERTIFICATION ===',flush=True);print(f'root_sha256={rh}',flush=True);print(f'workers={a.workers}+1 checker; initial_depth={a.initial_depth}; leaf_timeout={a.leaf_seconds}s; proof_cap={a.proof_max_gib}GiB',flush=True);print('ETA initial: 2-6h favorable, 6-15h working, 15-30h hard tail.',flush=True)
    if sp.exists():sv=json.loads(sp.read_text())['vars']
    else:
        print('PREPARE split-variable ranking ...',flush=True);sv,fixed=split_order(root,a.split_limit);save(sp,{'root_sha256':rh,'vars':sv,'fixed':fixed});print(f'PREPARE_OK vars={len(sv)} fixed={len(fixed)}',flush=True)
    if statep.exists():
        st=json.loads(statep.read_text());
        if st['root_sha256']!=rh:raise SystemExit('root hash mismatch')
        for c in st['cubes'].values():
            if c['status']=='ACTIVE':c['status']='PENDING'
            if c['status']=='CERT_ACTIVE':c['status']='CERT_PENDING'
    else:
        cubes={};d=a.initial_depth
        for m in range(1<<d):
            bits=format(m,f'0{d}b');lits=[sv[i] if b=='1' else -sv[i] for i,b in enumerate(bits)];cid='c'+bits;cubes[cid]={'id':cid,'depth':d,'lits':lits,'status':'PENDING','parent':None}
        st={'format':'CONWAY99-FIXED-K3-PARALLEL-CERT-1','root_sha256':rh,'started_at':time.time(),'cubes':cubes,'splits':0,'parameters':vars(a)};save(statep,st)
    def persist():save(statep,st)
    def split(c):
        d=c['depth'];v=sv[d];c['status']='SPLIT';c['split_var']=v
        for bit,lit in [('0',-v),('1',v)]:
            cid=c['id']+bit
            if cid not in st['cubes']:st['cubes'][cid]={'id':cid,'depth':d+1,'lits':c['lits']+[lit],'status':'PENDING','parent':c['id']}
        st['splits']+=1
    def cov():
        leaves=[c for c in st['cubes'].values() if c['status']!='SPLIT'];total=sum((weight(c) for c in leaves),Fraction())
        if total!=1:raise RuntimeError(f'coverage invariant {total}')
        return sum((weight(c) for c in leaves if c['status']=='CERTIFIED'),Fraction())
    pool=cf.ThreadPoolExecutor(max_workers=a.workers);cpool=cf.ThreadPoolExecutor(max_workers=1);futs={};cfut=None;ccid=None;last=0;cert_events=[]
    try:
        while True:
            if any(c['status']=='SAT' for c in st['cubes'].values()):print('=== CAMPAIGN_COMPLETE_WITH_SAT_QUOTIENT ===',flush=True);break
            cv=cov()
            if cv==1:st['status']='UNSAT_CERTIFIED';st['ended_at']=time.time();persist();print('=== CAMPAIGN_PASS coverage=100% all leaves LRAT+Cake certified ===',flush=True);break
            if shutil.disk_usage(run).free<a.disk_floor_gib*1024**3:raise RuntimeError('disk floor')
            pend=sorted((c for c in st['cubes'].values() if c['status']=='PENDING'),key=lambda c:(c['depth'],c['id']))
            while pend and len(futs)<a.workers:
                c=pend.pop(0);c['status']='ACTIVE';f=pool.submit(solve_one,root,dict(c),jobs/c['id'],a.cadical,a.leaf_seconds,a.disk_floor_gib);futs[f]=c['id']
            for f in [x for x in futs if x.done()]:
                cid=futs.pop(f);c=st['cubes'][cid];r=f.result();c['last_solve']=r;k=r['kind']
                if k=='UNSAT':
                    if r['proof_bytes']>a.proof_max_gib*1024**3:cleanup(jobs/cid);split(c)
                    else:c['status']='CERT_PENDING'
                elif k=='TIMEOUT':cleanup(jobs/cid);split(c)
                elif k=='SAT':c['status']='SAT';st['status']='SAT_QUOTIENT_VERIFIED';st['sat_cube']=cid
                elif k=='RESOURCE':c['status']='PENDING';persist();raise RuntimeError('resource stop')
                else:c['status']='ERROR';persist();raise RuntimeError(f'{cid}: {k}')
            if cfut is None:
                q=sorted((c for c in st['cubes'].values() if c['status']=='CERT_PENDING'),key=lambda c:(c['depth'],c['id']))
                if q:
                    c=q[0];c['status']='CERT_ACTIVE';ccid=c['id'];cfut=cpool.submit(certify,jobs/ccid,dict(c),a.lrat_check,a.cake)
            elif cfut.done():
                c=st['cubes'][ccid];r=cfut.result();cfut=None
                if not r.get('ok'):c['status']='ERROR';c['cert_error']=r;persist();raise RuntimeError(f'certificate failure {ccid}: {r}')
                c['status']='CERTIFIED';c['certificate']=r;cert_events.append((time.time(),float(weight(c))));ccid=None
            persist();now=time.time()
            if now-last>=a.status_seconds:
                cv=cov();cnt={}
                for c in st['cubes'].values():cnt[c['status']]=cnt.get(c['status'],0)+1
                recent=[x for x in cert_events if x[0]>=now-7200];eta='unknown'
                if len(recent)>=2:
                    dt=recent[-1][0]-recent[0][0];dw=sum(x[1] for x in recent)
                    if dt>0 and dw>0:eta=f'{(1-float(cv))/(dw/dt)/3600:.2f}h(weighted)'
                leaves=[c for c in st['cubes'].values() if c['status']!='SPLIT'];md=max(c['depth'] for c in leaves)
                print(f"STATUS elapsed={(now-st['started_at'])/3600:.2f}h coverage={float(cv*100):.4f}% certified={cnt.get('CERTIFIED',0)} active={cnt.get('ACTIVE',0)} pending={cnt.get('PENDING',0)} certq={cnt.get('CERT_PENDING',0)+cnt.get('CERT_ACTIVE',0)} splits={st['splits']} max_depth={md} disk_free={shutil.disk_usage(run).free/1024**3:.1f}GiB ETA={eta}",flush=True);last=now
            time.sleep(1)
    except KeyboardInterrupt:
        st['status']='STOPPED_RESUMABLE';persist();print('STOPPED_RESUMABLE',flush=True);raise
    finally:
        pool.shutdown(wait=False,cancel_futures=True);cpool.shutdown(wait=False,cancel_futures=True)
if __name__=='__main__':main()
