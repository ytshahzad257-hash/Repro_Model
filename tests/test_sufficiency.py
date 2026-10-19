from apr.sufficiency import decide_generic

FINALS = {"L", "R", "F1", "F2"}


def run(transitions, answers, token):
    return decide_generic(
        "s0",
        lambda u: transitions.get(u, ()),
        lambda u: u in FINALS,
        lambda u: answers[u],
        token,
    )


def test_equal_tokens_on_several_right_steps_are_all_explored():
    # Two steps emit the same token; only the second leads to a different answer.
    transitions = {"s0": (("a1", "F1"), ("a2", "F2"))}
    answers = {"F1": 0, "F2": 1}
    result = run(transitions, answers, lambda _a: "same")
    assert not result.sufficient
    assert result.left_answer != result.right_answer


def test_silent_steps_can_be_interleaved():
    transitions = {"s0": (("silent", "m"),), "m": (("tok", "F1"),)}
    result = run(transitions, {"F1": 0}, lambda a: "x" if a == "tok" else None)
    assert result.sufficient


def test_distinct_tokens_make_recorder_sufficient():
    transitions = {"s0": (("a1", "F1"), ("a2", "F2"))}
    result = run(transitions, {"F1": 0, "F2": 1}, lambda a: a)
    assert result.sufficient
