import bootstrap
"""Immutable audit selection and preregistered control selection; no census rerun."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODEL = 'ROOT8105-depth2-lemma-falsification-1.0.0'
PLAN_SHA = '946fa4f19370e5df2871bfe11a78b4afc5de95f601e5345b8f6394b7fafb8ae0'
RULES_COMMIT = '40c0050af19353fd9c9d1a203e58f5df07636229'
VARIANTS = [('F', False, False), ('F_LD', True, False),
            ('F_CAP', False, True), ('F_LD_CAP', True, True)]


def selection():
    data = (BASE / 'supplement_manifest.json').read_bytes()
    if hashlib.sha256(data).hexdigest() != PLAN_SHA:
        raise ValueError('frozen filter selection changed')
    return json.loads(data)


def jobs():
    from kernel import load_roots
    roots = {r['id']: r for r in load_roots()}
    out = []
    for chosen in selection()['roots']:
        root = roots[chosen['root']]
        if any(root[k] != chosen[v] for k, v in [('row', 'root_row'), ('type', 'type')]):
            raise ValueError('selection root identity mismatch')
        out.append(root | {'targets': chosen['targets'], 'kind': 'sample'})
    if len(out) != 24 or sum(len(r['targets']) for r in out) != 48:
        raise ValueError('selection dimensions')
    out.append({'id': 0, 'row': '0x0', 'type': -1, 'kind': 'controls'})
    return out


def keys(root, test=False):
    return set(map(str, range(1, 84))) if test else (
        {'1'} if root['kind'] in ('controls', 'tree') else {str(t['target']) for t in root['targets']})


def choose_controls(cases):
    """First eight DISTINCT states per (type, reason), across rejecting variants.

    A selected state is checked under every rejecting variant, preserving CAP's
    dependence on LD. Membership is fixed by this rule before any pilot outcome.
    """
    buckets = {}
    for c in sorted(cases, key=lambda x: (x['root'], x['target'], x['rank'])):
        reasons = sorted({v['reason'] for v in c['variants'].values() if not v['pass']})
        for reason in reasons:
            bucket = buckets.setdefault((c['type'], reason), [])
            if len(bucket) < 8:
                bucket.append(c)
    return [{'type': typ, 'reason': reason, 'cases': items}
            for (typ, reason), items in sorted(buckets.items())]
