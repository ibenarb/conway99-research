"""Targeted science, generator, checkpoint and real-process CPU controls."""
from fractions import Fraction
import json
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from campaign import BASE_CONFIG, TRAINING, as_candidate, pick
from common import ROOT, atomic, checked, core, cpu, sha
from evaluate import holm, sign_test, evaluate, export
from generate import cover, lift, structure
from prepare import registry, jobs
from runtime import HERE, THREAD_ENV, read
from search import candidate, escape_allowed, fresh_costs, key, select


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = registry()["entries"]
        cls.original = {e["id"]: as_candidate(e) for e in cls.entries if not e["control_only"]}

    def test_generator_reproduction(self):
        rows, details = cover(203, 5)
        self.assertIsNotNone(rows)
        reference = (ROOT / "data/memetik/ai_candidates/accepted/omega/codex_v01_c02.g6").read_text().strip()
        self.assertEqual(core.encode_g6(rows), reference)
        checked(reference, "omega")
        source = read(ROOT / "data/memetik/ai_candidates/submissions/20260915_codex_v01/submission.json")
        item = next(x for x in source["candidates"] if x["candidate_id"] == "C08")
        rows, details = lift(int(item["seed"]), 5)
        self.assertEqual(core.encode_g6(rows), item["graph6"])
        checked(item["graph6"], "lambda")
        self.assertTrue(structure(rows, "Z33_lift"))

    def test_frozen_selection_has_no_clones_or_training(self):
        pool = [as_candidate(e) for e in self.entries if e["arm"] == "lambda"]
        for seed in range(20260920, 20260928):
            rows, _ = lift(seed, 2)
            pool.append(candidate(rows, "lambda", "Z33_lift", f"new-{seed}", None, fresh_costs()))
        chosen = pick(pool, "lambda", TRAINING["lambda"])
        self.assertEqual(len({p["class"] for p in chosen}), 16)
        self.assertFalse({p["line"] for p in chosen} & set(TRAINING["lambda"]))
        self.assertIn("hog57338", {p["line"] for p in chosen})
        self.assertIn("lambda_Linf2_00", {p["line"] for p in chosen})
        self.assertEqual({p["family"] for p in chosen}, {"HoG", "Z33_lift", "triangle_packing"})
        selected = select(chosen, [], "lambda", "Linf", random.Random(1), 0,
                          sorted({p["family"] for p in chosen}))
        self.assertEqual(len(selected), 16)
        self.assertEqual({p["family"] for p in selected}, {p["family"] for p in chosen})

    def test_anchor_and_lexicographic_escape(self):
        anchor = {"F": 1000, "L1": 800, "Linf": 4, "Nmax": 20}
        self.assertFalse(escape_allowed(dict(anchor, F=1101), anchor, anchor, "F", 1000, 2))
        self.assertTrue(escape_allowed(dict(anchor, F=1100), anchor, anchor, "F", 1000, 2))
        self.assertFalse(escape_allowed(dict(anchor, Nmax=23), anchor, anchor, "Linf", 0, 0))
        self.assertFalse(escape_allowed(dict(anchor, Linf=5), anchor, anchor, "Linf", 0, 0))
        self.assertTrue(escape_allowed(dict(anchor, Linf=3, Nmax=400, L1=9000), anchor, anchor, "Linf", 0, 0))
        self.assertNotEqual(key(anchor, "Linf"), key(dict(anchor, L1=802), "Linf"))

    def test_exact_sign_holm(self):
        self.assertEqual(sign_test(12, 0), Fraction(1, 4096))
        self.assertEqual(sign_test(0, 0), 1)
        self.assertEqual(sign_test(3, 0), Fraction(1, 8))
        adjusted = holm([Fraction(1, 4096)]*6)
        self.assertEqual(adjusted, [Fraction(6, 4096)]*6)
        self.assertEqual(holm([Fraction(1, 8)]*6), [Fraction(3, 4)]*6)

    def test_synthetic_export_and_missing_pair_rejection(self):
        # Synthetic CPU receipts test the audit, NOT a measured experiment.
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            manifest = jobs()
            atomic(directory / "confirmation.json", manifest)
            for task in manifest["jobs"]:
                root = directory / "tasks" / task["id"]
                root.mkdir(parents=True)
                parent = self.original["hog57338" if task["arm"] == "lambda" else "codex_v01_c02"]
                atomic(root / "task.json", task)
                atomic(root / "result.json", {"status": "COMPLETE", "best": parent,
                                              "curves": [{"cpu": 0, "scores": parent["scores"]}]})
                atomic(root / "receipt.json", {"exit_code": 0, "cpu_seconds": 3600,
                    "task_sha256": sha((root / "task.json").read_bytes()),
                    "result_sha256": sha((root / "result.json").read_bytes())})
            report = evaluate(directory)
            self.assertEqual(report["status"], "PAIRED_COMPARISON_VERIFIED")
            self.assertTrue(all(d["ties"] == 12 and d["recommended_variant"] == "A0" for d in report["decisions"]))
            path = Path(export(directory))
            self.assertTrue(path.exists())
            self.assertTrue(path.with_suffix(path.suffix+".sha256").exists())
            (root / "result.json").unlink()
            self.assertEqual(evaluate(directory)["status"], "INCOMPLETE_OR_INVALID")

    def test_real_worker_pause_resume_cpu_receipt(self):
        pool = [as_candidate(e) for e in self.entries if e["arm"] == "lambda"]
        for seed in range(20260920, 20260928):
            rows, _ = lift(seed, 2)
            pool.append(candidate(rows, "lambda", "Z33_lift", str(seed), None, fresh_costs()))
        founders = pick(pool, "lambda", [])
        config = dict(BASE_CONFIG, perturb_cpu=0.01, descent_cpu=0.03,
                      thresholds={"lambda": {"L1": 10, "F": 20}})
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            task = {"id": "control", "kind": "compare", "arm": "lambda", "target": "Linf", "variant": "A1",
                    "seed": 1123, "worker_cpu_seconds": 3, "config": config, "founders": founders}
            atomic(directory / "task.json", task)

            def start():
                return subprocess.Popen([sys.executable, str(HERE / "worker.py"), str(directory)],
                                        env={**os.environ, **THREAD_ENV}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            def reap(proc):
                _, status, usage = os.wait4(proc.pid, 0)
                proc.returncode = os.waitstatus_to_exitcode(status)
                error = proc.stderr.read().decode()
                proc.stderr.close()
                proc.stdout.close()
                self.assertEqual(proc.returncode, 0, error)
                return usage.ru_utime+usage.ru_stime

            first = start()
            time.sleep(0.3)
            first.send_signal(signal.SIGTERM)
            spent = reap(first)
            self.assertEqual(read(directory / "result.json")["status"], "PAUSED")
            self.assertGreater(spent, 0)
            before = read(directory / "checkpoint.json")["state"]
            atomic(directory / "receipt.json", {"cpu_seconds": spent})
            second = start()
            spent2 = reap(second)
            after = read(directory / "checkpoint.json")["state"]
            output = read(directory / "result.json")
            self.assertEqual(output["status"], "COMPLETE")
            self.assertGreaterEqual(after["episodes"], before["episodes"])
            self.assertGreaterEqual(spent+spent2, 2.95)
            self.assertLess(spent+spent2, 3.5)
            self.assertTrue(all(p["cpu"] <= 3 for p in output["curves"]))
            self.assertTrue(all(len(m) <= 128 for m in after["memory"].values()))
            checked(output["best"]["graph6"], "lambda")


if __name__ == "__main__":
    unittest.main()
