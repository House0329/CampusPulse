"""CampusPulse product surfaces. This module and app.py are the only Streamlit layers."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.data import load_locations
from src.explain import explain_space
from src.feedback import (
    PULSE_DISCLAIMER,
    PULSE_EMPTY,
    PULSE_HEADING,
    append_pulse,
    make_pulse,
    pulses_for_space,
)
from src.map_svg import build_map_svg, legend_html
from src.matching import (
    COMPARE_CAP,
    FEATURE_LABELS,
    PRIORITY_TO_FEATURE,
    START_POINTS,
    TASK_COLUMN,
    TASKS,
    add_compare_id,
    apply_priority_boost,
    compare_decision_hint,
    rank_spaces,
    space_features,
    task_weights,
)
from src.state import go, select_task

SYNTHETIC_DISCLAIMER = "Synthetic campus data · Schematic map · For prototype evaluation only."

TASK_BLURBS = {
    "Coding": "Power, Wi-Fi, and enough quiet to stay for a longer session.",
    "Reading": "Low noise, comfortable seating, and steady lighting.",
    "Writing": "Quiet enough to think, with a desk you can occupy.",
    "Group work": "Space to talk without feeling like you are in the way.",
    "Exam revision": "Calm, uncrowded, and comfortable enough to focus.",
}

PROFILE_VALUE_FEATURES = ("quiet", "wifi", "power", "comfort", "low_crowding", "discussion")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1120px; padding-top: 1.4rem; padding-bottom: 3rem;}
        [data-testid="stAppViewContainer"] {background: #F7F8FC;}
        [data-testid="stHeader"] {background: transparent;}
        footer {visibility: hidden;}
        /* Streamlit focuses the main pane on click; hide the typing caret
           except inside real text fields (selectbox search, etc.). */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlock"],
        [data-testid="stHeader"],
        .block-container,
        .stMarkdown {
            caret-color: transparent !important;
        }
        [data-testid="stMain"]:focus,
        [data-testid="stAppViewContainer"]:focus,
        [data-testid="stVerticalBlock"]:focus,
        .block-container:focus {
            outline: none !important;
        }
        input:not([type="hidden"]):not([type="range"]):not([type="checkbox"]):not([type="radio"]),
        textarea {
            caret-color: #111827 !important;
        }
        h1, h2, h3, label, .stMarkdown, .stCaption {color: #111827;}
        /* Streamlit puts button labels in <p>; a global p color makes dark-theme
           buttons look like solid black blocks until hover. */
        button[data-testid^="stBaseButton"],
        .stButton > button,
        .stFormSubmitButton > button {
            min-height: 48px !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #E5E7EB !important;
        }
        button[data-testid^="stBaseButton"] p,
        button[data-testid^="stBaseButton"] span,
        .stButton > button p,
        .stFormSubmitButton > button p {
            color: inherit !important;
        }
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primaryFormSubmit"],
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            background-color: #3657FF !important;
            border-color: #3657FF !important;
            color: #FFFFFF !important;
        }
        button[data-testid="stBaseButton-primary"] p,
        button[data-testid="stBaseButton-primaryFormSubmit"] p,
        .stButton > button[kind="primary"] p {
            color: #FFFFFF !important;
        }
        button[data-testid^="stBaseButton"]:hover {
            background-color: #EEF2FF !important;
            border-color: #3657FF !important;
            color: #111827 !important;
        }
        button[data-testid="stBaseButton-primary"]:hover,
        button[data-testid="stBaseButton-primaryFormSubmit"]:hover,
        .stButton > button[kind="primary"]:hover {
            background-color: #2C46D6 !important;
            border-color: #2C46D6 !important;
            color: #FFFFFF !important;
        }
        button[data-testid="stBaseButton-primary"]:hover p,
        .stButton > button[kind="primary"]:hover p {
            color: #FFFFFF !important;
        }
        [data-testid="stButtonGroup"] button,
        [data-testid="stPills"] button {
            color: #111827 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
        }
        [data-testid="stPills"] button p {
            color: inherit !important;
        }
        [data-testid="stSelectbox"] label,
        [data-testid="stSlider"] label {
            color: #111827 !important;
        }
        .cp-header {display:flex; align-items:center; gap:10px; margin-bottom: 4px;}
        .cp-wordmark {font-size: 28px; font-weight: 750; color:#111827; letter-spacing:-0.03em;}
        .cp-badge {
            display:inline-block; background:#F59E0B; color:#111827; font-weight:700;
            font-size:0.72rem; letter-spacing:0.06em; padding:4px 10px; border-radius:999px;
        }
        .cp-muted {color:#6B7280; font-size:0.95rem; line-height:1.45;}
        .cp-disclaimer {
            color:#6B7280; font-size:0.85rem; margin-top: 1.2rem;
            padding-top: 0.8rem; border-top: 1px solid #E5E7EB;
        }
        .cp-card {
            background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px;
            padding:20px; margin-bottom: 8px;
        }
        .cp-kicker {color:#3657FF; font-size:0.78rem; font-weight:700; letter-spacing:0.04em; text-transform:uppercase;}
        .cp-title {font-size:1.15rem; font-weight:750; color:#111827; margin: 6px 0 2px;}
        .cp-match {font-size:1.35rem; font-weight:750; color:#111827;}
        .cp-match span {color:#3657FF;}
        .cp-tags {display:flex; flex-wrap:wrap; gap:8px; margin-top:12px;}
        .cp-chip {
            border-radius:999px; padding:5px 10px; border:1px solid #E5E7EB;
            color:#111827; font-size:0.8rem; background:#F7F8FC;
        }
        .cp-chip-warn {background:#FFF8EB; border-color:#F8D48A; color:#92400E;}
        .cp-context {
            background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px;
            padding:14px 18px; color:#111827; margin-bottom: 8px;
        }
        .cp-map-wrap {
            background:#FFFFFF; border:1px solid #E5E7EB; border-radius:16px;
            padding:12px; height:420px; box-sizing:border-box;
        }
        .cp-map-wrap svg {width:100%; height:100%; display:block;}
        .cp-legend {display:flex; flex-wrap:wrap; gap:12px 16px; margin: 8px 2px 16px;}
        .cp-legend-item {display:flex; align-items:center; gap:6px; color:#6B7280; font-size:0.85rem;}
        .cp-legend-dot {width:10px; height:10px; border-radius:99px; display:inline-block;}
        .cp-why-title {font-weight:750; font-size:1.05rem; margin-bottom:8px;}
        .cp-reason {margin:0 0 6px; color:#111827;}
        .cp-bar-row {display:grid; grid-template-columns: 120px 1fr 42px; gap:10px; align-items:center; margin:8px 0;}
        .cp-bar-label {color:#6B7280; font-size:0.88rem;}
        .cp-bar-track {height:10px; background:#EEF1F8; border-radius:999px; overflow:hidden;}
        .cp-bar-fill {height:100%; background:#3657FF; border-radius:999px;}
        .cp-bar-val {font-size:0.85rem; color:#111827; text-align:right;}
        .cp-hint {background:#EEF2FF; border:1px solid #C7D2FE; border-radius:14px; padding:14px 16px; color:#111827;}
        .cp-table-wrap {overflow-x:auto;}
        .cp-table {width:100%; min-width: 560px; border-collapse:collapse; background:#fff; border-radius:16px;}
        .cp-table th, .cp-table td {padding:12px 14px; border-bottom:1px solid #E5E7EB; text-align:left;}
        .cp-table th {color:#6B7280; font-size:0.82rem; font-weight:600;}
        .cp-best {color:#0E9F6E; font-weight:700;}
        @media (max-width: 720px) {
            .cp-wordmark {font-size: 24px;}
            .cp-map-wrap {height:300px;}
            .cp-bar-row {grid-template-columns: 1fr; gap:4px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def get_locations() -> pd.DataFrame:
    return load_locations()


def _current_weights():
    priorities = list(st.session_state.priorities or [])
    return apply_priority_boost(task_weights(st.session_state.task), priorities)


def _ranked(df: pd.DataFrame) -> pd.DataFrame:
    return rank_spaces(
        df,
        st.session_state.task,
        st.session_state.start_point,
        list(st.session_state.priorities or []),
    )


def _features_for(row: pd.Series) -> dict[str, float]:
    start_x, start_y = START_POINTS[st.session_state.start_point]
    return space_features(row, start_x, start_y)


def _disclaimer() -> None:
    st.markdown(f'<p class="cp-disclaimer">{SYNTHETIC_DISCLAIMER}</p>', unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        '<div class="cp-header"><span class="cp-wordmark">CampusPulse</span>'
        '<span class="cp-badge">DEMO</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<p class="cp-muted">{SYNTHETIC_DISCLAIMER}</p>', unsafe_allow_html=True)


def _priority_tags(values: list[str]) -> str:
    if not values:
        return '<span class="cp-chip">No extra priorities</span>'
    return "".join(f'<span class="cp-chip">{html.escape(v)}</span>' for v in values)


def _space_tags(row: pd.Series, weights: dict[str, float]) -> list[str]:
    explanation = explain_space(row, weights, _features_for(row))
    tags = [str(row["cluster"])]
    for feat in explanation["reason_features"]:
        label = FEATURE_LABELS[feat]
        if label not in tags:
            tags.append(label)
    return tags[:3]


def _good_for(row: pd.Series) -> list[str]:
    ranked = sorted(TASK_COLUMN.items(), key=lambda item: float(row[item[1]]), reverse=True)
    labels = [name for name, col in ranked if float(row[col]) >= 3.8]
    return labels[:4] or [ranked[0][0]]


def _rating_display(row: pd.Series, feat: str) -> tuple[str, float]:
    if feat == "distance":
        value = float(row["distance_score"]) * 100
        return f"{int(round(value))}%", value / 100.0 * 5.0
    if feat == "low_crowding":
        value = 6.0 - float(row["crowding"])
        return f"{value:.1f}", value
    value = float(row[feat])
    return f"{value:.1f}", value


def render_discover() -> None:
    render_header()
    st.markdown("### What are you doing today?")
    st.markdown(
        '<p class="cp-muted">A good study space is not universally good — it is good for a particular task.</p>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="small")
    for index, task in enumerate(TASKS):
        col = left if index % 2 == 0 else right
        with col:
            selected = st.session_state.task == task
            if st.button(
                task,
                key=f"task_{task}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                select_task(task)
                st.rerun()

    st.markdown(f'<p class="cp-muted">{html.escape(TASK_BLURBS[st.session_state.task])}</p>', unsafe_allow_html=True)

    st.selectbox("Starting point", options=list(START_POINTS.keys()), key="start_point")

    if "priority_pills" not in st.session_state:
        st.session_state.priority_pills = list(st.session_state.priorities)

    st.pills(
        "Priorities (choose up to 3)",
        options=list(PRIORITY_TO_FEATURE.keys()),
        selection_mode="multi",
        key="priority_pills",
        help="These nudge the design presets. You do not need to tune the algorithm.",
    )

    pills = st.session_state.priority_pills or []
    if isinstance(pills, str):
        pills = [pills]

    if len(pills) > 3:
        st.warning("Choose up to three priorities.")

    if st.button("Find study spaces", type="primary", use_container_width=True, key="find_spaces"):
        if len(pills) > 3:
            st.warning("Choose up to three priorities.")
            st.stop()
        st.session_state.priorities = list(pills)
        go("results")
        st.rerun()

    _disclaimer()


def render_results() -> None:
    render_header()
    df = get_locations()
    ranked = _ranked(df)
    weights = _current_weights()
    top3 = ranked.head(3)
    priorities = list(st.session_state.priorities or [])

    context = (
        f'<div class="cp-context"><strong>{html.escape(st.session_state.task)}</strong> · '
        f'from {html.escape(st.session_state.start_point)}'
        f'<div class="cp-tags">{_priority_tags(priorities)}</div></div>'
    )
    st.markdown(context, unsafe_allow_html=True)

    edit, compare = st.columns([1, 1])
    with edit:
        if st.button("Edit task & priorities", use_container_width=True, key="edit_priorities"):
            go("discover")
            st.rerun()
    with compare:
        if st.session_state.compare_ids:
            label = f"Compare selected ({len(st.session_state.compare_ids)}/{COMPARE_CAP})"
            if st.button(label, type="primary", use_container_width=True, key="open_compare"):
                go("compare")
                st.rerun()

    if st.session_state.compare_notice:
        st.info(st.session_state.compare_notice)
        st.session_state.compare_notice = None

    st.markdown("#### Schematic campus")
    st.markdown(
        build_map_svg(ranked, top3["space_id"].tolist(), start=st.session_state.start_point),
        unsafe_allow_html=True,
    )
    st.markdown(legend_html(), unsafe_allow_html=True)
    st.caption("Pins show relative location on a fictional campus. This is not a navigation map.")

    st.markdown("#### Top matches")
    cols = st.columns(3)
    for index, (_, row) in enumerate(top3.iterrows()):
        with cols[index]:
            kicker = "Top match" if index == 0 else f"Match {index + 1}"
            tags = "".join(f'<span class="cp-chip">{html.escape(tag)}</span>' for tag in _space_tags(row, weights))
            st.markdown(
                f"""
                <div class="cp-card">
                  <div class="cp-kicker">{kicker}</div>
                  <div class="cp-title">{html.escape(str(row["name"]))}</div>
                  <div class="cp-match"><span>{int(row["match"])}%</span> match</div>
                  <div class="cp-muted">{html.escape(str(row["cluster"]))} · {html.escape(str(row["zone"]))}</div>
                  <div class="cp-tags">{tags}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View details", key=f"view_{row['space_id']}", use_container_width=True):
                st.session_state.selected_space = row["space_id"]
                go("detail")
                st.rerun()
            if st.button("Add to compare", key=f"addcmp_{row['space_id']}", use_container_width=True):
                ids, notice = add_compare_id(st.session_state.compare_ids, str(row["space_id"]))
                st.session_state.compare_ids = ids
                st.session_state.compare_notice = notice
                st.rerun()

    with st.expander("See remaining spaces"):
        rest = ranked.iloc[3:]
        for _, row in rest.iterrows():
            c1, c2, c3 = st.columns([3, 1.2, 1.3])
            c1.markdown(f"**{row['name']}** · {row['cluster']}")
            c2.markdown(f"{int(row['match'])}% match")
            if c3.button("View", key=f"list_{row['space_id']}"):
                st.session_state.selected_space = row["space_id"]
                go("detail")
                st.rerun()

    _disclaimer()


