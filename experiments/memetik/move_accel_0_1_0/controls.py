"""Differential checks: complete ordered streams, RNG state and hard validity."""
import random
import time
from itertools import islice

import bootstrap
from common import core, checked, cpu
import moves
import fast_moves
from search import Guard


def stream(module, rows, family, rng, guard):
    if family in ('4x4', '4x6', '6x6'):
        return module.omega_moves(rows, family, rng, guard)
    owner = moves.reference if module is moves else module
    return getattr(owner, family+'_moves')(rows, rng, guard)


def check_cases(cases, seconds=300):
    guard = Guard(cpu()+seconds)
    records = []
    # Warm catalogue construction is charged to controls, excluded from speed ratios.
    moves.catalogue(4)
    moves.catalogue(6)
    for case in cases:
        rows, _ = checked(case['graph6'], case['arm'])
        families = ('4x4', '4x6', '6x6') if case['arm'] == 'omega' else ('apex', 'rotation')
        for seed in (71, 913):
            for family in families:
                sequences, states, times = {}, {}, {}
                # Alternate order to reduce warm-cache/order bias.
                engines = (('reference', moves), ('fast', fast_moves))
                if seed == 913:
                    engines = engines[::-1]
                for label, module in engines:
                    rng = random.Random(seed)
                    start = cpu()
                    sequences[label] = list(stream(module, rows, family, rng, guard))
                    times[label] = cpu()-start
                    states[label] = rng.getstate()
                assert sequences['reference'] == sequences['fast'], (case['id'], family, seed)
                assert states['reference'] == states['fast'], (case['id'], 'RNG')
                for move in sequences['fast']:
                    core.validate(core.apply_move(rows, move), case['arm'])
                # Independent verifier for a bounded, deterministic sample.
                for move in sequences['fast'][:3]:
                    checked(core.encode_g6(core.apply_move(rows, move)), case['arm'])
                records.append({'case': case['id'], 'family': family, 'seed': seed,
                                'moves': len(sequences['fast']), 'cpu_seconds': times,
                                'speedup': times['reference']/max(times['fast'], 1e-9)})
        # Weighted family mixing and shared RNG must agree, including exhaustion.
        streams, rngs = [], []
        for module in (moves, fast_moves):
            rng = random.Random(991)
            source = module.MoveSource(rows, case['arm'], rng, guard)
            streams.append([source.next() for _ in range(40)])
            rngs.append(rng.getstate())
        assert streams[0] == streams[1] and rngs[0] == rngs[1]
    return {'status': 'ORDER_RNG_VALIDITY_PASS', 'cases': len(cases), 'records': records}
