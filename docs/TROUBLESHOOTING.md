# Troubleshooting

If `pytest` is missing, install the development extra with `python -m pip install -e '.[dev]'`. If a managed environment cannot install packages, run `python -c "import ast, pathlib; [ast.parse(p.read_text()) for p in pathlib.Path('.').rglob('*.py')]"` for syntax validation and use `python experiments/run_all.py --fast` for behavior checks.

If TLC is unavailable, set `TLA2TOOLS_JAR` to an existing TLC jar. The artifact never downloads or fabricates TLC. If TLC reports a syntax or invariant error, preserve the log under `results/logs/` and inspect the module/configuration pair before comparing counts.

If a generated output is denied by a managed filesystem, run the command from a writable checkout or grant the process write access to `results/generated/` and `figures/paper/`. Generated files must still be created by scripts.

If a reported value differs, inspect `docs/ASSUMPTIONS.md` and the generated metadata sidecar. Do not edit generated result files or tune guards to match a number without a semantic justification.

For a resumed agent control, unchanged workload records are compared after canonical JSON conversion, because JSON turns order tuples into lists. A genuinely changed workload/provider/model is rejected; preserve old raw records and select a new output directory. Use a larger declared Java heap and fewer concurrent jobs for an actual TLC out-of-memory error; do not reinterpret it as a model disagreement.
