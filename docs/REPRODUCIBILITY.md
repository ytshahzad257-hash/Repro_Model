# Software reproducibility

## Verify saved evidence

Install the development dependencies and run the README verification commands. The delivered raw model evidence is complete; validation does not require a live model server. `scripts/validate_agent_v6_3.py` checks task values, prompt order, every completed call journal, endpoints, Wilson intervals and the six paired tests. The earlier-run verifier checks original hashes or the single declared model-path metadata redaction without rescoring earlier experiments.

The frozen current protocol is `experiments/agent/PREREGISTRATION_6_3.md`. Its timestamp/hash receipt and execution-source identity are under `results/generated/agent/`. Model/runtime/weight identities are recorded with the primary run. The two fixed arms contain 100 tasks each. The primary decision precedes the unchanged canary battery; the optional arm follows the frozen timing rule. Incorrect pre-cut plans remain in the fixed sample.

## Smoke/reuse mode

```sh
python experiments/run_all.py --fast
```

This reuses saved finite and model evidence, runs the current schema control and regenerates selected workflow outputs and result plots. It is labelled a smoke/reuse run. Use an isolated copy to keep the delivered measurements and manifest unchanged. Reports disclose reused evidence rather than claiming new model calls or new TLC checks.

## Full finite/workflow reproduction

Use Java and the pinned TLA+ tools jar. `scripts/setup_tla.sh`, the Dockerfile and the manually triggered workflow identify the supported tool download. Set the jar path and heap limit:

```sh
export TLA2TOOLS_JAR=/absolute/path/to/tla2tools.jar
export JAVA_TOOL_OPTIONS=-Xmx2g
python experiments/run_all.py --dry-run --jobs 2
```

The dry-run mode performs finite/workflow work with a deterministic schema stub and reuses reported model evidence. Omit `--dry-run` to resume the matching cached local-model run; missing tasks require the pinned model server. The model is `qwen2.5:7b`; its exact digest, Ollama version, context, temperature and output limits are fixed by the protocol. Earlier run directories are never rescored or replaced by the current driver.

## Fresh model inference

Use a separate isolated copy and retain the delivered records. Archive that copy's current decision-run directories, timing decision and execution snapshot before beginning new timing. Preserve the frozen scientific sources and capture the intended runtime/model identity with `scripts/capture_agent_model_identity.py`. Run the three paired discarded warm-ups, freeze eligibility, then execute the fixed primary arm and eligible descriptive arm. Never run two controllers against one output directory.

Completed tasks and successful calls are saved atomically or journalled. Resume missing work after a crash with the same protocol/runtime; preserve incomplete attempt journals. Do not select retries or exclusions by answer quality. A fresh replication is distinct from cached validation.

## Result plots and manifest

`python experiments/paper_figures.py` generates the finite-model, bound and quarantine charts from saved result JSON (the historical filename is retained for compatibility). `python scripts/final_figures.py results/generated <output-dir>` draws the quarantine-robustness and decision-experiment charts. Both read only saved results.

After intentional changes, regenerate and verify the current manifest:

```sh
python scripts/build_manifest.py
python scripts/verify_manifest.py
```

Public log representations retain separate original/public hashes; `scripts/compress_server_logs_v6_3.py` verifies the declared compressed representations. See `docs/PUBLIC_DISTRIBUTION.md` for the redaction scope.
