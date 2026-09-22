"""Bounded auxiliary child: CPU receipts are finalized by the parent."""
import boot
from util import *
import math

def main():
    import util
    def request_stop(*args):
        util.ABORT = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    action, destination, ceiling = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3])
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(ceiling), math.ceil(ceiling) + 1))
    resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
    if action == "spin":
        before = own_cpu()
        time.sleep(0.1)
        after = own_cpu()
        assert after - before < 0.05
        value = 1
        while own_cpu() < ceiling - 1 and not abort_requested():
            for _ in range(1000):
                value = (value * 1664525 + 1013904223) & 0xffffffff
        atomic(destination, {"self_cpu": own_cpu(), "wait_cpu": after - before, "counter": value})
    elif action == "controls":
        from checks import run_checks
        import controls as base_controls
        def budget_guard(self):
            if abort_requested() or own_cpu() + child_cpu() >= ceiling - 5:
                raise RuntimeError("Control auxiliary interrupted or CPU exhausted")
        base_controls.Guard.check = budget_guard
        result = run_checks(Path(sys.argv[4]) if len(sys.argv) > 4 else None)
        atomic(destination, result)
    elif action == "harvest":
        from harvest import harvest
        result = harvest(Path(sys.argv[4]), ceiling)
        atomic(destination, result)
    else:
        raise ValueError("Unknown auxiliary action")

if __name__ == "__main__":
    main()
