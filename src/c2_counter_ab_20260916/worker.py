"""One no-proof solver process, exact child CPU accounting and optional graph check."""
import ctypes
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from common import LOG_LIMIT, save, sha
from c2_reference import CNF, Frame, read_primary_model, reconstruct, verify_graph


def bind_parent(expected):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG')
    if os.getppid() != expected:
        os._exit(125)


def classify(code, lines):
    states = {line.strip() for line in lines if line.startswith('s ')}
    if code == 20 and states == {'s UNSATISFIABLE'}:
        return 'UNSAT_UNCERTIFIED'
    if code == 10 and states == {'s SATISFIABLE'}:
        return 'SAT_PENDING_GRAPH_CHECK'
    if code == 0 and states <= {'s UNKNOWN', 's INDETERMINATE'}:
        return 'OPEN_BUDGET'
    return 'SOLVER_ERROR'


def run(spec, solver, seconds, folder, parent):
    bind_parent(parent)
    folder = Path(folder)
    log = folder/'solver.log'
    started = time.monotonic()
    if sha(spec['cnf']) != spec['cnf_sha256']:
        raise ValueError('Job CNF hash mismatch')
    # Exactly one positional input: NO proof destination and NO LRAT flags.
    command = [str(solver), '--seed='+str(spec['seed']), '-t', str(seconds), spec['cnf']]
    worker_pid = os.getpid()

    def limits():
        bind_parent(worker_pid)
        resource.setrlimit(resource.RLIMIT_FSIZE, (LOG_LIMIT, LOG_LIMIT))
        resource.setrlimit(resource.RLIMIT_CPU, (seconds+30, seconds+60))
        resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    with log.open('wb') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, preexec_fn=limits, timeout=seconds+90)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    with log.open(errors='replace') as stream:
        status = classify(result.returncode, stream)
    record = dict(spec, status=status, exit=result.returncode, command=command,
                  budget_seconds=seconds, solver_wall_seconds=round(time.monotonic()-started, 3),
                  solver_cpu_seconds=round(usage.ru_utime+usage.ru_stime, 3),
                  peak_rss_KiB=usage.ru_maxrss, log_bytes=log.stat().st_size, proof_files_created=0)
    if sha(spec['cnf']) != spec['cnf_sha256']:
        record['status'] = 'INPUT_CHANGED'
    elif status == 'SAT_PENDING_GRAPH_CHECK':
        cnf, frame = CNF(), Frame(spec.get('k', 14))
        try:
            frame.allocate(cnf)
            values = read_primary_model(log, len(frame.map))
            graph = reconstruct(frame, values)
            if not verify_graph(graph, frame.k) or not all(values[abs(v)] == (v > 0) for v in spec['assumptions']):
                raise ValueError('Reconstructed graph or cube check failed')
            save(folder/'graph.json', graph)
            record['status'] = 'GRAPH_VERIFIED'
        except (ValueError, KeyError) as error:
            record.update(status='INVALID_SAT_MODEL', error=repr(error))
        finally:
            cnf.close()
    save(folder/'result.json', record)
    return record


if __name__ == '__main__':
    specfile, solver, seconds, folder, parent = sys.argv[1:]
    try:
        run(json.loads(Path(specfile).read_text()), solver, int(seconds), folder, int(parent))
    except BaseException as error:
        save(Path(folder)/'result.json', {'status': 'WORKER_ERROR', 'error': repr(error)})
        raise
