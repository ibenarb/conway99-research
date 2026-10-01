"""Exhaustive local move oracle, hereditary bounds, projection and I/O tests."""
import itertools
import json
from pathlib import Path
import random
import tempfile
import threading
import unittest
import packing as p


def rows_from_edges(n, edges):
    rows = [0] * n
    for u, v in edges:
        p.add(rows, u, v)
    return rows


def rook():
    return rows_from_edges(9, [(u, v) for u in range(9) for v in range(u)
                              if u // 3 == v // 3 or u % 3 == v % 3])


class PackingTests(unittest.TestCase):
    def test_add_oracle_exhaustive(self):
        n = 5
        edges = list(itertools.combinations(range(n), 2))
        valid = checked = 0
        for mask in range(1 << len(edges)):
            rows = rows_from_edges(n, [e for i, e in enumerate(edges) if mask & (1 << i)])
            try:
                p.packing_check(rows, 3)
            except ValueError:
                continue
            valid += 1
            for u, v in edges:
                if rows[u] & (1 << v):
                    child = list(rows)
                    p.remove(child, u, v)
                    p.packing_check(child, 3)
                else:
                    child = list(rows)
                    p.add(child, u, v)
                    try:
                        p.packing_check(child, 3)
                        expected = True
                    except ValueError:
                        expected = False
                    self.assertEqual(p.add_allowed(rows, u, v, 3), expected)
                    checked += 1
        self.assertGreater(valid, 100)
        self.assertGreater(checked, 1000)

    def test_nine_vertex_add_oracle(self):
        rng = random.Random(827)
        for unused in range(12):
            rows = [0] * 9
            order = list(itertools.combinations(range(9), 2))
            rng.shuffle(order)
            for u, v in order[:24]:
                if p.add_allowed(rows, u, v, 4):
                    p.add(rows, u, v)
            for u, v in order:
                if rows[u] & (1 << v):
                    continue
                child = list(rows)
                p.add(child, u, v)
                try:
                    p.packing_check(child, 4)
                    expected = True
                except ValueError:
                    expected = False
                self.assertEqual(p.add_allowed(rows, u, v, 4), expected)

    def test_99_projection_and_heredity(self):
        rows = [0] * 99
        for u in range(99):
            for offset in range(1, 8):
                p.add(rows, u, (u + offset) % 99)
        self.assertEqual(len(p.edge_list(rows)), 693)
        child, deleted = p.project(rows, random.Random(194), 14)
        checked = p.packing_check(child, 14)
        self.assertEqual(checked['deficit'], deleted)
        for u, v in p.edge_list(child)[:30]:
            smaller = list(child)
            p.remove(smaller, u, v)
            p.packing_check(smaller, 14)

    def test_invalid_rejected(self):
        with self.assertRaises(ValueError):
            p.packing_check(rows_from_edges(4, itertools.combinations(range(4), 2)), 3)
        with self.assertRaises(ValueError):
            p.packing_check(rows_from_edges(5, [(a, b) for a in (0, 1) for b in (2, 3, 4)]), 4)
        with self.assertRaises(ValueError):
            p.packing_check([2, 0], 2)
        with self.assertRaises(ValueError):
            p.packing_check([1], 2)

    def test_projection_preserves_only_deletions(self):
        rng = random.Random(901)
        for n in (5, 9, 17):
            for unused in range(5):
                rows = rows_from_edges(n, [e for e in itertools.combinations(range(n), 2)
                                          if rng.random() < 0.7])
                child, deleted = p.project(rows, rng, min(4, n - 1))
                p.packing_check(child, min(4, n - 1))
                self.assertTrue(all(c & ~a == 0 for c, a in zip(child, rows)))
                self.assertEqual(deleted, len(p.edge_list(rows)) - len(p.edge_list(child)))

    def test_rook_target_and_separate_kinds(self):
        rows = rook()
        self.assertEqual(p.decode(p.encode(rows)), rows)
        self.assertEqual(p.lambda_record(rows, 4)['scores'], {'W': 0, 'L1': 0})
        self.assertEqual(p.packing_check(rows, 4), {'edges': 18, 'deficit': 0})
        for arm in ('packing_tabu', 'lambda_descent_projection'):
            with tempfile.TemporaryDirectory() as directory:
                result = p.run_task({'graph6': p.encode(rows)}, {'arm': arm, 'degree': 4}, directory, p.cpu() + 2)
                self.assertEqual(result['status'], 'PACKING_EDGE_TARGET_REACHED')
                self.assertEqual(result['best']['kind'], 'packing')
                self.assertEqual(result['lambda_best']['kind'], 'lambda_parent')
                self.assertFalse(result['stats']['checkpoint_resume'])
                again = p.run_task({'graph6': p.encode(rows)}, {'arm': arm, 'degree': 4}, directory, p.cpu() + 2)
                self.assertTrue(again['stats']['checkpoint_resume'])

    def test_pause_and_corrupt_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            stop = threading.Event()
            stop.set()
            founder = {'graph6': p.encode(rook())}
            result = p.run_task(founder, {'degree': 4}, directory, p.cpu() + 1, stop_event=stop)
            self.assertEqual(result['status'], 'PAUSED')
            p.packing_check(result['best']['graph6'], 4)
            path = Path(directory) / 'best.json'
            record = json.loads(path.read_text())
            record['scores']['edges'] = 100
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                p.run_task(founder, {'degree': 4}, directory, p.cpu() + 1)



if __name__ == '__main__':
    unittest.main(verbosity=2)
