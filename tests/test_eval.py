"""Phase 8: illustrative evaluation file is labelled synthetic and reproducible."""

from pathlib import Path

import pandas as pd

from scripts.generate_synthetic_eval import (
    COLUMN_ORDER,
    N_PROFILES,
    OUT_PATH,
    TASKS,
    build_synthetic_evaluation,
)

ROOT = Path(__file__).resolve().parents[1]


def test_eval_generator_is_deterministic():
    a = build_synthetic_evaluation(seed=2026)
    b = build_synthetic_evaluation(seed=2026)
    pd.testing.assert_frame_equal(a, b)


def test_eval_csv_is_labelled_synthetic_illustrative():
    assert OUT_PATH.is_file(), "Run: python scripts/generate_synthetic_eval.py"
    df = pd.read_csv(OUT_PATH)
    assert list(df.columns)[:1] == ["data_type"]
    assert list(df.columns) == COLUMN_ORDER
    assert (df["data_type"] == "synthetic_illustrative").all()
    assert len(df) == N_PROFILES * len(TASKS) * 2
    assert set(df["condition"]) == {"baseline_a", "campuspulse_b"}
    assert "participant" not in df.columns.str.lower().tolist()


def test_docs_do_not_claim_a_human_study():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    data_note = (ROOT / "DATA_NOTE.md").read_text(encoding="utf-8").lower()
    research = (ROOT / "research" / "README.md").read_text(encoding="utf-8").lower()
    blob = readme + "\n" + data_note + "\n" + research
    assert "synthetic campus data" in blob
    assert "must not be reported as a human-subject study" in research
    assert "we recruited" not in blob
    assert "user study results" not in blob
    assert "not a recruited user study" in readme
