"""Complete paired endpoint audit, exact sign/Holm decision and verified export."""
import csv
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import tarfile

from common import atomic, checked, sha
from runtime import read
from search import key


def sign_test(wins, losses):
    n = wins+losses
    return Fraction(sum(math.comb(n, k) for k in range(wins, n+1)), 2**n) if n else Fraction(1)


def holm(probabilities):
    answer = [None]*len(probabilities)
    running = Fraction(0)
    for i, index in enumerate(sorted(range(len(probabilities)), key=lambda k: probabilities[k])):
        running = min(Fraction(1), max(running, (len(probabilities)-i)*probabilities[index]))
        answer[index] = running
    return answer


def practical(pairs, target):
    # Predeclared 0.5% median relative gain. Linf: lower radius, otherwise
    # Nmax relative improvement; final L1 tie-break evaluated only if both tie.
    gains = []
    for a0, a1 in pairs:
        if target != "Linf":
            gains.append((a0[target]-a1[target])/max(1, a0[target]))
        elif a0["Linf"] != a1["Linf"]:
            gains.append((a0["Linf"]-a1["Linf"])/max(1, a0["Linf"]))
        elif a0["Nmax"] != a1["Nmax"]:
            gains.append((a0["Nmax"]-a1["Nmax"])/max(1, a0["Nmax"]))
        else:
            gains.append((a0["L1"]-a1["L1"])/max(1, a0["L1"]))
    return statistics.median(gains)


def evaluate(directory):
    directory = Path(directory)
    manifest = read(directory / "confirmation.json")
    results = {}
    actual_cpu = 0.0
    issues = []
    for task in manifest["jobs"]:
        root = directory / "tasks" / task["id"]
        if not (root / "receipt.json").exists() or not (root / "result.json").exists():
            issues.append(task["id"]+": missing result/CPU receipt")
            continue
        receipt, result = read(root / "receipt.json"), read(root / "result.json")
        if receipt["exit_code"] != 0 or result["status"] != "COMPLETE":
            issues.append(task["id"]+": incomplete")
            continue
        if read(root / "task.json") != task:
            raise ValueError("Task differs from frozen manifest")
        if receipt["task_sha256"] != sha((root / "task.json").read_bytes()) or receipt["result_sha256"] != sha((root / "result.json").read_bytes()):
            raise ValueError("Result/CPU-receipt digest mismatch")
        _, scores = checked(result["best"]["graph6"], task["arm"])
        if scores != result["best"]["scores"]:
            raise ValueError("Endpoint scores differ from independent audit")
        limit = task["worker_cpu_seconds"]
        reserve = result.get("closing_reserve_cpu_seconds", 2.0)
        if receipt["cpu_seconds"] < limit-reserve-0.05 or receipt["cpu_seconds"] > limit:
            issues.append(task["id"]+": CPU endpoint/closing overhead outside tolerance")
        if any(p["cpu"] > limit for p in result["curves"]):
            raise ValueError("Post-budget best value in primary curve")
        if any(key(a["scores"], task["target"]) < key(b["scores"], task["target"])
               for a, b in zip(result["curves"], result["curves"][1:])):
            raise ValueError("Nonmonotone best curve")
        actual_cpu += receipt["cpu_seconds"]
        results[task["id"]] = result
    if issues:
        return {"status": "INCOMPLETE_OR_INVALID", "issues": issues, "main_campaign_authorized": False}
    decisions, probabilities = [], []
    for arm in ("omega", "lambda"):
        for target in ("L1", "F", "Linf"):
            pairs = [(results[f"{arm}-{target}-{i:02d}-A0"]["best"]["scores"],
                      results[f"{arm}-{target}-{i:02d}-A1"]["best"]["scores"]) for i in range(12)]
            wins = sum(key(b, target) < key(a, target) for a, b in pairs)
            losses = sum(key(b, target) > key(a, target) for a, b in pairs)
            p = sign_test(wins, losses)
            probabilities.append(p)
            decisions.append({"arm": arm, "target": target, "wins_A1": wins, "ties": 12-wins-losses,
                              "losses_A1": losses, "p_exact": str(p), "p": float(p),
                              "median_relative_gain": practical(pairs, target),
                              "paired_scores": [{"A0": a, "A1": b} for a, b in pairs]})
    for decision, adjusted in zip(decisions, holm(probabilities)):
        decision.update(holm_p_exact=str(adjusted), holm_p=float(adjusted),
                        recommended_variant="A1" if adjusted <= Fraction(1, 20)
                        and decision["median_relative_gain"] >= 0.005 else "A0")
    return {"status": "PAIRED_COMPARISON_VERIFIED", "decisions": decisions,
            "nominal_worker_cpu_hours": 144, "actual_worker_cpu_hours": actual_cpu/3600,
            "unused_budget_seconds": 518400-actual_cpu,
            "scope": "Twelve independent paired seeds per arm/target; no universal superiority claim",
            "main_campaign_authorized": False}


def export(directory):
    directory = Path(directory)
    report = evaluate(directory)
    atomic(directory / "evaluation.json", report)
    if report["status"] != "PAIRED_COMPARISON_VERIFIED":
        raise RuntimeError("Cannot export a verified comparison: " + report["status"])
    target = directory / "comparison_verified.tar.gz"
    if target.exists():
        raise FileExistsError("Refuse overwrite of existing export")
    files = [p for name in ("confirmation.json", "founder_split.json", "fingerprint.json", "trained_config.json",
                            "calibration_result.json", "evaluation.json") if (p := directory / name).exists()]
    files += [p for p in (directory / "tasks").glob("*/*.json") if p.name in ("task.json", "result.json", "receipt.json")]
    hashes = {str(p.relative_to(directory)): sha(p.read_bytes()) for p in sorted(files)}
    atomic(directory / "export_manifest.json", hashes)
    files.append(directory / "export_manifest.json")
    partial = target.with_suffix(target.suffix+".partial")
    with partial.open("xb") as raw:
        with tarfile.open(fileobj=raw, mode="w:gz") as archive:
            for p in sorted(files):
                archive.add(p, arcname=str(p.relative_to(directory)), recursive=False)
    with tarfile.open(partial, "r:gz") as archive:
        actual = {m.name: sha(archive.extractfile(m).read()) for m in archive if m.isfile()}
    expected = {**hashes, "export_manifest.json": sha((directory / "export_manifest.json").read_bytes())}
    if actual != expected:
        raise ValueError("Export content verification failed")
    partial.rename(target)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            digest.update(block)
    target.with_suffix(target.suffix+".sha256").write_text(digest.hexdigest()+"  "+target.name+"\n")
    return str(target)
