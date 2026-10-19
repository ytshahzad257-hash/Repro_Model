# Assumptions and interpretation choices

The original implementation of versions 1–4 was not preserved. Version 5 introduced a
documented reconstruction and replaced the earlier numerical assertions. Version 5.1 is
preserved as the baseline, including its expected values in
`results/historical_paper_assertions/revision5_1_expected.json`. Version 6 extends that
executable baseline. No historical numbers are treated as independently reproduced.

## Formal model

1. One beneficiary, operational context, effective cut and fixed post-cut policy epoch.
2. Revocation is exogenous. Update fences the revoked source route, isolation clears
   revoked loaded/session state, and fencing holds pending effects. Persistence follows
   isolation and fencing; commitment follows persistence. This is one allowed commit rule.
3. Sources outside the revoked subset retain permission. Independent mode has one bit
   per source; the declared pairs change only revoked bits. Coverage is representative.
4. Session cache is a distinct persistent flag. A clean public derivation does not itself
   reset that cache. SourceOnly keeps it; governed isolation clears revoked components.
5. The release gate may approve a secret-valued payload. Full raw noninterference then
   fails legitimately; equal-release comparisons are the theorem's domain. For an injective
   release equal-release secret pairs are diagonal. The separate release record retains
   source provenance despite an empty operational admission label.
6. Refusals are visible public enabledness differences. Payload-only comparisons are
   deliberately weaker. Logical step position is modeled; physical time is excluded.
7. Review availability is reachability of an answer, conditional on service, not universal
   scheduler fairness. DeleteEvidence is the negative control.
8. Theorem 1 needs the permitted view as decoder side information. Its logical index
   bound excludes the cost of retaining that view, identifiers, integrity and serialization.
9. Least quarantine concerns graphs without approved release nodes or declassification
   edges and is relative to finite acyclic event graphs, unrestricted tuple payloads
   and the declared control-state-aware scheduler class. Fixed kernels can have smaller
   sufficient quarantines; a lower dependence bound cannot certify that an item is clean.
10. Public inputs are exogenous authorized roots, held fixed in the realization's
    dependence semantics. Internally derived queries remain labeled task outputs. The proof's labels bound source-tag projections of release-relative representation
    dependencies. Raw dependence through an approved view can remain authorized. Clean
    reconstruction has the stronger raw-independence requirement.

## Synthetic workflows

11. Source restriction flags are sampled independently, forcing one if none was sampled.
    Uniform/recency/Zipf selection admits inputs without replacement. Recency decay and
    Zipf exponent are explicit generator parameters recorded in result metadata.
12. Used-edge dependence is sampled ground truth. CLR propagates all admitted inputs,
    so soundness follows structurally; it is not a test of complete real-world capture.
13. Uniform experiments share graphs and nested use draws across use probabilities.
    Correlated use chooses an all-input kernel or independent use; its marginal rate
    differs from nominal u. First-only always uses the first admitted input and ignores u.
    Overlapping fixed-length/growth points are repeated executions, not independent new
    samples. Coverage JSON discloses unique seed/parameter pairs and verifies raw metrics.
14. Workflow confidence intervals are normal intervals for means over workflow seeds.
    The over-quarantine ratio is the mean of ratios among nonempty quarantines, not a
    pooled item ratio. Per-seed metrics and aggregate settings are saved separately.
15. Item fractions do not establish affordability or task utility.

## Instrumented local-model prototype

16. Data are fictional supplier quote records. Three category labels cycle in task metadata
    without entering model prompts or creating distinct workflows. Revocation affects one
    restricted source; other restricted sources remain permitted for this beneficiary.
17. SourceOnly retains previously loaded raw-record copies and derivatives; no new source
    fetch is executed after the cut. DeleteAll removes affected memory and evidence;
    CLR quarantines it; reconstruction uses only the surviving allowed inputs.
18. Model confinement is implemented by constructing every prompt from the selected
    memory list and carrying all session/cache/queued-argument payloads as labeled items.
    Calls use an explicit context limit and output limits. This is not a proof of every
    R1–R8 premise, physical isolation or model-weight unlearning.
19. The reported provider/model/settings are recorded in summary JSON and raw calls.
    API-key-free stub results are a separate deterministic control, not LLM measurements.
    Raw per-task records are resumable. A run resumed after interruption retains completed
    tasks; a partially completed, unpersisted task is rerun with the same seed/settings.
20. Exact/fuzzy leakage metrics apply to the follow-up responses. Exact leakage means the
    revoked formatted price or its code appears verbatim; fuzzy leakage means the code
    appears case-insensitively or a number lies within 1% of the revoked price. They do not detect all
    semantic disclosure. Fuzzy numeric matching can flag unrelated permitted values or
    the public budget threshold; an approved Boolean finding is intentionally disclosed.
21. Task success uses the predeclared exact supplier/price JSON predicate. No output
    repair, answer substitution, prompt retuning or model change is used to raise success.
