"""Finite review checks; no campaign launch. Uses pinned catalogue, separate score checker."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import sys
import time

def decode(text):
    data = [ord(c) - 63 for c in text]
    assert data[0] == 63 and all(0 <= c < 64 for c in data)
    n = data[1] * 4096 + data[2] * 64 + data[3]
    assert n == 99 and len(data) == 813
    bits = "".join(f"{v:06b}" for v in data[4:])
    adj = [set() for _ in range(n)]
    pos = 0
    for j in range(1, n):
        for i in range(j):
            if bits[pos] == "1":
                adj[i].add(j)
                adj[j].add(i)
            pos += 1
    assert set(bits[pos:]) <= {"0"}
    return adj

def measure(adj):
    assert len(adj) == 99
    assert all(len(a) == 14 and i not in a for i, a in enumerate(adj))
    assert all(i in adj[j] for i, a in enumerate(adj) for j in a)
    hist = Counter()
    for i in range(99):
        for j in range(i):
            cn = len(adj[i].intersection(adj[j]))
            edge = j in adj[i]
            assert not edge or cn == 1
            hist[cn + int(edge) - 2] += 1
    m = max(map(abs, hist))
    return dict(W=sum(v for k, v in hist.items() if k),
                L1=sum(abs(k) * v for k, v in hist.items()),
                F=sum(k * k * v for k, v in hist.items()),
                Linf=m, Nmax=sum(v for k, v in hist.items() if abs(k) == m))

def apply(adj, move):
    out = [set(a) for a in adj]
    for i, j in move[0]:
        assert j in out[i] and i in out[j]
        out[i].remove(j)
        out[j].remove(i)
    for i, j in move[1]:
        assert i != j and j not in out[i] and i not in out[j]
        out[i].add(j)
        out[j].add(i)
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("review", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    start = time.process_time()
    w = json.loads((args.review / "witness_2116_result.json").read_text())
    adj = decode(w["start_graph6"])
    assert measure(adj) == w["start_scores"]
    first = apply(adj, w["step1"]["move"])
    assert measure(first) == w["step1"]["scores"]
    final = apply(first, w["step2"]["move"])
    assert final == decode(w["graph6"])
    assert measure(final) == w["scores"]
    assert apply(first, w["step1"]["move"][::-1]) == adj
    assert apply(final, w["step2"]["move"][::-1]) == first
    seen = {}
    def visit(obj):
        if isinstance(obj, dict):
            if "graph6" in obj and "scores" in obj:
                g = obj["graph6"]
                if g not in seen:
                    seen[g] = measure(decode(g))
                assert seen[g] == {k: obj["scores"][k] for k in seen[g]}
            for v in obj.values():
                visit(v)
        elif isinstance(obj, list):
            for v in obj:
                visit(v)
    for path in args.review.glob("*.json"):
        visit(json.loads(path.read_text()))
    sys.path.insert(0, str(args.repo / "experiments/memetik/lambda_compare_0_2_0"))
    import bootstrap
    from common import core
    from kernel import Scorer, catalogue
    class Guard:
        def check(self):
            if time.process_time() - start > 300:
                raise RuntimeError("Finite diagnostic allowance exhausted: INCOMPLETE")
    guard = Guard()
    counts = {}
    for label, graph, move in (("step1", w["start_graph6"], w["step1"]["move"]),
                               ("step2", core.encode_g6(tuple(sum(1 << v for v in a) for a in first)), w["step2"]["move"])):
        expected = tuple(tuple(tuple(e) for e in part) for part in move)
        found = [name for name, m in catalogue(core.decode_g6(graph), True, guard) if m == expected]
        assert found == [w[label]["operator"]]
        counts[label] = found
    graph = w["graph6"]
    steps = []
    while True:
        rows = core.decode_g6(graph)
        original = decode(graph)
        current = measure(original)
        scorer = Scorer(rows)
        choices = []
        count = 0
        for name, move in catalogue(rows, True, guard):
            child, fast = scorer.evaluate(move)
            exact = measure(apply(original, move))
            assert fast == exact
            count += 1
            if (exact["W"], exact["L1"]) < (current["W"], current["L1"]):
                choices.append(((exact["W"], exact["L1"], move), name, move, child, exact))
        if not choices:
            break
        _, name, move, child, scores = min(choices, key=lambda c: c[0])
        graph = core.encode_g6(child)
        assert measure(decode(graph)) == scores
        steps.append(dict(operator=name, move=move, graph6=graph, scores=scores))
        assert len(steps) < 100
    result = dict(status="PASS", reviewer_two_step_witness_checked=True,
                  intermediate_scores=w["step1"]["scores"], final_scores=w["scores"],
                  inverses_checked=True, catalogue_membership=counts,
                  unique_review_graphs_checked=len(seen), descent_steps=steps,
                  descended_graph6=graph, descended_scores=measure(decode(graph)),
                  final_catalogue_size=count, local_status="LOCAL_MIN_EXACT_APC",
                  catalogue_scope="Pinned project catalogue; score/validity checks independent",
                  original_archive_opened=False, cpu_seconds=time.process_time()-start)
    (args.out / "WITNESS_CHECK.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("descended_graph6","descent_steps")}, indent=2))
    print("descent_steps", len(steps))

if __name__ == "__main__":
    main()
