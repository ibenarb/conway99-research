# Reproducing the bounded controls

The published controller, sensor, C++ sources, test files and row_screen_inputs.json are sufficient for the synthetic controls on Linux with Python3 and g++. Use a fresh directory and run `python3 run_public_controls.py`. Tests deliberately preserve failure artefacts and reject existing output directories instead of deleting or overwriting them.

These tests need no private production input. Test resource sensors are explicitly synthetic; real_pilot.py uses the independent Windows/WSL sensor and requires the locally preserved original case inputs/contracts. The real timing benchmark therefore is not reproducible from the small public files alone. Its input hashes, source/binary context, proof hashes and results are published; complete pilot artefacts remain in the byte-verified local research archive.

The row screen is independently runnable with `python3 screen_rows.py`; it uses only Python's standard library and the supplied62 algebraic records. Its output must agree with PURE_ROW_SCREEN_PORTABLE.json. The reference implementation uses the original specification; provenance binds both and the original catalogue/ledger.

Recorded setup failures: the first V1 fixture generator did not find a mixed SAT/UNSAT model until two symmetry orbits were combined; the initial UNKNOWN test wrapper pointed one directory too shallow after copying into a bundle. Both failed closed, were corrected in fresh directories, and their artefacts remain. The first Windows archive enumeration could not classify a Linux test symlink (WinError1920); no archive was created by that attempt. The archive operation was therefore executed under Linux, excluding test symlinks explicitly. None of these failures changed production or generated a counted exclusion.

The archive snapshot predates this small reproduction entry point and note; Git preserves these additions. Native per-task JSON receipts alone are not importable certificates. No hardware power-loss or adversarial concurrent-filesystem guarantee is claimed.
