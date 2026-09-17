import sys, time, json, pathlib, sqlite3
sys.path.insert(0, str(pathlib.Path(__file__).parent / 'source'))
from core import decode_g6, encode_g6
from search import neighbors, short, independent
name, arm, obj, threshold = sys.argv[1:]
threshold = int(threshold)
db = sqlite3.connect('file:' + str(pathlib.Path('audit022', name + '.sqlite').resolve()) + '?mode=ro', uri=True)
root = db.execute('select g6 from nodes where depth=0').fetchone()[0]
base = short(decode_g6(root))[obj]

class Budget:

    def __init__(self):
        self.start = time.process_time()

    def check(self):
        if time.process_time() - self.start > 240:
            raise TimeoutError('CPU_LIMIT')
budget = Budget()
queue = [root]
seen = {root}
states = []
boundary = None
transitions = 0
status = 'COMPONENT_CLOSED'
edges = []
try:
    for g in queue:
        rows = decode_g6(g)
        m = short(rows)
        assert m == independent(rows)
        census = {}
        for family, move, child in neighbors(rows, arm, budget, census):
            cm = short(child)
            cg = encode_g6(child)
            transitions += 1
            if cm[obj] < threshold:
                edges.append([g, cg])
                if cg not in seen:
                    seen.add(cg)
                    queue.append(cg)
                    if len(queue) > 3000:
                        raise TimeoutError('STATE_LIMIT')
            else:
                boundary = min(boundary or cm[obj], cm[obj])
        states.append({'graph6': g, 'metrics': m, 'census': census})
        if len(states) % 20 == 0:
            print(name, len(states), len(queue), flush=True)
except TimeoutError as e:
    status = str(e)
r = {'task': name, 'strict_threshold': threshold, 'baseline': base, 'status': status, 'discovered': len(queue), 'expanded': len(states), 'transitions': transitions, 'minimum_boundary': boundary, 'minimum_inside': min((s['metrics'][obj] for s in states)), 'cpu_seconds': time.process_time() - budget.start, 'states': states, 'internal_edges': edges}
pathlib.Path('analysis022', name + '_sublevel.json').write_text(json.dumps(r, indent=4))
print(json.dumps({k: v for k, v in r.items() if k not in ('states', 'internal_edges')}), flush=True)
