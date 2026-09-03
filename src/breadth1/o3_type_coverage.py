#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


TAU_CASES = ((6, 27), (13, 20), (20, 13), (27, 6))


def partitions(n: int, minimum: int = 3):
    if n == 0:
        yield ()
        return
    for a in range(n, minimum - 1, -1):
        for rest in partitions(n - a, minimum):
            if not rest or a >= rest[0]:
                yield (a,) + rest


def type_rows():
    rows = []
    for tau, u_size in TAU_CASES:
        for part in partitions(u_size):
            if 4 in part:
                continue

            counts = Counter(part)
            cycle_ge5 = [m for m in part if m >= 5]
            special = [m for m in part if 5 <= m <= 8]

            rows.append({
                "tau": tau,
                "u_size": u_size,
                "cycle_type": ",".join(map(str, part)),
                "components": len(part),
                "c3": counts[3],
                "c5": counts[5],
                "c6": counts[6],
                "c7": counts[7],
                "c8": counts[8],
                "c_ge9": sum(v for k, v in counts.items() if k >= 9),
                "has_c3_lemma_B": int(counts[3] > 0),
                "has_generic_cm": int(bool(cycle_ge5)),
                "has_special_c5_c8": int(bool(special)),
                "has_moment_layer": int(bool(cycle_ge5)),
                "touched_by_c3_c5_c6": int(any(m in (3, 5, 6) for m in part)),
                "all_component_lengths": ",".join(map(str, part)),
            })
    return rows


def summarize(rows):
    by_tau = {}
    for tau, _ in TAU_CASES:
        subset = [r for r in rows if r["tau"] == tau]
        by_tau[str(tau)] = {
            "types": len(subset),
            "without_c3": sum(r["c3"] == 0 for r in subset),
            "with_c3": sum(r["c3"] > 0 for r in subset),
            "with_generic_cm": sum(r["has_generic_cm"] for r in subset),
            "with_special_c5_c8": sum(r["has_special_c5_c8"] for r in subset),
            "untouched_by_c3_c5_c6": sum(not r["touched_by_c3_c5_c6"] for r in subset),
        }

    return {
        "format": "O3-BREADTH-1-TYPE-COVERAGE-0.1",
        "total_types": len(rows),
        "without_c3": sum(r["c3"] == 0 for r in rows),
        "with_c3": sum(r["c3"] > 0 for r in rows),
        "with_generic_cm": sum(r["has_generic_cm"] for r in rows),
        "with_special_c5_c8": sum(r["has_special_c5_c8"] for r in rows),
        "untouched_by_c3_c5_c6": sum(not r["touched_by_c3_c5_c6"] for r in rows),
        "by_tau": by_tau,
    }


def validate(rows, summary):
    expected_types = {"6": 103, "13": 28, "20": 6, "27": 2}
    expected_without_c3 = {"6": 42, "13": 13, "20": 3, "27": 1}

    assert summary["total_types"] == 139
    assert summary["without_c3"] == 59
    assert summary["untouched_by_c3_c5_c6"] == 21

    for tau in expected_types:
        assert summary["by_tau"][tau]["types"] == expected_types[tau]
        assert summary["by_tau"][tau]["without_c3"] == expected_without_c3[tau]

    assert len({(r["tau"], r["cycle_type"]) for r in rows}) == 139
    assert all("4" not in r["all_component_lengths"].split(",") for r in rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    rows = type_rows()
    summary = summarize(rows)
    validate(rows, summary)

    tsv_path = Path(args.tsv)
    summary_path = Path(args.summary)
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys())
    with tsv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    summary_path.write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )

    print("O3_TYPE_COVERAGE PASS")
    print("TOTAL", summary["total_types"])
    print("WITHOUT_C3", summary["without_c3"])
    print("UNTOUCHED_C3_C5_C6", summary["untouched_by_c3_c5_c6"])
    for tau in ("6", "13", "20", "27"):
        item = summary["by_tau"][tau]
        print(
            "TAU",
            tau,
            "types",
            item["types"],
            "without_c3",
            item["without_c3"],
            "generic_cm",
            item["with_generic_cm"],
        )


if __name__ == "__main__":
    main()
