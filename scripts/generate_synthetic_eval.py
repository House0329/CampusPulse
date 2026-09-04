"""Generate illustrative synthetic evaluation rows for chart/layout prototyping.

These values are NOT human-subject results. They exist so Portfolio charts have a
reproducible layout and so acceptance-target ranges stay explicit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_PATH = ROOT / "research" / "synthetic_evaluation.csv"
DEFAULT_SEED = 2026
N_PROFILES = 12
TASKS = ("Coding", "Group work", "Exam revision")
CONDITIONS = ("baseline_a", "campuspulse_b")

# Design targets from the build spec. Used as generator centres, not as findings.
CENTERS = {
    "baseline_a": {
        "task_completion": 0.83,
        "decision_time_s": 68.0,
        "decision_confidence": 3.1,
        "information_usefulness": 3.0,
        "why_understanding": 2.7,
        "mental_effort": 3.8,
    },
    "campuspulse_b": {
        "task_completion": 0.97,
        "decision_time_s": 36.0,
        "decision_confidence": 4.2,
        "information_usefulness": 4.5,
        "why_understanding": 4.4,
        "mental_effort": 2.6,
    },
}

STDS = {
    "decision_time_s": 8.0,
    "decision_confidence": 0.35,
    "information_usefulness": 0.30,
    "why_understanding": 0.35,
    "mental_effort": 0.35,
}

COLUMN_ORDER = [
    "data_type",
    "profile_id",
    "simulated_task",
    "condition",
    "task_completion",
    "decision_time_s",
    "decision_confidence",
    "information_usefulness",
    "why_understanding",
    "mental_effort",
]


def build_synthetic_evaluation(seed: int = DEFAULT_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []

    for profile_index in range(1, N_PROFILES + 1):
        profile_id = f"P{profile_index:02d}"
        for task in TASKS:
            for condition in CONDITIONS:
                center = CENTERS[condition]
                completion = int(rng.random() < center["task_completion"])
                time_s = float(
                    np.clip(
                        rng.normal(center["decision_time_s"], STDS["decision_time_s"]),
                        12.0,
                        120.0,
                    )
                )
                row = {
                    "data_type": "synthetic_illustrative",
                    "profile_id": profile_id,
                    "simulated_task": task,
                    "condition": condition,
                    "task_completion": completion,
                    "decision_time_s": round(time_s, 1),
                    "decision_confidence": round(
                        float(np.clip(rng.normal(center["decision_confidence"], STDS["decision_confidence"]), 1.0, 5.0)),
                        1,
                    ),
                    "information_usefulness": round(
                        float(
                            np.clip(
                                rng.normal(center["information_usefulness"], STDS["information_usefulness"]),
                                1.0,
                                5.0,
                            )
                        ),
                        1,
                    ),
                    "why_understanding": round(
                        float(np.clip(rng.normal(center["why_understanding"], STDS["why_understanding"]), 1.0, 5.0)),
                        1,
                    ),
                    "mental_effort": round(
                        float(np.clip(rng.normal(center["mental_effort"], STDS["mental_effort"]), 1.0, 5.0)),
                        1,
                    ),
                }
                rows.append(row)

    return pd.DataFrame(rows)[COLUMN_ORDER]


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = build_synthetic_evaluation()
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} illustrative rows to {OUT_PATH.relative_to(ROOT)}")
    print("Means by condition (illustrative only, not human-subject findings):")
    numeric = [
        "task_completion",
        "decision_time_s",
        "decision_confidence",
        "information_usefulness",
        "why_understanding",
        "mental_effort",
    ]
    print(df.groupby("condition")[numeric].mean().round(2).to_string())


if __name__ == "__main__":
    main()
