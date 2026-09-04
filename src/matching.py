"""Task-first weighted matching. Pure functions — no Streamlit import."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

TASKS = (
    "Coding",
    "Reading",
    "Writing",
    "Group work",
    "Exam revision",
)

TASK_COLUMN = {
    "Coding": "coding",
    "Reading": "reading",
    "Writing": "writing",
    "Group work": "group_work",
    "Exam revision": "exam_revision",
}

MATCH_FEATURES = (
    "quiet",
    "wifi",
    "power",
    "comfort",
    "low_crowding",
    "discussion",
    "distance",
)

# Design presets from the build spec. Columns sum to 1. Not survey-derived.
TASK_PRESETS: dict[str, dict[str, float]] = {
    "Coding": {
        "quiet": 0.15,
        "wifi": 0.21,
        "power": 0.23,
        "comfort": 0.14,
        "low_crowding": 0.07,
        "discussion": 0.02,
        "distance": 0.18,
    },
    "Reading": {
        "quiet": 0.28,
        "wifi": 0.08,
        "power": 0.08,
        "comfort": 0.18,
        "low_crowding": 0.17,
        "discussion": 0.02,
        "distance": 0.19,
    },
    "Writing": {
        "quiet": 0.24,
        "wifi": 0.10,
        "power": 0.14,
        "comfort": 0.18,
        "low_crowding": 0.12,
        "discussion": 0.02,
        "distance": 0.20,
    },
    "Group work": {
        "quiet": 0.04,
        "wifi": 0.15,
        "power": 0.10,
        "comfort": 0.14,
        "low_crowding": 0.04,
        "discussion": 0.38,
        "distance": 0.15,
    },
    "Exam revision": {
        "quiet": 0.30,
        "wifi": 0.06,
        "power": 0.10,
        "comfort": 0.18,
        "low_crowding": 0.20,
        "discussion": 0.01,
        "distance": 0.15,
    },
}

PRIORITY_TO_FEATURE = {
    "Quiet": "quiet",
    "Power": "power",
    "Wi-Fi": "wifi",
    "Comfort": "comfort",
    "Close by": "distance",
    "Discussion-friendly": "discussion",
}

PRIORITY_BOOST = 0.08
MAX_PRIORITIES = 3
COMPARE_CAP = 3

TASK_DEFAULT_PRIORITIES: dict[str, list[str]] = {
    "Coding": ["Quiet", "Power", "Wi-Fi"],
    "Reading": ["Quiet", "Comfort", "Close by"],
    "Writing": ["Quiet", "Comfort", "Close by"],
    "Group work": ["Discussion-friendly", "Comfort", "Wi-Fi"],
    "Exam revision": ["Quiet", "Comfort", "Close by"],
}

FEATURE_LABELS = {
    "quiet": "Quiet",
    "wifi": "Wi-Fi",
    "power": "Power",
    "comfort": "Comfort",
    "low_crowding": "Room to focus",
    "discussion": "Discussion",
    "distance": "Close by",
}

START_POINTS: dict[str, tuple[float, float]] = {
    "North Gate": (24.0, 6.0),
    "Library Hub": (26.0, 28.0),
    "Main Hall": (50.0, 48.0),
    "Residence": (80.0, 90.0),
}

MAX_DISTANCE = float(np.sqrt(100.0**2 + 100.0**2))


def task_weights(task: str) -> dict[str, float]:
    if task not in TASK_PRESETS:
        raise ValueError(f"Unknown task: {task}")
    return dict(TASK_PRESETS[task])


def apply_priority_boost(
    weights: dict[str, float],
    priorities: Iterable[str],
    boost: float = PRIORITY_BOOST,
) -> dict[str, float]:
    labels = list(priorities)
    if len(labels) > MAX_PRIORITIES:
        raise ValueError("Choose up to three priorities.")
    unknown = [label for label in labels if label not in PRIORITY_TO_FEATURE]
    if unknown:
        raise ValueError(f"Unknown priorities: {unknown}")

    w = dict(weights)
    for label in labels:
        w[PRIORITY_TO_FEATURE[label]] += boost
    total = sum(w.values())
    return {key: value / total for key, value in w.items()}


def _rating_01(value: float) -> float:
    return float(np.clip((float(value) - 1.0) / 4.0, 0.0, 1.0))


def distance_score(x: float, y: float, start_x: float, start_y: float) -> float:
    dist = float(np.sqrt((float(x) - start_x) ** 2 + (float(y) - start_y) ** 2))
    return float(1.0 - np.clip(dist / MAX_DISTANCE, 0.0, 1.0))


def space_features(row: pd.Series, start_x: float, start_y: float) -> dict[str, float]:
    low_crowding = 6.0 - float(row["crowding"])
    return {
        "quiet": _rating_01(row["quiet"]),
        "wifi": _rating_01(row["wifi"]),
        "power": _rating_01(row["power"]),
        "comfort": _rating_01(row["comfort"]),
        "low_crowding": _rating_01(low_crowding),
        "discussion": _rating_01(row["discussion"]),
        "distance": distance_score(row["x"], row["y"], start_x, start_y),
    }


def match_score(
    features: dict[str, float],
    weights: dict[str, float],
    task_fit_01: float,
) -> tuple[int, float, dict[str, float]]:
    contributions = {feat: weights[feat] * features[feat] for feat in MATCH_FEATURES}
    attribute_score = float(sum(contributions.values()))
    raw = 100.0 * (0.70 * attribute_score + 0.30 * float(task_fit_01))
    match = int(round(float(np.clip(raw, 0.0, 100.0))))
    return match, attribute_score, contributions


def rank_spaces(
    df: pd.DataFrame,
    task: str,
    start: str,
    priorities: Iterable[str],
) -> pd.DataFrame:
    """Return a copy of df ranked by Match Score, with contribution columns."""
    if start not in START_POINTS:
        raise ValueError(f"Unknown start point: {start}")
    if task not in TASK_COLUMN:
        raise ValueError(f"Unknown task: {task}")

    weights = apply_priority_boost(task_weights(task), priorities)
    start_x, start_y = START_POINTS[start]
    task_col = TASK_COLUMN[task]

    records = []
    for _, row in df.iterrows():
        feats = space_features(row, start_x, start_y)
        task_fit = _rating_01(row[task_col])
        match, attribute_score, contributions = match_score(feats, weights, task_fit)
        record = row.to_dict()
        record["match"] = match
        record["attribute_score"] = round(attribute_score, 6)
        record["task_fit"] = round(task_fit, 6)
        record["distance_score"] = round(feats["distance"], 6)
        for feat, value in contributions.items():
            record[f"contrib_{feat}"] = round(value, 6)
        records.append(record)

    ranked = pd.DataFrame(records)
    ranked = ranked.sort_values(
        ["match", "space_id"],
        ascending=[False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)
    return ranked


def add_compare_id(compare_ids: Iterable[str], space_id: str, cap: int = COMPARE_CAP) -> tuple[list[str], str | None]:
    ids = list(compare_ids)
    if space_id in ids:
        return ids, None
    if len(ids) >= cap:
        return ids, "You can compare up to 3 spaces."
    return ids + [space_id], None


def compare_decision_hint(compare_df: pd.DataFrame) -> str:
    ordered = compare_df.sort_values(["match", "space_id"], ascending=[False, True], kind="mergesort")
    best = ordered.iloc[0]
    second = ordered.iloc[1]
    if float(best["match"]) - float(second["match"]) >= 8:
        return f"{best['name']} is the clearest fit for your current priorities."
    return f"{best['name']} leads overall, but {second['name']} is a close alternative."
