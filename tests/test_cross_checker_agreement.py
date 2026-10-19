import json
from pathlib import Path

import pytest

from apr.explorer import explore
from apr.model import TransitionSystem
from apr.policies import Configuration

GENERATED = Path(__file__).resolve().parents[1] / "results" / "generated"


def test_secret_independent_configurations_have_same_structural_counts():
    for configuration in Configuration:
        if configuration in {Configuration.TIMED_RELEASE, Configuration.REFUSAL_MUTATION}:
            continue
        system = TransitionSystem(configuration)
        zero = explore(system, 0)
        one = explore(system, 1)
        assert len(zero.states) == len(one.states)
        assert zero.transitions == one.transitions


def test_timed_release_has_asymmetric_reachability():
    system = TransitionSystem(Configuration.TIMED_RELEASE)
    assert len(explore(system, 1).states) > len(explore(system, 0).states)


@pytest.mark.skipif(not (GENERATED / "cross_checker_agreement.json").exists(), reason="run scripts/tlc_matrix.py first")
def test_recorded_tlc_cross_check_passed():
    result = json.loads((GENERATED / "cross_checker_agreement.json").read_text())
    assert result["status"] == "PASS"
    assert result["mismatches"] == []
