"""Independent standard-library verifier for the embedded candidate JSON."""
import argparse
import collections
import hashlib
import itertools
import json
import math
import re
import sys


def decode(g):
    if not isinstance(g, str) or not g or any(not 63 <= ord(c) <= 126 for c in g):
        raise ValueError("Invalid graph6 bytes/header/whitespace")
    v = [ord(c) - 63 for c in g]
    if v[0] != 63:
        n, start = v[0], 1
    elif len(v) >= 4 and v[1] != 63:
        n, start = (v[1] << 12) + (v[2] << 6) + v[3], 4
        if n < 63:
            raise ValueError("Noncanonical graph6 order")
    else:
        raise ValueError("Unsupported or malformed graph6 order")
    if n != 99:
        raise ValueError(f"Order {n}, required 99")
    bits = [(x >> b) & 1 for x in v[start:] for b in range(5, -1, -1)]
    count = n * (n - 1) // 2
    if len(v) != start + (count + 5) // 6 or any(bits[count:]):
        raise ValueError("Wrong graph6 length or nonzero padding")
    a = [set() for _ in range(n)]
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos]:
                a[i].add(j)
                a[j].add(i)
            pos += 1
    return a


def calculate(a, arm, frame):
    n = len(a)
    hist = collections.Counter()
    bad = 0
    for i in range(n):
        for j in range(i + 1, n):
            common = len(a[i] & a[j])
            edge = j in a[i]
            hist[common + int(edge) - 2] += 1
            bad += int(edge and common != 1)
    linf = max(map(abs, hist))
    scores = {
        "W": sum(v for k, v in hist.items() if k),
        "L1": sum(abs(k) * v for k, v in hist.items()),
        "F": sum(k * k * v for k, v in hist.items()),
        "Linf": linf,
        "Nmax": sum(v for k, v in hist.items() if abs(k) == linf),
        "lambda_bad_edges": bad,
        "residual_histogram": {str(k): hist[k] for k in sorted(hist)}
    }
    hard = {
        "order_99": n == 99,
        "simple_undirected": all(i not in a[i] and all(i in a[j] for j in a[i])
                                 for i in range(n)),
        "regular_14": all(len(s) == 14 for s in a),
        "lambda_edge_condition": bad == 0,
        "omega_frame_condition": None
    }
    if arm == "omega" or frame is not None:
        if not isinstance(frame, dict) or set(frame) != {"canonical_to_graph6"}:
            raise ValueError("Missing or malformed omega frame")
        q = frame["canonical_to_graph6"]
        if (not isinstance(q, list) or any(type(x) is not int for x in q)
                or sorted(q) != list(range(99))):
            raise ValueError("Frame is not a permutation of 0,...,98")
        inv = {v: k for k, v in enumerate(q)}
        b = [{inv[v] for v in a[q[i]]} for i in range(99)]
        pairs = [(i, j) for i in range(14) for j in range(i + 1, 14)
                 if j != (i + 7) % 14]
        ok = b[0] == set(range(1, 15))
        for i in range(14):
            expected = {0, 1 + (i + 7) % 14}
            expected.update(15 + k for k, pair in enumerate(pairs) if i in pair)
            ok = ok and b[i + 1] == expected
        for j, pair in enumerate(pairs):
            ok = ok and b[j + 15] & set(range(15)) == {x + 1 for x in pair}
            outer = {v - 15 for v in b[j + 15] if v >= 15}
            ok = ok and len(outer) == 12
            for label in range(14):
                actual = sum(label in pairs[k] for k in outer)
                required = 2 - int(label in pair) - int((label + 7) % 14 in pair)
                ok = ok and actual == required
        hard["omega_frame_condition"] = bool(ok)
    return hard, scores


