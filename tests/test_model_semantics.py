from apr.model import TransitionSystem
from apr.policies import Configuration


def actions_to_commit(system: TransitionSystem) -> tuple[str, ...]:
    state = system.initial(0)
    actions = ("Read[0]", "Derive[0]", "Load[0]", "RequestRevoke", "UpdatePolicy", "Isolate", "Fence", "Persist", "CommitCut")
    for action in actions:
        assert action in system.enabled_actions(state), (action, state)
        state = system.successor(state, action).target
    return actions


def test_paper_action_vocabulary_is_present():
    system = TransitionSystem()
    state = system.initial(0)
    assert "Read[0]" in system.enabled_actions(state)
    assert "Read[0]" in system.enabled_actions(state)


def test_governed_quarantines_loaded_context_at_cut():
    system = TransitionSystem(Configuration.GOVERNED)
    state = system.initial(0)
    for action in actions_to_commit(system):
        state = system.successor(state, action).target
    assert state.committed
    assert not state.has_loaded


def test_source_only_preserves_loaded_context_and_violates_information_safety():
    system = TransitionSystem(Configuration.SOURCE_ONLY)
    state = system.initial(0)
    for action in actions_to_commit(system):
        state = system.successor(state, action).target
    assert state.has_loaded
    use = system.successor(state, "OpUse").target
    assert use.unauthorized_info


def test_ignore_grant_checks_records_authorization_failure():
    system = TransitionSystem(Configuration.IGNORE_GRANT_CHECKS)
    state = system.initial(0)
    for action in actions_to_commit(system):
        state = system.successor(state, action).target
    state = system.successor(state, "GrantRevoke").target
    state = system.successor(state, "Review").target
    state = system.successor(state, "GenerateReport").target
    state = system.successor(state, "Answer").target
    state = system.successor(state, "ReportExport").target
    state = system.successor(state, "OpUse").target
    assert state.unauthorized_authority
