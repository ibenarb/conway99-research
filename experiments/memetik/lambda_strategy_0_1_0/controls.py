"""Independent validity, inverse, rejection, selection and enumeration controls."""
import bootstrap
from common import core, checked, cpu, atomic
from strategy import cycle_move, cycle_moves, quota_select
from search import key
import fast_moves
from itertools import combinations, product
from pathlib import Path
import random
import json
import unittest


class Controls(unittest.TestCase):
    def test_positive_inverse_and_exhaustive_small(self):
        rows = core.from_edges(9, [e for t in ((0,1,2),(3,4,5),(6,7,8)) for e in combinations(t,2)])
        ts = fast_moves.reference.triangles(rows)
        brute = set()
        for triples in combinations(ts, 3):
            for tips in product(*triples):
                for direction in (-1, 1):
                    m = cycle_move(rows, triples, tips, direction)
                    if m:
                        brute.add(m)
        actual = set(cycle_moves(rows))
        self.assertEqual(actual, brute)
        self.assertEqual(len(actual), 54)
        for move in actual:
            child = core.apply_move(rows, move)
            self.assertEqual(core.apply_move(child, move[::-1]), rows)
            adjacent = [set(core.vertices(r)) for r in child]
            self.assertTrue(all(len(a) == 2 for a in adjacent))
            self.assertTrue(all(len(adjacent[u] & adjacent[v]) == 1 for u in range(9) for v in adjacent[u]))

    def test_bounded_real_enumeration_against_naive(self):
        rows = tuple(sum(1 << j for j in range(9) if j != i and (j//3 == i//3 or j%3 == i%3)) for i in range(9))
        ts = fast_moves.reference.triangles(rows)
        brute = set()
        for triples in combinations(ts, 3):
            for tips in product(*triples):
                for direction in (-1, 1):
                    m = cycle_move(rows, triples, tips, direction)
                    if m:
                        brute.add(m)
        self.assertTrue(brute)
        self.assertTrue(set(fast_moves.rotation_moves(rows)))
        self.assertTrue(set(fast_moves.rotation_moves(rows)).issubset(brute))
        self.assertEqual(set(cycle_moves(rows)), brute)
        self.assertEqual(set(cycle_moves(rows, random.Random(33))), brute)

    def test_negative_extra_triangle(self):
        # External common neighbor destroys lambda for the proposed new edge 0-3.
        edges = [e for t in ((0,1,2),(3,4,5),(6,7,8),(0,9,10),(3,9,11)) for e in combinations(t,2)]
        rows = core.from_edges(12, edges)
        self.assertTrue(all((rows[u] & rows[v]).bit_count() == 1 for u,v in edges))
        self.assertIsNone(cycle_move(rows, [(0,1,2),(3,4,5),(6,7,8)], [2,3,6]))
        self.assertIsNone(cycle_move(rows, [(0,1,2),(0,9,10),(6,7,8)], [2,9,6]))
        self.assertIsNone(cycle_move(rows, [(0,1,2),(3,4,5),(6,7,8)], [2,3,6], 0))

    def test_persistent_quotas(self):
        founders = json.loads((bootstrap.HERE / 'founders.json').read_text())
        for epoch in (0, 5, 100):
            selected = quota_select(founders, [], 'lambda', 'W', random.Random(9), epoch, ['HoG','Z33_lift','triangle_packing'])
            self.assertEqual(len(selected), 16)
            self.assertEqual(len({p['class'] for p in selected}), 16)
            self.assertEqual({p['family'] for p in selected}, {'HoG','Z33_lift','triangle_packing'})
            self.assertIn(min(founders, key=lambda p: key(p['scores'],'W')), selected)

    def test_passive_archive_and_false_success(self):
        from instrumentation import Observer
        from tempfile import TemporaryDirectory
        from common import verifier
        founders = json.loads((bootstrap.HERE / 'founders.json').read_text())
        parent = next(p for p in founders if p['line'] == 'hog57338')
        with TemporaryDirectory() as temporary:
            task = {'founders': [parent], 'id': 'control'}
            state = {}
            observer = Observer(Path(temporary), state, cpu()+30, 0, task)
            observer.parent = parent
            rows = core.decode_g6(parent['graph6'])
            move = next(m for m in fast_moves.apex_moves(rows)
                        if key(core.metrics(core.apply_move(rows,m)), 'Linf') < key(parent['scores'],'Linf'))
            child = core.apply_move(rows,move)
            scores = core.metrics(child)
            self.assertGreaterEqual(key(scores,'W'),key(parent['scores'],'W'))
            observer.observe(child,scores,'apex')
            self.assertLess(key(state['observations']['archive']['Linf']['scores'],'Linf'),key(parent['scores'],'Linf'))
            self.assertEqual(state['observations']['archive']['W']['state'],parent['state'])
            with self.assertRaises(ValueError):
                observer.observe(rows,dict(core.metrics(rows),F=0),'fake')
        rook = tuple(sum(1 << j for j in range(9) if j != i and (i//3 == j//3 or i%3 == j%3)) for i in range(9))
        self.assertTrue(verifier.check_graph(core.encode_g6(rook),'lambda',expected_n=9,expected_degree=4)['is_solution'])
        self.assertFalse(verifier.check_graph(parent['graph6'],'lambda')['is_solution'])


def real_report():
    founders = json.loads((bootstrap.HERE / 'founders.json').read_text())
    report = []
    for item in founders:
        rows, _ = checked(item['graph6'], 'lambda')
        old = set(fast_moves.rotation_moves(rows))
        start = cpu()
        moves = list(cycle_moves(rows))
        assert old.issubset(set(moves))
        improvements = dict.fromkeys(('W', 'L1', 'F', 'Linf'), 0)
        best = dict(item['scores'])
        escapes = 0
        from generate import structure
        for move in moves:
            child = core.apply_move(rows, move)
            _, scores = checked(core.encode_g6(child), 'lambda')
            assert core.apply_move(child, move[::-1]) == rows
            for target in improvements:
                improvements[target] += key(scores, target) < key(item['scores'], target)
            if key(scores, 'W') < key(best, 'W'):
                best = scores
            if item['family'] == 'Z33_lift':
                escapes += structure(child, 'Z33_lift') is False
        report.append({'line': item['line'], 'state': item['state'], 'cycles': len(moves),
                       'old_rotations': len(old), 'improvements': improvements,
                       'best_W': best, 'fixed_partition_exits': escapes, 'cpu_seconds': cpu()-start})
        print(item['line'], len(moves), improvements, flush=True)
    return report


if __name__ == '__main__':
    import sys
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    if len(sys.argv) == 2:
        atomic(Path(sys.argv[1]), {'tests': result.testsRun, 'real': real_report()})
