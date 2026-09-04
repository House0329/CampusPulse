"""Phase 4: each explanation has exactly two reasons and one trade-off."""

from src.explain import explain_space
from src.matching import apply_priority_boost, rank_spaces, space_features, task_weights
from src.synthetic import build_synthetic_dataset


def test_explanation_has_two_reasons_and_one_tradeoff():
    df = build_synthetic_dataset(seed=42)
    priorities = ["Quiet", "Power", "Wi-Fi"]
    weights = apply_priority_boost(task_weights("Coding"), priorities)
    ranked = rank_spaces(df, "Coding", "North Gate", priorities)

    for _, row in ranked.iterrows():
        start_x, start_y = 24.0, 6.0
        features = space_features(row, start_x, start_y)
        explanation = explain_space(row, weights, features)
        assert explanation["headline"] == "Why this space?"
        assert len(explanation["reasons"]) == 2
        assert all(isinstance(text, str) and text for text in explanation["reasons"])
        assert isinstance(explanation["tradeoff"], str) and explanation["tradeoff"]
        assert "%" not in explanation["reasons"][0]
        assert "weight" not in explanation["tradeoff"].lower()


def test_explanations_are_deterministic():
    df = build_synthetic_dataset(seed=42)
    ranked = rank_spaces(df, "Group work", "Main Hall", ["Discussion-friendly", "Comfort"])
    weights = apply_priority_boost(task_weights("Group work"), ["Discussion-friendly", "Comfort"])
    row = ranked.iloc[0]
    features = space_features(row, 50.0, 48.0)
    a = explain_space(row, weights, features)
    b = explain_space(row, weights, features)
    assert a == b
