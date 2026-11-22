# C2 project audit and additional assurance programme — 22 November 2026

The Conway_99 project accepts Yongxian Zhang's (mxym) exclusion of involutions in an srg(99,14,1,2), at frozen revision d73a176f942b1fd67bac3b60c07d181487d84b66 of [mxym/math](https://github.com/mxym/math/tree/d73a176f942b1fd67bac3b60c07d181487d84b66). The project audit includes original-program replays and separate checks; the full AI-assisted project referee report (Claude) found no mathematical gap, uncovered case or unsound pruning. This is a project assessment, not journal acceptance or a complete independent reimplementation of every search.

Combined with Dilan Djematene's prior exclusion of order-three automorphisms and the published Behbahani–Lam restriction to prime divisors 2 and 3, a graph with these parameters would be asymmetric. Graph existence remains open. The published restriction is a load-bearing cited result; this project has not replayed that search.

## Priority and publication

The C2 proof, reductions and original search implementation are credited to Yongxian Zhang. Ralph Beckmann proposes that Zhang lead any publication and decide its timing in consultation with the partners. Djematene's earlier full C3 result is credited separately. No author list, contributor consent or publication decision is presumed. The English audit/reconstruction, complete referee report/addendum and V3 evidence package were emailed to Zhang and Djematene on 22 November 2026. A short public notice was posted in the existing mizopl issue. Private drafts and correspondence are not published here.

The partner notification explains that the following additional checks proceed independently of a decision to publish. They strengthen assurance; their incomplete status must not be described as completed independent verification.

## Five additional checks

| ID | Task and acceptance condition | Status updated 22 November 2026, 21:10 CET |
|---|---|---|
| S1 | Independent singleton-root search: implement from the mathematical specification; account for all 3,580 first-layer charts and the second-layer cases; independently verify every pruning condition and coverage. | All-chart preliminary unary conditions independently enumerated without orbit pruning; 177,842 raw signs retained. Heavy-quartet and second-layer reimplementation still pending. |
| S2 | Full second high-rank solver: all 3,156 chart/parity/mode jobs, including both rank-10 modes; fresh inputs, explicit exhaustion and coverage, no silent acceptance of empty or failed runs. | Pilot passed; all 98 strong chart/parity orbit sets regenerated exactly. Full second-solver queue running; 22 completed jobs captured in the current private evidence snapshot, not full coverage. |
| S3 | Full second low-rank solver for ranks 8 and 9, with nonsplit and split complements; reproduce input domains before full search. | All six rank-8 domain counts reproduced and checked. Complete rank-8/9 second search remains to implement; domain agreement is not exclusion. |
| S4 | Validate the referee's 31-class genus route: mass argument, automorphism orders, pairwise nonisometry, orthogonal dual units, regenerated atlas and every exact Farkas inequality. | New exact finite checker passed for all 31 classes, 465 nonisometry pairs, dual-unit frames and all 46 Farkas certificates; atlas totals 122/46/80 match. Five unimodular group orders and mass arithmetic also recomputed. Classification citation and manuscript integration remain. |
| S5 | Fresh C3 Lean build at 9678dec98108003359cde7b404d57a6e09dd865c, statement comparison and independent checker runs; explain five archived-log checksum mismatches. | Fresh pinned Lean executable and all 28 copied source/configuration files verified. Kernel build/comparator and historical-log explanations remain; disk reserve is checked before cache downloads. |

## Evidence and execution policy

Original and referee inputs are preserved, hashed and never edited in place. Portability changes receive separate versions and explicit provenance. A replay of the referee's program is a second implementation relative to Zhang's program, not a third independent implementation. All conclusions distinguish PASS, failed execution, an open mathematical case and incomplete coverage.

Local execution retains at least four logical CPU equivalents as a load reserve on the 24-thread Ryzen. Admission uses multiple CPU measurements, other projects' actual CPU load, RAM and disk thresholds; no hard research timeouts or duplicate jobs. No paid cloud computation, no changes to unrelated processes and no revival of abandoned campaigns.

The detailed private dossier and subsequent run records are maintained in [conway99-review-exchange](https://github.com/ibenarb/conway99-review-exchange/tree/review/project/c2-assurance-20261122/reviews/2026-11-22-c2-audit-assurance). Access is unchanged. Public summaries will record substantive results and limitations.

## Current deliverables

- English audit/reconstruction: C2_Manuscript_v3.pdf, SHA-256 3a61ea3a3896ce147e893f5ccb7aaecce9de9d9eb82d3b4931eb471031f347b2.
- Full dossier: C2_Review_Package_v3.zip, SHA-256 e7478f3bba1c6a25aa70c5c988a9fc949a9b0bfb50db5dbfb345b582bac53b20.
- Complete referee report with asymmetry addendum retained verbatim in the private dossier.

Earlier dated C2-open reports in this repository describe historical campaigns. They are superseded by this graph-specific audit and do not become general lattice exclusions retroactively.
