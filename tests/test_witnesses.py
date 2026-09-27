from apr.explorer import observation_witness
from apr.model import TransitionSystem
from apr.policies import Configuration


def test_source_only_has_a_deterministic_counterexample():
    first = observation_witness(TransitionSystem(Configuration.SOURCE_ONLY))
    second = observation_witness(TransitionSystem(Configuration.SOURCE_ONLY))
    assert first is not None and second is not None
    assert first.left.actions == second.left.actions
    assert first.right.actions == second.right.actions
