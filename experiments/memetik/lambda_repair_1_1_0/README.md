# Lambda repair 1.1.0 — clean restart

Fresh Ryzen/WSL2 run: ryzen_lambda_repair_110_20260928.
Never run the 1.0.1 recovery package for this experiment.
24 original founders and the same 144 fixed tasks; MANIFEST.json,
BOUNDARY_CHECK.json, model.py and verify.py remain byte-identical to 1.0.0.
All task outcomes and CPU counters begin anew. The failed 1.0.0 run remains
separate and untouched. No candidate from it is imported.

## Runtime and start

Use the existing dedicated Python:
$HOME/conway99_workspace/venvs/lambda-repair-1.0.0/bin/python.
Dependencies are checked against the original exact lock; no environment
modifications or automatic installations. start.py prepares and launches;
--prepare-only only prepares. Existing targets are never overwritten.
The PYZ release contains the complete program and starts the same start.py.

## Operational policy

Per-task soft search target: 3600 CPU seconds including model/startup.
Each attempt reserves up to 20 CPU seconds for shutdown; at most 60 seconds
cumulative additional task shutdown allowance. Calibration uses the original
task account. All actual wait4 CPU, including tail, counts towards the same
156-CPU-hour total limit and the original 12-CPU-hour auxiliary limit.
No accounting erasure, redistribution or automatic global budget increase.
A five-second tolerance is for reporting local hard-limit anomalies, not
unrecorded time or permission to keep searching after a stop request.
Kernel hard stop and a 60-host-second termination timeout bound unresponsive
workers. Small accounted overshoots produce local receipt warnings.
A local worker failure is retained and isolated; unrelated tasks continue.
Invalid graphs, unresolved accounting, failed mathematical controls,
unavailable authoritative clock and resource danger remain global stops.

## Mandatory target-host gate

Before search: real Windows clock probe; twelve parallel CPU workers through
this very controller, two with deliberate three-CPU-second shutdown tails;
verify internal CPU vs /proc vs process_time vs wait4; require that healthy
peers continue after a delayed worker is collected. Then mathematical
controls and three size calibrations. These checks consume auxiliary CPU.
Cloud tests label their injected clock FakeHost. They do not certify Ryzen.
The real gate must print SCHEDULER_PREFLIGHT_PASS before productive search.

## Status and operation

RUN/program/run.py ACTION RUN, ACTION=status/pause/launch/verify/export.
status reads the latest snapshot; it is not a fresh process measurement.
A snapshot is written immediately after the first launch block and every
10 minutes thereafter. It includes its timestamp and local warning counts.
ETA uses measured productive CPU per Windows host second after at least
120 seconds of repair; the ideal budget projection is displayed separately.
Guest clocks are diagnostic only. No fixed clock correction factor.
A clean USER_PAUSE can be resumed; a hard crash with unresolved CPU cannot.

## Evidence

OPTIMAL_UNCERTIFIED is not a certified exclusion. Timeouts remain UNKNOWN.
Primary success is an independently verified W<2076. A technical error or
incomplete run does not establish exhaustion of the repair method.
Rules: docs/EXPERIMENT_RULES.md; GC-01/02/04/05/06/08/09.
