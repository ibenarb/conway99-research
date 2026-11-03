# Checks for the reply audit of 3 November 2026

The independent standard-library checker verifies the scope of the seven-anchor matching lemma, the component column-sum arithmetic and the necessary residual-capacity filter. It includes explicit controls against strengthening an existential zero-degree conclusion to a universal one.

From the repository root, run `python verification/c2_slice/audit_reply_20261103.py`. The output agrees with [reply_audit.json](../../results/c2/2026-11-03/reply_audit.json) after omitting its optional `upstream_summary` field.

To reproduce the bookkeeping section too, download the [pinned external summary](https://github.com/mizopl/conway-99-graph/blob/5bae03c494ee69501a6b5c7024a4b86c31c8bec8/verify-it-yourself/null_ktype1_ge1_unconditional_lego_summary.json) and pass its local filename as the sole argument. Verify its SHA-256 against [source_manifest.json](../../results/c2/2026-11-03/source_manifest.json).

The 232 labelled matchings and 64 feasible binary degree vectors are enumerated completely. The capacity tests cover 2,304 two-column/two-domain instances and 196,608 one-column/eight-domain instances, including empty domains. The code checks that every genuine completion passes. False positives are expected: passing is not sufficient.

These checks do not execute the large upstream searches, build Lean, verify the graph-to-solver projection, or certify a new SRG exclusion. Source files were inspected at the pinned commit. The [review](../../docs/c2/MIZOPL_REPLY_REVIEW_2026-11-03.md) states what remains unverified.
