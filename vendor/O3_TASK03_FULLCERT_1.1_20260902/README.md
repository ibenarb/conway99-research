# Vendored O3 Task03 FULLCERT qsat source

This directory is a **content-exact export** of

`O3_TASK03_FULLCERT_1.1_20260902/SOURCE/context/qsat`

from the immutable local FULLCERT freeze.

It is vendored for external reproducibility and review. Do not edit these files in place; any future derived implementation should live under `src/` and cite this snapshot by hash.

## Provenance

The user-created transfer archive was

`O3_TASK03_FULLCERT_qsat_source_20260902.tar.gz`

with SHA256

`85d331f6b45c79d166d45e784f8ea7dd722becceae73f2ff2f474b56f260e7b0`.

The production encoder `qsat/encode.py` has SHA256

`131cf8aea1fbf6eeb76e363357b55498d084f109ec93b42c51d0d0c6abdbe6f1`.

All ten Python files were parsed successfully with Python `ast.parse` before import. Git blob SHA-1 values for all ten files were independently compared with the source snapshot and matched exactly. See `PROVENANCE.json` for content SHA256 values and byte counts.

## Relation to the Breadth scout

`src/breadth1/o3_ab_matched_scout_runner.py` historically loaded this encoder from the local FULLCERT freeze. External reruns may instead pass

```text
--legacy-encode vendor/O3_TASK03_FULLCERT_1.1_20260902/qsat/encode.py
```

The historical `encode.py` contains tau=6-specific helper functions, but the Breadth A/B build calls `legacy_encode.cnf_from_core(..., lemma_triangle_eo=False)` and adds the tau-generic C3 Exact-One layer in `src/breadth1/o3_abc_encode.py`. Therefore the hard-coded historical triangle helper is not used in the all-tau Breadth experiment.
