# Case 1005: complete C2B1 exclusion evidence

## Result and scope

The complete independent closure audit for case 1005 returned **PASS**: all 9,072 boundary representatives have freshly replayed canonically restricted UNSAT proofs, with zero remaining boundary tasks. The complete archive has passed byte verification. The independent final release review on 11 November returned PASS, including all 9,072 native receipts and 3,024 batch-log hashes. Git documentation governs admission to the global ledger; the audit itself never increments that ledger.

This excludes case 1005 within the documented L62 local matrix contract. It is not a complete C2 exclusion. After evidence commit `381bbf9c595223f8111e519cf29465c37a8d2ae0`, case 1005 was admitted once on 11 November. The certified total is **14 of 62**, leaving **48** pending. Case numbers are catalogue identifiers.

## Mathematical coverage

The independent audit reconstructed all twelve row domains: 22,176 masks for rows 0Ã¢â‚¬â€œ3 and 91,392 masks for rows 4Ã¢â‚¬â€œ11. It checked 289,536 ordered boundary states, 9,072 representatives, and 32 coupled actions, including the transports and minimum-representative conditions required for the C2B1 restriction. The restricted native proofs become a whole-case exclusion only together with these coverage and symmetry checks.

Closure context SHA256: `181bf3f99a1b27f0ec96d3ffcba51c0856cd9d4d646a1ac40e5d3e1e5a75b0a7`.

Proof manifest SHA256: `a30719b457ab7e9d3660e129aadd1d8d503431f7930193ddb2986c6533ee7e7e`.

Complete final audit SHA256: `fe7c3719c06ff92887965e98bb864fd8250f87f67927a88971ff9b76e2ef74f1`. The full audit is retained inside the complete archive; the accompanying summary reports its 9,072 fresh replay records.

## Execution and provenance

The production seal was committed before the first regular checkpoint (`ba26df76886ec2b066e175c5a614edf79000a977`). The regular checkpoint and start contract were recorded in `a97e2da452cef10d99bd07ecb5dec5e952fa46f8`. Production started on 9 November 2026 at 19:56:44.590 Berlin and completed audit plus archive verification on 10 November at 00:19:12.396 Berlin.

Total elapsed time was 15,747.806 seconds (4 h 22 min 27.806 s). The guarded full independent closure stage took 4,461.202 seconds (1 h 14 min 21.202 s). No errors or resource-stop records were observed. These timings concern this case; comparison with other cases does not establish a controlled speedup factor.

## Complete retained proof archive

`C2B1_case_1005_complete_86c28ed8bece40bc8efe1f8c144296fb.zip`

- Size: 582,072,132 bytes.
- SHA256: `f6822facfafa0264030311d44026da0ee84aea15aa0d1ecbd099c7e076f82441`.
- 75,826 payload files plus the archive manifest.
- Complete indexed corpus of 9,072 closure proofs, with inputs, sources, contracts, transaction and fresh replay evidence.

On 11 November the archive SHA256 and every payload member were checked again against the stored byte lengths and SHA256 hashes. The exact proof index set 0Ã¢â‚¬â€œ9071 was confirmed. Result: **PASS** (`FINAL_ARCHIVE_RECHECK.json`). The large complete archive remains local; publication of this report and its hashes is not a claim that the full archive has been uploaded to GitHub.

## Release safeguards

The existing sealed search/audit evidence is retained unchanged. Final review is recorded separately in `FINAL_REVIEW.md`. No further campaign is started by this closure operation; no heartbeat, email or GitHub comment is sent. T20 is unchanged. L62 and C2 remain open.
