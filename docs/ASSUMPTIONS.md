# Assumptions and reconstruction boundary

The supplied manuscript describes the action vocabulary and configuration intent but does not include the historical TLA+ modules, TLC configurations, Python explorer, full state vector, action guards, recorder/question automata, seeds, or exact synthetic generator. The current repository makes the following choices explicit.

1. A source has three monotone per-source flags: read, derived, and loaded.
2. A revocation request requires a loaded representation.
3. The reference path requires isolation and fencing before evidence persistence.
4. Review follows the sequence Review, GenerateReport, and Answer; release is a separate gated action.
5. Review failures are counted as committed states in which deleted evidence cannot answer.
6. The operational comparison pairs identical public action sequences; Algorithm 1 uses an asynchronous product over recorder tokens.
7. Timed release is represented as a logical observation component.
8. The sufficiency experiment uses a newly declared compact 16-history finite LTS. Its verdicts are reconstruction evidence, while the unavailable historical automata and node counts remain unresolved.
9. Synthetic workflows use 20 sources, 100 derived items, restricted probability 0.1, fan-in 3, explicit seeds, five use-probability settings, and nine growth settings. Full mode contains 28,000 workflows.
10. The current Python results are generated under the environment recorded in each metadata sidecar. TLC was unavailable for the present revision, and no Python/TLC agreement is claimed.
11. The TLA+ modules are a separate reference specification. Their scalar source state and fixed product abstraction are not presented as a recovered copy of the historical K-parametric implementation.
12. These choices are scientific reconstruction assumptions. They must be replaced or narrowed if the authors later supply the historical implementation and inputs.

These assumptions are evidence boundaries, not result-matching adjustments. The historical manuscript assertions remain under results/historical_paper_assertions/.