def verify(c, families, generators):
    fail, missing = [], []
    if not isinstance(c, dict):
        return "FAIL", ["Candidate is not an object"]
    fields = {
        "candidate_id", "family_id", "arm", "status", "graph6", "graph6_sha256",
        "seed", "parents", "generator_id", "generator_args", "hard_checks",
        "scores", "omega_frame", "isomorphism", "runtime", "notes"
    }
    missing.extend("Missing field: " + x for x in sorted(fields - set(c)))
    for key in ("candidate_id", "family_id", "generator_id", "notes"):
        if key in c and (not isinstance(c[key], str) or not c[key]):
            fail.append("Invalid string: " + key)
    for key, allowed in [("arm", {"lambda", "omega"}),
                         ("status", {"generated_unverified", "self_verified"})]:
        if key in c and (not isinstance(c[key], str) or c[key] not in allowed):
            fail.append("Invalid " + key)
    if c.get("family_id") is not None and c["family_id"] not in families:
        fail.append("Unknown family reference")
    if c.get("generator_id") is not None and c["generator_id"] not in generators:
        fail.append("Unknown generator reference")
    if c.get("seed") is not None and not isinstance(c["seed"], str):
        fail.append("Seed must be string or null")
    for key in ("parents", "generator_args"):
        if key in c and (not isinstance(c[key], list)
                         or any(not isinstance(v, str) for v in c[key])):
            fail.append("Invalid list: " + key)
    iso = c.get("isomorphism")
    if not isinstance(iso, dict):
        missing.append("Isomorphism object absent")
    else:
        keys = {"method", "within_submission", "against_project_archive", "duplicate_of"}
        missing.extend("Isomorphism field absent: " + x for x in keys - set(iso))
        if iso.get("method") is not None and not isinstance(iso["method"], str):
            fail.append("Invalid isomorphism method")
        for key in ("within_submission", "against_project_archive"):
            if key in iso and iso[key] not in ("not_checked", "partial", "complete"):
                fail.append("Invalid isomorphism scope")
        if "duplicate_of" in iso and (not isinstance(iso["duplicate_of"], list)
                or any(not isinstance(v, str) for v in iso["duplicate_of"])):
            fail.append("Invalid duplicate list")
    runtime = c.get("runtime")
    if not isinstance(runtime, dict):
        missing.append("Runtime object absent")
    else:
        for key in ("wall_seconds", "cpu_seconds", "peak_rss_mib", "environment"):
            if key not in runtime:
                missing.append("Runtime field absent: " + key)
            elif key == "environment":
                if runtime[key] is not None and not isinstance(runtime[key], str):
                    fail.append("Invalid runtime environment")
            elif runtime[key] is not None and (type(runtime[key]) not in (int, float)
                    or not math.isfinite(runtime[key]) or runtime[key] < 0):
                fail.append("Invalid runtime number: " + key)
    if c.get("graph6") is None:
        missing.append("Graph data absent")
        return ("FAIL" if fail else "UNVERIFIED"), fail + missing
    try:
        a = decode(c["graph6"])
        if c.get("arm") not in ("lambda", "omega"):
            return ("FAIL" if fail else "UNVERIFIED"), fail + missing
        if c["arm"] == "omega" and c.get("omega_frame") is None:
            missing.append("Required omega frame absent")
            hard, scores = calculate(a, "lambda", None)
        else:
            hard, scores = calculate(a, c["arm"], c.get("omega_frame"))
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        return "FAIL", fail + [str(exc)] + missing
    required = ["order_99", "simple_undirected", "regular_14"]
    required.append("lambda_edge_condition" if c["arm"] == "lambda" else "omega_frame_condition")
    for key in required:
        if hard[key] is False:
            fail.append("Hard condition violated: " + key)
        elif hard[key] is None:
            missing.append("Hard condition open: " + key)
    digest = hashlib.sha256((c["graph6"] + "\n").encode("ascii")).hexdigest()
    if c.get("graph6_sha256") is None:
        missing.append("SHA256 absent")
    elif c["graph6_sha256"] != digest:
        fail.append("SHA256 mismatch")
    reported_hard = c.get("hard_checks")
    if not isinstance(reported_hard, dict):
        missing.append("Hard-check object absent")
    else:
        for key, value in hard.items():
            if key not in reported_hard:
                missing.append("Hard-check field absent: " + key)
                continue
            reported = reported_hard[key]
            if reported is not None and type(reported) is not bool:
                fail.append("Invalid hard-check type: " + key)
            elif reported is not None and value is not None and reported != value:
                fail.append("Hard-check mismatch: " + key)
            elif reported is not None and value is None:
                missing.append("Reported hard check cannot be verified: " + key)
            elif key in required and reported is None and c.get("status") == "self_verified":
                missing.append("Self-verified hard-check flag absent: " + key)
    reported_scores = c.get("scores")
    if not isinstance(reported_scores, dict):
        missing.append("Score object absent")
    else:
        for key, value in scores.items():
            reported = reported_scores.get(key)
            if reported is None:
                missing.append("Score absent: " + key)
            elif key == "residual_histogram":
                if (not isinstance(reported, dict)
                        or any(not isinstance(k, str) or not re.fullmatch(r"-?(0|[1-9][0-9]*)", k)
                               or type(v) is not int or v < 0 for k, v in reported.items())):
                    fail.append("Invalid residual histogram")
                elif reported != value:
                    fail.append("Histogram mismatch")
            elif type(reported) is not int or reported != value:
                fail.append("Score mismatch: " + key)
    return ("FAIL" if fail else "UNVERIFIED" if missing else "PASS"), fail + missing


