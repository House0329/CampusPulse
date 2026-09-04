"""Phase 7: regression scenarios on the canonical synthetic campus CSV."""

from src.data import load_locations
from src.matching import rank_spaces


def _ranked(task: str, start: str, priorities: list[str]):
    return rank_spaces(load_locations(), task, start, priorities)


def test_coding_top3_is_focus_or_quick_work():
    top = _ranked("Coding", "North Gate", ["Quiet", "Power", "Wi-Fi"]).head(3)
    assert top["cluster"].isin(["Deep Focus", "Quick Work"]).all()
    again = _ranked("Coding", "North Gate", ["Quiet", "Power", "Wi-Fi"]).head(3)
    assert list(top["space_id"]) == list(again["space_id"])
    assert top["match"].between(0, 100).all()


def test_group_work_top3_is_collaboration():
    top = _ranked("Group work", "Main Hall", ["Discussion-friendly", "Comfort"]).head(3)
    assert (top["cluster"] == "Group Collaboration").sum() >= 2


def test_exam_revision_top3_is_deep_focus():
    top = _ranked("Exam revision", "Library Hub", ["Quiet", "Comfort"]).head(3)
    assert (top["cluster"] == "Deep Focus").sum() >= 2


def test_writing_close_by_lifts_nearby_spaces():
    near = _ranked("Writing", "Residence", ["Close by"])
    far = _ranked("Writing", "North Gate", ["Close by"])
    residence_rank_from_home = int(near.set_index("space_id").loc["S14", "rank"])
    residence_rank_from_north = int(far.set_index("space_id").loc["S14", "rank"])
    assert residence_rank_from_home < residence_rank_from_north

    library_from_north = int(far.set_index("space_id").loc["S01", "rank"])
    library_from_residence = int(near.set_index("space_id").loc["S01", "rank"])
    assert library_from_north < library_from_residence
    assert float(near.set_index("space_id").loc["S14", "distance_score"]) > float(
        far.set_index("space_id").loc["S14", "distance_score"]
    )
