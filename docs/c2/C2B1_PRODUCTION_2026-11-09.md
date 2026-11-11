Current status, 11 November 2026: case 1005 is formally closed; 14/62 certified,48pending,no active case campaign. See CASE1005_CLOSURE.md and CASE1005_RELEASE.json. The integration/start narrative below is historical.

# C2B1 production integration â€” 9 November 2026

Update 19:57 Berlin: case 1005 is running with the reviewed C2B1 integration since 18:56:44 UTC. The first regular checkpoint and subsequent batches passed; the initial three receipts remain byte-identical. Pre-checkpoint seal commit ba26df76886ec2b066e175c5a614edf79000a977; start-contract commit a97e2da452cef10d99bd07ecb5dec5e952fa46f8. 13 of 62 L62 cases certified, 49 pending. Case identifiers are catalogue identifiers, not the number of cases completed. Neither L62 nor C2 is closed.

The integrated method combines shared-prefix batches with coupled block-exchange minimum filtering. It uses C2B1 restricted UNSAT certificates, never treating a restricted result alone as a global exclusion. Complete domains, coverage and coupled actions are checked by the unchanged independent closure gate.

Case 1005 has 289,536 ordered boundary states, 9,072 representatives and 32 coupled actions. Complete row-domain sizes are 22,176 for rows 0â€“3 and 91,392 for rows 4â€“11. The full structural audit passed; it is explicitly non-closing.

Validation: 26 transaction integrity/recovery controls; three real SIGKILL controls; three UNSAT/UNKNOWN/open-prefix controls; a 96-boundary receipt-scaling control; six binding/partial-verifier/regular-restart controls; twelve production/helper/real-data seal controls. Six real pilots passed. A real Aâ€“Bâ€“A comparison on boundaries 0,12,1 produced byte-identical proof payloads with independent native replay, batch 4.2638 s versus individual 6.4284 s. This limited comparison is not a full-case benchmark and does not establish acceleration against the previous eight-worker campaign.

The final immutable seal binds the production controller, transaction controller, independent sensor, both native programs and their sources, case/closure/search contracts, complete representative masks, structural audit, final pilots, controls, storage plan and archived source copies. Search receipts bind the case, boundary masks, C2B1 semantics and closure context. A partial native verifier result does not commit a batch.

One sequential batch of three boundaries runs at a time. The regular gate stops after its first durable batch. The full run resumes that same contract, preserving checked receipts, then invokes the unchanged complete closure gate for fresh independent replay of all 9,072 proofs, followed by byte verification of the full archive. It never automatically increments the global count.

Recovery is conservative: unresolved search attempts and resource stops require diagnosis. Explicit finish is permitted only after all search receipts exist; identical partial closure copies are reused, conflicting bytes rejected, and each fresh replay and archive uses a new destination. Old evidence is retained. No automatic blind retries.

Storage forecast: three raw copies plus five compressed copies including the archive, maximum of six pilot sizes, 50% margin, plus 24 GiB reserve: 36,281,262,552 bytes required; 61,571,936,256 bytes free when planned. This is not a mathematical upper bound. The independent resource watcher remains mandatory. A repeat finish requires assessment of retained earlier snapshots.

Independent reviewer gave conditional start approval at 19:53 Berlin after the regular checkpoint, Git and fresh exclusivity/resource checks. Shared local Git checkout and T20 are unchanged. No heartbeat or external messages are enabled.
