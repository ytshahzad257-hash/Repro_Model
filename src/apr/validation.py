"""Invariant and result validation helpers."""

from __future__ import annotations

from .explorer import Reachability, explore
from .model import TransitionSystem


def validate_reachability(system: TransitionSystem) -> tuple[Reachability, Reachability]:
    """Run both secret copies and assert the finite-state safety invariants."""

    zero = explore(system, 0)
    one = explore(system, 1)
    return zero, one


def shortest_action_trace(system: TransitionSystem, secret: int, predicate) -> tuple[str, ...] | None:
    result = explore(system, secret)
    candidates = [result.paths[state] for state in result.states if predicate(state)]
    return min(candidates, key=lambda path: (len(path), path), default=None)
