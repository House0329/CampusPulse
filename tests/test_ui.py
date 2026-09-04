"""Phase 5: product-mode UI loads without a browser and keeps the synthetic label visible."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.ui import SYNTHETIC_DISCLAIMER

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def _app() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=20)


def test_discover_shows_synthetic_disclaimer():
    at = _app().run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "CampusPulse" in blob
    assert SYNTHETIC_DISCLAIMER in blob
    assert "Schematic map" in blob


def test_find_study_spaces_reaches_results():
    at = _app().run()
    at.button(key="find_spaces").click().run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Top matches" in blob or "Schematic campus" in blob
    assert SYNTHETIC_DISCLAIMER in blob
    assert "pca" not in blob.lower()
    assert "cluster 0" not in blob.lower()


def test_compare_empty_state_asks_for_two_spaces():
    at = _app().run()
    at.session_state["page"] = "compare"
    at.session_state["compare_ids"] = []
    at.run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "2–3" in blob or "2-3" in blob or "Add 2" in blob


def test_detail_shows_why_and_tradeoff():
    at = _app().run()
    at.session_state["page"] = "detail"
    at.session_state["selected_space"] = "S01"
    at.session_state["task"] = "Coding"
    at.session_state["start_point"] = "North Gate"
    at.session_state["priorities"] = ["Quiet", "Power", "Wi-Fi"]
    at.run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Why this space?" in blob
    assert "Trade-off" in blob
    assert SYNTHETIC_DISCLAIMER in blob
    assert "pca" not in blob.lower()
    assert "cluster 0" not in blob.lower()


def test_compare_two_spaces_shows_decision_hint():
    at = _app().run()
    at.session_state["page"] = "compare"
    at.session_state["compare_ids"] = ["S01", "S06"]
    at.session_state["task"] = "Coding"
    at.run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Attribute" in blob
    assert "clearest fit" in blob or "close alternative" in blob
    assert SYNTHETIC_DISCLAIMER in blob


def test_view_details_button_opens_space_detail():
    at = _app().run()
    at.button(key="find_spaces").click().run()
    view_key = next(button.key for button in at.button if str(button.key).startswith("view_"))
    at.button(key=view_key).click().run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Why this space?" in blob
    assert "Study profile" in blob
    assert "Good for" in blob


def test_add_two_spaces_opens_compare():
    at = _app().run()
    at.button(key="find_spaces").click().run()
    add_keys = [button.key for button in at.button if str(button.key).startswith("addcmp_")]
    at.button(key=add_keys[0]).click().run()
    at.button(key=add_keys[1]).click().run()
    at.button(key="open_compare").click().run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Attribute" in blob
    assert "clearest fit" in blob or "close alternative" in blob


def test_detail_shows_session_only_pulse_empty_state():
    at = _app().run()
    at.session_state["page"] = "detail"
    at.session_state["selected_space"] = "S01"
    at.run()
    assert not at.exception
    blob = "\n".join(str(block.value) for block in at.markdown) + "\n".join(
        str(block.value) for block in at.caption
    )
    assert "Demo pulse" in blob or "demo pulse" in blob.lower()
    assert "Stored only in this browser session; not real campus activity." in blob
    assert "No demo pulse submitted in this session." in blob
    assert "students reported" not in blob.lower()
    assert "38" not in blob


def test_submit_demo_pulse_stays_in_session_not_csv():
    from src.data import DEFAULT_LOCATIONS_PATH

    before = DEFAULT_LOCATIONS_PATH.read_bytes()
    at = _app().run()
    at.session_state["page"] = "detail"
    at.session_state["selected_space"] = "S01"
    at.run()
    at.slider(key="pulse_noise_S01").set_value(5)
    at.slider(key="pulse_crowding_S01").set_value(2)
    at.slider(key="pulse_comfort_S01").set_value(4)
    at.checkbox(key="pulse_return_S01").check()
    at.button(key="FormSubmitter:pulse_form_S01-Submit demo pulse").click().run()
    assert not at.exception
    pulses = list(at.session_state["demo_feedback"])
    assert len(pulses) == 1
    assert pulses[0]["space_id"] == "S01"
    assert pulses[0]["noise"] == 5
    assert pulses[0]["would_return"] is True
    assert DEFAULT_LOCATIONS_PATH.read_bytes() == before
    blob = "\n".join(str(block.value) for block in at.markdown)
    assert "Pulse 1" in blob
    assert "not campus activity" in blob.lower() or "not real campus activity" in blob.lower()
