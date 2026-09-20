"""Positive fixtures for rare families plus stale-state/RNG regressions."""
import random
import unittest

import bootstrap
import moves
import fast_moves
from common import core


class AccelerationTests(unittest.TestCase):
    def test_rotation_positive_rook_fixture(self):
        # A small lambda=1 graph exercises actual rotations, not empty streams.
        rows = [sum(1 << j for j in range(9) if i != j and (i//3 == j//3 or i%3 == j%3)) for i in range(9)]
        for seed in (1, 99):
            ra, rb = random.Random(seed), random.Random(seed)
            a = list(moves.reference.rotation_moves(rows, ra))
            b = list(fast_moves.rotation_moves(rows, rb))
            self.assertTrue(a)
            self.assertEqual(a, b)
            self.assertEqual(ra.getstate(), rb.getstate())
            for move in b:
                child = core.apply_move(rows, move)
                self.assertTrue(all(row.bit_count() == 4 for row in child))
                self.assertTrue(all((child[u] & child[v]).bit_count() == 1 for u in range(9) for v in core.vertices(child[u])))

    def test_product_six_positive_and_changed_state(self):
        # Kernel fixture, not an Omega founder: plant a legal signed rectangle.
        vectors = moves.catalogue(6)
        x = vectors[0]
        used = {u for u, s in x}
        y = next(v for v in vectors if not used.intersection(u for u, s in v))
        deleted = tuple(sorted(core.edge(u+15, v+15) for u, sx in x for v, sy in y if sx*sy < 0))
        added = tuple(sorted(core.edge(u+15, v+15) for u, sx in x for v, sy in y if sx*sy > 0))
        rows = [0]*99
        for u, v in deleted:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
        original = (deleted, added)
        for current, wanted in ((rows, original), (core.apply_move(rows, original), (added, deleted))):
            ra, rb = random.Random(71), random.Random(71)
            a = list(moves.omega_moves(current, '6x6', ra))
            b = list(fast_moves.omega_moves(current, '6x6', rb))
            self.assertIn(wanted, a)
            self.assertEqual(a, b)
            self.assertEqual(ra.getstate(), rb.getstate())


if __name__ == '__main__':
    unittest.main()
