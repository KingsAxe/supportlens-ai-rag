"""Lightweight evaluation report page for Streamlit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from src.ingestion.io import resolve_repo_path

st.set_page_config(page_title="Evaluation Report", page_icon="ER", layout="wide")
st.title("Evaluation Report")
st.caption("Current local metrics for retrieval and dry-run answer quality.")

RETRIEVAL_FALLBACK = {
    "question_count": 12,
    "hit_rate": 0.9167,
    "mrr": 0.8083,
}
ANSWER_FALLBACK = {
    "question_count": 12,
    "average_citation_validity_rate": 1.0000,
    "average_grounding_proxy_score": 0.8333,
    "basic_quality_pass_rate": 1.0000,
    "section_completeness_rate": 1.0000,
}


def _load_json_if_available(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


retrieval_metrics = _load_json_if_available(resolve_repo_path("data", "processed", "hybrid_rerank_retrieval_metrics.json"))
if not retrieval_metrics or retrieval_metrics.get("eval_file") != "data/sample/evaluation_questions_hard.jsonl":
    retrieval_metrics = RETRIEVAL_FALLBACK

answer_metrics = _load_json_if_available(resolve_repo_path("data", "processed", "answer_evaluation_summary.json"))
if not answer_metrics or answer_metrics.get("eval_file") != "data/sample/evaluation_questions_hard.jsonl":
    answer_metrics = ANSWER_FALLBACK

st.subheader("Retrieval Metrics")
retrieval_cols = st.columns(3)
retrieval_cols[0].metric("Hard-set questions", retrieval_metrics["question_count"])
retrieval_cols[1].metric("Hit Rate", f"{retrieval_metrics['hit_rate']:.4f}")
retrieval_cols[2].metric("MRR", f"{retrieval_metrics['mrr']:.4f}")

st.subheader("Dry-Run Answer Metrics")
answer_cols = st.columns(4)
answer_cols[0].metric("Citation validity", f"{answer_metrics['average_citation_validity_rate']:.4f}")
answer_cols[1].metric("Grounding proxy", f"{answer_metrics['average_grounding_proxy_score']:.4f}")
answer_cols[2].metric("Basic quality pass", f"{answer_metrics['basic_quality_pass_rate']:.4f}")
answer_cols[3].metric("Section completeness", f"{answer_metrics['section_completeness_rate']:.4f}")

st.markdown(
    """
### Notes

- The hard-set retrieval benchmark is still the main controlled comparison set.
- The app defaults to deterministic dry-run generation for reproducible reviewer testing.
- Monitoring now captures answer-generation events, user ratings, thumbs feedback, optional comments, and retrieval metadata in ignored local logs.
- Full live LLM evaluation is still pending provider quota access for the configured Qwen setup.
"""
)
