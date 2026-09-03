#!/usr/bin/env python3
"""Independent bookkeeping checker for Task-03 FULLCERT 1.1.

This is deliberately separate from the certification runner. It does not prove
UNSAT itself; lrat-check and cake_lpr do that per certificate. It independently
checks that the certified cubes cover the 512-root partition and that every
Triangle split used to replace a TIMEOUT parent is the exact 001/010/100
partition of an EO triplet syntactically present in the lemma source CNF.
"""

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

PATTERNS = ["001", "010", "100"]


def sha256_file(path, block=8 * 1024 * 1024):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(block), b""):
            h.update(data)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def fail(message):
    raise RuntimeError(message)


def check_cert_artifact(cert):
    if cert.get("lrat_exit") != 0 or cert.get("cake_exit") != 0:
        fail(f"checker exit not zero for {cert.get('cnf')}")
    gz = Path(cert["proof_gz"])
    if not gz.exists():
        fail(f"missing proof archive {gz}")
    if sha256_file(gz) != cert["gzip_sha256"]:
        fail(f"gzip hash mismatch {gz}")
    raw_expected = cert.get("raw_proof_sha256")
    if raw_expected:
        h = hashlib.sha256()
        with gzip.open(gz, "rb") as f:
            for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                h.update(block)
        if h.hexdigest() != raw_expected:
            fail(f"decompressed raw-proof hash mismatch {gz}")


