# Manuscript consistency report

This report is generated from the executable artifact. Expected paper values are read from `results/expected/`; they are never used by the model.

## Current revision reconstruction checks

| Configuration | Field | Expected reconstruction value | Observed | Status |
| --- | --- | ---: | ---: | --- |
| Governed | state_count_s0 | 356 | 356 | MATCH |
| Governed | state_count_s1 | 356 | 356 | MATCH |
| Governed | transitions | 1053 | 1053 | MATCH |
| Governed | information_safety | holds | holds | MATCH |
| Governed | authorization_safety | holds | holds | MATCH |
| Governed | review_failures | 0 | 0 | MATCH |
| Governed | product_states | 356 | 356 | MATCH |
| Governed | synchronous_observations | equal | equal | MATCH |
| Governed | payload_only | equal | equal | MATCH |
| Governed | witness_length | None | None | MATCH |
| SourceOnly | state_count_s0 | 500 | 500 | MATCH |
| SourceOnly | state_count_s1 | 500 | 500 | MATCH |
| SourceOnly | transitions | 1500 | 1500 | MATCH |
| SourceOnly | information_safety | violated | violated | MATCH |
| SourceOnly | authorization_safety | holds | holds | MATCH |
| SourceOnly | review_failures | 0 | 0 | MATCH |
| SourceOnly | product_states | 500 | 500 | MATCH |
| SourceOnly | synchronous_observations | differ | differ | MATCH |
| SourceOnly | payload_only | differ | differ | MATCH |
| SourceOnly | witness_length | 10 | 10 | MATCH |
| IgnoreInfoChecks | state_count_s0 | 988 | 988 | MATCH |
| IgnoreInfoChecks | state_count_s1 | 988 | 988 | MATCH |
| IgnoreInfoChecks | transitions | 3358 | 3358 | MATCH |
| IgnoreInfoChecks | information_safety | violated | violated | MATCH |
| IgnoreInfoChecks | authorization_safety | holds | holds | MATCH |
| IgnoreInfoChecks | review_failures | 0 | 0 | MATCH |
| IgnoreInfoChecks | product_states | 988 | 988 | MATCH |
| IgnoreInfoChecks | synchronous_observations | differ | differ | MATCH |
| IgnoreInfoChecks | payload_only | differ | differ | MATCH |
| IgnoreInfoChecks | witness_length | 11 | 11 | MATCH |
| UnguardedExport | state_count_s0 | 224 | 224 | MATCH |
| UnguardedExport | state_count_s1 | 224 | 224 | MATCH |
| UnguardedExport | transitions | 553 | 553 | MATCH |
| UnguardedExport | information_safety | violated | violated | MATCH |
| UnguardedExport | authorization_safety | holds | holds | MATCH |
| UnguardedExport | review_failures | 0 | 0 | MATCH |
| UnguardedExport | product_states | 224 | 224 | MATCH |
| UnguardedExport | synchronous_observations | differ | differ | MATCH |
| UnguardedExport | payload_only | differ | differ | MATCH |
| UnguardedExport | witness_length | 14 | 14 | MATCH |
| DeleteEvidence | state_count_s0 | 176 | 176 | MATCH |
| DeleteEvidence | state_count_s1 | 176 | 176 | MATCH |
| DeleteEvidence | transitions | 435 | 435 | MATCH |
| DeleteEvidence | information_safety | holds | holds | MATCH |
| DeleteEvidence | authorization_safety | holds | holds | MATCH |
| DeleteEvidence | review_failures | 312 | 312 | MATCH |
| DeleteEvidence | product_states | 176 | 176 | MATCH |
| DeleteEvidence | synchronous_observations | equal | equal | MATCH |
| DeleteEvidence | payload_only | equal | equal | MATCH |
| DeleteEvidence | witness_length | None | None | MATCH |
| IgnoreGrantChecks | state_count_s0 | 460 | 460 | MATCH |
| IgnoreGrantChecks | state_count_s1 | 460 | 460 | MATCH |
| IgnoreGrantChecks | transitions | 1373 | 1373 | MATCH |
| IgnoreGrantChecks | information_safety | holds | holds | MATCH |
| IgnoreGrantChecks | authorization_safety | violated | violated | MATCH |
| IgnoreGrantChecks | review_failures | 0 | 0 | MATCH |
| IgnoreGrantChecks | product_states | 460 | 460 | MATCH |
| IgnoreGrantChecks | synchronous_observations | equal | equal | MATCH |
| IgnoreGrantChecks | payload_only | equal | equal | MATCH |
| IgnoreGrantChecks | witness_length | None | None | MATCH |
| TimedRelease | state_count_s0 | 356 | 356 | MATCH |
| TimedRelease | state_count_s1 | 356 | 356 | MATCH |
| TimedRelease | transitions | 1053 | 1053 | MATCH |
| TimedRelease | information_safety | holds | holds | MATCH |
| TimedRelease | authorization_safety | holds | holds | MATCH |
| TimedRelease | review_failures | 0 | 0 | MATCH |
| TimedRelease | product_states | 356 | 356 | MATCH |
| TimedRelease | synchronous_observations | differ | differ | MATCH |
| TimedRelease | payload_only | equal | equal | MATCH |
| TimedRelease | witness_length | 13 | 13 | MATCH |
| K=1 | states | 356 | 356 | MATCH |
| K=1 | transitions | 1053 | 1053 | MATCH |
| K=1 | product_states | 356 | 356 | MATCH |
| K=1 | delete_evidence_review_failures | 312 | 312 | MATCH |
| K=2 | states | 1792 | 1792 | MATCH |
| K=2 | transitions | 5354 | 5354 | MATCH |
| K=2 | product_states | 1792 | 1792 | MATCH |
| K=2 | delete_evidence_review_failures | 1560 | 1560 | MATCH |
| K=3 | states | 6896 | 6896 | MATCH |
| K=3 | transitions | 20886 | 20886 | MATCH |
| K=3 | product_states | 6896 | 6896 | MATCH |
| K=3 | delete_evidence_review_failures | 5928 | 5928 | MATCH |
| K=4 | states | 24016 | 24016 | MATCH |
| K=4 | transitions | 74330 | 74330 | MATCH |
| K=4 | product_states | 24016 | 24016 | MATCH |
| K=4 | delete_evidence_review_failures | 20280 | 20280 | MATCH |
| receipts/admission | verdict | insufficient | insufficient | MATCH |
| receipts/admission | explored_product_nodes | 89 | 89 | MATCH |
| receipts/order | verdict | sufficient | sufficient | MATCH |
| receipts/order | explored_product_nodes | 89 | 89 | MATCH |
| receipts/causal | verdict | insufficient | insufficient | MATCH |
| receipts/causal | explored_product_nodes | 89 | 89 | MATCH |
| admission_ledger_only/admission | verdict | sufficient | sufficient | MATCH |
| admission_ledger_only/admission | explored_product_nodes | 1601 | 1601 | MATCH |
| admission_ledger_only/order | verdict | insufficient | insufficient | MATCH |
| admission_ledger_only/order | explored_product_nodes | 1601 | 1601 | MATCH |
| admission_ledger_only/causal | verdict | insufficient | insufficient | MATCH |
| admission_ledger_only/causal | explored_product_nodes | 1601 | 1601 | MATCH |
| receipts_plus_admission_ledger/admission | verdict | sufficient | sufficient | MATCH |
| receipts_plus_admission_ledger/admission | explored_product_nodes | 41 | 41 | MATCH |
| receipts_plus_admission_ledger/order | verdict | sufficient | sufficient | MATCH |
| receipts_plus_admission_ledger/order | explored_product_nodes | 41 | 41 | MATCH |
| receipts_plus_admission_ledger/causal | verdict | insufficient | insufficient | MATCH |
| receipts_plus_admission_ledger/causal | explored_product_nodes | 41 | 41 | MATCH |
| full_mediator_log/admission | verdict | sufficient | sufficient | MATCH |
| full_mediator_log/admission | explored_product_nodes | 31 | 31 | MATCH |
| full_mediator_log/order | verdict | sufficient | sufficient | MATCH |
| full_mediator_log/order | explored_product_nodes | 31 | 31 | MATCH |
| full_mediator_log/causal | verdict | insufficient | insufficient | MATCH |
| full_mediator_log/causal | explored_product_nodes | 31 | 31 | MATCH |
| K=3 | pre_cut_histories | 3626241 | 3626241 | MATCH |
| K=3 | operational_view_fibers | 7 | 7 | MATCH |
| K=3 | admission_bits | 3 | 3 | MATCH |
| K=3 | enforcement_order_bits | 3 | 3 | MATCH |
| K=3 | final_state_bits | 6 | 6 | MATCH |
| K=3 | full_ex_post_bits | 7 | 7 | MATCH |
| u=0.10 | quarantined | 0.721735 | 0.721735 | MATCH |
| u=0.10 | truly_dependent | 0.014935 | 0.014935 | MATCH |
| u=0.10 | over_quarantine_ratio | 0.9781911451489019 | 0.9781911451489019 | MATCH |
| u=0.10 | withheld_clean | 0.7068 | 0.7068 | MATCH |
| u=0.25 | quarantined | 0.72106 | 0.72106 | MATCH |
| u=0.25 | truly_dependent | 0.057265 | 0.057265 | MATCH |
| u=0.25 | over_quarantine_ratio | 0.9247113507244 | 0.9247113507244 | MATCH |
| u=0.25 | withheld_clean | 0.663795 | 0.663795 | MATCH |
| u=0.50 | quarantined | 0.71667 | 0.71667 | MATCH |
| u=0.50 | truly_dependent | 0.22098500000000001 | 0.22098500000000001 | MATCH |
| u=0.50 | over_quarantine_ratio | 0.7047021666447514 | 0.7047021666447514 | MATCH |
| u=0.50 | withheld_clean | 0.495685 | 0.495685 | MATCH |
| u=0.75 | quarantined | 0.72948 | 0.72948 | MATCH |
| u=0.75 | truly_dependent | 0.494025 | 0.494025 | MATCH |
| u=0.75 | over_quarantine_ratio | 0.34450776128960714 | 0.34450776128960714 | MATCH |
| u=0.75 | withheld_clean | 0.235455 | 0.235455 | MATCH |
| u=1.00 | quarantined | 0.71476 | 0.71476 | MATCH |
| u=1.00 | truly_dependent | 0.71476 | 0.71476 | MATCH |
| u=1.00 | over_quarantine_ratio | 0.0 | 0.0 | MATCH |
| u=1.00 | withheld_clean | 0.0 | 0.0 | MATCH |

## Specification and environment findings

| Category | Manuscript location | Evidence | Recommended action |
| --- | --- | --- | --- |
| PROVENANCE | Section 7.2 | The historical checker pair, TLC runtime, original seeds, and original recorder automata were not supplied. | The manuscript now identifies the Python output as an independent reconstruction and makes no Python/TLC agreement claim. |
| TLC STATUS | Section 7.2 | TLC was unavailable in the current environment. | The TLA+ files remain a separately documented reference specification; TLC validation is pending external execution. |
| HISTORICAL VALUES | Sections 7.3–7.5 | Earlier paper assertions are preserved under `results/historical_paper_assertions/`. | Current tables and figures use the generated reconstruction values. |
| STOCHASTIC PROVENANCE | Section 7.5 | Historical seeds were not supplied. | The current generator uses declared seeds and labels the results as reconstruction evidence. |

Generated reconstruction checks: 136; matches: 136; unexplained mismatches: 0.
