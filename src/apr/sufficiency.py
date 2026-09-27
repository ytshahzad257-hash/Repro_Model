"""Algorithm 1: question-relative evidence sufficiency."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Iterable, TypeVar


S = TypeVar("S", bound=Hashable)
Token = str
Action = str


@dataclass(frozen=True, slots=True)
class LabeledStep(Generic[S]):
    action: Action
    token: Token | None
    target: S


@dataclass(frozen=True, slots=True)
class FiniteLTS(Generic[S]):
    initial: S
    finals: frozenset[S]
    transitions: dict[S, tuple[LabeledStep[S], ...]]
    answer: Callable[[S, tuple[Action, ...]], object]

    def successors(self, state: S) -> tuple[LabeledStep[S], ...]:
        return self.transitions.get(state, ())


@dataclass(frozen=True, slots=True)
class ProductPoint(Generic[S]):
    left: S
    right: S


@dataclass(frozen=True, slots=True)
class SufficiencyResult(Generic[S]):
    sufficient: bool
    explored_nodes: int
    left_history: tuple[Action, ...] | None = None
    right_history: tuple[Action, ...] | None = None
    left_answer: object | None = None
    right_answer: object | None = None


class RecorderMachine:
    """Deterministic Mealy recorder: `token` returns a token or silent None."""

    def __init__(self, token: Callable[[Action], Token | None]) -> None:
        self._token = token

    def token(self, action: Action) -> Token | None:
        return self._token(action)


def _reconstruct(
    point: ProductPoint[S], parents: dict[ProductPoint[S], tuple[ProductPoint[S] | None, str, str]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    left: list[str] = []
    right: list[str] = []
    current: ProductPoint[S] | None = point
    while current is not None:
        parent, left_action, right_action = parents[current]
        if left_action:
            left.append(left_action)
        if right_action:
            right.append(right_action)
        current = parent
    return tuple(reversed(left)), tuple(reversed(right))


def decide_sufficiency(
    lts: FiniteLTS[S], recorder: RecorderMachine, *, max_nodes: int | None = None
) -> SufficiencyResult[S]:
    """Run the asynchronous self-composition BFS from Algorithm 1.

    Silent moves can occur on one side. Equal non-silent tokens must be taken
    jointly. A side stops once it enters a completion state.
    """

    initial = ProductPoint(lts.initial, lts.initial)
    frontier: deque[ProductPoint[S]] = deque([initial])
    parents: dict[ProductPoint[S], tuple[ProductPoint[S] | None, str, str]] = {initial: (None, "", "")}
    while frontier:
        point = frontier.popleft()
        if max_nodes is not None and len(parents) > max_nodes:
            raise RuntimeError(f"sufficiency search exceeded max_nodes={max_nodes}")
        if point.left in lts.finals and point.right in lts.finals:
            left_history, right_history = _reconstruct(point, parents)
            left_answer = lts.answer(point.left, left_history)
            right_answer = lts.answer(point.right, right_history)
            if left_answer != right_answer:
                return SufficiencyResult(False, len(parents), left_history, right_history, left_answer, right_answer)

        left_steps = () if point.left in lts.finals else lts.successors(point.left)
        right_steps = () if point.right in lts.finals else lts.successors(point.right)
        for step in left_steps:
            left_token = recorder.token(step.action)
            if left_token is None:
                successor = ProductPoint(step.target, point.right)
                if successor not in parents:
                    parents[successor] = (point, step.action, "")
                    frontier.append(successor)
        for step in right_steps:
            right_token = recorder.token(step.action)
            if right_token is None:
                successor = ProductPoint(point.left, step.target)
                if successor not in parents:
                    parents[successor] = (point, "", step.action)
                    frontier.append(successor)
        right_by_token = {recorder.token(step.action): step for step in right_steps if recorder.token(step.action) is not None}
        for left_step in left_steps:
            left_token = recorder.token(left_step.action)
            if left_token is None or left_token not in right_by_token:
                continue
            right_step = right_by_token[left_token]
            successor = ProductPoint(left_step.target, right_step.target)
            if successor not in parents:
                parents[successor] = (point, left_step.action, right_step.action)
                frontier.append(successor)
    return SufficiencyResult(True, len(parents))


def recorder_from_actions(actions: Iterable[str]) -> RecorderMachine:
    included = frozenset(actions)
    return RecorderMachine(lambda action: action if action in included else None)
