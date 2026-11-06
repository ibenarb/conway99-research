# Independent boundary-coverage certificate

Run `python verify_witness_stdlib.py` in this directory with ordinary Python (do not use `-O`, as checks use assertions). No third-party packages are required. It writes independent_witness_receipt.json and prints PASS after checking the matrix contract, group and rejection of the whole orbit.

The compressed setup contains the original ordered pools and declared group extracted from the pinned upstream preparation at d3ac3b573e8b824609398af879b6c62b9aaceb39 (external class 0). It is input data, not a proof of completeness of upstream pool generation. The checker independently validates the concrete boundary and full contract preservation of the supplied group. The witness file contains only the three fields consumed by the checker; all images are recomputed.

See [the audit](../../docs/c2/BOUNDARY_COVERAGE_AUDIT_2026-11-06.md). This certificate establishes a boundary-selection coverage defect, not a full SAT witness or a disproof of mathematical UNSAT.
