"""CampusPulse Streamlit entry — single-page product shell."""

import streamlit as st

from src.state import init_state
from src.ui import render_app

st.set_page_config(
    page_title="CampusPulse",
    layout="wide",
)

init_state()
render_app()
