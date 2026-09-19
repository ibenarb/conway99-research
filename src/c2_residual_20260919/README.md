# C2 residual 1.0.0

Source package for Office preparation, not a production campaign controller.
Run from the repository/package root. Python assertions must remain enabled.
No dependencies beyond Python standard library; UP additionally needs C++17.

Entry points (choose one task at a time; these are not an automatic sequence):

- Small controls: `python3 src/c2_residual_20260919/check_residual.py --out scratch_controls.json`
- Export all 11 certificates: `python3 src/c2_residual_20260919/residual.py export --out scratch_certificates`
- Generate four variants of one case: `python3 src/c2_residual_20260919/residual.py prepare --certificates scratch_certificates --out scratch_variants --case matching_6`
- Compile UP only: `g++ -O2 -std=c++17 src/c2_residual_20260919/up.cpp -o c2_up`
- Diagnose prepared cases: `python3 src/c2_residual_20260919/check_up.py --binary ./c2_up --variants scratch_variants --certificates scratch_certificates --out scratch_up`

No solver is launched by any command. Office commands are supplied only after
the actual local path/resource probe.

prepare accepts repeated --case and --prefix 0..1722 (default 1722). Without --case,
all eleven cases are generated; do not do so unnecessarily on Office. Streaming
keeps the clause body on disk rather than retaining millions of Python tuples.

Before real SAT scouts, use the Office-specific resource/host guard and explicit
limits. This package intentionally has no copied Ryzen worker settings.
Proof and results: docs/c2_residual_20260919/THEOREM.md and REPORT.md.