def load_document(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    blocks = re.findall(r"^\x60{3}json[ \t]*\n(.*?)^\x60{3}[ \t]*$", text, re.M | re.S)
    if len(blocks) != 1:
        raise ValueError(f"Expected exactly one JSON block, found {len(blocks)}")
    def reject(x):
        raise ValueError("Nonfinite JSON constant: " + x)
    def object_pairs(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("Duplicate JSON key: " + k)
            result[k] = v
        return result
    doc = json.loads(blocks[0], parse_constant=reject, object_pairs_hook=object_pairs)
    if not isinstance(doc, dict) or doc.get("schema_version") != "conway99-candidates-1.0":
        raise ValueError("Invalid schema_version")
    if not isinstance(doc.get("submission_id"), str) or not doc["submission_id"]:
        raise ValueError("Missing submission_id")
    if not isinstance(doc.get("candidates"), list):
        raise ValueError("Candidates must be an array")
    families = set(re.findall(r"^### (F[0-9]+)\b", text, re.M))
    generators = set(re.findall(r"^generator_id: (G[0-9]+)\b", text, re.M))
    return doc, families, generators


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown")
    args = parser.parse_args()
    try:
        doc, families, generators = load_document(args.markdown)
    except (ValueError, OSError) as exc:
        print("FAIL document:", exc)
        return 1
    counts = collections.Counter()
    ids = [c.get("candidate_id") for c in doc["candidates"] if isinstance(c, dict)]
    for c in doc["candidates"]:
        try:
            status, reasons = verify(c, families, generators)
        except (TypeError, ValueError, KeyError) as exc:
            status, reasons = "FAIL", ["Malformed schema: " + str(exc)]
        cid = c.get("candidate_id") if isinstance(c, dict) else None
        if cid is not None and ids.count(cid) != 1:
            status, reasons = "FAIL", reasons + ["Duplicate candidate ID"]
        counts[status] += 1
        print(status, cid, "; ".join(reasons) if reasons else "Hard conditions, SHA256 and scores agree")
        iso = c.get("isomorphism") if isinstance(c, dict) else None
        if isinstance(iso, dict):
            print("  Isomorphism: reported only; not rerun by this verifier:",
                  iso.get("within_submission"), iso.get("against_project_archive"))
    print("TOTAL", dict(counts))
    return 1 if counts["FAIL"] else 2 if counts["UNVERIFIED"] else 0


if __name__ == "__main__":
    sys.exit(main())
