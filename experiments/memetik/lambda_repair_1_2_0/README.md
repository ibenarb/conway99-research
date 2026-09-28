# Lambda repair 1.2.0 — fresh extended repeat

Same 24 founders, 144 windows/seeds and mathematical model as 1.1.0.
Each task receives 7200 CPU seconds including calibration, model construction and prior attempts.
A calibration attempt ending at its soft target does not finish the task.
Audit rejects CPU_LIMIT_UNKNOWN with at least five seconds of remaining task budget.
12 workers; total 300 CPU hours, including 12 auxiliary CPU hours; 24 host hours safety ceiling.
20 CPU seconds attempt shutdown reserve, 60 seconds cumulative task grace; actual CPU charged.
Fresh directory ryzen_lambda_repair_120_20260928; older runs unchanged.
Existing pinned venv lambda-repair-1.0.0, Python 3.12.
Real Windows scheduler preflight required on startup.
Estimated 9–12 hours if early completions resemble the previous run; worst-case ceilings can require 24 hours.
ETA is an explicit budget projection, accounts for active CPU and final long tasks.
No claims of certified CP-SAT exclusion; CPU limit remains UNKNOWN.
