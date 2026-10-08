"""Independent N1 witness validation: standard library only, no encoder imports."""
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(x):
    return type(x) is int


def load(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def geometry(spec):
    m, anchor = spec["m"], spec["anchor"]
    require(integer(m) and m in (2, 7), "unsupported m")
    labels = [(i, j) for i in range(2*m) for j in range(i+1, 2*m) if j-i != m]
    n = len(labels)
    require(integer(anchor) and 0 <= anchor < n, "anchor")
    require(spec["kind"] in ("control", "root-class"), "kind")
    require(isinstance(spec["root_id"], (str, int)) and not isinstance(spec["root_id"], bool),
            "root identity")
    require(integer(spec["class_id"]) and spec["class_id"] >= 0, "class identity")
    rows = {}
    for key, neighbors in spec["rows"].items():
        require(str(int(key)) == key and 0 <= int(key) < n, "row index")
        u = int(key)
        require(isinstance(neighbors, list) and all(integer(v) and 0 <= v < n for v in neighbors),
                "row neighbors")
        require(len(neighbors) == len(set(neighbors)) == 2*m-2 and u not in neighbors,
                "row degree/duplicates/diagonal")
        rows[u] = set(neighbors)
    require(anchor in rows, "missing anchor row")
    ns = rows[anchor]
    special = {v for v in ns if set(labels[v]).intersection(labels[anchor])}
    require(len(special) == 2, "anchor special neighbors")
    pairs, endpoints = set(), []
    for pair in spec["matching"]:
        require(isinstance(pair, list) and len(pair) == 2, "matching pair")
        u, v = pair
        require(integer(u) and integer(v) and 0 <= u < v < n, "matching ordering")
        require((u, v) not in pairs, "duplicate matching pair")
        require(not set(labels[u]).intersection(labels[v]), "matching label overlap")
        pairs.add((u, v))
        endpoints += [u, v]
    require(len(endpoints) == len(set(endpoints)) and set(endpoints) == ns-special,
            "matching does not cover residual neighbors")
    fixed = {}
    def impose(u, v, bit):
        key = tuple(sorted((u, v)))
        require(key not in fixed or fixed[key] == bit, "conflicting fixed edge")
        fixed[key] = bit
    for u in range(n):
        impose(u, u, 0)
    for u, neighbors in rows.items():
        for v in range(n):
            impose(u, v, int(v in neighbors))
    for u in ns:
        for v in ns:
            if u < v:
                impose(u, v, int((u, v) in pairs))
    return labels, rows, fixed, pairs


def validate_binding(binding, cnf):
    require(binding["schema"] == "ROOT8105_N1_BINDING_1", "binding schema")
    require(binding["cnf_sha256"] == digest(cnf), "bound CNF changed")
    labels, rows, fixed, pairs = geometry(binding["spec"])
    n = len(labels)
    free = [(u, v) for u in range(n) for v in range(u+1, n) if (u, v) not in fixed]
    expected = [[u, v, i+1] for i, (u, v) in enumerate(free)]
    require(binding["edge_map"] == expected and all(
        all(integer(x) for x in row) for row in binding["edge_map"]), "noncanonical edge map")
    nv = binding["metadata"]["variables"]
    require(integer(nv) and nv >= len(free), "variable count")
    headers = []
    with Path(cnf).open() as stream:
        for line in stream:
            words = line.split()
            if words and words[0] == "p":
                headers.append(words)
    require(headers == [["p", "cnf", str(nv), str(binding["metadata"]["clauses"])]],
            "CNF header/binding mismatch")
    return labels, rows, fixed, pairs


def assignment(path, nv):
    result = {}
    tokens = Path(path).read_text().split()
    require(tokens and tokens[-1] == "0", "model terminator")
    for token in tokens[:-1]:
        lit = int(token)
        require(lit != 0 and 1 <= abs(lit) <= nv and abs(lit) not in result,
                "duplicate/missing/out-of-range model variable")
        result[abs(lit)] = int(lit > 0)
    require(len(result) == nv, "incomplete model")
    return result


def check_matrix(spec, matrix):
    labels, rows, fixed, pairs = geometry(spec)
    n, m = len(labels), spec["m"]
    require(isinstance(matrix, list) and len(matrix) == n and
            all(isinstance(row, list) and len(row) == n for row in matrix), "matrix shape")
    require(all(integer(bit) and bit in (0, 1) for row in matrix for bit in row), "matrix bit")
    for u in range(n):
        require(matrix[u][u] == 0, "diagonal")
        require(all(matrix[u][v] == matrix[v][u] for v in range(n)), "symmetry")
        require(sum(matrix[u]) == 2*m-2, "degree")
        if u in rows:
            require({v for v in range(n) if matrix[u][v]} == rows[u], "fixed row")
        special = set(labels[u]) | {(c+m) % (2*m) for c in labels[u]}
        for c in range(2*m):
            margin = sum(matrix[u][v] for v in range(n) if c in labels[v])
            require(margin == (1 if c in special else 2), "margin")
    for (u, v), bit in fixed.items():
        require(matrix[u][v] == bit, "fixed matching/edge")
    scope = rows[spec["anchor"]] | {spec["anchor"]}
    checked = 0
    for u in range(n):
        for v in range(u+1, n):
            if u in scope or v in scope:
                common = sum(matrix[u][w] * matrix[v][w] for w in range(n))
                rhs = 2 - matrix[u][v] - len(set(labels[u]).intersection(labels[v]))
                require(common == rhs, "N1 codegree")
                checked += 1
    return {"status": "DIRECT_N1_CHECK_PASS", "scope": sorted(scope),
            "pair_equations": checked, "unchecked_pairs": n*(n-1)//2-checked,
            "margin_equations": n*2*m, "SRG_claim": False,
            "root_exclusion": False, "catalog_identity_checked": False}


def decode_and_check(binding, cnf, model):
    labels, rows, fixed, pairs = validate_binding(binding, cnf)
    bits = assignment(model, binding["metadata"]["variables"])
    n = len(labels)
    matrix = [[0]*n for _ in range(n)]
    for (u, v), bit in fixed.items():
        matrix[u][v] = matrix[v][u] = bit
    for u, v, var in binding["edge_map"]:
        matrix[u][v] = matrix[v][u] = bits[var]
    return matrix, check_matrix(binding["spec"], matrix)
