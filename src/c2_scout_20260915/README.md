# Conway99 C2 scout 2.0.0 — 2026-09-15

Purpose: compare three exhaustive partitions against unpartitioned controls without generating production proof files. This is an empirical calibration, not an involution exclusion. Source/input reproduction and finite controls do not constitute an UNSAT proof.

## Preparation and execution

Run `python3 setup.py` as `rb_debian` inside Debian WSL, with Python 3.11+, git, g++, make, and Windows PowerShell interop available. Setup builds CaDiCaL 2.2.1 at commit `4198d817d0dcde5b1240eefbff70b555b7df2af9`, records the local binary hash, reproduces the pinned reference input and creates partitions. It checks Windows disk telemetry and starts/stops the independent observer before compiling. No production solver starts during setup.

After `C2_SCOUT_PREPARED_NOT_LAUNCHED`, execute the `next_command` in `~/conway99_workspace/c2_scout_v2/setup.json`. Default: 11 workers, 1200 wall seconds per cube, 3200 wall seconds for each baseline control. The launcher detaches; `ready.json` confirms observer readiness, while `status.json` records actual running jobs. A second controller is rejected by a process-held lock. Setup must not be rerun during a campaign.

The only production command form is `cadical --seed=N -t SECONDS INPUT.cnf`: one positional input, no proof destination and no LRAT option. In this version `-t` means wall time, not CPU time. Each worker separately records measured solver CPU with `getrusage`. Default maximum allocated search budget is 38,400 solver wall seconds across all 27 jobs; an ideal 11-worker schedule needs at least about 58 minutes. Allow roughly 1–1.5 hours with scheduling and machine load. No completion time for the mathematical problem follows from this estimate.

Create a file named `STOP` inside the current run directory to request a controlled stop. No automatic long run follows calibration. Inspect `summary.json` and solver logs before deciding on a next experiment. A future longer run would need an explicit new budget; this solver invocation has no checkpoint/resume mechanism.

## Comparison and coverage

Three independent 8-cube partitions use three distinct primary variables each:

- `disjoint_triangle`: the original B triangle on outer labels (0,2), (4,6), (8,10); split variables 22,36,685.
- `shared_triangle`: a B triangle on (0,2), (0,4), (0,6).
- `bc_coupled`: B and C for the pair (0,2)/(4,6), plus B for (0,2)/(8,10).

For each strategy all eight Boolean assignments are included; the original CNF body is an exact prefix of each cube body followed by three units. These are alternative full covers, not 24 disjoint parts of one partition. Exhaustiveness/disjointness is checked within each partition. No orbit reduction or equivalence of the three partitions is asserted. Easy/impossible cubes are part of the measurement, not silently discarded.

Each partition receives 8×1200=9600 allocated wall seconds; the baseline ensemble receives 3×3200=9600. Early termination changes actual CPU used; report both allocated budget and measured CPU. Seeds are zero for all cubes and 0,1,2 for baselines. Do not call a partition better merely because it reports more conflicts per second. Few solved cubes may be trivial and need not reduce the hard remainder. If nothing solves, report no demonstrated winner and use the run as a calibration result, not a progress percentage.

## Interpretation

- `OPEN_BUDGET`: no decision within budget, not an exclusion.
- `UNSAT_UNCERTIFIED`: matching exit code 20 and UNSAT line; requires a later certificate-producing run and independent checking.
- `GRAPH_VERIFIED`: complete primary assignment reconstructed and checked for graph size, degrees, symmetry and every common-neighbor equation, plus cube assumptions. Save adjacency and review provenance.
- Any inconsistent status, input change, process failure or resource fault stops the campaign.

Even all eight untrusted UNSAT messages are not a completed case proof. The reference encoder/model theorem and all later certificates still need their separate audit chain.

## Storage and process safety

The earlier run monitored free space inside Linux but exhausted the Windows volume backing its growing VHDX. This version checks the current distribution's registered Windows storage drive independently and stops below 50 GiB free; Linux reserve is 25 GiB, RAM reserve 4 GiB. Observer failure or stale telemetry also stops the campaign. A separate Windows observer watches the controller heartbeat and attempts to terminate only the identified campaign process group if it becomes stale. It does not shut down unrelated distributions.

No production proof output is generated. Solver logs have a kernel-enforced 64 MiB per-file limit; solver address space is capped at 4 GiB, core dumps disabled, with wall/CPU watchdogs. Twenty-seven maximum-sized logs occupy 1.69 GiB; prepared inputs occupy about 1 GiB. A 3 GiB campaign-directory limit adds another stop condition. The limits do not bound disk use by unrelated programs. Host-wide I/O hangs can defeat timely monitoring; this is risk reduction, not a guarantee against Windows/kernel failures.

Workers and solvers use Linux parent-death signals. Controller cleanup stops workers before attempting final report writes, so a report-write error cannot skip the stop loop. The observer uses Windows TEMP for small telemetry, not network storage. Existing Ubuntu recovery/archive files are neither opened nor changed.

## Verification

`python3 test_scout.py /path/to/cadical` exercises mismatched statuses, enforced file-size limits, altered-input rejection, solver termination after worker death, exact reference hashes, and all 24 coverage assignments. Setup also solves tiny SAT/UNSAT controls and reconstructs a valid nine-vertex graph through the real worker. Local development additionally ran the controller on 27 tiny UNSAT jobs with simulated Windows telemetry; all were classified as uncertified and no proof files were created.

Windows PowerShell observer execution cannot be validated in the Linux build environment. Setup performs that real-environment check and fails closed before the research launch if it fails. The recorded tests do not claim an end-to-end production run on the user's Windows machine.
