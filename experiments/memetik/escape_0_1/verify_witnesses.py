"""Independent witness replay: python verify_witnesses.py RUN_DIRECTORY"""
import hashlib
import json
from pathlib import Path
import sys
from core import apply_move, decode_g6, metrics, validate
from runner import independent, key


def check(directory):
    directory = Path(directory)
    config = json.loads((directory / 'config.json').read_text())
    founders = {item['id']: item for item in config['founders']}
    total = 0
    for path in directory.glob('*__*.json'):
        data = json.loads(path.read_text())
        item = founders[data['founder']]
        parent = decode_g6(item['graph6'])
        for objective, witness in data['best_witness'].items():
            child = apply_move(parent, (tuple(map(tuple, witness['deleted'])), tuple(map(tuple, witness['added']))))
            validate(child, item['arm'])
            assert child == decode_g6(witness['graph6'])
            assert hashlib.sha256((witness['graph6']+'\n').encode()).hexdigest() == witness['sha256']
            actual = metrics(child)
            assert json.loads(json.dumps(actual)) == witness['metrics']
            assert all(actual[k] == v for k, v in independent(child).items())
            assert key(actual, objective) < key(item['metrics'], objective)
            assert witness['path_length'] == 1
            total += 1
    return {'witnesses_replayed_and_verified': total}


if __name__ == '__main__':
    print(json.dumps(check(sys.argv[1])))
