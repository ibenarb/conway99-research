# Public C2 review package and supplementary evidence

Published at Ralph Beckmann's explicit request on 23 November 2026. No GitHub account or invitation is required to read this public branch.

## Start here

- [Original review package, V3 ZIP](C2_Review_Package_v3.zip): the original 2.7 MB archive, preserved byte for byte, including the English audit manuscript, reviewer memorandum, referee evidence and original replay records.
- [English audit manuscript](C2_Manuscript_v3.pdf).
- [Full referee report and asymmetry addendum](Referee_full_report_and_addendum_original.txt).
- [Final completion record](FINAL_COMPLETION.json) and [scope and dated progress](STATUS_AND_PLAN.md).
- [Supplementary evidence](checks/): complete retained solver inputs, outputs, certificates, controls and final audit records for the five additional checks. These records postdate the V3 ZIP; the ZIP alone is not the complete supplementary evidence set.
- [Public file manifest](PUBLIC_FILES.json): SHA-256, byte size and Git blob identity for every preserved evidence file.

The complete public evidence set is approximately 12.8 GB. Browse the report or download the small V3 ZIP first if you do not need all raw solver inputs.

## Results and limits

S1 accounts for all 3,580 charts (3,308 physical searches and 272 nonphysical cases). The stronger first-layer search closes every case, including the original second-layer cases; the original second-layer survivor ledger was not independently reproduced. S2 covers all 3,156 high-rank jobs and S3 all 92 low-rank chart/parities. S4 distinguishes finite certificate checking from the classification/mass completeness argument. S5 freshly rebuilt the pinned C3 project using pinned dependency caches, rather than rebuilding all of Mathlib. The five historical log-hash differences were already present at their first commits; their pre-commit cause remains unknown. Implementation, input-generation and shared-backend dependencies are disclosed in the underlying reports.

These are project assurance results, not journal acceptance, a formal verification of every search predicate, or a proof that the graph does not exist.

## Attribution and historical documents

The C2 proof audited here is Yongxian Zhang's proof at revision d73a176f942b1fd67bac3b60c07d181487d84b66. This identifies the particular proof under review; it does not adjudicate priority for the C2 result. Dilan Djematene's earlier C2 work must also be acknowledged in an account of the result and its chronology, alongside his C3 work. The historical V3 manuscript's attribution discussion is incomplete in this respect. This public cover note corrects that omission without silently altering archived evidence. No agreed author list, consent to submit a paper, or new publication claim is implied. Ralph Beckmann has no publication plans of his own.

The referee report is an AI-assisted project report produced by Claude for the Conway_99 project. Its assessment is preserved as an attributed report. The subsequent assurance checks and their limits are documented separately.

## Preservation and public-release scope

Evidence files are unchanged from the final private audit snapshot 45ffbbfc0234c2a0c2ce4bdbb00ba1967f41004f. Original documents may refer to the repository as private, say that computations were still running, or describe the ZIP as not yet published; those are dated historical statements. The current completion record and this cover note give the final status and current public access.

This release contains the original review deliverables and complete mathematical evidence directories for S1-S5, including their unsuccessful controls and execution incidents. Local storage-maintenance inventories, unrelated host/process telemetry and the email-delivery receipt are outside this public release. Original audit manifests are retained for provenance; PUBLIC_FILES.json enumerates the actual public files. No private email correspondence or unrelated private repository history is published.

The Windows execution wrappers record the original local environment and are not turnkey portable installation instructions. Portable mathematical kernels, exact inputs, provenance and result hashes are included. Existing third-party authorship and licensing remain unchanged; this release asserts no new license over third-party material.