def eo_clause_set(source, groups):
    wanted = set()
    for group in groups:
        x, y, z = group
        wanted.add(tuple(sorted((x, y, z))))
        wanted.add(tuple(sorted((-x, -y))))
        wanted.add(tuple(sorted((-x, -z))))
        wanted.add(tuple(sorted((-y, -z))))
    seen = set()
    with Path(source).open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c") or line.startswith("p"):
                continue
            clause = tuple(sorted(int(x) for x in line.split() if x != "0"))
            if clause in wanted:
                seen.add(clause)
    missing = wanted - seen
    if missing:
        fail(f"missing EO clauses, first={sorted(missing)[:4]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    manifest = load(manifest_path)
    coverage = load(manifest["coverage_input"])

    if sha256_file(manifest["coverage_input"]) != manifest["coverage_input_sha256"]:
        fail("coverage_input hash mismatch")
    if sha256_file(coverage["lemma_source"]) != coverage["lemma_source_sha256"]:
        fail("lemma source hash mismatch")
    if sha256_file(coverage["rescout_state"]) != coverage["rescout_state_sha256"]:
        fail("rescout state hash mismatch")
    if sha256_file(coverage["frontier_state"]) != coverage["frontier_state_sha256"]:
        fail("frontier state hash mismatch")
    if sha256_file(coverage["core"]) != coverage["core_sha256"]:
        fail("core hash mismatch")

    baseline = manifest.get("baseline_certificate")
    if baseline is not None:
        check_cert_artifact(baseline)
        print("COVERAGE_CHECK_OK mode=BASELINE_DIRECT stronger_than_lemma")
        return

    rescout = load(coverage["rescout_state"])
    frontier = load(coverage["frontier_state"])
    roots = sorted(rescout["cubes"])
    if roots != [format(i, "09b") for i in range(512)]:
        fail("512 root partition incomplete")

    direct = sorted(k for k, r in rescout["cubes"].items() if r["state"] == "UNSAT_UNCERTIFIED")
    hard = sorted(k for k, r in rescout["cubes"].items() if r["state"] == "TIMEOUT")
    if len(direct) != 488 or len(hard) != 24:
        fail(f"bad rescout partition direct={len(direct)} hard={len(hard)}")
    if direct != sorted(coverage["direct_roots"]) or hard != sorted(coverage["hard_roots"]):
        fail("coverage-input root sets differ from rescout")
    if sorted(frontier["root_timeout_parents"]) != hard:
        fail("frontier hard roots differ from rescout")

    jobs = frontier["jobs"]
    children = defaultdict(list)
    depth1 = defaultdict(list)
    for key, rec in jobs.items():
        if rec.get("parent_job"):
            children[rec["parent_job"]].append((key, rec))
        if rec["depth"] == 1:
            depth1[rec["root_parent"]].append((key, rec))

    groups = set()
    for root in hard:
        kids = depth1[root]
        pats = sorted(rec["pattern"] for _, rec in kids)
        if pats != PATTERNS:
            fail(f"bad first split root={root} patterns={pats}")
        split_groups = {tuple(rec["split_vars"]) for _, rec in kids}
        if len(split_groups) != 1:
            fail(f"inconsistent first split vars root={root}")
        groups |= split_groups

    for key, rec in jobs.items():
        if rec["state"] != "TIMEOUT":
            continue
        kids = children.get(key, [])
        pats = sorted(child["pattern"] for _, child in kids)
        if pats != PATTERNS:
            fail(f"bad internal split key={key} patterns={pats}")
        split_groups = {tuple(child["split_vars"]) for _, child in kids}
        if len(split_groups) != 1:
            fail(f"inconsistent internal split vars key={key}")
        groups |= split_groups

    eo_clause_set(coverage["lemma_source"], groups)

    parent_keys = set(children)
    leaves = sorted((key, rec) for key, rec in jobs.items() if key not in parent_keys)
    if len(leaves) != 168:
        fail(f"expected 168 leaves got {len(leaves)}")
    if any(rec["state"] != "UNSAT_UNCERTIFIED" for _, rec in leaves):
        fail("frontier contains non-UNSAT final leaf")

    modular = manifest.get("modular_certificates", {})
    hard_certs = manifest.get("hard_root_certificates", {})

    for bits in direct:
        key = "ROOT_" + bits
        cert = modular.get(key)
        if cert is None:
            fail(f"missing direct root certificate {key}")
        state_sha = rescout["cubes"][bits]["cnf_sha256"]
        if cert["cnf_sha256"] != state_sha:
            fail(f"direct root CNF binding mismatch {bits}")
        check_cert_artifact(cert)

    leaves_by_root = defaultdict(list)
    for key, rec in leaves:
        leaves_by_root[rec["root_parent"]].append((key, rec))

    root_modes = {}
    for bits in hard:
        root_cert = hard_certs.get(bits)
        if root_cert is not None:
            state_sha = rescout["cubes"][bits]["cnf_sha256"]
            if root_cert["cnf_sha256"] != state_sha:
                fail(f"hard-root CNF binding mismatch {bits}")
            check_cert_artifact(root_cert)
            root_modes[bits] = "DIRECT_HARD_ROOT"
            continue

        required = leaves_by_root[bits]
        if not required:
            fail(f"hard root has no final leaves {bits}")
        for leaf_key, rec in required:
            cert_key = "LEAF_" + leaf_key
            cert = modular.get(cert_key)
            if cert is None:
                fail(f"missing leaf certificate {cert_key}")
            if cert["cnf_sha256"] != rec["cnf_sha256"]:
                fail(f"leaf CNF binding mismatch {leaf_key}")
            check_cert_artifact(cert)
        root_modes[bits] = f"LEAVES_{len(required)}"

    if len(root_modes) != 24:
        fail("not all hard roots covered")
    if not manifest.get("lemma_coverage_complete"):
        fail("manifest claims lemma coverage incomplete despite reconstructed coverage")

    direct_mode_count = sum(mode == "DIRECT_HARD_ROOT" for mode in root_modes.values())
    leaf_mode_count = 24 - direct_mode_count
    print(
        "COVERAGE_CHECK_OK mode=LEMMA_CNF roots=512 direct488=488 hard24=24 "
        f"hard_direct={direct_mode_count} hard_by_leaves={leaf_mode_count} eo_groups_used={len(groups)}"
    )


if __name__ == "__main__":
    main()
