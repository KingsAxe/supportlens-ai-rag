"""Placeholder Streamlit page for future monitoring work."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Monitoring Dashboard", page_icon="??", layout="wide")
st.title("Monitoring Dashboard")

st.warning("This dashboard is intentionally deferred to the next phase.")
st.markdown(
    """
Planned next-phase items:

- usage and latency monitoring
- thumbs up / thumbs down feedback capture
- retrieval source mix analysis
- low-confidence and escalation tracking
- category and intent trend charts
"""
)
