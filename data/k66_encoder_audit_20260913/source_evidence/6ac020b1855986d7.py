#!/usr/bin/env python3
"""Start or resume the frozen Conway99 k66 certification pilot."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shlex
import shutil
import sys
import time
import zipfile
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path.home() / 'conway99_workspace/conway99-research')
    ap.add_argument('--run-dir', type=Path, help='New output directory; must not already exist')
    ap.add_argument('--resume', type=Path, help='Resume exactly this previously prepared directory')
    ap.add_argument('--prepare-only', action='store_true', help='Prepare CNFs without launching SAT or checkers')
    ap.add_argument('--controls-only', action='store_true', help='Run toolchain controls, then stop before research solvers')
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--cake-heap-mb', type=int, default=16384)
    ap.add_argument('--disk-floor-gib', type=float, default=75.0)
    ap.add_argument('--status-seconds', type=float, default=600.0)
    ap.add_argument('--root-cnf', type=Path)
    ap.add_argument('--cadical')
    ap.add_argument('--lrat-check')
    ap.add_argument('--cake')
    args = ap.parse_args()
    if args.resume and args.run_dir:
        ap.error('--resume and --run-dir are mutually exclusive')
    if args.prepare_only and args.controls_only:
        ap.error('--prepare-only and --controls-only are mutually exclusive')
    if not 1 <= args.workers <= 8 or not 1 <= args.status_seconds <= 600:
        ap.error('workers must be 1..8, status-seconds must be 1..600')
    if args.disk_floor_gib < 75 or not 16384 <= args.cake_heap_mb <= 32768:
        ap.error('Production safety floors: disk >=75 GiB; Cake heap 16384..32768 MiB')
    archive = Path(sys.argv[0]).resolve()
    if not zipfile.is_zipfile(archive):
        raise SystemExit('Run the complete .pyz file, not extracted __main__.py')
    if args.resume:
        run = args.resume.expanduser().resolve()
        if not (run / 'manifest.json').is_file():
            raise SystemExit('Resume manifest missing; no files modified')
    else:
        run = (args.run_dir or Path.home() / 'conway99_workspace/o3_reconciliation_runs' /
               ('k66_v4_cert_' + time.strftime('%Y%m%d_%H%M%S') + f'_{time.time_ns() % 1000000:06d}')).expanduser().resolve()
        run.mkdir(parents=True, exist_ok=False)
    lock = (run / 'runner.lock').open('a+')
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('This pilot directory already has an active runner')
    source = run / 'source'
    source.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        digests = json.loads(package.read('payload_sha256.json'))
        for name, expected in digests.items():
            if Path(name).name != name:
                raise SystemExit('Invalid package payload path')
            content = package.read(name)
            if hashlib.sha256(content).hexdigest() != expected:
                raise SystemExit('Package payload corruption: ' + name)
            path = source / name
            if path.exists():
                if path.read_bytes() != content:
                    raise SystemExit('Refusing to change existing run source: ' + name)
            else:
                path.write_bytes(content)
    sys.path.insert(0, str(source))
    from k66_prepare import prepare, save, sha, verify_prepared
    from k66_runtime import Safety, execute_pilot, find_tools, handoff, pin_tools, tool_controls
    print('K66_RUN_DIRECTORY ' + str(run), flush=True)
    print('Repository read-only: pinned Git objects, no checkout, no pull, no commits.', flush=True)
    save(run / 'package.json', {'archive': str(archive), 'sha256': sha(archive), 'payloads': digests})
    resume_cmd = [sys.executable, str(archive), '--resume', str(run), '--repo', str(args.repo),
                  '--workers', str(args.workers), '--cake-heap-mb', str(args.cake_heap_mb),
                  '--disk-floor-gib', str(args.disk_floor_gib), '--status-seconds', str(args.status_seconds)]
    for option, value in [('--cadical', args.cadical), ('--lrat-check', args.lrat_check), ('--cake', args.cake)]:
        if value:
            resume_cmd.extend([option, value])
    (run / 'resume_command.txt').write_text(shlex.join(resume_cmd) + '\n')
    try:
        Safety(run, disk_floor=args.disk_floor_gib).check()
        if args.resume:
            manifest = verify_prepared(run)
        else:
            hint = args.root_cnf or Path.home() / 'conway99_workspace/o3_reconciliation_runs/review_reconciled_20260907/fixed_triangle/fixed_triangle_o3_quotient.cnf'
            manifest = prepare(args.repo, run, source, hint)
        if args.prepare_only:
            print('K66_PREPARE_ONLY_PASS No SAT or checker process started.', flush=True)
            handoff(run)
            return
        tools = find_tools(Path.home(), {'cadical': args.cadical, 'lrat-check': args.lrat_check, 'cake_lpr': args.cake})
        frozen = pin_tools(run, tools)
        if args.controls_only:
            tool_controls(run, frozen, Safety(run, disk_floor=args.disk_floor_gib), args.cake_heap_mb)
            print('K66_CONTROLS_ONLY_PASS No research solver process started.', flush=True)
            handoff(run)
            return
        execute_pilot(run, manifest, frozen, workers=args.workers, heap_mb=args.cake_heap_mb,
                      disk_floor=args.disk_floor_gib, status_seconds=args.status_seconds)
    except BaseException as exc:
        if not (run / 'state.json').exists():
            save(run / 'startup_error.json', {'error': repr(exc), 'phase': 'PREPARATION_OR_TOOL_ADMISSION'})
            handoff(run)
        print('RESUME_COMMAND ' + shlex.join(resume_cmd), flush=True)
        raise
    finally:
        lock.close()


if __name__ == '__main__':
    main()
