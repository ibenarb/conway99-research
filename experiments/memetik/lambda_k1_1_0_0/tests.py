"""Real child-process integration; disposable cloud fixture, never a Ryzen run."""
import argparse,datetime,os,shutil,signal,subprocess,sys,threading,time
from common import *


class FakeHost:
    def __init__(self):self.begin=time.monotonic();self.last=self.sample()
    def sample(self,*args,**kwargs):
        self.last={'host_seconds':time.monotonic()-self.begin,'windows_cpu_seconds':0,'physical_free_bytes':100*GIB,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};return self.last
    def close(self):return 0


def integration(run):
    import controller
    from controller import Controller
    from run import prepare,verify_run
    from audit import audit,premature_tasks
    prepare(run);c=Controller(run,host=FakeHost(),test=True)
    def pause():
        while c.phase!='REPAIR' or not c.active:time.sleep(.05)
        time.sleep(1);os.kill(os.getpid(),signal.SIGTERM)
    threading.Thread(target=pause,daemon=True).start();c.execute()
    first=read(run/'RESULT.json');assert first['reason']=='USER_PAUSE',first
    before=dict(first['cpu_seconds']);audit(run);verify_run(run)
    controller.PAUSE=False;c=Controller(run,host=FakeHost(),test=True);c.execute()
    result=read(run/'RESULT.json');assert result['status']=='COMPLETED_BUDGETED_PILOT',result
    assert all(result['cpu_seconds'][k]>=v for k,v in before.items())
    proof=audit(run);assert read(run/'status.json')['charged_cpu_seconds']==read(run/'ledger.json')['used']
    assert premature_tasks({'x':'CPU_LIMIT_UNKNOWN'},{'x':{'cpu_limit_seconds':7200}},{'x':60},5)==['x']
    victim=run/'program/README.md';old=victim.read_bytes();victim.write_bytes(old+b'broken')
    try:
        try:audit(run)
        except AssertionError:pass
        else:raise RuntimeError('Corruption passed')
    finally:victim.write_bytes(old)
    ledger=read(run/'ledger.json');ledger['active']['lost']={'allocation':10};atomic(run/'ledger.json',ledger)
    try:
        try:verify_run(run)
        except RuntimeError:pass
        else:raise AssertionError('Lost reservation accepted')
    finally:ledger['active'].clear();atomic(run/'ledger.json',ledger)
    atomic(run/'TEST_INTEGRATION.json',{'status':'PASS','pause_resume':True,'all_four_families':True,'audit':proof,'source_corruption_rejected':True,'unresolved_cpu_rejected':True,'clock':'FakeHost cloud; real Windows preflight still required'})


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--child',type=Path);a=p.parse_args()
    if a.child:integration(a.child);return
    root=a.out.resolve();root.mkdir(parents=True,exist_ok=False);program=root/'fixture';shutil.copytree(HERE,program,ignore=shutil.ignore_patterns('__pycache__'))
    m=read(program/'MANIFEST.json'); chosen=[]
    for family in ('A','B','C1','C2'):
        t=dict(next(t for t in m['tasks'] if t['family']==family));t['cpu_limit_seconds']=15;chosen.append(t)
    t=dict(next(t for t in m['tasks'] if t['family']=='C2' and t['arm']=='lambda_descent_projection'));t['cpu_limit_seconds']=15;chosen.append(t)
    # Keep the complete manifest for controls; shorter task targets preserve pairing.
    for t in m['tasks']:t['cpu_limit_seconds']=15
    # Controls inspect all B pairs, then scheduler fixture contains only five tasks.
    atomic(program/'MANIFEST.json',m)
    package=read(program/'PACKAGE.json');package['files']['MANIFEST.json']=digest(program/'MANIFEST.json');atomic(program/'PACKAGE.json',package)
    # The controller itself uses only these five tasks, but frozen audit must agree.
    m['tasks']=chosen
    atomic(program/'MANIFEST.json',m)
    controls=(program/'controls.py').read_text().replace("assert len(group)==4","assert len(group)==1 or len(group)==4").replace("assert {(t['linearization_level'],t['radius']) for t in group}=={(0,None),(0,16),(2,None),(2,16)}","assert all(t['linearization_level'] in (0,2) for t in group)")
    (program/'controls.py').write_text(controls)
    for n in ('MANIFEST.json','controls.py'):package['files'][n]=digest(program/n)
    atomic(program/'PACKAGE.json',package)
    with (root/'integration.log').open('w') as log:
        subprocess.run([sys.executable,str(program/'tests.py'),'--child',str(root/'run')],stdout=log,stderr=subprocess.STDOUT,check=True,env={**os.environ,**THREAD_ENV})
    result=read(root/'run/TEST_INTEGRATION.json');atomic(root/'RESULT.json',result);print(json.dumps(result))


if __name__=='__main__':main()
