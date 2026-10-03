"""Bounded beam exploration. All global outcomes remain pilot outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import resource
import signal
import time
from pathlib import Path

from core import Geometry, atomic, encode, enumerate_projection, pack, unpack

STOP = False


def stop(signum, frame):
    global STOP
    STOP = True


def limits(memory_gib, cpu_s):
    resource.setrlimit(resource.RLIMIT_AS, (int(memory_gib * 2**30), int(memory_gib * 2**30)))
    hard = max(2, int(cpu_s + 30))
    resource.setrlimit(resource.RLIMIT_CPU, (hard, hard + 1))
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('job')
    parser.add_argument('directory')
    parser.add_argument('--cpu', type=float, required=True)
    parser.add_argument('--memory', type=float, default=1.5)
    args = parser.parse_args()
    limits(args.memory, args.cpu)
    job = json.loads(Path(args.job).read_text())
    out = Path(args.directory)
    out.mkdir(parents=True, exist_ok=True)
    start_cpu, start_wall = time.process_time(), time.monotonic()
    g = Geometry(job.get('m', 7))
    cfg = job['config']
    checkpoint = out / 'checkpoint.json'
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text())
    else:
        state = {'depth': 1, 'frontier': [pack({0: int(job['row'], 16)})],
                 'parent': 0, 'target_index': 0, 'targets': None, 'pool': [],
                 'serial': 0, 'max_depth': 1, 'observed_models': 0,
                 'closed_projections': 0, 'limited_projections': 0,
                 'finished': False, 'restarts': 0, 'proof_candidates': [], 'levels': []}
    rng = random.Random(job['seed'])
    outcome = 'CPU_LIMIT_UNKNOWN'
    try:
        while state['depth'] < cfg['target_depth'] and state['frontier'] and not STOP:
            if time.process_time() - start_cpu >= args.cpu:
                break
            level_start = time.process_time()
            depth = state['depth']
            # Fair-share remaining budget across remaining target levels. Deepening
            # never waits for a shallow census to exhaust a huge projection.
            remaining = max(0, args.cpu - (time.process_time() - start_cpu))
            level_budget = max(cfg['node_cpu_s'], remaining / max(1, cfg['target_depth'] - depth))
            pool = {g.key(unpack(s)): s for s in state['pool']}
            level_models, level_tests, level_complete = 0, 0, 0
            while state['parent'] < len(state['frontier']) and not STOP:
                if time.process_time() - start_cpu >= args.cpu:
                    break
                if time.process_time() - level_start >= level_budget and pool:
                    break
                rows = unpack(state['frontier'][state['parent']])
                g.verify(rows)
                if state['targets'] is None:
                    target_rng = random.Random(job['seed'] + depth * 1000003 + state['parent'] + state['restarts'] * 999983)
                    state['targets'] = g.targets(rows, job['arm'], target_rng, cfg['target_choices'])
                    state['target_index'] = 0
                while state['target_index'] < len(state['targets']) and not STOP:
                    remaining = args.cpu - (time.process_time() - start_cpu)
                    if remaining <= 0:
                        break
                    target = state['targets'][state['target_index']]
                    encode_start = time.process_time()
                    cnf, variables = encode(g, rows, target)
                    encode_cpu = time.process_time() - encode_start
                    remaining = args.cpu - (time.process_time() - start_cpu)
                    if remaining <= 0:
                        break
                    serial = state['serial']
                    path = out / 'enumerations' / f'{serial:07d}'
                    # A crash during an enumeration preserves it, then a resumed
                    # cleanly accounted attempt uses a new serial number.
                    while path.exists():
                        serial += 1
                        path = out / 'enumerations' / f'{serial:07d}'
                    sample, meta = enumerate_projection(
                        g, rows, target, cnf, variables,
                        min(cfg['node_cpu_s'], remaining), cfg['node_wall_s'],
                        cfg['projection_cap'], cfg['row_reservoir'], job['seed'] + serial,
                        artifact=path)
                    meta.update({'encode_cpu_s': encode_cpu, 'parent_index': state['parent'],
                                 'root_id': job['root_id'], 'arm': job['arm'],
                                 'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
                    atomic(path / 'enumeration.json', meta)
                    state['serial'] = serial + 1
                    state['observed_models'] += meta['count']
                    level_models += meta['count']
                    level_tests += 1
                    if meta['status'] == 'PROJECTED_ENUMERATION_COMPLETE':
                        level_complete += 1
                        state['closed_projections'] += 1
                        if len(state['proof_candidates']) < cfg['proofs_per_job']:
                            state['proof_candidates'].append(str(path.resolve()))
                    else:
                        state['limited_projections'] += 1
                    canon_start = time.process_time()
                    sample_duplicates = 0
                    for row in sample:
                        child = dict(rows)
                        child[target] = row
                        g.verify(child)
                        key = g.key(child)
                        sample_duplicates += int(key in pool)
                        pool.setdefault(key, pack(child))
                    # Exact certificate bytes determine equality. Hashes are used
                    # ONLY as a deterministic sampling priority, not equality.
                    if len(pool) > cfg['beam_width']:
                        selected = sorted(pool, key=lambda k: hashlib.sha256(
                            str(job['seed'] + state['restarts']).encode() + k).digest())[:cfg['beam_width']]
                        pool = {k: pool[k] for k in selected}
                    meta.update({'canonical_cpu_s': time.process_time() - canon_start,
                                 'sampled_children': len(sample), 'sample_duplicates': sample_duplicates})
                    atomic(path / 'enumeration.json', meta)
                    state['pool'] = list(pool.values())
                    state['target_index'] += 1
                    if pool and depth + 1 > state['max_depth']:
                        state['max_depth'] = depth + 1
                        atomic(out / 'best.json', {'depth': depth + 1, 'rows': next(iter(pool.values())),
                                                  'verified_partial_only': True})
                    atomic(checkpoint, state)
                    if time.process_time() - level_start >= level_budget and pool:
                        break
                if state['target_index'] == len(state['targets']):
                    state['parent'] += 1
                    state['targets'] = None
                if time.process_time() - level_start >= level_budget and pool:
                    break
            if STOP or time.process_time() - start_cpu >= args.cpu:
                break
            state['levels'].append({'depth': depth, 'parents_available': len(state['frontier']),
                                    'parents_fully_visited': state['parent'], 'projections': level_tests,
                                    'complete_projections': level_complete, 'models_observed': level_models,
                                    'retained_canonical_states': len(pool),
                                    'cpu_s_this_segment': time.process_time() - level_start,
                                    'global_width_is_unknown': True})
            state.update({'depth': depth + 1, 'frontier': list(pool.values()), 'pool': [],
                          'parent': 0, 'target_index': 0, 'targets': None})
            if not state['frontier']:
                state['restarts'] += 1
                state.update({'depth': 1, 'frontier': [pack({0: int(job['row'], 16)})],
                              'pool': [], 'parent': 0, 'target_index': 0, 'targets': None})
            atomic(checkpoint, state)
        if STOP:
            outcome = 'PAUSED'
        elif state['max_depth'] >= cfg['target_depth']:
            outcome = 'TARGET_DEPTH_REACHED'
            state['finished'] = True
        elif not state['frontier']:
            outcome = 'SAMPLED_FRONTIER_EXHAUSTED_UNKNOWN'
            state['finished'] = True
        atomic(checkpoint, state)
    except MemoryError:
        outcome = 'MEMORY_LIMIT_UNKNOWN'
    except Exception:
        outcome = 'INTEGRITY_OR_WORKER_ERROR'
        raise
    finally:
        snapshot = time.process_time()
        atomic(out / 'worker_result.json', {'status': outcome, 'state': state,
                                           'cpu_s': snapshot - start_cpu,
                                           'wall_s': time.monotonic() - start_wall,
                                           'certified_root_exclusion': False})
    print(json.dumps({'status': outcome, 'max_depth': state['max_depth']}), flush=True)


if __name__ == '__main__':
    main()
