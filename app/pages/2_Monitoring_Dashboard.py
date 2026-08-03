"""Monitoring dashboard page for SupportLens AI."""

from __future__ import annotations

import streamlit as st

from src.monitoring.analytics import load_monitoring_events, summarize_monitoring_events
from src.monitoring.logger import create_demo_monitoring_events

st.set_page_config(page_title="Monitoring Dashboard", page_icon="MD", layout="wide")
st.title("Monitoring Dashboard")
st.caption("Local feedback and usage monitoring for the submission-ready reviewer workflow.")

col_a, col_b = st.columns([1.4, 1])
with col_a:
    st.markdown(
        """
This dashboard reads local monitoring events from `data/processed/monitoring_events.jsonl`.

If no events are visible yet:

- go to **Ask SupportLens**;
- generate a few answers;
- submit feedback;
- return here.
"""
    )
with col_b:
    if st.button("Create demo monitoring events", use_container_width=True):
        demo_events = create_demo_monitoring_events()
        st.success(f"Wrote {len(demo_events)} synthetic demo monitoring events to the ignored local log.")


events = load_monitoring_events()
if not events:
    st.warning("Go to Ask SupportLens, generate a few answers, submit feedback, then return here.")
    st.stop()

summary = summarize_monitoring_events(events)
metric_cols = st.columns(6)
metric_cols[0].metric("Answers generated", summary["total_questions"])
metric_cols[1].metric("Feedback submissions", summary["total_feedback_submissions"])
metric_cols[2].metric("Average rating", f"{summary['average_rating']:.2f}" if summary["average_rating"] is not None else "N/A")
metric_cols[3].metric("Thumbs up", summary["thumbs_up_count"])
metric_cols[4].metric("Thumbs down", summary["thumbs_down_count"])
metric_cols[5].metric("Average latency ms", f"{summary['average_latency_ms']:.2f}" if summary["average_latency_ms"] is not None else "N/A")

st.subheader("Event Trends")
trend_left, trend_right = st.columns(2)
with trend_left:
    st.markdown("**Questions generated over time**")
    if summary["answer_trend"]:
        st.line_chart(summary["answer_trend"], x="date", y="count")
    else:
        st.info("No answer-generation trend data available yet.")
with trend_right:
    st.markdown("**Feedback submissions over time**")
    if summary["feedback_trend"]:
        st.line_chart(summary["feedback_trend"], x="date", y="count")
    else:
        st.info("No feedback trend data available yet.")

chart_a, chart_b = st.columns(2)
with chart_a:
    st.markdown("**Rating distribution**")
    if summary["rating_distribution"]:
        st.bar_chart(summary["rating_distribution"], x="rating", y="count")
    else:
        st.info("No rating data available yet.")
with chart_b:
    st.markdown("**Thumbs up vs thumbs down**")
    thumbs_rows = [
        {"thumbs": "up", "count": summary["thumbs_up_count"]},
        {"thumbs": "down", "count": summary["thumbs_down_count"]},
    ]
    st.bar_chart(thumbs_rows, x="thumbs", y="count")

chart_c, chart_d = st.columns(2)
with chart_c:
    st.markdown("**Dataset mode usage**")
    if summary["most_common_dataset_modes"]:
        st.bar_chart(summary["most_common_dataset_modes"], x="dataset_mode", y="count")
    else:
        st.info("No dataset mode usage recorded yet.")
with chart_d:
    st.markdown("**Prompt version usage**")
    if summary["top_prompt_versions"]:
        st.bar_chart(summary["top_prompt_versions"], x="prompt_version", y="count")
    else:
        st.info("No prompt version usage recorded yet.")

chart_e, chart_f = st.columns(2)
with chart_e:
    st.markdown("**Source type distribution**")
    if summary["most_common_source_types"]:
        st.bar_chart(summary["most_common_source_types"], x="source_type", y="count")
    else:
        st.info("No source type data available yet.")
with chart_f:
    st.markdown("**Dry-run vs real-mode usage**")
    if summary["dry_run_vs_real"]:
        st.bar_chart(summary["dry_run_vs_real"], x="mode", y="count")
    else:
        st.info("No generation mode usage recorded yet.")

st.subheader("Latency Distribution")
if summary["latency_distribution"]:
    st.bar_chart(summary["latency_distribution"], y="latency_ms")
else:
    st.info("No latency data available yet.")
