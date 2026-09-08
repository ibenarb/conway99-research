# O3 fixed-K3: parallel coverage-exact certification protocol

Date: 2026-09-08

## Purpose

The first exact fixed-K3 quotient run used one monolithic CaDiCaL process. It was intentionally interrupted after 94,938.55 s (26.37 h) with solver exit `-2` (SIGINT). Its root CNF SHA256 is

`b55a21481c2514770af5103a000e4a18bb16723a2d61224ca6afc87c0eeabdd0`.

The interruption is not a mathematical result. It is retained only as a diagnostic showing that a one-thread monolithic LRAT run is operationally unsuitable: it produced a >300 GiB partial proof without a meaningful progress fraction.

The replacement campaign preserves the same root CNF and changes only the search/certification architecture.

## Exact coverage

Let `F` be the root CNF. Choose a deterministic ordered list of unfixed primary variables `x_1,x_2,...`. At initial depth `d`, generate all `2^d` cubes

`C_b = { x_i = b_i : 1 <= i <= d }`, `b in {0,1}^d`.

These cubes are pairwise disjoint and their union is all assignments of `F`. A hard leaf cube `C` at depth `k` is replaced by exactly two children

`C ∧ ¬x_{k+1}` and `C ∧ x_{k+1}`.

Hence every dynamic split is an exact binary partition. Assigning measure `2^{-depth}` to each frontier cube gives an exact invariant: the total frontier measure is always 1. The reported `coverage` is the sum of the measures of leaves that have completed the full certification chain.

## Split variables

Only the 992 primary `S`/`L` variables are eligible. Primary variables fixed by root unit clauses are removed. The remaining variables are ranked deterministically by occurrence count in the root CNF, with variable number as tie-breaker. The chosen sequence and root hash are stored in `split_vars.json`.

This ranking is a search heuristic only. Correctness and completeness do not depend on it.

## Worker policy

The campaign uses 21 parallel CaDiCaL solver workers plus one serial checker lane, keeping project compute at at most 22 active compute lanes on the 24-thread Ryzen host.

A leaf receives a bounded solver quantum (default 180 s). Timeout is not interpreted as a logical result: the partial proof is deleted and the leaf is replaced by its two exact children. An UNSAT leaf whose LRAT proof exceeds the configured Cake-friendly proof cap (default 1.0 GiB) is treated the same way: its already-known UNSAT status is deliberately not used, and the cube is subdivided so that final evidence remains independently Cake-checkable on available RAM.

## Accepted leaf statuses

A leaf is counted as `CERTIFIED` only after all of the following:

1. CaDiCaL exits 20 on the exact leaf CNF and produces LRAT.
2. `lrat-check` exits 0 on that leaf CNF/proof pair.
3. `cake_lpr` exits 0.
4. Cake stdout contains the positive verdict `s VERIFIED UNSAT`.
5. CNF and proof hashes are recorded.

Only then is the raw LRAT gzip-compressed; the compressed hash and size are also recorded. The leaf CNF may then be removed because it is reconstructed exactly from the immutable root CNF plus the cube literal list stored in the certificate.

A SAT result is accepted only if the witness independently reconstructs a 35x35 quotient satisfying row degrees, orbit-balance equations, and all quotient matrix equations. Such a result ends the exclusion campaign and means the fixed-K3 quotient cannot be excluded at this layer.

## Completion criterion

`CAMPAIGN_PASS` is emitted only when the exact certified frontier measure equals 1. Equivalently, every branch of the binary coverage tree ends in an LRAT+Cake certified UNSAT leaf. Therefore the root fixed-K3 quotient CNF is UNSAT.

The controller writes `state.json` throughout and is designed to resume interrupted work without treating interrupted solver attempts as evidence.

## Progress reporting

Every 10 minutes the controller reports elapsed wall time, exact certified coverage percentage, numbers of active/pending/checking leaves, split count, maximum frontier depth, free disk, and a weighted-throughput ETA when enough certified-leaf history exists. The ETA is explicitly heuristic; the coverage percentage itself is exact.
