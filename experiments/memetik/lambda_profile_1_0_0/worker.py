"""Isolated wait4-accounted profile worker."""
import boot
from support import *
from episodes import work


def run(directory, allocation):
    directory = Path(directory)
    task = read(directory / 'task.json')
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGXCPU):
        signal.signal(sig, stopped)
    hard = int(allocation)
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, hard - 1), hard))
    guard = Guard(allocation - 3)
    try:
        if task['kind'] == 'controls':
            from controls import controls
            result = controls(guard)
        elif task['kind'] == 'spin':
            end = own_cpu() + task['seconds']
            while own_cpu() < end:
                guard.check()
            result = {'status': 'DONE'}
        else:
            result = work(task, directory, guard)
    except Pause as error:
        result = {'status': 'PAUSED', 'reason': str(error)}
    result['self_cpu'] = own_cpu()
    atomic(directory / 'slice_result.json', result)


if __name__ == '__main__':
    run(sys.argv[1], float(sys.argv[2]))
