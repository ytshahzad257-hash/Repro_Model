"""Deterministic recorder primitives used by Algorithm 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecorderState:
    """Small deterministic Mealy recorder state."""

    evidence: tuple[str, ...] = ()

    def emit(self, token: str | None) -> "RecorderState":
        return RecorderState(self.evidence if token is None else self.evidence + (token,))


class Recorder:
    """Protocol for deterministic evidence recorders."""

    name = "recorder"

    def token(self, action: str) -> str | None:
        raise NotImplementedError

    def initial(self) -> RecorderState:
        return RecorderState()


class ActionRecorder(Recorder):
    def __init__(self, name: str, included: frozenset[str]) -> None:
        self.name = name
        self.included = included

    def token(self, action: str) -> str | None:
        return action if action in self.included else None
