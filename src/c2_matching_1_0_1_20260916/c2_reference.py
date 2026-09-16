"""Deterministic complete C2 CNF encoder, standard-library only, version 1.0.0."""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path
import shutil
import tempfile
import time

VERSION = "1.0.0"
SPEC_COMMIT = "31c563f6ba460227c6ae4eebcd519257fcba5ad4"


def negate(literal):
    return not literal if isinstance(literal, bool) else -literal


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


class CNF:
    def __init__(self, retain=False):
        self.variables = 0
        self.clauses = 0
        self.body = tempfile.TemporaryFile(mode="w+b")
        self.saved = [] if retain else None
        self.products = {}
        self.equalities = set()

    def variable(self):
        self.variables += 1
        return self.variables

    def clause(self, *literals):
        result = []
        seen = set()
        for literal in literals:
            if literal is True:
                return
            if literal is False:
                continue
            if not isinstance(literal, int) or literal == 0 or abs(literal) > self.variables:
                raise ValueError("Invalid literal")
            if -literal in seen:
                return
            if literal not in seen:
                seen.add(literal)
                result.append(literal)
        self.clauses += 1
        self.body.write((" ".join(map(str, result)) + (" " if result else "") + "0\n").encode())
        if self.saved is not None:
            self.saved.append(tuple(result))

    def conjunction(self, a, b):
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        if a == b:
            return a
        if a == -b:
            return False
        key = tuple(sorted((a, b)))
        if key not in self.products:
            y = self.variable()
            self.clause(-y, a)
            self.clause(-y, b)
            self.clause(y, -a, -b)
            self.products[key] = y
        return self.products[key]

    def select(self, x, high, low):
        if type(high) is type(low) and high == low:
            return high
        if high is True and low is False:
            return x
        if high is False and low is True:
            return -x
        y = self.variable()
        self.clause(-y, -x, high)
        self.clause(-y, x, low)
        self.clause(y, -x, negate(high))
        self.clause(y, x, negate(low))
        return y

    def exact(self, terms, target):
        weights = Counter()
        for term in terms:
            if term is True:
                target -= 1
            elif term is not False:
                if not isinstance(term, int) or term <= 0 or term > self.variables:
                    raise ValueError("Exact sums require positive variables or bool constants")
                weights[term] += 1
        divisor = 0
        for weight in weights.values():
            divisor = gcd(divisor, weight)
        if divisor > 1:
            if target % divisor:
                self.clause(False)
                return
            weights = Counter({v: w // divisor for v, w in weights.items()})
            target //= divisor
        items = tuple(sorted(weights.items()))
        key = (items, target)
        if key in self.equalities:
            return
        self.equalities.add(key)
        remaining = [0] * (len(items) + 1)
        for i in range(len(items) - 1, -1, -1):
            remaining[i] = remaining[i + 1] + items[i][1]

        @lru_cache(maxsize=None)
        def node(i, total):
            if total < 0 or total > remaining[i]:
                return False
            if i == len(items):
                return total == 0
            x, weight = items[i]
            high = node(i + 1, total - weight)
            low = node(i + 1, total)
            return self.select(x, high, low)

        self.clause(node(0, target))

    def write(self, path):
        self.body.flush()
        end = self.body.tell()
        self.body.seek(0)
        with Path(path).open("wb") as output:
            output.write(f"p cnf {self.variables} {self.clauses}\n".encode())
            shutil.copyfileobj(self.body, output)
        self.body.seek(end)
        return {"variables": self.variables, "clauses": self.clauses,
                "bytes": Path(path).stat().st_size, "sha256": sha256(path)}

    def close(self):
        self.body.close()


class Frame:
    def __init__(self, k):
        if k not in (4, 14):
            raise ValueError("Only k=4 control and k=14 target are supported")
        self.k = k
        labels = list(itertools.combinations(range(k), 2))
        labels = [p for p in labels if p[1] != (p[0] ^ 1)]
        self.reps = [p for p in labels if p < self.partner(p)]
        self.labels = self.reps + [self.partner(p) for p in self.reps]
        self.pairs = len(self.reps)
        self.variables = {}
        self.map = []

    @staticmethod
    def partner(label):
        return tuple(sorted(x ^ 1 for x in label))

    def allocate(self, cnf):
        if cnf.variables or self.variables:
            raise ValueError("Frame primaries must be allocated first, once")
        for block in ("B", "C"):
            for i, j in itertools.combinations(range(self.pairs), 2):
                v = cnf.variable()
                self.variables[(block, i, j)] = v
                self.map.append([v, block, i, j])

    def edge(self, x, y):
        i, j = sorted((x % self.pairs, y % self.pairs))
        if i == j:
            return False
        block = "B" if x // self.pairs == y // self.pairs else "C"
        return self.variables[(block, i, j)]

    def mapping(self):
        return {"version": VERSION, "k": self.k, "labels": self.labels,
                "pair_count": self.pairs, "primary_count": len(self.map),
                "primary_columns": ["variable", "block", "i", "j"],
                "primary_variables": self.map,
                "fixed_zero": "M[x,x]=M[x,t(x)]=0; first half contains pair representatives"}


def encode_base(cnf, frame, progress=None):
    k = frame.k
    labels = frame.labels
    n = len(labels)
    phases = []
    for phase in ("E1_DEGREES", "E2_MIXED", "E3_COMMON_NEIGHBORS"):
        before = cnf.variables, cnf.clauses
        for x in range(n):
            if phase == "E1_DEGREES":
                cnf.exact([frame.edge(x, z) for z in range(n)], k - 2)
            elif phase == "E2_MIXED":
                for a in range(k):
                    cnf.exact([frame.edge(x, z) for z in range(n) if a in labels[z]],
                              2 - int(a in labels[x]) - int((a ^ 1) in labels[x]))
            else:
                for y in range(x + 1, n):
                    terms = [cnf.conjunction(frame.edge(x, z), frame.edge(z, y)) for z in range(n)]
                    terms.append(frame.edge(x, y))
                    cnf.exact(terms, 2 - len(set(labels[x]) & set(labels[y])))
            if progress:
                progress(phase, x + 1, n)
        phases.append({"phase": phase, "added_variables": cnf.variables - before[0],
                       "added_clauses": cnf.clauses - before[1]})
    return phases


def add_matching(cnf, frame):
    for i in range(frame.pairs):
        doubles = []
        for j in range(frame.pairs):
            if i != j:
                a, b = sorted((i, j))
                doubles.append(cnf.conjunction(frame.variables[("B", a, b)],
                                               frame.variables[("C", a, b)]))
        cnf.exact(doubles, 1)


def read_primary_model(path, count):
    values = {}
    for line in Path(path).read_text().splitlines():
        if not line.startswith("v "):
            continue
        for token in line[2:].split():
            literal = int(token)
            if literal == 0 or abs(literal) > count:
                continue
            var, value = abs(literal), literal > 0
            if var in values and values[var] != value:
                raise ValueError("Contradictory model assignment")
            values[var] = value
    if set(values) != set(range(1, count + 1)):
        raise ValueError("Incomplete primary assignment; no missing bits are guessed")
    return values


def reconstruct(frame, values):
    k, n = frame.k, len(frame.labels)
    size = 1 + k + n
    a = [[0] * size for _ in range(size)]
    for i in range(k):
        a[0][1+i] = a[1+i][0] = 1
        a[1+i][1+(i ^ 1)] = 1
    for x, label in enumerate(frame.labels):
        for i in label:
            a[1+k+x][1+i] = a[1+i][1+k+x] = 1
        for y in range(n):
            variable = frame.edge(x, y)
            a[1+k+x][1+k+y] = int(values[variable]) if variable is not False else 0
    return a


def verify_graph(a, k):
    size = 1 + k + k * (k - 2) // 2
    if len(a) != size or any(len(row) != size for row in a):
        return False
    if any(a[i][i] != 0 or sum(a[i]) != k for i in range(size)):
        return False
    if any(a[i][j] not in (0, 1) or a[i][j] != a[j][i] for i in range(size) for j in range(size)):
        return False
    for i in range(size):
        for j in range(i + 1, size):
            common = sum(a[i][z] * a[j][z] for z in range(size))
            if common != (1 if a[i][j] else 2):
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, choices=(4, 14), default=14)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", type=Path, help="Validate SAT output instead of generating CNFs")
    args = parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        parser.error("Output directory must be new or empty")
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    cnf, frame = CNF(), Frame(args.k)
    frame.allocate(cnf)
    try:
        write_json(args.out / "variables.json", frame.mapping())
        if args.model:
            values = read_primary_model(args.model, len(frame.map))
            a = reconstruct(frame, values)
            if not verify_graph(a, args.k):
                raise ValueError("SAT model fails independent graph check")
            write_json(args.out / "graph.json", a)
            write_json(args.out / "graph_check.json", {"status": "GRAPH_VERIFIED", "k": args.k,
                                                       "input_sha256": sha256(args.model)})
            print("GRAPH_VERIFIED", flush=True)
            return
        last = [0.0]

        def progress(phase, done, total):
            now = time.monotonic()
            if done == total or now - last[0] >= 600:
                print("STATUS " + json.dumps({"phase": phase, "done": done, "total": total,
                      "elapsed_seconds": round(now - started, 2),
                      "ETA": "unknown; generation only"}), flush=True)
                last[0] = now

        phases = encode_base(cnf, frame, progress)
        base = cnf.write(args.out / "baseline.cnf")
        add_matching(cnf, frame)
        matching = cnf.write(args.out / "matching.cnf")
        result = {"status": "GENERATED_NOT_SOLVED", "version": VERSION, "k": args.k,
                  "spec_commit": SPEC_COMMIT, "primary_variables": len(frame.map),
                  "source_sha256": sha256(__file__), "phases": phases,
                  "baseline": base, "matching": matching,
                  "variables_sha256": sha256(args.out / "variables.json"),
                  "matching_extension": "baseline clause body is an exact prefix; same primary numbering",
                  "matching_identical": base["sha256"] == matching["sha256"],
                  "symmetry_breaking": "none beyond the proved fixed frame and prescribed involution"}
        write_json(args.out / "manifest.json", result)
        print("C2_REFERENCE_RESULT " + json.dumps(result), flush=True)
    finally:
        cnf.close()


if __name__ == "__main__":
    main()
