"""Targeted controls for new intake, host guard and changed Omega generation."""
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from common import ROOT, core, checked
import moves
import prepare
import resources


class Controls(unittest.TestCase):
    def test_budget_and_pairing(self):
        manifest = prepare.jobs()
        self.assertEqual(len(manifest["jobs"]), 144)
        self.assertEqual(manifest["total_worker_cpu_seconds"], 518400)
        self.assertFalse(manifest["launch_enabled"])
        for a, b in zip(manifest["jobs"][::2], manifest["jobs"][1::2]):
            self.assertEqual(a["seed"], b["seed"])
            self.assertEqual(a["arm"], b["arm"])
            self.assertEqual(a["target"], b["target"])
            self.assertEqual((a["variant"], b["variant"]), ("A0", "A1"))
        self.assertEqual(len({j["seed"] for j in manifest["jobs"]}), 9)

    def test_physical_full_despite_virtual_free(self):
        with patch.object(resources.shutil, "disk_usage") as disk, patch.object(resources, "memory", return_value={"MemAvailable": 40*resources.GIB}):
            disk.return_value.free = 900*resources.GIB
            report = resources.snapshot("/", host_probe=lambda: {"physical_free_bytes": resources.GIB})
        self.assertFalse(report["may_launch"])
        self.assertIn("WINDOWS_PHYSICAL_DISK_RESERVE", report["hazards"])

    def test_missing_host_probe_blocks(self):
        def failed():
            raise subprocess.TimeoutExpired("powershell", 20)
        report = resources.snapshot("/", host_probe=failed)
        self.assertFalse(report["may_launch"])
        self.assertIn("RESOURCE_PROBE_FAILED", report["hazards"])

    def test_intake(self):
        registry = prepare.registry()
        self.assertEqual(registry["unique_eligible_by_arm"], {"omega": 17, "lambda": 12})
        b = next(x for x in registry["entries"] if x["id"] == "B_W2080")
        self.assertEqual(b["scores"]["W"], 2080)
        self.assertEqual(next(x for x in registry["entries"] if x["id"] == "claude_v01_b")["family"], "Z14")
        self.assertFalse(registry["selection_frozen"])

    def test_changed_generator_matches_reference_and_updates(self):
        rows = core.decode_g6((ROOT / "data/memetic_v2/reference/B_maple_20260829.g6").read_text())
        before = set(moves.reference.omega_moves(rows, "4x4", random.Random(9)))
        self.assertEqual(set(moves.omega_moves(rows, "4x4", random.Random(13))), before)
        self.assertTrue(before)
        child = core.apply_move(rows, sorted(before)[0])
        checked(core.encode_g6(child), "omega")
        self.assertEqual(set(moves.omega_moves(child, "4x4")), set(moves.reference.omega_moves(child, "4x4")))
        self.assertNotEqual(before, set(moves.omega_moves(child, "4x4")))

    def test_masks_against_reference_formula(self):
        rows = core.decode_g6((ROOT / "data/memetik/ai_candidates/accepted/omega/codex_v01_c02.g6").read_text())
        vectors = moves.catalogue(4)
        self.assertEqual(len(vectors), 2121)
        for x in vectors[::31]:
            expected = {}
            for v in range(84):
                if v in {u for u, s in x}:
                    continue
                required = [(-1 if rows[u+15] & (1 << (v+15)) else 1)*s for u, s in x]
                if len(set(required)) == 1:
                    expected[v] = required[0]
            self.assertEqual(moves.compatible(rows, x), expected)


if __name__ == "__main__":
    unittest.main()
