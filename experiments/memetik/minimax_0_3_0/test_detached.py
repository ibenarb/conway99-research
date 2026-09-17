"""Keep the test container alive while the launching CLI exits normally."""
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

root = Path(__file__).parent
base = root/('detached_checked_'+str(time.time_ns()))
app = root/'Conway99_Minimax_Office_0.3.0.pyz'
command = [sys.executable,str(app)]
start = json.loads(subprocess.check_output(command+['start','--base-dir',str(base),'--hours','0.01'],text=True))
directory = Path(start['run_dir'])
print(json.dumps(start),flush=True)
limit = time.monotonic()+55
while time.monotonic()<limit:
    state=json.loads((directory/'status.json').read_text())
    if state['phase'] in ('FINISHED','STOPPED'):
        break
    time.sleep(1)
assert state['phase']=='FINISHED',state
summary=json.loads((directory/'summary.json').read_text())
for name,result in summary.items():
    assert result['status']=='WALLTIME_LIMIT',result
    with sqlite3.connect(directory/(name+'.sqlite')) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert db.execute('SELECT COUNT(*),SUM(closed) FROM nodes').fetchone()==(result['discovered'],result['expanded'])
    assert result['expanded']>(85 if name.startswith('HoG') else 13)
reject=subprocess.run(command+['resume','--base-dir',str(base)],capture_output=True,text=True)
assert reject.returncode!=0 and 'finished' in reject.stderr
report={'pass':True,'launcher_exits_and_workers_continue':True,'shared_deadline_seconds':36,'elapsed_wall_seconds':state['elapsed_wall_seconds_since_launch'],'both_real_tasks_advanced':True,'final_statuses':state['statuses'],'exact_SQL_counts':True,'finished_resume_rejected':True,'run_dir':str(directory)}
(root/'detached_test_report.json').write_text(json.dumps(report,indent=4)+'\n')
print(json.dumps(report,indent=4),flush=True)
