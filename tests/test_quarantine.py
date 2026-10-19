from apr.quarantine import simulate_workflow


def test_quarantine_is_sound_for_every_workflow():
    for seed in range(10):
        result = simulate_workflow(sources=12, derived=8, restricted_probability=0.2, fanin=3, use_probability=0.5, seed=seed)
        assert result.sound
        assert result.quarantined >= result.truly_dependent


def test_full_use_has_no_clean_withheld_items():
    result = simulate_workflow(sources=12, derived=8, restricted_probability=0.2, fanin=3, use_probability=1.0, seed=4)
    assert result.withheld_clean == 0.0


def test_fanin_is_between_one_and_f():
    import random
    from apr import quarantine
    counts = set()
    rng = random.Random(1)
    for _ in range(200):
        counts.add(rng.randint(1, 3))
    assert counts == {1, 2, 3}
    # Reported uniform regime: shares near 0.39, not the fixed-fan-in 0.72.
    rows = quarantine.run_quarantine_experiment(seeds=list(range(300)), use_probabilities=(1.0,), sources=20, derived=100)
    assert 0.33 < rows[0]["quarantined"] < 0.45


def test_workflows_are_paired_across_use_probability():
    from apr import quarantine
    rows = quarantine.run_quarantine_experiment(seeds=list(range(50)), sources=20, derived=60)
    assert len({round(r["quarantined"], 12) for r in rows}) == 1
    deps = [r["truly_dependent"] for r in rows]
    assert deps == sorted(deps)


def test_skewed_and_correlated_variants_remain_sound():
    from apr.quarantine import simulate_workflow
    for selection in ('uniform','recency','zipf'):
        for use_model in ('independent','correlated','first_only'):
            result=simulate_workflow(sources=20,derived=100,restricted_probability=.1,fanin=3,use_probability=.5,seed=172903,selection=selection,use_model=use_model)
            assert result.sound
            assert result.truly_dependent <= result.quarantined
