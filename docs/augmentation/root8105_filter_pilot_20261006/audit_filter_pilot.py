"""Read-only closure/selection audit. Does not rerun any sampler or census."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

parser=argparse.ArgumentParser()
parser.add_argument('package',type=Path)
parser.add_argument('run',type=Path)
parser.add_argument('output',type=Path)
a=parser.parse_args()
sys.path.insert(0,str(a.package.resolve()))
from census import audit_start
from runtime import connect, fingerprint, digest
from plan import jobs, keys
from kernel import Geo

con=connect(a.run,readonly=True)
assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
audit_start(con)
assert con.execute('SELECT COUNT(*) FROM attempts WHERE ended IS NULL').fetchone()[0]==0
assert con.execute('SELECT COUNT(*) FROM sessions WHERE ended IS NULL').fetchone()[0]==0
assert con.execute('SELECT COUNT(*) FROM attempts WHERE cpu_exact!=1').fetchone()[0]==0
assert con.execute("SELECT COUNT(*) FROM requests WHERE state='OPEN'").fetchone()[0]==0
assert dict(con.execute('SELECT state,COUNT(*) FROM roots GROUP BY state'))=={'DONE':25}
expected={j['id']:j for j in jobs()}
unique=set(); relations=collections.Counter(); all_relations=collections.Counter(); variants={v:{'reject':0,'cpu_s':0.0} for v in ['F','F_LD','F_CAP','F_LD_CAP']};g=Geo()
for item in con.execute('SELECT * FROM results'):
    data=json.loads(item['payload']); root=expected[item['root']]
    assert digest(data)==item['digest']
    assert set(data['counts'])==keys(root)
    attempt=con.execute('SELECT * FROM attempts WHERE id=?',(item['attempt'],)).fetchone()
    raw=json.loads((a.run/attempt['output']).read_text())
    assert raw==data
    if item['root']==0:
        assert data['counts']['1']['checks']==[]
        continue
    parent=int(root['row'],16)
    for t in range(1,84): all_relations[str((parent>>t&1,len(g.sets[0]&g.sets[t])))]+=1
    for t in root['targets']:
        entry=data['counts'][str(t['target'])]
        assert entry['width']==t['width']
        assert [x['rank'] for x in entry['cases']]==t['ranks']
        relations[str((parent>>t['target']&1,len(g.sets[0]&g.sets[t['target']])))]+=1
        for case in entry['cases']:
            key=(root['id'],t['target'],case['rank']);assert key not in unique;unique.add(key)
            for v in variants:
                variants[v]['reject']+=not case['variants'][v]['pass']
                variants[v]['cpu_s']+=case['variants'][v]['cpu_s']
assert len(unique)==4608
preserved=json.loads((a.run/'calibration_receipts.json').read_text())
assert all(con.execute('SELECT attempt,digest FROM results WHERE root=?',(v['root'],)).fetchone()[:]==(v['attempt'],v['digest']) for v in preserved)
sessions=[dict(x) for x in con.execute('SELECT id,started,ended,cpu,state FROM sessions ORDER BY started')]
summary=json.loads((a.run/'summary.json').read_text())
res={'status':'PASS','scope':'read-only receipt and fixed-selection audit, not a repeated calculation',
     'code_hash':fingerprint()['code_hash'],'states':len(unique),'sample_jobs':24,'control_jobs':1,
     'independent_rejection_controls':'NOT_APPLICABLE_NO_REJECTIONS_IN_FIXED_SAMPLE',
     'calibration_receipts_preserved':len(preserved),'variants':variants,
     'selected_target_relation_counts':dict(relations),'all_target_relation_counts_on_selected_roots':dict(all_relations),
     'relation_key':'(built-row adjacency e, label intersection cardinality)',
     'session_wall_utc_seconds':sum(x['ended']-x['started'] for x in sessions),
     'sessions':sessions,'totals':summary['totals'],'accounts':summary['accounts']}
a.output.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k not in ('sessions','accounts')},indent=2))
