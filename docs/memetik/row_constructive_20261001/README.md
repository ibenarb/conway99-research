# Conway99 constructive row pilot 0.2.0

This supersedes the incumbent-repair interpretation of row-health 0.1.0.

H starts empty. The fixed 1+14 border remains fixed. Rows are processed in the fixed order 16,...,99. A completed H-row has degree 12.

For outer vertex u let P_u be its fixed pair of border labels and S_u its H-neighbourhood. The 14 border-margin equations are enforced exactly. For every already completed row v the new row must satisfy

|S_u ∩ S_v| = 2 - H_uv - |P_u ∩ P_v|.

Thus each new row is a finite exact 0/1 subproblem because S_v is already fixed. Relations to future rows are unresolved, not counted as unhealthy. A forward necessary-condition test rejects row choices that already overfill a future degree, border margin, or common-neighbour obligation.

The search keeps a population through 8 independent DFS workers over row completions: ascending deterministic, descending deterministic, and six randomized workers. Backtracking is explicit. Exact row infeasibility, node-limit exhaustion, forward rejection and total wall-time exhaustion remain distinct.

A prefix of depth d guarantees all fixed-border relations for completed rows and all pair relations among completed rows. Reaching depth 84 would yield a full SRG(99,14,1,2), hence W=0; partial depth is not interpreted as a smaller SRG.

Office profile: 8 workers, 18 hours, atomic checkpoints every 60 s, controller status every 10 minutes (<80 chars).
