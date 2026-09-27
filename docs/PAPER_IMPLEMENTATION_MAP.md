# Paper implementation map

This map is the implementation plan and audit index. The manuscript is the authority for the formal vocabulary. The executable interpretation is described in `ASSUMPTIONS.md` whenever the supplied paper omits a guard, state component, seed, or output convention.

| Paper section | Paper object | Implementation file or module | Executable check | Generated artifact or result |
| --- | --- | --- | --- | --- |
| 4.1 | Definitions 1–2: representation, validity, authorization, retention | `src/apr/state.py`, `src/apr/policies.py` | Immutable state and policy tests | `results/generated/table4.json` |
| 4.2 | Definitions 3–4: dependence and authority support | `src/apr/model.py` | `test_security_properties.py` | Table 4 safety verdicts |
| 4.3 | Definition 5: assurance contract | `docs/FORMAL_MODEL.md` | Documentation review | `docs/ASSUMPTIONS.md` |
| 4.4 | Definition 6: effective cut | `src/apr/model.py` actions `RequestRevoke` through `CommitCut` | `test_transitions.py` | Table 4 and witness traces |
| 4.5 | Definitions 7–9: transitions, releases, clean reconstruction | `src/apr/model.py` | Configuration and observation tests | Table 4 observations |
| 5.1 | Definition 10: question-relative sufficiency | `src/apr/sufficiency.py` | `test_sufficiency.py` | `results/generated/table6.*` |
| 5.2 | Theorems 1–2 and Corollary 1 | `experiments/question_bounds.py` | Deterministic bound calculation | `results/generated/question_class_bounds.*`, Figure 5 |
| 5.4 | Proposition 2: admission is not causation | `experiments/reproduce_table6.py` | Full mediator log causal witness | `results/generated/witnesses/*causal*.json` |
| 5.5 | Theorem 3 and Algorithm 1 | `src/apr/sufficiency.py` | BFS witness correctness | Table 6 and witness JSON |
| 6.1–6.3 | Definitions 11–12, A1–A7, Lemmas 2–3, Theorem 4 | `docs/FORMAL_MODEL.md`, `src/apr/self_composition.py` | Product and timing tests | Table 4 product/observation fields |
| 6.4 | Definition 13, R1–R8, Proposition 4, Theorem 5 | `src/apr/labels.py`, `src/apr/quarantine.py` | Soundness tests | Table 7 synthetic results |
| 6.5 | Theorem 5: compatibility/composition | `docs/ARCHITECTURE.md` | Cross-component smoke checks | Reproduction report |
| 7.1 | Three per-source actions and 17 global actions | `src/apr/model.py` | `test_transitions.py` | Table 4 and 5 |
| 7.1–7.3 | Seven configurations and Table 4 | `src/apr/policies.py`, `src/apr/explorer.py` | Python BFS for both secrets | `results/generated/table4.*` |
| 7.3 | K=1..4 scaling and Table 5 | `experiments/reproduce_table5.py` | Deterministic structural counts | `results/generated/table5.*`, Figure 8 |
| 7.4 | Recorder/question matrix and Table 6 | `experiments/reproduce_table6.py` | Algorithm 1 verdicts and witnesses on the compact 16-history reconstruction | `results/generated/table6.*` |
| 7.5 | Synthetic quarantine and Table 7 requested by artifact brief | `src/apr/quarantine.py`, `experiments/reproduce_table7.py` | Soundness and CI calculation | `results/generated/table7.*`, Figure 9 |
| 7.2 | Optional TLC comparison | `tla/modules/`, `scripts/cross_checkers.py` | TLC export comparison when a matching jar and export are supplied | `results/generated/cross_checker_agreement.json` |
| 8 | Limitations and threats to validity | `docs/FORMAL_MODEL.md`, `docs/ASSUMPTIONS.md` | Review against scope claims | `docs/MANUSCRIPT_CONSISTENCY_REPORT.md` |

