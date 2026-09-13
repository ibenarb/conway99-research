#!/usr/bin/env python3
"""Ryzen-only exact arithmetic and byte reproduction; never invokes a solver."""
from __future__ import annotations

import argparse
import ast
import concurrent.futures as cf
import hashlib
import importlib.util
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

VERSION = "1.0.0"
SOURCE_COMMIT = "0a54ce594f89b948c77200328f5de7379bae4806"
REPO = "ibenarb/conway99-research"
BRANCH = "research/algebra-memetic-20260912"
RUN = "k66_v4_cert_20260908_231256_132359"
SEVEN = ["v4_09316", "v4_09317", "v4_09322", "v4_09323", "v4_09331", "v4_09332", "v4_09333"]
STAR_ROOTS = ["v4_09232"] + SEVEN
EXPECTED_REMOVALS = dict(zip(STAR_ROOTS, [12, 28, 35, 10, 12, 24, 10, 6]))
SOURCE_FILES = {"star": "e88199345481ed6e.py", "deep": "689553cc7f9df62e.py",
                "r2": "ff29f19d0f5a564a.py"}
SOURCE_HASHES = {"star": "e616de8e49bd678ac9425afb7bf6f067507827780c8746bfe0e184058b129088",
                 "deep": "dad41b4b5114377cd2327774d2f6dcd1acc67090b8965faa08e641e149e78782",
                 "r2": "914ff612545d0a005a4a147af05db521d68dcd3dd3e0ba73261461f94ac5d24e"}
MANIFEST_SHA = "63cbc21e88e4d49b58da7401577593679caec77b9444fd3b236deba0ab679075"
INT_MAX = (1 << 63) - 1


def require(condition, label):
    if not condition:
        raise RuntimeError(label)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_sources(workspace):
    base = workspace / "k66_encoder_source_audit_v1/payload"
    modules = {}
    for name, filename in SOURCE_FILES.items():
        path = base / filename
        require(file_hash(path) == SOURCE_HASHES[name], "source hash: " + name)
        modules[name] = load_module(path, "k66_audit_" + name)
    return modules


def bounded(array, name, bounds):
    maximum = max((abs(int(x)) for x in array.flat), default=0)
    require(maximum <= INT_MAX, "int64 bound: " + name)
    bounds[name] = max(bounds.get(name, 0), maximum)
    return array


def mm(np, a, b, name, bounds):
    bounded(np.abs(a) @ np.abs(b), name + ":absolute_sum", bounds)
    return bounded(a @ b, name, bounds)


def exact_minor(np, matrix):
    n = len(matrix)
    schur = [[Fraction(int(x)) for x in row] for row in matrix]
    basis = []
    for k in range(n):
        pivot = schur[k][k]
        require(pivot >= 0, "negative exact PSD pivot")
        if not pivot:
            require(all(schur[k][j] == 0 for j in range(k, n)), "nonzero row at zero PSD pivot")
            continue
        basis.append(k)
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                schur[i][j] -= schur[i][k] * schur[k][j] / pivot
    r = len(basis)
    require(r > 0, "unexpected rank-zero production input")
    aug = [[Fraction(int(matrix[i, j])) for j in basis] +
           [Fraction(k == t) for t in range(r)] for k, i in enumerate(basis)]
    for k in range(r):
        pivot = aug[k][k]
        require(pivot != 0, "singular selected minor")
        aug[k] = [x / pivot for x in aug[k]]
        for i in range(r):
            if i != k:
                multiplier = aug[i][k]
                aug[i] = [a - multiplier * b for a, b in zip(aug[i], aug[k])]
    inverse = [row[r:] for row in aug]
    denominator = math.lcm(*(x.denominator for row in inverse for x in row))
    scaled = np.array([[int(x * denominator) for x in row] for row in inverse], dtype=object)
    require(np.array_equal(matrix[np.ix_(basis, basis)] @ scaled,
                           denominator * np.eye(r, dtype=object)), "independent inverse identity")
    require(np.array_equal(matrix[:, basis] @ scaled @ matrix[basis, :],
                           denominator * matrix), "rank and complete range identity")
    return basis, scaled, denominator


