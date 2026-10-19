# Audit-Preserving Revocation: Reproducibility Software and Data

This repository contains the software and saved experiment evidence for audit-preserving revocation of derived memory in LLM agents: finite-state models in TLA+ and an independent Python explorer, exact evidence-sufficiency and private-evidence bounds, synthetic quarantine workflows, and an instrumented local-model prototype with its preregistered protocols, raw prompts and responses.

## Install and verify

Requires Python 3.11 or newer. From the repository root:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/verify_manifest.py
python scripts/public_distribution.py
python -m pytest -q
python scripts/check_expected.py
python scripts/verify_finite_preservation_6_2.py
python scripts/verify_earlier_runs_v6_3.py
python scripts/validate_agent_v6_3.py
python scripts/cross_checkers.py
```

Run `verify_manifest.py` before any command that regenerates results, because regeneration rewrites provenance metadata in `results/generated/`. The cross-check validates the saved Python and TLC results; it does not launch TLC. The decision experiment comprises 100 primary and 100 secondary tasks with every prompt, raw response and call journal. Earlier model runs and deterministic schema controls are kept separately.

## Contents

- `src/apr/`: state exploration, labels, revocation, evidence sufficiency and agent memory.
- `tla/`: TLA+ specifications (`v5/` is current; `legacy_reconstruction/` is unused).
- `experiments/`: seeded workloads, finite and workflow computations, and frozen model protocols.
- `scripts/`: validation, cross-checking, manifest and plotting scripts.
- `tests/`: model, protocol, scoring and preservation tests.
- `results/`: saved measurements, raw model evidence, witnesses, expected values and execution logs.
- `docs/`: architecture, model assumptions, terminology and reproducibility guidance.
- `artifact/`: checksum list and manifest.

## Reproduction

See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md). `python experiments/run_all.py --fast` performs a smoke run that regenerates software outputs without new model inference. Full finite reproduction requires the pinned Java and TLC tools; a fresh model replication requires the pinned local model and runtime and a separate output directory.

Plots: `python experiments/paper_figures.py <output-dir>` and `python scripts/final_figures.py results/generated <output-dir>`.

## Scope

The finite checks are bounded. One quantized model and synthetic quote tasks do not establish production security, enterprise usefulness or affordability. The memory-only experiment represents planning without an independent permission list, and the SourceOnly condition retains raw records as well as derivatives.

## License and citation

Source code is released under the MIT License. See `CITATION.cff` for citation metadata.
