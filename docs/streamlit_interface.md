# Streamlit Interface

## Interface Scope

This phase adds a lightweight Streamlit interface for Attempt 1 submission review. The goal is to expose the current grounded RAG workflow without overbuilding the application layer.

## How to Run Locally

```bash
streamlit run app/streamlit_app.py
```

Recommended preparation flow before using the Ask page:

```bash
python -m src.ingestion.pipeline --combined-sample
```

Docker Compose is also supported for reviewer startup:

```bash
docker compose up --build
```

## Pages Implemented

1. `streamlit_app.py`
   Landing page with project overview and reviewer instructions.
2. `pages/1_Ask_SupportLens.py`
   Main answer-generation interface.
3. `pages/2_Monitoring_Dashboard.py`
   Local monitoring and feedback dashboard.
4. `pages/3_Evaluation_Report.py`
   Lightweight metrics summary page.

## Dry-Run Default Behavior

The app defaults to dry-run generation because it is deterministic, reproducible, and safe for reviewers who do not configure API access.

Dry-run mode:

- uses the existing grounded retrieval and citation pipeline;
- does not make external LLM calls;
- still shows answer structure, citations, retrieval metadata, and local monitoring hooks.

## Combined-Sample Default

The default and recommended dataset mode is `combined-sample`.

Why:

- it includes the synthetic benchmark cases used by the controlled evaluation sets;
- it adds the public Bitext-derived support cases as broader-language distractors;
- it reflects the Attempt 1 submission setup more honestly than the tiny synthetic-only case set.

## Real LLM Limitation

Real OpenAI-compatible LLM mode is implemented in code and can be selected in the app only when environment-based configuration is present.

Current limitation:

- live Qwen chat validation is still blocked by a provider-side quota or billing response in the current environment.

## Reviewer Workflow

1. Open the app landing page.
2. Go to **Ask SupportLens**.
3. Keep `combined-sample` selected unless you are intentionally testing another mode.
4. Click **Prepare / Refresh Knowledge Base**.
5. Enter a support question or load an example.
6. Generate the answer in dry-run mode.
7. Review the answer, citations, and retrieval metadata.
8. Submit optional rating, thumbs feedback, and comments.
9. Open **Monitoring Dashboard** to review local monitoring charts.
10. Open **Evaluation Report** for the current metrics summary.

## Safe Data Preparation Design

The app does not auto-run multiple ingestion modes on rerun. That is intentional.

Safety behavior:

- the selected mode is prepared only when the user clicks the prepare button;
- the app warns when the currently prepared mode does not match the selected mode;
- answer generation does not silently run all ingestion modes in sequence.

This prevents the earlier `data/processed/` corruption issue caused by multiple ingestion modes writing to the same targets concurrently.

## Monitoring and Feedback

The app now logs two local event types:

- `answer_generated`
- `feedback_submitted`

These events are written to ignored local JSONL logs under `data/processed/` and are surfaced through the monitoring dashboard.

## Screenshots

Placeholder for submission screenshots:

- landing page
- Ask SupportLens page
- evidence and citations table
- monitoring dashboard
- evaluation report page
