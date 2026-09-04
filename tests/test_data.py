"""Phase 1: synthetic dataset bounds, count, and seed-42 determinism."""

from pathlib import Path

import pandas as pd

from src.synthetic import RATING_COLUMNS, SPACE_SEEDS, build_synthetic_dataset

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "locations.csv"


def test_space_seed_count_is_18():
    assert len(SPACE_SEEDS) == 18


def test_dataset_has_18_rows():
    df = build_synthetic_dataset(seed=42)
    assert len(df) == 18
    assert df["space_id"].nunique() == 18


def test_ratings_are_clipped_to_1_5():
    df = build_synthetic_dataset(seed=42)
    for col in RATING_COLUMNS:
        assert df[col].between(1.0, 5.0).all(), col


def test_coordinates_are_within_0_100():
    df = build_synthetic_dataset(seed=42)
    assert df["x"].between(0.0, 100.0).all()
    assert df["y"].between(0.0, 100.0).all()


def test_seed_42_is_deterministic():
    a = build_synthetic_dataset(seed=42)
    b = build_synthetic_dataset(seed=42)
    pd.testing.assert_frame_equal(a, b)


def test_csv_matches_canonical_generator():
    assert CSV_PATH.is_file(), "Run: python scripts/build_dataset.py"
    generated = build_synthetic_dataset(seed=42)
    saved = pd.read_csv(CSV_PATH)
    shared = [c for c in generated.columns if c in saved.columns]
    pd.testing.assert_frame_equal(
        generated[shared].reset_index(drop=True),
        saved[shared].reset_index(drop=True),
        check_dtype=False,
    )
