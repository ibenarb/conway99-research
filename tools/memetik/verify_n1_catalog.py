"""Verify only archived root 210/6682 class zero; never invoke a SAT solver."""
import argparse
import copy
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import resource
import sys
import tarfile
import tempfile
import time

BASE = "bd0e5f301e02de2fe6180a88bb00d5259caaedb6"
ROOTS = "experiments/memetik/root8105_review_followup_1_0_1/reference/roots.tsv"
ARCHIVE = "docs/augmentation/root8105_n1_20261006/CLASSES.tar.xz"
RECEIPT = "docs/augmentation/root8105_n1_20261006/CLASSES_RECEIPT.json"
SELECTED = "docs/augmentation/root8105_early_diagnostic_20261006/SELECTED_PATHS.json.gz"
PINS = {
    SELECTED: "807a7af96b1909eaf28901345cb3756b6a904b63173196ad9b5a13fe23cddfef",
    ROOTS: "c525d03be144a7493c3239340c6263dcb8a29b5521e5d3b152ce43afe90cac41",
    ARCHIVE: "7313fa8b2e95e617a261a4269502f03e9843d651329490f3795603459a30a601",
    RECEIPT: "97b9462339a22b61d4d4f72ceac375dfff610bbedfdd423b5610e6b51d93a573",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def root_records(data):
    labels = [(i, j) for i in range(14) for j in range(i+1, 14) if j-i != 7]
    records = {}
    for line in data.decode().splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        rid = int(fields[0])
        require(rid not in records, "duplicate root id")
        neighbors = [labels.index(tuple(map(int, p.split("-")))) for p in fields[3:]]
        require(len(set(neighbors)) == len(neighbors) == 12, "root degree")
        records[rid] = sorted(neighbors)
    require(sorted(records) == list(range(1, 8106)), "root catalogue ids")
    return records


def check_identity(spec, roots, cover):
    require(spec["kind"] == "root-class" and spec["m"] == 7 and spec["anchor"] == 0,
            "task geometry")
    require(spec["root_id"] in (210, 6682), "task root scope")
    require(spec["class_id"] == 0, "task class scope")
    require(spec["rows"] == {"0": roots[spec["root_id"]]}, "catalogue root mismatch")
    classes = [c for c in cover["classes"] if c["id"] == 0]
    require(len(classes) == 1, "class zero identity")
    entry = classes[0]
    require(spec["matching"] == entry["representative"], "catalogue matching mismatch")
    require(entry["representative"] in entry["members"] and
            entry["orbit_size"] == len(entry["members"]), "archived class consistency")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    start = time.process_time()
    repo, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name, expected in PINS.items():
        require(sha((repo/name).read_bytes()) == expected, "source hash: " + name)
    sys.path.insert(0, str(repo/"tools/memetik/root8105_n1_runtime_0_3_0"))
    import bind_n1
    roots = root_records((repo/ROOTS).read_bytes())
    old = json.loads((repo/RECEIPT).read_text())
    selected = json.loads(gzip.decompress((repo/SELECTED).read_bytes()))
    results, negatives = [], []
    with tarfile.open(repo/ARCHIVE) as archive, tempfile.TemporaryDirectory() as temp:
        require(len(archive.getnames()) == len(set(archive.getnames())), "duplicate archive entries")
        require(json.load(archive.extractfile("FINAL_RECEIPT.json")) == old, "receipt mismatch")
        contents = {n: archive.extractfile(n).read() for n in old["files"]}
        for name, data in contents.items():
            require(sha(data) == old["files"][name], "archived hash: " + name)
        for rid in (210, 6682):
            prefix = "r%d_class000" % rid
            cover = json.loads(contents["r%d_coverage.json" % rid])
            report, = [r for r in old["reports"] if r["root_id"] == rid]
            row = hex(sum(1 << v for v in roots[rid]))
            require(report["root_row_hex"] == row, "receipt root row")
            chosen = [r["spec"] for r in selected if r["spec"]["root_id"] == rid]
            require(chosen and all(s["row"] == row for s in chosen), "selected root row")
            require(cover["status"] == "EXHAUSTIVE_MATCHING_COVERAGE_PASS" and
                    cover["class_count"] == report["classes"] == len(cover["classes"]) and
                    cover["raw_count"] == report["raw_matchings"], "coverage receipt")
            entry, = [c for c in cover["classes"] if c["id"] == 0]
            spec = dict(kind="root-class", root_id=rid, class_id=0, m=7, anchor=0,
                        rows={"0": roots[rid]}, matching=entry["representative"])
            check_identity(spec, roots, cover)
            for name in ("root_id", "class_id", "matching"):
                bad = copy.deepcopy(spec)
                bad[name] = ({210: 6682, 6682: 210}[rid] if name == "root_id"
                             else 1 if name == "class_id" else [])
                try:
                    check_identity(bad, roots, cover)
                except ValueError:
                    negatives.append(dict(root_id=rid, changed=name, rejected=True))
                else:
                    raise ValueError("identity mutation accepted")
            binding = bind_n1.prepare(spec, Path(temp)/prefix)
            require((Path(temp)/prefix/"input.cnf").read_bytes() == contents[prefix+".cnf"],
                    "regenerated CNF is not byte identical")
            require(binding["edge_map"] == json.loads(contents[prefix+"_edges.json"]),
                    "edge mapping mismatch")
            require(binding["metadata"] == report["metadata"], "metadata mismatch")
            target = out/(prefix+"_binding.json")
            target.write_bytes((Path(temp)/prefix/"binding.json").read_bytes())
            results.append(dict(root_id=rid, class_id=0, root_row_hex=row,
                binding_file=target.name, binding_sha256=sha(target.read_bytes()),
                cnf_sha256=binding["cnf_sha256"], edge_map_sha256=old["files"][prefix+"_edges.json"],
                coverage_sha256=old["files"]["r%d_coverage.json" % rid],
                catalog_identity_checked=True, cnf_byte_identity=True, edge_map_identity=True,
                full_coverage_reaudited=False, solved=False, root_excluded=False))
    save(out/"CATALOG_RECEIPT.json", dict(schema="N1_CATALOG_IDENTITY_1", status="PASS",
        reference_commit=BASE, source_sha256=PINS | {SELECTED: sha((repo/SELECTED).read_bytes())},
        python_sat=importlib.metadata.version("python-sat"), results=results,
        negative_identity_checks=negatives, rules=["GC-08", "GC-16", "GC-20", "GC-22", "GC-23"],
        process_cpu_s_to_receipt=time.process_time()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        accounting_scope="this verification process before receipt serialization; no solver started"))
    print("PASS: 2 catalogue identities, 2 byte-identical CNFs/maps, 6 rejected identity mutations")


if __name__ == "__main__":
    main()
