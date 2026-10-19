"""Self-composition helpers and timing-sensitive observation comparison."""

from __future__ import annotations

from dataclasses import dataclass

from .explorer import ObservationWitness, self_composition
from .model import TransitionSystem


@dataclass(frozen=True, slots=True)
class Comparison:
    product_states: int
    complete_equal: bool
    payload_equal: bool
    complete_witness: ObservationWitness | None
    payload_witness: ObservationWitness | None


def compare(system: TransitionSystem) -> Comparison:
    complete = self_composition(system)
    payload = self_composition(system, payload_only=True)
    return Comparison(complete.nodes, complete.witness is None, payload.witness is None, complete.witness, payload.witness)
