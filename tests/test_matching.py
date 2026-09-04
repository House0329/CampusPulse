"""Phase 3: matching weights, priority boost, distance, and stable Top 3."""

import numpy as np
import pandas as pd
import pytest

from src.matching import (
    MAX_PRIORITIES,
    START_POINTS,
    TASK_PRESETS,
    TASKS,
    add_compare_id,
    apply_priority_boost,
    compare_decision_hint,
    distance_score,
    rank_spaces,
    task_weights,
)
from src.synthetic import build_synthetic_dataset


def _df():
    return build_synthetic_dataset(seed=42)


def test_each_task_preset_sums_to_one():
    for task in TASKS:
        weights = task_weights(task)
        assert weights == TASK_PRESETS[task]
        assert pytest.approx(sum(weights.values()), abs=1e-12) == 1.0


def test_priority_boost_renormalizes():
    base = task_weights("Coding")
    boosted = apply_priority_boost(base, ["Quiet", "Power", "Wi-Fi"])
    assert pytest.approx(sum(boosted.values()), abs=1e-12) == 1.0
    assert boosted["quiet"] > base["quiet"]
    assert boosted["power"] > base["power"]
    assert boosted["wifi"] > base["wifi"]


def test_more_than_three_priorities_rejected():
    with pytest.raises(ValueError, match="three"):
        apply_priority_boost(task_weights("Coding"), ["Quiet", "Power", "Wi-Fi", "Comfort"])
        assert MAX_PRIORITIES == 3


def test_match_bounds_0_to_100():
    ranked = rank_spaces(_df(), "Coding", "North Gate", ["Quiet", "Power", "Wi-Fi"])
    assert ranked["match"].between(0, 100).all()
    assert ranked["match"].dtype == np.int64 or ranked["match"].dtype == int or pd.api.types.is_integer_dtype(ranked["match"])


def test_closer_start_scores_higher_distance():
    near = distance_score(25, 24, *START_POINTS["Library Hub"])
    far = distance_score(25, 24, *START_POINTS["Residence"])
    assert near > far


def test_ranking_is_deterministic():
    a = rank_spaces(_df(), "Writing", "Main Hall", ["Quiet", "Comfort", "Close by"])
    b = rank_spaces(_df(), "Writing", "Main Hall", ["Quiet", "Comfort", "Close by"])
    pd.testing.assert_series_equal(a["space_id"], b["space_id"])
    pd.testing.assert_series_equal(a["match"], b["match"])


def test_every_task_produces_stable_top3():
    df = _df()
    for task in TASKS:
        ranked = rank_spaces(df, task, "North Gate", ["Quiet", "Comfort"])
        top = ranked.head(3)
        assert len(top) == 3
        assert top["match"].is_monotonic_decreasing
        again = rank_spaces(df, task, "North Gate", ["Quiet", "Comfort"]).head(3)
        pd.testing.assert_series_equal(top["space_id"], again["space_id"])


def test_compare_cap_is_three():
    ids, notice = add_compare_id(["S01", "S02", "S03"], "S04")
    assert ids == ["S01", "S02", "S03"]
    assert notice is not None


def test_compare_hint_clear_lead():
    frame = pd.DataFrame(
        [
            {"name": "Library 4F", "match": 92, "space_id": "S01"},
            {"name": "East Cafe", "match": 70, "space_id": "S05"},
        ]
    )
    assert "clearest fit" in compare_decision_hint(frame)


def test_compare_hint_close_alternative():
    frame = pd.DataFrame(
        [
            {"name": "Tech Hub", "match": 81, "space_id": "S04"},
            {"name": "North Study Hall", "match": 80, "space_id": "S03"},
        ]
    )
    assert "close alternative" in compare_decision_hint(frame)
