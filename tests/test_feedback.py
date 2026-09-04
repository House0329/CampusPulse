"""Phase 6: demo pulse stays in memory and never writes campus files."""

from pathlib import Path

import pytest

from src.feedback import append_pulse, make_pulse, pulses_for_space

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "locations.csv"


def test_pulse_bounds_rejected():
    with pytest.raises(ValueError):
        make_pulse("S01", noise=0, crowding=3, comfort=3, would_return=True)
    with pytest.raises(ValueError):
        make_pulse("S01", noise=3, crowding=6, comfort=3, would_return=False)


def test_append_pulse_does_not_touch_csv():
    before = CSV_PATH.read_bytes()
    entries = append_pulse(
        [],
        make_pulse("S01", noise=4, crowding=2, comfort=5, would_return=True),
    )
    after = CSV_PATH.read_bytes()
    assert before == after
    assert entries[0]["space_id"] == "S01"
    assert pulses_for_space(entries, "S02") == []
    assert len(pulses_for_space(entries, "S01")) == 1
