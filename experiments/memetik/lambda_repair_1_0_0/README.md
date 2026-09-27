# Lambda repair 1.0.0 — Ryzen / WSL2 / Python 3.12 x86_64

Executable implementation of the frozen pilot V2, commit
f67039295f658380f5795d95b72ad9a32769a9d8. Both MANIFEST.json and
BOUNDARY_CHECK.json are byte-identical to that published input.

24 pairwise nonisomorphic founders; 144 fixed tasks; windows 24/40/60;
defect-guided and hash-random connected windows. Degree14 and edge-lambda1
are hard constraints; all unordered pair residuals enter (W,L1).
Objective 50000*W+L1. Outside-outside pairs remain fixed.

No productive Ryzen run has been performed while preparing this package.
The small cloud validation campaign is explicitly separate.

## Installation and launch

`start.py` creates only the new environment
`$HOME/conway99_workspace/venvs/lambda-repair-1.0.0` and the new run
`$HOME/conway99_workspace/ryzen_lambda_repair_100_20260927`.
Existing memetik/profile/radius directories and environments are untouched.
Existing destinations are not overwritten. OR-Tools 9.14.6206 and every
transitive dependency are pinned by version and Linux wheel SHA256.
The first launch downloads about 58 MB of dependencies from the configured
Python package index. WHEELS.json records the exact distribution files.
Python 3.12 and x86_64 Linux are required; no source compilation is needed.

Run start.py using the existing memetik Python. It installs the separate
environment, freezes sources, then launches the autonomous controller.
`--prepare-only` installs/prepares without launching any campaign.
Do not run start.py twice for the same directory.

Production needs WSL and working Windows PowerShell interop. HostClock uses
Windows Stopwatch and reads the actual backing VHDX volume. Failure is a
hard diagnostic stop, not a silent fallback to drifting WSL time.

## Autonomous phases

1. Small exhaustive controls, all-founder score checks, set-based independent
   reproduction of all 144 boundary counts, three complete seed-assignment
   checks, and known N-to-A positive repair on its eight-vertex support.
2. One 60-CPU-second calibration attempt at each window size, charged to
   that existing task's original one-hour allowance. Incumbents are retained.
3. All remaining fixed tasks, up to 12 single-threaded processes. Five rigid
   windows have replayable boundary propagation traces and do not need search.
4. Final candidate verification, resource settlement and RESULT.json.

Up to 144 productive CPU-hours plus 12 auxiliary CPU-hours, including
controls, coordination and verification. Each task includes initialization
and model building. No task receives unused time from other tasks. A small
shutdown margin remains unspent. The full allocation is a ceiling, not a
required consumption. Existing results never seed new tasks automatically.

24-hour active Windows wall limit. Group RSS limit 24 GiB; stop launching
below 6 GiB free RAM; drain if group cap is exceeded or free RAM falls below
2 GiB. Logical and host backing-volume free disk must each remain >=25 GiB.
Parallelism is reduced by measured memory needs and current competing load.
Status every ten minutes in controller.log and status.json. ETA uses
remaining CPU ceilings; actual completion may be earlier, or the wall limit
may leave incomplete tasks. Previous planning estimate: 14–20 h on free Ryzen.

## Status, pause, resume, export

All actions use the dedicated environment's Python and the frozen
`RUN/program/run.py ACTION RUN`, with ACTION `status`, `pause`, `launch`,
`verify`, or `export`. Provide the full run-directory path twice.
`launch` resumes only a clean USER_PAUSE and retains CPU/wall counters.
An unresolved session, worker error or changed source needs diagnosis.
Do not delete ledger/session files to force a restart.

Every improved incumbent is independently checked and atomically saved
before further search. Resume reconstructs CP-SAT from that incumbent;
learned clauses and the internal search tree are not checkpointed. Restart
CPU is charged. Individual attempt logs, immutable result/incumbent snapshots
and wait4 receipts are retained. A hard controller/host crash is deliberately
not auto-resumed because exact CPU settlement would be unresolved.

Export is allowed only after a clean stop, runs audit.py, and produces
RUN_results.tar.gz plus SHA256; it never overwrites an existing export.
State/graph6 checks are independent of the solver. Isomorphism classification
of new results is deferred to the isolated project audit environment.

## Interpretation

Primary success: independently verified W<2076. No automatic stop at the
first record; W=0 stops after verification. Secondary improvements are
reported against their own founders. CPU/time termination is UNKNOWN.
`OPTIMAL_UNCERTIFIED` is a CP-SAT report without an independently checked
proof certificate. This release makes no certified solver-exclusion claims.
`COMPLETED_BUDGETED_PILOT` means all task policies finished, not all windows
were solved to optimality. Rigid-boundary claims have separate elementary
propagation traces. No global nonexistence or convergence conclusion.

## Validation and source references

TEST_RESULTS.json and the associated test scripts record cloud checks.
The real Windows host clock is tested at Ryzen startup; a cloud FakeHost
integration test is not presented as a Windows execution test.

OR-Tools source/API reference: https://github.com/google/or-tools/tree/v9.14
The solver dependency is pinned to the tested version, not claimed latest.
No modifications to the older frozen profile/radius packages are included.
