"""Compute question-class counts from the executable model."""

from __future__ import annotations

import csv
import json
import math
from functools import lru_cache

from apr.model import TransitionSystem
from apr.policies import Configuration

from common import GENERATED, provenance, write_csv, write_json


def compute_for_sources(sources: int) -> dict[str, object]:
    system = TransitionSystem(Configuration.GOVERNED, sources=sources)
    initial = system.initial(0)

    @lru_cache(maxsize=None)
    def path_count(state) -> int:
        if state.committed:
            return 1
        return sum(path_count(transition.target) for transition in system.transitions(state))

    pre_cut_histories = sum(path_count(transition.target) for transition in system.transitions(initial) if not transition.target.committed)
    # The operational view is a declared projection: public cut flags and the
    # beneficiary's loaded mask. It is computed from reachable states, not a
    # copied paper number.
    seen = {initial}
    frontier = [initial]
    while frontier:
        state = frontier.pop()
        for transition in system.transitions(state):
            if not transition.target.committed and transition.target not in seen:
                seen.add(transition.target)
                frontier.append(transition.target)
    fibers = {}
    for state in seen:
        key = (state.request_revoke, state.policy_updated, state.isolated, state.fenced, state.evidence_persisted)
        fibers.setdefault(key, []).append(state)
    admission_classes = max((len({state.loaded_mask for state in values}) for values in fibers.values()), default=1)
    final_classes = max((len({(state.loaded_mask, state.derived, state.read) for state in values}) for values in fibers.values()), default=1)
    full_classes = max((len(values) for values in fibers.values()), default=1)
    return {
        "sources": sources,
        "pre_cut_histories": pre_cut_histories,
        "operational_view_fibers": len(fibers),
        "admission_bits": math.ceil(math.log2(max(1, admission_classes))),
        "enforcement_order_bits": math.ceil(math.log2(max(1, len(fibers)))),
        "final_state_bits": math.ceil(math.log2(max(1, final_classes))),
        "full_ex_post_bits": math.ceil(math.log2(max(1, full_classes))),
        "state_count": len(seen),
    }


def run() -> list[dict[str, object]]:
    rows = [compute_for_sources(sources) for sources in (1, 2, 3)]
    metadata = provenance(experiment="question_class_bounds", inputs={"sources": [1, 2, 3]})
    write_json(GENERATED / "question_class_bounds.json", {"rows": rows, "metadata": metadata})
    write_csv(GENERATED / "question_class_bounds.csv", rows)
    write_json(GENERATED / "question_class_bounds.metadata.json", metadata)
    return rows


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
