"""Independent integer audit of the two cited memetic founders.
Run from the repository root: python3 src/memetik/audit_founders.py
No project-module or third-party imports are required.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PAIRS = list(combinations(range(14), 2))
OUTER = [(a, b) for a, b in PAIRS if b - a != 7]


def read_graph(path):
    raw = path.read_bytes()
    text = raw.decode("ascii").strip()
    values = [ord(c) - 63 for c in text]
    assert len(values) >= 4 and values[0] == 63 and values[1] < 63
    assert all(0 <= v <= 63 for v in values)
    n = (values[1] << 12) + (values[2] << 6) + values[3]
    assert n == 99
    size = n * (n - 1) // 2
    assert len(values) == 4 + (size + 5) // 6
    assert values[-1] & ((1 << ((-size) % 6)) - 1) == 0
    adj = [set() for _ in range(n)]
    position = 0
    for j in range(1, n):
        for i in range(j):
            bit = (values[4 + position // 6] >> (5 - position % 6)) & 1
            if bit:
                adj[i].add(j)
                adj[j].add(i)
            position += 1
    assert all(len(row) == 14 and i not in row for i, row in enumerate(adj))
    return adj, hashlib.sha256(raw).hexdigest()


def omega_checks(adj):
    expected = [set(range(1, 15))] + [set() for _ in range(98)]
    for label in range(14):
        expected[label + 1] = {0, 1 + (label + 7) % 14}
    for i, pair in enumerate(OUTER):
        expected[i + 15] = {a + 1 for a in pair} | {v for v in adj[i + 15] if v >= 15}
        for a in pair:
            expected[a + 1].add(i + 15)
    frame = expected == adj
    violations = 0
    for i, pair in enumerate(OUTER):
        for label in range(14):
            target = 1 if label in pair or (label + 7) % 14 in pair else 2
            observed = sum(j + 15 in adj[i + 15] for j, p in enumerate(OUTER) if label in p)
            violations += observed != target
    return {"canonical_frame": frame, "P_margin_violations": violations,
            "valid_in_supplied_frame": frame and violations == 0}


def audit(path):
    adj, digest = read_graph(path)
    hist = Counter()
    edge_hist = Counter()
    for i, j in combinations(range(99), 2):
        r = len(adj[i] & adj[j]) + int(j in adj[i]) - 2
        hist[r] += 1
        if j in adj[i]:
            edge_hist[r] += 1
    assert sum(hist.values()) == 4851
    assert sum(r * count for r, count in hist.items()) == 0
    return {"file": path.name, "sha256": digest, "n": 99, "degree": 14,
            "W": sum(c for r, c in hist.items() if r),
            "L1": sum(abs(r) * c for r, c in hist.items()),
            "L2_squared": sum(r * r * c for r, c in hist.items()),
            "Linf": max(map(abs, hist)), "lambda_violations": sum(c for r, c in edge_hist.items() if r),
            "residual_histogram": dict(sorted(hist.items())),
            "edge_residual_histogram": dict(sorted(edge_hist.items())),
            "omega": omega_checks(adj)}


def main():
    folder = ROOT / "data/memetic_v2/reference"
    reports = [audit(folder / name) for name in ("B_maple_20260829.g6", "hog57338.g6")]
    b, hog = reports
    assert (b["W"], b["L1"], b["L2_squared"], b["Linf"]) == (2110, 3512, 9716, 10)
    assert b["omega"]["valid_in_supplied_frame"] and b["lambda_violations"] == 460
    assert (hog["W"], hog["L1"], hog["L2_squared"], hog["Linf"]) == (2182, 2398, 2836, 3)
    assert hog["lambda_violations"] == 0
    result = {"status": "PASS", "scope": "Two archived founders; no live pilot or new search",
              "source_commit": "31c563f6ba460227c6ae4eebcd519257fcba5ad4",
              "method": "Independent set intersections and explicit P margins; Python standard library",
              "reports": reports}
    destination = ROOT / "results/memetik/founder_audit_20260913.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=4, sort_keys=True) + "\n")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
