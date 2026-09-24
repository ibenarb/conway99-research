"""AP descent with cycle3 queried only after a complete AP local minimum.

All unfinished enumeration prefixes survive checkpoints. Both arms use this
instrumentation; P preserves the frozen state transitions and RNG calls.
"""
import boot
from common import core, cpu
from engine import Engine as FrozenEngine
from kernel import Scorer, cycle_moves
from search import key


def move_key(move):
    return tuple(tuple(tuple(edge) for edge in part) for part in move)


class ExperimentEngine(FrozenEngine):
    def metrics(self):
        return self.s.setdefault('experiment_metrics', {
            'ap_catalogue_cpu': 0.0, 'cycle_catalogue_cpu': 0.0,
            'cycle_queries_started': 0, 'cycle_queries_completed': 0,
            'cycle_queries_with_improvement': 0, 'cycle_adoptions': 0,
            'cycle_replayed_moves': 0})

    def batch(self, current, guard, sample_size=None):
        metrics = self.metrics()
        batch = self.s.get('batch')
        if not (batch and batch.get('cycle_started')):
            started = cpu()
            try:
                choices = super().batch(current, guard, sample_size)
            finally:
                metrics['ap_catalogue_cpu'] += cpu() - started
            if (self.variant != 'PCesc' or self.s['episode']['phase'] != 'descent'
                    or any(key(c['scores'], self.target) < key(current['scores'], self.target)
                           for c in choices)):
                return choices
            batch = self.s['batch']
            batch.update(cycle_started=True, cycle_complete=False, ap_count=len(choices))
            metrics['cycle_queries_started'] += 1
        if batch['state'] != current['state']:
            raise ValueError('Cycle state mismatch')
        if batch['cycle_complete']:
            return batch['items']
        started = cpu()
        try:
            rows = core.decode_g6(current['graph6'])
            scorer = Scorer(rows)
            seen = {move_key(c['move']) for c in batch['items'][:batch['ap_count']]}
            prefix = len(batch['items']) - batch['ap_count']
            index = 0
            for move in cycle_moves(rows, None, guard):
                guard.check()
                ident = move_key(move)
                if ident in seen:
                    continue
                seen.add(ident)
                if index < prefix:
                    metrics['cycle_replayed_moves'] += 1
                    index += 1
                    continue
                child, scores = scorer.evaluate(move)
                guard.check()
                self.obs.evaluated(child, scores, 'cycle3', current)
                guard.check()
                batch['items'].append({'operator': 'cycle3', 'move': move, 'scores': scores})
                index += 1
            guard.check()
            batch['cycle_complete'] = True
            metrics['cycle_queries_completed'] += 1
            metrics['cycle_queries_with_improvement'] += int(any(
                key(c['scores'], self.target) < key(current['scores'], self.target)
                for c in batch['items'][batch['ap_count']:]))
            return batch['items']
        finally:
            metrics['cycle_catalogue_cpu'] += cpu() - started

    def adopt(self, current, choice, guard):
        result = super().adopt(current, choice, guard)
        if choice['operator'] == 'cycle3':
            self.metrics()['cycle_adoptions'] += 1
        return result

    def finish_episode(self, reason):
        if self.variant == 'PCesc' and reason == 'LOCAL_MIN_EXACT_AP':
            if not self.s['batch'].get('cycle_complete'):
                raise AssertionError('APC minimum claimed without complete cycle query')
            reason = 'LOCAL_MIN_EXACT_APC'
        super().finish_episode(reason)

    def step(self, guard):
        if self.variant == 'PCesc':
            self.step_episode(guard)
        else:
            super().step(guard)
