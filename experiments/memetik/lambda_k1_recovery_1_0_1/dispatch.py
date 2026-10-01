"""One isolated worker for a frozen K1 task."""
import argparse, math, signal, threading, time
from common import *


def main():
    p=argparse.ArgumentParser();p.add_argument('task',type=Path);p.add_argument('directory',type=Path);p.add_argument('allowance',type=float);p.add_argument('--stop-cpu',type=float,required=True);a=p.parse_args()
    hard=max(1,math.floor(a.allowance-2));resource.setrlimit(resource.RLIMIT_CPU,(max(1,hard-3),hard));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    task=read(a.task);founder=next(g for g in read(HERE/'MANIFEST.json')['founders'] if g['id']==task['founder'])
    stop=threading.Event()
    def stopping(*_):stop.set()
    for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGXCPU):signal.signal(sig,stopping)
    try:
        if task['kind']=='cp':
            import worker
            for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGXCPU):signal.signal(sig,worker.stop)
            result=worker.solve_task(founder,task,a.directory,a.allowance,seed=task['seed'],stop_cpu=a.stop_cpu)
        else:
            module=__import__('catalog' if task['kind']=='catalog' else 'packing')
            result=module.run_task(founder,task,a.directory,a.allowance,a.stop_cpu,stop)
        result.update(process_cpu_seconds=cpu(),proc_cpu_seconds=process(os.getpid())['cpu'],python_process_time_seconds=time.process_time(),kind=task['kind'],arm=task['arm'])
        atomic(a.directory/'result.json',result)
    except BaseException as error:
        atomic(a.directory/'error.json',{'error':repr(error),'cpu_seconds':cpu()});raise


if __name__=='__main__':main()
