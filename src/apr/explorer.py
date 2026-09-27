"""Deterministic explicit-state breadth-first exploration."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from .model import Observation, Transition, TransitionSystem
from .state import State


@dataclass(frozen=True, slots=True)
class Path:
    state: State
    actions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Reachability:
    initial: State
    states: frozenset[State]
    transitions: int
    paths: dict[State, tuple[str, ...]]
    info_safe: bool
    auth_safe: bool
    review_failures: int


@dataclass(frozen=True, slots=True)
class ObservationWitness:
    left: Path
    right: Path
    left_observation: tuple[tuple[object, ...], ...]
    right_observation: tuple[tuple[object, ...], ...]


def explore(system: TransitionSystem, secret: int) -> Reachability:
    """Explore all reachable states using deterministic BFS."""

    initial = system.initial(secret)
    queue: deque[State] = deque([initial])
    states: set[State] = {initial}
    paths: dict[State, tuple[str, ...]] = {initial: ()}
    transitions = 0
    info_safe = True
    auth_safe = True
    while queue:
        state = queue.popleft()
        info_safe = info_safe and system.info_safe(state)
        auth_safe = auth_safe and system.auth_safe(state)
        for transition in system.transitions(state):
            transitions += 1
            target = transition.target
            if target not in states:
                states.add(target)
                paths[target] = paths[state] + (transition.action,)
                queue.append(target)
    # A review failure is a reachable committed state in which the contract's
    # retained evidence was deleted. States before the review service runs are
    # schedulable and are therefore not counted as failures.
    review_failures = sum(1 for state in states if state.committed and state.evidence_deleted)
    return Reachability(initial, frozenset(states), transitions, paths, info_safe, auth_safe, review_failures)


def shortest_completion_paths(system: TransitionSystem, secret: int) -> tuple[Path, ...]:
    """Return one shortest path for each reachable completion state."""

    result = explore(system, secret)
    return tuple(
        Path(state, result.paths[state])
        for state in sorted(result.states, key=lambda item: (len(result.paths[item]), result.paths[item]))
        if system.is_completion(state)
    )


def _event_signature(path: Path, system: TransitionSystem, *, payload_only: bool) -> tuple[tuple[object, ...], ...]:
    events: list[tuple[object, ...]] = []
    state = system.initial(path.state.secret)
    for position, action in enumerate(path.actions, start=1):
        transition = system.successor(state, action)
        observation = transition.observation
        if observation is None:
            state = transition.target
            continue
        if observation.kind == "release":
            if payload_only:
                events.append(("release", observation.payload))
            else:
                timing = position + (1 if system.policy.release_timing_depends_on_secret and state.secret else 0)
                events.append(("release", observation.payload, timing))
        else:
            events.append((observation.kind, observation.payload))
        state = transition.target
    return tuple(events)


def observation_witness(system: TransitionSystem, *, payload_only: bool = False) -> ObservationWitness | None:
    """Find the first shortest pair of completion histories with differing observations."""

    # The paper compares post-cut operational traces. Requiring an operational
    # use in the witness avoids reporting a release-only prefix when a later
    # use is the first meaningful observation.
    left_paths = tuple(path for path in shortest_completion_paths(system, 0) if path.state.op_uses >= 1)
    right_paths = tuple(path for path in shortest_completion_paths(system, 1) if path.state.op_uses >= 1)
    left_signatures = {id(path): _event_signature(path, system, payload_only=payload_only) for path in left_paths}
    right_signatures = {id(path): _event_signature(path, system, payload_only=payload_only) for path in right_paths}
    candidates: list[ObservationWitness] = []
    right_by_actions: dict[tuple[str, ...], list[Path]] = {}
    for right in right_paths:
        right_by_actions.setdefault(right.actions, []).append(right)
    for left in left_paths:
        left_obs = left_signatures[id(left)]
        for right in right_by_actions.get(left.actions, []):
            right_obs = right_signatures[id(right)]
            if left_obs != right_obs:
                candidates.append(ObservationWitness(left, right, left_obs, right_obs))
    if not candidates:
        return None
    return min(candidates, key=lambda item: (max(len(item.left.actions), len(item.right.actions)), item.left.actions, item.right.actions))


def product_state_count(system: TransitionSystem) -> int:
    """Explore the synchronous public-action self-composition over state pairs.

    The model's public action schedule is shared between the two secret worlds.
    Question-relative asynchronous self-composition is implemented separately
    in :mod:`apr.sufficiency`; keeping this product synchronous prevents silent
    internal interleavings from being mistaken for operational observations.
    """

    initial = (system.initial(0), system.initial(1))
    queue: deque[tuple[State, State]] = deque([initial])
    seen = {initial}
    while queue:
        left, right = queue.popleft()
        left_transitions = system.transitions(left)
        right_transitions = system.transitions(right)
        right_by_action = {transition.action: transition for transition in right_transitions}
        left_by_action = {transition.action: transition for transition in left_transitions}
        for action in sorted(set(left_by_action) & set(right_by_action)):
            left_transition = left_by_action[action]
            right_transition = right_by_action[action]
            node = (left_transition.target, right_transition.target)
            if node not in seen:
                seen.add(node)
                queue.append(node)
    return len(seen)


def model_result(system: TransitionSystem) -> dict[str, object]:
    """Return a serializable result row for a configuration."""

    left = explore(system, 0)
    right = explore(system, 1)
    complete = observation_witness(system)
    payload = observation_witness(system, payload_only=True)
    return {
        "configuration": system.configuration.value,
        "sources": system.sources,
        "states": f"{len(left.states)} / {len(right.states)}",
        "state_count_s0": len(left.states),
        "state_count_s1": len(right.states),
        "transitions": left.transitions,
        "transitions_s1": right.transitions,
        "information_safety": "holds" if left.info_safe and right.info_safe else "violated",
        "authorization_safety": "holds" if left.auth_safe and right.auth_safe else "violated",
        "review_failures": left.review_failures + right.review_failures,
        "product_states": product_state_count(system),
        "synchronous_observations": "differ" if complete else "equal",
        "payload_only": "differ" if payload else "equal",
        "witness_length": None if complete is None else max(len(complete.left.actions), len(complete.right.actions)),
    }
