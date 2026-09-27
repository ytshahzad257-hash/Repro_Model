# Cross-checker report

The Python explorer and TLA+ files are maintained as separate reconstruction layers. The current revision does not claim that they have been executed against identical historical semantics.

When TLC is unavailable, the generated status is WARNING and the reason is recorded. A future numeric comparison requires a machine-readable TLC result export with the same configuration, K parameter, state-count convention, product construction, and observation fields as the Python output. If both exports are available and a field differs, the result is FAIL until the discrepancy is investigated.
