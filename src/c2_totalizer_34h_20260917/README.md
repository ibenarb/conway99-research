# Totalizer scout 34 hours, version 1.0.2

User authorized extension from 18 to 34 hours on 2026-09-17.
Default and maximum per-case wall budget: 122400 seconds. Eleven workers.
CPU and subprocess watchdog limits derive from the passed budget as before.
No proof logging; resource limits and guard unchanged. No solver checkpoints.
A mathematical decision by the budget deadline is not guaranteed.

prepare_extended.py requires a prior WINDOWS_SHARING_SELFTEST_PASS and checks
that the tested guard source is byte-identical to this release. Solver and all
eleven CNFs are rehashed. Shared campaign lock prevents overwriting setup while
a prior controller runs. No active process is stopped or extended in place.
Setup is backed up before source selection changes. Then run run_matching.py
--seconds 122400. Starts a new timestamped run; old results remain unchanged.

Operator reported real Windows guard test for 1.0.1: short lock 14 retries,
0.748 seconds; delete-shared 0 retries,0.003 seconds; persistent lock expected
failure at 5.021 seconds,94 retries; six fresh telemetry updates,zero read retries.
This evidence is operator-reported and the receipt is retained on the target.
A new Windows test is unnecessary because this guard is unchanged.

Local validation: all eleven dummy jobs complete; CLI accepts 122400 and rejects
122401. Mathematical source, worker and guard byte-identical to previous release.
This is not a 34-hour endurance test. Prior guard analysis and test details are
in src/c2_guard_fix_20260917 at commit a7a63794c820b83f277e160b918541fadbbd18ed.
