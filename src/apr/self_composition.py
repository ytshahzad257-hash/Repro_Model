"""Self-composition helpers and timing-sensitive observation comparison."""

from __future__ import annotations

from dataclasses import dataclass

from .explorer import ObservationWitness, observation_witness, product_state_count
from .model import TransitionSystem


@dataclass(frozen=True, slots=True)
class Comparison:
    product_states: int
    complete_equal: bool
    payload_equal: bool
    complete_witness: ObservationWitness | None
    payload_witness: ObservationWitness | None


def compare(system: TransitionSystem) -> Comparison:
    complete = observation_witness(system)
    payload = observation_witness(system, payload_only=True)
    return Comparison(product_state_count(system), complete is None, payload is None, complete, payload)
