"""Recheck published data and small catalogues; never opens the Ryzen run.

Run from any directory. Writes only into the new planning directory.
No search campaign, canonicalization, original-archive audit or clock diagnosis.
"""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'docs/memetik/lambda_results_20260922'
OUT = ROOT / 'docs/memetik/lambda_plan_codex_20260922'
FIELDS = ('W', 'L1', 'F', 'Linf', 'Nmax')
CACHE = {}


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def key(scores, target):
    fields = {'W': ('W', 'L1'), 'L1': ('L1',), 'F': ('F',),
              'Linf': ('Linf', 'Nmax', 'L1')}[target]
    return tuple(scores[f] for f in fields)


def decode(text):
    """Separate decoder; no imported decoder, bitset intersection or score code."""
    payload = text.encode('ascii')
    assert payload[:1] == b'~' and len(payload) == 813
    assert all(63 <= c <= 126 for c in payload)
    order = sum((payload[i + 1] - 63) * 64 ** (2 - i) for i in range(3))
    assert order == 99
    stream = ''.join(format(c - 63, '06b') for c in payload[4:])
    neighbors = [set() for _ in range(order)]
    offset = 0
    for v in range(1, order):
        for u, bit in enumerate(stream[offset:offset + v]):
            if bit == '1':
                neighbors[u].add(v)
                neighbors[v].add(u)
        offset += v
    assert set(stream[offset:]) <= {'0'}
    return neighbors


def measure(neighbors):
    n = len(neighbors)
    assert n == 99
    assert all(len(row) == 14 and i not in row for i, row in enumerate(neighbors))
    assert all(i in neighbors[j] for i, row in enumerate(neighbors) for j in row)
    hist = Counter()
    row_sums = [0] * n
    cn_pairs = 0
    triangles = 0
    for v in range(n):
        for u in range(v):
            common = len(neighbors[u] & neighbors[v])
            edge = int(v in neighbors[u])
            assert not edge or common == 1
            r = common + edge - 2
            hist[r] += 1
            row_sums[u] += r
            row_sums[v] += r
            cn_pairs += common * (common - 1) // 2
            triangles += edge * common
    assert not any(row_sums) and triangles == 693
    maximum = max(abs(r) for r in hist)
    scores = {'W': sum(c for r, c in hist.items() if r),
              'L1': sum(abs(r) * c for r, c in hist.items()),
              'F': sum(r * r * c for r, c in hist.items()),
              'Linf': maximum,
              'Nmax': sum(c for r, c in hist.items() if abs(r) == maximum)}
    assert scores['F'] == 2 * cn_pairs - 8316
    assert scores['F'] % 4 == 0 and scores['L1'] % 2 == 0
    if maximum == 2:
        assert scores['L1'] == scores['W'] + scores['Nmax']
        assert scores['F'] == scores['W'] + 3 * scores['Nmax']
    return scores


def check(text):
    if text not in CACHE:
        CACHE[text] = measure(decode(text))
    return CACHE[text]


def walk(value):
    if isinstance(value, dict):
        if 'graph6' in value and 'scores' in value:
            assert check(value['graph6']) == {k: value['scores'][k] for k in FIELDS}
            if 'state' in value:
                assert sha(value['graph6'].encode()) == value['state']
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)


