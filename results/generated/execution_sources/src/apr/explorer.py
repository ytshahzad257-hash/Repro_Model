"""Deterministic explicit-state exploration and synchronous self-composition."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .model import Observation, TransitionSystem
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
    """Explore all reachable states with deterministic BFS.

    ``transitions`` counts every enabled (state, action) pair of a reachable
    state, which is the convention TLC reports as "states generated" minus the
    initial state.
    """

    initial = system.initial(secret)
    queue: deque[State] = deque([initial])
    states: set[State] = {initial}
    paths: dict[State, tuple[str, ...]] = {initial: ()}
    successors: dict[State, list[State]] = {}
    transitions = 0
    info_safe = True
    auth_safe = True
    while queue:
        state = queue.popleft()
        info_safe = info_safe and system.info_safe(state)
        auth_safe = auth_safe and system.auth_safe(state)
        targets: list[State] = []
        for transition in system.transitions(state):
            transitions += 1
            target = transition.target
            targets.append(target)
            if target not in states:
                states.add(target)
                paths[target] = paths[state] + (transition.action,)
                queue.append(target)
        successors[state] = targets
    # A review failure is a reachable post-cut state from which no answered
    # review is reachable (the ReviewAvailable obligation fails there).
    can_answer: set[State] = {state for state in states if state.review_answered}
    changed = True
    while changed:
        changed = False
        for state in states:
            if state not in can_answer and any(target in can_answer for target in successors[state]):
                can_answer.add(state)
                changed = True
    review_failures = sum(1 for state in states if state.committed and state not in can_answer)
    return Reachability(initial, frozenset(states), transitions, paths, info_safe, auth_safe, review_failures)


def _observe(observation: Observation | None, position: int, *, payload_only: bool) -> tuple[object, ...] | None:
    if observation is None:
        return None
    if payload_only:
        return (observation.kind, observation.payload)
    return (observation.kind, observation.payload, position)


@dataclass(frozen=True, slots=True)
class ProductResult:
    nodes: int
    transitions: int
    witness: ObservationWitness | None


def self_composition(system: TransitionSystem, *, payload_only: bool = False,
                     left_secret: int = 0, right_secret: int = 1,
                     equal_release: bool = False) -> ProductResult:
    """Synchronous self-composition of the s=0 and s=1 copies.

    A node is (left state, right state, lag), where lag is the difference of
    the copies' logical positions.  Public actions are taken jointly when they
    are enabled in both copies (the common public interaction strategy);
    internal actions are taken by one copy alone and change the lag.

    Complete observations compare, at every node, the set of enabled public
    requests (a request enabled in one copy and refused in the other is an
    observable refusal) and, at every joint step, (kind, payload, logical
    position); positions agree exactly when the lag is 0.  The payload-only
    comparison checks payloads of accepted joint steps only.  The search is a
    complete BFS; ``transitions`` counts successor moves of distinct nodes,
    the convention TLC reports as "states generated" minus one.
    """

    from .policies import Configuration
    if equal_release and system.configuration is Configuration.APPROVED_SECRET_RELEASE:
        starts = [(system.initial(s), system.initial(s), 0) for s in sorted({left_secret,right_secret})]
    else:
        starts = [(system.initial(left_secret), system.initial(right_secret), 0)]
    parent: dict = {start: (None, "", "") for start in starts}
    queue: deque = deque(starts)
    transitions = 0
    first_witness = None
    while queue:
        node = queue.popleft()
        left, right, lag = node
        left_moves = {t.action: t for t in system.transitions(left)}
        right_moves = {t.action: t for t in system.transitions(right)}
        if first_witness is None and not payload_only:
            left_public = {a for a in left_moves if not system.is_internal(a)}
            right_public = {a for a in right_moves if not system.is_internal(a)}
            if left_public != right_public:
                first_witness = (node, "", "", ("enabled", tuple(sorted(left_public))), ("enabled", tuple(sorted(right_public))))
        successors = []
        for action, transition in left_moves.items():
            if system.is_internal(action):
                successors.append(((transition.target, right, lag + 1), action, "", None, None))
        for action, transition in right_moves.items():
            if system.is_internal(action):
                successors.append(((left, transition.target, lag - 1), "", action, None, None))
        for action in sorted(set(left_moves) & set(right_moves)):
            if system.is_internal(action):
                continue
            lt, rt = left_moves[action], right_moves[action]
            ol = None if lt.observation is None else (lt.observation.kind, lt.observation.payload)
            orr = None if rt.observation is None else (rt.observation.kind, rt.observation.payload)
            if not payload_only and ol is not None:
                ol, orr = ol + (0,), orr + (-lag,)  # positions equal iff lag == 0
            successors.append(((lt.target, rt.target, lag), action, action, ol, orr))
        transitions += len(successors)
        for successor, la, ra, ol, orr in successors:
            if first_witness is None and ol != orr:
                first_witness = (node, la, ra, ol, orr)
            if successor not in parent:
                parent[successor] = (node, la, ra)
                queue.append(successor)
    witness = None
    if first_witness is not None:
        node, last_left, last_right, ol, orr = first_witness
        left_actions: list[str] = [last_left] if last_left else []
        right_actions: list[str] = [last_right] if last_right else []
        current = node
        while current is not None:
            prev, la, ra = parent[current]
            if la:
                left_actions.append(la)
            if ra:
                right_actions.append(ra)
            current = prev
        left_actions.reverse()
        right_actions.reverse()
        witness = ObservationWitness(
            Path(node[0], tuple(left_actions)),
            Path(node[1], tuple(right_actions)),
            (ol,) if ol is not None else (),
            (orr,) if orr is not None else (),
        )
    return ProductResult(len(parent), transitions, witness)


def product_state_count(system: TransitionSystem) -> int:
    return self_composition(system).nodes


def observation_witness(system: TransitionSystem, *, payload_only: bool = False) -> ObservationWitness | None:
    return self_composition(system, payload_only=payload_only).witness


def model_result(system: TransitionSystem) -> dict[str, object]:
    """Return a serializable result row for a configuration."""

    left = explore(system, 0)
    right = explore(system, 1)
    complete = self_composition(system)
    payload = self_composition(system, payload_only=True)
    witness = complete.witness
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
        "product_states": complete.nodes,
        "product_transitions": complete.transitions,
        "synchronous_observations": "differ" if witness else "equal",
        "payload_only": "differ" if payload.witness else "equal",
        "witness_length": None if witness is None else max(len(witness.left.actions), len(witness.right.actions)),
        "witness_left": None if witness is None else list(witness.left.actions),
        "witness_right": None if witness is None else list(witness.right.actions),
    }
