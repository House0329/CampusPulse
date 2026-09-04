"""Natural-language recommendation explanations. Pure functions — no Streamlit."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.matching import MATCH_FEATURES

POSITIVE_PHRASES = {
    "quiet": "Very quiet for focused work.",
    "power": "Strong access to power outlets.",
    "wifi": "Reliable Wi-Fi for online work.",
    "comfort": "Comfortable for longer sessions.",
    "distance": "Close to your selected starting point.",
    "discussion": "Good for conversation and collaboration.",
    "low_crowding": "Less crowded, with more room to settle in.",
}

TRADEOFF_PHRASES = {
    "quiet": "Can be noisier than your ideal.",
    "power": "Power access is only average.",
    "wifi": "Wi-Fi is not one of its strengths.",
    "comfort": "Comfort is more basic here.",
    "distance": "It is a longer walk from your start.",
    "discussion": "Not ideal for group discussion.",
    "low_crowding": "It can feel busier than you might prefer.",
}

WEIGHT_TRADEOFF_THRESHOLD = 0.10


def _contribution_map(row: pd.Series, features: dict[str, float], weights: dict[str, float]) -> dict[str, float]:
    if all(f"contrib_{feat}" in row.index for feat in MATCH_FEATURES):
        return {feat: float(row[f"contrib_{feat}"]) for feat in MATCH_FEATURES}
    return {feat: float(weights[feat]) * float(features[feat]) for feat in MATCH_FEATURES}


def explain_space(
    row: pd.Series,
    weights: dict[str, float],
    features: dict[str, float],
) -> dict[str, Any]:
    """Return 2 positive reasons and 1 trade-off. Never expose raw weights."""
    contribution = _contribution_map(row, features, weights)
    top_positive = sorted(contribution, key=contribution.get, reverse=True)[:2]

    candidates = [feat for feat in MATCH_FEATURES if weights[feat] >= WEIGHT_TRADEOFF_THRESHOLD]
    if not candidates:
        candidates = list(MATCH_FEATURES)
    tradeoff = min(candidates, key=lambda feat: features[feat])

    return {
        "headline": "Why this space?",
        "reasons": [POSITIVE_PHRASES[feat] for feat in top_positive],
        "tradeoff": TRADEOFF_PHRASES[tradeoff],
        "reason_features": top_positive,
        "tradeoff_feature": tradeoff,
    }
