import json,sys,statistics,hashlib,random,collections,datetime,sqlite3,tempfile
from pathlib import Path
SRC,RUN,OUT=map(Path,sys.argv[1:]);sys.path.insert(0,str(SRC))
from runtime import schema,close_requests
x=json.loads((OUT/'integrity.json').read_text());lines=(RUN/'controller.log').read_text().splitlines();s=[json.loads(l.split(' ',1)[1]) for l in lines if l.startswith('CENSUS_STATUS ')];h=[v for v in s if v['host_clock']]
sessions=x['sessions'];host=x['clock_meta'];summary=x['summary']
windows=sum(v['Windows_clock_process'] for k,v in host.items() if k.startswith('helper_cpu_'))
linuxhelpers=sum(v['Linux_children_excluding_workers'] for k,v in host.items() if k.startswith('helper_cpu_'))
clock=dict(status_records=len(s),clock_ok_records=sum(v['clock_ok'] for v in s),host_records=len(h),host_age_s=[min(v['utc']-v['host_clock']['utc_s'] for v in h),max(v['utc']-v['host_clock']['utc_s'] for v in h)],host_utc_vs_stopwatch_max_interval_difference_s=max(abs((v['host_clock']['utc_s']-h[0]['host_clock']['utc_s'])-(v['host_clock']['stopwatch_s']-h[0]['host_clock']['stopwatch_s'])) for v in h),status_utc_cadence_median_s=statistics.median(b['utc']-a['utc'] for a,b in zip(s,s[1:])),session_utc_durations_s=[v['ended']-v['started'] for v in sessions],min_mem_available_bytes=min(v['resources']['mem_available_bytes'] for v in s),windows_helpers_cpu_s=windows,linux_helpers_cpu_s=linuxhelpers,supervisor_only_cpu_s=summary['supervisor_cpu_s']-windows-linuxhelpers,aggregate_cpu_h=summary['aggregate_cpu_s']/3600,overrun_cpu_h=(summary['aggregate_cpu_s']-summary['budget_cpu_s'])/3600,warning_metadata={k:v for k,v in host.items() if k.startswith('warnings_')},limitation='No saved paired monotonic/host anchors or deltas: exact guest drift cannot be reconstructed; clock_ok false is not missing host clock.')
# Reproduce stale request mirror with unmodified rc3, only a disposable synthetic DB.
with tempfile.TemporaryDirectory() as tmp:
 con=sqlite3.connect(':memory:');schema(con);con.execute("insert into requests(id,state) values ('regression','OPEN')");con.commit();p=Path(tmp)/'time_request.json';p.write_text('{"state":"OPEN"}');close_requests(con,'CLOSED_COMPLETE');clock['request_mirror_regression']={'db':con.execute('select state from requests').fetchone()[0],'file':json.loads(p.read_text())['state']};assert clock['request_mirror_regression']=={'db':'CLOSED_COMPLETE','file':'OPEN'}
(OUT/'operations_analysis.json').write_text(json.dumps(clock,indent=2)+'\n')
# Future pilot selection only, no filter executions or state enumeration.
rows=[json.loads(l) for l in (RUN/'census.jsonl').read_text().splitlines()];rng=random.Random(810520261007);chosen=[]
for typ in (0,1,2):
 group=sorted((r for r in rows if r['type']==typ),key=lambda r:(r['min'],r['stab'],r['id']))
 for i in range(8):
  block=group[len(group)*i//8:len(group)*(i+1)//8];prefer=[r for r in block if (r['stab']==1)==(i%2==0)];r=rng.choice(prefer or block)
  ordered=sorted(range(1,84),key=lambda t:(r['widths_t1_to_t83'][t-1],t));targets=[ordered[0],ordered[41],ordered[-1]]
  chosen.append(dict(root=r['id'],type=typ,stab=r['stab'],min=r['min'],root_row=r['row'],targets=[dict(target=t,width=r['widths_t1_to_t83'][t-1],ranks=sorted(rng.sample(range(r['widths_t1_to_t83'][t-1]),min(64,r['widths_t1_to_t83'][t-1])))) for t in targets]))
pilot=dict(status='PROPOSAL_NOT_EXECUTED',seed=810520261007,selection='8 minimum-width rank blocks per type; alternate trivial/nontrivial stabilizer preference with fallback; random root within each block; ordered target ranks 0,41,82 (width,label); uniform 64 ranks without replacement per target',roots=chosen,states=sum(len(t['ranks']) for r in chosen for t in r['targets']),rules=['GC-01','GC-08','GC-16','GC-19','GC-20'])
(OUT/'filter_pilot_manifest.json').write_text(json.dumps(pilot,indent=2)+'\n')
print(json.dumps(clock,indent=2));print('PILOT',len(chosen),pilot['states'],hashlib.sha256((OUT/'filter_pilot_manifest.json').read_bytes()).hexdigest())
