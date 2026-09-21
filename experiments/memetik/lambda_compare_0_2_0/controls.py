"""Deterministic mathematical and state-continuation controls; no Ryzen claim."""
import bootstrap
from common import atomic, core, checked, sha, cpu
from search import key, tuple_state
from kernel import Scorer, apex_exact, pivots, catalogue
from archive import Archive, make_item
from engine import Engine
from worker import initial
import fast_moves
import check_review
import copy
import json
from pathlib import Path
import random
import tempfile


class Guard:
    generated = 0
    def check(self):
        pass


class Interrupted(Exception):
    pass


class Countdown(Guard):
    def __init__(self, count):
        self.count = count
    def check(self):
        self.count -= 1
        if self.count == 0:
            raise Interrupted()


class PrefixGuard(Guard):
    def __init__(self,state):
        self.state = state
    def check(self):
        batch = self.state.get('batch')
        if batch and batch['items']:
            raise Interrupted()


class Observation:
    def __init__(self, task, state, archive, interrupt_adopt=False):
        self.task,self.s,self.archive = task,state,archive
        self.interrupt_adopt = interrupt_adopt
        self.trace = []
    def evaluated(self, rows, scores, name, origin):
        pass
    def adopt(self, rows, scores, name, origin, guard):
        if self.interrupt_adopt:
            self.interrupt_adopt = False
            raise Interrupted()
        item = make_item(rows,origin,guard)
        self.archive.put(item)
        if key(scores,self.task['target'])<key(self.s['best']['scores'],self.task['target']):
            self.s['best'] = item
        self.trace.append((name,item['state']))
        return item
    def endpoint(self, item, reason):
        self.archive.put(item,True)
    def family_event(self):
        pass


def task_for(founders, variant, seed=92021):
    config = json.loads((bootstrap.HERE/'config.json').read_text())
    return {'id':'test-'+variant,'kind':'compare','variant':variant,'target':'W','seed':seed,
            'founders':copy.deepcopy(founders),'config':config}


def continuation(founders, variant, stop_at_adoption):
    task = task_for(founders,variant)
    # Short forced restart exercises persisted tabu/archive selection too.
    task['config']['restart_after_stagnant_iterations'] = 2
    states,traces,rngs = [],[],[]
    with tempfile.TemporaryDirectory() as temp:
        for interrupted in (False,True):
            state = initial(task)
            rng = random.Random(task['seed'])
            path = Path(temp)/f'{interrupted}.sqlite'
            archive = Archive(path)
            for item in founders:
                archive.put(item)
            obs = Observation(task,state,archive,interrupt_adopt=interrupted and stop_at_adoption)
            engine = Engine(task,state,rng,obs)
            if interrupted:
                try:
                    engine.step(Guard() if stop_at_adoption else PrefixGuard(state))
                except Interrupted:
                    pass
                else:
                    raise AssertionError('Test failed to interrupt')
                saved_rng = json.loads(json.dumps(rng.getstate()))
                state = json.loads(json.dumps(state))
                archive.close()
                archive = Archive(path)
                rng = random.Random()
                rng.setstate(tuple_state(saved_rng))
                obs = Observation(task,state,archive)
                engine = Engine(task,state,rng,obs)
            while len(obs.trace)<4:
                engine.step(Guard())
            traces.append(obs.trace)
            rngs.append(rng.getstate())
            states.append((state['best']['state'],state['tabu'],state['iterations'],state['restarts']))
            archive.close()
    assert traces[0]==traces[1] and rngs[0]==rngs[1] and states[0]==states[1], (variant,stop_at_adoption)
    return {'variant':variant,'interrupted_at':'decision' if stop_at_adoption else 'catalogue',
            'same_next_four_moves_rng_best_tabu_and_restart':True}


def baseline_episode(founders):
    import search
    original = search.MoveSource
    search.MoveSource = fast_moves.MoveSource
    task = task_for(founders,'B0',210921)
    task['config']['baseline_perturb_cpu']=600
    task['config']['baseline_descent_cpu']=600
    rng = random.Random(task['seed'])
    parent = search.parent_choice(founders,'W',rng)
    expected,record,_ = search.episode(parent,'lambda','W','A0',rng,
                           {'perturb_cpu':600,'descent_cpu':600,'sample_size':32},[],0,cpu()+1500)
    expected_rng = rng.getstate()
    search.MoveSource = original
    state = initial(task)
    rng = random.Random(task['seed'])
    with tempfile.TemporaryDirectory() as temp:
        archive = Archive(Path(temp)/'archive.sqlite')
        for item in founders:
            archive.put(item)
        obs = Observation(task,state,archive)
        engine = Engine(task,state,rng,obs)
        while state['episodes']<1:
            engine.step(Guard())
        archive.close()
    assert state['children'][0]['graph6']==expected['graph6']
    assert rng.getstate()==expected_rng
    return {'same_graph6_and_rng':True,'perturb_moves':record['perturb_trades'],'descent_moves':record['descent_trades']}


