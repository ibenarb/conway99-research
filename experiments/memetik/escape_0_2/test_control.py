"""Targeted tests of new search accounting, not a rerun of old graph audits."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from core import BudgetEnd, decode_g6, encode_g6
import search

ROOT = Path(__file__).resolve().parents[3]
NODES = json.loads((ROOT / 'results/memetik/escape_census_20260915/escape_A_component_result.json').read_text())['nodes']
GRAPHS = {n['metrics']['W']: decode_g6(n['graph6']) for n in NODES}


def transition(first, second):
    removed = tuple((i,j) for i in range(99) for j in range(i+1,99) if first[i] & (1 << j) and not second[i] & (1 << j))
    added = tuple((i,j) for i in range(99) for j in range(i+1,99) if second[i] & (1 << j) and not first[i] & (1 << j))
    return removed, added


def source(rows):
    g6 = encode_g6(rows)
    return {'graph6': g6, 'sha256': hashlib.sha256((g6+'\n').encode()).hexdigest(), 'arm': 'omega'}


def stream(mapping, interrupt=False):
    def generate(rows, arm, budget, counts):
        for child in mapping.get(rows, []):
            yield '4x4', transition(rows, child), child
            if interrupt:
                raise BudgetEnd('TEST_INTERRUPTION')
        for family in search.families(arm):
            counts[family] = {'trades': len(mapping.get(rows, [])) if family == '4x4' else 0, 'complete': True}
    return generate


class Accounting(unittest.TestCase):
    def execute(self, mode, mapping, depth=3, interrupt=False):
        with tempfile.TemporaryDirectory() as directory, patch.object(search, 'neighbors', stream(mapping, interrupt)), patch.object(search.resource, 'setrlimit'):
            return search.execute({'id':'test', 'mode':mode, 'objective':'W'}, source(GRAPHS[2212]), directory, {'cpu_seconds':30,'max_states':30,'max_depth':depth,'max_descent_steps':20})

    def test_bfs_deterioration_and_minimum_length(self):
        result = self.execute('bfs', {GRAPHS[2212]: [GRAPHS[2260]], GRAPHS[2260]: [GRAPHS[2193]]})
        self.assertEqual(result['status'], 'IMPROVEMENT_FOUND')
        self.assertEqual(result['witness']['path_length'], 2)
        self.assertEqual(result['witness']['barrier_above_start'], 48)
        self.assertEqual(result['no_improvement_through_depth'], 1)

    def test_depth_limit_is_not_component_closure(self):
        result = self.execute('bfs', {GRAPHS[2212]: [GRAPHS[2260]], GRAPHS[2260]: [GRAPHS[2193]]}, depth=1)
        self.assertEqual(result['status'], 'DEPTH_LIMIT')
        self.assertFalse(result['component_complete'])
        self.assertEqual(result['no_improvement_through_depth'], 1)

    def test_neutral_search_does_not_cross_deterioration(self):
        result = self.execute('neutral', {GRAPHS[2212]: [GRAPHS[2260]], GRAPHS[2260]: [GRAPHS[2193]]})
        self.assertEqual(result['status'], 'COMPONENT_EXHAUSTED')
        self.assertEqual(result['discovered'], 1)
        self.assertNotIn('witness', result)

    def test_partial_expansion_rolls_back(self):
        result = self.execute('bfs', {GRAPHS[2212]: [GRAPHS[2260]]}, interrupt=True)
        self.assertEqual(result['status'], 'TEST_INTERRUPTION')
        self.assertEqual(result['expanded'], 0)
        self.assertEqual(result['discovered'], 1)
        self.assertEqual(result['no_improvement_through_depth'], 0)
        self.assertFalse(result['component_complete'])


if __name__ == '__main__':
    unittest.main()
