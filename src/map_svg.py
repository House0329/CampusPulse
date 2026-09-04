"""Inline schematic campus map. Coordinates are 0–100 and not geographic."""

from __future__ import annotations

import html
from typing import Iterable

import pandas as pd

from src.matching import START_POINTS

CLUSTER_COLORS = {
    "Deep Focus": "#3657FF",
    "Quick Work": "#0E9F6E",
    "Social Study": "#D97706",
    "Group Collaboration": "#7C3AED",
}

ZONES = (
    {"name": "North", "x": 5, "y": 8, "w": 42, "h": 36, "fill": "#E8EEFF"},
    {"name": "East", "x": 53, "y": 8, "w": 42, "h": 36, "fill": "#E7F7F0"},
    {"name": "West", "x": 5, "y": 52, "w": 42, "h": 40, "fill": "#FFF4E5"},
    {"name": "South", "x": 53, "y": 52, "w": 42, "h": 40, "fill": "#F3E8FF"},
)


def _cluster_color(name: str) -> str:
    return CLUSTER_COLORS.get(str(name), "#6B7280")


def build_map_svg(
    df: pd.DataFrame,
    ranked_ids: Iterable[str],
    start: str | None = None,
) -> str:
    """Return an SVG campus schematic. Top-3 pins are numbered; others are quieter dots."""
    top_ids = [str(x) for x in list(ranked_ids)[:3]]
    rank_of = {space_id: index + 1 for index, space_id in enumerate(top_ids)}

    parts: list[str] = [
        '<div class="cp-map-wrap">',
        '<svg viewBox="0 0 100 100" role="img" aria-label="Schematic campus map" class="campus-map">',
        '<rect x="0" y="0" width="100" height="100" rx="3" fill="#F7F8FC" stroke="#E5E7EB" stroke-width="0.4"/>',
    ]

    for zone in ZONES:
        parts.append(
            f'<rect x="{zone["x"]}" y="{zone["y"]}" width="{zone["w"]}" height="{zone["h"]}" '
            f'rx="2.2" fill="{zone["fill"]}" stroke="#E5E7EB" stroke-width="0.35"/>'
        )
        parts.append(
            f'<text x="{zone["x"] + 2.2}" y="{zone["y"] + 5}" fill="#6B7280" '
            f'font-size="3.2" font-family="Inter, Arial, sans-serif">{zone["name"]}</text>'
        )

    parts.append(
        '<rect x="44.5" y="42" width="11" height="12" rx="1.2" fill="#EEF1F8" stroke="#E5E7EB" stroke-width="0.3"/>'
        '<text x="50" y="49.2" text-anchor="middle" fill="#9CA3AF" font-size="2.4" '
        'font-family="Inter, Arial, sans-serif">Quad</text>'
    )

    if start and start in START_POINTS:
        sx, sy = START_POINTS[start]
        parts.append(
            f'<rect x="{sx - 1.6}" y="{sy - 1.6}" width="3.2" height="3.2" rx="0.4" '
            f'transform="rotate(45 {sx} {sy})" fill="#111827"/>'
        )
        parts.append(
            f'<text x="{sx + 3.2}" y="{sy + 1.1}" fill="#111827" font-size="2.6" '
            f'font-family="Inter, Arial, sans-serif">{html.escape(start)}</text>'
        )

    rest = df[~df["space_id"].astype(str).isin(top_ids)]
    for _, row in rest.iterrows():
        color = _cluster_color(row.get("cluster", ""))
        parts.append(
            f'<circle cx="{float(row["x"]):.2f}" cy="{float(row["y"]):.2f}" r="1.6" '
            f'fill="{color}" fill-opacity="0.45" stroke="#FFFFFF" stroke-width="0.35"/>'
        )

    top_df = df[df["space_id"].astype(str).isin(top_ids)].copy()
    top_df["_rank"] = top_df["space_id"].astype(str).map(rank_of)
    for _, row in top_df.sort_values("_rank").iterrows():
        color = _cluster_color(row.get("cluster", ""))
        x = float(row["x"])
        y = float(row["y"])
        rank = int(row["_rank"])
        name = html.escape(str(row["name"]))
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.6" fill="{color}" stroke="#FFFFFF" stroke-width="0.7"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{y + 1.05:.2f}" text-anchor="middle" fill="#FFFFFF" '
            f'font-size="2.6" font-weight="700" font-family="Inter, Arial, sans-serif">{rank}</text>'
        )
        label_x = x + 3.4 if x < 78 else x - 3.4
        anchor = "start" if x < 78 else "end"
        parts.append(
            f'<text x="{label_x:.2f}" y="{y - 2.4:.2f}" text-anchor="{anchor}" fill="#111827" '
            f'font-size="2.7" font-weight="600" font-family="Inter, Arial, sans-serif">{name}</text>'
        )

    parts.append("</svg></div>")
    return "".join(parts)


def legend_html() -> str:
    chips = []
    for name, color in CLUSTER_COLORS.items():
        chips.append(
            f'<span class="cp-legend-item"><span class="cp-legend-dot" style="background:{color}"></span>'
            f"{html.escape(name)}</span>"
        )
    return '<div class="cp-legend">' + "".join(chips) + "</div>"
