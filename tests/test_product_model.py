from apr.model import TransitionSystem
from apr.policies import Configuration
from apr.self_composition import compare


def test_governed_observations_are_equal():
    comparison = compare(TransitionSystem(Configuration.GOVERNED))
    assert comparison.complete_equal
    assert comparison.payload_equal


def test_timed_release_separates_timing_from_payload():
    comparison = compare(TransitionSystem(Configuration.TIMED_RELEASE))
    assert not comparison.complete_equal
    assert comparison.payload_equal
    assert comparison.complete_witness is not None
