from apr.explorer import explore
from apr.model import TransitionSystem
from apr.policies import Configuration


def test_governed_security_verdicts_hold():
    result = explore(TransitionSystem(Configuration.GOVERNED), 1)
    assert result.info_safe
    assert result.auth_safe


def test_named_bad_configurations_expose_the_claimed_failure_kind():
    assert not explore(TransitionSystem(Configuration.SOURCE_ONLY), 1).info_safe
    assert not explore(TransitionSystem(Configuration.IGNORE_INFO_CHECKS), 1).info_safe
    assert not explore(TransitionSystem(Configuration.UNGUARDED_EXPORT), 1).info_safe
    assert not explore(TransitionSystem(Configuration.IGNORE_GRANT_CHECKS), 1).auth_safe
    assert explore(TransitionSystem(Configuration.DELETE_EVIDENCE), 1).info_safe
