# Audit Preserving Revocation for Derived Memory

This repository is the independently reconstructed executable artifact accompanying the manuscript Audit-Preserving Revocation for Derived Memory in Enterprise LLM Agents. It contains a finite transition-system model, a separate TLA+ reference specification, an independent Python explorer, question-relative sufficiency analysis, deterministic synthetic quarantine experiments, generated tables and figures, witnesses, provenance metadata, and a checksum manifest.

The repository supports the finite-model and synthetic claims implemented by the current reconstruction. It does not claim production deployment, complete LLM unlearning, causal-dependence detection from mediator logs, or coverage of physical timing, resource contention, distributed cuts, repeated epochs, or multiple principals.

## Reproduce the current revision

Requires Python 3.11 or newer. The Python dependencies are declared in pyproject.toml.

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -e '.[dev]'
    python -m pytest -q
    python experiments/run_all.py

The full command regenerates the current revision's Python results, figures, witnesses, metadata, consistency report, and manifest. --fast runs a smaller smoke reproduction and omits the full scaling plot.

The current revision reports:

- seven finite configurations with K=1 Python reconstruction results;
- K=1..4 Python scaling results;
- a compact 16-history Algorithm 1 experiment;
- question-class bounds for K=1,2,3;
- five use-probability and nine growth settings for the synthetic quarantine experiment; and
- 28,000 full-mode synthetic workflows.

TLC is not bundled and was not available in the environment used for the current manuscript revision. Set TLA2TOOLS_JAR to a local TLC distribution and run python scripts/run_tlc.py when an external TLC validation is available. The manuscript makes no Python/TLC agreement claim for the current release.

## Artifact layout

- src/apr/ contains the Python semantics and analyses.
- experiments/ contains executable result and figure generators.
- tla/ contains the separate TLA+ reference modules and configurations.
- tests/ contains model, security, sufficiency, witness, and quarantine tests.
- docs/ contains the formal interpretation, assumptions, mapping, and reproducibility instructions.
- results/expected/ contains regression assertions for the current reconstruction.
- results/historical_paper_assertions/ preserves the earlier manuscript assertions for auditability.
- figures/generated/ contains generated previews and the publication-ready figure assets used by the revised manuscript.

## Evidence status

The original historical implementation, historical stochastic seeds, TLC execution log, and original recorder/question automata were not supplied. The current Python results are therefore authoritative for the independent reconstruction reported in the revised manuscript. Expected values are kept separate from model code, and historical assertions are retained separately rather than silently overwritten.

## License and citation

The artifact is released under the MIT License. See LICENSE and CITATION.cff. A public repository DOI or URL should be added to the citation metadata when the package is archived.
