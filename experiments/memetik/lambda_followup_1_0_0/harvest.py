"""Read-only finite archive harvest; no mutation of frozen record starters."""
import boot
from util import *
from search import key
from kernel import Scorer, catalogue
import sqlite3

class End(Exception):
    pass

class FoundSolution(Exception):
    pass

def save_solution(run, graph, scores, origin):
    if scores["F"] != 0:
        return
    if checked(graph, "lambda")[1] != scores:
        raise RuntimeError("False harvest solution")
    payload = {"candidate": {"graph6": graph, "scores": scores},
               "origin": origin, "graph6_sha256": sha(graph.encode())}
    atomic(run / "SOLUTION.json", payload)
    atomic(run / "SOLUTION_BACKUP.json", payload)
    raise FoundSolution()

class Guard:
    def __init__(self, deadline):
        self.deadline = deadline
    def check(self):
        if abort_requested() or own_cpu() >= self.deadline:
            raise End()

def harvest(run, ceiling):
    plan = read(run / "plan.json")
    source = Path(plan["source"])
    guard = Guard(own_cpu() + ceiling - 8)
    source_lock = lock(source / "controller.lock", create=False)
    report = {"status": "INCOMPLETE", "databases_completed": [], "rows_seen": 0,
              "graphs_checked": 0, "descents": [], "records": {}, "scope": "OBSERVED only",
              "record_bank_modified": False, "depth2_scope": "not attempted unless separately recorded"}
    seen = {}
    try:
        original = read(source / "manifest.json")
        if file_sha(source / "manifest.json") != plan["source_manifest_sha256"]:
            raise RuntimeError("Original manifest changed")
        if any((source / "tasks").glob("*/active.json")):
            raise RuntimeError("Source is active")
        expected = read(boot.HERE / "ORIGINAL_RECEIPTS.json")
        for task in original["jobs"]:
            guard.check()
            jid = task["id"]
            d = source / "tasks" / jid
            if read(d / "receipt.json") != expected[jid] or file_sha(d / "archive.sqlite") != expected[jid]["archive_sha256"]:
                raise RuntimeError("Archive receipt differs: " + jid)
            sqlite_frozen(d / "archive.sqlite")
            db = sqlite3.connect((d / "archive.sqlite").resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
            try:
                for target, cpu, value, role in db.execute("SELECT target,cpu,value,role FROM records WHERE role='OBSERVED' ORDER BY id"):
                    guard.check()
                    report["rows_seen"] += 1
                    item = json.loads(value)
                    graph = item["graph6"]
                    h = sha(graph.encode())
                    if h not in seen:
                        rows, scores = checked(graph, "lambda")
                        if scores != item["scores"] or core.canonical(rows) != item["class"]:
                            raise RuntimeError("Invalid archive record")
                        save_solution(run, graph, scores, "original OBSERVED archive")
                        seen[h] = {"candidate": item, "targets": [], "origins": []}
                        report["graphs_checked"] += 1
                    seen[h]["origins"].append({"job": jid, "cpu": cpu, "role": role, "target": target})
                    if target not in seen[h]["targets"]:
                        seen[h]["targets"].append(target)
                report["databases_completed"].append(jid)
            finally:
                db.close()
        for h, info in sorted(seen.items()):
            for target in sorted(info["targets"]):
                guard.check()
                rows = core.decode_g6(info["candidate"]["graph6"])
                steps = []
                complete = False
                try:
                    while True:
                        guard.check()
                        scorer = Scorer(rows)
                        better = []
                        count = 0
                        for name, move in catalogue(rows, True, guard):
                            child, scores = scorer.evaluate(move)
                            count += 1
                            if key(scores, target) < key(scorer.scores, target):
                                better.append((key(scores, target), move, name, child, scores))
                        if not better:
                            complete = True
                            break
                        _, move, name, rows, scores = min(better, key=lambda v: (v[0], v[1]))
                        graph = core.encode_g6(rows)
                        if checked(graph, "lambda")[1] != scores:
                            raise RuntimeError("Harvest incremental mismatch")
                        steps.append({"operator": name, "move": move, "graph6": graph, "scores": scores})
                        save_solution(run, graph, scores, "harvest strict descent")
                    final = core.encode_g6(rows)
                finally:
                    final = core.encode_g6(rows)
                    report["descents"].append({"source": h, "target": target, "steps": steps,
                        "graph6": final, "scores": checked(final, "lambda")[1],
                        "status": "LOCAL_MIN_EXACT_APC" if complete else "INCOMPLETE"})
        pool = {}
        for entry in report["descents"]:
            if entry["target"] == "W" and entry["status"] == "LOCAL_MIN_EXACT_APC":
                pool.setdefault(entry["graph6"], entry)
        candidates = sorted(pool.values(), key=lambda e: (key(e["scores"], "W"), sha(e["graph6"].encode())))[:10]
        report["depth2"] = []
        report["depth2_scope"] = "Up to ten best distinct labelled W descent endpoints; project catalogue"
        for entry in candidates:
            guard.check()
            rows = core.decode_g6(entry["graph6"])
            base = Scorer(rows)
            detail = {"source_graph6_sha256": sha(entry["graph6"].encode()), "sequences": 0,
                      "status": "INCOMPLETE", "best": None}
            report["depth2"].append(detail)
            for name1, move1 in catalogue(rows, True, guard):
                middle, score1 = base.evaluate(move1)
                next_scorer = Scorer(middle)
                for name2, move2 in catalogue(middle, True, guard):
                    child, scores = next_scorer.evaluate(move2)
                    detail["sequences"] += 1
                    if key(scores, "W") < key(base.scores, "W") and (
                            detail["best"] is None or key(scores, "W") < key(detail["best"]["scores"], "W")):
                        graph = core.encode_g6(child)
                        if checked(graph, "lambda")[1] != scores:
                            raise RuntimeError("Depth2 witness invalid")
                        save_solution(run, graph, scores, "harvest depth2")
                        detail["best"] = {"graph6": graph, "scores": scores,
                                          "moves": [[name1, move1], [name2, move2]], "middle_scores": score1}
            detail["status"] = "COMPLETE"
        report["status"] = "OBSERVED_READ_DESCENTS_AND_SELECTED_DEPTH2_COMPLETE"
    except FoundSolution:
        report["status"] = "VERIFIED_SOLUTION"
    except End:
        report["status"] = "INCOMPLETE_CPU_ALLOWANCE"
    finally:
        source_lock.close()
        report["records"] = seen
        atomic(run / "HARVEST.json", report)
    return {k: v for k, v in report.items() if k not in ("records", "descents")}
