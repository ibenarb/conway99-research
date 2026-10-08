"""Bind an exact regenerated N1 CNF to task assumptions and edge mapping."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import n1_check as direct

ENCODER_SHA256 = "3d041ddde9b01692fa18ed0c7d07fb8f8b0b16ddbd65c6c62c6305c0e6aa4d6a"
ENCODER_COMMIT = "55f978b28f6f4b4e8648e24a26c453d80ed0834f"


def encoder():
    path = Path(__file__).resolve().parents[1] / "root8105_n1" / "model.py"
    if direct.digest(path) != ENCODER_SHA256:
        raise ValueError("pinned encoder changed")
    loader = importlib.util.spec_from_file_location("n1_pinned_encoder", path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def prepare(spec, directory):
    direct.geometry(spec)
    module = encoder()
    cnf, variables, metadata = module.encode(
        spec["m"], {int(k): set(v) for k, v in spec["rows"].items()},
        spec["matching"], spec["anchor"])
    directory.mkdir(exist_ok=False)
    cnf.to_file(str(directory / "input.cnf"))
    binding = {"schema": "ROOT8105_N1_BINDING_1", "spec": spec,
               "encoder_commit": ENCODER_COMMIT, "encoder_sha256": ENCODER_SHA256,
               "cnf_sha256": direct.digest(directory / "input.cnf"),
               "edge_map": [[u, v, lit] for (u, v), lit in variables.items()],
               "metadata": metadata, "catalog_identity_checked": False}
    direct.validate_binding(binding, directory / "input.cnf")
    (directory / "binding.json").write_text(json.dumps(binding, indent=2) + "\n")
    return binding


def verify_regeneration(binding, cnf):
    direct.validate_binding(binding, cnf)
    if binding["encoder_sha256"] != ENCODER_SHA256 or binding["encoder_commit"] != ENCODER_COMMIT:
        raise ValueError("encoder identity")
    with tempfile.TemporaryDirectory(prefix="n1-bind-") as temp:
        expected = prepare(binding["spec"], Path(temp) / "expected")
        if binding != expected:
            raise ValueError("binding does not match pinned encoder")
        if direct.digest(cnf) != expected["cnf_sha256"]:
            raise ValueError("CNF differs from regenerated input")
    return {"status": "EXACT_N1_BINDING_VERIFIED",
            "cnf_sha256": binding["cnf_sha256"], "encoder_sha256": ENCODER_SHA256}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    a = parser.parse_args()
    prepare(direct.load(a.spec), a.output.resolve())


if __name__ == "__main__":
    main()
