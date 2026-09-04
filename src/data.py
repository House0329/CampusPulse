"""CSV loaders. Runtime reads precomputed files; it does not regenerate the campus."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCATIONS_PATH = ROOT / "data" / "locations.csv"


def load_locations(path: str | Path | None = None) -> pd.DataFrame:
    csv_path = Path(path) if path is not None else DEFAULT_LOCATIONS_PATH
    return pd.read_csv(csv_path)
