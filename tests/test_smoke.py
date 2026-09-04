"""Phase 0 smoke tests: scaffold exists and the runtime stack is the specified four packages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_app_py_exists():
    assert (ROOT / "app.py").is_file()


def test_requirements_only_allowed_packages():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for pkg in ("streamlit", "pandas", "numpy", "pytest"):
        assert pkg in text
    forbidden = ("folium", "sklearn", "scikit-learn", "plotly", "matplotlib", "geopandas")
    for pkg in forbidden:
        assert pkg not in text


def test_pytest_ini_exists():
    assert (ROOT / "pytest.ini").is_file()
