# ROOT8105 N1 runtime 0.8.1 — recoverable Windows memory pressure

Limited to the same two fixed class-zero calibration inputs. No mathematical
model, native solver, checker, or proof acceptance change. This release repeats
only Root210 class0, in a NEW run, after the stopped 0.8.0 search.

## Host memory policy

Available Windows physical memory below the existing 8 GiB reserve now sends
SIGSTOP through a pidfd to this session's validated native child only. The
observer and supervisor continue. The process, CDCL state, and open proof stay
alive; native CPU does not advance while stopped. Status PAUSED_HOST_MEMORY is
stored in state.json and platform/health.json. Exact triggering measurements
are sealed in platform/pressure-events/*.json and platform/pause.json.

Resume uses SIGCONT on the same validated process after fresh Windows samples
have stayed at or above 9 GiB for ten host Stopwatch seconds. A lower sample
resets the recovery interval. There is no pause timeout. Existing positive and
zero budget replies retain their meaning. Zero releases the paused process for
cooperative termination; fatal platform faults also release it for termination.
An unanswered time-budget request never causes a pause.

Pausing does not release the child's RAM and is not a durable disk checkpoint.
An OS crash, reboot or external process termination still loses the internal
solver state. Other guards (guest RAM, cgroup OOM, disk, RSS, invalid clocks) retain
their existing stop behavior. Never restart WSL or alter unrelated C2 processes.

## Accounting

Only an exact HOST_MEMORY_RESERVE fault with an intact linked final receipt,
valid rechecked Windows final clock/CPU receipt, exit 0 and closed native
registration may be classified as a resource stop with complete end accounts.
The original fault is retained and exported as resource_stops. Missing or
changed evidence, other faults and open native registration remain blocking.
No sealed predecessor file or 0.8.0 manifest is modified.

## One repeat on RB-CUBE

Use the existing ROOT8105_N1_python interpreter and native_072 binaries.
`retry.py --output NEW_DIRECTORY` reads and checks the stopped predecessor,
executes test_memory_pause and test_resource_accounts on this target, prepares
only Root210, and records PREDECESSOR.json with all old confirmed CPU. It does
not start the solver. Then use `runtime.py run NEW_DIRECTORY/r210_class000`.
A new run gets a new native 21600s / aggregate 28800s decision budget. The old
11944.596729 native seconds and 12500.9748332 recorded aggregate seconds stay
separate and visible. This is an authorized repeated test, not continuation of
the already terminated old CDCL process. Root6682 is not automatically started.

The package-specific start command checks the ZIP digest, refuses existing
output/package paths, prepares the new run, then requests a detached start.
`status.py ROOT` is the compact read-only status command. For time-budget replies,
use the existing runtime.py reply interface with the current request ID and
scope; 0 stops and a positive integer adds that many CPU seconds once.

## Validation and boundaries

12 targeted pause tests (including real Linux process signals and an in-memory
counter across two cycles), eight actual predecessor-account tests, and 22
release gate checks passed in the cloud. Host memory samples in pressure tests
are synthetic; no actual host memory exhaustion was induced. The same 20 pause
and account tests run on WSL before the repeat is prepared. Existing Windows
transport and native binaries keep their 0.7.2 acceptance evidence; the new
pressure behavior is not falsely described as already accepted on Ryzen.
No N1 searches or previous mathematical audits were repeated in the cloud.
Relevant project rules: GC-01, GC-08, GC-15, GC-18, GC-19, GC-21, GC-22, GC-24.
