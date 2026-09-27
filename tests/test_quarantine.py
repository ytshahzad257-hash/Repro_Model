from apr.quarantine import simulate_workflow


def test_quarantine_is_sound_for_every_workflow():
    for seed in range(10):
        result = simulate_workflow(sources=12, derived=8, restricted_probability=0.2, fanin=3, use_probability=0.5, seed=seed)
        assert result.sound
        assert result.quarantined >= result.truly_dependent


def test_full_use_has_no_clean_withheld_items():
    result = simulate_workflow(sources=12, derived=8, restricted_probability=0.2, fanin=3, use_probability=1.0, seed=4)
    assert result.withheld_clean == 0.0
