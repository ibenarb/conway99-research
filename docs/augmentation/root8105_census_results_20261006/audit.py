import sys,json,hashlib,math,collections,random,time,gc,concurrent.futures
from pathlib import Path
SRC=Path(sys.argv[1]); RUN=Path(sys.argv[2]); OUT=Path(sys.argv[3]); OUT.mkdir(exist_ok=True,parents=True)
sys.path.insert(0,str(SRC))
from runtime import connect,get,digest,fingerprint
from census import audit_start,checked_payload,report
from kernel import Geo,VertexSampler,load_roots

def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
def job(pair):
 rid,t,expected,row=pair
 start=time.process_time(); s=VertexSampler(Geo(),int(row,16),t); actual=s.total;s.rec.cache_clear();del s;gc.collect()
 return dict(root=rid,target=t,expected=expected,actual=actual,match=actual==expected,cpu_s=time.process_time()-start)

if __name__=='__main__':
 start=time.process_time();con=connect(RUN,readonly=True);audit_start(con)
 assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 exports=[json.loads(l) for l in (RUN/'census.jsonl').read_text().splitlines()]
 roots=load_roots(); assert len(exports)==len(roots)==8105
 assert [r['id'] for r in exports]==list(range(1,8106))
 for r,orig in zip(exports,roots):
  rid=r['id'];assert all(r[k]==v for k,v in orig.items())
  result=con.execute('select * from results where root=?',(rid,)).fetchone()
  a=con.execute('select * from attempts where id=?',(result['attempt'],)).fetchone()
  spec=json.loads((RUN/'attempts'/f"{a['id']}.input.json").read_text())
  p=checked_payload(RUN/'attempts'/f"{a['id']}.output.json",spec)
  assert p==json.loads(result['payload']) and digest(p)==result['digest']
  assert p['state']=='COMPLETE' and p['error'] is None and a['state']=='COMPLETE' and a['cpu_exact']==1
  assert spec['root']==orig and spec['root_row_hash']==digest(orig['row']) and not spec['test_mode']
  for k in ('model','root_hash','model_hash'): assert p[k]==get(con,k)==r[k]
  assert p['code_hash']==fingerprint()['code_hash']==r['code_hash']
  assert set(p['counts'])==set(map(str,range(1,84)))
  ws=[p['counts'][str(t)]['width'] for t in range(1,84)]
  assert ws==r['widths_t1_to_t83'] and min(ws)==r['min']
  assert r['argmin']==[t for t in range(1,84) if ws[t-1]==min(ws)]
  assert a['cpu']+0.001>=p['worker_cpu_s']
 summary=json.loads((RUN/'summary.json').read_text()); rep=report(con)
 assert all(summary[k]==v for k,v in rep.items())
 assert sum(r['min'] for r in exports)==summary['sum_min_width_completed_roots']==4846403679
 assert con.execute('select count(*) from attempts').fetchone()[0]==8105
 sessions=[dict(r) for r in con.execute('select * from sessions order by started')]
 meta={r['key']:json.loads(r['value']) for r in con.execute('select * from meta') if r['key'].startswith(('helper_','host_clock_','warnings_'))}
 requests=[dict(r) for r in con.execute('select * from requests')]
 def stats(xs):
  xs=sorted(xs);return {'n':len(xs),'min':xs[0],'p25':xs[(len(xs)-1)//4],'median':xs[(len(xs)-1)//2],'p75':xs[3*(len(xs)-1)//4],'max':xs[-1],'sum':sum(xs)}
 analysis={str(typ):{'root_minima':stats([r['min'] for r in exports if r['type']==typ]),'all_widths':stats([w for r in exports if r['type']==typ for w in r['widths_t1_to_t83']])} for typ in (0,1,2)}
 save('integrity.json',dict(status='PASS',archive_sha256='84751007d21c17f234cbc11a19b32a85c50a2ae29791ea959111a6a54ba5908d',summary=summary,sessions=sessions,clock_meta=meta,requests=requests,request_file=json.loads((RUN/'time_request.json').read_text()),inputs=[dict(r) for r in con.execute('select * from inputs')],stats=analysis,all_root_minima=stats([r['min'] for r in exports]),audit_cpu_s=time.process_time()-start))
 print('INTEGRITY_PASS',json.dumps(analysis),flush=True)
 # Thirty disjoint strata: root type x width rank decile within type, ties by root,target.
 # Allocate exactly 13455 using proportional largest remainders, then fixed-seed sampling.
 strata={}
 for typ in (0,1,2):
  pairs=sorted([(w,r['id'],t,r['row']) for r in exports if r['type']==typ for t,w in enumerate(r['widths_t1_to_t83'],1)])
  for d in range(10): strata[(typ,d)]=pairs[len(pairs)*d//10:len(pairs)*(d+1)//10]
 N=672715; n=13455; alloc={k:n*len(v)//N for k,v in strata.items()}
 for k in sorted(strata,key=lambda k:(-(n*len(strata[k])%N),k))[:n-sum(alloc.values())]: alloc[k]+=1
 rng=random.Random(810520261006); sample=[]
 for k,v in sorted(strata.items()):
  for w,rid,t,row in rng.sample(v,alloc[k]): sample.append((rid,t,w,row))
 sample.sort();assert len(sample)==n and len({p[:2] for p in sample})==n
 save('sample_manifest.json',dict(seed=810520261006,selection='type x within-type width rank deciles; largest-remainder proportional allocation; sample without replacement',population=N,size=n,strata=[dict(type=k[0],decile=k[1],population=len(v),sample=alloc[k]) for k,v in sorted(strata.items())],pairs=sample))
 print('SAMPLE_FIXED',hashlib.sha256((OUT/'sample_manifest.json').read_bytes()).hexdigest(),flush=True)
 wall=time.monotonic(); cpu=0;errors=0
 with (OUT/'independent.jsonl').open('w') as f, concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool:
  for i,res in enumerate(pool.map(job,sample,chunksize=8),1):
   f.write(json.dumps(res)+'\n'); cpu+=res['cpu_s'];errors+=not res['match']
   if i%200==0: f.flush();print('PROGRESS',i,n,'cpu_s',round(cpu,2),'wall_s',round(time.monotonic()-wall,2),'mismatches',errors,flush=True)
 save('independent_summary.json',dict(status='PASS' if errors==0 else 'FAIL',pairs=n,mismatches=errors,worker_task_cpu_s=cpu,wall_s=time.monotonic()-wall,algorithm='kernel.VertexSampler Python-int vertex recursion; shares geometry/constraints with edge DP; not a wholly independent model encoder',sample_sha256=hashlib.sha256((OUT/'sample_manifest.json').read_bytes()).hexdigest()))
 print('INDEPENDENT_FINISHED',errors,flush=True)