def render_detail() -> None:
    render_header()
    ranked = _ranked(get_locations())
    space_id = st.session_state.selected_space
    hit = ranked[ranked["space_id"] == space_id]
    if hit.empty:
        st.warning("Choose a space from the results map.")
        if st.button("Back to results", key="detail_missing"):
            go("results")
            st.rerun()
        return

    row = hit.iloc[0]
    weights = _current_weights()
    features = _features_for(row)
    explanation = explain_space(row, weights, features)

    if st.button("← Back to results", key="back_results"):
        go("results")
        st.rerun()

    st.markdown(
        f"""
        <div class="cp-card">
          <div class="cp-kicker">{html.escape(str(row["cluster"]))}</div>
          <div class="cp-title">{html.escape(str(row["name"]))}</div>
          <div class="cp-match"><span>{int(row["match"])}%</span> match · {html.escape(str(row["zone"]))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reasons = "".join(f'<p class="cp-reason">• {html.escape(text)}</p>' for text in explanation["reasons"])
    st.markdown(
        f"""
        <div class="cp-card">
          <div class="cp-why-title">{html.escape(explanation["headline"])}</div>
          {reasons}
          <p class="cp-muted"><span class="cp-chip cp-chip-warn">Trade-off</span> {html.escape(explanation["tradeoff"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_feats = sorted(weights, key=weights.get, reverse=True)[:5]
    bars = []
    for feat in top_feats:
        label, numeric = _rating_display(row, feat)
        width = max(4.0, min(100.0, (numeric / 5.0) * 100.0))
        bars.append(
            f'<div class="cp-bar-row"><div class="cp-bar-label">{html.escape(FEATURE_LABELS[feat])}</div>'
            f'<div class="cp-bar-track"><div class="cp-bar-fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="cp-bar-val">{html.escape(label)}</div></div>'
        )
    st.markdown(
        f'<div class="cp-card"><div class="cp-why-title">Study profile</div>{"".join(bars)}</div>',
        unsafe_allow_html=True,
    )

    tags = "".join(f'<span class="cp-chip">{html.escape(tag)}</span>' for tag in _good_for(row))
    st.markdown(
        f'<div class="cp-card"><div class="cp-why-title">Good for</div><div class="cp-tags">{tags}</div></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chosen_space == row["space_id"]:
        st.success(f'{row["name"]} is your choice for this session. Nothing is saved beyond this browser tab.')

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Add to compare", use_container_width=True, key="detail_compare"):
            ids, notice = add_compare_id(st.session_state.compare_ids, str(row["space_id"]))
            st.session_state.compare_ids = ids
            if notice:
                st.warning(notice)
            elif len(ids) >= 2:
                go("compare")
                st.rerun()
            else:
                st.info("Add one more space to compare.")
    with c2:
        if st.button("Choose this space", type="primary", use_container_width=True, key="detail_choose"):
            st.session_state.chosen_space = str(row["space_id"])
            st.rerun()

    _render_demo_pulse(str(row["space_id"]))
    _disclaimer()


def _render_demo_pulse(space_id: str) -> None:
    st.markdown(f"#### {PULSE_HEADING}")
    st.caption(PULSE_DISCLAIMER)

    with st.form(key=f"pulse_form_{space_id}"):
        c1, c2, c3 = st.columns(3)
        with c1:
            noise = st.slider("Noise", min_value=1, max_value=5, value=3, step=1, key=f"pulse_noise_{space_id}")
        with c2:
            crowding = st.slider("Crowding", min_value=1, max_value=5, value=3, step=1, key=f"pulse_crowding_{space_id}")
        with c3:
            comfort = st.slider("Comfort", min_value=1, max_value=5, value=3, step=1, key=f"pulse_comfort_{space_id}")
        would_return = st.checkbox("Would choose again", key=f"pulse_return_{space_id}")
        submitted = st.form_submit_button("Submit demo pulse")

    if submitted:
        pulse = make_pulse(space_id, noise, crowding, comfort, would_return)
        st.session_state.demo_feedback = append_pulse(list(st.session_state.demo_feedback), pulse)
        st.rerun()

    local = pulses_for_space(list(st.session_state.demo_feedback), space_id)
    if not local:
        st.markdown(f'<p class="cp-muted">{PULSE_EMPTY} {PULSE_DISCLAIMER}</p>', unsafe_allow_html=True)
        return

    st.markdown('<p class="cp-muted">Your demo pulse this session — not campus activity.</p>', unsafe_allow_html=True)
    for index, pulse in enumerate(local, start=1):
        again = "yes" if pulse["would_return"] else "no"
        st.markdown(
            f"- Pulse {index}: noise {pulse['noise']}, crowding {pulse['crowding']}, "
            f"comfort {pulse['comfort']}, would choose again: {again}"
        )


def render_compare() -> None:
    render_header()
    if st.button("← Back to results", key="compare_back"):
        go("results")
        st.rerun()

    ids = list(st.session_state.compare_ids)
    if len(ids) < 2:
        st.markdown(
            '<div class="cp-card"><p>Add 2–3 spaces from the results list to compare them side by side.</p></div>',
            unsafe_allow_html=True,
        )
        _disclaimer()
        return

    ranked = _ranked(get_locations())
    compare_df = ranked[ranked["space_id"].isin(ids)].copy()
    compare_df = compare_df.sort_values(["match", "space_id"], ascending=[False, True], kind="mergesort")

    st.markdown(f'<div class="cp-hint">{html.escape(compare_decision_hint(compare_df))}</div>', unsafe_allow_html=True)
    st.caption("Match score is a guide, not the only answer. Use the rows below to see the trade-offs.")

    weights = _current_weights()
    features = [feat for feat, _weight in sorted(weights.items(), key=lambda item: item[1], reverse=True)[:6]]

    header_cells = "".join(
        f'<th>{html.escape(str(row["name"]))}<br><span class="cp-match"><span>{int(row["match"])}%</span></span></th>'
        for _, row in compare_df.iterrows()
    )
    body_rows = []
    for feat in features:
        values = []
        raw_values = []
        for _, row in compare_df.iterrows():
            label, numeric = _rating_display(row, feat)
            values.append(label)
            raw_values.append(numeric)
        best = max(raw_values) if raw_values else 0
        cells = []
        for label, numeric in zip(values, raw_values):
            klass = ' class="cp-best"' if numeric == best and best > 0 else ""
            cells.append(f"<td{klass}>{html.escape(label)}</td>")
        body_rows.append(
            f"<tr><th>{html.escape(FEATURE_LABELS[feat])}</th>{''.join(cells)}</tr>"
        )

    st.markdown(
        f'<div class="cp-table-wrap"><table class="cp-table"><thead><tr><th>Attribute</th>{header_cells}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table></div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Remove from comparison")
    cols = st.columns(len(compare_df))
    for index, (_, row) in enumerate(compare_df.iterrows()):
        with cols[index]:
            if st.button(f'Remove {row["name"]}', key=f"rm_{row['space_id']}", use_container_width=True):
                st.session_state.compare_ids = [sid for sid in ids if sid != row["space_id"]]
                st.rerun()
            if st.button("View details", key=f"cmpview_{row['space_id']}", use_container_width=True):
                st.session_state.selected_space = row["space_id"]
                go("detail")
                st.rerun()

    _disclaimer()


def render_app() -> None:
    inject_styles()
    page = st.session_state.get("page", "discover")
    if page == "discover":
        render_discover()
    elif page == "results":
        render_results()
    elif page == "detail":
        render_detail()
    elif page == "compare":
        render_compare()
    else:
        go("discover")
        render_discover()