def apply(neighbors, move):
    child = [set(row) for row in neighbors]
    for u, v in move[0]:
        assert v in child[u]
        child[u].remove(v)
        child[v].remove(u)
    for u, v in move[1]:
        assert u != v and v not in child[u]
        child[u].add(v)
        child[v].add(u)
    return child


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    start = time.process_time()
    manifest = load(DATA / 'PUBLICATION_MANIFEST.json')
    for path, expected in manifest['files'].items():
        assert sha((ROOT / path).read_bytes()) == expected, path
    endpoints = load(DATA / 'ENDPOINTS.json.gz')
    audit = load(DATA / 'AUDIT.json.gz')
    census = load(DATA / 'RECORD_CENSUS.json')
    summary = load(DATA / 'SUMMARY.json')
    receipts = load(DATA / 'RECEIPTS.json')
    founders = load(ROOT / 'experiments/memetik/lambda_compare_0_2_0/founders.json')
    assert len(endpoints) == 192 and len(receipts) == 193
    for value in (endpoints, census, summary['observed_records_all_targets'], founders):
        walk(value)
    published_unique = len(CACHE)
    assert len({item['seed'] for item in endpoints.values()}) == 12
    for receipt in receipts.values():
        assert receipt['exit_code'] == 0
        assert abs(sum(s['cpu_seconds'] for s in receipt['sessions']) - receipt['cpu_seconds']) < 1e-8
        assert receipt['budget_cpu_seconds'] == receipt['cpu_seconds']
    assert receipts['controls']['status'] == 'CONTROLS_PASS'
    for job, item in endpoints.items():
        assert job == f"{item['variant']}--lambda-{item['target']}-{item['replicate']:02d}"
        receipt = receipts[job]
        assert receipt['status'] == 'COMPLETE' and receipt['exit_code'] == 0
        assert len(receipt['sessions']) == 1 and receipt['closed_reserve_cpu_seconds'] == 0
        assert abs(sum(s['cpu_seconds'] for s in receipt['sessions']) - receipt['cpu_seconds']) < 1e-8
        assert item['cpu_seconds'] == receipt['cpu_seconds'] == receipt['budget_cpu_seconds']
        assert 3595 <= item['cpu_seconds'] <= 3600
        assert item['milestones']['3600']['scores'] == item['best']['scores']
        assert item['milestones']['3600']['graph6_sha256'] == sha(item['best']['graph6'].encode())
        assert key(item['milestones']['600']['scores'], item['target']) >= key(item['milestones']['1800']['scores'], item['target']) >= key(item['best']['scores'], item['target'])
    total_cpu = sum(item['cpu_seconds'] for item in endpoints.values())
    assert abs(total_cpu / 3600 - audit['comparison_cpu_hours']) < 1e-9
    recomputed = []
    for source in audit['comparisons']:
        target, v, c, mark = (source[k] for k in ('target', 'variant', 'comparator', 'milestone_cpu'))
        pairs = [[endpoints[f'{a}--lambda-{target}-{i:02d}']['milestones'][str(mark)]['scores'] for a in (c, v)] for i in range(12)]
        wins = sum(key(b, target) < key(a, target) for a, b in pairs)
        losses = sum(key(b, target) > key(a, target) for a, b in pairs)
        assert pairs == source['paired_scores']
        assert (wins, 12 - wins - losses, losses) == (source['wins'], source['ties'], source['losses'])
        recomputed.append({'target': target, 'variant': v, 'comparator': c, 'mark': mark,
                           'wins': wins, 'ties': 12 - wins - losses, 'losses': losses})
    w_table = []
    for i in range(12):
        jobs = [endpoints[f'{v}--lambda-W-{i:02d}'] for v in ('P', 'T', 'TC')]
        assert len({j['seed'] for j in jobs}) == 1
        w_table.append({'replicate': i, 'seed': jobs[0]['seed'],
                        **{j['variant']: list(key(j['best']['scores'], 'W')) for j in jobs},
                        'delta_W_P_minus_TC': jobs[0]['best']['scores']['W'] - jobs[2]['best']['scores']['W']})
    deltas = [r['delta_W_P_minus_TC'] for r in w_table]
    groups = {}
    for v in ('B0', 'P', 'T', 'TC'):
        jobs = [endpoints[f'{v}--lambda-W-{i:02d}'] for i in range(12)]
        values = sorted(j['best']['scores']['W'] for j in jobs)
        groups[v] = {'W_sorted': values, 'median': statistics.median(values),
                     'tukey_hinges': [statistics.median(values[:6]), statistics.median(values[6:])],
                     'different_labelled_best_graphs': len({j['best']['graph6'] for j in jobs}),
                     'restarts': [j['restarts'] for j in jobs],
                     'iterations': [j['iterations'] for j in jobs]}
    for label, item in census.items():
        for target, witness in item['improving_witnesses'].items():
            child = apply(decode(item['graph6']), witness['move'])
            assert child == decode(witness['graph6'])
            assert measure(child) == witness['scores']
            assert apply(child, witness['move'][::-1]) == decode(item['graph6'])
            assert key(witness['scores'], target) < key(item['scores'], target)
    # Production catalogue is reused; validity and scores are checked independently.
    sys.path.insert(0, str(ROOT / 'experiments/memetik/lambda_compare_0_2_0'))
    import bootstrap
    from common import core
    from kernel import catalogue, Scorer

    class Guard:
        def check(self):
            if time.process_time() - start > 240:
                raise RuntimeError('Diagnostic allowance exhausted; no completeness claim')

    guard = Guard()
    checked_moves = 0
    census_rechecked = {}
    for label, item in census.items():
        rows = core.decode_g6(item['graph6'])
        counts = {}
        scorer = Scorer(rows)
        for operator, move in catalogue(rows, True, guard):
            child, fast = scorer.evaluate(move)
            neighbors = apply(decode(item['graph6']), move)
            exact = measure(neighbors)
            assert exact == fast
            assert decode(core.encode_g6(child)) == neighbors
            assert apply(neighbors, move[::-1]) == decode(item['graph6'])
            count = counts.setdefault(operator, {'moves': 0, 'improving': dict.fromkeys(('W', 'L1', 'F', 'Linf'), 0)})
            count['moves'] += 1
            for target in count['improving']:
                count['improving'][target] += key(exact, target) < key(item['scores'], target)
            checked_moves += 1
        assert counts == item['catalogue'], label
        census_rechecked[label] = counts
    # A small strict descent on two already published witnesses, no stochastic search.
    descents = {}
    for target in ('W', 'Linf'):
        item = census['observed_' + target]['improving_witnesses'][target]
        graph6 = item['graph6']
        steps = []
        while True:
            rows = core.decode_g6(graph6)
            current = check(graph6)
            scorer = Scorer(rows)
            choice = None
            size = 0
            for operator, move in catalogue(rows, True, guard):
                child, scores = scorer.evaluate(move)
                size += 1
                assert measure(apply(decode(graph6), move)) == scores
                if key(scores, target) < key(current, target):
                    order = (key(scores, target), move)
                    if choice is None or order < choice[0]:
                        choice = order, operator, move, core.encode_g6(child), scores
            if choice is None:
                break
            _, operator, move, child_text, scores = choice
            assert check(child_text) == scores
            assert apply(decode(graph6), move) == decode(child_text)
            steps.append({'operator': operator, 'move': move, 'graph6': child_text, 'scores': scores})
            graph6 = child_text
        descents[target] = {'start_graph6': item['graph6'], 'start_scores': item['scores'],
                            'steps': steps, 'graph6': graph6, 'scores': check(graph6),
                            'graph6_sha256': sha(graph6.encode()),
                            'status': 'LOCAL_MIN_EXACT_APC', 'final_catalogue_size': size,
                            'scope': 'new post-run deterministic diagnostic; not a historical endpoint'}
    result = {'status': 'PUBLISHED_DATA_AND_SMALL_DIAGNOSTICS_PASS',
              'original_archive_opened': False, 'published_hashes_checked': len(manifest['files']),
              'endpoint_jobs_checked': 192, 'receipt_arithmetic_checked': 193,
              'unique_published_labelled_graphs_checked': published_unique,
              'milestone_limit': '600/1800 score arithmetic checked; missing intermediate graph6 not independently decoded',
              'comparisons_checked': len(recomputed), 'comparison_cpu_hours': total_cpu / 3600,
              'controls_cpu_seconds_from_receipt': receipts['controls']['cpu_seconds'],
              'census_moves_independently_validated': checked_moves,
              'catalogue_completeness': 'enumeration by pinned project code; no independent exhaustive cycle enumeration',
              'canonical_certificates_recomputed': False,
              'W_groups': groups, 'W_pairs': w_table,
              'P_minus_TC_delta_W_mean': statistics.mean(deltas),
              'P_minus_TC_delta_W_median': statistics.median(deltas),
              'comparisons': recomputed, 'census': census_rechecked,
              'diagnostic_cpu_seconds': time.process_time() - start}
    write('OWN_CHECK.json', result)
    write('POSTRUN_DESCENTS.json', descents)
    (OUT / 'W_PAIRS.tsv').write_text('replicate\tseed\tP_W\tP_L1\tT_W\tT_L1\tTC_W\tTC_L1\n' + ''.join('\t'.join(map(str, [r['replicate'], r['seed'], *r['P'], *r['T'], *r['TC']])) + '\n' for r in w_table))
    print(json.dumps({k: v for k, v in result.items() if k not in ('comparisons', 'census', 'W_pairs', 'W_groups')}, indent=2))
    print(json.dumps({t: {k: v for k, v in d.items() if k not in ('graph6', 'start_graph6', 'steps')} | {'steps': len(d['steps'])} for t, d in descents.items()}, indent=2))


if __name__ == '__main__':
    main()
