import json
import gzip
from pathlib import Path
from verify_results import check

root = Path(__file__).parent
for name, selections in json.loads(gzip.decompress((root / 'extrema_witnesses.json.gz').read_bytes()).decode()).items():
    arm = 'lambda' if name.startswith('HoG') else 'omega'
    for selection in selections.values():
        previous = None
        for entry in selection['path']:
            adjacency, metrics = check(entry['graph6'], arm)
            assert metrics == entry['metrics']
            if previous is not None:
                for i, j in entry['move']['deleted']:
                    previous[i].remove(j)
                    previous[j].remove(i)
                for i, j in entry['move']['added']:
                    assert j not in previous[i]
                    previous[i].add(j)
                    previous[j].add(i)
                assert previous == adjacency
            previous = adjacency
print('PASS: all selected extrema witnesses, arms, scores and parent transitions')
