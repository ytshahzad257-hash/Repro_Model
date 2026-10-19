"""Question automata for evidence-sufficiency experiments."""

from __future__ import annotations

from dataclasses import dataclass

from .state import State


@dataclass(frozen=True, slots=True)
class Question:
    name: str

    def answer(self, state: State, history: tuple[str, ...]) -> str:
        raise NotImplementedError


class AdmissionQuestion(Question):
    def answer(self, state: State, history: tuple[str, ...]) -> str:
        return "admitted" if state.has_loaded else "not-admitted"


class OrderQuestion(Question):
    def answer(self, state: State, history: tuple[str, ...]) -> str:
        relevant = tuple(action for action in history if action in {"Isolate", "Fence", "Persist", "CommitCut"})
        return "<".join(relevant)


class FinalStateQuestion(Question):
    def answer(self, state: State, history: tuple[str, ...]) -> str:
        return repr((state.committed, state.review_answered, state.released, state.grant_revoked))


class CausalQuestion(Question):
    def answer(self, state: State, history: tuple[str, ...]) -> str:
        return "causal-use-unknown"
