"""Passive four-champion archive of every scored neighbor, bounded diagnostics."""
import bootstrap
from common import core, checked, atomic, cpu, sha, verifier
from search import key
from collections import Counter
import time


class Observer:
    def __init__(self, directory, state, deadline, base, task):
        self.directory, self.state, self.deadline = directory, state, deadline
        self.base, self.task = base, task
        self.parent = None
        if 'observations' not in state:
            state['observations'] = {'evaluated_moves': {}, 'archive': {}, 'archive_cost_cpu': 0,
                                     'isomorphic_returns': 0, 'path_maxima_histogram': {},
                                     'requested_lengths': {}, 'adopted_moves': {}, 'perturb_stops': {}}
            for target in ('W', 'L1', 'F', 'Linf'):
                state['observations']['archive'][target] = min(task['founders'], key=lambda f: key(f['scores'], target))
        self.data = state['observations']

    def observe(self, rows, scores, name):
        counts = self.data['evaluated_moves']
        counts[name] = counts.get(name, 0) + 1
        targets = [t for t, p in self.data['archive'].items() if key(scores, t) < key(p['scores'], t)]
        if not targets and scores['F']:
            return
        start = cpu()
        text = core.encode_g6(rows)
        _, actual = checked(text, 'lambda')
        if any(actual[k] != scores[k] for k in actual):
            raise ValueError('Observed score mismatch')
        item = dict(graph6=text, scores=actual, family=self.parent['family'], line=self.parent['line'],
                    parent=self.parent['state'], state=sha(text.encode()), cpu=self.base+cpu())
        if cpu() <= self.deadline:
            for t in targets:
                self.data['archive'][t] = item
            if actual['F'] == 0:
                result = verifier.check_graph(text, 'lambda')
                if not result['is_solution']:
                    raise ValueError('False solution')
                atomic(self.directory.parent.parent / 'SOLUTION.json', {'candidate': item, 'verification': result, 'task': self.task['id']})
                print('INDEPENDENTLY_VERIFIED_SOLUTION', flush=True)
        self.data['archive_cost_cpu'] += cpu()-start

    def record_episode(self, record, result):
        self.data['isomorphic_returns'] += result['class'] == self.parent['class']
        for field, value in (('requested_lengths', record['requested']), ('perturb_stops', record['perturb_stop'])):
            bucket = self.data[field]
            bucket[str(value)] = bucket.get(str(value), 0)+1
        for name, value in record['adopted_moves'].items():
            self.data['adopted_moves'][name] = self.data['adopted_moves'].get(name, 0)+value
        maxima = record['path_maxima']
        delta = ','.join(str(maxima[k]-self.parent['scores'][k]) for k in ('W','L1','F','Linf'))
        bucket = self.data['path_maxima_histogram']
        bucket[delta] = bucket.get(delta, 0)+1

    def record_population(self):
        history = self.state.setdefault('family_history', [])
        history.append({'epoch': self.state['epoch'], 'cpu': self.base+cpu(),
                        'counts': dict(Counter(p['family'] for p in self.state['population']))})
        del history[:-512]
