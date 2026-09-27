# Architecture

The artifact has four independent layers.

`src/apr/model.py` defines the finite transition system. A `State` is immutable and hashable. `TransitionSystem.enabled_actions` computes guards in a fixed order and `successor` applies one action. `policies.py` holds only named semantic switches; it does not contain paper result values.

`src/apr/explorer.py` performs deterministic breadth-first reachability for each secret, counts edges, records shortest paths, and computes synchronized observation comparisons. `self_composition.py` exposes the complete versus payload-only comparison. The comparison uses the same public action sequence on both one-bit worlds; Algorithm 1 has its own asynchronous product because its theorem concerns recorder tokens and silent steps.

`src/apr/sufficiency.py` is independent of the finite model. It accepts a generic labeled transition system, a deterministic recorder, and a completion set. It implements silent left/right moves, equal-token joint moves, bad-state detection, BFS parent pointers, and witness reconstruction.

`src/apr/labels.py` and `src/apr/quarantine.py` implement the conservative label and synthetic dependence layers. The synthetic kernel samples actual use separately from admission, so clean-but-quarantined items can occur.

The experiment scripts consume the modules and write machine-readable results, tables, figures, witness files, and provenance sidecars. `tla/` is maintained separately and is never imported by the Python model. `scripts/cross_checkers.py` compares a machine-readable TLC export with Python when TLC is available.
