"""Resumable move-boundary state machines for B0/P/T/TC.

A suspended generator is replayed from its saved RNG state; evaluated prefixes
are retained. Replaying consumes CPU and is reported, never a fresh search.
"""
import bootstrap
from common import core, cpu
from search import key, parent_choice, select, tuple_state
from kernel import Scorer, catalogue
import fast_moves
import random


class PhaseEnd(Exception):
    pass


class LocalGuard:
    def __init__(self, outer, phase_deadline=None):
        self.outer = outer
        self.phase_deadline = phase_deadline
        self.generated = 0

    def check(self):
        self.outer.check()
        if self.phase_deadline is not None and cpu() >= self.phase_deadline:
            raise PhaseEnd()


def increment(bucket, name, amount=1):
    bucket[str(name)] = bucket.get(str(name),0)+amount


class Engine:
    def __init__(self, task, state, rng, observer):
        self.task, self.s, self.rng, self.obs = task,state,rng,observer
        self.config, self.variant, self.target = task['config'],task['variant'],task['target']

    def begin_episode(self):
        parent = parent_choice(self.s['population'],self.target,self.rng)
        recipe = self.rng.choices(range(3),self.config['perturb_weights'])[0]
        desired = self.rng.randint(*self.config['perturb_ranges'][recipe])
        self.s['episode'] = {'parent':parent,'current':parent,'phase':'perturb',
                             'requested':desired,'perturb':0,'descent':0,
                             'phase_cpu':0.0,'maxima':dict(parent['scores']),
                             'operators':{},'recipe':recipe}
        increment(self.s['parent_families'],parent['family'])

    def finish_episode(self, reason):
        ep = self.s['episode']
        result = ep['current']
        self.obs.archive.put(result,endpoint=True)
        hist = self.s['histogram']
        for field,value in (('perturb_length',ep['perturb']),('requested_length',ep['requested']),
                            ('descent_length',ep['descent']),('stop',reason),
                            ('returned',result['state']==ep['parent']['state']),
                            ('isomorphic_return',result['class']==ep['parent']['class'])):
            increment(hist.setdefault(field,{}),value)
        barrier = ','.join(str(ep['maxima'][m]-ep['parent']['scores'][m]) for m in ('W','L1','F','Linf'))
        increment(hist.setdefault('observed_path_maxima',{}),barrier)
        self.s['episodes'] += 1
        self.s['children'].append(result)
        if len(self.s['children']) == 16:
            families = sorted({p['family'] for p in self.task['founders']})
            self.s['population'] = select(self.s['population'],self.s['children'],'lambda',self.target,self.rng,self.s['epoch'],families)
            self.s['children'] = []
            self.s['epoch'] += 1
            self.obs.family_event()
        self.s['episode'] = None
        self.s['batch'] = None
        self.obs.endpoint(result,reason)

    def finish_path_observation(self, reason):
        path = self.s['path']
        hist = self.s['histogram']
        for field,value in (('tabu_path_length',path['moves']),
                            ('tabu_isomorphic_return',path['current']['class']==path['origin']['class'])):
            increment(hist.setdefault(field,{}),value)
        barrier = ','.join(str(path['maxima'][m]-path['origin']['scores'][m]) for m in ('W','L1','F','Linf'))
        increment(hist.setdefault('tabu_observed_path_maxima',{}),barrier)
        self.obs.endpoint(path['current'],reason)

    def begin_path(self, restart=False):
        if restart:
            parent = self.obs.archive.choose(self.rng,self.target,self.config['restart_exploration_probability'],self.config['restart_tournament'])
            self.s['restarts'] += 1
            walking = self.rng.randint(*self.config['restart_walk_range'])
        else:
            parent = min(self.task['founders'],key=lambda p:key(p['scores'],self.target))
            walking = 0
        self.s['path'] = {'current':parent,'origin':parent,'walk_remaining':walking,
                          'moves':0,'maxima':dict(parent['scores']),'stagnant':0}
        self.s['tabu'] = {}
        self.s['batch'] = None
        increment(self.s['parent_families'],parent['family'])

    def batch(self, current, guard, sample_size=None):
        rows = core.decode_g6(current['graph6'])
        if self.s['batch'] is None:
            self.s['batch'] = {'state':current['state'],'items':[], 'complete':False,
                               'rng_start':self.rng.getstate(), 'sample_size':sample_size}
        batch = self.s['batch']
        if batch['state'] != current['state'] or batch['sample_size'] != sample_size:
            raise ValueError('Batch/current mismatch')
        if batch['complete']:
            return batch['items']
        scorer = Scorer(rows)
        local_rng = random.Random()
        local_rng.setstate(tuple_state(batch['rng_start']))
        if sample_size is not None:
            source = fast_moves.MoveSource(rows,'lambda',local_rng,guard)
            def stream():
                for _ in range(sample_size):
                    value = source.next()
                    if value is None:
                        break
                    yield value
        else:
            def stream():
                yield from catalogue(rows,self.variant=='TC',guard)
        prefix = len(batch['items'])
        try:
            for index,(name,move) in enumerate(stream()):
                guard.check()
                if index < prefix:
                    self.s['replayed_moves'] += 1
                    continue
                child,scores = scorer.evaluate(move)
                guard.check()
                self.obs.evaluated(child,scores,name,current)
                guard.check()
                batch['items'].append({'operator':name,'move':move,'scores':scores})
            guard.check()
        except PhaseEnd:
            # A baseline phase timeout consumes RNG draws already made, exactly
            # like the reference generator. A campaign pause instead replays.
            if sample_size is not None:
                self.rng.setstate(local_rng.getstate())
            raise
        batch['complete'] = True
        if sample_size is not None:
            self.rng.setstate(local_rng.getstate())
        increment(self.s['histogram'].setdefault('complete_neighbourhood_size',{}),len(batch['items']))
        self.s['complete_batches'] += 1
        return batch['items']

    def adopt(self, current, choice, guard):
        move = tuple(tuple(tuple(edge) for edge in part) for part in choice['move'])
        child = core.apply_move(core.decode_g6(current['graph6']),move)
        item = self.obs.adopt(child,choice['scores'],choice['operator'],current,guard)
        self.s['batch'] = None
        return item

    def step_episode(self, outer):
        if self.s['episode'] is None:
            self.begin_episode()
        ep = self.s['episode']
        phase = ep['phase']
        if phase == 'perturb' and ep['perturb'] >= ep['requested']:
            ep['phase'],ep['phase_cpu'] = 'descent',0.0
            return
        phase_limit = None
        if self.variant == 'B0':
            phase_limit = self.config['baseline_'+phase+'_cpu']
            if ep['phase_cpu'] >= phase_limit:
                if phase == 'perturb':
                    ep['phase'],ep['phase_cpu'],self.s['batch'] = 'descent',0.0,None
                else:
                    self.finish_episode('BASELINE_DESCENT_CPU_LIMIT')
                return
        guard = LocalGuard(outer,None if phase_limit is None else cpu()+phase_limit-ep['phase_cpu'])
        started = cpu()
        try:
            sample = (1 if phase=='perturb' else self.config['baseline_sample_size']) if self.variant=='B0' else None
            choices = self.batch(ep['current'],guard,sample)
            decision_rng = self.s['batch'].setdefault('decision_rng',self.rng.getstate())
            self.rng.setstate(tuple_state(decision_rng))
            if phase == 'perturb':
                if not choices:
                    ep['phase'],ep['phase_cpu'],self.s['batch'] = 'descent',0.0,None
                    return
                choice = choices[0] if self.variant=='B0' else self.rng.choice(choices)
            else:
                better = [c for c in choices if key(c['scores'],self.target)<key(ep['current']['scores'],self.target)]
                if not better:
                    self.finish_episode('STALLED_SAMPLED' if self.variant=='B0' else 'LOCAL_MIN_EXACT_AP')
                    return
                choice = min(better,key=lambda c:key(c['scores'],self.target))
            ep['current'] = self.adopt(ep['current'],choice,guard)
            ep[phase] += 1
            increment(ep['operators'],choice['operator'])
            for name in ('W','L1','F','Linf'):
                ep['maxima'][name] = max(ep['maxima'][name],ep['current']['scores'][name])
        except PhaseEnd:
            self.s['batch'] = None
            if phase == 'perturb':
                ep['phase'],ep['phase_cpu'] = 'descent',0.0
            else:
                self.finish_episode('BASELINE_DESCENT_CPU_LIMIT')
        finally:
            if self.s['episode'] is ep and ep['phase'] == phase:
                ep['phase_cpu'] += cpu()-started

    def step_tabu(self, outer):
        if self.s['path'] is None:
            self.begin_path()
        path = self.s['path']
        if path['stagnant'] >= self.config['restart_after_stagnant_iterations']:
            self.finish_path_observation('TABU_RESTART')
            self.begin_path(True)
            path = self.s['path']
        guard = LocalGuard(outer)
        choices = self.batch(path['current'],guard)
        if not choices:
            self.finish_path_observation('EMPTY_EXACT_CATALOG')
            self.begin_path(True)
            return
        decision_rng = self.s['batch'].setdefault('decision_rng',self.rng.getstate())
        self.rng.setstate(tuple_state(decision_rng))
        iteration = self.s['iterations']
        self.s['tabu'] = {e:expiry for e,expiry in self.s['tabu'].items() if expiry>iteration}
        if path['walk_remaining']:
            choice = self.rng.choice(choices)
        else:
            eligible = [c for c in choices if key(c['scores'],self.target)<key(self.s['best']['scores'],self.target)
                        or not any(self.s['tabu'].get(f'{a},{b}',0)>iteration for a,b in c['move'][1])]
            if not eligible:
                # Explicit deterministic expiry advance, no forbidden move adopted.
                self.s['iterations'] = min(self.s['tabu'].values())
                increment(self.s['histogram'].setdefault('tabu_events',{}),'ALL_FORBIDDEN_ADVANCE')
                return
            best_key = min(key(c['scores'],self.target) for c in eligible)
            choice = self.rng.choice([c for c in eligible if key(c['scores'],self.target)==best_key])
        previous_best = key(self.s['best']['scores'],self.target)
        before = path['current']
        path['current'] = self.adopt(before,choice,guard)
        tenure = self.rng.randint(*self.config['tabu_deleted_edge_tenure'])
        for a,b in choice['move'][0]:
            self.s['tabu'][f'{a},{b}'] = iteration+tenure+1
        path['walk_remaining'] = max(0,path['walk_remaining']-1)
        path['moves'] += 1
        path['stagnant'] = 0 if key(self.s['best']['scores'],self.target)<previous_best else path['stagnant']+1
        for name in ('W','L1','F','Linf'):
            path['maxima'][name] = max(path['maxima'][name],path['current']['scores'][name])
        self.s['iterations'] += 1

    def step(self, guard):
        if self.variant in ('B0','P'):
            self.step_episode(guard)
        else:
            self.step_tabu(guard)
