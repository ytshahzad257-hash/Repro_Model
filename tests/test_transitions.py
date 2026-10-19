from apr.model import GLOBAL_ACTIONS, TransitionSystem


def test_global_action_names_match_section_7_vocabulary():
    assert len(GLOBAL_ACTIONS) == 17
    assert GLOBAL_ACTIONS[:7] == ("PrepareEffect", "RequestRevoke", "UpdatePolicy", "Isolate", "Fence", "Persist", "CommitCut")


def test_state_is_immutable():
    state = TransitionSystem().initial(0)
    try:
        state.secret = 1
    except AttributeError:
        pass
    else:
        raise AssertionError("state mutation should be rejected")
