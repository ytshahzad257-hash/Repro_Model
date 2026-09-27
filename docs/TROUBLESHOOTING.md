# Troubleshooting

If `pytest` is missing, install the development extra with `python -m pip install -e '.[dev]'`. If a managed environment cannot install packages, run `python -c "import ast, pathlib; [ast.parse(p.read_text()) for p in pathlib.Path('.').rglob('*.py')]"` for syntax validation and use `python experiments/run_all.py --fast` for behavior checks.

If TLC is unavailable, set `TLA2TOOLS_JAR` to an existing TLC jar. The artifact never downloads or fabricates TLC. If TLC reports a syntax or invariant error, preserve the log under `results/logs/` and inspect the module/configuration pair before comparing counts.

If a generated output is denied by a managed filesystem, run the command from a writable checkout or grant the process write access to `results/generated/` and `figures/generated/`. Generated files must still be created by scripts.

If a paper value differs, inspect `docs/ASSUMPTIONS.md`, the generated metadata sidecar, and `docs/MANUSCRIPT_CONSISTENCY_REPORT.md`. Do not edit generated result files or tune guards to match a number without a semantic justification.
