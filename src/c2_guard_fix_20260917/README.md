# Totalizer long scout: guard correction 1.0.1

This release fixes heartbeat publication, not the mathematical encoder.
Run `python3 activate.py` on the Debian/Ryzen installation. It verifies the
existing solver and eleven CNF hashes and acquires the shared campaign lock.
It does not launch a research solver. Existing results are retained.

Activation takes approximately 30–60 seconds plus input hashing. It opens the
heartbeat from Windows with a read-only sharing mode for 700 ms and checks
that WSL retries replacement successfully. With ReadWrite|Delete sharing it
checks replacement without retries. A seven-second lock must trigger the
bounded five-second write failure and preserve the previously published file.
A subsequent 15-second telemetry check must observe at least three updates.
Only success updates setup.json, with a timestamped backup. The selftest
prints the new source path and a separate possible launch command.

Production changes:
- Heartbeat PermissionError retries, 50 ms intervals and five-second deadline.
- Timestamp refreshed on each attempt; published old heartbeat retained on error.
- No retry for ENOSPC, EIO or missing paths.
- Windows heartbeat reader uses ReadWrite|Delete sharing, disposing handles.
- Both write/read retry counts appear in status and summary.

All 50-GiB host, 25-GiB Linux, 4-GiB available-RAM, output limits and freshness
checks remain unchanged. Persistent errors still stop all active workers.
No proof logging, solver rebuild, CNF changes or automatic follow-up runs.
A new search starts over; there is no checkpoint resumption.

Local tests: `python3 check_guard.py`, `python3 check_controller.py`,
`python3 check_shutdown.py`. The latter starts eleven dummy child solvers,
injects a persistent write error and verifies no live child survives cleanup.
Controller test resource telemetry is simulated because the local test
filesystem has less than the production 25-GiB reserve. It is not changed in
production. Windows sharing tests cannot run in the Linux development container.
The Windows independent emergency-killer path is not tested by this release;
Linux controller cleanup and parent-death signals are tested.
