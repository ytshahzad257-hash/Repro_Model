from apr.explorer import explore
from apr.model import TransitionSystem
from apr.policies import Configuration


def test_explorer_is_deterministic():
    system = TransitionSystem(Configuration.GOVERNED)
    first = explore(system, 0)
    second = explore(system, 0)
    assert len(first.states) == len(second.states)
    assert first.transitions == second.transitions
    assert first.paths == second.paths


def test_all_configurations_are_reachable():
    for configuration in Configuration:
        result = explore(TransitionSystem(configuration), 0)
        assert result.states
        assert result.transitions >= len(result.states) - 1
