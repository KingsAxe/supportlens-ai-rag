"""Main Streamlit page for SupportLens question answering."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.rag.answer import (
    generate_support_answer,
    knowledge_base_status,
    normalize_dataset_mode,
    prepare_knowledge_base,
)
from src.rag.config import load_config
from src.rag.prompts import PROMPT_VARIANTS

DATASET_OPTIONS = ["sample", "public-sample", "combined-sample"]
EXAMPLE_QUESTIONS = [
    "A customer says they were charged twice after upgrading. What should support do?",
    "A customer wants to cancel after a failed payment and asks for a refund. How should support respond?",
    "A customer cannot access their account after multiple login attempts. What should support check?",
]

st.set_page_config(page_title="Ask SupportLens", page_icon="??", layout="wide")
st.title("Ask SupportLens")
st.caption("Grounded support-answer generation with citations, using `hybrid_rerank` and a safe dry-run default.")

config = load_config()


def _format_mode_label(mode: str | None) -> str:
    if not mode:
        return "not prepared"
    return mode.replace("_", "-")


def _short_preview(text: str, limit: int = 160) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


with st.sidebar:
    st.header("Controls")
    dataset_mode_display = st.selectbox("Dataset mode", DATASET_OPTIONS, index=2)
    dataset_mode_internal = normalize_dataset_mode(dataset_mode_display)
    st.caption("Retrieval method: `hybrid_rerank` (fixed for Attempt 1)")
    top_k = st.slider("Top K", min_value=3, max_value=10, value=5)
    prompt_version = st.selectbox("Prompt version", sorted(PROMPT_VARIANTS), index=0)

    generation_options = ["dry-run"]
    generation_help = "Deterministic reviewer-friendly mode."
    if config.real_llm_available:
        generation_options.append("real-llm")
        generation_help = "Real mode is optional and depends on working provider quota and API access."
    generation_mode = st.radio("Generation mode", generation_options, index=0, help=generation_help)

    if st.button("Prepare / Refresh Knowledge Base", use_container_width=True):
        with st.spinner(f"Preparing knowledge base for {dataset_mode_display}..."):
            summary = prepare_knowledge_base(dataset_mode_internal)
        st.session_state["last_prepared_mode"] = summary["mode"]
        st.success(
            f"Prepared {_format_mode_label(summary['mode'])}: "
            f"{summary['support_case_count']} support cases, {summary['policy_count']} policies, "
            f"{summary['playbook_count']} playbooks, {summary['chunk_count']} chunks."
        )

status = knowledge_base_status(dataset_mode_internal)
status_cols = st.columns(3)
status_cols[0].metric("Selected dataset mode", dataset_mode_display)
status_cols[1].metric("Prepared knowledge base", _format_mode_label(status["current_mode"]))
status_cols[2].metric("Ready for generation", "Yes" if status["ready"] else "No")

if not status["ready"]:
    st.warning(
        "The selected knowledge base is not prepared yet. Use **Prepare / Refresh Knowledge Base** "
        "before generating an answer. The app does not auto-run multiple ingestion modes on rerun."
    )
else:
    st.success(
        f"Knowledge base ready in {_format_mode_label(status['current_mode'])} mode. "
        "This app uses one selected ingestion mode at a time to avoid processed-data corruption."
    )

st.subheader("Support Question")
example_columns = st.columns(3)
for idx, question in enumerate(EXAMPLE_QUESTIONS):
    if example_columns[idx].button(f"Use Example {idx + 1}", use_container_width=True):
        st.session_state["support_question"] = question

question = st.text_area(
    "Enter a customer-support question",
    key="support_question",
    height=140,
    placeholder="Describe the customer issue, requested action, and any known support context.",
)

if st.button("Generate Support Answer", type="primary", use_container_width=True):
    if not question.strip():
        st.error("Enter a support question first.")
    elif not status["ready"]:
        st.error("Prepare the selected knowledge base before generating an answer.")
    else:
        dry_run = generation_mode != "real-llm"
        with st.spinner("Generating grounded support answer..."):
            try:
                result = generate_support_answer(
                    question=question.strip(),
                    top_k=top_k,
                    dry_run=dry_run,
                    prompt_version=prompt_version,
                    dataset_mode=dataset_mode_display,
                )
            except Exception as exc:  # pragma: no cover - UI fallback path
                st.exception(exc)
            else:
                st.session_state["last_answer_result"] = result

result: dict[str, Any] | None = st.session_state.get("last_answer_result")
if result:
    st.subheader("Generated Answer")
    st.markdown(result["answer_text"])

    st.subheader("Evidence / Citations")
    evidence_rows = [
        {
            "citation_id": item["citation_id"],
            "source_type": item["source_type"],
            "source_id": item["source_id"],
            "title_category": f"{item['title']} / {item['category']}",
            "score": round(float(item["score"]), 4),
            "text_preview": _short_preview(item["text"]),
        }
        for item in result["citations"]
    ]
    st.dataframe(evidence_rows, use_container_width=True, hide_index=True)

    st.subheader("Retrieval Metadata")
    metadata = {
        "retrieval_method": result["retrieval_method"],
        "dataset_mode": result["dataset_mode"].replace("_", "-"),
        "top_k": top_k,
        "prompt_version": result["prompt_version"],
        "dry_run": result["dry_run"],
        "provider": result["provider"],
        "model": result["model"],
        "latency_ms": result["latency_ms"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
    }
    st.json(metadata)

st.info(
    "Dry-run mode is deterministic and reviewer-friendly. Real LLM mode requires a configured provider, "
    "working API access, and available provider quota."
)
