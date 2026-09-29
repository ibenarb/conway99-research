"""Independent set-based graph6, lambda and full residual checks. No OR-Tools."""
import hashlib
from collections import Counter


def decode(text):
    data = [ord(c) - 63 for c in text.strip()]
    if not data or any(not 0 <= x < 64 for x in data):
        raise ValueError('Invalid graph6 bytes')
    if data[0] == 63:
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        data = data[4:]
    else:
        n, data = data[0], data[1:]
    if not 1 <= n <= 99 or len(data) != (n * (n - 1) // 2 + 5) // 6:
        raise ValueError('Invalid graph6 size')
    rows = [set() for _ in range(n)]
    i = 0
    for v in range(n):
        for u in range(v):
            if (data[i // 6] >> (5 - i % 6)) & 1:
                rows[u].add(v)
                rows[v].add(u)
            i += 1
    if i % 6 and data[-1] & ((1 << (6 - i % 6)) - 1):
        raise ValueError('Nonzero graph6 padding')
    return rows


def encode(rows):
    n = len(rows)
    values = [n] if n < 63 else [63, (n >> 12) & 63, (n >> 6) & 63, n & 63]
    bits = [int(u in rows[v]) for v in range(n) for u in range(v)]
    bits += [0] * (-len(bits) % 6)
    for k in range(0, len(bits), 6):
        values.append(sum(bits[k + i] << (5 - i) for i in range(6)))
    return ''.join(chr(x + 63) for x in values)


def checked(graph6, degree=14, lam=1, target=2):
    rows = decode(graph6)
    if any(len(row) != degree for row in rows):
        raise ValueError('Degree violated')
    hist = Counter()
    for v in range(len(rows)):
        for u in range(v):
            cn = len(rows[u].intersection(rows[v]))
            edge = int(v in rows[u])
            if edge and cn != lam:
                raise ValueError('Lambda violated')
            hist[cn + edge - target] += 1
    maximum = max(map(abs, hist))
    scores = {'W': sum(c for r, c in hist.items() if r), 'L1': sum(abs(r) * c for r, c in hist.items()),
              'F': sum(r * r * c for r, c in hist.items()), 'Linf': maximum,
              'Nmax': sum(c for r, c in hist.items() if abs(r) == maximum)}
    return rows, scores


def record(graph6, **kwargs):
    _, scores = checked(graph6, **kwargs)
    return {'graph6': graph6, 'state': hashlib.sha256(graph6.encode()).hexdigest(), 'scores': scores}


def window_check(graph6, founder, vertices):
    rows, scores = checked(graph6)
    base, _ = checked(founder)
    inside = set(vertices)
    for v in range(len(rows)):
        for u in range(v):
            if not (u in inside and v in inside) and ((u in rows[v]) != (u in base[v])):
                raise ValueError('Frozen edge changed')
    return scores


def key(scores):
    return scores['W'], scores['L1']


def mask_check(graph6, founder, edge_mask, radius=None, **parameters):
    """Independently check frozen pairs and distance from the original founder."""
    rows, scores = checked(graph6, **parameters)
    base, _ = checked(founder, **parameters)
    if len(rows) != len(base):
        raise ValueError('Founder size mismatch')
    allowed = set()
    for pair in edge_mask:
        if len(pair) != 2 or any(type(v) is not int for v in pair):
            raise ValueError('Invalid edge mask pair')
        u, v = pair
        if not 0 <= u < v < len(rows) or (u, v) in allowed:
            raise ValueError('Edge mask must contain unique ordered pairs')
        allowed.add((u, v))
    distance = 0
    for v in range(len(rows)):
        for u in range(v):
            if (v in rows[u]) != (v in base[u]):
                if (u, v) not in allowed:
                    raise ValueError('Frozen edge changed outside mask')
                distance += 1
    if radius is not None:
        if type(radius) is not int or radius < 0:
            raise ValueError('Radius must be a nonnegative integer')
        if distance > radius:
            raise ValueError('Founder-centered Hamming radius violated')
    return scores


def task_check(graph6, founder, task, **parameters):
    if 'edge_mask' in task:
        mask = task['edge_mask']
    else:
        n = len(decode(founder))
        inside = set(task['vertices'])
        mask = [(u, v) for v in range(n) for u in range(v) if u in inside and v in inside]
    return mask_check(graph6, founder, mask, task.get('radius'), **parameters)
