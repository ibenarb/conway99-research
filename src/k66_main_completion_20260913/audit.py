"""Audit submitted tree and checker logs; does not replay proof files."""
import collections
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

archive = Path(sys.argv[1])
expected = 'ae44c1274c5c3c646f964475e3c6a6057bb11525105144e2f41126ad54f0ebbb'
assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist()) == len(set(z.namelist()))
    assert z.testzip() is None
    manifest = json.loads(z.read('manifest.json'))
    summary = json.loads(z.read('summary.json'))
    state = json.loads(z.read('state.json'))
    cubes = state['cubes']
    roots = summary['roots']
    assert set(roots) == set(manifest['roots']) == set(manifest['root_hashes'])
    seen = set()
    counts = {}
    compressed = 0
    raw = 0
    for root in roots:
        stack = [root]
        tally = collections.Counter()
        assert cubes[root]['parent'] is None and cubes[root]['lits'] == []
        while stack:
            key = stack.pop()
            assert key not in seen
            seen.add(key)
            node = cubes[key]
            assert node['id'] == key and node['root_id'] == root
            assert node['depth'] == len(node['lits'])
            assert len(set(map(abs, node['lits']))) == len(node['lits'])
            tally[node['status']] += 1
            if node['status'] == 'SPLIT':
                v = node['split_var']
                assert isinstance(v, int) and v > 0 and v not in map(abs, node['lits'])
                for suffix, literal in [('0', -v), ('1', v)]:
                    child = cubes[key + suffix]
                    assert child['parent'] == key
                    assert child['lits'] == node['lits'] + [literal]
                    stack.append(key + suffix)
            else:
                assert node['status'] == 'CERTIFIED'
                checker = node['checker']
                assert checker['status'] == 'CERTIFIED'
                assert checker['cake_exit'] == checker['lrat_exit'] == 0
                assert checker['cake_marker'] is True and checker['lrat_marker'] is True
                assert 'c VERIFIED' in z.read(key + '/lrat.out').decode().splitlines()
                assert 's VERIFIED UNSAT' in z.read(key + '/cake.out').decode().splitlines()
                for tool in ['lrat', 'cake']:
                    assert z.read(key + '/' + tool + '.err') == b''
                for field in ['proof_gz_sha256', 'proof_raw_sha256']:
                    assert re.fullmatch('[0-9a-f]{64}', checker[field])
                assert node['solver']['proof_sha256'] == checker['proof_raw_sha256']
                assert node['solver']['proof_bytes'] == checker['proof_raw_bytes']
                compressed += checker['proof_gz_bytes']
                raw += checker['proof_raw_bytes']
        assert tally['CERTIFIED'] == tally['SPLIT'] + 1
        assert sum(tally.values()) == summary['coverage_audit'][root]
        counts[root] = dict(tally)
    assert seen == set(cubes)
    assert sum(c['CERTIFIED'] for c in counts.values()) == summary['certified_leaves'] == 897
    assert sum(c['SPLIT'] for c in counts.values()) == summary['splits'] == 890
    out = dict(status='PASS_TREE_AND_CHECKER_LOG_AUDIT', archive_sha256=expected,
               roots=counts, root_hashes=manifest['root_hashes'], nodes=len(seen),
               compressed_proof_GiB=compressed / 2**30, raw_proof_GiB=raw / 2**30,
               started_at=state['started_at'], completed_at=state['completed_at'],
               scope='Exact partition and archived checker logs checked; proof bytes and leaf CNFs absent, not replayed. Upstream removals not certified by this run.')
    print(json.dumps(out, indent=2))