def solution_controls(founders):
    import worker
    import queueing
    import signal
    from unittest.mock import patch
    from types import SimpleNamespace
    real = worker.verifier.check_graph
    rows = [sum(1<<j for j in range(9) if j!=i and (i//3==j//3 or i%3==j%3)) for i in range(9)]
    graph6 = core.encode_g6(rows)
    fixture = real(graph6,'lambda',expected_n=9,expected_degree=4)
    assert fixture['is_solution']
    assert not real(graph6,'lambda')['is_solution']  # Wrong order for Conway99.
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        directory = root/'tasks'/'fixture'
        directory.mkdir(parents=True)
        obs = worker.Observer(directory,{'id':'fixture'},{},None,None,0,60)
        try:
            obs.solution(founders[0])
        except ValueError:
            pass
        else:
            raise AssertionError('Non-solution accepted')
        assert not (root/'SOLUTION.json').exists()
        # Plumbing test with real independent verifier on known srg(9,4,1,2).
        # Production always retains defaults n=99 and k=14.
        with patch.object(worker,'verifier',SimpleNamespace(check_graph=lambda text,arm:real(text,arm,expected_n=9,expected_degree=4))):
            obs.solution({'graph6':graph6,'scores':{'F':0}})
        assert read_json(root/'SOLUTION.json')['verification']['is_solution']
        handlers = {s:signal.getsignal(s) for s in (signal.SIGTERM,signal.SIGINT)}
        pool = queueing.Queue(root)
        try:
            with patch.object(queueing.Pool,'check',return_value={}), patch.object(queueing,'checked',return_value=(rows,{'F':0})):
                pool.check()
            assert pool.stop and pool.last_reason==['VERIFIED_SOLUTION']
            atomic(root/'SOLUTION.json',{'candidate':founders[0]})
            with patch.object(queueing.Pool,'check',return_value={}):
                try:
                    pool.check()
                except RuntimeError:
                    pass
                else:
                    raise AssertionError('Controller accepted false success')
        finally:
            pool.lock.close()
            for sig,handler in handlers.items():
                signal.signal(sig,handler)
    return {'false_zero_rejected':True,'wrong_order_rejected':True,
            'positive_fixture':'srg(9,4,1,2) verifier + injected plumbing test; no Conway99 solution',
            'durable_marker_and_controlled_stop':True}


def read_json(path):
    return json.loads(path.read_text())


def run():
    started = cpu()
    founders = json.loads((bootstrap.HERE/'founders.json').read_text())
    review = json.loads((bootstrap.ROOT/'docs/memetik/lambda_review_20260921/CHECK.json').read_text())
    cases = founders+review['review_graphs']
    census = []
    scored = 0
    for index,item in enumerate(cases):
        rows,scores = checked(item['graph6'],'lambda')
        exact = set(apex_exact(rows,Guard()))
        reference = set(fast_moves.apex_moves(rows))
        assert exact==reference
        pivot = set(pivots(rows,Guard()))
        # Exhaustive independent proposal validation on six representative founders.
        if index<6:
            assert pivot==check_review.brute_pivots(rows)
        counts = {}
        scorer = Scorer(rows)
        assert scorer.scores==scores
        for name,move in catalogue(rows,True,Guard()):
            counts[name] = counts.get(name,0)+1
            child,incremental = scorer.evaluate(move)
            full = core.metrics(child)
            assert incremental=={k:full[k] for k in incremental}
            core.validate(child,'lambda')
            assert core.apply_move(child,move[::-1])==rows
            scored += 1
        census.append({'line':item.get('line',item.get('name')),'counts':counts})
    hog = next(f for f in founders if f['line']=='hog57338')
    descents = {}
    for target in ('W','L1'):
        rows = core.decode_g6(hog['graph6'])
        while True:
            scorer = Scorer(rows)
            choices = [(move,scorer.evaluate(move)) for _,move in catalogue(rows,False,Guard())]
            better = [(move,child,scores) for move,(child,scores) in choices if key(scores,target)<key(scorer.scores,target)]
            if not better:
                break
            _,rows,_ = min(better,key=lambda x:(key(x[2],target),x[0]))
        expected = review['hog_descents'][target]
        assert core.encode_g6(rows)==expected['graph6']
        descents[target] = core.metrics(rows)
    continuations = [continuation(founders,v,point) for v in ('B0','P','T','TC') for point in (False,True)]
    # No 64-entry cap: distinct valid labelled graphs may collapse canonically,
    # so feed one hundred explicitly unique storage fixture keys for this DB test.
    with tempfile.TemporaryDirectory() as temp:
        archive = Archive(Path(temp)/'archive.sqlite')
        for i in range(100):
            archive.put({**hog,'class':f'storage-fixture-{i}'})
        assert archive.count()==100
        archive.close()
        archive = Archive(Path(temp)/'archive.sqlite')
        assert archive.count()==100
        archive.close()
    return {'status':'CONTROLS_PASS','cases':census,'all_move_score_inverse_and_lambda_checks':scored,
            'brute_force_pivot_cases':6,'reproduced_descents':descents,'continuations':continuations,
            'baseline_episode':baseline_episode(founders),'success_path':solution_controls(founders),'archive_100_storage_fixture_entries':True,
            'cpu_seconds':cpu()-started,'scope':'local controls, not campaign results or Ryzen throughput'}


if __name__=='__main__':
    import sys
    report = run()
    if len(sys.argv)>1:
        atomic(Path(sys.argv[1]),report)
    print(json.dumps(report,indent=2))
