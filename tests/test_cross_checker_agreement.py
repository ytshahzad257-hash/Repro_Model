from apr.explorer import explore
from apr.model import TransitionSystem
from apr.policies import Configuration


def test_two_secret_copies_have_same_structural_counts():
    for configuration in Configuration:
        system = TransitionSystem(configuration)
        zero = explore(system, 0)
        one = explore(system, 1)
        assert len(zero.states) == len(one.states)
        assert zero.transitions == one.transitions
