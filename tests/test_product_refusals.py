"""Regression for independent review finding F6: secret-dependent refusals must be observable."""

from apr.explorer import self_composition
from apr.model import TransitionSystem
from apr.policies import Configuration


class RefuseUseWhenSecret(TransitionSystem):
    """Mutation: operational use is refused only in the secret-1 world."""

    def _global_enabled(self, state, action):
        if action == "OpUse" and state.secret == 1:
            return False
        return super()._global_enabled(state, action)


def test_secret_dependent_refusal_is_detected():
    mutated = RefuseUseWhenSecret(Configuration.GOVERNED)
    assert self_composition(mutated).witness is not None


def test_governed_has_equal_enabledness():
    assert self_composition(TransitionSystem(Configuration.GOVERNED)).witness is None
