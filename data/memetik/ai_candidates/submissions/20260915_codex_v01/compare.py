import argparse
import hashlib
import itertools
import json
import pathlib
import time

import networkx as nx
import numpy as np
import pynauty

from verify import calculate, decode, load_document


def canonical(g):
    adj = {int(i): sorted(int(j) for j in g.neighbors(i)) for i in g.nodes}
    return pynauty.certificate(pynauty.Graph(len(g), adjacency_dict=adj))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--archive")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    start = time.perf_counter()
    graphs, certificates, rows = {}, {}, {}
    document, _, _ = load_document(args.markdown)
    for data in document["candidates"]:
        name = data["candidate_id"]
        g = nx.from_graph6_bytes(data["graph6"].encode("ascii"))
        graphs[name] = g
        certificates[name] = canonical(g)
        a = nx.to_numpy_array(g, nodelist=range(99), dtype=np.int64)
        r = (a @ a + a - 2)[np.triu_indices(99, 1)]
        values, counts = np.unique(r, return_counts=True)
        mx = int(np.abs(r).max())
        scores = {"W": int(np.count_nonzero(r)), "L1": int(np.abs(r).sum()),
                  "F": int((r * r).sum()), "Linf": mx,
                  "Nmax": int(np.count_nonzero(np.abs(r) == mx)),
                  "lambda_bad_edges": int(np.count_nonzero(
                      ((a @ a) != 1) & (a == 1))) // 2,
                  "residual_histogram": {str(v): int(c) for v, c in zip(values, counts)}}
        arm = data["arm"]
        frame = data["omega_frame"]
        hard, direct = calculate(decode(data["graph6"]), arm, frame)
        assert scores == direct == data["scores"]
        assert hard["regular_14"]
        assert hard["omega_frame_condition" if arm == "omega" else "lambda_edge_condition"]
        assert hashlib.sha256((data["graph6"] + "\n").encode()).hexdigest() == data["graph6_sha256"]
        pg = pynauty.Graph(99, adjacency_dict={i: sorted(g[i]) for i in g})
        aut = pynauty.autgrp(pg)
        rows[name] = {
            "hard_checks": hard, "scores": scores, "connected": nx.is_connected(g),
            "automorphism_order_mantissa": aut[1], "automorphism_order_exponent": aut[2],
            "vertex_orbits": aut[4], "duplicates": [], "archive_duplicates": []}
    for i, j in itertools.combinations(graphs, 2):
        if certificates[i] == certificates[j]:
            rows[i]["duplicates"].append(j)
            rows[j]["duplicates"].append(i)
    archive = []
    if args.archive:
        for path in sorted(pathlib.Path(args.archive).rglob("*.g6")):
            for line_number, line in enumerate(path.read_bytes().splitlines(), 1):
                if not line:
                    continue
                label = str(path.relative_to(args.archive)) + ":" + str(line_number)
                g = nx.from_graph6_bytes(line)
                item = {"path": label, "order": len(g),
                        "sha256": hashlib.sha256(line + b"\n").hexdigest()}
                if len(g) == 99:
                    cert = canonical(g)
                    for name in graphs:
                        if certificates[name] == cert:
                            rows[name]["archive_duplicates"].append(label)
                archive.append(item)
    result = {"candidates": rows, "archive_scope": archive,
              "wall_seconds": time.perf_counter() - start,
              "networkx_version": nx.__version__, "pynauty_version": pynauty.__version__}
    pathlib.Path(args.out).write_text(json.dumps(result, indent=4))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
