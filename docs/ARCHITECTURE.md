# Architecture
`src/apr/model.py` defines immutable finite-state semantics through explicit guards and successors. Named switches contain no result counts. Source valuations may be shared or independent; the revoked subset and session cache are separate state. `explorer.py` counts enabled state/action pairs and checks full, payload-only and equal-release products, including public enabledness. `tla/v5/` is independently authored and never imported by Python. The fail-closed cross-check compares declared quantities from both encodings.

`src/apr/sufficiency.py` is a generic finite-state recorder/question self-composition, distinct from operational exclusion products. `recorder_experiment.py` supplies the actual finite agent's pre-cut histories with a hidden-use choice. `question_bounds.py` computes exact history/fiber/class counts by dynamic programming. These constructions are not measured model causation.

`labels.py` and `quarantine.py` implement conservative admission reachability and separately sampled used-edge ground truth. The robustness experiments vary selection/use rules with explicit seeds and retain per-workflow metrics. Capture soundness follows structurally in this generator.

`src/apr/agent/prototype.py` provides the confined memory list, labels, private quarantine/release path and provider adapters. `experiments/agent/run_agent_experiment.py` creates fictional tasks, replays paired full-DAG canary substitutions, executes fixed follow-ups and records raw provider responses. The deterministic stub is a separate control. The prototype does not establish all runtime premises.

Drivers write source provenance, raw results, software validation reports and result plots. Document-building files are excluded from this distribution. Checksums are regenerated after software outputs and documentation are saved. Historical model/runtime and execution records are retained under results/.
