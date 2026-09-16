# C2 counter comparison 1.0.0 — 16 September 2026

Purpose: test a different E3 exact-sum encoding after all eleven matching types remained
open for eight hours. The immutable reference and mathematical matching cover remain.
No extra direct conflict clauses in this release: isolate the encoding change.

Reference: 570171 variables, 1990821 clauses (before 66 matching units).
Variant: 534135 variables, 1921773 clauses (before 66 matching units).
Variant hash: 7c105a67b0f7865f2ceec085ac9e5017213208e657e728381406323052acf3dd.
Balanced truncated bidirectional totalizer; E1/E2 are byte-algorithm-identical.

## Installation and execution

On the existing Debian Ryzen installation, download the pinned release ZIP to a new
source directory under ~/conway99_workspace/c2_counter_ab_v1. Run prepare_ab.py, then
run_matching.py --seconds 1200. Preparation refuses an existing setup/partition directory.
It checks the old matching inputs, source/solver identities, the regenerated variant,
primary mapping, projection controls and four tiny actual solver calls. It does not
start a production solver. The launcher starts the detached controller after preparation.

The controller executes two waves with a barrier:
1. all eleven reference cases, seed 0, 1200 wall seconds each;
2. all eleven totalizer cases, same seed, assumptions and budget.

Maximum eleven workers, roughly 40 minutes search plus preparation/cleanup. Groups
never overlap. Fixed wave order remains a possible thermal/time-of-day confound; this
is a bounded pilot, not a statistically replicated performance claim.

Read status.json in the reported output directory. Use its STOP file for an intentional
stop. The previous matching campaign lock prevents concurrent runs with that controller.
The new setup is separate and does not overwrite the old setup, CNFs, or results.

## Resource controls

windows_guard.py, worker.py and c2_reference.py are byte-identical to the tested 1.0.2
release. Host disk reserve 50 GiB, Linux reserve 25 GiB, RAM reserve 4 GiB, per-solver
address-space limit 4 GiB, log file limit 64 MiB, campaign output limit 3 GiB. Preparation
requires 55 GiB host and 30 GiB Linux free. No LRAT/proof output. Windows guard uses
fresh telemetry, independent observer, bounded retries; worker parent-death termination
unchanged. The guard's earlier eight-hour pass is evidence, not a future guarantee.
Two waves of logs are capped at 22*64 MiB; input generation adds less than 0.5 GiB.

## Evaluation

Count decisions SAT/UNSAT/OPEN and compare matched cases' solve time where decided.
UNSAT remains uncertified until a separate proof-producing/checking run. SAT is checked
by reconstructing the graph with the unchanged reference checker. If all cases remain
open, conflict rates, variable counts and clause counts are diagnostic only; do not infer
a winner or distance to a solution. No automatic overnight extension or follow-up.
