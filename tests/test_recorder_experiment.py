from apr.recorder_experiment import run_matrix


def test_table6_verdict_pattern_for_k1():
    verdicts = {(r["recorder"], r["question"]): r["verdict"] for r in run_matrix(1)}
    assert verdicts[("receipts", "admission")] == "insufficient"
    assert verdicts[("receipts", "order")] == "sufficient"
    assert verdicts[("admission_ledger", "admission")] == "sufficient"
    assert verdicts[("admission_ledger", "order")] == "insufficient"
    assert verdicts[("receipts_plus_admission_ledger", "admission")] == "sufficient"
    assert verdicts[("receipts_plus_admission_ledger", "order")] == "sufficient"
    for recorder in ("receipts", "admission_ledger", "receipts_plus_admission_ledger", "full_mediator_log"):
        assert verdicts[(recorder, "causal")] == "insufficient"


def test_insufficient_witnesses_have_equal_evidence_and_different_answers():
    from apr.recorder_experiment import token_function
    for row in run_matrix(1):
        if row["verdict"] == "insufficient":
            token = token_function(row["recorder"])
            left = [token(a) for a in row["witness_left"] if token(a) is not None]
            right = [token(a) for a in row["witness_right"] if token(a) is not None]
            assert left == right
            assert row["answer_left"] != row["answer_right"]
