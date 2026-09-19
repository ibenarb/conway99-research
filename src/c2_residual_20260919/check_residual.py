"""Exhaustive lex projection controls and direct small-graph checks; no C99 search."""
import argparse
from itertools import permutations, product
import json
from pathlib import Path
import sys
from residual import CNF, Frame, add_lex, certificate, closure, triangles, ROOT, sha256, write_json
from c2_reference import reconstruct, verify_graph
from counter import CounterCNF, encode_variant
sys.path.insert(0, str(ROOT / 'src/c2_reference_20260913'))
from test_reference import sat


def controls():
    count = 0
    # All permutations, all prefixes, all bit strings: existential projection
    # of the actual emitted CNF versus Python's independent tuple comparison.
    for n in range(1, 5):
        for p in permutations(range(1, n+1)):
            for prefix in range(n+1):
                cnf = CNF(retain=True)
                cnf.variables = n
                add_lex(cnf, p, prefix)
                for bits in product((0, 1), repeat=n):
                    expected = bits[:prefix] <= tuple(bits[v-1] for v in p[:prefix])
                    assert sat(cnf.saved, [v if bits[v-1] else -v for v in range(1, n+1)]) == expected
                    count += 1
                cnf.close()
    # Nontrivial group control for all 64 bit strings, simultaneous generator
    # comparisons and every prefix. Orbit minima preserve invariant predicates.
    gens = [(1,2,3,4,5,0), (1,0,2,3,4,5)]
    group = closure(gens, 6)
    assert len(group) == 720
    orbit_checks = 0
    for bits in product((0, 1), repeat=6):
        minimum = min(tuple(bits[p[i]] for i in range(6)) for p in group)
        for prefix in range(7):
            cnf = CNF(retain=True)
            cnf.variables = 6
            for p in gens:
                add_lex(cnf, [v+1 for v in p], prefix)
            assert sat(cnf.saved, [v if minimum[v-1] else -v for v in range(1,7)])
            cnf.close()
            orbit_checks += 1
    # Known k=4 model; all four primary assignments against full graph SRG test.
    tiny_checks = 0
    for variant in ('totalizer', 'lex', 'triangles', 'both'):
        cnf, frame = CounterCNF(retain=True), Frame(4)
        frame.allocate(cnf)
        cert = certificate(frame, (1,))
        encode_variant(cnf, frame)
        for unit in cert['units']:
            cnf.clause(unit)
        if variant in ('lex', 'both'):
            for g in cert['generators']:
                add_lex(cnf, g['primary_old_to_new'], len(frame.map))
        if variant in ('triangles', 'both'):
            for clause in triangles(frame):
                cnf.clause(*clause)
        accepted = 0
        for bits in product((0,1), repeat=len(frame.map)):
            values = dict(enumerate(bits, 1))
            expected = verify_graph(reconstruct(frame, values), 4)
            actual = sat(cnf.saved, [v if b else -v for v, b in values.items()])
            assert actual == expected
            accepted += actual
            tiny_checks += 1
        assert accepted == 1
        cnf.close()
    return {'status': 'C2_RESIDUAL_SMALL_CONTROLS_PASS', 'lex_projection_checks': count,
            'orbit_minimum_checks': orbit_checks, 'nontrivial_control_group_order': len(group),
            'rook_variant_projection_checks': tiny_checks,
            'scope': 'Finite controls plus written proof; no C99 satisfiability decision.',
            'sources': {p.name: sha256(p) for p in Path(__file__).parent.glob('*.py')}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = controls()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out, report)
    print(json.dumps(report))
