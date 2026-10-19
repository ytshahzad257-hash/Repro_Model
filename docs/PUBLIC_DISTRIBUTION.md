# Distribution and provenance

This repository contains the reproducibility software and the saved experiment evidence: source code, tests, TLA+ modules, seeds, expected assertions, generated results, raw model prompts and responses, and execution logs.

Absolute local directory prefixes in retained execution logs and model-installation metadata are replaced by portable display prefixes. These display paths are redactions, not original machine locations.

All eight frozen scientific execution sources, the preregistration documents, task prompts, raw model responses, scored endpoints, intervals and hypothesis tests are unchanged. Model and runtime names and weight digests are retained to identify the methods.

`results/generated/public_distribution.json` records original and distributed hashes for every retained file whose distributed representation differs from the original (path redactions, compressed logs and documentation), together with the hashes of the frozen scientific sources. Of the 727 earlier frozen model files, 726 are byte-identical and one model-installation metadata file carries only a declared path-prefix redaction.

Run `python scripts/public_distribution.py`, `python scripts/verify_manifest.py` and the remaining README checks to validate this snapshot. No new inference, endpoint search or TLC execution was performed to package it.
