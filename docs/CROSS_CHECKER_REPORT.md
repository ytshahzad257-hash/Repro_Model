# Cross-checker report
PASS: 1,386 compared quantities, 0 mismatches across 99 declared cases and 1,287 TLC jobs. See `results/generated/cross_checker_agreement.json` and the compact logs in `results/logs/tlc/`.

Both encodings separately define guards, successors and observations. Each case compares single-copy state/transition counts in both worlds; unrestricted and equal-release product state/transition counts; information safety, authorization safety, review availability and full/payload/equal-release observations. Full observations include public enabledness. Missing coverage, incomplete/error TLC runs or a value mismatch cause a failing exit status. Count jobs explore completely; property jobs may stop at a reported first violation.

Shared-secret cases cover all configurations through five sources. Independent-bit cases cover representative one/all revoked pairs through three sources; they do not exhaust all valuations or subsets. The injective approved release compares diagonal pairs in its equal-release product. The encodings agree on compared quantities; this does not compare their full transition relations, prove refinement or rule out a shared contract error.

Saved TLC execution logs and the machine-readable matrix retain the finite-run outcomes.
