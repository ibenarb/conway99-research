"""Build pinned native dependencies in a NEW isolated directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

CADICAL = "4198d817d0dcde5b1240eefbff70b555b7df2af9"
DRAT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"


def call(args, cwd):
    subprocess.run(args, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    root = args.destination.resolve()
    root.mkdir(exist_ok=False)
    for name, url, commit in (
        ("cadical", "https://github.com/arminbiere/cadical.git", CADICAL),
        ("drat", "https://github.com/marijnheule/drat-trim.git", DRAT),
    ):
        call(["git", "clone", url, name], root)
        call(["git", "checkout", "--detach", commit], root / name)
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                         cwd=root / name, text=True).strip()
        if actual != commit:
            raise ValueError("source commit mismatch")
    call(["./configure"], root / "cadical")
    call(["make", "-j4"], root / "cadical")
    source = Path(__file__).resolve().parent / "worker.cpp"
    call(["g++", "-std=c++11", "-O2", "-Wall", "-Wextra", "-pthread",
          "-I", str(root / "cadical/src"), str(source),
          str(root / "cadical/build/libcadical.a"),
          "-o", str(root / "n1-worker")], root)
    call(["gcc", "-std=c99", "-O2", str(root / "drat/drat-trim.c"),
          "-o", str(root / "drat-trim")], root)
    receipt = {"cadical_commit": CADICAL, "drat_commit": DRAT,
               "binaries": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                            for name in ("n1-worker", "drat-trim")}}
    (root / "BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
