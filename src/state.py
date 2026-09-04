"""Session-only UI state. This is the only state store — no database."""

from __future__ import annotations

import streamlit as st

from src.matching import TASK_DEFAULT_PRIORITIES

DEFAULT_STATE = {
    "page": "discover",
    "task": "Coding",
    "start_point": "North Gate",
    "priorities": list(TASK_DEFAULT_PRIORITIES["Coding"]),
    "selected_space": None,
    "compare_ids": [],
    "demo_feedback": [],
    "chosen_space": None,
    "compare_notice": None,
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def go(page: str) -> None:
    st.session_state.page = page


def select_task(task: str) -> None:
    st.session_state.task = task
    defaults = list(TASK_DEFAULT_PRIORITIES[task])
    st.session_state.priorities = defaults
    st.session_state.priority_pills = defaults