22. Three paired full-DAG canary substitutions detect some sensitivity. No detected
    change is evidence about that intervention only, not certified independence or a
    complete dependence upper bound. Baseline instability is reported separately.
23. Audit answers are scored against a separate full evaluator trace. The declared
    logical-bit comparison uses a history class allowing every slot/source admission mask,
    including faulty admission, and two enforcement orders with fixed task side information.
    It is tight for that declared unconstrained class, not for the fixed program's narrower
    reachable histories, and does not imply online compression of the JSON ledger.
    The primary utility predicate requires literal supplier/price fields. A separately labeled
    retrospective key-name diagnostic preserves canonical supplier and exact-value checks;
    it does not replace the primary score or constitute general semantic grading.
24. Binary task intervals are Wilson intervals, including nonzero uncertainty when no
    event is observed. Continuous means use normal intervals. Intervals describe this
    generator and model, not all enterprise workloads.
25. Shared pre-cut calls are charged to every condition. Counterfactual-validation calls
    are excluded from condition cost. Label-operation timing covers the instrumented
    joins/filtering, not an entire deployed provenance service. Seconds/call is an
    aggregate ratio; timing is shared-machine observation, not a controlled capacity test.

## Provenance and release

26. Source snapshots record the actual Git commit/dirty state at process start and a hash
    including recursive experiment sources, scripts, TLA+ modules, seeds and pyproject.
    Runs made from an uncommitted working tree are recorded as such. Reaggregation metadata identifies the aggregation source; it does not relabel older raw model calls as executions of that later source.
27. Generated raw evidence is included in the final manifest. Git internals, caches,
    editable-install metadata and TeX build intermediates are excluded. Checksums are
    regenerated after software reports and outputs are saved, then verified.
28. Archival release (tag and persistent identifier) is performed by the authors.

## Version 6.2 measurement amendment (finite semantics unchanged)

The new experiment preserves task values/seeds, leakage functions, twelve-question battery, three paired full-DAG interventions and audit comparators. Explicit record fields and a literal supplier/price schema replace the ambiguous prompt. The primary predicate source remains unchanged; a separately declared secondary predicate requires the correct canonical cheapest ID and any finite numeric price. NoRevocation has no cut or release and a correctly empty order trace; its canary emissions are permitted, not violations. The cheapest quote remains permitted by the existing synthetic price bands, limiting the task's utility interpretation.

Warm-up outputs/scores are discarded. The timing-only sample decision precedes main calls and selects the predeclared prefix. Resumptions check protocol, workload and pinned runtime/model identity. The new deterministic stub deduplicates identical parsed quote triples to prevent recursive text duplication; this implementation repair occurred before any 6.2 model inference and does not change the model prompts, primary predicate or old stub. Earlier stub implementation trials are excluded from reported evidence.

Wilson intervals describe binary task proportions. Paired utility differences use exact conditional McNemar tests and conservative pointwise confidence intervals from Bonferroni simultaneous Clopper-Pearson discordant-cell bounds. Holm adjustment covers both utility endpoints across the four revocation contrasts. CLR input exclusion is runtime enforced; its zero exact matches, when observed, are an implementation check, not independent validation of general causal exclusion. The old model's nominal zero strict success is a schema-confounded measurement and is not a utility finding.

The preserved template field cycles category labels in task metadata but is not inserted into model prompts. These are quote-set tasks; the metadata labels are not evidence of three distinct model-visible workflows. The frozen preregistration retains its original template terminology, and this clarification changes only the interpretation, not the prompts or tasks.

The confidence-interval and test interpretation is nominal and assumes independent task sampling at a fixed sample size. Five tasks used for the timing-only sample decision are rerun in the main prefix. Because task runtime can correlate with task difficulty, coverage conditional on this adaptive timing decision is not established. This limitation does not change the frozen sample rule, endpoint definitions or analysis.

## Version 6.3 decision experiment

The new variant overrides only the designated restricted target's amount/price/payload, making it strictly cheapest at a seed-drawn discount below the next quote. Only that source is revoked; all other quotes remain allowed. All tasks remain in the fixed primary sample, including incorrect pre-cut plans. NoRevocation has no cut and its target selection is permitted.

The primary post-cut plan omits a separate permission-ID list and relies on the surviving memory store. The secondary prompt retains the exact earlier list. Cut/operational methods are inherited unchanged. SourceOnly retains loaded raw-record copies as well as derivatives, so a uniquely derived-memory cause is not identified. E1 scores a plan; execution-boundary checks are outside this experiment. The approved threshold finding is constant on this low-price variant, which adds no release-channel coverage beyond the existing finite cases.

The first scored decision precedes the canary battery. Counterfactual sensitivity replay is omitted because it is not an endpoint of this new decision study; earlier sensitivity data remain unchanged. Primary six-test inference has a fixed sample; optional-arm eligibility alone depends on discarded timing tasks. The optional arm is descriptive. Pilot cache/shared-machine effects can affect its eligibility. Exact intervals are conservative and pointwise, not an inversion of McNemar tests. All frozen prompts, scores and sample rules remain unchanged after inference begins.
