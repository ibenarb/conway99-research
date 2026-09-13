# K66 restart: processing on Ryzen

This restart supersedes the derived conclusions and verification scripts under docs/src/results k66_completion_20260913, k66_main_completion_20260913 and k66_star125_20260913 as authoritative audit evidence. Historical files remain for traceability; none of their claimed checks are adopted without independent verification.

Run src/k66_restart_20260913/k66_ryzen_audit_v1.py on the Ryzen. It is self-contained (Python standard library), read-only with respect to research inputs, and resumes file-hash work through versioned checkpoints. It performs archive/tree/log checks, controls on hash-identical historical checker binaries, and hash checks of locally available CNF and compressed/uncompressed proof bytes. It does NOT rerun production proof checkers or SAT solving. See the generated REPORT.md and compact_report.json for separate evidence levels and missing mathematical obligations.

The two existing ZIP copies under data/k66_main_completion_20260913 and data/k66_star125_20260913 remain damaged and MUST NOT be used. Their replacements and any other large Git uploads must now be made directly from Ryzen, as instructed by the owner. No large binary is added or replaced by this commit.

Expected originals:
- Main: 6432367 bytes; SHA256 ae44c1274c5c3c646f964475e3c6a6057bb11525105144e2f41126ad54f0ebbb
- Star: 14349650 bytes; SHA256 11287fffa90e6700c7fea159d8c9e948e92418ca3b875c3a3e9556ff45bc3be0

Initial fresh archive inspection found exact coverage of 897 terminal nodes by 890 binary splits, plus 300 LRAT warning lines in 157 logs. These warnings must not be silently accepted as clean LRAT verification. Cake logs are separate evidence. All counts are recomputed locally by the new program. No production proof replay has been performed in this restart.
