"""Independent result verifier. Python standard library only.

No imports from the search kernel, no bitset popcount scorer, no solver or
canonicalizer. Neighbor sets and their intersections are reconstructed from
raw graph6 bytes. A search result is a solution only if every pair passes.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys


def read_adjacency(text):
    raw = text.strip()
    if raw.startswith(">>graph6<<"):
        raw = raw[10:]
    data = [ord(char) - 63 for char in raw]
    if not data or any(value < 0 or value > 63 for value in data):
        raise ValueError("Malformed graph6 alphabet")
    if data[0] == 63:
        if len(data) < 4 or data[1] == 63:
            raise ValueError("Unsupported graph6 header")
        size = data[1] * 4096 + data[2] * 64 + data[3]
        header = 4
    else:
        size = data[0]
        header = 1
    expected_bits = size * (size - 1) // 2
    if len(data) - header != (expected_bits + 5) // 6:
        raise ValueError("Incorrect graph6 byte count")
    bits = []
    for value in data[header:]:
        bits.extend(int(bool(value & (2 ** shift))) for shift in range(5, -1, -1))
    if any(bits[expected_bits:]):
        raise ValueError("Nonzero padding bits")
    adjacent = [set() for _ in range(size)]
    position = 0
    for right in range(size):
        for left in range(right):
            if bits[position]:
                adjacent[left].add(right)
                adjacent[right].add(left)
            position += 1
    return adjacent


def check_graph(text, arm=None, claimed=None, expected_n=99, expected_degree=14):
    neighbors = read_adjacency(text)
    n = len(neighbors)
    errors = []
    if n != expected_n:
        errors.append("ORDER")
    degrees = [len(row) for row in neighbors]
    if any(d != expected_degree for d in degrees):
        errors.append("DEGREE")
    if any(i in row for i, row in enumerate(neighbors)):
        errors.append("DIAGONAL")
    if any(i not in neighbors[j] for i, row in enumerate(neighbors) for j in row):
        errors.append("SYMMETRY")
    residuals = Counter()
    common_histogram = Counter()
    bad_edges = []
    bad_nonedges = []
    defect_degree = [0] * n
    square_sum = 0
    wrong = 0
    triangle_sum = 0
    four_sum = 0
    for first in range(n):
        for second in range(first + 1, n):
            count = len(neighbors[first].intersection(neighbors[second]))
            is_edge = second in neighbors[first]
            required = 1 if is_edge else 2
            residual = count - required
            residuals[residual] += 1
            common_histogram[(int(is_edge), count)] += 1
            square_sum += residual ** 2
            if residual != 0:
                wrong += 1
                defect_degree[first] += 1
                defect_degree[second] += 1
                (bad_edges if is_edge else bad_nonedges).append([first, second, count])
            if is_edge:
                triangle_sum += count
            four_sum += count * (count - 1) // 2
    if arm == "lambda" and bad_edges:
        errors.append("LAMBDA")
    if arm == "omega":
        if n != 99:
            errors.append("OMEGA_ORDER")
        else:
            pairs = []
            for a in range(14):
                for b in range(a + 1, 14):
                    if b != (a + 7) % 14:
                        pairs.append((a, b))
            if neighbors[0] != set(range(1, 15)):
                errors.append("OMEGA_ROOT")
            for label in range(14):
                expected = {0, 1 + (label + 7) % 14}
                expected.update(15 + i for i, pair in enumerate(pairs) if label in pair)
                if neighbors[1 + label] != expected:
                    errors.append("OMEGA_FRAME")
                    break
            for i, pair in enumerate(pairs):
                v = i + 15
                if neighbors[v].intersection(range(15)) != {pair[0] + 1, pair[1] + 1}:
                    errors.append("OMEGA_INCIDENCE")
                    break
                outer_neighbors = [u - 15 for u in neighbors[v] if u >= 15]
                if len(outer_neighbors) != 12:
                    errors.append("OMEGA_OUTER_DEGREE")
                    break
                for label in range(14):
                    count = sum(label in pairs[u] for u in outer_neighbors)
                    required = 2 - int(label in pair) - int((label + 7) % 14 in pair)
                    if count != required:
                        errors.append("OMEGA_P_MARGIN")
                        break
    elif arm not in (None, "lambda"):
        errors.append("UNKNOWN_ARM")
    if claimed:
        for field, actual in (("F", square_sum), ("W", wrong), ("lambda_bad", len(bad_edges))):
            if field in claimed and claimed[field] != actual:
                errors.append("CLAIM_" + field)
        if "defect_degrees" in claimed and claimed["defect_degrees"] != sorted(defect_degree):
            errors.append("CLAIM_DEFECT_DEGREES")
    hard_valid = not errors
    solution = hard_valid and square_sum == 0 and not bad_edges and not bad_nonedges
    return {"hard_valid": hard_valid, "is_solution": solution,
            "errors": sorted(set(errors)), "n": n, "degrees": sorted(set(degrees)),
            "edges": sum(degrees) // 2, "F": square_sum, "W": wrong,
            "lambda_bad": len(bad_edges), "mu_bad": len(bad_nonedges),
            "triangles": triangle_sum // 3, "C4": four_sum // 2,
            "residual_histogram": {str(k): v for k, v in sorted(residuals.items())},
            "defect_degrees": sorted(defect_degree),
            "first_bad_edges": bad_edges[:10], "first_bad_nonedges": bad_nonedges[:10],
            "verifier": "independent-neighbor-sets-v1"}


def candidate_objects(value):
    if isinstance(value, dict):
        if isinstance(value.get("g6"), str):
            yield value
        else:
            for item in value.values():
                yield from candidate_objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from candidate_objects(item)


def read_document(path):
    if path.name.endswith(".gz"):
        value = json.loads(gzip.decompress(path.read_bytes()))
    else:
        value = json.loads(path.read_text())
    if isinstance(value, dict) and "payload" in value and "sha256" in value:
        payload = json.dumps(value["payload"], sort_keys=True, separators=(",", ":")).encode()
        if hashlib.sha256(payload).hexdigest() != value["sha256"]:
            raise ValueError("Checkpoint digest mismatch")
        return value["payload"]
    return value


def verify_path(path, arm=None):
    path = Path(path)
    if path.suffix == ".g6":
        entries = [{"g6": line, "arm": arm} for line in path.read_text().splitlines() if line.strip()]
    elif path.suffix == ".jsonl":
        entries = []
        for line in path.read_text().splitlines():
            if line.strip():
                entries.extend(candidate_objects(json.loads(line)))
    else:
        entries = list(candidate_objects(read_document(path)))
    reports = []
    seen = set()
    for value in entries:
        key = (value["g6"], value.get("arm", arm))
        if key in seen:
            continue
        seen.add(key)
        report = check_graph(value["g6"], value.get("arm", arm), value)
        report["graph_sha256"] = hashlib.sha256(value["g6"].encode()).hexdigest()
        reports.append(report)
    if not reports:
        raise ValueError("No graph candidates found")
    return {"path": str(path), "graphs": len(reports),
            "all_hard_valid": all(r["hard_valid"] for r in reports),
            "solutions": sum(r["is_solution"] for r in reports), "reports": reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--arm", choices=("omega", "lambda"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = verify_path(args.path, args.arm)
    rendered = json.dumps(result, indent=4) + "\n"
    if args.output:
        Path(args.output).write_text(rendered)
    else:
        print(rendered, end="")
    if not result["all_hard_valid"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
