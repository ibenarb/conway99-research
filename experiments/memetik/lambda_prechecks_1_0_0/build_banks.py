"""Deterministic same-origin AP walks; not fitness-selected and not a search run."""
import boot
from util import *
from kernel import catalogue
from archive import make_item
from prepare import ORIGINS
import random


class Guard:
    def __init__(self, deadline):
        self.deadline = deadline
    def check(self):
        if own_cpu() > self.deadline:
            raise RuntimeError('Isolated bank preparation budget exhausted')


def main():
    originals = {p['line']: p for p in read(boot.FROZEN / 'founders.json')}
    out = {}
    for i, origin in enumerate(ORIGINS):
        started = own_cpu()
        guard = Guard(started + 180)
        rng = random.Random(20260924000 + i)
        current = originals[origin]
        population = [current]
        seen = {current['class']}
        trace = []
        while len(population) < 16:
            rows = core.decode_g6(current['graph6'])
            moves = list(catalogue(rows, False, guard))
            if not moves:
                raise RuntimeError('AP-isolated founder: ' + origin)
            name, move = rng.choice(moves)
            child = make_item(core.apply_move(rows, move), current, guard)
            trace.append({'operator': name, 'move': move, 'graph6': child['graph6'], 'scores': child['scores']})
            if child['class'] not in seen:
                population.append(child)
                seen.add(child['class'])
            current = child
        out[origin] = {'origin': originals[origin], 'seed': 20260924000 + i,
                       'population': population, 'trace': trace,
                       'preparation_cpu_seconds': own_cpu() - started,
                       'selection': 'first sixteen canonical-distinct states of an unselected AP walk'}
        print(origin, len(trace), round(own_cpu() - started, 3), flush=True)
    atomic(boot.HERE / 'ISOLATED_BANKS.json', out)


if __name__ == '__main__':
    main()
