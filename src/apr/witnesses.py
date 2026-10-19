"""Witness serialization helpers."""

from __future__ import annotations

from dataclasses import asdict

from .state import State


def history_record(actions: tuple[str, ...], state: State) -> dict[str, object]:
    return {"actions": list(actions), "final_state": asdict(state)}


def witness_record(left: tuple[str, ...], right: tuple[str, ...], left_state: State, right_state: State) -> dict[str, object]:
    return {"history": history_record(left, left_state), "history_prime": history_record(right, right_state)}
