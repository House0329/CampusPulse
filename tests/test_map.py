"""Phase 5: schematic SVG map — no real geography, numbered Top 3."""

from src.map_svg import build_map_svg, legend_html
from src.matching import rank_spaces
from src.synthetic import build_synthetic_dataset
from src.analysis import assign_clusters_and_pca


def _ranked():
    df, _meta = assign_clusters_and_pca(build_synthetic_dataset(seed=42))
    return rank_spaces(df, "Coding", "North Gate", ["Quiet", "Power", "Wi-Fi"])


def test_map_svg_has_aria_label_and_eighteen_pins():
    ranked = _ranked()
    svg = build_map_svg(ranked, ranked.head(3)["space_id"].tolist(), start="North Gate")
    assert 'aria-label="Schematic campus map"' in svg
    assert svg.count("<circle") == 18
    assert "folium" not in svg.lower()
    assert "pca" not in svg.lower()
    assert "Library 4F" in svg or ranked.iloc[0]["name"] in svg


def test_map_numbers_top3_and_marks_start():
    ranked = _ranked()
    top_ids = ranked.head(3)["space_id"].tolist()
    svg = build_map_svg(ranked, top_ids, start="North Gate")
    assert ">1</text>" in svg
    assert ">2</text>" in svg
    assert ">3</text>" in svg
    assert "North Gate" in svg


def test_legend_uses_text_not_color_alone():
    markup = legend_html()
    for name in ("Deep Focus", "Quick Work", "Social Study", "Group Collaboration"):
        assert name in markup
