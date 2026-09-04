"""Deterministic synthetic campus dataset (18 fictional study spaces).

All values are generated from four archetype centers plus seeded jitter.
They do not describe any real university.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

ARCHETYPE_CENTERS: dict[str, dict[str, float]] = {
    "Deep Focus": {
        "quiet": 4.7,
        "crowding": 2.0,
        "comfort": 4.2,
        "wifi": 4.3,
        "power": 4.2,
        "discussion": 1.6,
        "lighting": 4.5,
    },
    "Quick Work": {
        "quiet": 3.6,
        "crowding": 3.0,
        "comfort": 3.7,
        "wifi": 4.6,
        "power": 4.6,
        "discussion": 2.4,
        "lighting": 3.9,
    },
    "Social Study": {
        "quiet": 2.5,
        "crowding": 3.7,
        "comfort": 4.3,
        "wifi": 4.1,
        "power": 3.1,
        "discussion": 4.2,
        "lighting": 4.2,
    },
    "Group Collaboration": {
        "quiet": 2.3,
        "crowding": 3.3,
        "comfort": 4.0,
        "wifi": 4.4,
        "power": 4.0,
        "discussion": 4.8,
        "lighting": 4.0,
    },
}

ATTRIBUTE_ORDER = (
    "quiet",
    "crowding",
    "lighting",
    "comfort",
    "wifi",
    "power",
    "discussion",
)

# Schematic x/y in 0–100. Zone layout matches the later SVG map, not geography.
SPACE_SEEDS: list[dict[str, Any]] = [
    {"space_id": "S01", "name": "Library 4F", "zone": "North", "archetype": "Deep Focus", "x": 25.0, "y": 24.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S02", "name": "Library 2F", "zone": "North", "archetype": "Deep Focus", "x": 28.0, "y": 32.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S03", "name": "North Study Hall", "zone": "North", "archetype": "Quick Work", "x": 16.0, "y": 16.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S04", "name": "Tech Hub", "zone": "North", "archetype": "Quick Work", "x": 40.0, "y": 36.0, "open_late": 1, "food_allowed": 0},
    {"space_id": "S05", "name": "East Cafe", "zone": "East", "archetype": "Social Study", "x": 62.0, "y": 16.0, "open_late": 0, "food_allowed": 1},
    {"space_id": "S06", "name": "Student Centre", "zone": "East", "archetype": "Group Collaboration", "x": 84.0, "y": 28.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S07", "name": "Innovation Lounge", "zone": "East", "archetype": "Group Collaboration", "x": 70.0, "y": 36.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S08", "name": "Commons Cafe", "zone": "East", "archetype": "Social Study", "x": 88.0, "y": 18.0, "open_late": 0, "food_allowed": 1},
    {"space_id": "S09", "name": "Silent Annex", "zone": "West", "archetype": "Deep Focus", "x": 18.0, "y": 58.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S10", "name": "Garden Room", "zone": "West", "archetype": "Deep Focus", "x": 34.0, "y": 66.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S11", "name": "West Lounge", "zone": "West", "archetype": "Social Study", "x": 14.0, "y": 80.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S12", "name": "Reading Room", "zone": "West", "archetype": "Deep Focus", "x": 38.0, "y": 84.0, "open_late": 0, "food_allowed": 0},
    {"space_id": "S13", "name": "South Project Room", "zone": "South", "archetype": "Group Collaboration", "x": 62.0, "y": 58.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S14", "name": "Residence Lounge", "zone": "South", "archetype": "Social Study", "x": 80.0, "y": 86.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S15", "name": "Late Lab", "zone": "South", "archetype": "Quick Work", "x": 90.0, "y": 64.0, "open_late": 1, "food_allowed": 0},
    {"space_id": "S16", "name": "Commons Booths", "zone": "South", "archetype": "Quick Work", "x": 58.0, "y": 74.0, "open_late": 1, "food_allowed": 1},
    {"space_id": "S17", "name": "Atrium Tables", "zone": "South", "archetype": "Social Study", "x": 72.0, "y": 70.0, "open_late": 0, "food_allowed": 1},
    {"space_id": "S18", "name": "Seminar Hub", "zone": "South", "archetype": "Group Collaboration", "x": 86.0, "y": 80.0, "open_late": 0, "food_allowed": 0},
]

RATING_COLUMNS = (
    "quiet",
    "crowding",
    "lighting",
    "comfort",
    "wifi",
    "power",
    "discussion",
    "coding",
    "reading",
    "writing",
    "group_work",
    "exam_revision",
)

DEFAULT_SEED = 42


def _jitter(rng: np.random.Generator, base: float, sigma: float = 0.28) -> float:
    value = base + rng.normal(0, sigma)
    return float(np.clip(value, 1.0, 5.0))


def _task_scores(attrs: dict[str, float], rng: np.random.Generator) -> dict[str, float]:
    low_crowding = 6.0 - attrs["crowding"]
    raw = {
        "coding": float(np.mean([attrs["wifi"], attrs["power"], attrs["quiet"], attrs["comfort"]])),
        "reading": float(np.mean([attrs["quiet"], attrs["lighting"], attrs["comfort"]])),
        "writing": float(np.mean([attrs["quiet"], attrs["comfort"], attrs["power"]])),
        "group_work": float(np.mean([attrs["discussion"], attrs["wifi"], attrs["comfort"]])),
        "exam_revision": float(np.mean([attrs["quiet"], low_crowding, attrs["comfort"]])),
    }
    return {
        key: float(np.clip(value + rng.uniform(-0.15, 0.15), 1.0, 5.0))
        for key, value in raw.items()
    }


def build_synthetic_dataset(seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Return 18 fictional spaces. Seed 42 is the canonical, reproducible dataset."""
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []

    for spec in SPACE_SEEDS:
        center = ARCHETYPE_CENTERS[spec["archetype"]]
        attrs = {key: _jitter(rng, center[key]) for key in ATTRIBUTE_ORDER}
        tasks = _task_scores(attrs, rng)
        row = {
            "space_id": spec["space_id"],
            "name": spec["name"],
            "zone": spec["zone"],
            "x": spec["x"],
            "y": spec["y"],
            **attrs,
            **tasks,
            "open_late": spec["open_late"],
            "food_allowed": spec["food_allowed"],
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    for col in RATING_COLUMNS:
        df[col] = df[col].round(2)
    return df