def universe(np):
    modes = []
    for support in itertools.combinations(range(4), 2):
        modes.append(tuple(int(k in support) for k in range(4)))
    modes += [tuple(2 * int(k == j) for k in range(4)) for j in range(4)]
    raw = [sum(parts, ()) for parts in itertools.product(modes, repeat=3)
           if sum(2 in part for part in parts) <= 2]
    require(len(raw) == 936 and len(set(raw)) == 936, "independent universe")
    cellspec = [(1, 1), (1, 0), (0, 1), (0, 0)]
    z = np.array([row + bits for bits in cellspec for row in raw], dtype=object)
    ell = np.array([sum(int(x) == 2 for x in row[:12]) for row in z], dtype=object)
    q = z[:, 12] + z[:, 13]
    cells = np.array([c for c in range(4) for _ in raw], dtype=int)
    coords = [(i, j) for i in range(14) for j in range(i, 14)]
    products = np.array([[row[i] * row[j] for i, j in coords] for row in z], dtype=object)
    target = np.array([[12 * (i == j) + 6 - 3 * (i < 12 and j < 12 and i // 4 == j // 4)
                        for j in range(14)] for i in range(14)], dtype=object)
    return z, ell, q, cells, coords, products, target


def exact_case(np, summary, job):
    z, ell, q, cells, coords, products, target = universe(np)
    bits = summary["attached_T_bits"]
    require(summary["s"] == 1 and len(bits) == 12 and all(len(row) == 2 and all(x in (0, 1) for x in row) for row in bits),
            "K66 T-skeleton shape")
    require(sum(row[0] for row in bits) == sum(row[1] for row in bits) == 6 and
            sum(row[0] * row[1] for row in bits) == 1, "K66 cell-size derivation")
    h = np.zeros((14, 14), dtype=object)
    for group in range(3):
        for i, j in [(0, 1), (2, 3)]:
            h[4 * group + i, 4 * group + j] = h[4 * group + j, 4 * group + i] = 1
    for i, bits in enumerate(summary["attached_T_bits"]):
        for t in range(2):
            h[i, 12 + t] = h[12 + t, i] = int(bits[t])
    h[12, 12] = h[13, 13] = 2
    h[12, 13] = h[13, 12] = int(summary["s"])
    for (a, b), perm in zip([(0, 1), (0, 2), (1, 2)], job["matching_permutations"]):
        require(sorted(perm) == list(range(4)), "invalid matching permutation")
        for i, j in enumerate(perm):
            h[4 * a + i, 4 * b + j] = h[4 * b + j, 4 * a + i] = 1
    bounds = {}
    gram = bounded(target - mm(np, h, h, "H_squared", bounds) - h, "G", bounds)
    basis, inverse, den = exact_minor(np, gram)
    bounded(inverse, "scaled_inverse", bounds)
    mm(np, gram[np.ix_(basis, basis)], inverse, "source_inverse_check", bounds)
    require(den <= INT_MAX, "inverse denominator")
    budget = np.array([gram[i, j] for i, j in coords], dtype=object)
    w = mm(np, z[:, basis], inverse, "W", bounds)
    leverage = bounded((bounded(w * z[:, basis], "lev_products", bounds)).sum(axis=1), "lev", bounds)
    bounded(np.abs(w * z[:, basis]).sum(axis=1), "lev_abs_sum", bounds)
    range_lhs = mm(np, w, gram[basis, :], "range_lhs", bounds)
    range_rhs = bounded(den * z, "range_rhs", bounds)
    m = -h - np.eye(14, dtype=object)
    m[:, :4] += 3
    mz = mm(np, z, m.T, "MZ", bounds)
    beta_products = bounded(w * mz[:, basis], "beta_products", bounds)
    bounded(np.abs(beta_products).sum(axis=1), "beta_abs_sum", bounds)
    beta = bounded(beta_products.sum(axis=1), "beta", bounds)
    slack = bounded(den - leverage, "slack", bounds)
    lower = bounded(-3 * slack, "beta_lower", bounds)
    upper = bounded(4 * slack, "beta_upper", bounds)
    gates = [("entry_budget", np.all(products <= budget, axis=1)),
             ("range", np.all(range_lhs == range_rhs, axis=1)),
             ("leverage", leverage <= den),
             ("B_diagonal", (beta >= lower) & (beta <= upper)),
             ("nonempty_cell", np.array([summary["cell_sizes"][int(c)] > 0 for c in cells]))]
    active = np.ones(len(z), dtype=bool)
    counts = []
    for label, condition in gates:
        active &= condition
        counts.append({"filter": label, "remaining": int(active.sum())})
    ids = np.flatnonzero(active)
    zz, ee, qq, cc = z[ids], ell[ids], q[ids], cells[ids]
    require(len(ids) > 0, "empty production profile domain")
    require(summary["cell_sizes"] == [0, 5, 5, 8], "audit scoped to K66 cells")
    require(not np.any(qq == 2), "dormant q=2 filter unexpectedly active")
    aa = mm(np, zz[:, basis], inverse, "A", bounds)
    delta = mm(np, aa, zz[:, basis].T, "delta", bounds)
    eta = mm(np, aa, mz[ids][:, basis].T, "eta", bounds)
    require(np.array_equal(eta, eta.T), "independent eta symmetry")
    dots = mm(np, zz, zz.T, "D", bounds)
    lv, bt = leverage[ids], beta[ids]
    allowed = np.zeros((len(ids), len(ids)), dtype=np.uint8)
    for b in range(3):
        first_base = bounded(b * den - eta, "first_base", bounds)
        first = bounded(first_base - bounded(4 * delta, "four_delta", bounds), "first", bounds)
        second_base = bounded(eta - b * den, "second_base", bounds)
        second = bounded(second_base - bounded(3 * delta, "three_delta", bounds), "second", bounds)
        r1 = bounded(bounded(4 * (den - lv), "four_slack", bounds) - bt, "r1", bounds)
        r2 = bounded(bounded(3 * (den - lv), "three_slack", bounds) + bt, "r2", bounds)
        require(np.all(r1 >= 0) and np.all(r2 >= 0), "negative PSD diagonal")
        require(max(abs(int(x)) for a in (first, second, r1, r2) for x in a.flat) <= 3037000499,
                "historical square guard")
        f2 = bounded(first * first, "first_square", bounds)
        s2 = bounded(second * second, "second_square", bounds)
        rr1 = bounded(r1[:, None] * r1[None, :], "r1_product", bounds)
        rr2 = bounded(r2[:, None] * r2[None, :], "r2_product", bounds)
        ok = (dots + b <= 6) & (f2 <= rr1) & (s2 <= rr2)
        if b == 2:
            ok &= (ee[:, None] <= 1) & (ee[None, :] <= 1)
        allowed[ok] |= 1 << b
    caps = np.array([1 if int(e) + int(t) else 2 for e, t in zip(ee, qq)], dtype=int)
    caps[np.diag(allowed) == 0] = 1
    d = dict(H=h, ids=ids, z=zz, ell=ee, q=qq, cap=caps, cell=cc, budget=budget,
             products=products[ids], allowed=allowed, cell_sizes=np.array(summary["cell_sizes"]))
    common = (np.array(z, dtype=np.int64), np.array(ell, dtype=np.int64), np.array(q, dtype=np.int64),
              np.where(ell + q > 0, 1, 2).astype(np.int64), cells, np.array(products, dtype=np.int64),
              coords, np.array(target, dtype=np.int64))
    return d, common, {"rank": len(basis), "basis": basis, "denominator": den,
                      "filter_counts": counts, "int64_absolute_bounds": bounds,
                      "special_q2_filter": "VACUOUS_IN_K66", "status": "EXACT_INTEGER_REFERENCE_PASS"}


def guard_encoder(module):
    cls = module.CNF
    original = cls.weighted_eq
    def checked(self, items, target):
        require(isinstance(target, int) and not isinstance(target, bool), "noninteger target")
        for variable, weight in items:
            require(isinstance(weight, int) and weight >= 0, "unsupported weight")
            require(isinstance(variable, bool) or (isinstance(variable, int) and 0 < variable <= self.n),
                    "unsupported literal in BDD")
        return original(self, items, target)
    cls.weighted_eq = checked


def unit_consistent(clauses, assignment):
    values = dict(assignment)
    while True:
        changed = False
        for clause in clauses:
            if any(abs(lit) in values and values[abs(lit)] == (lit > 0) for lit in clause):
                continue
            unset = [lit for lit in clause if abs(lit) not in values]
            if not unset:
                return False
            if len(unset) == 1:
                lit = unset[0]
                values[abs(lit)] = lit > 0
                changed = True
        if not changed:
            return True


def bdd_controls(modules):
    checks = 0
    for module in modules.values():
        for weights in [(0, 0, 0), (1, 1, 1), (1, 2, 4), (2, 0, 3)]:
            for target in range(-1, sum(weights) + 4):
                c = module.CNF()
                xs = [c.var() for _ in weights]
                items = list(zip(xs, weights)) + [(xs[0], 1), (True, 1), (False, 2)]
                c.weighted_eq(items, target)
                for bits in itertools.product((False, True), repeat=3):
                    actual = unit_consistent(c.cl, dict(zip(xs, bits)))
                    expected = sum(w * int(v) for w, v in zip(weights, bits)) + int(bits[0]) + 1 == target
                    require(actual == expected, "BDD projection control")
                    checks += 1
        for target in [-1, 0, 1]:
            c = module.CNF()
            c.weighted_eq([], target)
            require(unit_consistent(c.cl, {}) == (target == 0), "empty weighted equation")
            checks += 1
        if hasattr(module.CNF, "cardinality_leq"):
            for limit in range(-1, 5):
                c = module.CNF()
                xs = [c.var() for _ in range(3)]
                c.cardinality_leq(xs + [False], limit)
                for bits in itertools.product((False, True), repeat=3):
                    require(unit_consistent(c.cl, dict(zip(xs, bits))) == (sum(bits) <= limit), "capacity control")
                    checks += 1
    return {"status": "PASS", "finite_projection_checks": checks,
            "scope": "Small exhaustive controls supplement the generic BDD induction proof."}


def write_compare(cnf, new, old, expected=None):
    new.parent.mkdir(parents=True, exist_ok=True)
    temp = new.with_suffix(".cnf.tmp")
    h = hashlib.sha256()
    old_hash = hashlib.sha256()
    identical = True
    with temp.open("wb") as out, old.open("rb") as source:
        header = f"p cnf {cnf.n} {len(cnf.cl)}\n".encode("ascii")
        out.write(header)
        h.update(header)
        block = source.read(len(header))
        old_hash.update(block)
        identical &= block == header
        buffer = bytearray()
        for clause in cnf.cl:
            require(all(type(v) is int and 0 < abs(v) <= cnf.n for v in clause), "DIMACS literal bounds")
            buffer.extend((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
            if len(buffer) >= 1 << 20:
                out.write(buffer)
                h.update(buffer)
                block = source.read(len(buffer))
                old_hash.update(block)
                identical &= block == buffer
                buffer.clear()
        if buffer:
            out.write(buffer)
            h.update(buffer)
            block = source.read(len(buffer))
            old_hash.update(block)
            identical &= block == buffer
        for block in iter(lambda: source.read(1 << 20), b""):
            identical = False
            old_hash.update(block)
    temp.replace(new)
    result = {"new": str(new), "original": str(old), "bytes": new.stat().st_size,
              "sha256": h.hexdigest(), "original_sha256": old_hash.hexdigest(),
              "variables": cnf.n, "clauses": len(cnf.cl), "byte_identical": bool(identical),
              "certificate_input_sha256": expected}
    save(new.with_suffix(".comparison.json"), result)
    require(identical, "CNF bytes differ; both inputs retained: " + str(new))
    require(expected is None or h.hexdigest() == expected, "certificate input hash: " + str(old))
    return result


def run_case(task):
    import numpy as np
    cid, workspace_string, output_string, identity, star_hashes, root_hashes = task
    workspace, output = Path(workspace_string), Path(output_string)
    case_dir = output / "cases" / cid
    result_path = case_dir / "result.json"
    if result_path.exists():
        prior = json.loads(result_path.read_text())
        if prior.get("identity") == identity and prior.get("status") == "PASS":
            require(all(file_hash(Path(r["new"])) == r["sha256"] and
                        file_hash(Path(r["original"])) == r["original_sha256"] for r in prior["cnfs"]),
                    "changed CNF in resume checkpoint")
            return prior
    started = time.monotonic()
    run = workspace / "o3_reconciliation_runs" / RUN
    manifest = json.loads((run / "manifest.json").read_text())
    job = next(j for j in manifest["jobs"] if j["id"] == cid)
    modules = load_sources(workspace)
    for module in modules.values():
        guard_encoder(module)
    g, deep, r2 = modules["star"], modules["deep"], modules["r2"]
    exact, common, arithmetic = exact_case(np, manifest["case_summary"], job)
    raw, raw_ell = g.make_profiles(np)
    source_z = np.concatenate([np.column_stack((raw, np.tile(bits, (936, 1))))
                               for bits in [(1, 1), (1, 0), (0, 1), (0, 0)]])
    source_ell = np.tile(raw_ell, 4)
    source_q = source_z[:, 12:].sum(axis=1)
    source_cells = np.repeat(np.arange(4), 936)
    source_coords = list(zip(*np.triu_indices(14)))
    source_products = np.array([source_z[:, i] * source_z[:, j] for i, j in source_coords]).T
    source_target = 12 * np.eye(14, dtype=np.int64) + 6 * np.ones((14, 14), dtype=np.int64)
    for group in range(3):
        source_target[4 * group:4 * group + 4, 4 * group:4 * group + 4] -= 3
    source_common = (source_z, source_ell, source_q, np.where(source_ell + source_q > 0, 1, 2),
                     source_cells, source_products, source_coords, source_target)
    require(all(np.array_equal(a, b) for a, b in zip(common, source_common)), "source universe/input construction")
    common = source_common
    original = g.prepare_case(np, manifest["case_summary"], job, common)
    for key in exact:
        require(np.array_equal(exact[key], original[key]), "reference/source disagreement: " + cid + ":" + key)
    other = r2.prepare(np, manifest["case_summary"], job, common)
    for key in other:
        reference_key = "products" if key == "prods" else key
        require(np.array_equal(other[key], exact[reference_key]), "R2 domain disagreement: " + key)
    d = original
    active = set(range(len(d["ids"])))
    records, rounds = [], []
    mappings = {int(gid): i for i, gid in enumerate(d["ids"])}
    domain = [{"id": int(gid), "local_index": i, "z": list(map(int, d["z"][i])),
               "ell": int(d["ell"][i]), "q": int(d["q"][i]), "cap": int(d["cap"][i]),
               "cell": int(d["cell"][i])} for i, gid in enumerate(d["ids"])]
    save(case_dir / "domain.json", {"profiles": domain, "arithmetic": arithmetic})
    if cid in STAR_ROOTS:
        require(len(active) == g.EXPECTED_PROFILES[cid], "initial profile count")
        g.CASE_DATA[cid] = d
        preflight = run / "neighbor_star_preflight_20260909"
        prior_removed = []
        for round_no in [1, 2, 3]:
            before = sorted(int(d["ids"][i]) for i in active)
            g.ACTIVE[cid] = set(active)
            paths = sorted((preflight / f"star_round_{round_no}" / cid).glob("profile_*.cnf"))
            removed = []
            for path in paths:
                parts = path.stem.split("_")
                require(len(parts) == 2 and parts[1].isdigit(), "unexpected temporary profile filename")
                gid = int(parts[1])
                require(gid in mappings and mappings[gid] in active, "inactive removal target")
                idx = mappings[gid]
                expected = star_hashes.get(f"star_round_{round_no}/{cid}/{path.name}")
                require(cid not in SEVEN or expected is not None, "missing restart certificate input link")
                cnf = g.build_star_cnf(np, cid, idx)
                item = write_compare(cnf, case_dir / f"star_round_{round_no}" / path.name, path, expected)
                item.update(kind="STAR", round=round_no, global_profile_id=gid,
                            depends_on_earlier_removed=list(prior_removed))
                records.append(item)
                removed.append(idx)
            active.difference_update(removed)
            removed_ids = sorted(int(d["ids"][i]) for i in removed)
            after = sorted(int(d["ids"][i]) for i in active)
            summary = json.loads((preflight / f"star_round_{round_no}_summary.json").read_text())[cid]
            require(summary["removed_this_round"] == len(removed) and summary["active_profiles"] == len(active),
                    "round summary mismatch")
            rounds.append(dict(round=round_no, before=before, removed=removed_ids, after=after,
                               semantics="SIMULTANEOUS", depends_on_earlier_removed=list(prior_removed)))
            prior_removed += removed_ids
        require(len(prior_removed) == EXPECTED_REMOVALS[cid], "total removals")
        require(rounds[1]["removed"] == ([3520] if cid == "v4_09317" else []), "round two membership")
        require(rounds[2]["removed"] == [], "unexpected round three removal")
        if cid in SEVEN:
            dd = deep.prepare_case(np, manifest["case_summary"], job, common)
            require(all(np.array_equal(d[k], dd[k]) for k in d), "Deep7 domain mismatch")
            require(deep.prior_removed_indices(dd, preflight, cid) == set(mappings[i] for i in prior_removed),
                    "Deep7 prior-import mismatch")
            deep_dir = run / "neighbor_star_deep7_autonomous_20260909"
            history = json.loads((deep_dir / "star_history.json").read_text())
            require(len(history) == 1 and all(history[0][phase]["unsat"] == 0 for phase in ["quick", "deep"]),
                    "unaccounted Deep7 removals")
            require(history[0]["active_counts"][cid] == len(active), "Deep7 active count")
            require(not list(deep_dir.glob("round_*_*/" + cid + "/*.cnf")), "unexpected retained Deep7 CNF")
            deep.CASE_DATA[cid], deep.ACTIVE[cid] = dd, set(active)
            cnf, _, _, _ = deep.encode_global(np, dd, active)
            records.append(dict(write_compare(cnf, case_dir / "deep7_global.cnf",
                                deep_dir / "global" / cid / "model.cnf", root_hashes[cid]), kind="DEEP7_GLOBAL"))
        cnf, _, _, _ = g.encode_global(np, d, active)
        expected = root_hashes.get(cid)
        if cid == "v4_09232":
            summ = json.loads((preflight / "summary.json").read_text())
            expected = next(x["cnf_sha256"] for x in summ["global_results"] if x["id"] == cid)
        records.append(dict(write_compare(cnf, case_dir / "preflight_global.cnf",
                            preflight / "global_rescout" / cid / "model.cnf", expected), kind="PREFLIGHT_GLOBAL"))
    else:
        cert = json.loads((run / "profile_conflict_cnf_scout_20260909_r2/cert15_manifest.json").read_text())
        expected = next(x["cnf_sha256"] for x in cert["records"] if x["id"] == cid)
        cnf, _ = r2.encode(np, other)
        records.append(dict(write_compare(cnf, case_dir / "r2_global.cnf",
                            run / "profile_conflict_cnf_scout_20260909_r2" / cid / "model.cnf", expected), kind="R2_GLOBAL"))
    result = dict(status="PASS", identity=identity, case=cid, initial_profiles=len(d["ids"]),
                  final_profiles=len(active), arithmetic=arithmetic, rounds=rounds, cnfs=records,
                  wall_seconds=round(time.monotonic() - started, 3), production_proofs_replayed=0)
    save(result_path, result)
    return result


def publish(output, workspace):
    relative = "results/k66_encoder_audit_20260913/reproduction"
    state_path = output / "publish_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    worktree = output / "git_worktree"
    def command(args, cwd=None):
        return subprocess.check_output(args, cwd=cwd, stderr=subprocess.PIPE, timeout=300)
    if "commit" not in state:
        backup = workspace / "k66_restart_git_backup"
        origin = command(["git", "remote", "get-url", "origin"], backup).decode().strip()
        require(origin.rstrip("/").removesuffix(".git") in ("https://github.com/" + REPO, "git@github.com:" + REPO),
                "unexpected backup origin")
        if not worktree.exists():
            command(["git", "fetch", "origin", BRANCH], backup)
            command(["git", "merge-base", "--is-ancestor", SOURCE_COMMIT, "FETCH_HEAD"], backup)
            command(["git", "worktree", "add", "--detach", str(worktree), "FETCH_HEAD"], backup)
        destination = worktree / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted((output / "publish").iterdir()):
            require(path.suffix == ".json" and path.stat().st_size < 1024 * 1024, "compact publication only")
            target = destination / path.name
            require(not target.exists() or target.read_bytes() == path.read_bytes(), "different prior published result")
            shutil.copyfile(path, target)
        command(["git", "add", "--", relative], worktree)
        staged = command(["git", "diff", "--cached", "--name-only"], worktree).decode().splitlines()
        require(all(p.startswith(relative + "/") for p in staged), "unexpected staged path")
        if staged:
            command(["git", "commit", "-m", "Record exact K66 encoder and CNF reproduction results"], worktree)
        state = {"commit": command(["git", "rev-parse", "HEAD"], worktree).decode().strip(), "path": relative}
        save(state_path, state)
    command(["git", "push", "origin", state["commit"] + ":refs/heads/" + BRANCH], worktree)
    tree_sha = command(["git", "rev-parse", state["commit"] + ":" + relative], worktree).decode().strip()
    entries = json.loads(command(["gh", "api", "repos/" + REPO + "/git/trees/" + tree_sha]))["tree"]
    remote = {x["path"]: x for x in entries}
    receipts = []
    for path in sorted((output / "publish").iterdir()):
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(remote[path.name]["sha"] == blob and remote[path.name]["size"] == len(data), "remote blob mismatch")
        downloaded = command(["gh", "api", "repos/" + REPO + "/contents/" + relative + "/" + path.name +
                              "?ref=" + state["commit"], "-H", "Accept: application/vnd.github.raw+json"])
        require(downloaded == data and digest(downloaded) == digest(data), "full result return-download mismatch")
        receipts.append(dict(file=path.name, bytes=len(data), sha256=digest(data), git_blob_sha1=blob))
        save(output / "GIT_REPRODUCTION_RECEIPT.json", dict(state, status="VERIFYING", files=receipts))
    save(output / "GIT_REPRODUCTION_RECEIPT.json", dict(state, status="VERIFIED", files=receipts))
    print("GIT_REPRODUCTION_BACKUP_VERIFIED", json.dumps(state), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "conway99_workspace")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    workspace = args.workspace
    output = workspace / "k66_encoder_reproduction_v1"
    output.mkdir(parents=True, exist_ok=True)
    import fcntl
    lock = (output / "audit.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    modules = load_sources(workspace)
    controls = bdd_controls(modules)
    save(output / "controls.json", controls)
    print("ENCODER_CONTROLS", json.dumps(controls), flush=True)
    if args.controls_only:
        return
    run = workspace / "o3_reconciliation_runs" / RUN
    require(file_hash(run / "manifest.json") == MANIFEST_SHA, "manifest identity")
    manifest = json.loads((run / "manifest.json").read_text())
    require(manifest["case_id"] == "k66_s1_t225" and len(manifest["jobs"]) == 23, "case scope")
    require(len({j["id"] for j in manifest["jobs"]}) == 23, "unique residual IDs")
    inventory_path = workspace / "k66_restart_audit_v1/inventory.json"
    inventory = json.loads(inventory_path.read_text())
    star_entries = [x for x in inventory if "star125" in x["archive"] and x["path"].endswith(".cnf")]
    star_hashes = {x["path"]: x["sha256"] for x in star_entries}
    require(len(star_entries) == len(star_hashes) == 125, "125 restart Star-CNF links")
    main_manifest = workspace / "o3_reconciliation_runs/k66_deep7_coarsecert_20260910_130841/manifest.json"
    old_entries = [x for x in inventory if "deep7_coarsecert" in x["archive"] and x["path"] == "manifest.json"]
    require(len(old_entries) == 1 and file_hash(main_manifest) == old_entries[0]["sha256"], "main manifest restart link")
    root_hashes = json.loads(main_manifest.read_text())["root_hashes"]
    require(set(root_hashes) == set(SEVEN), "certified root set")
    source_index = json.loads((workspace / "k66_encoder_source_audit_v1/payload/SOURCE_INDEX.json").read_text())
    metadata_hashes = {}
    for record in source_index["files"].values():
        if record["category"] == "run_metadata":
            path = Path(record["origin"])
            require(file_hash(path) == record["sha256"], "run metadata changed: " + str(path))
            metadata_hashes[str(path)] = record["sha256"]
    identity_data = dict(version=VERSION, script_sha256=file_hash(Path(__file__)), manifest_sha256=MANIFEST_SHA,
                         sources=SOURCE_HASHES, restart_inventory_sha256=file_hash(inventory_path),
                         metadata_sha256=metadata_hashes, root_hashes=root_hashes)
    identity = digest(json.dumps(identity_data, sort_keys=True).encode())
    save(output / "identity.json", identity_data)
    tasks = [(j["id"], str(workspace), str(output), identity, star_hashes, root_hashes)
             for j in manifest["jobs"]]
    results, errors = [], []
    started = last = time.monotonic()
    with cf.ProcessPoolExecutor(max_workers=max(1, min(args.workers, 8))) as pool:
        futures = {pool.submit(run_case, task): task[0] for task in tasks}
        while futures:
            done, _ = cf.wait(futures, timeout=1, return_when=cf.FIRST_COMPLETED)
            for future in done:
                cid = futures.pop(future)
                try:
                    result = future.result()
                    results.append(result)
                    print("CASE_PASS", cid, "CNFs=" + str(len(result["cnfs"])), flush=True)
                except Exception as error:
                    failure = dict(case=cid, status="FAIL", error=repr(error))
                    errors.append(failure)
                    save(output / "cases" / cid / "failure.json", failure)
                    print("CASE_FAIL", json.dumps(failure), flush=True)
            now = time.monotonic()
            if now - last >= 600:
                completed = len(results) + len(errors)
                eta = (now - started) * len(futures) / completed if completed else None
                print("STATUS", json.dumps(dict(done=completed, total=23, elapsed_seconds=round(now - started),
                      ETA_seconds=round(eta) if eta is not None else None,
                      ETA_basis="completed-case average; differing case sizes")), flush=True)
                last = now
    results.sort(key=lambda r: r["case"])
    cnfs = [c for r in results for c in r["cnfs"]]
    seven_stars = [c for r in results if r["case"] in SEVEN for c in r["cnfs"] if c["kind"] == "STAR"]
    counts = {kind: sum(c["kind"] == kind for c in cnfs) for kind in ["STAR", "DEEP7_GLOBAL", "PREFLIGHT_GLOBAL", "R2_GLOBAL"]}
    status = "PASS" if not errors and len(results) == 23 and len(seven_stars) == 125 and counts == {
        "STAR": 137, "DEEP7_GLOBAL": 7, "PREFLIGHT_GLOBAL": 8, "R2_GLOBAL": 15} else "FAIL"
    summary = dict(status=status, version=VERSION, identity=identity, case_count=len(results), counts=counts,
                   seven_root_stars=len(seven_stars), errors=errors, production_proofs_replayed=0,
                   seconds=round(time.monotonic() - started), controls=controls,
                   scope="Encoder/input reproduction only; no new UNSAT proof, orbit coverage or 223 exclusions audit.")
    save(output / "publish/summary.json", summary)
    save(output / "publish/identity.json", identity_data)
    for result in results:
        compact = dict(result)
        compact["rounds"] = [{k: v for k, v in r.items() if k not in ("before", "after")}
                             for r in result["rounds"]]
        for c in compact["cnfs"]:
            c.pop("depends_on_earlier_removed", None)
        save(output / "publish" / (result["case"] + ".json"), compact)
    print("K66_REPRODUCTION_RESULT", json.dumps(summary), flush=True)
    if args.publish:
        publish(output, workspace)
    require(status == "PASS", "one or more audit obligations failed; inspect saved results")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("K66_REPRODUCTION_FAILED", type(error).__name__, str(error), file=sys.stderr, flush=True)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        raise SystemExit(1)
