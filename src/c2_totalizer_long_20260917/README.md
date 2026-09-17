# Single 18-hour totalizer wave

User-authorized bounded gamble, 17 September 2026. Eleven matching cases, seed 0,
each at most 64800 wall seconds, eleven concurrent workers. Approximately 198 CPU
hours if all remain open and each obtains a full core. Does not resume a checkpoint;
the first 20 minutes of the earlier totalizer scout are repeated. No reference rerun.
No new encoder, assumptions, solver, or proof settings. No automatic follow-up.

prepare_long.py checks and reuses the existing counter-ab inputs and solver, under the
same campaign lock. Separate root c2_totalizer_long_v1. No old results overwritten.
run_matching.py is the counter-ab controller reduced to one eleven-job totalizer wave
and extended to 64800 seconds. Worker, Windows observer and reference graph checker
are byte-identical to counter-ab 1.0.0 / matching 1.0.2.

Host reserve 50 GiB, Linux reserve 25 GiB, RAM reserve 4 GiB. Per-worker address space
4 GiB, log cap 64 MiB, output cap 3 GiB. Proof logging OFF. Eleven solver logs together
capped at 704 MiB. An error or resource floor stops the campaign. Successful SAT graph
reconstruction stops other workers for review. UNSAT is uncertified. Completion,
errors, status and solver logs are retained. No automatic shutdown of Windows.

Start: python3 prepare_long.py then python3 run_matching.py --seconds 64800.
Keep the host awake and powered; the detached launch does not prevent host sleep.
Control-flow regression: eleven dummy solver jobs, simulated Windows telemetry; this
checks controller plumbing, not a production solve or an 18-hour reliability guarantee.
