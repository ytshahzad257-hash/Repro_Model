# Executable formal model

The Python implementation (`src/apr/model.py`) and independent TLA+ specification
(`tla/v5/APRSemantics.tla`, `APR.tla`, `APRProduct.tla`) implement this description.
They share only case inputs in `experiments/finite_cases.py`, not semantic code.
`results/generated/cross_checker_agreement.json` is the authoritative comparison summary.

## State and parameters

One immutable record holds the secret valuation, per-source `read`, `derived`, `loaded`
and `session_cache` flags, and the administrative/effect/review flags listed in the TLA+
`InitState`. A load sets both loaded and cache flags when caching is enabled. Initial
flags are false. All actions set monotone lifecycle flags except isolation/reconstruction
clearing memory. State space exploration follows all enabled actions, including cycles
caused by clearing and reloading in the information-check mutation.

`secrets="shared"` uses a single bit for all sources. `secrets="independent"` uses an
integer bit vector with one bit per source. `revoked` is a nonempty source subset;
other sources retain access after the cut. TLA+ represents independent operational
payloads as bit-indexed functions, Python as equivalent integer bit vectors: equality
within each product is equivalent. This representational difference is not a refinement
claim or a direct comparison of payload byte encodings.

## Action guards and successors

- `Read[i]`: a not-yet-read source; after policy update, a revoked source is fenced
  unless IgnoreInfoChecks. Nonrevoked sources remain readable.
- `Derive[i]` / `Load[i]`: preceding lifecycle stage complete; revoked sources cannot
  derive/load after isolation unless IgnoreInfoChecks. Load sets persistent cache.
- `PrepareEffect`: loaded context exists, no earlier preparation, not fenced.
- `RequestRevoke`: exogenous, once, before commit. No prior read/load required.
- `UpdatePolicy`: follows request; fences the revoked source route.
- `Isolate`: follows update; clears loaded and cache flags for revoked sources,
  except SourceOnly. DeleteEvidence additionally destroys the evidence.
- `Fence`: follows update; holds pending effects.
- `Persist`: follows isolation and fencing. `CommitCut`: follows persistence.
- `FireEffect`: prepared, not already fired, and not fenced; public acknowledgment.
- `OpUse`: committed, not already used, an item/cache/export/release/public
  reconstruction exists, and grant checks permit it. RefusalMutation additionally
  refuses when the first revoked bit is one. Use sets the information-violation flag
  exactly when a revoked loaded/cache item or an exported report is consumed;
  the authority flag is set for ignored revoked grants. Approved releases are exempt
  from the prohibited raw-input flag by explicit authorization.
- `Review`, `GenerateReport`, `Answer`: ordered service steps after commit and
  persistence. Answer is unavailable after evidence deletion.
- `ReportExport`: only UnguardedExport, after an answered review.
- `Release`: gated reviewed content, once. Constant public payload except
  ApprovedSecretRelease, which releases the entire encoded secret valuation.
- `DelayRelease`: TimedRelease only, first revoked bit one, internal and once,
  before the release becomes enabled.
- `PrivateDeliberation`: once after commit; no operational observation.
- `CleanPublicReconstruct`: once after commit; sets public reconstruction and clears
  ordinary loaded state. It does **not** clear an independent persistent cache.
- `GrantRevoke`: once after commit.

Operational use returns an exported secret if a report was exported; otherwise it
returns the loaded/cached source valuation when present; otherwise it uses the approved
release if available, or the independent public constant. In partial-revocation mode,
nonrevoked memory may legitimately determine its own output bits.

## Configurations

Governed enforces every modeled obligation. SourceOnly retains loaded/cache residue;
IgnoreInfoChecks permits forbidden reloads; UnguardedExport permits report re-entry;
DeleteEvidence loses review; IgnoreGrantChecks ignores the operation grant;
TimedRelease exposes logical release position; ApprovedSecretRelease tests explicit
nonconstant declassification; RefusalMutation tests secret-dependent public enabledness.

## Properties and products

Information/authority safety mean their violation flags remain false. Python review
availability asks whether an answered review is reachable from every committed state;
TLA+ checks `ReviewPossible` (no destroyed evidence after commitment), equivalent here
because the remaining review service steps are enabled independently of other actions.
This is existential service reachability, not a liveness guarantee under every schedule.

A product synchronizes public actions and permits unilateral internal delay actions.
The full observer compares public enabledness (including refusals), kind, payload and
logical position. The payload-only observer compares accepted joint payloads and
intentionally ignores refused requests. Product transitions are enabled moves, not a
Cartesian product of all single-copy transitions. Equal-release comparison uses the
same pair for constant releases; for the injective secret release it uses the two
initial diagonal pairs. It therefore validates conditioning, not secrecy between
unequal secrets. TLC generated-state counts subtract the number of initial states.

Each TLC count job explores the entire graph. Separate property jobs stop at the first
counterexample, avoiding enormous redundant error traces. An incomplete count, an
unexpected TLC error, missing cases or a compared-field mismatch causes failure.

## Declared finite coverage

`finite_cases.py` declares shared-secret cases through five sources and representative
independent-secret pairs through three sources. Independent baselines alternate bits;
the other world flips either the first source alone or every source, with exactly those
sources revoked. These are representative pairs, not all assignments/subsets. The two
one-source pattern names denote the same pair. Cache-off controls compare the original
configurations at one source; the full cross-check includes caching enabled.

## Evidence bounds and sufficiency

Theorem 1 histories end on first entering a committed state in Governed. The permitted
view projects source reads, RequestRevoke, UpdatePolicy and FireEffect. Exact dynamic
programming computes history/fiber/class counts; the larger calculation has explicit
RSS and elapsed-time budgets and records success or the measured limit.

Algorithm 1 uses the pre-cut model with each Load split into hidden use/ignore choices.
Receipts record policy/enforcement/effect actions; the admission ledger records loads;
the full mediator log erases the hidden kernel-use distinction. Hidden use is an
illustrative executable construction, not measured LLM causation.

## Connection to the formal contract

Task steps exclude release-interface steps: the former satisfy A2 and the latter
are governed by A4. R1–R3 propagation applies to task computations, while R6/R7
provide the explicit private-review and approved-release interfaces. Dependencies are representation sets. Runtime labels are tag sets. The contract's
injective source-version map converts projected dependencies to tags before stating a
label upper bound. Approved release paths are cut consistently in release-relative
dependence; clean reconstruction instead requires raw independence. The runtime theorem
uses a source-scoped prohibited set. The general contract permits broader sets, which
need an additional policy mechanism. Equal pre-cut public inputs, equal approved views
and the common post-cut strategy remain explicit premises. The graph-only minimality proposition concerns pre-release graphs without declassification
edges; it does not demand quarantine of authorized released views. No checker count agreement
establishes those premises for the prototype or a production system.
