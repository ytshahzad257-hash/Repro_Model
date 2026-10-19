# Independent TLA+ finite model
The directory name `v5/` is retained for continuity. APRSemantics defines its own guards, successors and observations. APR is the single-copy specification. APRProduct compares full observations, payloads and public enabledness, with a separate equal-release initial-pair restriction.

```sh
TLA2TOOLS_JAR=/absolute/path/tla2tools.jar JAVA_TOOL_OPTIONS=-Xmx2g python scripts/tlc_matrix.py --jobs 2
python scripts/cross_checkers.py
```

The declared matrix currently has 99 cases and 1,287 jobs; case declarations are in experiments/finite_cases.py. Count jobs explore the full graph; property jobs stop at the first violation. TLC generated-state counts subtract the number of initial states to obtain enabled transition counts; equal-release products can have multiple diagonal initial pairs. See docs/FORMAL_MODEL.md and docs/REPRODUCIBILITY.md for precise coverage/tool identity. Legacy reconstruction modules are unused.
