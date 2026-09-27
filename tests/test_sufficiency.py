from apr.sufficiency import FiniteLTS, LabeledStep, RecorderMachine, decide_sufficiency


def test_algorithm_returns_witness_with_equal_evidence_and_different_answers():
    transitions = {
        0: (LabeledStep("left", "same", 1), LabeledStep("right", "same", 2)),
        1: (),
        2: (),
    }
    lts = FiniteLTS(0, frozenset({1, 2}), transitions, lambda state, _history: state)
    result = decide_sufficiency(lts, RecorderMachine(lambda _action: "same"))
    assert not result.sufficient
    assert result.left_history is not None
    assert result.right_history is not None
    assert result.left_answer != result.right_answer


def test_silent_steps_can_be_interleaved():
    transitions = {0: (LabeledStep("silent", None, 1),), 1: (LabeledStep("token", "x", 2),), 2: ()}
    lts = FiniteLTS(0, frozenset({2}), transitions, lambda _state, _history: "same")
    result = decide_sufficiency(lts, RecorderMachine(lambda action: "x" if action == "token" else None))
    assert result.sufficient
