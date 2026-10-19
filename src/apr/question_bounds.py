"""Theorem 1 on the executable model: private-evidence width per question class.

Histories H are the finite runs of the Governed model from the initial state
(secret 0) that end on first entering a committed (post-cut) state.  The
permitted operational view lambda(h) is the projection of h onto the events the
contract lets the former beneficiary distinguish at the cut: its own source
requests Read[i], the public policy events RequestRevoke and UpdatePolicy, and
pre-fence effect firings FireEffect.  For a question q, N_x(q) is the number
of distinct answers of q on the fibre lambda^{-1}(x); Theorem 1(ii) gives the
minimum fixed-width private record as ceil(log2 max_x N_x).

The computation is exact.  It is a forward dynamic program over nodes
(state, lambda-prefix, question accumulator), which counts histories without
enumerating them one by one.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from .model import TransitionSystem
from .policies import Configuration
from .state import State

ORDER_EVENTS = ("Isolate", "Fence", "Persist", "CommitCut")
PUBLIC_POLICY_EVENTS = ("RequestRevoke", "UpdatePolicy", "FireEffect")


def in_view(action: str) -> bool:
    return action.startswith("Read[") or action in PUBLIC_POLICY_EVENTS


def _bits(count: int) -> int:
    return math.ceil(math.log2(count)) if count > 1 else 0


@dataclass(frozen=True)
class QuestionBounds:
    sources: int
    histories: int
    fibers: int
    max_fiber_histories: int
    admission_classes: int
    order_classes: int
    final_state_classes: int
    family_classes: int

    def as_row(self) -> dict[str, object]:
        return {
            "sources": self.sources,
            "pre_cut_histories": self.histories,
            "operational_view_fibers": self.fibers,
            "max_fiber_histories": self.max_fiber_histories,
            "admission_classes_max": self.admission_classes,
            "admission_bits": _bits(self.admission_classes),
            "enforcement_order_classes_max": self.order_classes,
            "enforcement_order_bits": _bits(self.order_classes),
            "final_state_classes_max": self.final_state_classes,
            "final_state_bits": _bits(self.final_state_classes),
            "family_classes_max": self.family_classes,
            "family_bits": _bits(self.family_classes),
            "full_ex_post_classes_max": self.max_fiber_histories,
            "full_ex_post_bits": _bits(self.max_fiber_histories),
        }


def compute(sources: int, configuration: Configuration = Configuration.GOVERNED) -> QuestionBounds:
    system = TransitionSystem(configuration, sources=sources)
    start = system.initial(0)
    # node -> number of distinct histories reaching it
    # node = (state, view prefix, admitted mask, enforcement-order prefix)
    Node = tuple[State, tuple[str, ...], int, tuple[str, ...]]
    layer: dict[Node, int] = {(start, (), 0, ()): 1}
    histories_per_view: dict[tuple[str, ...], int] = defaultdict(int)
    answers: dict[tuple[str, ...], dict[str, set]] = defaultdict(lambda: {"adm": set(), "ord": set(), "fin": set(), "fam": set()})
    # Before the cut, each lifecycle action is phase-bounded and global
    # milestones occur once. Isolation clears loaded state but forbids later
    # governed reloads, so pre-cut runs are bounded and the graph is a DAG.
    while layer:
        nxt: dict[Node, int] = defaultdict(int)
        for (state, view, admitted, order), count in layer.items():
            for transition in system.transitions(state):
                action = transition.action
                target = transition.target
                new_view = view + (action,) if in_view(action) else view
                new_adm = admitted | (1 << int(action[5:-1])) if action.startswith("Load[") else admitted
                new_order = order + (action,) if action in ORDER_EVENTS else order
                if system.is_completion(target):
                    histories_per_view[new_view] += count
                    bucket = answers[new_view]
                    bucket["adm"].add(new_adm)
                    bucket["ord"].add(new_order)
                    bucket["fin"].add(target)
                    bucket["fam"].add((new_adm, new_order, target))
                else:
                    nxt[(target, new_view, new_adm, new_order)] += count
        layer = nxt
    return QuestionBounds(
        sources=sources,
        histories=sum(histories_per_view.values()),
        fibers=len(histories_per_view),
        max_fiber_histories=max(histories_per_view.values()),
        admission_classes=max(len(b["adm"]) for b in answers.values()),
        order_classes=max(len(b["ord"]) for b in answers.values()),
        final_state_classes=max(len(b["fin"]) for b in answers.values()),
        family_classes=max(len(b["fam"]) for b in answers.values()),
    )


def enumerate_histories(sources: int, configuration: Configuration = Configuration.GOVERNED):
    """Brute-force enumeration (for tests on small K)."""

    system = TransitionSystem(configuration, sources=sources)
    stack = [(system.initial(0), ())]
    while stack:
        state, history = stack.pop()
        for transition in system.transitions(state):
            extended = history + (transition.action,)
            if system.is_completion(transition.target):
                yield extended, transition.target
            else:
                stack.append((transition.target, extended))
