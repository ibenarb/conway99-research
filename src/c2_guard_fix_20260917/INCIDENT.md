# Incident 2026-09-17: Totalizer long run

## Evidence supplied by operator

Run: matching_20260917_020557_445533, source_oaj1ypl8, version 1.0.0.
Summary: TOTALIZER_LONG_FAILED, wall_seconds=45159 (12:32:39), results=[],
groups={}, eleven interrupted jobs, proofs_checked=0, guard_read_retries=4.
Traceback: run_matching.py:93 -> windows_guard.py:162 -> Path.replace ->
os.replace. PermissionError errno 13 while renaming heartbeat.tmp to heartbeat
in Windows guard directory 6e8495f88dbc4cc18594066037fd49d8.

This report transcribes the operator's summary, not a newly retrieved full
run archive. Full solver logs have not been analyzed here. No CPU time or
solver progress is inferred from elapsed controller wall time.

## Finding

The old Python heartbeat writer had no retry on PermissionError. The reader
already had bounded retry handling. Thus guard_read_retries does not measure
or protect heartbeat writes. A single failed replacement propagated into the
controller's finally block, which stops active workers.

Windows file sharing is a plausible mechanism. The old reader used
IO.File.ReadAllText; the revised reader explicitly grants ReadWrite|Delete.
Microsoft documents Delete sharing as allowing subsequent file deletion:
https://learn.microsoft.com/en-us/dotnet/api/system.io.fileshare?view=netframework-4.8.1
The process responsible for the actual failed replacement is not identified.
We cannot exclude another program, permanent permission problems or a different
WSL/filesystem condition solely from this traceback.

## Validation and limits

Nine local fault controls pass, including transient replacement and temp-write
errors, permanent failure preserving the published heartbeat, immediate fatal
storage errors and existing stale/disk/stop checks. Eleven dummy jobs complete
normally. Eleven real dummy solver processes stop on injected permanent guard
failure. Detailed outputs in VALIDATION.json. Two initial controller tests
stopped at the local disk reserve; the test-only resource readings were then
simulated, without changing production limits.

Real Windows file-share tests are implemented in activate.py and remain pending
on the user's host. They test short locks, delete-sharing, persistent locks
and fresh telemetry. No 18-hour reliability guarantee or Windows emergency-kill
end-to-end claim follows from the local controls.

## Research interpretation

No new C2 exclusion. Eleven cases remain open. The 12.5-hour run cannot resume
its in-memory solver state. Saved logs may still be used for performance
analysis. A guard-only repair does not improve mathematical search strength.
Before a further long campaign, pass target selftest; do not bypass campaign
lock, remove freshness guards, or restart proof logging.
