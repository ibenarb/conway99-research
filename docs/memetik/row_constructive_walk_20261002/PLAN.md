# Row-constructive WALK campaign 0.3.0

Date: 2026-10-02. Branch: `memetik`.

## Goal

Turn the successful one-step diagnostics into an autonomous dynamic-row campaign.
The current verified lower bound for a locally consistent partial construction is
18 built H rows. The campaign searches for depth 19 and, after a hit, automatically
tries 20, 21, ... from the same backtracking cut.

## Seed policy

The campaign does **not** use only the two saved depth-17 witnesses. It harvests
every valid `best` and `prefix` still present in JSON checkpoints/witness files
under the supplied source run directory and deduplicates prefixes by SHA-256.

This is "all available saved 16-states", not all depth-16 states ever visited by
the 18-hour run; those were not all persisted. Backtracking from shallower cuts
regenerates alternative 16-states dynamically.

## Backtracking depth

First campaign: cuts 16,15,...,8. Do not jump directly to depth 1.

Evidence: along both independent depth-17 witnesses, every remaining row stayed
individually feasible through depth 8; the frontier collapse began only around
depth 9 and became severe at 13--17. Cuts below 8 therefore add enormous branching
before the first observed discriminatory signal.

If no depth-19 construction is found from any saved ancestry through cut 8, a
second campaign may extend cuts 7,...,1. That would be a new, explicitly larger
experiment, not a silent budget extension.

## Search and semantics

For each cut and deduplicated base prefix, `probe_target_depth.py` performs dynamic
row-identity search. The first target is depth 19. A hit raises the target by one.
An exact exhausted search closes only that base/cut/target. Any solver node limit,
solution limit, task timeout, or campaign time reserve is UNKNOWN/UNRESOLVED and
must not be reported as exhaustion.

Relevant rules: GC-08, GC-15, GC-16, GC-17.

## Office production budget

- 8 concurrent tasks.
- 18 h campaign wall budget.
- 10 min shutdown reserve.
- 4 h per-task wall cap.
- 128,000,000 enumeration-node cap per row subproblem.
- 65,536-solution cap per row subproblem.
- status/heartbeat every 10 min.
- checkpoint granularity: one JSON result per base/cut/target plus campaign progress.

These are production limits, not mathematical bounds.
