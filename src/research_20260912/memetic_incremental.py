"""Research-only exact incremental metrics. No production runner is changed."""
from collections import Counter


def prepare(rows):
    n = len(rows)
    histogram = Counter()
    defects = [0] * n
    lambda_bad = triangle_sum = c4_sum = 0
    for i in range(n):
        for j in range(i):
            common = (rows[i] & rows[j]).bit_count()
            adjacent = (rows[i] >> j) & 1
            residual = common + adjacent - 2
            histogram[residual] += 1
            defects[i] += int(residual != 0)
            defects[j] += int(residual != 0)
            lambda_bad += int(adjacent and common != 1)
            triangle_sum += adjacent * common
            c4_sum += common * (common-1)//2
    return histogram, defects, lambda_bad, triangle_sum, c4_sum


def update(old, new, state, touched):
    histogram, defects, lambda_bad, triangle_sum, c4_sum = state
    histogram, defects = histogram.copy(), defects.copy()
    touched = set(touched)
    n = len(old)
    for i in sorted(touched):
        for j in range(n):
            if j == i or (j in touched and j < i):
                continue
            oc = (old[i] & old[j]).bit_count()
            nc = (new[i] & new[j]).bit_count()
            oa = (old[i] >> j) & 1
            na = (new[i] >> j) & 1
            before, after = oc + oa - 2, nc + na - 2
            histogram[before] -= 1
            histogram[after] += 1
            change = int(after != 0) - int(before != 0)
            defects[i] += change
            defects[j] += change
            lambda_bad += int(na and nc != 1) - int(oa and oc != 1)
            triangle_sum += na*nc - oa*oc
            c4_sum += nc*(nc-1)//2 - oc*(oc-1)//2
    return histogram, defects, lambda_bad, triangle_sum, c4_sum


def metrics(state):
    hist, defects, lb, ts, cs = state
    hist = {r: count for r, count in hist.items() if count}
    largest = max(map(abs, hist), default=0)
    return {'F': sum(r*r*c for r, c in hist.items()),
            'W': sum(c for r, c in hist.items() if r),
            'L1': sum(abs(r)*c for r, c in hist.items()),
            'Linf': largest, 'Nmax': sum(c for r, c in hist.items() if abs(r) == largest),
            'lambda_bad': lb, 'triangles': ts//3, 'C4': cs//2,
            'residual_histogram': dict(sorted(hist.items())),
            'defect_degrees': sorted(defects), 'max_defect_degree': max(defects, default=0)}
