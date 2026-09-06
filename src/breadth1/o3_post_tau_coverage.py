#!/usr/bin/env python3
"""Generate the post-tau-theorem O3 type coverage summary.

Historical 139-type artifacts are intentionally not rewritten. This script
applies the project theorem tau ≡ 0 (mod 3) to the existing C4-free type
enumeration and marks the two previously excluded tau=6 controls.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import o3_generic_core as generic

ALLOWED_TAU = (6, 27)
KNOWN_EXCLUDED = {
    (6, (3,) * 9): "PREVIOUSLY_EXCLUDED",
    (6, (6,) + (3,) * 7): "FULLCERT_1.1_EXCLUDED",
}


def rows():
    out = []
    for tau in ALLOWED_TAU:
        for part in generic.all_types(tau):
            if 4 in part:
                continue
            counts = Counter(part)
            out.append({
                "tau": tau,
                "u_size": 33 - tau,
                "cycle_type": ",".join(map(str, part)),
                "components": len(part),
                "c3": counts[3],
                "c5": counts[5],
                "c6": counts[6],
                "c7": counts[7],
                "c8": counts[8],
                "c_ge9": sum(number for length, number in counts.items() if length >= 9),
                "has_c3_lemma_B": int(counts[3] > 0),
                "has_generic_cm": int(any(length >= 5 for length in part)),
                "status": KNOWN_EXCLUDED.get((tau, part), "OPEN"),
            })
    return out


def summary(data):
    by_tau = Counter(row["tau"] for row in data)
    status = Counter(row["status"] for row in data)
    open_by_tau = Counter(row["tau"] for row in data if row["status"] == "OPEN")
    value = {
        "format": "O3-BREADTH-1-POST-TAU-COVERAGE-1.0",
        "theorem": "FPF order-3 implies tau ≡ 0 (mod 3); combined with trace restriction gives tau in {6,27}",
        "historical_c4_free_types": 139,
        "removed_by_tau_mod3": {"tau13": 28, "tau20": 6, "total": 34},
        "remaining_types": len(data),
        "by_tau": {str(k): {"types": by_tau[k]} for k in sorted(by_tau)},
        "previously_excluded": {
            "count": len(data) - status["OPEN"],
            "types": [
                "tau06_3-3-3-3-3-3-3-3-3",
                "tau06_6-3-3-3-3-3-3-3",
            ],
        },
        "open_types": status["OPEN"],
        "open_by_tau": {str(k): open_by_tau[k] for k in sorted(open_by_tau)},
        "historical_scout_note": (
            "The 2026-09-05 A/B scout remains a valid 139-type historical experiment; "
            "34 of its types are now known impossible by theorem and must not be included "
            "in future campaigns."
        ),
    }
    assert value["remaining_types"] == 105
    assert value["open_types"] == 103
    assert value["open_by_tau"] == {"6": 101, "27": 2}
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", required=True)
    ap.add_argument("--summary", required=True)
    args = ap.parse_args()

    data = rows()
    fieldnames = list(data[0])
    with Path(args.tsv).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(data)
    Path(args.summary).write_text(json.dumps(summary(data), indent=2, sort_keys=True) + "\n")
    print("O3_POST_TAU_COVERAGE PASS types=105 open=103")


if __name__ == "__main__":
    main()
