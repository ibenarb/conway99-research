"""Independent DPLL projection checks; no external solver needed."""
from itertools import product
import json
from c2_reference import CNF, Frame, encode_base, reconstruct, verify_graph
from counter import CounterCNF, encode_variant


def sat(clauses, assumptions):
    clauses = list(clauses) + [(v,) for v in assumptions]
    def solve(cs):
        while True:
            if not cs:
                return True
            if any(not c for c in cs):
                return False
            unit = next((c[0] for c in cs if len(c) == 1), None)
            if unit is None:
                break
            cs = [tuple(v for v in c if v != -unit) for c in cs if unit not in c]
        v = min(cs, key=len)[0]
        return solve(cs + [(v,)]) or solve(cs + [(-v,)])
    return solve(clauses)


def check():
    counts = {'weighted_projections': 0, 'graph_projections': 0}
    # Zero weights, duplicate variables, constants, impossible sums, and gcd cases.
    for weights in product(range(4), repeat=4):
        for constant in (0, 1):
            terms = [i + 1 for i, w in enumerate(weights) for _ in range(w)] + [False] + [True] * constant
            for target in (-1, 0, 1, 2):
                enc = CounterCNF(retain=True)
                ref = CNF(retain=True)
                for _ in range(4):
                    enc.variable()
                    ref.variable()
                enc.small = True
                enc.exact(terms, target)
                ref.exact(terms, target)
                for bits in product((0, 1), repeat=4):
                    assumptions = [i + 1 if b else -(i + 1) for i, b in enumerate(bits)]
                    expected = sum(w * b for w, b in zip(weights, bits)) + constant == target
                    assert sat(enc.saved, assumptions) == expected
                    assert sat(ref.saved, assumptions) == expected
                    counts['weighted_projections'] += 1
                enc.close()
                ref.close()
    # Larger balanced trees with independent bits, exercise truncated merge boundaries.
    for n in (5, 6, 7, 8):
        for target in (0, 1, 2):
            enc = CounterCNF(retain=True)
            xs = [enc.variable() for _ in range(n)]
            enc.small = True
            enc.exact(xs, target)
            for bits in product((0, 1), repeat=n):
                assumptions = [v if b else -v for v, b in zip(xs, bits)]
                assert sat(enc.saved, assumptions) == (sum(bits) == target)
                counts['weighted_projections'] += 1
            enc.close()
    for encoder, encode in ((CNF, encode_base), (CounterCNF, encode_variant)):
        cnf, frame = encoder(retain=True), Frame(4)
        frame.allocate(cnf)
        encode(cnf, frame)
        for bits in product((0, 1), repeat=len(frame.map)):
            values = {i + 1: bool(b) for i, b in enumerate(bits)}
            assumptions = [v if b else -v for v, b in values.items()]
            assert sat(cnf.saved, assumptions) == verify_graph(reconstruct(frame, values), 4)
            counts['graph_projections'] += 1
        cnf.close()
    return dict(status='COUNTER_PROJECTION_CONTROLS_PASS', **counts,
                scope='Finite independent controls supplement the threshold induction proof; no Conway99 decision.')


if __name__ == '__main__':
    print(json.dumps(check()), flush=True)
