"""Small review audit; no new search campaign and no depth-3/4 replay.
Usage via tools/memetik/audit_python.py -- SCRIPT ORIGINAL_ZIP OUTPUT_DIR
Reviewer scripts are executed with only their frozen source path relocated.
"""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
archive = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(archive.read_bytes()) == '2299db62ac1b77ed90b2e83a7be6101970f7725e4d73e539f032497c0d1d9f69'
with zipfile.ZipFile(archive) as z:
    files = {Path(n).name: z.read(n) for n in z.namelist() if not n.endswith('/')}
assert len(files) == 20
entries = []
for line in files['SHA256SUMS'].decode().splitlines():
    digest, name = line.split()
    assert sha(files[name]) == digest, name
    entries.append(name)
assert set(entries) == set(files) - {'SHA256SUMS'}
pinned_sources = json.loads(files['QUELLEN.json'])['input_sha256']
for spec, digest in pinned_sources.items():
    path = spec.split(' @')[0]
    assert sha((ROOT / path).read_bytes()) == digest, path
assert files['REVIEWPROMPT_gelesen.md'] == (ROOT / 'docs/memetik/lambda_radius_20260926/REVIEWPROMPT_NAECHSTER_SCHRITT.md').read_bytes()
source = ROOT / 'experiments/memetik/lambda_radius_1_0_0'
sys.path.insert(0, str(source))
import boot
from support import core
starts = json.loads((source / 'STARTS.json').read_text())
claimed = json.loads(files['indep_scores.json'])
score_results = {}
for label, s in starts.items():
    rows = core.decode_g6(s['graph6'])
    adj = [{j for j in range(len(rows)) if row >> j & 1} for row in rows]
    hist = {}
    q2 = nonedge_sum = 0
    for u, v in itertools.combinations(range(len(rows)), 2):
        c = len(adj[u] & adj[v])
        edge = v in adj[u]
        assert not edge or c == 1
        r = c + int(edge) - 2
        hist[str(r)] = hist.get(str(r), 0) + 1
        q2 += c * (c - 1) // 2
        if not edge:
            nonedge_sum += r
    assert len(rows) == 99 and {len(a) for a in adj} == {14}
    assert q2 % 2 == 0 and nonedge_sum == 0
    vals = [int(r) for r, n in hist.items() for _ in range(n)]
    scores = dict(W=sum(r != 0 for r in vals), L1=sum(abs(r) for r in vals),
                  F=sum(r * r for r in vals), Linf=max(map(abs, vals)))
    scores['Nmax'] = sum(abs(r) == scores['Linf'] for r in vals)
    assert scores == s['scores']
    assert hist == claimed[label]['hist']
    assert q2 // 2 == claimed[label]['Q']
    assert sha(s['graph6'].encode()) == s['state']
    score_results[label] = dict(scores=scores, Q=q2 // 2, hist=hist)
replayed = {}
for name in ('twoswitch_completeness', 'cycle3_census'):
    code = files[name + '.py'].decode().replace('/home/claude/src/experiments/memetik/lambda_radius_1_0_0', str(source))
    p = subprocess.run([sys.executable, '-c', code], cwd=out, text=True, capture_output=True, timeout=180)
    (out / (name + '.log')).write_text(p.stdout + p.stderr)
    assert p.returncode == 0, (name, p.stderr)
    actual = json.loads((out / (name + '.json')).read_text())
    assert actual == json.loads(files[name + '.json'])
    replayed[name] = actual
# Reproduce episode aggregate by reading frozen result bytes, without extracting archives.
agg = {}
with zipfile.ZipFile(ROOT / 'releases/memetik/Lambda_Review_20260926.zip') as z:
    expected = json.loads(files['episode_histograms.json'])
    for campaign in ('F', 'O'):
        total = dict(episodes=0, returned=0, iso=0, short=0, mid=0, long=0)
        jobs = []
        for n in sorted(z.namelist()):
            if not (n.startswith(campaign + '__runs__comparison__tasks__') and n.endswith('__result.json')):
                continue
            result = json.loads(z.read(n))
            h = result['histogram']
            num = sum(h['returned'].values())
            assert num == sum(h['perturb_length'].values()) == sum(h['stop'].values())
            assert h['stop'] == {'LOCAL_MIN_EXACT_AP': num}
            total['episodes'] += num
            total['returned'] += h['returned'].get('True', 0)
            total['iso'] += h['isomorphic_return'].get('True', 0)
            for k, v in h['perturb_length'].items():
                total['short' if int(k) <= 4 else 'mid' if int(k) <= 12 else 'long'] += v
            jobs.append(n)
        assert total == expected[campaign]['total']
        agg[campaign] = dict(total=total, jobs=len(jobs), return_fraction=total['returned'] / total['episodes'],
                             joint_length_return_histogram_available=False,
                             min_returns_length_ge5=max(0, total['returned'] - total['short']),
                             min_return_fraction_length_ge5=max(0, total['returned'] - total['short']) / (total['mid'] + total['long']))
# Internal consistency of submitted depth-3 outputs, not a new enumeration.
depth3 = {}
for label in ('2076', '2077'):
    r = json.loads(files['depth3_' + label + '.json'])
    assert sum(r['W_hist_depth3'].values()) == r['distinct_new_depth3']
    assert sum(r['W_hist_by_depth']['2'].values()) == r['parents']
    log = files['depth3_' + label + '.log'].decode().splitlines()
    assert json.loads(log[-1]) == r
    depth3[label] = dict(parents=r['parents'], children=r['children'], new3=r['distinct_new_depth3'],
                        minimum_exact_depth3=r['best5_WL1_depth3'][0][0],
                        sample_upper_transition_index_exclusive=450000,
                        unsampled_tail_transitions=r['children'] - 449999,
                        replayed_here=False)
report = dict(status='PASS_SMALL_CHECKS', archive_sha256=sha(archive.read_bytes()), files=len(files),
              manifest_entries=len(entries), source_hashes=len(pinned_sources), prompt_byteidentical=True,
              scores=score_results, replayed=replayed, episodes=agg, depth3_internal_consistency=depth3,
              limits=['No new depth3/depth4 enumeration', 'Graph6 decoder shared for independent score check',
                      'Reviewer recommendation text absent', 'No state checkpoint or SQLite in submission'])
(out / 'AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
