"""Resource-guarded entrypoint for long C2B1 closure audits; no campaign controller."""
from pathlib import Path
import argparse
import ctypes
import fcntl
import json
import os
import resource
import signal
import subprocess
import sys
import time
from resource_sensor import Sensor


def require(condition,message):
    if not condition:
        raise RuntimeError(message)


def limits(parent):
    require(ctypes.CDLL(None).prctl(1,signal.SIGKILL) == 0,'Cannot bind audit lifetime')
    if os.getppid() != parent:
        os.kill(os.getpid(),signal.SIGKILL)
    current_nice=os.getpriority(os.PRIO_PROCESS,0)
    if current_nice<15:
        os.nice(15-current_nice)
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(128*1024**2,128*1024**2))
    # No cumulative CPU cap: thousands of individually bounded replays may be needed.


def run(bundle,output,mode):
    root=Path(__file__).resolve().parent
    bundle,output=bundle.resolve(),output.resolve()
    require(not output.exists() and not output.is_relative_to(bundle) and not bundle.is_relative_to(output),'Output must be new and separate')
    lockfile=root.parent/'C2_BatchRecoveryIncremental_20261107/research.lock'
    require(lockfile.parent.is_dir(),'Established research-lock directory missing')
    with lockfile.open('a+b') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        output.mkdir(parents=True)
        sensor=Sensor(output)
        process=None
        try:
            sample,reasons=sensor.resources()
            require(not reasons,'RESOURCE_HOLD: '+repr((sample,reasons)))
            parent=os.getpid();begin=time.monotonic();last_progress=begin;size=0
            logfile=output/'audit.log'
            with logfile.open('xb') as stream:
                process=subprocess.Popen([sys.executable,str(root/'closure_gate.py'),str(bundle),str(output/'audit'),'--mode',mode],stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:limits(parent))
                while process.poll() is None:
                    time.sleep(0.2)
                    sample,reasons=sensor.resources()
                    require(not reasons,'RESOURCE_HOLD: '+repr((sample,reasons)))
                    current=logfile.stat().st_size
                    if current != size:
                        size=current;last_progress=time.monotonic()
                    require(time.monotonic()-last_progress<300,'Audit made no progress for300seconds')
                stream.flush();os.fsync(stream.fileno())
            require(process.returncode == 0,'Audit failed with code '+str(process.returncode))
            final=json.loads((output/'audit/FINAL_AUDIT.json').read_text())
            expected='PASS' if mode=='complete' else 'NONCLOSING_'+mode.upper()
            require(final['status']==expected and final['case_proved_unsat']==(mode=='complete'),'Unexpected closure status')
            result=dict(status='PASS',audit_status=final['status'],case_proved_unsat=final['case_proved_unsat'],seconds=time.monotonic()-begin,scope='Guarded audit; counting still requires complete bytechecked archive and Git/release documentation')
            (output/'RUN_RESULT.json').write_text(json.dumps(result,indent=4)+'\n')
            print(json.dumps(result),flush=True)
            return result
        except BaseException as error:
            (output/'RUN_FAILED.json').write_text(json.dumps(dict(status='FAIL',case_proved_unsat=False,error=repr(error)),indent=4)+'\n')
            raise
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid,signal.SIGKILL)
                process.wait()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('bundle',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--mode',choices=['complete','subset','structure'],default='complete')
    args=parser.parse_args()
    run(args.bundle,args.output,args.mode)
