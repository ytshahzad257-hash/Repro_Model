"""Algorithm 1: question-relative evidence sufficiency (Theorem 2).

The question automaton must be folded into the state passed to
``decide_generic`` so that the answer is a function of the final product
state.  The Revision 4 entry point ``decide_sufficiency`` read answers from one
reconstructed path and kept only one right-hand step per token; it was unsound
for path-dependent answers and has been removed.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Revision 5: Algorithm 1 over a generic finite system with a question
# automaton folded into the state.  Unlike ``decide_sufficiency`` above, the
# answer is a function of the final (product) state, as Theorem 2 requires,
# and every pair of equal-token steps is explored (not one per token).

@dataclass(frozen=True, slots=True)
class GenericResult:
    sufficient: bool
    explored_nodes: int
    left_history: tuple[str, ...] | None = None
    right_history: tuple[str, ...] | None = None
    left_answer: object | None = None
    right_answer: object | None = None


def decide_generic(initial, successors, is_final, answer, token) -> GenericResult:
    """Asynchronous self-composition BFS (Algorithm 1).

    ``successors(u)`` yields (action, v); ``token(action)`` is the recorder
    output or None for a silent step; ``answer(u)`` is defined on final states.
    """

    start = (initial, initial)
    parents: dict = {start: (None, "", "")}
    frontier: deque = deque([start])
    while frontier:
        node = frontier.popleft()
        left, right = node
        left_final, right_final = is_final(left), is_final(right)
        if left_final and right_final:
            if answer(left) != answer(right):
                lh, rh = _reconstruct_generic(node, parents)
                return GenericResult(False, len(parents), lh, rh, answer(left), answer(right))
            continue
        left_steps = () if left_final else tuple(successors(left))
        right_steps = () if right_final else tuple(successors(right))
        right_by_token: dict = {}
        for action, target in right_steps:
            tok = token(action)
            if tok is None:
                succ = (left, target)
                if succ not in parents:
                    parents[succ] = (node, "", action)
                    frontier.append(succ)
            else:
                right_by_token.setdefault(tok, []).append((action, target))
        for action, target in left_steps:
            tok = token(action)
            if tok is None:
                succ = (target, right)
                if succ not in parents:
                    parents[succ] = (node, action, "")
                    frontier.append(succ)
                continue
            for r_action, r_target in right_by_token.get(tok, ()):
                succ = (target, r_target)
                if succ not in parents:
                    parents[succ] = (node, action, r_action)
                    frontier.append(succ)
    return GenericResult(True, len(parents))


def _reconstruct_generic(node, parents) -> tuple[tuple[str, ...], tuple[str, ...]]:
    left: list[str] = []
    right: list[str] = []
    current = node
    while current is not None:
        parent, la, ra = parents[current]
        if la:
            left.append(la)
        if ra:
            right.append(ra)
        current = parent
    return tuple(reversed(left)), tuple(reversed(right))
