"""Pinned historical graph kernels; no modification of earlier experiments."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource

ROOT = Path(__file__).resolve().parents[3]
VERSION = "ryzen-compare-0.4.0"
BASE = "c54d4a1369f2f2b6f1289692c5001f49712a91a5"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load("comparison_graph_core", "src/memetic_v2/core.py")
verifier = load("comparison_independent_verifier", "src/memetic_v2/verify.py")


def cpu():
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, value):
    path = Path(path)
    data = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def checked(text, arm):
    rows = core.decode_g6(text)
    core.validate(rows, arm)
    scores = core.metrics(rows)
    independent = verifier.check_graph(text, arm, scores)
    if not independent["hard_valid"]:
        raise ValueError(independent["errors"])
    histogram = {int(k): v for k, v in independent["residual_histogram"].items()}
    maximum = max(map(abs, histogram))
    independent.update(L1=sum(abs(k)*v for k, v in histogram.items()), Linf=maximum,
                       Nmax=sum(v for k, v in histogram.items() if abs(k) == maximum))
    for key in ("W", "L1", "F", "Linf", "Nmax"):
        if scores[key] != independent[key]:
            raise ValueError("Independent score mismatch: " + key)
    return rows, {k: scores[k] for k in ("W", "L1", "F", "Linf", "Nmax")}
