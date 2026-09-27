# Agent instructions

- Treat the manuscript semantics as the specification; resolve convenience choices conservatively and record them in `docs/ASSUMPTIONS.md`.
- Never alter model semantics merely to satisfy a paper number.
- Never hardcode research results into executable semantics.
- Keep the Python explorer independent of the TLA+ model.
- Keep experiments deterministic. All randomness must come from explicit seeds in `experiments/seeds.json`.
- Generate result files through scripts. Do not edit generated results manually.
- Document every ambiguity and every implementation or result mismatch.
- Run relevant tests after changes.
- Update `docs/MANUSCRIPT_CONSISTENCY_REPORT.md` whenever scientific behavior changes.
- Do not claim production validation, complete unlearning, causal dependence detection, or coverage of channels outside the implemented finite model.
