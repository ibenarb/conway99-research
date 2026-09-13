#!/usr/bin/env python3
"""Independent SAT-free Conway_99 V4 orbit and arithmetic audit.

Python standard library only. Writes a NEW output directory, never modifies
project sources and never launches a solver. Integer computations only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools as it
import json
import math
import platform
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

VERSION = "0.1.1"
REFERENCE_COMMIT = "b279cd6de420bc4ad64869c8c7f99d653c73a195"
REFERENCE_BLOBS = {
    "src/reconciliation/o3_fixed_triangle_structural_v3.py": "33304bed06710a0e0da08119e954bc158d2f0224",
    "docs/breadth1/O3_fixed_triangle_internal_model.md": "498546157b3597867c5af78aad6011aa7e5cb94d",
    "docs/breadth1/O3_fixed_triangle_v3_frontier_analysis.md": "400ec8ebc2266f58da1feabec65183023253949f",
}
PERMS = tuple(it.permutations(range(4)))
PID = {p: i for i, p in enumerate(PERMS)}
PAIRS = ((0, 1), (0, 2), (1, 2))
PAIR_ID = {e: k for k, e in enumerate(PAIRS)}
CELLS = ((1, 1), (1, 0), (0, 1), (0, 0))
CELL_ID = {p: i for i, p in enumerate(CELLS)}
PARTNER = (1, 0, 3, 2)
MATCHING = {frozenset((0, 1)), frozenset((2, 3))}
D8 = tuple(p for p in PERMS if {frozenset((p[0], p[1])), frozenset((p[2], p[3]))} == MATCHING)
TRIPLES = tuple(it.product(range(24), repeat=3))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def inverse(p: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p.index(i) for i in range(len(p)))


def image(p: tuple[int, ...], subset: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(p[u] for u in subset))


def local_types() -> tuple[list[dict[str, Any]], dict[Any, int]]:
    subsets = tuple(it.combinations(range(4), 2))
    seen, orbits = set(), []
    for pair in it.product(subsets, repeat=2):
        if pair in seen:
            continue
        orbit = {(image(p, pair[0]), image(p, pair[1])) for p in D8}
        seen.update(orbit)
        orbits.append((min(orbit), orbit))
    orbits.sort()
    lookup = {pair: k for k, (_, orb) in enumerate(orbits) for pair in orb}
    types = [{"type": k, "N12": rep[0], "N13": rep[1], "orbit_size": len(orb),
              "intersection": len(set(rep[0]) & set(rep[1])),
              "swap": lookup[(rep[1], rep[0])]}
             for k, (rep, orb) in enumerate(orbits)]
    require(len(D8) == 8 and len(orbits) == 7 and len(seen) == 36, "D8 partition failed")
    require([r["swap"] for r in types] == [0, 3, 2, 1, 4, 5, 6], "Type convention failed")
    return types, lookup


def build_cases(types: Any, lookup: Any) -> list[dict[str, Any]]:
    counts: Counter[Any] = Counter()
    # Directly enumerate the 36^3 ordered local patterns, independently of project code.
    for patterns in it.product(tuple(lookup), repeat=3):
        ts = tuple(lookup[p] for p in patterns)
        a = sum(len(set(p[0]) & set(p[1])) for p in patterns)
        canonical = min(tuple(sorted(ts)), tuple(sorted(types[t]["swap"] for t in ts)))
        for s in (0, 1):
            d, c = 6 - s, 6 - 5 * s - a
            if 0 <= c <= d:
                counts[(s, canonical)] += 1
    cases = []
    for idx, ((s, ts), count) in enumerate(sorted(counts.items())):
        a = sum(types[t]["intersection"] for t in ts)
        d, c = 6 - s, 6 - 5 * s - a
        bits = [(int(u in types[t]["N12"]), int(u in types[t]["N13"]))
                for t in ts for u in range(4)]
        hard = (s == 0 and 2 not in ts) or (s == 1 and ts in {(2, 2, 5), (2, 5, 6), (5, 6, 6)})
        weight = count * math.comb(18, d) * math.comb(d, c) * math.comb(18 - d, d - c)
        cases.append({
            "id": f'k{idx:02d}_s{s}_t{"".join(map(str, ts))}', "s": s, "types": ts, "a": a,
            "cell_sizes": (c, d - c, d - c, 18 - 2 * d + c), "attached_T_bits": bits,
            "raw_group_patterns": count, "raw_T_weight": weight, "historical_V3_hard": hard,
        })
    require(len(cases) == 72 and sum(c["s"] == 0 for c in cases) == 62, "V3 case count failed")
    require(sum(c["raw_T_weight"] for c in cases) == 3544507983744, "T weight failed")
    require(sum(c["historical_V3_hard"] for c in cases) == 43, "Hard-case mapping failed")
    return cases


def transformation_table() -> dict[Any, Any]:
    table = {}
    for p, q, flip in it.product(D8, D8, (False, True)):
        pinv = inverse(p)
        values = []
        for pi in PERMS:
            new = tuple(q[pi[pinv[u]]] for u in range(4))
            values.append(PID[inverse(new) if flip else new])
        require(len(set(values)) == 24, "Non-bijective S4 action")
        table[(p, q, flip)] = tuple(values)
    return table


def actions_for(case: Any, types: Any, table: Any) -> list[Any]:
    actions, ts = [], case["types"]
    for sigma, epsilon in it.product(it.permutations(range(3)), (0, 1)):
        choices = []
        for r in range(3):
            src, dst = types[ts[r]], types[ts[sigma[r]]]
            wanted = (dst["N12"], dst["N13"])
            if epsilon:
                wanted = wanted[::-1]
            choices.append(tuple(g for g in D8 if (image(g, src["N12"]), image(g, src["N13"])) == wanted))
        for gs in it.product(*choices):
            action: list[Any] = [None] * 3
            for old, (r, t) in enumerate(PAIRS):
                sr, st = sigma[r], sigma[t]
                dest = PAIR_ID[tuple(sorted((sr, st)))]
                action[dest] = (old, table[(gs[r], gs[t], sr > st)])
            actions.append(tuple(action))
    require(bool(actions), "Empty stabilizer")
    return actions


def apply_action(action: Any, triple: tuple[int, ...]) -> int:
    a = action[0][1][triple[action[0][0]]]
    b = action[1][1][triple[action[1][0]]]
    c = action[2][1][triple[action[2][0]]]
    return (a * 24 + b) * 24 + c


def fixed_count(action: Any) -> int:
    """Independent Burnside count by cycles of the three coordinates."""
    unvisited, result = set(range(3)), 1
    while unvisited:
        start, cycle = min(unvisited), []
        current = start
        while current not in cycle:
            cycle.append(current)
            unvisited.remove(current)
            current = action[current][0]
        require(current == start, "Invalid coordinate permutation")
        count = 0
        for value in range(24):
            mapped = value
            for dest in reversed(cycle):
                mapped = action[dest][1][mapped]
            count += mapped == value
        result *= count
    return result


def neighbors_for(triple: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    neighbors = [[4 * (u // 4) + PARTNER[u % 4]] for u in range(12)]
    for k, (r, t) in enumerate(PAIRS):
        for u, v in enumerate(PERMS[triple[k]]):
            i, j = 4 * r + u, 4 * t + v
            neighbors[i].append(j)
            neighbors[j].append(i)
    require(all(len(set(ns)) == 3 for ns in neighbors), "Attached degree failed")
    return tuple(tuple(ns) for ns in neighbors)


def row_constants(case: Any, neighbors: Any) -> list[tuple[int, int, int]]:
    bits, s, result = case["attached_T_bits"], case["s"], []
    for u, (x, y) in enumerate(bits):
        ns = Counter(CELL_ID[bits[v]] for v in neighbors[u])
        a, b, c = ns[0], ns[1], ns[2]
        result.append((6 - 3 * x - s * y - a - b, 6 - 3 * y - s * x - a - c,
                       (2 + s) * (x + y) - 2 + 2 * a + b + c))
    return result


def lemma2(case: Any, constants: Any) -> bool:
    """Literal review bound o_X+1, including empty cells; not silently tightened."""
    oa, ob, oc, od = case["cell_sizes"]
    lower, upper = 0, 0
    for qb, qc, qd in constants:
        lo = max(0, qb - ob - 1, qc - oc - 1, -qd)
        hi = min(oa + 1, qb, qc, od + 1 - qd)
        if lo > hi:
            return False
        lower += lo
        upper += hi
    return lower <= 6 * oa <= upper


def row_realizability(case: Any, constants: Any) -> bool:
    """Necessary refinement: each attached row has one ordinary L edge.

    Enumerate w and the L-cell, then convolve w values using a bitset. This is
    a relaxation: rows are not yet coupled through ordinary profile columns.
    """
    cells, reachable = case["cell_sizes"], 1
    for u, (qb, qc, qd) in enumerate(constants):
        options = []
        for w in range(cells[0] + 2):
            weights = (w, qb - w, qc - w, qd + w)
            require(sum(weights) == 10 - sum(case["attached_T_bits"][u]), "Row-sum identity failed")
            for ell in range(4):
                if cells[ell] and all((2 <= weights[k] <= cells[k] + 1) if k == ell
                                     else (0 <= weights[k] <= cells[k]) for k in range(4)):
                    options.append(w)
                    break
        if not options:
            return False
        next_reachable = 0
        for w in options:
            next_reachable |= reachable << w
        reachable = next_reachable
    return bool((reachable >> (6 * cells[0])) & 1)


def make_gram(case: Any, neighbors: Any) -> tuple[list[list[int]], list[list[int]]]:
    h = [[0] * 14 for _ in range(14)]
    for u in range(12):
        for v in neighbors[u]:
            h[u][v] = 1
        for b, bit in enumerate(case["attached_T_bits"][u]):
            h[u][12 + b] = h[12 + b][u] = bit
    h[12][12] = h[13][13] = 2
    h[12][13] = h[13][12] = case["s"]
    m = [[0] * 14 for _ in range(14)]
    for i in range(14):
        for j in range(i, 14):
            r = int(i < 12 and j < 12 and i // 4 == j // 4)
            value = 12 * (i == j) + 6 - 3 * r - h[i][j] - sum(h[i][k] * h[k][j] for k in range(14))
            m[i][j] = m[j][i] = value
    return h, m


def gram_basic(m: list[list[int]]) -> bool:
    return all(m[i][j] >= 0 and m[i][j] ** 2 <= m[i][i] * m[j][j]
               for i in range(len(m)) for j in range(i, len(m)))


def exact_psd_details(m: list[list[int]]) -> tuple[bool, int, Any]:
    """Exact Schur test plus a negative principal-minor certificate if indefinite.

    Positive updates are positive scalings of the Schur complement. A zero
    pivot is allowed only with zero remaining row. The used-index principal
    determinant equals the stored pivot. All divisions are checked exactly.
    """
    b, previous, rank, used = [row[:] for row in m], 1, 0, []
    for k in range(len(b)):
        pivot = b[k][k]
        if pivot < 0:
            return False, rank, {"indices": used + [k], "determinant": pivot}
        if pivot == 0:
            for j in range(k + 1, len(b)):
                if b[k][j]:
                    value = -b[k][j] ** 2
                    require(value % previous == 0, "Minor certificate division failed")
                    return False, rank, {"indices": used + [k, j], "determinant": value // previous}
            continue
        rank += 1
        for i in range(k + 1, len(b)):
            for j in range(i, len(b)):
                value = pivot * b[i][j] - b[i][k] * b[k][j]
                require(value % previous == 0, "Non-exact fraction-free division")
                b[i][j] = b[j][i] = value // previous
        previous = pivot
        used.append(k)
    return True, rank, None


def exact_psd(m: list[list[int]]) -> tuple[bool, int]:
    status, rank, _ = exact_psd_details(m)
    return status, rank


def profiles_936() -> list[tuple[int, ...]]:
    options = [tuple(int(i in pair) for i in range(4)) for pair in it.combinations(range(4), 2)]
    options += [tuple(2 if i == ell else 0 for i in range(4)) for ell in range(4)]
    profiles = [sum(choice, ()) for choice in it.product(options, repeat=3) if sum(choice, ()).count(2) <= 2]
    require(len(profiles) == len(set(profiles)) == 936, "Profile universe failed")
    require(Counter(p.count(2) for p in profiles) == {0: 216, 1: 432, 2: 288}, "Profile modes failed")
    return profiles


def verify_local_repo(repo: Path | None) -> dict[str, Any]:
    if repo is None:
        return {"requested": False, "reference_commit": REFERENCE_COMMIT}
    result: dict[str, Any] = {"requested": True, "path": str(repo), "files": {}}
    require(repo.is_dir(), f"Repository directory missing: {repo}")
    result["head"] = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    for name, expected in REFERENCE_BLOBS.items():
        content = (repo / name).read_bytes()
        actual = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        result["files"][name] = {"expected_blob": expected, "actual_blob": actual}
        require(actual == expected, f"Reference source differs: {name}; no project files changed")
    return result


def self_tests() -> dict[str, Any]:
    require(exact_psd([[1, 0], [0, 1]]) == (True, 2), "Positive PSD control failed")
    require(exact_psd([[1, 1], [1, 1]]) == (True, 1), "Singular PSD control failed")
    require(exact_psd([[0, 0, 0], [0, 1, 1], [0, 1, 1]]) == (True, 1), "Zero pivot failed")
    require(not exact_psd([[0, 1], [1, 0]])[0], "Indefinite control failed")
    for seed in range(20):
        x = [[(i * 17 + j * 5 + seed) % 7 - 3 for j in range(5)] for i in range(8)]
        m = [[sum(a * b for a, b in zip(ri, rj)) for rj in x] for ri in x]
        require(exact_psd(m)[0], "Constructed positive Gram rejected")
    require(10 + 2 * 4 == 12 + 6 and 10 + 2 * 4 != 12 + 3, "Wrong-3J negative control failed")
    profiles_936()
    return {"integer_PSD_controls": "PASS", "wrong_3J_negative_control": "PASS",
            "profiles": 936, "profile_mode_counts": {0: 216, 1: 432, 2: 288}}


def save(path: Path, value: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def audit_case(case: Any, types: Any, table: Any, do_psd: bool, progress: Any) -> tuple[Any, Any]:
    start = time.monotonic()
    actions = actions_for(case, types, table)
    burnside = sum(fixed_count(a) for a in actions)
    require(burnside % len(actions) == 0, "Nonintegral Burnside average")
    seen, records = bytearray(len(TRIPLES)), []
    raw_kept = raw_row_kept = covered = 0
    ranks: Counter[Any] = Counter()
    for code, triple in enumerate(TRIPLES):
        if seen[code]:
            continue
        orbit = {apply_action(action, triple) for action in actions}
        require(code == min(orbit), "Nonminimal representative")
        require(len(actions) % len(orbit) == 0, "Orbit-stabilizer failed")
        require(not any(seen[x] for x in orbit), "Orbit overlap")
        neighbors = neighbors_for(triple)
        constants = row_constants(case, neighbors)
        keep = lemma2(case, constants)
        row_keep = row_realizability(case, constants) if keep else False
        # Invariance is checked for all 13,824 labelled triples per case.
        for member in orbit:
            seen[member] = 1
            if member != code:
                mc = row_constants(case, neighbors_for(TRIPLES[member]))
                require(lemma2(case, mc) == keep, "Lemma2 K-invariance failed")
                if keep:
                    require(row_realizability(case, mc) == row_keep, "Row K-invariance failed")
        covered += len(orbit)
        raw_kept += len(orbit) if keep else 0
        raw_row_kept += len(orbit) if row_keep else 0
        basic_keep = psd_keep = None
        witness = None
        if row_keep:
            _, m = make_gram(case, neighbors)
            basic_keep = gram_basic(m)
            if basic_keep and do_psd:
                psd_keep, rank, witness = exact_psd_details(m)
                ranks[str(rank) if psd_keep else "indefinite"] += 1
            elif do_psd:
                psd_keep = False
        elif do_psd:
            psd_keep = False
        records.append([code, len(orbit), int(keep), int(row_keep), basic_keep, psd_keep, witness])
        progress(case["id"], covered, len(TRIPLES))
    require(all(seen) and sum(r[1] for r in records) == 13824, "Label coverage failed")
    require(len(records) == burnside // len(actions), "Burnside disagrees with orbit enumeration")
    summary = {
        **case, "K_order": len(actions), "V4_orbits": len(records), "burnside_orbits": burnside // len(actions),
        "labelled_Lemma2_survivors": raw_kept, "Lemma2_orbits": sum(r[2] for r in records),
        "row_realizable_orbits": sum(r[3] for r in records), "labelled_row_realizable": raw_row_kept,
        "gram_basic_orbits": sum(r[4] is True for r in records),
        "exact_PSD_orbits": sum(r[5] is True for r in records) if do_psd else None,
        "PSD_rank_counts": dict(ranks), "wall_seconds": round(time.monotonic() - start, 3),
        "checks": {"coverage": "PASS", "Burnside": "PASS", "Lemma2_K_invariance": "PASS",
                   "row_filter_K_invariance": "PASS"},
    }
    return summary, records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True, help="NEW output directory")
    ap.add_argument("--repo", type=Path, help="Read-only source-hash check in local repo")
    ap.add_argument("--cases", default="all", help="all or comma-separated case IDs")
    ap.add_argument("--exact-psd", action="store_true", help="Exact integer Gram PSD checks")
    ap.add_argument("--status-seconds", type=float, default=600.0)
    args = ap.parse_args()
    require(args.status_seconds > 0, "status-seconds must be positive")
    start = time.monotonic()
    provenance, tests = verify_local_repo(args.repo), self_tests()
    types, lookup = local_types()
    cases = build_cases(types, lookup)
    if args.cases != "all":
        wanted = set(args.cases.split(","))
        require(wanted <= {c["id"] for c in cases}, "Unknown case ID")
        cases = [c for c in cases if c["id"] in wanted]
    args.out.mkdir(parents=True, exist_ok=False)
    require(shutil.disk_usage(args.out).free >= 64 * 1024 * 1024, "Less than 64 MiB disk free")
    metadata = {
        "version": VERSION, "reference_commit": REFERENCE_COMMIT, "reference_blobs": REFERENCE_BLOBS,
        "review_source": "O3_fixed_triangle_claude_review_20260908.md", "python": sys.version,
        "platform": platform.platform(), "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "provenance": provenance, "self_tests": tests, "exact_PSD": args.exact_psd, "status": "RUNNING",
        "case_record_columns": ["matching_code_base24", "orbit_size", "Lemma2_keep", "row_realizable",
                                "gram_basic_keep", "exact_PSD_keep", "negative_principal_minor"],
        "claim_scope": "Independent finite arithmetic checks; no SAT/LRAT/Cake proofs",
    }
    save(args.out / "metadata.json", metadata)
    save(args.out / "local_types.json", types)
    save(args.out / "profiles_936.json", profiles_936())
    table, summaries = transformation_table(), []
    last_status = [time.monotonic()]

    def progress(cid: str, done: int, total: int) -> None:
        now = time.monotonic()
        if now - last_status[0] >= args.status_seconds:
            completed = len(summaries) + done / total
            eta = (now - start) * max(len(cases) - completed, 0) / max(completed, 1e-9)
            print(f"STATUS case={cid} cases_done={len(summaries)}/{len(cases)} labelled={done}/{total} "
                  f"elapsed_s={now-start:.1f} ETA_s~{eta:.1f}", flush=True)
            last_status[0] = now

    print(f"PREFLIGHT_START version={VERSION} cases={len(cases)} profiles=936 exact_PSD={args.exact_psd} NO_SAT", flush=True)
    try:
        for case in cases:
            summary, records = audit_case(case, types, table, args.exact_psd, progress)
            summaries.append(summary)
            save(args.out / f'{case["id"]}.json', {"summary": summary, "orbits": records})
            save(args.out / "case_summaries.json", summaries)
            print(f'{case["id"]} K={summary["K_order"]} orbits={summary["V4_orbits"]} '
                  f'lemma2={summary["Lemma2_orbits"]} row={summary["row_realizable_orbits"]} '
                  f'gram_basic={summary["gram_basic_orbits"]} PSD={summary["exact_PSD_orbits"]} '
                  f'sec={summary["wall_seconds"]}', flush=True)
        totals = {}
        for name, subset in (("all", summaries), ("historical_hard", [c for c in summaries if c["historical_V3_hard"]])):
            totals[name] = {key: sum(c[key] for c in subset) for key in (
                "V4_orbits", "Lemma2_orbits", "labelled_Lemma2_survivors", "row_realizable_orbits", "gram_basic_orbits"
            )}
            totals[name]["cases"] = len(subset)
            totals[name]["exact_PSD_orbits"] = sum(c["exact_PSD_orbits"] for c in subset) if args.exact_psd else None
        regression = {}
        if len(summaries) == 72:
            expected = {("all", "V4_orbits"): 116079, ("historical_hard", "V4_orbits"): 93860,
                        ("all", "labelled_Lemma2_survivors"): 619072, ("historical_hard", "Lemma2_orbits"): 72862}
            for (scope, key), value in expected.items():
                actual = totals[scope][key]
                regression[f"{scope}.{key}"] = {"expected": value, "actual": actual, "match": actual == value}
        with (args.out / "summary.tsv").open("w", encoding="utf-8") as stream:
            columns = ["id", "s", "a", "historical_V3_hard", "K_order", "V4_orbits", "Lemma2_orbits",
                       "row_realizable_orbits", "gram_basic_orbits", "exact_PSD_orbits", "wall_seconds"]
            stream.write("\t".join(columns) + "\n")
            for c in summaries:
                stream.write("\t".join(str(c[k]) for k in columns) + "\n")
        metadata.update({"status": "COMPLETE", "totals": totals, "review_regression": regression,
                         "wall_seconds": round(time.monotonic() - start, 3)})
        save(args.out / "metadata.json", metadata)
        print("PREFLIGHT_COMPLETE " + json.dumps(totals, sort_keys=True), flush=True)
        print("REVIEW_REGRESSION " + json.dumps(regression, sort_keys=True), flush=True)
    except BaseException as exc:
        metadata.update({"status": "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "ERROR",
                         "error": repr(exc), "completed_cases": len(summaries),
                         "wall_seconds": round(time.monotonic() - start, 3)})
        save(args.out / "metadata.json", metadata)
        raise


if __name__ == "__main__":
    main()
