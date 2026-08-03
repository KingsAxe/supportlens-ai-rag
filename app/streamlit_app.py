"""SupportLens AI Streamlit landing page."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="SupportLens AI",
    page_icon="SL",
    layout="wide",
)

st.title("SupportLens AI")
st.caption("Submission-focused customer support intelligence RAG interface for LLM Zoomcamp Attempt 1")

st.markdown(
    """
SupportLens AI helps reviewers test a grounded customer-support workflow built on the current local stack:

- `combined-sample` knowledge-base mode is the default and recommended setup.
- `hybrid_rerank` is the fixed retrieval method for the app.
- dry-run answer generation is the default and safest reviewer path.
- real OpenAI-compatible LLM mode is optional and only available when environment-based configuration is present.
"""
)

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Pages")
    st.markdown(
        """
1. **Ask SupportLens**
Generate a grounded support answer, inspect citations, and review retrieval metadata.
2. **Monitoring Dashboard**
View local answer-generation and feedback analytics, including demo monitoring events.
3. **Evaluation Report**
Lightweight view of current retrieval and dry-run answer-quality metrics.
"""
    )

with right:
    st.subheader("Reviewer Workflow")
    st.markdown(
        """
1. Open **Ask SupportLens**.
2. Keep **dry-run** enabled unless you have a working provider configuration.
3. Click **Prepare / Refresh Knowledge Base** using `combined-sample` mode.
4. Ask a support question or use an example.
5. Inspect the answer, citations, and retrieval metadata.
"""
    )

st.subheader("Run Locally")
st.code("streamlit run app/streamlit_app.py", language="bash")

st.info(
    "Dry-run mode is deterministic and reviewer-friendly. Real LLM mode is implemented in code, "
    "but live use still depends on provider quota and API access."
)
