# Artifact evaluation guide

## Claims supported by the current reconstruction

| Claim | Command | Expected evidence |
| --- | --- | --- |
| Python semantics | python -m pytest -q | Tests pass in a clean environment |
| K=1 configurations | python experiments/reproduce_table4.py | results/generated/table4.* |
| Python K scaling | python experiments/reproduce_table5.py | results/generated/table5.* |
| Question-relative sufficiency | python experiments/reproduce_table6.py | results/generated/table6.* and witnesses |
| Synthetic quarantine | python experiments/reproduce_table7.py | results/generated/table7.* and zero soundness failures |
| Figures | python experiments/reproduce_fig5.py, reproduce_fig8.py, reproduce_fig9.py | Generated figure sources and previews |
| Full reconstruction | python experiments/run_all.py | Reconstruction report and manifest |
| Optional TLC | set TLA2TOOLS_JAR=... then python scripts/run_tlc.py | External TLC status and logs |

## Evidence interpretation

The current Python outputs are the authoritative generated values for this independent reconstruction. The historical paper assertions are preserved under results/historical_paper_assertions/. They are not imported by the model and are not used to force generated results.

TLC was unavailable for the current revision. A future Python/TLC mismatch is a failure when both machine-readable result sets are available; missing TLC remains an explicit unavailable check.

## Known limitations

The original historical implementation, historical seeds, exact recorder/question automata, and production runtime are not included. The current artifact is finite, single-principal, one-cut, and conditional on the declared trusted components and observation boundary.
