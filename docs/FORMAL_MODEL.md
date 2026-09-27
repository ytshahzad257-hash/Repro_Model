# Executable formal model

The finite artifact uses one bit per restricted source. `Read[i]`, `Derive[i]`, and `Load[i]` represent source acquisition, derivation, and admission to the working context. The global actions are `PrepareEffect`, `RequestRevoke`, `UpdatePolicy`, `Isolate`, `Fence`, `Persist`, `CommitCut`, `OpUse`, `FireEffect`, `Review`, `GenerateReport`, `Answer`, `ReportExport`, `Release`, `PrivateDeliberation`, `CleanPublicReconstruct`, and `GrantRevoke`.

The cut consists of policy update, isolation, fencing, evidence persistence, and commit. Governed isolation removes loaded restricted context while retaining evidence. SourceOnly leaves loaded context. IgnoreInfoChecks permits source-derived admission after isolation. UnguardedExport marks report export as an operational path without the release gate. DeleteEvidence removes retained evidence. IgnoreGrantChecks records a revoked grant but allows the protected effect path. TimedRelease keeps the approved payload public while making the logical release position secret dependent.

The implementation interprets the following paper objects:

- The effective cut is the `committed` state reached after the cut obligations.
- A prohibited source is represented by the loaded/derived state associated with a restricted source.
- Labels are immutable sets of source tags. `join` is set union, and a label is free when it is disjoint from the prohibited set.
- Admission is the transition that changes `loaded`; quarantine is represented by `Isolate` clearing operational loaded state while retaining an evidence flag.
- Review state is the sequence `Review`, `GenerateReport`, `Answer`.
- Approved release is `Release`. Its payload is the public constant `0`; for TimedRelease its complete observation also contains logical position.
- The complete operational observation contains emitted payloads and release position. Payload-only observation drops the position.
- Authorization is a separate grant flag and is checked independently of information safety.
- Clean reconstruction clears loaded state and represents recomputation from a public route.

The model abstracts away from physical wall-clock channels, resource contention, hardware caches, human memory, model-weight memorization, external copies, multiple principals, distributed cuts, repeated epochs, and arbitrary asynchronous queues. The trusted policy, mediator, recorder, evidence store, review interface, and release gate are modeled as specifications; this is not a refinement proof for a production runtime.
