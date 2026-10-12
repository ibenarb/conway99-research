#!/usr/bin/env python3
"""C2 LOW pilot: preflight never starts production tasks."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from common import alive, host, identity, lock, proc, read, require, save, sha, verify_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    subs.add_parser('preflight')
    p = subs.add_parser('start')
    p.add_argument('--stage', choices=['initial', 'all'], default='initial')
    subs.add_parser('status')
    p = subs.add_parser('extend')
    p.add_argument('job')
    p.add_argument('seconds', type=float)
    for name in ['pause', 'resume']:
        p = subs.add_parser(name)
        p.add_argument('job')
    subs.add_parser('export')
    args = parser.parse_args()
    work = ROOT / 'work'
    work.mkdir(exist_ok=True)
    if args.action in ['preflight', 'start']:
        verify_manifest(ROOT)
        for path in (ROOT / 'bin').iterdir():
            path.chmod(path.stat().st_mode | 0o100)
    if args.action == 'preflight':
        guard = lock(work / 'preflight.lock')
        controller_guard = lock(work / 'controller.lock')
        from prepare import prepare
        from validate import controls
        resources = host(work)
        require(resources['available_ram_gib'] >= 2 and resources['linux_free_gib'] >= 5, 'PREFLIGHT_NEEDS_2_GIB_RAM_AND_5_GIB_DISK')
        save(work / 'target_resources.json', resources)
        print('RESOURCE_CHECK', json.dumps(resources), flush=True)
        prepare()
        controls()
        print('LOW_PREFLIGHT_PASS — no pilot tasks started', flush=True)
    elif args.action == 'start':
        require(read(work / 'validation.json', {}).get('status') == 'PASS', 'RUN_PREFLIGHT_FIRST')
        require(read(work / 'prepare.json', {}).get('status') == 'PASS', 'RUN_PREFLIGHT_FIRST')
        guard = lock(work / 'launch.lock')
        old = read(work / 'controller_launch.json', {})
        require(not alive(old.get('process')), 'CONTROLLER_ALREADY_RUNNING')
        # Detect an independent controller, including one launched manually.
        probe = lock(work / 'controller.lock')
        probe.close()
        if (work / 'controller_error.json').exists():
            (work / 'controller_error.json').rename(work / ('previous_controller_error_' + str(time.time_ns()) + '.json'))
        with (work / 'controller.log').open('ab') as output:
            child = subprocess.Popen([sys.executable, '-u', str(ROOT / 'src/control.py'), args.stage],
                    stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        save(work / 'controller_launch.json', {'process': proc(child.pid), 'stage': args.stage, 'started_unix': time.time()})
        time.sleep(0.3)
        require(child.poll() is None or child.returncode == 0, 'CONTROLLER_START_FAILED; inspect work/controller.log')
        print('LAUNCHED', child.pid, 'stage', args.stage)
    elif args.action == 'status':
        jobs = {}
        for p in sorted((work / 'jobs').glob('*/state.json')):
            state = read(p)
            if state.get('phase') != 'FINISHED':
                jobs[p.parent.name] = {k:state.get(k) for k in ['phase','cpu_s','time_extension_request','resource_reasons','peak_rss_bytes','output_bytes','updated_unix']}
        print(json.dumps({'controller': read(work / 'status.json'), 'live_jobs': jobs,
              'error': read(work / 'controller_error.json'), 'found_graph': read(work / 'FOUND_GRAPH.json')}, indent=2))
    elif args.action in ['extend', 'pause', 'resume']:
        require(all(c.isalnum() or c in '_-' for c in args.job), 'BAD_JOB_ID')
        d = work / 'jobs' / args.job
        require((d / 'spec.json').exists(), 'UNKNOWN_JOB')
        if args.action == 'extend':
            require(args.seconds >= 0, 'NONNEGATIVE_SECONDS_REQUIRED')
            previous = read(d / 'control.json', {})
            save(d / 'control.json', {'sequence': previous.get('sequence', 0) + 1, 'extend_seconds': args.seconds})
            print('STOP_REQUESTED' if args.seconds == 0 else 'EXTENSION_REQUESTED')
        elif args.action == 'pause':
            (d / 'PAUSE').touch()
            print('PAUSE_REQUESTED')
        else:
            (d / 'PAUSE').unlink(missing_ok=True)
            print('MANUAL_PAUSE_CLEARED; resource guards remain active')
    else:
        path = ROOT / ('LOW_diagnosis_' + time.strftime('%Y%m%d_%H%M%S') + '.zip')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in sorted(work.rglob('*')):
                if p.is_file() and p.suffix in ['.json', '.jsonl', '.log']:
                    z.write(p, p.relative_to(ROOT))
            z.write(ROOT / 'inputs/pilot.json', 'inputs/pilot.json')
            z.write(ROOT / 'config.json', 'config.json')
        print(json.dumps(identity(path), indent=2))


if __name__ == '__main__':
    main()
