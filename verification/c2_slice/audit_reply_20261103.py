"""Small independent checks for the Mizopl reply review of 3 November 2026.

Standard library only. Prints JSON; never touches search jobs or proof files.
Optional argument: the pinned upstream LEGO summary JSON, for bookkeeping checks.
"""
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def matchings(vertices):
    if not vertices:
        yield ()
        return
    first, *rest = vertices
    yield from matchings(rest)
    for partner in rest:
        remaining = [v for v in rest if v != partner]
        for tail in matchings(remaining):
            yield ((first, partner),) + tail


def check_handshaking():
    counts = Counter()
    for edges in matchings(list(range(7))):
        degrees = [0] * 7
        for a, b in edges:
            degrees[a] += 1
            degrees[b] += 1
        require(max(degrees) <= 1, "Not a matching")
        require(sum(degrees) == 2 * len(edges), "Handshaking failed")
        require(0 in degrees, "Matching on seven vertices without isolate")
        counts[len(edges)] += 1
    require(dict(counts) == {0: 1, 1: 21, 2: 105, 3: 105}, "Wrong enumeration")
    single_edge_degrees = [1, 1, 0, 0, 0, 0, 0]
    cycle_edges = [(i, (i + 1) % 7) for i in range(7)]
    cycle_degrees = [0] * 7
    for a, b in cycle_edges:
        cycle_degrees[a] += 1
        cycle_degrees[b] += 1
    require(cycle_degrees == [2] * 7, "Cycle control failed")
    parity_cases = 0
    for values in product(range(2), repeat=7):
        if sum(values) % 2 == 0:
            require(sum(values) <= 6 and 0 in values, "Arithmetic lemma failed")
            parity_cases += 1
    require(parity_cases == 64, "Wrong parity-vector count")
    return {
        "labelled_matchings": sum(counts.values()),
        "counts_by_edges": dict(sorted(counts.items())),
        "even_binary_degree_vectors": parity_cases,
        "single_edge_counterexample_to_all_degrees_zero": single_edge_degrees,
        "degree_two_control_without_isolate": cycle_degrees,
        "six_odd_plus_one_even_mod_two": (6 * 1 + 0) % 2,
        "scope": "Auxiliary graphs and arithmetic, not SRG witnesses",
    }


def capacity_pass(prefix, domains, width):
    once = sum(1 << c for c in range(width) if prefix[c] >= 1)
    twice = sum(1 << c for c in range(width) if prefix[c] >= 2)
    available_once = 0
    available_twice = 0
    for domain in domains:
        support = 0
        for mask in domain:
            support |= mask
        available_twice |= available_once & support
        available_once |= support
    full = (1 << width) - 1
    return (twice | (once & available_once) | available_twice) & full == full


def has_completion(prefix, domains, width):
    return any(
        all(prefix[c] + sum((mask >> c) & 1 for mask in rows) == 2
            for c in range(width))
        for rows in product(*domains)
    )


def check_capacity():
    domains = [
        tuple(mask for mask in range(4) if subset & (1 << mask))
        for subset in range(16)
    ]
    cases = feasible = rejected = false_positive = 0
    for prefix in product(range(3), repeat=2):
        for pair in product(domains, repeat=2):
            possible = has_completion(prefix, pair, 2)
            passed = capacity_pass(prefix, pair, 2)
            require(not possible or passed, "Filter discarded a completion")
            cases += 1
            feasible += possible
            rejected += not passed
            false_positive += passed and not possible
    one_column_cases = 0
    for prefix in range(3):
        for availabilities in product(range(4), repeat=8):
            row_domains = [tuple(x for x in range(2) if a & (1 << x))
                           for a in availabilities]
            maximum = sum(1 in d for d in row_domains)
            minimum = sum(d == (1,) for d in row_domains)
            possible = all(row_domains) and minimum <= 2 - prefix <= maximum
            passed = capacity_pass((prefix,), row_domains, 1)
            require(not possible or passed, "Eight-domain filter lost a completion")
            one_column_cases += 1
    require(not has_completion((0, 0), [(1, 2), (1, 2)], 2), "Bad control")
    require(capacity_pass((0, 0), [(1, 2), (1, 2)], 2), "Expected relaxation")
    return {
        "two_column_two_domain_cases": cases,
        "feasible_cases": feasible,
        "rejected_cases": rejected,
        "false_positives": false_positive,
        "one_column_eight_domain_cases": one_column_cases,
        "false_negatives": 0,
        "scope": "Necessary capacity condition; passes are not completion certificates",
    }


def check_column_table():
    rows = []
    for k in range(1, 6):
        n2 = 2 * k * (k - 1)
        n1 = 4 * k * (6 - k)
        n0 = 60 - n1 - n2
        require(n1 + 2 * n2 == 20 * k, "First moment failed")
        require(n1 + 4 * n2 == 4 * k * (k + 4), "Second moment failed")
        rows.append({"k": k, "n2": n2, "n1": n1, "n0": n0})
    for left, right in zip(rows, reversed(rows)):
        require((left["n2"], left["n1"], left["n0"]) ==
                (right["n0"], right["n1"], right["n2"]), "Duality failed")
    return rows


def check_upstream_summary(filename):
    data = json.loads(Path(filename).read_text(encoding="utf-8-sig"))
    strata = data["strata_certified"]
    six = strata["kt1_2_partition_2_2_1_1"]
    fifty_six = strata["kt1_2_partition_4_1_1"]
    require(len(six["orbits"]) == 6, "Wrong six-orbit record count")
    for field, total in (("b1", "total_b1"), ("b12", "total_b12")):
        require(sum(r[field] for r in six["orbits"]) == six[total], total)
    require(all(r["b123_sols"] == 0 for r in six["orbits"]), "Nonzero solutions")
    cones = fifty_six["subcones"]
    secondary = fifty_six["secondary_11_classes_8dom"]
    require({r["cone_id"] for r in cones} == set(range(45)), "Subcone IDs")
    require(len(secondary) == len({r["class_id"] for r in secondary}) == 11,
            "Secondary IDs")
    for field in ("b1", "d6", "d8"):
        require(sum(r[field] for r in cones) == fifty_six["subcones_total_" + field],
                "Subcone total " + field)
    for field in ("b1", "nodes"):
        require(sum(r[field] for r in secondary) ==
                fifty_six["secondary_11_classes_total_" + field],
                "Secondary total " + field)
    require(all(r["sols"] == 0 for r in cones + secondary), "Nonzero solutions")
    covered = sorted({c for r in cones for c in r["classes"]})
    require(covered == list(range(56)), "Reported class-label coverage")
    return {"six_records": 6, "subcone_records": 45, "secondary_records": 11,
            "reported_class_label_union": covered, "totals_consistent": True,
            "scope": "Internal JSON consistency only, not replay or geometric coverage"}


result = {"status": "PASS", "handshaking": check_handshaking(),
          "capacity": check_capacity(), "column_table": check_column_table(),
          "slice_accounting": {"type1_zero_orbits": 2670 + 55 + 168 + 10,
                               "reported_class6_remaining": 2670 - 270,
                               "nonnegative_K_orbits": 14 + 2670 + 55 + 168 +
                                                       10 + 30 + 56 + 6 + 299,
                               "negative_K_orbits": 272}}
if len(sys.argv) > 1:
    result["upstream_summary"] = check_upstream_summary(sys.argv[1])
print(json.dumps(result, indent=4, sort_keys=True))
