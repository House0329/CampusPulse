"""Generate the canonical synthetic campus CSV and analysis metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis import assign_clusters_and_pca
from src.synthetic import DEFAULT_SEED, build_synthetic_dataset

DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "locations.csv"
META_PATH = DATA_DIR / "analysis_meta.json"

COLUMN_ORDER = [
    "space_id",
    "name",
    "zone",
    "x",
    "y",
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
    "open_late",
    "food_allowed",
    "cluster",
    "pca_x",
    "pca_y",
]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = build_synthetic_dataset(seed=DEFAULT_SEED)
    df, meta = assign_clusters_and_pca(df, k=4, seed=DEFAULT_SEED)
    df = df[COLUMN_ORDER]
    df.to_csv(CSV_PATH, index=False)
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {len(df)} spaces to {CSV_PATH.relative_to(ROOT)}")
    print(f"Wrote analysis metadata to {META_PATH.relative_to(ROOT)}")
    print("cluster_counts:", meta["cluster_counts"])
    print("pca_explained_variance:", meta["pca_explained_variance"])


if __name__ == "__main__":
    main()
